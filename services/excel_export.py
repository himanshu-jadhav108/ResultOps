"""
ResultOps - Excel Export Service
Generates multi-sheet Excel workbooks for result reports.
"""

import io
import logging
from typing import Optional

import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from analytics.analytics import Analytics

logger = logging.getLogger(__name__)

_HEADER_FILL  = PatternFill("solid", fgColor="1F4E79")
_ALT_FILL     = PatternFill("solid", fgColor="D6E4F7")
_HEADER_FONT  = Font(bold=True, color="FFFFFF", size=11)
_BORDER_SIDE  = Side(style="thin", color="AAAAAA")
_CELL_BORDER  = Border(
    left=_BORDER_SIDE, right=_BORDER_SIDE,
    top=_BORDER_SIDE, bottom=_BORDER_SIDE
)


class ExcelExportService:
    """Generates Excel reports for a semester."""

    def __init__(self):
        self.analytics = Analytics()

    def generate_excel(self, semester_id: str, title: str = "ResultOps Report") -> bytes:
        """
        Generate a complete Excel workbook with:
        - Rank List sheet
        - Subject Analytics sheet
        - SGPA Distribution sheet
        
        Returns:
            Raw bytes of the .xlsx file.
        """
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Sheet 1: Rank List
            rank_df = self.analytics.student_rank_list(semester_id)
            if not rank_df.empty:
                rank_df.to_excel(writer, sheet_name="Rank List", index=False)
                _style_sheet(writer.sheets["Rank List"], rank_df)

            # Sheet 2: Subject Analytics
            subj_df = self.analytics.subject_analytics(semester_id)
            if not subj_df.empty:
                subj_df.to_excel(writer, sheet_name="Subject Analytics", index=False)
                _style_sheet(writer.sheets["Subject Analytics"], subj_df)

            # Sheet 3: SGPA Distribution
            dist_df = self.analytics.sgpa_distribution(semester_id)
            if not dist_df.empty:
                dist_df.to_excel(writer, sheet_name="SGPA Distribution", index=False)
                _style_sheet(writer.sheets["SGPA Distribution"], dist_df)

            # Sheet 4: Summary
            summary = self.analytics.semester_summary(semester_id)
            if summary:
                summary_df = pd.DataFrame(
                    list(summary.items()), columns=["Metric", "Value"]
                )
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
                _style_sheet(writer.sheets["Summary"], summary_df)

        output.seek(0)
        return output.read()


def _style_sheet(ws, df: pd.DataFrame) -> None:
    """Apply formatting to a worksheet: header row + alternating row colors."""
    # Style header row
    for col_num, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill   = _HEADER_FILL
        cell.font   = _HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = _CELL_BORDER

    # Style data rows
    for row_num in range(2, ws.max_row + 1):
        fill = _ALT_FILL if row_num % 2 == 0 else PatternFill()
        for col_num in range(1, ws.max_column + 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.fill   = fill
            cell.border = _CELL_BORDER
            cell.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-fit column widths
    for col_num, col_name in enumerate(df.columns, start=1):
        col_letter = get_column_letter(col_num)
        max_len = max(
            len(str(col_name)),
            *[len(str(ws.cell(row=r, column=col_num).value or "")) for r in range(2, ws.max_row + 1)],
            0
        )
        ws.column_dimensions[col_letter].width = min(max_len + 4, 40)
