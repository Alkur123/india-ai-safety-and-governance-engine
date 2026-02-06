
from engine.privacy.redact import redact_phi
from engine.harm.detector import detect_harm_category
from engine.harm.attack_vectors import detect_attack_vectors
from engine.harm.medical_intent import detect_medical_intent
from engine.policy import apply_policy
from engine.generation.llm import generate
from engine.verification.verify import verify
from engine.explainability.explain import explain
from engine.metrics.metrics import update_metrics
from engine.utils.uncertainty import assess_uncertainty


def run_system(query: str):
    # ---------- INITIALIZE GOVERNANCE STATE ----------
    timeline = []
    uncertainty = 0.0

    # ---------- PHI REDACTION ----------
    clean, phi = redact_phi(query)
    timeline.append(f"PII detected: {phi if phi else 'None'}")


    # ---------- HARM CLASSIFICATION ----------
    category = detect_harm_category(clean)
    timeline.append(f"Category detected: {category}")

    # ---------- ATTACK VECTOR DETECTION ----------
    attacks = detect_attack_vectors(clean)
    timeline.append(f"Attack vectors: {attacks}")

    # ---------- MEDICAL INTENT ----------
    medical_intent = None
    if category == "MEDICAL":
        medical_intent = detect_medical_intent(clean)

    # ---------- UNCERTAINTY ESTIMATION ----------
    uncertainty = assess_uncertainty(attacks, category, medical_intent)
    timeline.append(f"Uncertainty score: {uncertainty:.2f}")

    # ---------- ABSTAIN PATH ----------
    if uncertainty >= 0.6:
        update_metrics("ABSTAINED")
        return {
            "status": "ABSTAINED",
            "answer": "⚠️ Response withheld due to high uncertainty.",
            "category": category,
            "attacks": attacks,
            "phi": phi,
            "uncertainty": uncertainty,
            "timeline": timeline,
            "explain": explain(category, "ABSTAIN", attacks, phi)
        }

    # ---------- POLICY DECISION ----------
    policy = apply_policy(category, attacks, medical_intent)
    timeline.append(f"Policy decision: {policy['action']}")

    # ---------- BLOCK PATH ----------
    if policy["action"] == "BLOCK":
        update_metrics("BLOCKED")
        return {
            "status": "BLOCKED",
            "answer": "⚠️ Request blocked by safety policy.",
            "category": policy["category"],
            "attacks": attacks,
            "phi": phi,
            "uncertainty": uncertainty,
            "timeline": timeline,
            "explain": explain(category, "BLOCK", attacks, phi)
        }

    # ---------- GENERATION ----------
    ans = generate(clean)

    ok, _ = verify(ans, category)
    if not ok:
        update_metrics("ABSTAINED")
        timeline.append("Verification failed")
        return {
            "status": "ABSTAINED",
            "answer": "⚠️ Response withheld due to verification failure.",
            "category": category,
            "attacks": attacks,
            "phi": phi,
            "uncertainty": uncertainty,
            "timeline": timeline,
            "explain": explain(category, "ABSTAIN", attacks, phi)
        }

    update_metrics("ALLOWED")
    timeline.append("Response generated & verified")

    # ---------- ALLOW PATH ----------
    return {
        "status": "ALLOWED",
        "answer": ans,
        "category": category,
        "attacks": attacks,
        "phi": phi,
        "uncertainty": uncertainty,
        "timeline": timeline,
        "explain": explain(category, "ALLOW", attacks, phi)
    }
