MET = {
    "total": 0,
    "allowed": 0,
    "blocked": 0,
    "abstained": 0,
    "support_mode": 0,
    "escalation": 0
}

# 🔹 NEW: Global switch to disable metrics during evaluation
METRICS_ENABLED = True


def update_metrics(t, eval_mode=False):

    # 🔒 Do not count evaluation runs in inference metrics
    if eval_mode or not METRICS_ENABLED:
        return

    MET["total"] += 1

    if t == "ALLOWED":
        MET["allowed"] += 1

    if t == "BLOCKED":
        MET["blocked"] += 1

    if t == "ABSTAINED":
        MET["abstained"] += 1

    # Support Mode counter
    if t == "SUPPORT_MODE":
        MET["support_mode"] += 1

    # Escalation counter
    if t == "ESCALATION":
        MET["escalation"] += 1


def get_metrics():
    return MET