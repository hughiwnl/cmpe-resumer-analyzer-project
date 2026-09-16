"""Resume text extraction for PDF and DOCX files.

All extraction happens in memory from the uploaded file's bytes. Nothing
is written to disk, and nothing is logged, to respect resume privacy.
"""

import io

import fitz  # PyMuPDF
from docx import Document


def extract_text(uploaded_file) -> tuple[str, str | None]:
    """Extract text from an uploaded PDF or DOCX file.

    Args:
        uploaded_file: A Streamlit UploadedFile object.

    Returns:
        A (text, error) tuple. On success, error is None. On failure,
        text is an empty string and error contains a user-facing message.
    """
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if filename.endswith(".pdf"):
        return _extract_pdf_text(file_bytes)
    elif filename.endswith(".docx"):
        return _extract_docx_text(file_bytes)
    else:
        return "", "Unsupported file type. Please upload a PDF or DOCX file."


def _extract_pdf_text(file_bytes: bytes) -> tuple[str, str | None]:
    """Extract text from PDF bytes using PyMuPDF."""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            pages_text = [page.get_text() for page in doc]
        text = "\n".join(pages_text).strip()
    except Exception:
        return "", "Could not read this PDF. It may be corrupted, password-protected, or image-only (scanned)."

    if not text:
        return "", "No readable text found in this PDF. It may be a scanned image without a text layer."

    return text, None


def _extract_docx_text(file_bytes: bytes) -> tuple[str, str | None]:
    """Extract text from DOCX bytes using python-docx."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs]

        # Also pull text out of any tables, since resumes sometimes use them
        # for layout (e.g. skills lists or contact info).
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)

        text = "\n".join(p for p in paragraphs if p.strip()).strip()
    except Exception:
        return "", "Could not read this DOCX file. It may be corrupted or in an unsupported format."

    if not text:
        return "", "No readable text found in this DOCX file."

    return text, None
