import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")

print(f"Endpoint:   {FOUNDRY_PROJECT_ENDPOINT}")
print(f"Model:      {MODEL_DEPLOYMENT_NAME}")

credential = DefaultAzureCredential()

# connection to foundry project
foundry_client = AIProjectClient(
    endpoint=FOUNDRY_PROJECT_ENDPOINT,
    credential=credential
)

chat_client = foundry_client.get_openai_client()

ai_response = chat_client.responses.create(
    model=MODEL_DEPLOYMENT_NAME,
    instructions="You are a friendly and knowledgeable assistant who gives clear, concise answers.",
    input="What are three practical uses of AI in everyday life?"
)

print(f"The AI replied:\n{ai_response.output_text}")

                                     
