"""
ResultOps - Metadata Extractor
Dynamically detects university, college, department, session, and semester
from the PDF text without any hardcoding.
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PDFMetadata:
    university_name: str
    college_name: str
    department_name: str
    semester_number: int
    session_type: str   # 'Winter' or 'Summer'
    session_year: int


def extract_metadata(full_text: str) -> PDFMetadata:
    """
    Extract all global metadata from full PDF text.
    Parses university, college, department, semester, and session info.
    
    Args:
        full_text: Complete concatenated text from all PDF pages.
    
    Returns:
        PDFMetadata dataclass with all detected fields.
    
    Raises:
        ValueError: If required fields cannot be detected.
    """
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    university_name = _extract_university(lines)
    college_name = _extract_college(full_text)
    department_name = _extract_department(full_text)
    session_type, session_year = _extract_session(full_text)
    semester_number = _extract_semester_number(full_text)

    logger.info(
        f"Metadata extracted: University={university_name}, "
        f"College={college_name}, Dept={department_name}, "
        f"Sem={semester_number}, Session={session_type} {session_year}"
    )

    return PDFMetadata(
        university_name=university_name,
        college_name=college_name,
        department_name=department_name,
        semester_number=semester_number,
        session_type=session_type,
        session_year=session_year,
    )


def _extract_university(lines: list[str]) -> str:
    """
    University name is typically the first non-empty, non-numeric line.
    Falls back to first line if nothing else matches.
    """
    for line in lines[:10]:
        # Skip page numbers, single chars, or lines that look like headers
        if len(line) > 10 and not re.match(r'^\d+$', line):
            return line.strip()
    return lines[0] if lines else "Unknown University"


def _extract_college(text: str) -> str:
    """
    College name appears after PunCode or as the second header line.
    Pattern: look for line containing PunCode or 'College' keyword near top.
    """
    # Try: line after PunCode pattern
    match = re.search(r'PunCode\s*[:\-]?\s*\d+\s*\n(.+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Try: line containing 'College of' or ending in 'College'
    match = re.search(
        r'([A-Z][^\n]{5,60}(?:College|Institute|Engineering)[^\n]*)',
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # Try: second non-empty line
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) > 1:
        return lines[1]

    return "Unknown College"


def _extract_department(text: str) -> str:
    """
    Department / branch extracted from 'Branch :' or 'Department :' pattern.
    """
    match = re.search(
        r'(?:Branch|Department)\s*[:\-]\s*(.+)',
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # Fallback: look for Engineering branch names
    match = re.search(
        r'(Computer Engineering|IT|Electronics|Mechanical|Civil|'
        r'Electrical|Information Technology|E&TC|Chemical)[^\n]*',
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    return "Unknown Department"


def _extract_session(text: str) -> tuple[str, int]:
    """
    Extract session type (Winter/Summer) and year from PDF title/header.
    Examples:
        'College Ledger(Winter Session 2025)' → ('Winter', 2025)
        'Summer Session 2024'                 → ('Summer', 2024)
    """
    match = re.search(
        r'(Winter|Summer)\s+Session\s+(\d{4})',
        text, re.IGNORECASE
    )
    if match:
        return match.group(1).capitalize(), int(match.group(2))

    # Fallback: just find a 4-digit year
    year_match = re.search(r'\b(20\d{2})\b', text)
    year = int(year_match.group(1)) if year_match else 2025

    # Guess session from month context or default to Winter
    session = "Winter" if re.search(r'winter|nov|dec|jan', text, re.IGNORECASE) else "Summer"
    return session, year


def _extract_semester_number(text: str) -> int:
    """
    Extract semester number from 'SEMESTER: <n>' pattern.
    Takes the first occurrence (all students in a ledger share the same semester).
    """
    match = re.search(r'SEMESTER\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Try: 'Sem-4', 'SEM IV', etc.
    roman = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8}
    match = re.search(
        r'Sem(?:ester)?\s*[-]?\s*(VIII|VII|VI|IV|V|III|II|I|\d)',
        text, re.IGNORECASE
    )
    if match:
        val = match.group(1).upper()
        return roman.get(val, int(val) if val.isdigit() else 1)

    raise ValueError("Could not detect semester number from PDF. Check PDF format.")
