import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Bypass the __init__.py import chain by importing rule_engine directly
import importlib.util
spec = importlib.util.spec_from_file_location("rule_engine", os.path.join(os.path.dirname(__file__), '..', 'app', 'agents', 'rule_engine.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

extract_symptoms_fuzzy = mod.extract_symptoms_fuzzy
score_diseases = mod.score_diseases
process_rule_based_chat = mod.process_rule_based_chat

print("=" * 60)
print("TEST 1: Exact matching")
print("=" * 60)
syms = extract_symptoms_fuzzy("I have headache and nausea")
print(f"Input: 'I have headache and nausea'")
print(f"Detected: {syms}")

print("\n" + "=" * 60)
print("TEST 2: Typo matching (hedache -> headache)")
print("=" * 60)
syms = extract_symptoms_fuzzy("I have hedache and fever")
print(f"Input: 'I have hedache and fever'")
print(f"Detected: {syms}")

print("\n" + "=" * 60)
print("TEST 3: Disease scoring")
print("=" * 60)
syms = extract_symptoms_fuzzy("fever headache chills sweating nausea vomiting")
scores = score_diseases(syms)
print(f"Symptoms: {syms}")
for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {name}: {int(score*100)}%")

print("\n" + "=" * 60)
print("TEST 4: Full conversation simulation")
print("=" * 60)

chat_history = []

msg1 = "I have a headache"
print(f"\nPatient: {msg1}")
resp1 = process_rule_based_chat(chat_history, msg1)
print(f"System: {resp1}")
chat_history.append(("human", msg1))
chat_history.append(("ai", resp1))

msg2 = "Yes I have fever and chills"
print(f"\nPatient: {msg2}")
resp2 = process_rule_based_chat(chat_history, msg2)
print(f"System: {resp2}")
chat_history.append(("human", msg2))
chat_history.append(("ai", resp2))

msg3 = "Yes sweating and nausea too"
print(f"\nPatient: {msg3}")
resp3 = process_rule_based_chat(chat_history, msg3)
print(f"System: {resp3}")

print("\n" + "=" * 60)
print("TEST 5: Instant diagnosis (many symptoms)")
print("=" * 60)
resp = process_rule_based_chat([], "I have fever chills headache sweating nausea vomiting and muscle pain")
print(f"System: {resp}")

print("\n" + "=" * 60)
print("TEST 6: Unknown symptoms")
print("=" * 60)
chat2 = []
msg_a = "I feel zxqwerty"
print(f"Patient: {msg_a}")
resp_a = process_rule_based_chat(chat2, msg_a)
print(f"System: {resp_a}")
chat2.append(("human", msg_a))
chat2.append(("ai", resp_a))

msg_b = "still the same zxqwerty thing"
print(f"\nPatient: {msg_b}")
resp_b = process_rule_based_chat(chat2, msg_b)
print(f"System: {resp_b}")
