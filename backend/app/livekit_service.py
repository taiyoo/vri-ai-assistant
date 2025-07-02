import os
from datetime import datetime, timedelta
# Updated imports for LiveKit 1.0.11
from livekit import api
from typing import Optional
import logging
import subprocess
import threading
import sys
import signal

logger = logging.getLogger(__name__)

class LiveKitService:
    def __init__(self):
        # Get secrets from environment variables
        self.api_key = os.environ.get("LIVEKIT_API_KEY", "LIVEKIT_API_KEY")
        self.api_secret = os.environ.get("LIVEKIT_API_SECRET", "LIVEKIT_API_SECRET")
        self.livekit_url = os.environ.get("LIVEKIT_URL", "LIVEKIT_URL")
        self.worker_process = None

        # print(f"LiveKit API Key: {self.api_key}")  # Debugging line to check API key
        # print(f"LiveKit API Secret: {self.api_secret}")  # Debugging line to check API secret
        # print(f"LiveKit URL: {self.livekit_url}")  # Debugging line to check URL
        
        if not all([self.api_key, self.api_secret, self.livekit_url]):
            logger.error("LiveKit credentials not properly configured")
            raise ValueError("LiveKit credentials not properly configured. Check environment variables.")
    
    def create_token(self, user_id: str, room_name: Optional[str] = None) -> dict:
        """Create a LiveKit access token for the user (audio-only)"""
        try:
            # Generate room name if not provided
            if not room_name:
                room_name = f"voice-chat-{user_id}"
            
            # Create token
            token = (
                api.AccessToken(api_key=self.api_key, api_secret=self.api_secret)
                .with_identity(user_id) 
                .with_name(f"User-{user_id}")         
                .with_grants(api.VideoGrants(
                    room=room_name,      
                    room_join=True,
                    room_create=True,         # Allow creating the room if it doesn't exist
                    can_publish=True,         # Allow publishing audio
                    can_subscribe=True,       # Allow receiving audio
                    can_publish_data=True     # Needed for transcription data
                ))
            )
             
            logger.info(f"Created LiveKit audio token for user {user_id} in room {room_name}")
            logger.info(f"Token: {token.to_jwt()}")  # This method name remains the same

            return {
                "token": token.to_jwt(),  # This method name remains the same
                "url": self.livekit_url,
                "room": room_name
            }
            
        except Exception as e:
            logger.error(f"Failed to create LiveKit token: {str(e)}")
            raise ValueError(f"Failed to create LiveKit token: {str(e)}")
        
    def start_agent_worker(self, agent_script_path):
        """
        Start the LiveKit agent worker process that will be automatically
        dispatched to new rooms created in the LiveKit project.
        
        Args:
            agent_script_path: Path to the Python script containing the agent implementation
        """
        try:
            logger.info("Starting LiveKit agent worker process")
            
            # Set environment variables for the worker process
            env = os.environ.copy()
            env["LIVEKIT_API_KEY"] = self.api_key
            env["LIVEKIT_API_SECRET"] = self.api_secret
            env["LIVEKIT_URL"] = self.livekit_url
            
            # Start the worker process
            self.worker_process = subprocess.Popen(
                [sys.executable, agent_script_path, "start"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Start threads to monitor output
            threading.Thread(target=self._log_output, args=(self.worker_process.stdout, "INFO")).start()
            threading.Thread(target=self._log_output, args=(self.worker_process.stderr, "ERROR")).start()
            
            logger.info("LiveKit agent worker started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent worker: {str(e)}")
            return False
    
    def stop_agent_worker(self):
        """Stop the running agent worker process"""
        if self.worker_process:
            logger.info("Stopping LiveKit agent worker")
            self.worker_process.send_signal(signal.SIGTERM)
            self.worker_process = None
    
    def _log_output(self, pipe, default_level):
        """Log the output from the worker process"""
        for line in iter(pipe.readline, b''):
            line_str = line.decode('utf-8').strip()
            
            # Try to parse the log level from the message
            if "DEBUG:" in line_str:
                logger.debug(f"Agent worker: {line_str}")
            elif "INFO:" in line_str:
                logger.info(f"Agent worker: {line_str}")
            elif "WARNING:" in line_str or "WARN:" in line_str:
                logger.warning(f"Agent worker: {line_str}")
            elif "ERROR:" in line_str:
                logger.error(f"Agent worker: {line_str}")
            elif "CRITICAL:" in line_str:
                logger.critical(f"Agent worker: {line_str}")
            else:
                # Use the default level if we can't determine
                if default_level == "INFO":
                    logger.info(f"Agent worker: {line_str}")
                else:
                    logger.error(f"Agent worker: {line_str}")