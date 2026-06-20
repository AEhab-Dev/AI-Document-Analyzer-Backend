import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    original_filename: str = Field(max_length=255)
    stored_filename: str = Field(max_length=255)
    document_type: Optional[str] = Field(default=None, max_length=50)
    summary: Optional[str] = Field(default=None)
    word_count: Optional[int] = Field(default=None)
    was_truncated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))