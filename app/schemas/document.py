from pydantic import BaseModel
import uuid
from datetime import datetime
from typing import Optional


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    original_filename: str
    document_type: str
    summary: str
    was_truncated: bool
    word_count: int

    model_config = {"from_attributes": True}


class DocumentListItem(BaseModel):
    id: uuid.UUID
    original_filename: str
    document_type: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MessagePublic(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetailResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    document_type: Optional[str]
    summary: Optional[str]
    was_truncated: bool
    word_count: Optional[int]
    created_at: datetime
    messages: list[MessagePublic]

    model_config = {"from_attributes": True}