#!/usr/bin/env python
import os
import logging
import traceback
import sys
import asyncio
import json
from datetime import datetime

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
    
    # Import our custom modules
    from src.intent_classifier import IntentClassifier
    from src.router import AgentRouter
    from src.config import settings

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
            
            # Create a custom agent class with intent classification
            class AgedCareAgent(Agent):
                def __init__(self):
                    logger.info("Initializing AgedCareAgent with intent classification")
                    super().__init__(
                        instructions=(
                            "You are an AI Assistant for aged care workers. You help them record "
                            "activities of daily living (ADL), clinical observations, medication "
                            "administration, and answer questions about resident care. "
                            "You listen to their voice inputs and respond appropriately based on "
                            "the context and intent of their requests."
                        ),
                    )
                    
                    # Initialize intent classifier and router
                    self.intent_classifier = IntentClassifier()
                    self.agent_router = AgentRouter()
                    logger.info("AgedCareAgent initialized with intent classification and routing")

                async def on_session_start(self):
                    """Called when the session starts"""
                    logger.info("Session started, sending initial message")
                    await self.send_message(
                        "Hello, I'm your aged care assistant. I can help you record daily activities, "
                        "clinical observations, and answer questions about resident care. "
                        "What would you like to record or discuss today?"
                    )

                async def on_user_speech_committed(self, user_msg: str):
                    """Process user speech with intent classification and routing"""
                    try:
                        logger.info(f"Processing user speech: {user_msg[:100]}...")
                        
                        # Classify the intent
                        classification_result = await self.intent_classifier.classify_with_fallback(user_msg)
                        intent = classification_result.get("intent")
                        confidence = classification_result.get("confidence")
                        entities = classification_result.get("entities", {})
                        
                        logger.info(f"Intent classified: {intent} (confidence: {confidence})")
                        
                        # Prepare payload for the router
                        payload = {
                            "utterance": user_msg,
                            "context": f"User speech recorded at {datetime.now().isoformat()}",
                            "task": user_msg,
                            "entities": entities,
                            "timestamp": datetime.now().isoformat(),
                            "classification": classification_result
                        }
                        
                        # Route to appropriate agent
                        if intent in ["record_adl", "clinical", "medication", "behavior", "governance_check"]:
                            logger.info(f"Routing to domain-specific agent for intent: {intent}")
                            response = await self.agent_router.route(intent, payload)
                            
                            # Format response for TTS
                            if "result" in response:
                                if confidence > 0.8:
                                    response_msg = f"I've processed your {intent.replace('_', ' ')} request. {response['result']}"
                                else:
                                    response_msg = f"I think you're asking about {intent.replace('_', ' ')}. {response['result']}"
                                await self.send_message(response_msg)
                            else:
                                await self.send_message("I've recorded your information. Is there anything else you'd like to add?")
                                
                        elif intent == "general":
                            logger.info("Handling general conversation")
                            response = await self.agent_router.route(intent, payload)
                            await self.send_message(response.get("result", "How can I help you with aged care today?"))
                            
                        else:
                            logger.warning(f"Unknown intent: {intent}")
                            await self.send_message("I'm not sure how to help with that. Can you tell me about a resident's activities, medication, or ask a care-related question?")
                            
                    except Exception as e:
                        logger.error(f"Error processing user speech: {e}")
                        logger.error(traceback.format_exc())
                        await self.send_message("I'm sorry, I had trouble processing that. Could you please repeat your request?")

                async def handle_user_message(self, message: str):
                    """Alternative method name for handling user messages"""
                    await self.on_user_speech_committed(message)

                async def send_message(self, message: str):
                    """Send a message back to the user"""
                    try:
                        logger.info(f"Sending message: {message[:100]}...")
                        # Use the session's say method to convert text to speech
                        await self._session.say(message)
                    except Exception as e:
                        logger.error(f"Error sending message: {e}")            
 
            logger.info("Starting session with explicit transcription")
            
            # Create the agent instance
            agent = AgedCareAgent()
            
            # Start the session with explicit transcription
            await session.start(
                agent=agent,
                room=ctx.room,
                room_output_options=RoomOutputOptions(
                    transcription_enabled=True,
                ),
                room_input_options=RoomInputOptions(),
            )
            
            # Store session reference in agent for message sending
            agent._session = session
            
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