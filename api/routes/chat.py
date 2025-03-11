from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from ..services.chat_service import ChatService
from ..login import get_current_active_user
from database import User
from config import Config

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize chat service (will be cached)
chat_service = None

def get_chat_service():
    global chat_service
    if chat_service is None:
        chat_service = ChatService()
    return chat_service

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    response: str

# Create two versions of the endpoint with and without auth
if Config.ENABLE_AUTH:
    @router.post("/", response_model=ChatResponse)
    async def chat_endpoint(
        request: ChatRequest, 
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_active_user)
    ):
        """Generate a response to a medical query. Requires user authentication."""
        return await process_chat_request(request, current_user.username)
else:
    @router.post("/", response_model=ChatResponse)
    async def chat_endpoint(
        request: ChatRequest, 
        background_tasks: BackgroundTasks
    ):
        """Generate a response to a medical query. No authentication required."""
        return await process_chat_request(request, "anonymous")

async def process_chat_request(request: ChatRequest, username: str):
    """Process chat requests - common function for both auth and non-auth endpoints"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="No message provided.")
        
        # Get or initialize chat service
        service = get_chat_service()
        
        # Log the user's request
        logger.info(f"User {username} sent message: {request.message[:50]}...")
        
        # Generate response with history if provided
        response = service.generate_response(request.message, request.history)
        
        # Log the successful response generation
        logger.info(f"Generated response for user {username}, query length: {len(request.message)}")
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="I encountered a problem processing your medical question. Please try a different question or try again later."
        ) 