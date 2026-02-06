def detect_medical_intent(q):
    q=q.lower()
    if any(x in q for x in ["dose","dosage","prescribe","how much"]):
        return "ADVICE"
    return "INFO"
