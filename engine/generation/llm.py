from transformers import pipeline

# HF Spaces compatible pipeline (2026-safe)
gen = pipeline(
    task="text-generation",
    model="google/flan-t5-base",
    max_new_tokens=150
)

def generate(q: str):
    prompt = f"Explain safely:\n{q}"
    out = gen(prompt)
    return out[0]["generated_text"]
