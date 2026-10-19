from pydantic import BaseModel
import uuid


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    message_id: uuid.UUID
    