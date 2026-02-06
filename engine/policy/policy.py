# engine/policy/policy.py

def apply_policy(category, attacks, medical_intent, uncertainty=0.0):
    """
    Central governance decision engine.
    Returns deterministic BLOCK / ABSTAIN / ALLOW decisions
    with auditable policy categories.
    """

    # =========================
    # PROMPT INJECTION
    # =========================
    if attacks.get("prompt_injection"):
        return {
            "action": "BLOCK",
            "category": "PROMPT_INJECTION",
            "regulation": "AI Safety Policy"
        }

    # =========================
    # SELF HARM
    # =========================
    if category == "SELF_HARM":
        return {
            "action": "BLOCK",
            "category": "SELF_HARM",
            "regulation": "Mental Health Safety Guidelines"
        }

    # =========================
    # SEXUAL / CHILD SAFETY
    # =========================
    if category == "SEXUAL":
        return {
            "action": "BLOCK",
            "category": "SEXUAL",
            "regulation": "Child Safety & Abuse Prevention"
        }

    # =========================
    # VIOLENCE / TERROR
    # =========================
    if category == "VIOLENCE":
        return {
            "action": "BLOCK",
            "category": "VIOLENCE",
            "regulation": "Public Safety & Anti-Terror Laws"
        }

    # =========================
    # ILLEGAL / CRIME
    # =========================
    if category == "ILLEGAL":
        return {
            "action": "BLOCK",
            "category": "ILLEGAL",
            "regulation": "Indian Penal Code (IPC)"
        }

    # =========================
    # MEDICAL GOVERNANCE (INDIA)
    # =========================
    if category == "MEDICAL":
        if medical_intent == "ADVICE":
            return {
                "action": "BLOCK",
                "category": "MEDICAL_ADVICE",
                "regulation": "Indian Medical Council (IMC)"
            }
        return {
            "action": "ALLOW",
            "category": "MEDICAL_INFO",
            "regulation": "Educational Medical Information"
        }

    # =========================
    # LEGAL ADVICE (INDIA)
    # =========================
    if category == "LEGAL":
        return {
            "action": "BLOCK",
            "category": "LEGAL_ADVICE",
            "regulation": "Bar Council of India"
        }

    # =========================
    # FINANCIAL ADVICE (SEBI)
    # =========================
    if category == "FINANCIAL":
        return {
            "action": "BLOCK",
            "category": "FINANCIAL_ADVICE",
            "regulation": "SEBI Investment Advisory Rules"
        }

    # =========================
    # UNCERTAINTY GATE
    # =========================
    if uncertainty >= 0.6:
        return {
            "action": "ABSTAIN",
            "category": "UNCERTAIN",
            "regulation": "Risk Escalation Policy"
        }

    # =========================
    # SAFE DEFAULT
    # =========================
    return {
        "action": "ALLOW",
        "category": "SAFE",
        "regulation": "General AI Use"
    }

