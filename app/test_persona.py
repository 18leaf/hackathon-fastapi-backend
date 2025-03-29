import asyncio
from all_crud import get_event_personas


# Example test function (to be run via asyncio.run() for local testing)
async def test_get_event_personas():
    # Replace with a valid event ID in your test DB
    sample_event_id = "67e75f35a810c5bf42c49cdb"
    personas = await get_event_personas(sample_event_id)
    for p in personas:
        print(p)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_get_event_personas())
