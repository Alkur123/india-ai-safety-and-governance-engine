def diagram():
    return """
User Query
   ↓
PHI Redaction
   ↓
Harm + Attack Detection
   ↓
Policy Engine
   ↓
Generate / Block / Abstain
   ↓
Verification
   ↓
Explainability + Metrics
"""
