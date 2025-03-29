from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from config import settings

# your CRUD functions (for events, attendances, profiles, users)
import all_crud

# Initialize Azure client for inference
client = ChatCompletionsClient(
    endpoint="https://models.inference.ai.azure.com",
    credential=AzureKeyCredential(settings.GITHUB_TOKEN),
)


def call_azure_llm(prompt: str) -> str:
    """
    Call Azure's ChatCompletionsClient to get a summary and recommendations.
    """
    response = client.complete(
        messages=[
            UserMessage(prompt)
        ],
        model="DeepSeek-V3",  # or 'gpt-4', 'gpt-3.5-turbo'
        temperature=0.8,
        max_tokens=4096,
        top_p=0.9
    )
    return response.choices[0].message.content
