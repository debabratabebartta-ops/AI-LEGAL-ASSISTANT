"""Utilities for the PDF Legal Document Assistant."""
from io import BytesIO
from pypdf import PdfReader
import chatbot

MAX_PDF_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 30
MAX_SUMMARY_CHARS = 18000


def extract_pdf_text(pdf_bytes: bytes) -> tuple[str, int]:
    """Extract text from a PDF after applying basic size/page safeguards."""
    if not isinstance(pdf_bytes, (bytes, bytearray)) or not pdf_bytes:
        raise ValueError("The uploaded file is empty or invalid.")
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise ValueError("PDF is too large. The maximum allowed size is 10 MB.")
    if not bytes(pdf_bytes).lstrip().startswith(b"%PDF-"):
        raise ValueError("The uploaded file does not appear to be a valid PDF.")

    reader = PdfReader(BytesIO(bytes(pdf_bytes)))
    if reader.is_encrypted:
        raise ValueError("This PDF is password-protected. Please upload an unlocked PDF.")
    page_count = len(reader.pages)
    if page_count == 0:
        raise ValueError("The PDF does not contain any pages.")
    if page_count > MAX_PDF_PAGES:
        raise ValueError(f"This PDF has {page_count} pages. The maximum allowed is {MAX_PDF_PAGES} pages.")

    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    text = "\n\n".join(parts).strip()
    if not text:
        raise ValueError("No selectable text was found. This may be a scanned PDF; OCR is not supported yet.")
    return text, page_count


def summarize_legal_document(document_text: str) -> tuple[str, bool]:
    """Create an AI summary using the already-configured chatbot/Gemini pipeline."""
    cleaned = (document_text or "").strip()
    if not cleaned:
        raise ValueError("There is no document text to summarize.")
    was_truncated = len(cleaned) > MAX_SUMMARY_CHARS
    selected_text = cleaned[:MAX_SUMMARY_CHARS]
    prompt = (
        "Summarize the following uploaded legal document in simple English. "
        "Use these headings: 1) Document overview, 2) Main points, "
        "3) Important dates/names/amounts mentioned, 4) Duties or actions stated, "
        "5) Questions the reader may want to ask a qualified advocate. "
        "Do not invent facts, legal sections, deadlines, or outcomes. "
        "If something is unclear or absent, say so. Explain that this is an "
        "informational summary, not legal advice.\n\nDOCUMENT TEXT:\n"
        + selected_text
    )
    return chatbot.generate_legal_response(prompt), was_truncated
