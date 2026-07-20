# azure-mgmt-cognitiveservices`** — the Azure management SDK that Lists available models, create/delete deployments
# azure-ai-projects`** — the Foundry SDK that lets us list deployments and test them. List existing deployments, test models via OpenAI client

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import (
    Deployment,
    DeploymentProperties,
    DeploymentModel,
    Sku
)
from azure.ai.projects import AIProjectClient


load_dotenv(override=True)

my_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")       # Foundry project URL (for testing later)
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")       # Azure subscription ID
resource_group = os.getenv("AZURE_RESOURCE_GROUP")         # Resource group name
account_name = os.getenv("FOUNDRY_ACCOUNT_NAME")           # Cognitive Services account name

# Quick check — make sure nothing is missing
# print("Endpoint:      ", my_endpoint)
# print("Subscription:  ", subscription_id)
# print("Resource group:", resource_group)
# print("Account name:  ", account_name)

if not my_endpoint or not subscription_id or not resource_group or not account_name:
    print("WARNING: One or more values are empty. Fill in your .env file before continuing.")


credential = DefaultAzureCredential()

# This client talks to the Azure Resource Manager
mgmt_client = CognitiveServicesManagementClient(
    credential = credential,
    subscription_id = subscription_id
)

foundry_client = AIProjectClient(
    endpoint = my_endpoint,
    credential = credential
)

# checking the available models list in my resource region
available_models = mgmt_client.accounts.list_models(
    resource_group_name = resource_group,
    account_name = account_name
)

# print("Available models for deployment:\n")
# model_count = 0
# for model in available_models:
#     model_count += 1
#     capabilities = ", ".join(model.capabilities.keys()) if model.capabilities else "N/A"
#     print(f"  {model_count:3d}. {model.name:35s}  v{model.version:15s}  [{capabilities}]")
#     # Stop after 30 to keep the output manageable
#     if model_count >= 30:
#         print(f"\n  ... showing first 30 of many models.")
#         break

# print(f"\nTip: Visit https://ai.azure.com/catalog to browse the full catalog with descriptions.")


# deploying a model
model_name = "gpt-5-mini"
model_format = "OpenAI"
model_version = "2025-08-07" 
deployment_name = "gpt-5-mini_test_deployment"

found = False
model_sku_name = None
model_sku_capacity = None

for model in mgmt_client.accounts.list_models(
    resource_group_name = resource_group,
    account_name = account_name
):
    if model.name == model_name:
        found = True
        capabilities = ", ".join(model.capabilities.keys()) if model.capabilities else "N/A"
        print(f"Model found!")
        print(f"  Name:         {model.name}")
        print(f"  Version:      {model.version}")
        print(f"  Format:       {model.format}")
        print(f"  Capabilities: {capabilities}")

        if model.skus:
            sku_names = [s.name for s in model.skus]
            print(f"  Available SKUs: {', '.join(sku_names)}")

            # Use the first SKU — this is typically the recommended one 
            first_sku = model.skus[0]
            model_sku_name = first_sku.name
            model_sku_capacity = first_sku.capacity.default if first_sku.capacity else 10
            print(f"\n  Selected SKU for deployment:")
            print(f"    SKU:      {model_sku_name}")
            print(f"    Capacity: {model_sku_capacity}")
        break

# if not found:
#     print(f"Model '{model_name}' version '{model_version}' was not found!")
#     print("Check the output from Step 4 for available models and versions.")    
print(found, model_sku_name)
    
if not found or model_sku_name is None:
        print("ERROR: Model not found in Step 5. Cannot deploy. Check the model name and version above.")
else:
        # Build the deployment definition
        deployment = Deployment(
            properties=DeploymentProperties(
                model=DeploymentModel(
                    name=model_name,
                    version=model_version,
                    format=model_format
                ),
                version_upgrade_option="NoAutoUpgrade",
            ),
            sku=Sku(
                name=model_sku_name,
                capacity=model_sku_capacity
            )
        )

        print(f"Deployment configuration:")
        print(f"  Model:    {model_name} v{model_version}")
        print(f"  SKU:      {model_sku_name}")
        print(f"  Capacity: {model_sku_capacity}")

        try:
            print(f"\nDeploying '{model_name}' as '{deployment_name}'...")
            print("This usually takes about 1 minute. Please wait...\n")

            poller = mgmt_client.deployments.begin_create_or_update(
                resource_group_name=resource_group,
                account_name=account_name,
                deployment_name=deployment_name,
                deployment=deployment
            )
            result = poller.result()

            print(f"Deployment complete!")
            print(f"  Name:   {result.name}")
            print(f"  Model:  {result.properties.model.name} v{result.properties.model.version}")
            print(f"  Status: {result.properties.provisioning_state}")
            print(f"  SKU:    {result.sku.name} (capacity: {result.sku.capacity})")

        except HttpResponseError as e:
            print(f"Deployment failed with status code {e.status_code} ({e.reason}).")
            # The error response often contains a structured message with more details.
            print("\n--- Azure API Error ---")
            if e.error:
                print(f"Code:    {e.error.code}")
                print(f"Message: {e.error.message}")
            print("\nFull response body:")
            print(e.response.text)
            print("-----------------------\n")
            print("Common causes for deployment failures include:")
            print("- Incorrect SKU or capacity for the selected model and region.")
            print("- Reaching a regional quota for deployments or total transaction units (TPM).")
            print("- Insufficient permissions for your credential (ensure it has 'Cognitive Services Contributor' role).")


# listing the deployed models
print("All deployments in the project")
for dep in foundry_client.deployments.list():
    print(f"  Name:      {dep.name}")
    print(f"  Model:     {dep.model_name}")
    print(f"  Publisher: {dep.model_publisher}")
    print(f"  Version:   {dep.model_version}")
    print(f"  Type:      {dep.type}")
    print()


# testing the deployed model
chat_client = foundry_client.get_openai_client()

print(f"Sending a test question to '{deployment_name}'...\n")

ai_response = chat_client.responses.create(
    model=deployment_name,
    instructions="You are a helpful and concise assistant.",
    input="Explain what a model deployment is in Microsoft Foundry in two sentences."
)

print(f"The model replied:\n{ai_response.output_text}")