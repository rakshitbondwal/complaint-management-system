from io import BytesIO
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text_chunks = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        text_chunks.append(extracted)
    return "\n".join(text_chunks).strip()


def extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    """
    Lightweight, assignment-scope document handling.
    - .pdf   -> pypdf text extraction
    - .eml/.txt/.msg -> decode as plain text (email body simulation)
    Production-grade OCR/parsing intentionally out of scope per assignment brief.
    """
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    # treat everything else (email exports, .txt) as plain text
    return file_bytes.decode("utf-8", errors="ignore").strip()
