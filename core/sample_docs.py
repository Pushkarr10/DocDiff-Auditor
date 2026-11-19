# core/sample_docs.py
"""Utility to provide built‑in sample contract PDFs.

The functions return the PDF content as ``bytes`` objects so that the
Streamlit app can treat them exactly like an uploaded file.
"""

import fitz  # PyMuPDF


def _make_pdf(text: str) -> bytes:
    """Create a one‑page PDF containing *text*.

    The PDF is generated entirely in memory and returned as ``bytes``.
    """
    doc = fitz.open()
    page = doc.new_page()
    # Insert the text with some basic formatting.
    rect = page.rect
    margin = 72  # 1 inch
    text_rect = fitz.Rect(
        rect.x0 + margin,
        rect.y0 + margin,
        rect.x1 - margin,
        rect.y1 - margin,
    )
    page.insert_textbox(text_rect, text, fontsize=11, lineheight=1.2)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# Sample contract – version 1
VERSION_1 = """\
Sample Contract – Version 1

1. Confidentiality
Both parties agree to keep confidential all proprietary information.

2. Termination
Either party may terminate this agreement with 30 days written notice.

3. Governing Law
This agreement shall be governed by the laws of Example State.
"""

# Sample contract – version 2 (semantic changes, added & removed clauses)
VERSION_2 = """\
Sample Contract – Version 2

1. Confidentiality
Both parties shall maintain strict confidentiality of all sensitive data.

2. Termination
Either party may terminate this agreement with 45 days written notice.

3. Liability
Each party is liable for damages caused by its negligence.

4. Governing Law
This agreement shall be governed by the laws of Example State.
"""


def get_sample_pdfs() -> tuple[bytes, bytes]:
    """Return a tuple ``(baseline_pdf, revised_pdf)`` containing the two
    sample contracts as PDF bytes.
    """
    return _make_pdf(VERSION_1), _make_pdf(VERSION_2)
