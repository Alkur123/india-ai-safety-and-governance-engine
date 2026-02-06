def assess_uncertainty(attacks, category, medical_intent):
    score=0
    if any(attacks.values()): score+=0.4
    if category=="MEDICAL" and medical_intent=="INFO": score+=0.3
    return min(score,1.0)
