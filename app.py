import gradio as gr
import time

from engine.pipeline import run_system
from engine.metrics.metrics import get_metrics
from evaluation.eval_suite import run_evaluation


# ================================
# UI HELPERS
# ================================

def status_badge(status):
    return {
        "ALLOWED": "🟢 **ALLOWED**",
        "ABSTAINED": "🟡 **ABSTAINED**",
        "BLOCKED": "🔴 **BLOCKED**"
    }.get(status, status)


def compute_risk(status):
    if status == "BLOCKED":
        return 0.85
    if status == "ABSTAINED":
        return 0.60
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
    regulation = (
        explain.get("decision_summary", {})
               .get("regulation")
    )

    if not regulation or regulation == "General AI Safety Policy":
        return "📜 Indian Compliance Context: Not Applicable"

    return (
        "📜 **Indian Compliance Context**\n"
        f"• {regulation}"
    )


def language_badge(query):
    hindi_chars = any('\u0900' <= c <= '\u097F' for c in query)
    if hindi_chars:
        return (
            "🌐 Language Detected: Hindi (limited support)\n"
            "Multilingual governance support is part of the V3 roadmap."
        )
    return "🌐 Language Detected: English"


# ================================
# MAIN UI FUNCTION
# ================================

def ui(query):
    r = run_system(query)

    status = r.get("status", "UNKNOWN")
    score = compute_risk(status)

    explain_data = r.get("explain", {})
    regulation = explain_data.get("decision_summary", {}).get("regulation")

    return (
        status_badge(status),
        r.get("answer", ""),
        r.get("category", ""),
        risk_bar(score),
        format_attack_vectors(r.get("attacks", {})),
        (
            f"Final Decision: {status}\n"
            f"Category: {r.get('category')}\n"
            f"Regulation: {regulation or 'N/A'}\n"
            f"PHI Detected: {r.get('phi') or 'None'}\n\n"
            f"ℹ️ Deterministic, rule-based governance enforcement"
        ),
        indian_pii_badge(r.get("phi", [])),
        compliance_badge(explain_data),
        language_badge(query),
        f"{r.get('uncertainty', 0.0):.2f}",
        format_timeline(r.get("timeline", [])),
        explain_data
    )


def metrics_panel():
    return {
        "metrics": get_metrics(),
        "last_updated": time.strftime("%H:%M:%S")
    }


def eval_panel():
    result = run_evaluation()
    s = result["summary"]

    summary_text = (
        f"Precision: {s['precision']:.2f}\n"
        f"Recall: {s['recall']:.2f}\n\n"
        f"TP: {s['TP']}   (Correct blocks)\n"
        f"TN: {s['TN']}   (Correct allows)\n"
        f"FP: {s['FP']}   (Over-blocks)\n"
        f"FN: {s['FN']}   (Missed risks)"
    )

    return summary_text, result["details"]


# ================================
# GRADIO APP
# ================================

with gr.Blocks(title="AI Safety & Governance Engine") as demo:

    gr.Markdown("## 🛡️ AI Safety & Governance Engine")

    gr.Markdown(
        """
**Inference-time governance layer for LLM safety**
• Prompt injection & jailbreak detection  
• Medical, legal & financial advice enforcement (India-aware)  
• Indian PII redaction (Aadhaar, PAN, Mobile, Voter ID)  
• Policy-based **BLOCK / ABSTAIN / ALLOW**  
• Explainability + uncertainty modeling  
• Governance evaluation (FP / FN analysis)
"""
    )

    inp = gr.Textbox(
        label="User Query",
        placeholder="Enter a query to evaluate",
        lines=2
    )

    outputs = [
        gr.Markdown(label="Status"),
        gr.Textbox(label="Answer", lines=4),
        gr.Textbox(label="Decision Category"),
        gr.Textbox(label="Risk Assessment"),
        gr.Textbox(label="Attack Vector Analysis", lines=5),
        gr.Textbox(label="Decision Summary", lines=5),
        gr.Textbox(label="Indian PII Status", lines=4),
        gr.Textbox(label="Regulatory Context", lines=3),
        gr.Textbox(label="Language Awareness", lines=3),
        gr.Textbox(label="Uncertainty Score"),
        gr.Textbox(label="Governance Timeline", lines=6),
        gr.JSON(label="Explainability Trace"),
    ]

    gr.Button("Run Safety Engine").click(ui, inp, outputs)

    with gr.Accordion("🧩 System Architecture", open=False):
        gr.Markdown(
            """
User  
→ PHI Redaction  
→ Harm & Attack Detection  
→ Medical Intent  
→ Policy Engine  
→ **BLOCK / ABSTAIN / ALLOW**  
→ Generation  
→ Verification  
→ Explainability + Metrics
"""
        )

    gr.Markdown("### 📊 Inference-Time Metrics")
    metrics_output = gr.JSON(label="Metrics")
    gr.Button("Refresh Metrics").click(metrics_panel, outputs=metrics_output)

    with gr.Accordion("🧪 Governance Quality Dashboard", open=False):

        gr.Markdown(
            """
Evaluates **governance correctness**, not generation quality.
• TP – Correctly blocked  
• FP – Over-blocked  
• FN – Missed risks  
• TN – Correctly allowed
"""
        )

        eval_summary = gr.Textbox(label="Evaluation Summary", lines=8)
        eval_details = gr.JSON(label="Per-Prompt Results")

        gr.Button("Run Evaluation Suite").click(
            eval_panel,
            outputs=[eval_summary, eval_details]
        )

demo.launch()
