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
        """Check if the rule engine reached a Triage Decision by finding a JSON payload."""
        import re
        doctors = []
        events = []
        warning_msg = ""
        
        # Look for the JSON ACL payload block
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                payload = json.loads(json_match.group(1))
                specialty = payload.get("specialty", "General Practitioner")
                urgency = payload.get("urgency", "low")
                events.append(f"Received ACL Payload. Urgency: {urgency.upper()}")
                events.append(f"Referral Agent searching for {specialty} nearby...")
                
                # new referral agent returns (doctors, warning_msg)
                doctors, warning_msg = referral_agent.find_doctors(specialty, patient_lat=lat, patient_lng=lng)
                
                if doctors:
                    if any(doc.get("is_hospital") for doc in doctors):
                        events.append(f"No specific specialists found. Found {len(doctors)} nearby hospital(s).")
                    else:
                        events.append(f"Found {len(doctors)} specialist(s).")
            except json.JSONDecodeError:
                events.append("Error: Failed to parse ACL JSON payload.")
                
        return doctors, events, warning_msg

    def process_message(self, patient_id: int, message: str, lat: float = 6.5244, lng: float = 3.3792, api_key: str = None):
        session = self.get_or_create_session(patient_id)
        chat_history = self._trim_history(session["chat_history"])
        session["chat_history"] = chat_history
        events = ["Analyzing Symptoms..."]
        
        # 0. Deterministic Safety Layer
        emergency_keywords = ["accident", "unconscious", "bleeding", "heart attack", "stroke", "suicide", "can't breathe"]
        msg_lower = message.lower()
        if any(keyword in msg_lower for keyword in emergency_keywords):
            safety_msg = "**EMERGENCY DETECTED**: This is an automated safety override. Do not wait for an appointment. Please head to the nearest emergency room immediately or call local emergency services (112 in Nigeria / LASAMBUS)."
            chat_history.append(("human", message))
            chat_history.append(("ai", safety_msg))
            docs, msg = referral_agent.find_doctors("Emergency Medicine", patient_lat=lat, patient_lng=lng)
            if msg:
                safety_msg += f"\n\n*{msg}*"
            return {
                "text": safety_msg,
                "doctors": docs,
                "events": ["CRITICAL: Safety Override Triggered", "Routing to Nearest Hospitals"]
            }
            
        # 1. Deterministic Rule-Based Chat Flow (NO AI)
        from app.agents.rule_engine import process_rule_based_chat
        response_text = process_rule_based_chat(chat_history, message)
        
        events.append("Triage Complete.")
        
        # Update history
        chat_history.append(("human", message))
        chat_history.append(("ai", response_text))
        
        # 2. Check if the Assessment Agent reached a Triage Decision
        doctors, doc_events, warning_msg = self._find_doctors_for_response(response_text, lat, lng)
        events.extend(doc_events)
        
        # Remove JSON block from the text shown to user
        import re
        display_text = re.sub(r'```json\s*.*?\s*```', '', response_text, flags=re.DOTALL).strip()
        
        if warning_msg:
            display_text += f"\n\n*{warning_msg}*"
            
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
            docs, msg = referral_agent.find_doctors("Emergency Medicine", patient_lat=lat, patient_lng=lng)
            if msg:
                yield {"type": "token", "data": f"\n\n*{msg}*"}
            yield {"type": "doctors", "data": docs}
            return
            
        # 1. Deterministic Rule-Based Chat Flow (NO AI)
        from app.agents.rule_engine import process_rule_based_chat
        
        full_text = process_rule_based_chat(chat_history, message)

        # Remove JSON block for token streaming display
        import re
        display_text = re.sub(r'```json\s*.*?\s*```', '', full_text, flags=re.DOTALL).strip()

        for word in display_text.split():
            yield {"type": "token", "data": word + " "}
        
        yield {"type": "events", "data": ["Rule-based Engine Analyzing...", "Triage Complete."]}
        
        # Update history
        chat_history.append(("human", message))
        chat_history.append(("ai", full_text))
        
        # 2. Find doctors
        doctors, doc_events, warning_msg = self._find_doctors_for_response(full_text, lat, lng)
        
        if warning_msg:
            yield {"type": "token", "data": f"\n\n*{warning_msg}*"}
        
        all_events = ["Rule-based Engine Analyzing...", "Triage Complete."] + doc_events
        yield {"type": "events", "data": all_events}
        yield {"type": "doctors", "data": doctors}

orchestrator = Orchestrator()
