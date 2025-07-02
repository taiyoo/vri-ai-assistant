from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from app.livekit_service import LiveKitService
from app.user import User

router = APIRouter(prefix="/livekit", tags=["livekit"])
livekit_service = LiveKitService()

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
        user_id = current_user.id

        return livekit_service.create_token(user_id, token_request.room_name)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))