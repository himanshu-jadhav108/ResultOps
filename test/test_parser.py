"""
Comprehensive tests for the refactored parser.
"""

import pytest
from parser.refactored_parser import (
    MetadataExtractor,
    StudentBlockParser,
    ParsingConfidenceCalculator,
    ParsedSubject,
    StudentRecord,
    PDFMetadata,
)


class TestMetadataExtractor:
    """Test metadata extraction."""

    def test_extract_university(self):
        text = "UNIVERSITY: Savitribai Phule Pune University\nCollege: COEP"
        extractor = MetadataExtractor()
        metadata = extractor.extract(text)
        assert metadata.university == "Savitribai Phule Pune University"
        assert metadata.college == "COEP"

    def test_extract_semester(self):
        text = "SEMESTER: 5\nSession: Winter 2024"
        extractor = MetadataExtractor()
        metadata = extractor.extract(text)
        assert metadata.semester == 5
        assert metadata.session == "Winter 2024"

    def test_infer_sppu(self):
        text = "SPPU Result Ledger\nCollege: XYZ"
        extractor = MetadataExtractor()
        metadata = extractor.extract(text)
        assert "Savitribai Phule" in metadata.university


class TestStudentBlockParser:
    """Test student block parsing."""

    def test_split_blocks(self):
        text = """
        PRN: 1234567890 SEAT NO: A123456 NAME: John Doe
        SEMESTER: 5
        SGPA: 8.5
        
        PRN: 0987654321 SEAT NO: B654321 NAME: Jane Smith
        SEMESTER: 5
        SGPA: 7.2
        """
        parser = StudentBlockParser()
        blocks = parser.split_student_blocks(text)
        assert len(blocks) == 2

    def test_parse_prn_extraction(self):
        block = (
            "PRN: 123ABC456DEF SEAT NO: S123 NAME: Test Student RESULT: PASS\nSGPA: 8.0"
        )
        parser = StudentBlockParser()
        student = parser.parse_student_block(block)
        assert student is not None
        assert student.prn == "123ABC456DEF"
        assert student.seat_no == "S123"
        assert student.name == "Test Student"
        assert student.sgpa == 8.0

    def test_parse_credits(self):
        block = """
        PRN: TEST123 SEAT NO: S1 NAME: Test
        Credits Earned/Total : 22/24
        SGPA: 7.5
        """
        parser = StudentBlockParser()
        student = parser.parse_student_block(block)
        assert student.credits_earned == 22
        assert student.credits_total == 24
        assert student.status == "FAIL"  # 22 < 24

    def test_parse_subjects(self):
        block = """
        PRN: TEST123 SEAT NO: S1 NAME: Test
        410241  45  18  20  --  83  4  O  10  40
        410242  40  15  --  --  55  3  A  9  27
        SGPA: 8.0
        """
        parser = StudentBlockParser()
        student = parser.parse_student_block(block)
        assert len(student.subjects) == 2
        assert student.subjects[0].code == "410241"
        assert student.subjects[0].grade == "O"
        assert student.subjects[0].total == 83


class TestConfidenceCalculator:
    """Test confidence scoring."""

    def test_perfect_confidence(self):
        students = [
            StudentRecord(
                prn="1234567890",
                seat_no="S1",
                name="Test",
                semester=5,
                sgpa=8.5,
                credits_earned=24,
                credits_total=24,
                status="PASS",
                subjects=[ParsedSubject(code="410241", grade="O", total=80)],
            )
        ]
        metadata = PDFMetadata(
            university="SPPU", college="COEP", department="CS", semester=5
        )
        calculator = ParsingConfidenceCalculator()
        score, warnings = calculator.calculate_confidence(students, metadata, "test")
        assert score == 1.0
        assert len(warnings) == 0

    def test_low_confidence_missing_metadata(self):
        students = [
            StudentRecord(
                prn="123",
                seat_no="S1",
                name="",
                semester=0,
                sgpa=15.0,
                credits_earned=30,
                credits_total=24,
                status="PASS",
                subjects=[],
            )
        ]
        metadata = PDFMetadata()
        calculator = ParsingConfidenceCalculator()
        score, warnings = calculator.calculate_confidence(students, metadata, "test")
        assert score < 0.5
        assert len(warnings) > 0


class TestRankCalculation:
    """Test ranking logic (ranking now lives in Analytics, tested standalone here)."""

    def test_basic_ranking(self):
        from analytics.analytics import categorize_sgpa

        students = [
            {"prn": "1", "name": "A", "sgpa": 9.0},
            {"prn": "2", "name": "B", "sgpa": 8.5},
            {"prn": "3", "name": "C", "sgpa": 8.0},
        ]
        # Simulate the ranking logic from Analytics.student_rank_list
        students.sort(key=lambda r: r.get("sgpa") or 0, reverse=True)
        for i, s in enumerate(students, start=1):
            s["rank"] = i
            s["category"] = categorize_sgpa(s["sgpa"])

        assert students[0]["rank"] == 1
        assert students[1]["rank"] == 2
        assert students[2]["rank"] == 3
        assert students[0]["category"] == "Distinction"

    def test_sequential_ranking(self):
        from analytics.analytics import categorize_sgpa

        students = [
            {"prn": "1", "name": "A", "sgpa": 8.5},
            {"prn": "2", "name": "B", "sgpa": 8.5},  # Same SGPA
            {"prn": "3", "name": "C", "sgpa": 8.0},
        ]
        students.sort(key=lambda r: r.get("sgpa") or 0, reverse=True)
        for i, s in enumerate(students, start=1):
            s["rank"] = i
            s["category"] = categorize_sgpa(s["sgpa"])

        # Sequential ranking — no ties, no skipping
        assert students[0]["rank"] == 1
        assert students[1]["rank"] == 2
        assert students[2]["rank"] == 3


# Integration tests
@pytest.mark.integration
class TestFullParsing:
    """Integration tests with sample PDF structures."""

    def test_parse_sample_text(self):
        sample_text = """
        UNIVERSITY: Savitribai Phule Pune University
        College: College of Engineering Pune
        Department: Computer Engineering
        Session: Winter 2024
        
        PRN: 1020180001 SEAT NO: 1001 NAME: RAHUL SHARMA
        SEMESTER: 5

        410241  45  18  20  --  83  4  O  10  40
        410242  40  15  --  --  55  3  A  9  27
        410243  42  16  --  --  58  3  A  9  27
        410244  38  14  --  --  52  3  B  8  24
        410245  44  17  --  --  61  3  A  9  27

        Winter Session 2024 SGPA : 8.50  Credits Earned/Total : 24/24
        SGPA: (SEM-5) 8.50

        PRN: 1020180002 SEAT NO: 1002 NAME: PRIYA PATEL
        SEMESTER: 5

        410241  35  12  15  --  62  4  C  7  28
        410242  30  10  --  --  40  3  D  6  18
        410243  38  14  --  --  52  3  B  8  24
        410244  25  8   --  --  33  3  F  0  0
        410245  40  15  --  --  55  3  A  9  27
        
        Winter Session 2024 SGPA : 5.20  Credits Earned/Total : 20/24
        SGPA: (SEM-5) 5.20
        """

        # Use individual extractors for testing
        metadata = MetadataExtractor().extract(sample_text)
        blocks = StudentBlockParser().split_student_blocks(sample_text)
        students = [StudentBlockParser().parse_student_block(b) for b in blocks]
        students = [s for s in students if s]

        assert metadata.university is not None
        assert len(students) == 2
        assert students[0].sgpa == 8.5
        assert students[1].sgpa == 5.2
        assert students[1].status == "FAIL"
