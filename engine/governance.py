from engine.risk_engine import evaluate_risk


def governance_decision(intent, confidence):

    # Ensure confidence is safe numeric
    if confidence is None:
        confidence = 0.0

    risk = evaluate_risk(intent, confidence)

    if risk > 6:
        action = "BLOCKED"
        policy = "AIS-01"   # AI Safety Governance
    elif risk > 3:
        action = "REVIEW"
        policy = "AIS-00"   # Governance Review
    else:
        action = "ALLOW"
        policy = "GEN-00"   # General AI Usage

    return {
        "intent": intent,
        "confidence": confidence,
        "risk_score": risk,
        "policy_triggered": policy,
        "decision": action
    }