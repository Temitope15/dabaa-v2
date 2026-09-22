import json
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "data", "disease_db.json")
try:
    with open(db_path, "r", encoding="utf-8") as f:
        DISEASES = json.load(f)
except Exception as e:
    print(f"Failed to load disease_db: {e}")
    DISEASES = {}

ALL_SYMPTOMS = set()
for d in DISEASES.values():
    ALL_SYMPTOMS.update(d["symptoms"])

def extract_symptoms(text: str):
    found = []
    text_lower = text.lower()
    for sym in ALL_SYMPTOMS:
        if sym in text_lower:
            found.append(sym)
    return found

def process_rule_based_chat(chat_history, current_message):
    # Combine all previous human messages plus current
    human_messages = [msg[1] for msg in chat_history if msg[0] == "human"] + [current_message]
    all_text = " ".join(human_messages)
    
    detected_symptoms = extract_symptoms(all_text)
    
    if len(chat_history) == 0:
        if not detected_symptoms:
            return "I'm sorry to hear you're not feeling well. Could you tell me exactly what symptoms you are experiencing (e.g., headache, fever, stomach pain)?"
        return f"I see you are experiencing {', '.join(detected_symptoms)}. How long have you been feeling this way, and how severe is it?"
        
    elif len(chat_history) == 2:
        if not detected_symptoms:
            return "Could you provide a bit more detail about your symptoms so I can narrow down the possible causes?"
            
        # Find possible diseases
        disease_scores = {}
        for name, data in DISEASES.items():
            score = sum(1 for sym in detected_symptoms if sym in data["symptoms"])
            if score > 0:
                disease_scores[name] = score
                
        if not disease_scores:
            return "I see. Are you experiencing any common symptoms like fever, nausea, vomiting, or dizziness?"
            
        # Get top disease's unmentioned symptoms
        top_disease = max(disease_scores.items(), key=lambda x: x[1])[0]
        unmentioned = [s for s in DISEASES[top_disease]["symptoms"] if s not in detected_symptoms]
        
        if unmentioned:
            suggested = ", ".join(unmentioned[:3])
            return f"Noted. To help me narrow this down, are you also experiencing any of the following: {suggested}?"
        else:
            return "Thank you for the details. I have enough information to make a recommendation."
            
    else: # len(chat_history) >= 4 (Final Turn)
        # Final diagnosis
        disease_scores = {}
        for name, data in DISEASES.items():
            score = sum(1 for sym in detected_symptoms if sym in data["symptoms"])
            if score > 0:
                disease_scores[name] = score
                
        if disease_scores:
            top_disease = max(disease_scores.items(), key=lambda x: x[1])[0]
            disease_info = DISEASES[top_disease]
        else:
            top_disease = "a General Illness"
            disease_info = {"specialty": "General Practitioner", "urgency": "medium", "symptoms": detected_symptoms or ["general malaise"]}

        specialty = disease_info["specialty"]
        urgency = disease_info["urgency"]
        
        response = f"Thank you for sharing. Based on the symptoms you've reported ({', '.join(detected_symptoms)}), there is a possibility this could be related to **{top_disease}**. I strongly recommend seeing a specialist for a proper medical diagnosis and treatment.\n\n"
        
        payload = {
            "symptoms": detected_symptoms,
            "urgency": urgency,
            "specialty": specialty,
            "medical_summary": f"Patient reports symptoms indicative of possible {top_disease}."
        }
        response += f"```json\n{json.dumps(payload)}\n```"
        return response
