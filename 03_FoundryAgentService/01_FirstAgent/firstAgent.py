import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")  

# foundry client
foundry_client = AIProjectClient(
    endpoint=FOUNDRY_PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)

# creating the agent 
agent_name = "fitness-coach"

coach_agent = foundry_client.agents.create_version(
    agent_name=agent_name,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT_NAME,
        instructions="You are a friendly and motivating fitness coach. You help people create workout plans, give exercise tips, and encourage healthy habits. Always be supportive and positive."
    )
)

print(f"Agent created (id: {coach_agent.id}, name: {coach_agent.name}), version: {coach_agent.version}")


#  starting a conversation with agent
chat_client = foundry_client.get_openai_client()

chat_session = chat_client.conversations.create()

print(f"Created conversation with id: {chat_session.id}")


# chat with the agent
is_chatting = True

while is_chatting:
    user_message = input("You: ")

    if user_message.lower() in ["exit", "quit"]:
        is_chatting = False
        print("Ending the conversation. Stay active and healthy!")
    else:
        coach_reply = chat_client.responses.create(
            conversation=chat_session.id,
            extra_body={
                "agent": {
                    "name": agent_name,
                    "type": "agent_reference"
                }
            },
            input=user_message
        )
        print(f"Coach: {coach_reply.output_text}")