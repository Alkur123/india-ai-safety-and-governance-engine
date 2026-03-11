import gradio as gr
import time
import uuid

from engine.pipeline import run_system
from engine.metrics.metrics import get_metrics
from evaluation.eval_suite import run_evaluation


# ====================================
# SESSION INITIALIZATION
# ====================================

SESSION_ID = str(uuid.uuid4())


# ====================================
# UI HELPERS
# ====================================

def decision_banner(status):
    colors = {
        "ALLOWED": "🟢",
        "ABSTAINED": "🟡",
        "BLOCKED": "🔴",
        "SUPPORT_MODE": "🟣"
    }
    emoji = colors.get(status, "⚪")

    return f"""
# {emoji} {status}
---
"""


def compute_risk(status, category):
    if category == "SELF_HARM":
        return 0.90
    if status == "BLOCKED":
        return 0.85
    if status == "ABSTAINED":
        return 0.60
    if status == "SUPPORT_MODE":
        return 0.50
    return 0.20


def risk_bar(score):
    filled = int(score * 10)
    bar = "█" * filled + "░" * (10 - filled)

    if score < 0.3:
        return f"🟢 {bar}  {score:.2f} (LOW)"
    elif score < 0.7:
        return f"🟡 {bar}  {score:.2f} (MEDIUM)"
    else:
        return f"🔴 {bar}  {score:.2f} (HIGH)"


def format_attack_vectors(attacks):
    if not attacks:
        return "No attack vectors detected"

    return "\n".join(
        f"{'❌' if v else '✅'} {k}: {'DETECTED' if v else 'Clear'}"
        for k, v in attacks.items()
    )


def format_timeline(timeline):
    if not timeline:
        return "No timeline available"

    return "\n".join(
        f"{i*5:02d}ms : {step}"
        for i, step in enumerate(timeline)
    )


def indian_pii_badge(phi):
    if not phi:
        return "🇮🇳 Indian PII Check: Clear"

    lines = ["🇮🇳 **Indian PII Detected**"]
    for p in phi:
        lines.append(f"• {p}")
    return "\n".join(lines)


def compliance_badge(explain):
    if not explain:
        return "📜 Indian Compliance Context: Not Applicable"

    decision_summary = explain.get("decision_summary") or {}

    regulation = (
        decision_summary.get("regulation")
        or decision_summary.get("regulation_applied")
    )

    if not regulation:
        return "📜 Indian Compliance Context: Not Applicable"

    return (
        "📜 **Indian Compliance Context**\n"
        f"• {regulation}"
    )


def language_badge(query):
    if not query:
        return "🌐 Language Detection Unavailable"

    hindi_chars = any('\u0900' <= c <= '\u097F' for c in query)
    if hindi_chars:
        return "🌐 Language Detected: Hindi (limited support)"
    return "🌐 Language Detected: English"


# ====================================
# MAIN UI FUNCTION
# ====================================

def ui(query):
    try:
        r = run_system(query, session_id=SESSION_ID) or {}

        status = r.get("status", "UNKNOWN")
        category = r.get("category", "N/A")

        score = compute_risk(status, category)

        explain_data = r.get("explain") or {}
        attacks = r.get("attacks") or {}
        phi = r.get("phi") or []
        timeline = r.get("timeline") or ["No internal steps recorded"]
        session_state = r.get("session_state") or {}

        return (
            decision_banner(status),
            r.get("answer", ""),
            category,
            risk_bar(score),
            compliance_badge(explain_data),
            format_attack_vectors(attacks),
            format_timeline(timeline),
            indian_pii_badge(phi),
            language_badge(query),
            f"{r.get('uncertainty', 0.0):.2f}",
            explain_data,
            session_state
        )

    except Exception as e:
        return (
            f"🔴 ERROR: {str(e)}",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            {},
            {}
        )


# ====================================
# METRICS PANEL
# ====================================

def metrics_panel():
    try:
        metrics = get_metrics()
        formatted = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
        return f"{formatted}\n\nLast Updated: {time.strftime('%H:%M:%S')}"
    except Exception as e:
        return f"Metrics error: {str(e)}"


