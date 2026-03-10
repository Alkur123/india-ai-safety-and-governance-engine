import boto3
import json

# Create Bedrock runtime client
client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Claude 3.5 Sonnet model ID
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

def generate_response(prompt: str) -> str:

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 400,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body)
    )

    response_body = json.loads(response["body"].read())

    return response_body["content"][0]["text"]