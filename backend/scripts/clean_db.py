import json

db_path = "backend/app/data/disease_db.json"
with open(db_path, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned_data = {}
for name, info in data.items():
    if "Clinical Condition Variant" not in name:
        cleaned_data[name] = info

with open(db_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=4)
print(f"Cleaned DB. Now has {len(cleaned_data)} real diseases.")
