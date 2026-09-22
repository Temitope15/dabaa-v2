import re
import json

md_path = "backend/app/data/comprehensive_medical_knowledge.md"
out_path = "backend/app/data/disease_db.json"

diseases = {}

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern matching
blocks = content.split("## ")[1:]

for block in blocks:
    lines = block.strip().split("\n")
    if not lines: continue
    
    header = lines[0].strip()
    name = re.sub(r'\(.*?\)', '', header).strip()
    
    symptoms = []
    specialty = "General Practitioner"
    urgency = "medium"
    
    for line in lines[1:]:
        if line.startswith("**Typical Symptoms:**"):
            syms = line.replace("**Typical Symptoms:**", "").strip()
            # split by comma or 'and'
            symptoms = [s.strip().lower() for s in re.split(r',| and ', syms) if s.strip()]
            # remove trailing periods
            symptoms = [s.replace('.', '') for s in symptoms]
            
        elif line.startswith("**Recommended Specialty:**"):
            specialty = line.replace("**Recommended Specialty:**", "").strip()
            
        elif line.startswith("**Triage Guidelines"):
            guide = line.lower()
            if "emergency" in guide or "high urgency" in guide or "immediate" in guide or "urgent" in guide:
                urgency = "high"
            elif "routine" in guide or "low urgency" in guide:
                urgency = "low"

    if name and symptoms:
        diseases[name] = {
            "symptoms": symptoms,
            "specialty": specialty,
            "urgency": urgency
        }

print(f"Parsed {len(diseases)} diseases.")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(diseases, f, indent=4)

