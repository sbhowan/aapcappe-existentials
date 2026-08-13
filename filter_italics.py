#!/usr/bin/env python3
"""
Filters an Excel workbook by italic formatting and exports the kept rows to
CSV for analysis of output of AAPCAppE text search.

Usage:
    python filter_italics.py aapcappe_raw_output.xlsx aapcappe_speakers_only.csv

Requires:
    python -m pip install --upgrade openpyxl
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock


input_xlsx = sys.argv[1]
output_csv = sys.argv[2]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export Excel rows containing any italic text to CSV."
        )
    )
    parser.add_argument(input_xlsx, type=Path, help="Input .xlsx workbook")
    parser.add_argument(output_csv, type=Path, help="Output .csv file")
    return parser.parse_args()


def cell_contains_italics(cell: Any) -> bool:
    """
    Return True when either:
    1. the entire cell is italic, or
    2. at least one rich-text run inside the cell is italic.
    """
    # Entire-cell formatting
    if cell.font is not None and cell.font.italic is True:
        return True

    value = cell.value

    # Partial-cell rich-text formatting
    if isinstance(value, CellRichText):
        for run in value:
            if isinstance(run, TextBlock) and run.font.i is True:
                return True

    return False


def plain_value(value: Any) -> Any:
    """
    Converts rich-text cells to plain text for CSV output.
    """
    if isinstance(value, CellRichText):
        return str(value)
    return value


def main() -> int:
    workbook = load_workbook(
    input_xlsx,
    rich_text=True,
    data_only=False,
    )

    worksheet = workbook.active

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        kept = 0

        for row in worksheet.iter_rows():
        # Keep the entire row if any cell contains italic text
            if any(cell_contains_italics(cell) for cell in row):
                writer.writerow([plain_value(cell.value) for cell in row])
                kept += 1

    print(f"Kept {kept} rows.")


if __name__ == "__main__":
    main()
