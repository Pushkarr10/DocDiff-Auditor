# core/extractor.py
"""PDF extraction utilities.

Provides a simple function to extract textual paragraphs from a PDF file.
The extracted chunks are cleaned and returned as a list of strings.
"""

import fitz  # PyMuPDF


def extract_chunks(pdf_bytes: bytes) -> list[str]:
    """Extract cleaned paragraph chunks from a PDF.

    Args:
        pdf_bytes: The raw PDF file content.
    Returns:
        A list of paragraph strings.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    paragraphs: list[str] = []
    for page in doc:
        text = page.get_text("text")
        # Split on double newlines to get paragraph-like chunks
        raw_chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
        paragraphs.extend(raw_chunks)
    return paragraphs
