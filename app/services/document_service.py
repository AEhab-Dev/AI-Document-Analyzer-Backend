import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlmodel import Session, select
from app.core.config import settings
from app.models.document import Document
from app.models.message import Message
from app.services.pdf_service import extract_text_from_pdf
from app.services.ai_service import generate_summary


MAX_FILE_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


async def save_upload_file(file: UploadFile) -> tuple[str, str]:
    """
    Validates and saves uploaded PDF.
    Returns: (stored_filename, full_file_path)
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the {settings.MAX_FILE_SIZE_MB}MB limit.",
        )

    stored_filename = f"{uuid.uuid4()}.pdf"
    file_path = Path(settings.UPLOAD_DIR) / stored_filename

    async with aiofiles.open(file_path, "wb") as out_file:
        await out_file.write(contents)

    return stored_filename, str(file_path)


async def process_document(
    file: UploadFile,
    user_id: uuid.UUID,
    session: Session,
) -> Document:
    stored_filename, file_path = await save_upload_file(file)

    try:
        text, word_count, was_truncated = extract_text_from_pdf(file_path)
    except ValueError as e:
        Path(file_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    try:
        summary, doc_type = generate_summary(text)
    except Exception as e:
        Path(file_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {str(e)}",
        )

    document = Document(
        user_id=user_id,
        original_filename=file.filename or stored_filename,
        stored_filename=stored_filename,
        document_type=doc_type,
        summary=summary,
        word_count=word_count,
        was_truncated=was_truncated,
    )

    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def get_user_documents(user_id: uuid.UUID, session: Session, limit: int = 10) -> list[Document]:
    statement = (
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .limit(limit)
    )
    return session.exec(statement).all()


def get_document_by_id(
    document_id: uuid.UUID,
    user_id: uuid.UUID,
    session: Session,
) -> Document:
    document = session.get(Document, document_id)

    if not document or document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


def get_document_messages(document_id: uuid.UUID, session: Session) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.document_id == document_id)
        .order_by(Message.created_at.asc())
    )
    return session.exec(statement).all()