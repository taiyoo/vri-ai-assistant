#!/usr/bin/env python
import os
import logging
import traceback
import sys
import asyncio

# MCP tool registration for LLM to access DynamoDB
# from app.tools.dynamodb_tool import search_name_in_dynamodb

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("livekit-agent")

try:
    from livekit import rtc
    from livekit.agents import (
        Agent,
        AgentSession,
        AutoSubscribe,
        ChatContext,
        JobContext,
        JobProcess,
        RoomInputOptions,
        RoomOutputOptions,
        RunContext,
        WorkerOptions,
        cli,
        metrics,
        mcp,
        function_tool,
    )
    from livekit.plugins import deepgram, openai, silero

    logger.info("Successfully imported all required modules")

    async def entrypoint(ctx: JobContext):
        """Entrypoint function for the agent job."""
        try:
            logger.info(f"Agent connecting to room {ctx.room.name}")
            
            # Connect to the room and subscribe to audio
            await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
            logger.info("Connected to room successfully")
            
            # Wait for a participant to join
            logger.info("Waiting for participant to join...")
            participant = await ctx.wait_for_participant()
            logger.info(f"Participant joined: {participant.identity}")
            
            # Start the agent
            logger.info("Starting agent...")
            await run_multimodal_agent(ctx, participant)
            
            logger.info("Agent started successfully")
        except Exception as e:
            logger.error(f"Error in entrypoint: {str(e)}")
            logger.error(traceback.format_exc())

    async def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
        """Set up and run the multimodal agent"""
        try:
            logger.info("Creating agent session with transcription")
            
            # Create session with configured services
            session = AgentSession(
                vad=silero.VAD.load(),
                llm=openai.LLM(
                    model="gpt-4o",
                    api_key=os.environ.get("OPENAI_API_KEY")
                ),
                stt=deepgram.STT(
                    model="nova-3",
                    api_key=os.environ.get("DEEPGRAM_API_KEY")
                ),
                tts=deepgram.TTS(
                    # model="aura-asteria-en",
                    model="aura-2-thalia-en",
                    api_key=os.environ.get("DEEPGRAM_API_KEY")
                ),
                # tts=openai.TTS(
                #     voice="echo",
                #     api_key=os.environ.get("OPENAI_API_KEY")
                # ),
            )
            
            logger.info("Created agent session")
            
            # Create a custom agent class
            class AgedCareAgent(Agent):
                def __init__(self):
                    logger.info("Initializing AgedCareAgent")
                    super().__init__(
                        instructions=(
                            "You are an AI Assistant that allows aged care workers to talk as they are working "
                            "with residents, describing ordinary events such as eating food, drinking water "
                            "and using the toilet. With multiple staff using the app, a profile will be built "
                            "of each resident and their current status, and the app will be able to answer "
                            "questions from care workers (e.g.,'How much water has Mrs X had today or in the "
                            "past 3 hours?' or at dinner 'How much did Mr Y eat for lunch?')"
                        ),
                    )
                    logger.info("AgedCareAgent initialized")

                async def on_session_start(self):
                    """Called when the session starts"""
                    logger.info("Session started, sending initial message")
                    await self.send_message("Hello, I'm your aged care assistant. How can I help you today?")            

                # async def on_message(self, message: str):
                #     logger.info(f"Received message: {message}")
                #
                #     # Use the LLM to detect intent and extract name if present
                #     prompt = (
                #         "Classify the user's intent from the following message. "
                #         "If the user is asking to search for a resident's name, "
                #         "respond with 'search_name:<name>'. Otherwise, respond with 'other'.\n\n"
                #         f"Message: {message}"
                #     )
                #     llm_response = await self.llm.complete(prompt)
                #     response_text = llm_response.text.strip().lower()

                #     if response_text.startswith("search_name:"):
                #         name = response_text.split("search_name:")[1].strip()
                #         logger.info(f"Detected search_name intent for: {name}")
                        
                #         # Call the DynamoDB tool in a thread pool
                #         loop = asyncio.get_event_loop()
                #         results = await loop.run_in_executor(
                #             None, lambda: search_name_in_dynamodb(None, name)
                #         )
                        
                #         if results:
                #             if len(results) == 1:
                #                 patient = results[0]
                #                 # Build a summary from the patient record (customize as needed)
                #                 summary = (
                #                     f"Patient: {patient.get('PatientName', 'Unknown')}\n"
                #                     f"Age: {patient.get('Age', 'N/A')}\n"
                #                     f"Status: {patient.get('Status', 'N/A')}\n"
                #                     # Add more fields as needed
                #                 )
                #                 await self.send_message(f"Found one match:\n{summary}")
                #                 self.last_search_results = None
                #             else:
                #                 # Multiple matches: ask user to clarify
                #                 names = [item.get("PatientName", "Unknown") for item in results]
                #                 await self.send_message(
                #                     f"Found multiple matches: {', '.join(names)}. "
                #                     "Please specify which patient you want a summary for."
                #                 )
                #                 self.last_search_results = results
                #         else:
                #             await self.send_message("No matching names found.")
                #             self.last_search_results = None
                #     else:
                #         # Default LLM response
                #         logger.info("No search intent detected, responding normally.")
                #         reply = await self.llm.complete(message)
                #         await self.send_message(reply.text.strip())                    
                        
            logger.info("Starting session with explicit transcription")
            
            # Start the session with explicit transcription
            await session.start(
                agent=AgedCareAgent(),
                room=ctx.room,
                room_output_options=RoomOutputOptions(
                    transcription_enabled=True,
                ),
                room_input_options=RoomInputOptions(),
            )
            
            logger.info("Session started successfully")
            
        except Exception as e:
            logger.error(f"Error in run_multimodal_agent: {str(e)}")
            logger.error(traceback.format_exc())

    if __name__ == "__main__":
        try:
            # Run the worker application
            logger.info("Agent script started, registering worker...")
            cli.run_app(
                WorkerOptions(
                    entrypoint_fnc=entrypoint,
                )
            )
        except Exception as e:
            logger.error(f"Error running worker app: {str(e)}")
            logger.error(traceback.format_exc())
except Exception as e:
    logger.error(f"Error during module import: {str(e)}")
    logger.error(traceback.format_exc())