"""
ResultOps - PDF Parser
Extracts raw text from text-based university ledger PDFs using pdfplumber.
"""

import logging
from pathlib import Path
from typing import Union

import pdfplumber

logger = logging.getLogger(__name__)


def extract_text_from_pdf(source: Union[str, Path, bytes]) -> str:
    """
    Extract full text from a text-based PDF ledger.

    Args:
        source: File path (str/Path) or raw bytes (from Streamlit upload).

    Returns:
        Concatenated text from all pages.

    Raises:
        ValueError: If the PDF is empty or contains no extractable text.
        RuntimeError: If pdfplumber fails to open the file.
    """
    import io

    try:
        if isinstance(source, (str, Path)):
            pdf_file = open(source, "rb")
        else:
            # Assume bytes (from st.file_uploader)
            pdf_file = io.BytesIO(source)

        with pdfplumber.open(pdf_file) as pdf:
            if not pdf.pages:
                raise ValueError("PDF contains no pages.")

            pages_text = []
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if text:
                    pages_text.append(text)
                else:
                    logger.warning(f"Page {page_num} returned no text (possible scan).")

            full_text = "\n".join(pages_text)

        if not full_text.strip():
            raise ValueError(
                "No text could be extracted. This PDF may be scanned/image-based. "
                "ResultOps requires text-based PDFs."
            )

        logger.info(f"Extracted {len(full_text)} characters from {len(pages_text)} pages.")
        return full_text

    except pdfplumber.utils.exceptions.PDFSyntaxError as e:
        raise RuntimeError(f"PDF is corrupted or not a valid PDF file: {e}") from e
