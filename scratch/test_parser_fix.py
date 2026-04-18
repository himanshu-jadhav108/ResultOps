
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class SubjectResult:
    subject_code: str
    total: Optional[int]
    grade: Optional[str]
    grade_point: Optional[float]
    credit_point: Optional[float]
    credits: Optional[int] = None

_GRADE_PATTERN = re.compile(r"\b(O|A\+|A|B\+|B|C|D|F|P|AB|FF|E)\b")
_NUMBER_PATTERN = re.compile(r"\b(\d{1,3})\b")

def mock_parse_subject_line(line):
    # Old logic
    tokens = line.split()
    subject_code = tokens[0]
    rest = " ".join(tokens[1:])
    numbers = [int(m) for m in _NUMBER_PATTERN.findall(rest)]
    grade_match = _GRADE_PATTERN.search(rest)
    grade = grade_match.group(1) if grade_match else None
    
    total_old = numbers[-1] if numbers else None
    
    # Proposed new logic
    # Find grade and its position
    grade_match = _GRADE_PATTERN.search(rest)
    if not grade_match:
        return {"code": subject_code, "total_old": total_old, "total_new": "NO_GRADE"}

    grade = grade_match.group(1)
    grade_start = grade_match.start()
    
    # Split tokens into left and right of grade
    left_part = rest[:grade_start].strip()
    right_part = rest[grade_match.end():].strip()
    
    left_numbers = [int(m) for m in _NUMBER_PATTERN.findall(left_part)]
    right_numbers = [int(m) for m in _NUMBER_PATTERN.findall(right_part)]
    
    # Heuristic: ... Total Credits GRADE GP CP
    total_new = None
    credits = None
    gp = None
    cp = None
    
    if len(left_numbers) >= 2:
        total_new = left_numbers[-2]
        credits = left_numbers[-1]
    elif len(left_numbers) == 1:
        total_new = left_numbers[0]
        
    if len(right_numbers) >= 2:
        gp = right_numbers[0]
        cp = right_numbers[1]
    elif len(right_numbers) == 1:
        gp = right_numbers[0]

    return {
        "line": line,
        "code": subject_code,
        "grade": grade,
        "total_old": total_old,
        "total_new": total_new,
        "credits": credits,
        "gp": gp,
        "cp": cp
    }

test_lines = [
    "410241  45  18  20  --  83  4  O  10  40",
    "410242  40  15  --  --  55  3  A  9  27",
    "410244  25  8   --  --  33  3  F  0  0",
    "310241  20  10  30  2  A  8  16", # Subject with fewer components
]

print(f"{'Line':<45} | OldTot | NewTot | Credits | GP | CP")
print("-" * 85)
for line in test_lines:
    res = mock_parse_subject_line(line)
    print(f"{res['line'][:45]:<45} | {res['total_old']:<6} | {res['total_new']:<6} | {res['credits']:<7} | {res['gp']:<2} | {res['cp']:<2}")
