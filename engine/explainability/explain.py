def explain(category, action, attacks, phi, regulation=None):
    """
    Human-readable governance explanation.
    Designed for audits, demos, and public-sector compliance reviews.
    """

    triggered_attacks = [k for k, v in attacks.items() if v]

    explanation = {
        "decision_summary": {
            "final_action": action,
            "risk_category": category,
            "regulation_applied": regulation if regulation else "General AI Safety Policy"
        },
        "reasoning": [],
        "signals": {
            "attack_vectors_detected": triggered_attacks,
            "personal_data_detected": phi or []
        },
        "audit": {
            "log_type": "RTI-compliant audit record",
            "immutability": "append-only",
            "governance_scope": "India"
        }
    }

    # =========================
    # GOVERNANCE REASONING
    # =========================
    if action == "BLOCK":
        explanation["reasoning"].append(
            f"Request blocked under governance category: {category}."
        )

        if regulation:
            explanation["reasoning"].append(
                f"Decision enforced to comply with {regulation}."
            )

        if triggered_attacks:
            explanation["reasoning"].append(
                f"Risk indicators detected: {', '.join(triggered_attacks)}."
            )

        explanation["reasoning"].append(
            "Preventive enforcement applied before content generation."
        )

    elif action == "ABSTAIN":
        explanation["reasoning"].append(
            "Request exhibits elevated uncertainty or ambiguous intent."
        )
        explanation["reasoning"].append(
            "Response withheld to prevent unsafe, misleading, or non-compliant output."
        )

    elif action == "ALLOW":
        explanation["reasoning"].append(
            "Request evaluated as compliant with current governance policies."
        )
        explanation["reasoning"].append(
            "No restricted advice, illegal intent, or policy violations detected."
        )

    # =========================
    # PERSONAL DATA HANDLING
    # =========================
    if phi:
        explanation["reasoning"].append(
            f"Sensitive personal identifiers detected and redacted: {', '.join(phi)}."
        )
        explanation["reasoning"].append(
            "Personal data handling performed in accordance with data governance principles."
        )

    return explanation

