import re

def detect_harm_category(query: str) -> str:
    q = query.lower()

    # =========================
    # SELF-HARM / SUICIDE
    # =========================
    SELF_HARM = [
        "suicide", "kill myself", "end my life", "want to die",
        "self harm", "hurt myself", "cut myself",
        "jump off", "overdose", "hang myself", "unalive myself"
    ]

    # =========================
    # SEXUAL / ABUSE
    # =========================
    SEXUAL = [
        "porn", "explicit", "nude", "naked", "rape",
        "child abuse", "underage", "minor", "sexual assault"
    ]

    # =========================
    # VIOLENCE / TERROR
    # =========================
    VIOLENCE = [
        "kill", "murder", "shoot", "stab", "attack",
        "bomb", "terrorist", "weapon", "gun", "riot", "lynch"
    ]

    # =========================
    # ILLEGAL / CRIME
    # =========================
    ILLEGAL = [
        "hack", "phish", "malware", "ransomware", "ddos",
        "fraud", "fake id", "credit card fraud",
        "cocaine", "heroin", "meth", "lsd", "drugs",
        "sell drugs", "buy drugs", "illegal weapon"
    ]

    # =========================
    # MEDICAL ADVICE (INDIA-SENSITIVE)
    # =========================
    MEDICAL = [
        "prescribe", "prescription", "dosage", "dose",
        "medicine", "medication", "what should i take",
        "which tablet", "which drug", "how much medicine",
        "treatment for", "cure for"
    ]

    # =========================
    # LEGAL ADVICE (INDIA)
    # =========================
    LEGAL = [
        "legal advice", "lawyer advice", "can i sue",
        "is this legal", "file a case", "court case",
        "ipc section", "crpc", "fir", "bail process"
    ]

    # =========================
    # FINANCIAL / INVESTMENT ADVICE (SEBI)
    # =========================
    FINANCIAL = [
        "investment advice", "stock tips", "buy shares",
        "sell shares", "mutual fund advice",
        "crypto investment", "trading tips", "portfolio advice"
    ]

    # =========================
    # CATEGORY CHECKS (ORDER MATTERS)
    # =========================
    for t in SELF_HARM:
        if t in q:
            return "SELF_HARM"

    # obfuscated self-harm (s*u*i*c*i*d*e)
    if re.search(r"s[\W_]*u[\W_]*i[\W_]*c[\W_]*i[\W_]*d[\W_]*e", q):
        return "SELF_HARM"

    for t in SEXUAL:
        if t in q:
            return "SEXUAL"

    for t in VIOLENCE:
        if t in q:
            return "VIOLENCE"

    for t in ILLEGAL:
        if t in q:
            return "ILLEGAL"

    for t in MEDICAL:
        if t in q:
            return "MEDICAL"

    for t in LEGAL:
        if t in q:
            return "LEGAL"

    for t in FINANCIAL:
        if t in q:
            return "FINANCIAL"

    return "SAFE"

