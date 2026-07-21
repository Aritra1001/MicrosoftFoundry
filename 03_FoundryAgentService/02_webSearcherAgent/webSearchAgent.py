import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchPreviewTool

load_dotenv()

# taking the env variables
my_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model_name = os.getenv("MODEL_DEPLOYMENT_NAME")


# creating the foundry client
foundry_client = AIProjectClient(
    endpoint=my_endpoint,
    credential=DefaultAzureCredential()
)


# create the web searcher agent
search_agent_name="live-search-assistant"

search_agent = foundry_client.agents.create_version(
    agent_name=search_agent_name,
    definition=PromptAgentDefinition(
        model=model_name,
        instructions="You are a research assistant that searches the web to find current, accurate answers to user questions.",
        tools=[
            WebSearchPreviewTool()
        ]
    )
)


# creating the openai chat client to send msg to agent
chat_client = foundry_client.get_openai_client()

chat_session = chat_client.conversations.create()
print(f"Created conversation with id: {chat_session.id}")


# sending our question to the web search agent
question="What are the top trending technologies in 2026?"

response = chat_client.responses.create(
    conversation=chat_session.id,
    extra_body={
        "agent_reference": {
            "name": search_agent_name,
            "type": "agent_reference"
        }
    },
    input=question
)

print(f"Agent Response: {response.output_text}")
