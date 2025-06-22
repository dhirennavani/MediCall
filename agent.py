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

# Load environment variables from .env file
load_dotenv()

print("Agent script starting...")


# Define your agent's core behavior
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")
        print("Assistant agent initialized.")


# Function to create an outbound call (dispatches an agent)
# This function is not directly used when the agent is run for playground testing,
# but remains here for completeness if you intend to use it for outbound calls later.

# The entrypoint function is called when a job is assigned to this worker
async def entrypoint(ctx: agents.JobContext):
    print(f"Entrypoint called for job {ctx.job.id} in room {ctx.room.name}")
    
    llama_model = os.getenv("LLAMA_MODEL")
    llama_base_url = os.getenv("LLAMA_OPENAI_BASE_URL")
    llama_api_key = os.getenv("LLAMA_OPENAI_API_KEY")

    if not all([llama_model, llama_base_url, llama_api_key]):
        print("CRITICAL ERROR: LLAMA_MODEL, LLAMA_OPENAI_BASE_URL, or LLAMA_OPENAI_API_KEY environment variables are not set.")
        print("Please ensure your .env file is correctly configured for the LLM. Shutting down agent.")
        ctx.shutdown() # Shutdown if LLM config is missing, as the agent won't function
        return

    try:
        print("Initializing AgentSession components...")
        session = AgentSession(
            stt=openai.STT(model="gpt-4o-transcribe", language="en"),
            llm=openai.LLM(model=llama_model, base_url=llama_base_url, api_key=llama_api_key),
            tts=openai.TTS(model="gpt-4o-mini-tts", voice="ash", instructions="Speak in a friendly and conversational tone.",),
            vad=silero.VAD.load(),
            turn_detection=MultilingualModel(),
        )
        print("AgentSession components initialized successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize AgentSession or its plugins: {e}")
        print("Please check your LLM/STT/TTS API keys, models, and network connectivity. Shutting down agent.")
        ctx.shutdown()
        return

    try:
        print("Starting AgentSession and connecting agent to room...")
        await session.start(
            room=ctx.room,
            agent=Assistant(),
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVCTelephony(), 
            ),
        )
        print("AgentSession started.")
        
        await ctx.connect()

    except Exception as e:
        print(f"CRITICAL ERROR: Failed to start AgentSession or connect to room: {e}")
        print("Agent may not appear in the playground. Shutting down agent.")
        ctx.shutdown()
        return

    # this part would cause an error. We will re-enable it once basic
    # agent connection is confirmed.

    print(f"Job Metadata received: {ctx.job.metadata}")
    dial_info = {}
    if ctx.job.metadata:
        try:
            dial_info = json.loads(ctx.job.metadata)
        except json.JSONDecodeError as e:
            print(f"Error decoding job metadata: {e}. Metadata: {ctx.job.metadata}")
            ctx.shutdown()
            return

    phone_number = dial_info.get("phone_number")
    
    if phone_number:
        sip_participant_identity = phone_number 
        print(f"Attempting to create SIP participant for phone number: {phone_number}")

        try:
            sip_trunk_id = os.getenv("LIVEKIT_SIP_TRUNK_ID", 'ST_vpVA4GU38xxW') 
            if sip_trunk_id == 'ST_xxxx_REPLACE_ME':
                print("WARNING: LIVEKIT_SIP_TRUNK_ID is not set in .env or is still a placeholder. SIP call will likely fail.")
                # ctx.shutdown() 
                # return

            print(f"Creating SIP participant with trunk ID: {sip_trunk_id} to dial: {phone_number}")
            await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=sip_trunk_id,
                sip_call_to=phone_number,
                participant_identity=sip_participant_identity,
                wait_until_answered=True, 
            ))
            print(f"SIP call to {phone_number} picked up successfully.")
        except api.TwirpError as e:
            print(f"CRITICAL ERROR: Failed to create SIP participant for {phone_number}: {e.message}")
            print(f"SIP status code: {e.metadata.get('sip_status_code')}, Status: {e.metadata.get('sip_status')}")
            print("Please check your SIP Trunk ID, phone number, and LiveKit SIP configuration. Shutting down agent.")
            ctx.shutdown()
            return 
        except Exception as e:
            print(f"An unexpected error occurred during SIP participant creation: {e}")
            ctx.shutdown()
            return


    print("Generating initial greeting for the user.")
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )
    print("Initial greeting generated.")

    # Keep the agent session alive until the room ends
    await ctx.room.wait_closed()
    print("Agent session closed.")


if __name__ == "__main__":
    worker_options = agents.WorkerOptions(
        entrypoint_fnc=entrypoint, 
        agent_name="Medicall Assistant"
    )
    print(f"Starting LiveKit Agent CLI. Configured agent_name: '{worker_options.agent_name}'") 
    
    agents.cli.run_app(worker_options)
