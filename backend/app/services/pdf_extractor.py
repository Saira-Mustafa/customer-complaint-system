"""Extract text from uploaded PDF complaint documents using pypdf."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


class PdfExtractionError(ValueError):
    """Raised when a PDF cannot be read or contains no usable text."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Read all pages from a PDF and return the combined plain text.

    Production OCR is not used — only text embedded in the PDF is extracted.
    """
    if not file_bytes:
        raise PdfExtractionError("The uploaded PDF file is empty.")

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except Exception as exc:
        raise PdfExtractionError(f"Could not read PDF: {exc}") from exc

    if getattr(reader, "is_encrypted", False):
        raise PdfExtractionError("Encrypted PDFs are not supported.")

    pages: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        cleaned = page_text.strip()
        if cleaned:
            pages.append(cleaned)

    combined = "\n\n".join(pages).strip()
    if not combined:
        raise PdfExtractionError(
            "No readable text was found in the PDF. "
            "Scanned image-only PDFs are not supported without OCR."
        )

    return combined
