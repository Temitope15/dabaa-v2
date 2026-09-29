"""
Dààbà Rule-Based Clinical Triage Engine
========================================
Uses:
  - Trie (Prefix Tree) + DFS Backtracking for fuzzy symptom matching
  - Algorithmic Probability (F1 / Dice Coefficient) for disease scoring
  - Dynamic conversation loop that converges when confidence >= 80%
"""

import json
import os

# ---------------------------------------------------------------------------
# 1. Load Knowledge Base
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 2. Trie Data Structure for Fuzzy Symptom Matching
# ---------------------------------------------------------------------------
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = None  # The canonical symptom string


class SymptomTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.word = word.lower()

    def search_fuzzy(self, query: str, max_edits: int = 2) -> list:
        """
        DFS backtracking search through the Trie.
        Finds all symptoms within `max_edits` edit distance of `query`.
        Supports substitution, deletion, and insertion operations.
        """
        results = []
        query = query.lower()

        def dfs(node, i, edits_left):
            if edits_left < 0:
                return
            if i == len(query):
                if node.is_end:
                    results.append((node.word, max_edits - edits_left))
                # Check words that are 1 char longer in the trie
                if edits_left > 0:
                    for child in node.children.values():
                        if child.is_end:
                            results.append((child.word, max_edits - edits_left + 1))
                return

            char = query[i]
            for c, child in node.children.items():
                if c == char:
                    dfs(child, i + 1, edits_left)       # Exact match
                else:
                    dfs(child, i + 1, edits_left - 1)    # Substitution

            # Deletion: skip a character in query
            dfs(node, i + 1, edits_left - 1)

            # Insertion: advance in trie without consuming query char
            for c, child in node.children.items():
                dfs(child, i, edits_left - 1)

        dfs(self.root, 0, max_edits)

        # Deduplicate and sort by edit distance (best match first)
        seen = set()
        unique = []
        for word, dist in sorted(results, key=lambda x: x[1]):
            if word not in seen:
                seen.add(word)
                unique.append((word, dist))
        return unique


# Build the global Trie at startup — only insert SINGLE-WORD symptoms
# Multi-word symptoms (e.g. "chest pain") are handled by exact phrase matching only
SYMPTOM_TRIE = SymptomTrie()
SINGLE_WORD_SYMPTOMS = set()
MULTI_WORD_SYMPTOMS = set()

for symptom in ALL_SYMPTOMS:
    words = symptom.split()
    if len(words) == 1:
        SYMPTOM_TRIE.insert(symptom)
        SINGLE_WORD_SYMPTOMS.add(symptom)
    else:
        MULTI_WORD_SYMPTOMS.add(symptom)


# ---------------------------------------------------------------------------
# 3. Symptom Extraction (Exact + Fuzzy Trie)
# ---------------------------------------------------------------------------
def extract_symptoms_fuzzy(text: str) -> list:
    """
    Two-pass symptom extraction:
    Pass 1: Exact substring matching for multi-word symptoms (e.g. "chest pain").
    Pass 2: Fuzzy Trie DFS matching for single words (handles typos like "hedache").
    """
    found = set()
    text_lower = text.lower()

    # Pass 1: Exact multi-word phrase matching
    for sym in MULTI_WORD_SYMPTOMS:
        if sym in text_lower:
            found.add(sym)

    # Pass 2: Fuzzy single-word matching via Trie
    # Common non-medical words to skip
    skip_words = {"have", "been", "also", "just", "like", "feel", "feeling",
                  "very", "really", "since", "yesterday", "today", "some",
                  "with", "that", "this", "from", "they", "what", "when",
                  "will", "would", "could", "should", "about", "there",
                  "your", "their", "more", "than", "other", "into",
                  "still", "same", "thing", "think", "said", "does",
                  "much", "many", "well", "good", "back", "even",
                  "take", "going", "know", "need", "help", "tell",
                  "long", "time", "days", "week", "started", "start"}

    words = text_lower.split()
    for word in words:
        # Strip punctuation
        word = word.strip(".,!?;:'\"()[]")
        # Skip short words and common non-medical words
        if len(word) < 4 or word in skip_words:
            continue

        # Check for exact single-word symptom first (no edits needed)
        if word in SINGLE_WORD_SYMPTOMS:
            found.add(word)
            continue

        # Fuzzy search: stricter edit distance based on word length
        max_edits = 1 if len(word) < 6 else 2
        matches = SYMPTOM_TRIE.search_fuzzy(word, max_edits=max_edits)
        for match_word, edit_dist in matches:
            # Only accept if the match is close enough
            if edit_dist <= max_edits and edit_dist > 0:
                found.add(match_word)

    return list(found)


# ---------------------------------------------------------------------------
# 4. Disease Scoring (Algorithmic Probability / F1 Score)
# ---------------------------------------------------------------------------
def score_diseases(detected_symptoms: list) -> dict:
    """
    Scores every disease using the F1 Score (Dice Coefficient):
        F1 = (2 * Precision * Recall) / (Precision + Recall)
    Where:
        Precision = matched_symptoms / total_detected_symptoms
        Recall    = matched_symptoms / total_disease_symptoms
    """
    if not detected_symptoms:
        return {}

    scores = {}
    detected_set = set(detected_symptoms)

    for name, data in DISEASES.items():
        disease_syms = set(data["symptoms"])
        if not disease_syms:
            continue

        matches = detected_set.intersection(disease_syms)
        match_count = len(matches)

        if match_count > 0:
            precision = match_count / len(detected_set)
            recall = match_count / len(disease_syms)
            f1 = (2 * precision * recall) / (precision + recall)
            scores[name] = f1

    return scores


