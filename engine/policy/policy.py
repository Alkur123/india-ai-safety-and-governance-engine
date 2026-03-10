def apply_policy(category, attacks, medical_intent, uncertainty=0.0):
    """
    Central governance decision engine.
    Deterministic, auditable, regulation-aware.
    """

    # =========================
    # SELF HARM (PASSIVE → SUPPORT)
    # =========================
    if category == "SELF_HARM_PASSIVE":
        return {
            "action": "SUPPORT",
            "category": "SELF_HARM_PASSIVE",
            "rule_id": "MHSA-01",
            "regulation": "Mental Health Support Protocol"
        }

    # =========================
    # SELF HARM (ACTIVE → BLOCK)
    # =========================
    if category == "SELF_HARM":
        return {
            "action": "BLOCK",
            "category": "SELF_HARM",
            "rule_id": "MHSA-02",
            "regulation": "Mental Health Safety Guidelines"
        }

    # =========================
    # SEXUAL / CHILD SAFETY
    # =========================
    if category == "SEXUAL":
        return {
            "action": "BLOCK",
            "category": "SEXUAL",
            "rule_id": "CSA-01",
            "regulation": "Child Safety & Abuse Prevention"
        }

    # =========================
    # VIOLENCE / TERROR
    # =========================
    if category == "VIOLENCE":
        return {
            "action": "BLOCK",
            "category": "VIOLENCE",
            "rule_id": "PSA-01",
            "regulation": "Public Safety & Anti-Terror Laws"
        }

    # =========================
    # ILLEGAL / CRIME (INDIA)
    # =========================
    if category == "ILLEGAL":
        return {
            "action": "BLOCK",
            "category": "ILLEGAL",
            "rule_id": "IPC-01",
            "regulation": "Indian Penal Code (IPC)"
        }

    # =========================
    # MEDICAL GOVERNANCE (IMC)
    # =========================
    if category == "MEDICAL":
        if medical_intent == "ADVICE":
            return {
                "action": "BLOCK",
                "category": "MEDICAL_ADVICE",
                "rule_id": "IMC-01",
                "regulation": "Indian Medical Council (IMC)"
            }
        return {
            "action": "ALLOW",
            "category": "MEDICAL_INFO",
            "rule_id": "IMC-INFO",
            "regulation": "Educational Medical Information"
        }

    # =========================
    # LEGAL ADVICE (BCI)
    # =========================
    if category == "LEGAL":
        return {
            "action": "BLOCK",
            "category": "LEGAL_ADVICE",
            "rule_id": "BCI-01",
            "regulation": "Bar Council of India (BCI)"
        }

    # =========================
    # FINANCIAL ADVICE (SEBI)
    # =========================
    if category == "FINANCIAL":
        return {
            "action": "BLOCK",
            "category": "FINANCIAL_ADVICE",
            "rule_id": "SEBI-01",
            "regulation": "SEBI Investment Advisory Rules"
        }

    # =========================
    # PROMPT INJECTION
    # =========================
    if category == "PROMPT_INJECTION" or attacks.get("prompt_injection"):
        return {
            "action": "BLOCK",
            "category": "PROMPT_INJECTION",
            "rule_id": "AIS-01",
            "regulation": "AI Safety Policy"
        }

    # =========================
    # UNCERTAINTY GATE (LAST)
    # =========================
    if uncertainty >= 0.6:
        return {
            "action": "ABSTAIN",
            "category": "UNCERTAIN",
            "rule_id": "RISK-ESC",
            "regulation": "Risk Escalation Policy"
        }

    # =========================
    # SAFE DEFAULT
    # =========================
    return {
        "action": "ALLOW",
        "category": "SAFE",
        "rule_id": "GEN-00",
        "regulation": "General AI Use"
    }