# ====================================
# EVALUATION PANEL
# ====================================

def eval_panel():
    try:
        result = run_evaluation()
        s = result.get("summary", {})

        summary_text = (
            f"Precision: {s.get('precision', 0):.2f}\n"
            f"Recall: {s.get('recall', 0):.2f}\n\n"
            f"TP: {s.get('TP', 0)}\n"
            f"TN: {s.get('TN', 0)}\n"
            f"FP: {s.get('FP', 0)}\n"
            f"FN: {s.get('FN', 0)}"
        )

        return summary_text, result.get("details", [])

    except Exception as e:
        return f"Evaluation error: {str(e)}", []


# ====================================
# GRADIO APP
# ====================================

with gr.Blocks(title="Indian AI Governance Engine") as demo:

    gr.Markdown("## 🛡️ Indian AI Governance Engine")

    gr.Markdown("""
Inference-time governance middleware for LLM safety  
Designed for inference-time LLM safety governance in regulated Indian environments.
• Prompt injection & jailbreak detection  
• Medical, legal & financial advisory enforcement  
• Indian PII redaction  
• Policy-based BLOCK / ABSTAIN / SUPPORT MODE / ALLOW  
• Explainability + uncertainty modeling  
• Session-based risk accumulation (S2.5)
""")

    inp = gr.Textbox(label="User Query", placeholder="Enter a query to evaluate", lines=2)

    # ================================
    # LAYER 1 — OUTCOME
    # ================================

    gr.Markdown("### 🎯 Outcome")

    decision_output = gr.Markdown()
    answer_output = gr.Textbox(label="Answer", lines=4)
    category_output = gr.Textbox(label="Decision Category")
    risk_output = gr.Textbox(label="Risk Assessment")
    compliance_output = gr.Textbox(label="Indian Compliance Context")

    # ================================
    # LAYER 2 — GOVERNANCE REASONING
    # ================================

    gr.Markdown("### 🧠 Governance Reasoning")

    attacks_output = gr.Textbox(label="Attack Vector Analysis", lines=5)
    timeline_output = gr.Textbox(label="Governance Timeline", lines=6)
    pii_output = gr.Textbox(label="Indian PII Status", lines=4)
    language_output = gr.Textbox(label="Language Awareness")
    uncertainty_output = gr.Textbox(label="Uncertainty Score")

    # ================================
    # LAYER 3 — TECHNICAL TRANSPARENCY
    # ================================

    with gr.Accordion("🔍 Technical Transparency", open=False):
        explain_output = gr.JSON(label="Explainability Trace")
        session_output = gr.JSON(label="Session Memory State")

    gr.Button("Run Safety Engine").click(
        ui,
        inp,
        [
            decision_output,
            answer_output,
            category_output,
            risk_output,
            compliance_output,
            attacks_output,
            timeline_output,
            pii_output,
            language_output,
            uncertainty_output,
            explain_output,
            session_output
        ]
    )

    # ================================
    # SYSTEM ARCHITECTURE
    # ================================

    with gr.Accordion("🧩 System Architecture", open=False):
        gr.Markdown("""
User  
→ PHI Redaction  
→ Harm & Attack Detection  
→ Intent Detection  
→ Session Memory (S2.5)  
→ Policy Engine (Stateful Escalation)  
→ BLOCK / ABSTAIN / SUPPORT MODE / ALLOW  
→ Generation  
→ Verification  
→ Explainability + Metrics
""")

    # ================================
    # METRICS
    # ================================

    gr.Markdown("### 📊 Inference-Time Metrics")
    metrics_output = gr.Textbox(label="Current System Metrics", lines=6)
    gr.Button("Refresh Metrics").click(metrics_panel, outputs=metrics_output)

    # ================================
    # GOVERNANCE EVALUATION
    # ================================

    with gr.Accordion("🧪 Governance Quality Dashboard", open=False):
        eval_summary = gr.Textbox(label="Evaluation Summary", lines=8)
        eval_details = gr.JSON(label="Per-Prompt Results")

        gr.Button("Run Evaluation Suite").click(
            eval_panel,
            outputs=[eval_summary, eval_details]
        )

demo.launch()