# ---------------------------------------------------------------------------
# 5. Response Builders
# ---------------------------------------------------------------------------
def build_diagnosis_response(detected_symptoms: list, disease_scores: dict) -> str:
    """Build the final diagnosis response with JSON payload for map routing."""
    top_disease, top_prob = max(disease_scores.items(), key=lambda x: x[1])
    info = DISEASES[top_disease]
    pct = int(top_prob * 100)
    specialty = info["specialty"]
    urgency = info["urgency"]

    urgency_text = "immediate emergency" if urgency == "high" else "routine medical"

    response = f"Based on your symptoms ({', '.join(detected_symptoms)}), "
    response += f"my clinical knowledge base calculates a **{pct}% algorithmic probability** "
    response += f"that this could be **{top_disease}**.\n\n"
    response += f"This condition requires {urgency_text} attention. "
    response += f"I strongly recommend seeing a **{specialty}**. "
    response += f"Please book an appointment from the options below.\n\n"

    payload = {
        "symptoms": detected_symptoms,
        "urgency": urgency,
        "specialty": specialty,
        "medical_summary": f"{pct}% algorithmic match for {top_disease}."
    }
    response += f"```json\n{json.dumps(payload)}\n```"
    return response


def build_unknown_response() -> str:
    """When no symptoms are recognized after multiple turns."""
    response = "I'm not familiar with these symptoms in my knowledge base. "
    response += "For your safety, I strongly recommend visiting the nearest hospital immediately.\n\n"
    payload = {
        "symptoms": [],
        "urgency": "high",
        "specialty": "Emergency Medicine",
        "medical_summary": "Unrecognized symptoms. Patient referred to emergency."
    }
    response += f"```json\n{json.dumps(payload)}\n```"
    return response


def build_followup_question(detected: list, scores: dict, top_disease: str, top_prob: float) -> str:
    """Build a guided follow-up question with a checklist of discriminating symptoms."""
    # Get top 3 candidate diseases
    sorted_diseases = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]

    # Collect unmentioned symptoms from top candidates
    unmentioned = []
    seen = set()
    for disease_name, _ in sorted_diseases:
        for sym in DISEASES[disease_name]["symptoms"]:
            if sym not in detected and sym not in seen:
                seen.add(sym)
                unmentioned.append(sym)

    # Pick the most discriminating 5 symptoms
    checklist = unmentioned[:5]
    prob_pct = int(top_prob * 100)
    symptom_list = ", ".join(detected)
    checklist_str = "\n".join([f"• {s.title()}" for s in checklist])

    response = f"I understand you have **{symptom_list}**. "
    response += f"I'm narrowing it down (confidence: {prob_pct}%). "
    response += f"Do you also have any of the following?\n\n{checklist_str}"

    return response


# ---------------------------------------------------------------------------
# 6. Main Dynamic Chat Processor
# ---------------------------------------------------------------------------
def process_rule_based_chat(chat_history: list, current_message: str) -> str:
    """
    Fully dynamic diagnosis loop.
    - Extracts symptoms from ALL messages (cumulative).
    - Scores all diseases every turn.
    - If confidence >= 80% -> output diagnosis immediately.
    - If confidence < 80% -> ask guided follow-up with discriminating symptoms.
    - Soft safety net at 10 total messages -> output best match with actual %.
    """
    # Gather all human messages
    human_messages = [msg[1] for msg in chat_history if msg[0] == "human"]
    human_messages.append(current_message)
    all_text = " ".join(human_messages)
    turn_number = len(human_messages)  # How many patient messages so far
    total_messages = len(chat_history) + 1  # Total messages in conversation

    # Extract symptoms using Fuzzy Trie
    detected = extract_symptoms_fuzzy(all_text)

    # SAFETY NET: Turn 1, no symptoms found -> ask to describe
    if turn_number == 1 and not detected:
        return ("I'm sorry to hear you're not feeling well. "
                "Could you tell me exactly what symptoms you are experiencing? "
                "(e.g., headache, fever, stomach pain, cough)")

    # SAFETY NET: Turn 2+, still no symptoms -> unknown -> hospital
    if turn_number >= 2 and not detected:
        return build_unknown_response()

    # Score all diseases
    scores = score_diseases(detected)

    if not scores:
        return ("I couldn't find a strong match in my knowledge base for those symptoms. "
                "Could you describe them differently or add more detail?")

    top_disease, top_prob = max(scores.items(), key=lambda x: x[1])

    # DYNAMIC DECISION
    if top_prob >= 0.80:
        # ✅ Confident enough -> DIAGNOSE
        return build_diagnosis_response(detected, scores)

    elif total_messages >= 10:
        # ⚠️ Soft safety net: output best match with actual percentage
        return build_diagnosis_response(detected, scores)

    else:
        # 🔄 Not confident yet -> ask guided follow-up
        return build_followup_question(detected, scores, top_disease, top_prob)
