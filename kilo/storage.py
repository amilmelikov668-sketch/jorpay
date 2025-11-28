import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class User:
    username: str
    display_name: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Chat:
    id: str
    title: str
    participants: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Message:
    id: str
    chat_id: str
    sender: str
    text: str
    sent_at: datetime = field(default_factory=datetime.utcnow)


class InMemoryStore:
    """Thread-safe in-memory storage for Kilo."""

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}
        self._chats: Dict[str, Chat] = {}
        self._messages: Dict[str, List[Message]] = {}
        self._lock = threading.Lock()

    def create_user(self, username: str, display_name: str) -> User:
        with self._lock:
            if username in self._users:
                raise ValueError("User already exists")
            user = User(username=username, display_name=display_name)
            self._users[username] = user
            return user

    def create_chat(self, title: str, participants: List[str]) -> Chat:
        with self._lock:
            missing = [p for p in participants if p not in self._users]
            if missing:
                raise ValueError(f"Unknown users: {', '.join(missing)}")
            chat_id = str(uuid.uuid4())
            chat = Chat(id=chat_id, title=title, participants=participants)
            self._chats[chat_id] = chat
            self._messages[chat_id] = []
            return chat

    def add_message(self, chat_id: str, sender: str, text: str) -> Message:
        with self._lock:
            if chat_id not in self._chats:
                raise ValueError("Chat not found")
            if sender not in self._users:
                raise ValueError("Sender not found")
            if sender not in self._chats[chat_id].participants:
                raise ValueError("Sender is not part of this chat")
            message = Message(
                id=str(uuid.uuid4()), chat_id=chat_id, sender=sender, text=text
            )
            self._messages[chat_id].append(message)
            return message

    def get_chat(self, chat_id: str) -> Chat:
        with self._lock:
            if chat_id not in self._chats:
                raise ValueError("Chat not found")
            return self._chats[chat_id]

    def list_messages(self, chat_id: str) -> List[Message]:
        with self._lock:
            if chat_id not in self._messages:
                raise ValueError("Chat not found")
            return list(self._messages[chat_id])
