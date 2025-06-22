import asyncio
import json
import os
import random
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit import api
import json

load_dotenv()




async def create_outbound_call(phone_number: str, script: str):
    """
    Create an outbound call using agent dispatch.
    
    Args:
        phone_number (str): The phone number to call
    """
    print(f"Creating outbound call for phone number: {phone_number} with script: {script}")
    lkapi = api.LiveKitAPI()
    
    try:
        room_name = f"outbound-{''.join(str(random.randint(0, 9)) for _ in range(10))}"
        metadata_json = json.dumps({"phone_number": phone_number, "script": script})

        print(f"Attempting to dispatch agent for phone number: {phone_number} in room: {room_name}")
        print(f"Dispatch metadata: {metadata_json}")

        await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                # IMPORTANT: This `agent_name` here MUST match what you expect for outbound calls.
                # If your worker is unnamed, this dispatch won't be picked up by it.
                # For this specific `create_outbound_call`, if you expect it to be picked
                # by the current unnamed worker, you'd need to remove 'agent_name' here too,
                # or ensure the worker options *do* specify this name.
                agent_name="Medicall Assistant", 
                room=room_name,
                metadata=metadata_json
            )
        )
        print(f"Agent dispatch successful for room: {room_name}")
    except api.TwirpError as e:
        print(f"Error dispatching agent: {e.message}")
        print(f"Code: {e.code}, Metadata: {e.metadata}")
    finally:
        # Properly close the client session to avoid unclosed session warnings
        await lkapi.aclose()


if __name__ == "__main__":
    asyncio.run(create_outbound_call(""))
