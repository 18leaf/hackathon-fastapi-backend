from pyobjectid import PyObjectId  # For conversion in our model, if needed
from all_crud import create_ai_summary
# existing CRUD join function for personas
from all_crud import get_event_personas
from typing import List, Dict, Any
from datetime import datetime
import asyncio
# our previously defined CRUD join for personas
from all_crud import get_event_personas
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from config import settings

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
            # Optional: add a system message to set context
            SystemMessage(
                "You are an expert assistant skilled in analyzing user persona data, "
                "extracting sentiment insights, and suggesting innovative event recommendations."
            ),
            UserMessage(prompt)
        ],
        model="DeepSeek-V3",  # You can switch this to 'gpt-4' or 'gpt-3.5-turbo'
        temperature=0.8,
        max_tokens=2048,
        top_p=0.9
    )
    return response.choices[0].message.content


def build_recommendation_prompt(personas: list) -> str:
    """
    Construct a prompt that summarizes the user personas and instructs the LLM
    to analyze the sentiment and propose 2-3 event recommendations with a brief itinerary.
    Only descriptive attributes are used (major, year, interests, personality_type).
    """
    lines = ["### User Persona Analysis:"]
    for persona in personas:
        major = persona.get("major", "N/A")
        year = persona.get("year", "N/A")
        interests = ", ".join(persona.get("interests", [])) or "N/A"
        personality = persona.get("personality_type", "N/A")
        lines.append(
            f"- Major: {major}, Year: {year}, Interests: {interests}, Personality: {personality}")

    lines.append("\n### Instructions:")
    lines.append(
        "Based on the above user persona data, please provide a concise analysis of the overall sentiment and trends. "
        "Then, propose 2–3 event recommendations tailored to these personas. For each recommendation, provide a brief itinerary "
        "(including duration, key sessions, and objectives) that would foster better connectivity and engagement among these diverse groups."
    )
    return "\n".join(lines)


async def generate_recommendation(event_id: str) -> Dict[str, Any]:
    """
    Fetches user persona data for an event, builds a prompt, calls the LLM,
    and saves the prompt and response to the database.
    """
    personas = await get_event_personas(event_id)
    if not personas:
        raise Exception("No persona data found for this event.")

    prompt = build_recommendation_prompt(personas)
    recommendation = call_azure_llm(prompt)

    # Build the AI summary record (note: event_id needs to be converted to PyObjectId)
    ai_summary_data = {
        "event_id": PyObjectId(event_id),
        "request": prompt,
        "response": recommendation,
        "created_at": datetime.utcnow()
    }
    saved_summary = await create_ai_summary(ai_summary_data)
    return {"prompt": prompt, "recommendation": recommendation, "saved_record": saved_summary.dict(by_alias=True)}


# For local testing without API routing


async def test_generate_recommendation():
    # Replace with a valid event ID from your test DB
    sample_event_id = "67e75f35a810c5bf42c49cdb"
    result = await generate_recommendation(sample_event_id)
    print("Constructed Prompt:")
    print(result["prompt"])
    print("\nLLM Recommendation Output:")
    print(result["recommendation"])
    print("\nSaved Record:")
    print(result["saved_record"])

if __name__ == "__main__":
    asyncio.run(test_generate_recommendation())
