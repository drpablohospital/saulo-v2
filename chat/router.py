"""Chat endpoints for Saulo v2."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import json
import asyncio

from auth.dependencies import get_current_user_optional
from chat.service import ChatService
from chat.models import MessageCreate, ChatResponse
from ollama.client import OllamaClient

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()
ollama_client = OllamaClient()


@router.get("/models")
async def list_models():
    """List available Ollama models."""
    models = await ollama_client.list_models()
    return {"models": models}


@router.post("/", response_model=ChatResponse)
async def send_message(
    message: MessageCreate,
    user=Depends(get_current_user_optional)
):
    """Send a message and get response (non-streaming)."""
    user_id = user.get("user_id") if user else "anonymous"
    
    response = await chat_service.process_message(
        user_id=user_id,
        content=message.content,
        model=message.model,
        conversation_id=message.conversation_id
    )
    
    return response


@router.post("/stream")
async def send_message_stream(
    message: MessageCreate,
    user=Depends(get_current_user_optional)
):
    """Send a message and get streaming response."""
    user_id = user.get("user_id") if user else "anonymous"
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        queue = asyncio.Queue()
        
        async def progress_callback(msg: str):
            await queue.put(f"event: status\ndata: {json.dumps({'message': msg})}\n\n")
        
        # Start processing in background
        task = asyncio.create_task(
            chat_service.process_message_stream(
                user_id=user_id,
                content=message.content,
                model=message.model,
                conversation_id=message.conversation_id,
                progress_callback=progress_callback
            )
        )
        
        # Stream events while processing
        while not task.done():
            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield event
            except asyncio.TimeoutError:
                continue
        
        # Get final result
        result = await task
        yield f"event: response\ndata: {json.dumps(result)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    user=Depends(get_current_user_optional)
):
    """Get chat history for a conversation."""
    user_id = user.get("user_id") if user else "anonymous"
    
    messages = await chat_service.get_conversation_history(
        user_id=user_id,
        conversation_id=conversation_id
    )
    
    return {"conversation_id": conversation_id, "messages": messages}


@router.post("/new")
async def create_conversation(
    user=Depends(get_current_user_optional)
):
    """Create a new conversation."""
    user_id = user.get("user_id") if user else "anonymous"
    
    conversation_id = await chat_service.create_conversation(user_id)
    
    return {"conversation_id": conversation_id}


@router.get("/conversations")
async def list_conversations(
    user=Depends(get_current_user_optional)
):
    """List user's conversations."""
    user_id = user.get("user_id") if user else "anonymous"
    
    conversations = await chat_service.list_conversations(user_id)
    
    return {"conversations": conversations}