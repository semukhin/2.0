# src/api/router.py

import asyncio
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.graph.graph import graph_app
from src.auth.security import decode_token # Предполагается наличие

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str
    thread_id: str | None = None

async def event_stream(thread_id: str, user_id: int, query: str):
    """Генератор для потоковой передачи событий SSE."""
    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [("human", query)], "user_id": user_id}
    
    async for event in graph_app.astream_events(inputs, config, version="v1"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield f"data: {json.dumps({'type': 'llm_chunk', 'content': content})}\n\n"
        elif kind == "on_tool_start":
            yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name'], 'input': event['data'].get('input')})}\n\n"
        elif kind == "on_tool_end":
            yield f"data: {json.dumps({'type': 'tool_end', 'tool': event['name'], 'output': event['data'].get('output')})}\n\n"
    
    # Сигнал о завершении потока
    yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"


@router.post("/stream")
async def stream_chat(
    chat_request: ChatRequest,
    token: dict = Depends(decode_token) # Защищенный эндпоинт
):
    user_id = token.get("user_id")
    thread_id = chat_request.thread_id or f"user_{user_id}_{chat_request.query[:20]}"
    
    return StreamingResponse(
        event_stream(thread_id, user_id, chat_request.query),
        media_type="text/event-stream"
    )