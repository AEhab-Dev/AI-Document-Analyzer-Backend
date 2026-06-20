import pdfplumber
from pathlib import Path
from app.core.config import settings


def extract_text_from_pdf(file_path: str) -> tuple[str, int, bool]:
    """
    Returns: (extracted_text, word_count, was_truncated)
    """
    full_text_parts: list[str] = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text_parts.append(text.strip())

    full_text = "\n\n".join(full_text_parts).strip()

    if not full_text:
        raise ValueError(
            "No text could be extracted from this PDF. "
            "Scanned or image-based PDFs are not supported."
        )

    words = full_text.split()
    total_word_count = len(words)
    was_truncated = False

    if total_word_count > settings.MAX_WORDS:
        words = words[: settings.MAX_WORDS]
        full_text = " ".join(words)
        was_truncated = True

    return full_text, total_word_count, was_truncated