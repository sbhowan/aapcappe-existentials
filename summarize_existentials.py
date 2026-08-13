#!/usr/bin/env python3
"""
Creates one summary-table CSV from the token-level existential dataset.

Input:
    The CSV created by count_existentials.py 
    (default: aapcappe_existentials.csv)

Output:
    One long-format summary table with:
        variable
        category
        count
        percent

The table summarizes:
    construction
    marker
    verb_form
    tense
    verb_number
    outcome_singular
    polarity
    contracted
    manual_review

Usage:
    python summarize_existentials.py aapcappe_existentials.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


SUMMARY_VARIABLES = [
    "construction",
    "marker",
    "verb_form",
    "tense",
    "verb_number",
    "outcome_singular",
    "polarity",
    "contracted",
    "manual_review",
]


LABELS = {
    ("outcome_singular", "1"): "Singular BE",
    ("outcome_singular", "0"): "Plural BE",
    ("outcome_singular", ""): "Unmarked BE",
    ("contracted", "1"): "Contracted",
    ("contracted", "0"): "Uncontracted",
    ("manual_review", "1"): "Manual review",
    ("manual_review", "0"): "Automatic match",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a count/percentage summary table."
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument(
        "--output_csv", 
        type=Path,
        default="appcappe_summary.csv")
    return parser.parse_args()


def display_category(variable: str, value: str) -> str:
    return LABELS.get((variable, value), value if value else "Missing/Unmarked")


def main() -> int:
    args = parse_args()

    if not args.input_csv.exists():
        print(f"Error: file not found: {args.input_csv}", file=sys.stderr)
        return 1

    with args.input_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if not rows:
        print("Error: input CSV contains no token rows.", file=sys.stderr)
        return 1

    missing_columns = [
        column for column in SUMMARY_VARIABLES
        if column not in reader.fieldnames
    ]

    if missing_columns:
        print(
            "Error: missing required columns: "
            + ", ".join(missing_columns),
            file=sys.stderr,
        )
        return 1

    summary_rows = []

    # Overall token count
    summary_rows.append({
        "variable": "overall",
        "category": "All tokens",
        "count": len(rows),
        "percent": "100.00",
    })

    for variable in SUMMARY_VARIABLES:
        counts = Counter(row.get(variable, "").strip() for row in rows)
        total = sum(counts.values())

        for value, count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            percent = (count / total * 100) if total else 0

            summary_rows.append({
                "variable": variable,
                "category": display_category(variable, value),
                "count": count,
                "percent": f"{percent:.2f}",
            })

    with args.output_csv.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["variable", "category", "count", "percent"],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Read {len(rows)} token(s).")
    print(f"Saved summary table to: {args.output_csv}")

    return 0


if __name__ == "__main__":
    main()