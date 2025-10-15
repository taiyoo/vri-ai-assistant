from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LiveKit
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str


    # Voice providers (below is for deepgram)
    tts_provider: str = "aura-2-thalia-en"
    asr_provider: str = "nova-3"


    # AWS
    aws_region: str = "ap-southeast-2"
    bedrock_adl_model_id: str
    bedrock_med_model_id: str
    bedrock_beh_model_id: str
    bedrock_gov_model_id: str


    class Config:
        env_file = ".env"

settings = Settings() # type: ignore