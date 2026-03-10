import re

# Added jailbreak detection patterns
JAILBREAK_PATTERNS = [
    "dan mode",
    "developer mode",
    "bypass safety",
    "bypass content policy",
    "ignore safety guidelines",
    "ignore your instructions",
    "pretend you are an unrestricted ai",
    "simulate an ai without rules",
    "act as an ai without limitations"
]


def detect_attack_vectors(query: str):
    q = query.lower()

    return {
        # -------------------------
        # Prompt Injection / Jailbreak
        # -------------------------
        "prompt_injection": any(
            t in q for t in [
                "ignore previous",
                "ignore above",
                "bypass",
                "override system",
                "forget instructions",
                "you are no longer",
                "developer mode"
            ]
        ) or any(p in q for p in JAILBREAK_PATTERNS),

        # -------------------------
        # Jailbreak Pattern Detection (new signal)
        # -------------------------
        "jailbreak_attempt": any(
            p in q for p in JAILBREAK_PATTERNS
        ),

        # -------------------------
        # Obfuscation / Evasion
        # -------------------------
        # Detect real obfuscation patterns instead of normal sentences
        "obfuscation": any(
            t in q for t in [
                "base64",
                "rot13",
                "encode this",
                "decode this",
                "convert to binary",
                "hex encoding"
            ]
        ),

        # -------------------------
        # Escalation Language
        # -------------------------
        "urgency_pressure": any(
            t in q for t in [
                "urgent",
                "immediately",
                "right now",
                "asap",
                "emergency"
            ]
        ),

        # -------------------------
        # Repeated Harm Amplification
        # -------------------------
        "repeat_intent": q.count("?") >= 3 or q.count("!") >= 3,
    }
    