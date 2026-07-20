import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv(override=True)

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")

foundry_client = AIProjectClient(
    endpoint=FOUNDRY_PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)

chat_client = foundry_client.get_openai_client()

response = chat_client.responses.create(
    model=MODEL_DEPLOYMENT_NAME,
    input="Say 'Hello from Microsoft Foundry!' and nothing else.",
)

print(f":white_check_mark: {response.output_text}")
print("\nYour environment is ready. You can start with the demos!")
