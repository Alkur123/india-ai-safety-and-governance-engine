from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

INTENT_LABELS = [
    "safe question",
    "prompt injection",
    "data exfiltration",
    "policy violation"
]

def classify_intent(user_prompt: str):

    result = classifier(user_prompt, INTENT_LABELS)

    return {
        "intent": result["labels"][0],
        "confidence": float(result["scores"][0])
    }