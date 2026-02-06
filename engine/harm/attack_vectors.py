def detect_attack_vectors(q):
    q=q.lower()
    return {
        "prompt_injection": "ignore previous" in q or "bypass" in q,
        "self_harm": "kill myself" in q or "suicide" in q,
        "violence": "kill" in q or "bomb" in q,
        "illegal": "hack" in q or "fraud" in q,
        "medical": "prescription" in q
    }
