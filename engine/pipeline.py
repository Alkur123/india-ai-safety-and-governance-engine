import re

from engine.privacy.redact import redact_phi
from engine.harm.detector import (
    detect_harm_category,
    expand_euphemisms,
    detect_split_prompt,
)
from engine.harm.attack_vectors import detect_attack_vectors
from engine.harm.medical_intent import detect_medical_intent
from engine.policy import apply_policy
from engine.generation.llm import generate
from engine.verification.verify import verify
from engine.explainability.explain import explain
from engine.metrics.metrics import update_metrics
from engine.utils.uncertainty import assess_uncertainty
from engine.session.memory import update_session_memory

# ================= NEW IMPORTS (Governance Layer) =================
from engine.intent_classifier import classify_intent
from engine.governance import governance_decision

# ================= SEMANTIC ENGINE =================
from engine.harm.semantic import is_semantically_safe  


# ============================================================
# SUPPORT MODE RESPONSE
# ============================================================

def generate_support_response(query: str):
    return (
        "I can sense that you might be going through something difficult.\n\n"
        "You are not alone. If you are feeling overwhelmed, consider:\n"
        "• Reaching out to someone you trust\n"
        "• Taking slow breaths to ground yourself\n"
        "• Seeking professional help if this feels urgent\n\n"
        "If this is an emergency, please contact local emergency services immediately."
    )


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def run_system(query: str, session_id: str = "default", eval_mode: bool = False):

    timeline = []
    confidence_source = "rule"

    # STEP 0 – Euphemism expansion
    expanded_query = expand_euphemisms(query)
    timeline.append("Euphemism expansion complete")

    # ================= INTENT CLASSIFIER =================
    if not eval_mode:
        intent_result = classify_intent(expanded_query)

        gov_decision = governance_decision(
            intent_result["intent"],
            intent_result["confidence"]
        )

        timeline.append(
            f"Intent: {gov_decision['intent']} | "
            f"Confidence: {gov_decision['confidence']:.2f} | "
            f"Risk Score: {gov_decision['risk_score']} | "
            f"Decision: {gov_decision['decision']}"
        )

    # STEP 1 – Split detection
    split_detected = detect_split_prompt(query)

    if split_detected:
        actual_query = query.split("but")[-1]
        expanded_query = expand_euphemisms(actual_query)
        timeline.append("Split prompt detected")

    detection_query = expanded_query

    # STEP 2 – PII detection
    clean, phi = redact_phi(detection_query)
    timeline.append(f"PII detected: {phi if phi else 'None'}")

    # STEP 3 – Attack vector analysis
    attacks = detect_attack_vectors(clean)
    attacks["split_prompt"] = split_detected
    timeline.append("Attack vectors analyzed")

    # ==========================================================
    # STEP 4 – SEMANTIC SAFETY CHECK (REAL ENGINE)
    # ==========================================================

    safe_intent, semantic_score = is_semantically_safe(clean)

    timeline.append(f"Semantic safety check: {semantic_score}")

    if safe_intent:
        attacks["prompt_injection"] = False
        attacks["obfuscation"] = False
        attacks["urgency_pressure"] = False
        timeline.append("Semantic override cleared attack flags")

    # STEP 6 – Category detection
    detected_category = detect_harm_category(clean)
    timeline.append(f"Detected category: {detected_category}")

    # ==========================================================
    # SESSION MEMORY
    # ==========================================================

    session_state = update_session_memory(
        session_id,
        query,
        detected_category
    )

    timeline.append(
        f"Session risk: {session_state['cumulative_risk']:.2f}, "
        f"Distress: {session_state['distress_score']:.2f}"
    )

    if session_state["escalation_flag"]:
        update_metrics("ESCALATION", eval_mode=eval_mode)
        timeline.append("Session escalation triggered")

    # ==========================================================
    # SESSION RISK HARD LIMIT
    # ==========================================================

    SESSION_RISK_THRESHOLD = 10

    if session_state["cumulative_risk"] >= SESSION_RISK_THRESHOLD:

        timeline.append(
            f"Session Risk Threshold Exceeded: {session_state['cumulative_risk']:.2f}"
        )

        timeline.append("⚠️ Session blocked due to repeated high-risk interactions")

        timeline.append(
            f"✔ Session Risk Accumulated: {session_state['cumulative_risk']:.2f}"
        )

        update_metrics("BLOCKED", eval_mode=eval_mode)

        return {
            "status": "BLOCKED",
            "answer": "⚠️ Session risk threshold exceeded. Session blocked due to repeated high-risk interactions.",
            "category": "SESSION_RISK_BLOCK",
            "attacks": attacks,
            "phi": phi,
            "uncertainty": 1.0,
            "timeline": timeline,
            "explain": {},
            "confidence_source": confidence_source,
            "session_state": session_state,
        }

    # ==========================================================
    # UNCERTAINTY
    # ==========================================================

    medical_intent = None

    if detected_category == "MEDICAL":
        medical_intent = detect_medical_intent(clean)

    uncertainty = assess_uncertainty(attacks, detected_category, medical_intent)

    if session_state["cumulative_risk"] > 0.6:
        uncertainty += 0.2

    if session_state["distress_score"] > 0.6:
        uncertainty += 0.2

    uncertainty = min(uncertainty, 1.0)

    timeline.append(f"Uncertainty score: {uncertainty:.2f}")

    # ==========================================================
    # POLICY
    # ==========================================================

    policy = apply_policy(
        detected_category,
        attacks,
        medical_intent,
        uncertainty
    )

    timeline.append(
        f"Policy Triggered: {policy.get('rule_id','N/A')} | "
        f"Regulation: {policy.get('regulation','Unknown Regulation')}"
    )

    # Skip explainability during evaluation
    explain_result = explain(
        policy["category"],
        policy["action"],
        attacks,
        phi,
        policy.get("regulation")
    )



    # ==========================================================
    # SUPPORT MODE
    # ==========================================================

    if policy["action"] == "SUPPORT":

        timeline.append("Action: SUPPORT")

        timeline.append(
            f"✔ Session Risk Accumulated: {session_state['cumulative_risk']:.2f}"
        )

        update_metrics("SUPPORT_MODE", eval_mode=eval_mode)

        return {
            "status": "SUPPORT_MODE",
            "answer": generate_support_response(query),
            "category": policy["category"],
            "attacks": attacks,
            "phi": phi,
            "uncertainty": uncertainty,
            "timeline": timeline,
            "explain": explain_result,
            "confidence_source": confidence_source,
            "session_state": session_state,
        }

    # ==========================================================
    # ABSTAIN
    # ==========================================================

    if policy["action"] == "ABSTAIN":

        timeline.append("Action: ABSTAIN")

        timeline.append(
            f"✔ Session Risk Accumulated: {session_state['cumulative_risk']:.2f}"
        )

        update_metrics("ABSTAINED", eval_mode=eval_mode)

        return {
            "status": "ABSTAINED",
            "answer": "⚠️ Response withheld due to uncertainty.",
            "category": policy["category"],
            "attacks": attacks,
            "phi": phi,
            "uncertainty": uncertainty,
            "timeline": timeline,
            "explain": explain_result,
            "confidence_source": confidence_source,
            "session_state": session_state,
        }

    # ==========================================================
    # BLOCK
    # ==========================================================

    if policy["action"] == "BLOCK":

        timeline.append("Action: BLOCKED")

        timeline.append(
            f"✔ Session Risk Accumulated: {session_state['cumulative_risk']:.2f}"
        )

        update_metrics("BLOCKED", eval_mode=eval_mode)

        return {
            "status": "BLOCKED",
            "answer": "⚠️ Request blocked under governance policy.",
            "category": policy["category"],
            "attacks": attacks,
            "phi": phi,
            "uncertainty": uncertainty,
            "timeline": timeline,
            "explain": explain_result,
            "confidence_source": confidence_source,
            "session_state": session_state,
        }

    # ==========================================================
    # GENERATE
    # ==========================================================

    ans = "" if eval_mode else generate(clean)

    # ==========================================================
    # VERIFY
    # ==========================================================

    if not eval_mode and policy["category"] != "SAFE":

        ok, _ = verify(ans, policy["category"])

        if not ok:

            timeline.append("Post-generation verification failed")

            timeline.append(
                f"✔ Session Risk Accumulated: {session_state['cumulative_risk']:.2f}"
            )

            update_metrics("ABSTAINED", eval_mode=eval_mode)

            return {
                "status": "ABSTAINED",
                "answer": "⚠️ Response withheld after verification failure.",
                "category": policy["category"],
                "attacks": attacks,
                "phi": phi,
                "uncertainty": uncertainty,
                "timeline": timeline,
                "explain": explain_result,
                "confidence_source": confidence_source,
                "session_state": session_state,
            }

    timeline.append("Action: ALLOWED")

    timeline.append(
        f"✔ Session Risk Accumulated: {session_state['cumulative_risk']:.2f}"
    )

    update_metrics("ALLOWED", eval_mode=eval_mode)

    return {
        "status": "ALLOWED",
        "answer": ans,
        "category": policy["category"],
        "attacks": attacks,
        "phi": phi,
        "uncertainty": uncertainty,
        "timeline": timeline,
        "explain": explain_result,
        "confidence_source": confidence_source,
        "session_state": session_state,
    }