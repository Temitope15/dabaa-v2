import json
from app.schemas.patient_state import PatientState
from app.agents.assessment_agent import assessment_agent
from app.agents.referral_agent import referral_agent

MAX_HISTORY_TURNS = 6  # Keep only last 6 exchanges to reduce token count

class Orchestrator:
    def __init__(self):
        # In a real app, state would be persisted per user_id in the DB or Redis
        self.sessions = {}

    def get_or_create_session(self, patient_id: int):
        if patient_id not in self.sessions:
            self.sessions[patient_id] = {
                "patient_state": PatientState(patient_id=patient_id),
                "chat_history": []
            }
        return self.sessions[patient_id]

    def _trim_history(self, chat_history: list) -> list:
        """Keep only the last N turns to reduce input tokens and speed up the API."""
        if len(chat_history) > MAX_HISTORY_TURNS * 2:
            return chat_history[-(MAX_HISTORY_TURNS * 2):]
        return chat_history

    def _find_doctors_for_response(self, response_text: str, lat: float, lng: float):
        """Check if the Assessment Agent reached a Triage Decision by finding a JSON payload."""
        import re
        doctors = []
        events = []
        
        # Look for the JSON ACL payload block
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                payload = json.loads(json_match.group(1))
                specialty = payload.get("specialty", "General Practitioner")
                urgency = payload.get("urgency", "low")
                events.append(f"Received ACL Payload. Urgency: {urgency.upper()}")
                events.append(f"Referral Agent searching for {specialty} nearby...")
                
                doctors = referral_agent.find_doctors(specialty, patient_lat=lat, patient_lng=lng)
                
                if doctors:
                    if any(doc.get("is_hospital") for doc in doctors):
                        events.append(f"No specific doctors found. Found {len(doctors)} nearby hospital(s).")
                    else:
                        events.append(f"Found {len(doctors)} doctor(s).")
            except json.JSONDecodeError:
                events.append("Error: Failed to parse ACL JSON payload.")
                
        return doctors, events

    def process_message(self, patient_id: int, message: str, lat: float = 6.5244, lng: float = 3.3792, api_key: str = None):
        session = self.get_or_create_session(patient_id)
        chat_history = self._trim_history(session["chat_history"])
        session["chat_history"] = chat_history
        events = ["Assessment Agent Analyzing Symptoms..."]
        
        # 0. Deterministic Safety Layer
        emergency_keywords = ["accident", "unconscious", "bleeding", "heart attack", "stroke", "suicide", "can't breathe"]
        msg_lower = message.lower()
        if any(keyword in msg_lower for keyword in emergency_keywords):
            safety_msg = "**EMERGENCY DETECTED**: This is an automated safety override. Do not wait for an appointment. Please head to the nearest emergency room immediately or call local emergency services (112 in Nigeria / LASAMBUS)."
            chat_history.append(("human", message))
            chat_history.append(("ai", safety_msg))
            return {
                "text": safety_msg,
                "doctors": referral_agent.find_doctors("Emergency Medicine", patient_lat=lat, patient_lng=lng),
                "events": ["CRITICAL: Safety Override Triggered", "Routing to Nearest Hospitals"]
            }
            
        # 1. Run Assessment Agent
        try:
            response_text = assessment_agent.run(message, chat_history, api_key=api_key)
            events.append("Triage Complete.")
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                if api_key:
                    return {
                        "text": "The custom Gemini API key you provided has exceeded its quota or usage limit. Please check your Google Cloud Console or update the key in your **Profile**.",
                        "doctors": [],
                        "events": ["Error: User API Quota Exceeded"]
                    }
                else:
                    return {
                        "text": "It looks like the system is currently overloaded or we've hit our global API quota limit. Please go to your **Profile** to enter your own Gemini or OpenRouter API key to continue chatting without interruptions.",
                        "doctors": [],
                        "events": ["Error: Global API Quota Exceeded"]
                    }
            return {"text": f"Error: {e}", "doctors": [], "events": ["Error: Internal Error"]}
            
        # Update history
        chat_history.append(("human", message))
        chat_history.append(("ai", response_text))
        
        # 2. Check if the Assessment Agent reached a Triage Decision
        doctors, doc_events = self._find_doctors_for_response(response_text, lat, lng)
        events.extend(doc_events)
        
        # Remove JSON block from the text shown to user
        import re
        display_text = re.sub(r'```json\s*.*?\s*```', '', response_text, flags=re.DOTALL).strip()
        
        if doctors and any(doc.get("is_hospital") for doc in doctors):
            display_text += "\n\n*Oops! Sorry, there are no specific doctors around right now, but these are nearby hospitals that you can go to based on your location.*"
            
        return {
            "text": display_text,
            "doctors": doctors,
            "events": events
        }

    def process_message_streaming(self, patient_id: int, message: str, lat: float = 6.5244, lng: float = 3.3792, api_key: str = None):
        """Generator that yields tokens as they stream from the LLM."""
        session = self.get_or_create_session(patient_id)
        chat_history = self._trim_history(session["chat_history"])
        session["chat_history"] = chat_history
        
        # 0. Deterministic Safety Layer
        emergency_keywords = ["accident", "unconscious", "bleeding", "heart attack", "stroke", "suicide", "can't breathe"]
        msg_lower = message.lower()
        if any(keyword in msg_lower for keyword in emergency_keywords):
            safety_msg = "**EMERGENCY DETECTED**: This is an automated safety override. Do not wait for an appointment. Please head to the nearest emergency room immediately or call local emergency services (112 in Nigeria / LASAMBUS)."
            chat_history.append(("human", message))
            chat_history.append(("ai", safety_msg))
            yield {"type": "events", "data": ["CRITICAL: Safety Override Triggered", "Routing to Nearest Hospitals"]}
            yield {"type": "token", "data": safety_msg}
            yield {"type": "doctors", "data": referral_agent.find_doctors("Emergency Medicine", patient_lat=lat, patient_lng=lng)}
            return
            
        # 1. Stream from Assessment Agent
        try:
            full_text = ""
            hide_json = False
            for token in assessment_agent.run_stream(message, chat_history, api_key=api_key):
                full_text += token
                if "```json" in full_text and not hide_json:
                    hide_json = True
                    # Backtrack to remove the "```json" part that was already sent? Too complex.
                    # We just stop sending new tokens.
                if not hide_json:
                    yield {"type": "token", "data": token}
            
            yield {"type": "events", "data": ["Assessment Agent Analyzing Symptoms...", "Triage Complete."]}
            
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                if api_key:
                    return {
                        "text": "The custom Gemini API key you provided has exceeded its quota or usage limit. Please check your Google Cloud Console or update the key in your **Profile**.",
                        "doctors": [],
                        "events": ["Error: User API Quota Exceeded"]
                    }
                else:
                    return {
                        "text": "It looks like the system is currently overloaded or we've hit our global API quota limit. Please go to your **Profile** to enter your own Gemini or OpenRouter API key to continue chatting without interruptions.",
                        "doctors": [],
                        "events": ["Error: Global API Quota Exceeded"]
                    }
            return {"text": f"Error: {e}", "doctors": [], "events": ["Error: Internal Error"]}
        
        # Update history
        chat_history.append(("human", message))
        chat_history.append(("ai", full_text))
        
        # 2. Find doctors
        doctors, doc_events = self._find_doctors_for_response(full_text, lat, lng)
        
        if doctors and any(doc.get("is_hospital") for doc in doctors):
            hospital_note = "\n\n*Oops! Sorry, there are no specific doctors around right now, but these are nearby hospitals that you can go to based on your location.*"
            yield {"type": "token", "data": hospital_note}
        
        all_events = ["Assessment Agent Analyzing Symptoms...", "Triage Complete."] + doc_events
        yield {"type": "events", "data": all_events}
        yield {"type": "doctors", "data": doctors}

orchestrator = Orchestrator()
