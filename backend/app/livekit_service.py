import os
from datetime import datetime, timedelta
# Updated imports for LiveKit 1.0.11
from livekit import api
from typing import Optional
import logging
import boto3

logger = logging.getLogger(__name__)
ssm = boto3.client('ssm')

def get_ssm_param(name):
    return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']

class LiveKitService:
    def __init__(self):
        # Get secrets from Amazon SSM Parameter Store
        self.api_key = get_ssm_param('/bedrock-ai-assistant/livekit/api-key')
        self.api_secret = get_ssm_param('/bedrock-ai-assistant/livekit/api-secret')
        self.livekit_url = get_ssm_param('/bedrock-ai-assistant/livekit/url')
        self.worker_process = None

        # print(f"LiveKit API Key: {self.api_key}")  # Debugging line to check API key
        # print(f"LiveKit API Secret: {self.api_secret}")  # Debugging line to check API secret
        print(f"LiveKit URL: {self.livekit_url}")  # Debugging line to check URL
        
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
        
