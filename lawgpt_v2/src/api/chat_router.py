# src/api/chat_router.py

import json
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from src.graph.graph import graph_app
from src.auth.security import get_current_user
from src.auth.models import User

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str
    thread_id: str | None = None

async def event_stream_generator(thread_id: str, user_id: int, query: str):
    """Генератор для потоковой передачи событий SSE на фронтенд."""
    config = {"configurable": {"thread_id": thread_id}}
    
    # Начальное состояние для графа
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "user_id": user_id,
        "original_query": query
    }
    
    # Используем astream_events для получения событий о выполнении графа
    async for event in graph_app.astream_events(initial_state, config, version="v2"):
        kind = event["event"]
        
        # Отправляем события о вызове инструментов
        if kind == "on_tool_start":
            data = {
                "type": "tool_start", 
                "tool": event['name'], 
                "input": event['data'].get('input')
            }
            yield f"data: {json.dumps(data)}\n\n"
        
        # Отправляем события о завершении инструментов
        elif kind == "on_tool_end":
            data = {
                "type": "tool_end", 
                "tool": event['name'], 
            }
            yield f"data: {json.dumps(data)}\n\n"
            
        # Отправляем финальный ответ, когда он появляется в состоянии
        elif kind == "on_chain_end" and event["name"] == "ResponseFinalizerAgent":
            final_response = event["data"].get("output", {}).get("final_response")
            if final_response:
                data = {"type": "final_response", "content": final_response}
                yield f"data: {json.dumps(data)}\n\n"

    # Сигнал о завершении потока
    yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"

@router.post("/stream")
async def stream_chat(
    chat_request: ChatRequest,
    current_user: Annotated
):
    """
    Основной эндпоинт для взаимодействия с агентом.
    Принимает запрос и возвращает потоковый ответ с обновлениями статуса.
    """
    user_id = current_user.id
    thread_id = chat_request.thread_id or f"thread_{user_id}_{uuid.uuid4()}"
    
    return StreamingResponse(
        event_stream_generator(thread_id, user_id, chat_request.query),
        media_type="text/event-stream"
    )