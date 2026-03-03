"""
Refactored PDF parser with modular architecture and confidence scoring.
"""

import re
import pdfplumber
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class ParsedSubject:
    """Represents a parsed subject entry."""
    code: str
    internal: Optional[int] = None
    external: Optional[int] = None
    practical: Optional[int] = None
    oral: Optional[int] = None
    total: Optional[int] = None
    credits: Optional[int] = None
    grade: Optional[str] = None
    grade_points: Optional[int] = None
    credits_earned: Optional[int] = None
    is_ac: bool = False  # Audit course flag


@dataclass
class StudentRecord:
    """Represents a complete student record."""
    prn: str
    seat_no: str
    name: str
    semester: int
    sgpa: float
    credits_earned: int
    credits_total: int
    status: str  # PASS/FAIL
    subjects: List[ParsedSubject] = field(default_factory=list)
    total_marks: Optional[int] = None
    percentage: Optional[float] = None


@dataclass
class PDFMetadata:
    """Metadata extracted from PDF."""
    university: str = ""
    college: str = ""
    department: str = ""
    session: str = ""
    semester: int = 0
    exam_year: int = 0
    total_students: int = 0


class ParsingConfidenceCalculator:
    """Calculates confidence score based on parsing quality."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
    
    def calculate_confidence(self, students: List[StudentRecord], 
                           metadata: PDFMetadata,
                           raw_text: str) -> Tuple[float, List[str]]:
        """
        Calculate parsing confidence score (0.0 to 1.0).
        
        Returns:
            Tuple of (confidence_score, warnings)
        """
        if not students:
            return 0.0, ["No students found in PDF"]
        
        total_checks = 0
        passed_checks = 0
        
        # Check 1: Metadata completeness (20%)
        total_checks += 1
        if metadata.university and metadata.college and metadata.semester > 0:
            passed_checks += 1
        else:
            self.warnings.append("Incomplete metadata detected")
        
        # Check 2: PRN validity (20%)
        total_checks += 1
        valid_prns = sum(1 for s in students if self._validate_prn(s.prn))
        if valid_prns == len(students):
            passed_checks += 1
        else:
            self.warnings.append(f"Invalid PRN format in {len(students) - valid_prns} students")
        
        # Check 3: SGPA consistency (20%)
        total_checks += 1
        valid_sgpa = sum(1 for s in students if 0 <= s.sgpa <= 10)
        if valid_sgpa == len(students):
            passed_checks += 1
        else:
            self.warnings.append(f"SGPA out of range for {len(students) - valid_sgpa} students")
        
        # Check 4: Subject count consistency (20%)
        total_checks += 1
        subject_counts = [len(s.subjects) for s in students]
        if len(set(subject_counts)) == 1 and subject_counts[0] > 0:
            passed_checks += 1
        else:
            self.warnings.append("Inconsistent subject counts across students")
        
        # Check 5: Grade validity (20%)
        total_checks += 1
        valid_grades = all(
            all(sub.grade in ['O', 'A', 'B', 'C', 'D', 'E', 'F', 'P', 'PP', 'NP', None] 
                for sub in s.subjects)
            for s in students
        )
        if valid_grades:
            passed_checks += 1
        else:
            self.warnings.append("Unexpected grade values detected")
        
        confidence = passed_checks / total_checks
        
        # Additional penalty for missing critical fields
        for student in students:
            if not student.name or student.name.strip() == "":
                confidence -= 0.05
                self.warnings.append(f"Missing name for PRN {student.prn}")
            
            if student.credits_earned > student.credits_total:
                confidence -= 0.05
                self.warnings.append(f"Invalid credits for PRN {student.prn}")
        
        return max(0.0, confidence), self.warnings
    
    def _validate_prn(self, prn: str) -> bool:
        """Validate PRN format."""
        # Typical SPPU PRN: 10-15 alphanumeric characters
        pattern = r'^[A-Z0-9]{10,15}$'
        return bool(re.match(pattern, prn.upper()))


class MetadataExtractor:
    """Extracts metadata from PDF text."""
    
    PATTERNS = {
        'university': r'(?:University|UNIVERSITY)[:\s]+([^\n]+)',
        'college': r'(?:College|COLLEGE)[:\s]+([^\n]+)',
        'department': r'(?:Department|DEPARTMENT|Branch|BRANCH)[:\s]+([^\n]+)',
        'session': r'(?:Session|SESSION)[:\s]+([^\n]+)',
        'semester': r'(?:Semester|SEMESTER)[:\s]+(\d+)',
        'exam_year': r'(?:Year|YEAR)[:\s]+(\d{4})'
    }
    
    def extract(self, text: str) -> PDFMetadata:
        """Extract metadata from text."""
        metadata = PDFMetadata()
        
        for field, pattern in self.PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field == 'semester':
                    metadata.semester = int(value)
                elif field == 'exam_year':
                    metadata.exam_year = int(value)
                else:
                    setattr(metadata, field, value)
        
        # Infer university if not found
        if not metadata.university:
            if 'SPPU' in text or 'Savitribai' in text:
                metadata.university = "Savitribai Phule Pune University"
        
        return metadata


class StudentBlockParser:
    """Parses individual student blocks."""
    
    # PRN pattern: PRN: <number> or PRN <number>
    PRN_PATTERN = r'PRN[:\s]+([A-Z0-9]+)'
    SEAT_PATTERN = r'SEAT\s*NO[:\s]+([A-Z0-9]+)'
    NAME_PATTERN = r'NAME[:\s]+([^\n]+?)(?=\s+(?:PRN|SEAT|RESULT|$))'
    SGPA_PATTERN = r'SGPA[:\s]+(\d+\.?\d*)'
    CREDITS_PATTERN = r'Credits\s*Earned/Total\s*:\s*(\d+)/(\d+)'
    
    # Subject line pattern
    SUBJECT_PATTERN = r'(\d{6})\s+(\d+|--)\s+(\d+|--)\s+(\d+|--)?\s+(\d+|--)?\s+(\d+|--)\s+(\d)\s+([A-Z]+)\s+(\d+|--)\s+(\d+)'
    
    def split_student_blocks(self, text: str) -> List[str]:
        """Split text into individual student blocks."""
        # Split by PRN or "RESULT" keyword
        pattern = r'(?=PRN[:\s]+[A-Z0-9]+)'
        blocks = re.split(pattern, text)
        
        # Filter valid blocks (must contain PRN)
        valid_blocks = []
        for block in blocks:
            if re.search(self.PRN_PATTERN, block):
                valid_blocks.append(block.strip())
        
        return valid_blocks
    
    def parse_student_block(self, block: str) -> Optional[StudentRecord]:
        """Parse a single student block."""
        # Extract PRN
        prn_match = re.search(self.PRN_PATTERN, block)
        if not prn_match:
            return None
        prn = prn_match.group(1).strip().upper()
        
        # Extract Seat No
        seat_match = re.search(self.SEAT_PATTERN, block)
        seat_no = seat_match.group(1).strip() if seat_match else ""
        
        # Extract Name
        name_match = re.search(self.NAME_PATTERN, block, re.DOTALL)
        name = name_match.group(1).strip() if name_match else "Unknown"
        
        # Extract SGPA
        sgpa_match = re.search(self.SGPA_PATTERN, block)
        sgpa = float(sgpa_match.group(1)) if sgpa_match else 0.0
        
        # Extract Credits
        credits_match = re.search(self.CREDITS_PATTERN, block)
        if credits_match:
            credits_earned = int(credits_match.group(1))
            credits_total = int(credits_match.group(2))
        else:
            credits_earned = 0
            credits_total = 0
        
        # Determine status
        status = "PASS" if credits_earned >= credits_total else "FAIL"
        
        # Extract Semester
        sem_match = re.search(r'SEMESTER[:\s]+(\d+)', block)
        semester = int(sem_match.group(1)) if sem_match else 0
        
        # Parse subjects
        subjects = self._parse_subjects(block)
        
        # Calculate total marks
        total_marks = sum(
            (sub.total or 0) for sub in subjects if not sub.is_ac
        )
        
        return StudentRecord(
            prn=prn,
            seat_no=seat_no,
            name=name,
            semester=semester,
            sgpa=sgpa,
            credits_earned=credits_earned,
            credits_total=credits_total,
            status=status,
            subjects=subjects,
            total_marks=total_marks
        )
    
    def _parse_subjects(self, block: str) -> List[ParsedSubject]:
        """Parse subject lines from student block."""
        subjects = []
        lines = block.split('\n')
        
        for line in lines:
            # Check for AC (Audit Course) marker
            is_ac = 'AC' in line or 'Audit' in line
            
            # Try to match subject pattern
            match = re.search(self.SUBJECT_PATTERN, line)
            if match:
                groups = match.groups()
                subject = ParsedSubject(
                    code=groups[0],
                    internal=int(groups[1]) if groups[1] != '--' else None,
                    external=int(groups[2]) if groups[2] != '--' else None,
                    practical=int(groups[3]) if groups[3] and groups[3] != '--' else None,
                    oral=int(groups[4]) if groups[4] and groups[4] != '--' else None,
                    total=int(groups[5]) if groups[5] != '--' else None,
                    credits=int(groups[6]) if groups[6] else None,
                    grade=groups[7],
                    grade_points=int(groups[8]) if groups[8] != '--' else None,
                    credits_earned=int(groups[9]),
                    is_ac=is_ac
                )
                subjects.append(subject)
        
        return subjects


class ResultParser:
    """
    Main parser class that orchestrates PDF parsing.
    """
    
    def __init__(self):
        self.metadata_extractor = MetadataExtractor()
        self.student_parser = StudentBlockParser()
        self.confidence_calculator = ParsingConfidenceCalculator()
    
    def parse_pdf(self, pdf_path: str, progress_callback=None) -> Tuple[
        PDFMetadata, List[StudentRecord], float, List[str], str
    ]:
        """
        Parse PDF and return structured data with confidence score.
        
        Args:
            pdf_path: Path to PDF file
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            Tuple of (metadata, students, confidence_score, warnings, raw_text)
        """
        # Extract text from PDF
        raw_text = self._extract_text(pdf_path)
        
        # Extract metadata
        metadata = self.metadata_extractor.extract(raw_text)
        
        # Split into student blocks
        blocks = self.student_parser.split_student_blocks(raw_text)
        metadata.total_students = len(blocks)
        
        # Parse each student with progress
        students = []
        for i, block in enumerate(blocks):
            if progress_callback:
                progress_callback(i + 1, len(blocks))
            
            student = self.student_parser.parse_student_block(block)
            if student:
                students.append(student)
        
        # Calculate confidence
        confidence, warnings = self.confidence_calculator.calculate_confidence(
            students, metadata, raw_text
        )
        
        return metadata, students, confidence, warnings, raw_text
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract raw text from PDF."""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
        return text
    
    def parse_pdf_bytes(self, pdf_bytes: bytes, progress_callback=None) -> Tuple[
        PDFMetadata, List[StudentRecord], float, List[str], str
    ]:
        """Parse PDF from bytes."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        try:
            return self.parse_pdf(tmp_path, progress_callback)
        finally:
            os.unlink(tmp_path)


# Convenience functions for backward compatibility
def extract_metadata(text: str) -> PDFMetadata:
    """Extract metadata from text."""
    return MetadataExtractor().extract(text)

def split_student_blocks(text: str) -> List[str]:
    """Split text into student blocks."""
    return StudentBlockParser().split_student_blocks(text)

def parse_student_block(block: str) -> Optional[StudentRecord]:
    """Parse single student block."""
    return StudentBlockParser().parse_student_block(block)

def parse_subject_line(line: str) -> Optional[ParsedSubject]:
    """Parse single subject line."""
    # Implementation for individual line parsing
    parser = StudentBlockParser()
    # Create a dummy block with just this line
    dummy_block = f"PRN: DUMMY123\n{line}\nSGPA: 8.0"
    student = parser.parse_student_block(dummy_block)
    if student and student.subjects:
        return student.subjects[0]
    return None