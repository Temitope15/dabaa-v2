import json

# Complete, well-curated disease database for Nigerian healthcare context
# Each disease has clean, searchable single/two-word symptoms
DISEASES = {
    # === INFECTIOUS DISEASES ===
    "Malaria": {
        "symptoms": ["fever", "headache", "chills", "sweating", "nausea", "vomiting", "muscle pain", "fatigue", "weakness"],
        "specialty": "Internal Medicine",
        "urgency": "high"
    },
    "Typhoid Fever": {
        "symptoms": ["fever", "headache", "fatigue", "abdominal pain", "nausea", "constipation", "diarrhea", "loss of appetite", "weakness"],
        "specialty": "Internal Medicine",
        "urgency": "high"
    },
    "Cholera": {
        "symptoms": ["diarrhea", "vomiting", "dehydration", "leg cramps", "nausea", "weakness", "thirst"],
        "specialty": "Emergency Medicine",
        "urgency": "high"
    },
    "Tuberculosis": {
        "symptoms": ["cough", "chest pain", "fatigue", "night sweats", "weight loss", "fever", "blood in cough"],
        "specialty": "Pulmonologist",
        "urgency": "high"
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "fatigue", "loss of taste", "loss of smell", "shortness of breath", "sore throat", "body ache", "headache"],
        "specialty": "Internal Medicine",
        "urgency": "high"
    },
    "HIV/AIDS": {
        "symptoms": ["fever", "fatigue", "weight loss", "night sweats", "swollen lymph nodes", "diarrhea", "sore throat", "rash", "mouth sores"],
        "specialty": "Internal Medicine",
        "urgency": "high"
    },
    "Hepatitis B": {
        "symptoms": ["fatigue", "nausea", "vomiting", "abdominal pain", "dark urine", "joint pain", "jaundice", "loss of appetite", "fever"],
        "specialty": "Gastroenterologist",
        "urgency": "high"
    },
    "Lassa Fever": {
        "symptoms": ["fever", "headache", "sore throat", "muscle pain", "chest pain", "nausea", "vomiting", "facial swelling", "bleeding"],
        "specialty": "Emergency Medicine",
        "urgency": "high"
    },
    "Meningitis": {
        "symptoms": ["headache", "fever", "stiff neck", "nausea", "vomiting", "confusion", "sensitivity to light", "rash"],
        "specialty": "Neurologist",
        "urgency": "high"
    },
    "Urinary Tract Infection": {
        "symptoms": ["painful urination", "frequent urination", "lower abdominal pain", "cloudy urine", "blood in urine", "urgency to urinate", "fever"],
        "specialty": "Urologist",
        "urgency": "medium"
    },
    "Dengue Fever": {
        "symptoms": ["fever", "headache", "muscle pain", "joint pain", "rash", "nausea", "vomiting", "eye pain", "fatigue"],
        "specialty": "Internal Medicine",
        "urgency": "high"
    },

    # === RESPIRATORY ===
    "Asthma": {
        "symptoms": ["shortness of breath", "wheezing", "chest tightness", "cough", "difficulty breathing"],
        "specialty": "Pulmonologist",
        "urgency": "high"
    },
    "Pneumonia": {
        "symptoms": ["cough", "fever", "chills", "shortness of breath", "chest pain", "fatigue", "phlegm"],
        "specialty": "Pulmonologist",
        "urgency": "high"
    },
    "Bronchitis": {
        "symptoms": ["cough", "phlegm", "fatigue", "shortness of breath", "chest discomfort", "sore throat", "body ache"],
        "specialty": "Pulmonologist",
        "urgency": "medium"
    },
    "Sinusitis": {
        "symptoms": ["nasal congestion", "headache", "facial pain", "runny nose", "cough", "sore throat", "fever", "fatigue"],
        "specialty": "ENT Specialist",
        "urgency": "low"
    },
    "Common Cold": {
        "symptoms": ["runny nose", "sneezing", "sore throat", "cough", "congestion", "headache", "body ache", "fatigue"],
        "specialty": "General Practitioner",
        "urgency": "low"
    },
    "Flu (Influenza)": {
        "symptoms": ["fever", "cough", "sore throat", "body ache", "headache", "fatigue", "chills", "runny nose"],
        "specialty": "General Practitioner",
        "urgency": "medium"
    },

    # === CARDIOVASCULAR ===
    "Hypertension": {
        "symptoms": ["headache", "shortness of breath", "nosebleed", "dizziness", "chest pain", "blurred vision"],
        "specialty": "Cardiologist",
        "urgency": "high"
    },
    "Heart Attack": {
        "symptoms": ["chest pain", "shortness of breath", "sweating", "nausea", "dizziness", "arm pain", "jaw pain"],
        "specialty": "Emergency Medicine",
        "urgency": "high"
    },
    "Stroke": {
        "symptoms": ["sudden numbness", "confusion", "trouble speaking", "severe headache", "dizziness", "vision problems", "weakness"],
        "specialty": "Emergency Medicine",
        "urgency": "high"
    },
    "Heart Failure": {
        "symptoms": ["shortness of breath", "fatigue", "swollen legs", "swollen ankles", "rapid heartbeat", "cough", "weight gain"],
        "specialty": "Cardiologist",
        "urgency": "high"
    },

    # === GASTROINTESTINAL ===
    "Peptic Ulcer": {
        "symptoms": ["stomach pain", "bloating", "heartburn", "nausea", "vomiting", "loss of appetite", "weight loss"],
        "specialty": "Gastroenterologist",
        "urgency": "medium"
    },
    "Gastroenteritis": {
        "symptoms": ["diarrhea", "vomiting", "stomach pain", "nausea", "fever", "cramps", "dehydration"],
        "specialty": "General Practitioner",
        "urgency": "medium"
    },
    "Appendicitis": {
        "symptoms": ["abdominal pain", "nausea", "vomiting", "fever", "loss of appetite", "bloating"],
        "specialty": "General Surgeon",
        "urgency": "high"
    },
    "Gastric Reflux (GERD)": {
        "symptoms": ["heartburn", "chest pain", "difficulty swallowing", "regurgitation", "nausea", "sore throat"],
        "specialty": "Gastroenterologist",
        "urgency": "low"
    },
    "Food Poisoning": {
        "symptoms": ["nausea", "vomiting", "diarrhea", "stomach pain", "fever", "cramps", "weakness"],
        "specialty": "General Practitioner",
        "urgency": "medium"
    },
    "Irritable Bowel Syndrome": {
        "symptoms": ["abdominal pain", "bloating", "diarrhea", "constipation", "cramps", "gas"],
        "specialty": "Gastroenterologist",
        "urgency": "low"
    },

    # === ENDOCRINE ===
    "Type 2 Diabetes": {
        "symptoms": ["frequent urination", "increased thirst", "fatigue", "blurred vision", "weight loss", "slow healing", "tingling hands"],
        "specialty": "Endocrinologist",
        "urgency": "medium"
    },
    "Hyperthyroidism": {
        "symptoms": ["weight loss", "rapid heartbeat", "anxiety", "tremor", "sweating", "difficulty sleeping", "irritability"],
        "specialty": "Endocrinologist",
        "urgency": "medium"
    },
    "Hypothyroidism": {
        "symptoms": ["fatigue", "weight gain", "cold sensitivity", "constipation", "dry skin", "depression", "muscle weakness"],
        "specialty": "Endocrinologist",
        "urgency": "low"
    },

    # === MUSCULOSKELETAL ===
    "Arthritis": {
        "symptoms": ["joint pain", "swelling", "stiffness", "reduced movement", "redness", "fatigue"],
        "specialty": "Rheumatologist",
        "urgency": "low"
    },
    "Back Pain": {
        "symptoms": ["back pain", "muscle ache", "stiffness", "shooting pain", "limited flexibility", "difficulty standing"],
        "specialty": "Orthopedic Surgeon",
        "urgency": "low"
    },
    "Sickle Cell Crisis": {
        "symptoms": ["severe pain", "joint pain", "chest pain", "fever", "fatigue", "swelling", "shortness of breath"],
        "specialty": "Hematologist",
        "urgency": "high"
    },

    # === NEUROLOGICAL ===
    "Migraine": {
        "symptoms": ["headache", "nausea", "sensitivity to light", "sensitivity to sound", "dizziness", "blurred vision", "throbbing pain"],
        "specialty": "Neurologist",
        "urgency": "medium"
    },
    "Epilepsy": {
        "symptoms": ["seizures", "confusion", "staring spells", "uncontrollable jerking", "loss of consciousness", "anxiety"],
        "specialty": "Neurologist",
        "urgency": "high"
    },

    # === DERMATOLOGICAL ===
    "Eczema": {
        "symptoms": ["itchy skin", "rash", "dry skin", "red patches", "cracked skin", "swelling"],
        "specialty": "Dermatologist",
        "urgency": "low"
    },
    "Ringworm": {
        "symptoms": ["ring-shaped rash", "itchy skin", "red patches", "scaly skin", "hair loss"],
        "specialty": "Dermatologist",
        "urgency": "low"
    },
    "Acne": {
        "symptoms": ["pimples", "blackheads", "whiteheads", "oily skin", "scarring", "inflammation"],
        "specialty": "Dermatologist",
        "urgency": "low"
    },

    # === MENTAL HEALTH ===
    "Depression": {
        "symptoms": ["sadness", "loss of interest", "fatigue", "difficulty sleeping", "weight change", "difficulty concentrating", "hopelessness"],
        "specialty": "Psychiatrist",
        "urgency": "medium"
    },
    "Anxiety Disorder": {
        "symptoms": ["worry", "restlessness", "rapid heartbeat", "sweating", "trembling", "difficulty sleeping", "difficulty concentrating"],
        "specialty": "Psychiatrist",
        "urgency": "medium"
    },

    # === REPRODUCTIVE / UROLOGICAL ===
    "Prostate Enlargement": {
        "symptoms": ["frequent urination", "difficulty urinating", "weak urine stream", "urgency to urinate", "incomplete emptying"],
        "specialty": "Urologist",
        "urgency": "medium"
    },
    "Menstrual Cramps": {
        "symptoms": ["lower abdominal pain", "cramps", "back pain", "nausea", "headache", "fatigue", "diarrhea"],
        "specialty": "Gynecologist",
        "urgency": "low"
    },
    "Fibroid": {
        "symptoms": ["heavy menstrual bleeding", "pelvic pain", "frequent urination", "constipation", "back pain", "leg pain"],
        "specialty": "Gynecologist",
        "urgency": "medium"
    },

    # === OPHTHALMOLOGICAL ===
    "Glaucoma": {
        "symptoms": ["eye pain", "blurred vision", "headache", "nausea", "halos around lights", "vision loss", "eye redness"],
        "specialty": "Ophthalmologist",
        "urgency": "high"
    },
    "Conjunctivitis": {
        "symptoms": ["eye redness", "itchy eyes", "discharge from eye", "tearing", "swollen eyelids", "sensitivity to light"],
        "specialty": "Ophthalmologist",
        "urgency": "low"
    },

    # === ENT ===
    "Tonsillitis": {
        "symptoms": ["sore throat", "difficulty swallowing", "fever", "headache", "swollen tonsils", "ear pain", "bad breath"],
        "specialty": "ENT Specialist",
        "urgency": "medium"
    },
    "Ear Infection": {
        "symptoms": ["ear pain", "fever", "difficulty hearing", "fluid drainage", "headache", "irritability"],
        "specialty": "ENT Specialist",
        "urgency": "medium"
    },

    # === KIDNEY ===
    "Kidney Stones": {
        "symptoms": ["severe pain", "back pain", "blood in urine", "nausea", "vomiting", "painful urination", "fever"],
        "specialty": "Urologist",
        "urgency": "high"
    },
    "Kidney Infection": {
        "symptoms": ["fever", "back pain", "nausea", "vomiting", "painful urination", "frequent urination", "blood in urine"],
        "specialty": "Nephrologist",
        "urgency": "high"
    },

    # === OTHER COMMON ===
    "Anaemia": {
        "symptoms": ["fatigue", "weakness", "pale skin", "shortness of breath", "dizziness", "cold hands", "headache"],
        "specialty": "Hematologist",
        "urgency": "medium"
    },
    "Allergic Reaction": {
        "symptoms": ["rash", "itching", "swelling", "shortness of breath", "sneezing", "watery eyes", "hives"],
        "specialty": "General Practitioner",
        "urgency": "medium"
    },
    "Chicken Pox": {
        "symptoms": ["rash", "fever", "fatigue", "headache", "loss of appetite", "itchy blisters"],
        "specialty": "General Practitioner",
        "urgency": "medium"
    },
    "Measles": {
        "symptoms": ["fever", "cough", "runny nose", "rash", "red eyes", "sensitivity to light", "sore throat"],
        "specialty": "General Practitioner",
        "urgency": "high"
    },
}

out_path = "backend/app/data/disease_db.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(DISEASES, f, indent=4)

# Stats
all_syms = set()
for d in DISEASES.values():
    all_syms.update(d["symptoms"])
print(f"✅ Wrote {len(DISEASES)} diseases with {len(all_syms)} unique symptoms to {out_path}")
