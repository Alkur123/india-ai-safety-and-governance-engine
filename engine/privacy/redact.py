import re

# ==============================
# PII / PHI PATTERNS (GLOBAL + INDIA)
# ==============================

PATTERNS = {
    # -------- Global --------
    "EMAIL": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
    "PHONE": r"\b\d{10}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",

    # -------- India-specific --------
    # Aadhaar: 12 digits, optional spaces
    "AADHAAR": r"\b\d{4}\s?\d{4}\s?\d{4}\b",

    # PAN: ABCDE1234F
    "PAN": r"\b[A-Z]{5}\d{4}[A-Z]\b",

    # Indian Mobile: +91XXXXXXXXXX or 0XXXXXXXXXX or XXXXXXXXXX
    "INDIAN_MOBILE": r"\b(\+91|0)?[6-9]\d{9}\b",

    # Voter ID: ABC1234567
    "VOTER_ID": r"\b[A-Z]{3}\d{7}\b",
}

# ==============================
# REDACTION FUNCTION
# ==============================

def redact_phi(text: str):
    """
    Detects and redacts sensitive personal information.
    Returns:
        redacted_text (str)
        detected_types (list[str])
    """
    found = []

    for label, pattern in PATTERNS.items():
        if re.search(pattern, text):
            found.append(label)
            text = re.sub(pattern, f"[REDACTED_{label}]", text)

    return text, found
