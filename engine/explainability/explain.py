# engine/explainability/explain.py

def explain(category, action, attacks, phi, regulation=None):
    """
    Human-readable governance explanation.
    Designed for audits, demos, and compliance reviews.
    """

    triggered_attacks = [k for k, v in attacks.items() if v]

    explanation = {
        "decision_summary": {
            "final_action": action,
            "risk_category": category,
            "regulation": regulation or "General AI Safety Policy"
        },
        "reasoning": [],
        "signals": {
            "attack_vectors": triggered_attacks,
            "phi_detected": phi or []
        }
    }

    # ----------------------------
    # GOVERNANCE REASONING
    # ----------------------------
    if action == "BLOCK":
        explanation["reasoning"].append(
            f"Request violates safety policy under category '{category}'."
        )

        if regulation:
            explanation["reasoning"].append(
                f"Blocked to comply with {regulation}."
            )

        if triggered_attacks:
            explanation["reasoning"].append(
                f"Detected risk indicators: {', '.join(triggered_attacks)}."
            )

    elif action == "ABSTAIN":
        explanation["reasoning"].append(
            "Request contains ambiguity or elevated uncertainty."
        )
        explanation["reasoning"].append(
            "Response withheld to avoid unsafe or misleading output."
        )

    elif action == "ALLOW":
        explanation["reasoning"].append(
            "Request evaluated as safe under current governance rules."
        )
        explanation["reasoning"].append(
            "No policy violations or restricted advice detected."
        )

    # ----------------------------
    # PHI HANDLING
    # ----------------------------
    if phi:
        explanation["reasoning"].append(
            f"Sensitive personal data detected and redacted: {', '.join(phi)}."
        )

    return explanation

