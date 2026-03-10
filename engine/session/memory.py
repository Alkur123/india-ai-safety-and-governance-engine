# engine/session/memory.py

SESSION_STORE = {}

# ==============================
# Distress Signal Sets (Hybrid)
# ==============================

STRONG_DISTRESS = [
    "i want to die",
    "i want to kill myself",
    "end my life",
    "nothing matters anymore",
    "i can't go on",
]

MODERATE_DISTRESS = [
    "i feel hopeless",
    "i feel empty",
    "i feel alone",
    "help me",
    "i want it to stop",
]

LIGHT_DISTRESS = [
    "i feel sad",
    "tired of everything",
    "overwhelmed",
    "stressed",
]

# ==============================
# Risk Weights
# ==============================

CATEGORY_RISK = {
    "SAFE": 0.05,
    "PROMPT_INJECTION": 2.5,
    "ILLEGAL": 3.5,
    "VIOLENCE": 3.5,
    "SEXUAL": 3.5,
    "MEDICAL": 1.5,
    "LEGAL": 1.5,
    "FINANCIAL": 1.5,
    "SELF_HARM": 3.5,
    "SELF_HARM_PASSIVE": 2.0
}

# ==============================
# NEW: Slow-Burn Jailbreak Signals
# ==============================

JAILBREAK_SIGNALS = [
    "ignore previous",
    "bypass safety",
    "developer mode",
    "act as",
    "override system"
]


# ==============================
# Initialize Session
# ==============================

def initialize_session():
    return {
        "turn_count": 0,
        "cumulative_risk": 0.0,
        "distress_score": 0.0,
        "escalation_flag": False,
        "last_category": None,
        "history": []   # NEW
    }


# ==============================
# Distress Scoring
# ==============================

def compute_distress_score(query: str):
    q = query.lower()
    score = 0.0

    for phrase in STRONG_DISTRESS:
        if phrase in q:
            score += 0.6

    for phrase in MODERATE_DISTRESS:
        if phrase in q:
            score += 0.3

    for phrase in LIGHT_DISTRESS:
        if phrase in q:
            score += 0.15

    return min(score, 1.0)


# ==============================
# Temporal Decay
# ==============================

def apply_temporal_decay(session):
    session["cumulative_risk"] *= 0.9
    session["distress_score"] *= 0.85


# ==============================
# Update Session Memory
# ==============================

def update_session_memory(session_id, query, detected_category):

    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = initialize_session()

    session = SESSION_STORE[session_id]

    session["turn_count"] += 1

    # NEW: store query history
    session["history"].append(query.lower())

    # Apply decay
    apply_temporal_decay(session)

    # ==============================
    # Risk accumulation
    # ==============================

    risk_increment = CATEGORY_RISK.get(detected_category, 0.5)
    session["cumulative_risk"] += risk_increment

    # ==============================
    # NEW: Slow-Burn Jailbreak Detection
    # ==============================

    signal_hits = sum(
        any(signal in q for signal in JAILBREAK_SIGNALS)
        for q in session["history"][-5:]
    )

    if signal_hits >= 3:
        session["cumulative_risk"] += 4

    # ==============================
    # Distress update
    # ==============================

    distress_increment = compute_distress_score(query)
    session["distress_score"] += distress_increment
    session["distress_score"] = min(session["distress_score"], 1.0)

    # ==============================
    # Escalation logic
    # ==============================

    if (
        session["cumulative_risk"] > 10
        or session["distress_score"] > 0.6
    ):
        session["escalation_flag"] = True

    session["last_category"] = detected_category

    return session