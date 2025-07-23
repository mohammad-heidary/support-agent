### app/models.py
from pydantic import BaseModel
from typing import List, Optional, TypedDict

class Message(BaseModel):
    role: str  # 'user' or 'bot'
    content: str

class ChatSession(BaseModel):
    session_id: str
    model_name: Optional[str]
    history: List[Message] = []

class UserMessage(BaseModel):
    session_id: str
    content: str

class ModelAction(BaseModel):
    action: str 
    model_name: str | None = None

class DidarInput(TypedDict):
    query: str
