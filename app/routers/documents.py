from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentListItem,
    DocumentDetailResponse,
    MessagePublic,
)
from app.services.document_service import (
    process_document,
    get_user_documents,
    get_document_by_id,
    get_document_messages,
)
import uuid

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    document = await process_document(file, current_user.id, session)
    return DocumentUploadResponse(
        document_id=document.id,
        original_filename=document.original_filename,
        document_type=document.document_type or "general",
        summary=document.summary or "",
        was_truncated=document.was_truncated,
        word_count=document.word_count or 0,
    )


@router.get("", response_model=list[DocumentListItem])
def list_documents(
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    documents = get_user_documents(current_user.id, session, limit)
    return [DocumentListItem.model_validate(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    document = get_document_by_id(document_id, current_user.id, session)
    messages = get_document_messages(document_id, session)
    return DocumentDetailResponse(
        id=document.id,
        original_filename=document.original_filename,
        document_type=document.document_type,
        summary=document.summary,
        was_truncated=document.was_truncated,
        word_count=document.word_count,
        created_at=document.created_at,
        messages=[MessagePublic.model_validate(m) for m in messages],
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    document = get_document_by_id(document_id, current_user.id, session)
    session.delete(document)
    session.commit()
    return {"message": "Document deleted successfully"}