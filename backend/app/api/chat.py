from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from app.agents.orchestrator import orchestrator
from app.api.deps import get_current_user
from app.models.user import User
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    lat: Optional[float] = 6.5244  # Default to Lagos
    lng: Optional[float] = 3.3792
    api_key: Optional[str] = None

@router.post("/chat")
def chat_with_daaba(request: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        response = orchestrator.process_message(
            patient_id=current_user.id,
            message=request.message,
            lat=request.lat,
            lng=request.lng,
            api_key=request.api_key
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_with_daaba_stream(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """SSE endpoint that streams the AI response token-by-token for faster perceived speed."""
    
    def event_stream():
        try:
            # Send initial event
            yield f"data: {json.dumps({'type': 'event', 'data': 'Assessment Agent Analyzing Symptoms...'})}\n\n"
            
            result = orchestrator.process_message_streaming(
                patient_id=current_user.id,
                message=request.message,
                lat=request.lat,
                lng=request.lng,
                api_key=request.api_key
            )

            # If it's an error dict (quota exceeded etc), send it as a complete message
            if isinstance(result, dict):
                yield f"data: {json.dumps({'type': 'events', 'data': result.get('events', [])})}\n\n"
                yield f"data: {json.dumps({'type': 'text', 'data': result.get('text', '')})}\n\n"
                yield f"data: {json.dumps({'type': 'doctors', 'data': result.get('doctors', [])})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

            # Stream tokens from the generator
            for chunk in result:
                if chunk['type'] == 'token':
                    yield f"data: {json.dumps({'type': 'token', 'data': chunk['data']})}\n\n"
                elif chunk['type'] == 'events':
                    yield f"data: {json.dumps({'type': 'events', 'data': chunk['data']})}\n\n"
                elif chunk['type'] == 'doctors':
                    yield f"data: {json.dumps({'type': 'doctors', 'data': chunk['data']})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            error_msg = str(e)
            yield f"data: {json.dumps({'type': 'text', 'data': f'Error: {error_msg}'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
