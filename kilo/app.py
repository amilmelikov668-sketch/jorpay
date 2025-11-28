from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .storage import InMemoryStore

app = FastAPI(title="Kilo", description="Lightweight Telegram-inspired social network")
store = InMemoryStore()


class UserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)


class ChatRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    participants: list[str] = Field(..., min_items=1)


class MessageRequest(BaseModel):
    sender: str
    text: str = Field(..., min_length=1, max_length=2000)


@app.get("/")
def root() -> dict:
    return {"service": "Kilo", "status": "ok"}


@app.post("/users", status_code=201)
def create_user(user: UserRequest) -> dict:
    try:
        created = store.create_user(user.username, user.display_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "username": created.username,
        "display_name": created.display_name,
        "created_at": created.created_at,
    }


@app.post("/chats", status_code=201)
def create_chat(request: ChatRequest) -> dict:
    try:
        chat = store.create_chat(request.title, request.participants)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": chat.id,
        "title": chat.title,
        "participants": chat.participants,
        "created_at": chat.created_at,
    }


@app.get("/chats/{chat_id}")
def get_chat(chat_id: str) -> dict:
    try:
        chat = store.get_chat(chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": chat.id,
        "title": chat.title,
        "participants": chat.participants,
        "created_at": chat.created_at,
    }


@app.post("/chats/{chat_id}/messages", status_code=201)
def send_message(chat_id: str, request: MessageRequest) -> dict:
    try:
        message = store.add_message(chat_id, request.sender, request.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": message.id,
        "chat_id": message.chat_id,
        "sender": message.sender,
        "text": message.text,
        "sent_at": message.sent_at,
    }


@app.get("/chats/{chat_id}/messages")
def list_messages(chat_id: str) -> JSONResponse:
    try:
        messages = store.list_messages(chat_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    payload = [
        {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender": message.sender,
            "text": message.text,
            "sent_at": message.sent_at,
        }
        for message in messages
    ]
    return JSONResponse(payload)
