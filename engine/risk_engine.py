INTENT_RISK = {
    "safe question": 1,
    "prompt injection": 7,
    "data exfiltration": 9,
    "policy violation": 6
}


def evaluate_risk(intent, confidence):

    # Normalize intent text for reliable lookup
    if intent:
        normalized_intent = intent.replace("_", " ").lower()
    else:
        normalized_intent = "safe question"

    base_risk = INTENT_RISK.get(normalized_intent, 3)

    risk_score = base_risk * confidence

    return round(risk_score, 2)