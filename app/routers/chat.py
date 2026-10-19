from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.document_service import (
    get_document_by_id,
    get_document_messages,
)
from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import answer_question
from app.core.config import settings
from pathlib import Path
import uuid

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/{document_id}", response_model=ChatResponse)
def ask_question(
    document_id: uuid.UUID,
    payload: ChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    document = get_document_by_id(document_id, current_user.id, session)

    file_path = Path(settings.UPLOAD_DIR) / document.stored_filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found on server.",
        )

    try:
        document_text, _, _ = extract_text_from_pdf(str(file_path))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    existing_messages = get_document_messages(document_id, session)
    chat_history = [
        {"role": m.role, "content": m.content} for m in existing_messages
    ]

    try:
        answer = answer_question(document_text, payload.question, chat_history)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )

    user_message = Message(
        document_id=document_id,
        user_id=current_user.id,
        role="user",
        content=payload.question,
    )
    session.add(user_message)

    assistant_message = Message(
        document_id=document_id,
        user_id=current_user.id,
        role="assistant",
        content=answer,
    )
    session.add(assistant_message)
    session.commit()
    session.refresh(assistant_message)

    return ChatResponse(answer=answer, message_id=assistant_message.id)