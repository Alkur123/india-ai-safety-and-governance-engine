try:
    from engine.bedrock_adapter import generate_response
    BEDROCK_AVAILABLE = True
except:
    BEDROCK_AVAILABLE = False


# Local fallback model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def generate(q: str):

    prompt = f"""
You are a responsible AI assistant.

Respond clearly and helpfully.

User query:
{q}
"""

    # Try Bedrock first
    if BEDROCK_AVAILABLE:
        try:
            return generate_response(prompt)
        except:
            pass

    # Encode input
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generate response
    outputs = model.generate(**inputs, max_new_tokens=80)

    # Decode response
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return result