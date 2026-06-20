from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.document_service import get_document_by_id, get_document_messages
from app.services.export_service import build_export_pdf
import uuid

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{document_id}")
def export_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    document = get_document_by_id(document_id, current_user.id, session)
    messages = get_document_messages(document_id, session)
    pdf_bytes = build_export_pdf(document, list(messages))

    filename = document.original_filename.replace(".pdf", "_report.pdf")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )