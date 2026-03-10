from transformers import pipeline

# load once
generator = pipeline(
    "text-generation",
    model="google/flan-t5-base"
)

def call_llm(prompt):

    result = generator(
        prompt,
        max_length=100
    )

    return result[0]["generated_text"]