from io import BytesIO
from typing import Iterable

from pypdf import PdfReader


class PDFExtractionError(Exception):
    pass


def extract_text_from_uploaded_pdfs(uploaded_files: Iterable) -> str:
    """Extracts and concatenates text from uploaded PDF files."""
    collected_text = []

    for file in uploaded_files:
        try:
            reader = PdfReader(BytesIO(file.read()))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
            if text:
                collected_text.append(text)
        except Exception as exc:
            raise PDFExtractionError(f"Could not read PDF '{file.name}': {exc}") from exc

    if not collected_text:
        raise PDFExtractionError("No readable text was found in the uploaded PDF files.")

    return "\n\n".join(collected_text)
