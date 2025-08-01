from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from app.livekit_service import LiveKitService
from app.user import User

router = APIRouter(prefix="/livekit", tags=["livekit"])
livekit_service = LiveKitService()
# livekit_service.start_agent_worker("app/livekit_agent.py")
class TokenRequest(BaseModel):
    room_name: Optional[str] = None

@router.post("/token")
async def get_token(
    request: Request,           
    token_request: TokenRequest 
):
    """Generate a LiveKit token for the authenticated user"""
    try:
        # Extract user ID from Cognito claims
        current_user: User = request.state.current_user
        user_id = current_user.email if current_user.email else user_id  # Use email if available

        return livekit_service.create_token(user_id, token_request.room_name)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))