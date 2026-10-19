import uuid
from io import BytesIO
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from app.models.document import Document
from app.models.message import Message


def build_export_pdf(document: Document, messages: list[Message]) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
        alignment=TA_LEFT,
    )

    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#6B7280"),
        spaceAfter=2,
    )

    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#111827"),
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        leading=16,
        spaceAfter=4,
    )

    question_style = ParagraphStyle(
        "Question",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1D4ED8"),
        spaceBefore=10,
        spaceAfter=4,
    )

    answer_style = ParagraphStyle(
        "Answer",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        leading=16,
        spaceAfter=4,
        leftIndent=12,
    )

    story = []

    story.append(Paragraph("Document Analysis Report", title_style))
    story.append(Paragraph(f"File: {document.original_filename}", meta_style))
    story.append(
        Paragraph(
            f"Date: {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')}",
            meta_style,
        )
    )
    story.append(
        Paragraph(
            f"Document Type: {(document.document_type or 'Unknown').upper()}",
            meta_style,
        )
    )

    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB")))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("Summary", section_header_style))

    summary_text = (document.summary or "No summary available.").replace("\n", "<br/>")
    story.append(Paragraph(summary_text, body_style))

    user_messages = [m for m in messages if m.role == "user"]
    if user_messages:
        story.append(Spacer(1, 4 * mm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB")))
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("Questions & Answers", section_header_style))

        i = 0
        while i < len(messages):
            msg = messages[i]
            if msg.role == "user":
                story.append(Paragraph(f"Q: {msg.content}", question_style))
                if i + 1 < len(messages) and messages[i + 1].role == "assistant":
                    answer = messages[i + 1].content.replace("\n", "<br/>")
                    story.append(Paragraph(f"A: {answer}", answer_style))
                    i += 2
                else:
                    i += 1
            else:
                i += 1

    doc.build(story)
    buffer.seek(0)
    return buffer.read()