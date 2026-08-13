#!/usr/bin/env python3
"""
Creates a CSV of Appalachian English existentials from speaker data in 
aapcappe_speakers.csv for use in a logistic regression.

The output contains one row per detected token, preserves the original 
speaker-data columns, and adds predictors.

Recognized existential markers:
    there, they, it

Recognized finite forms:
    is, are, was, were
    's, 're
    isn't, aren't, wasn't, weren't
    ain't, hain't

Usages covered:
    there's people
    there are people
    there was people
    there were people
    there ain't people
    there hain't people
    they's people
    they was people
    they were people
    it's people
    it was people

Usage (for a headerless CSV):
    python count_existentials.py aapcappe_speakers.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


APOSTROPHES = str.maketrans({
    "’": "'",
    "‘": "'",
    "`": "'",
    "´": "'",
})

INTERVENING = (
    r"really|just|still|always|usually|often|sometimes|ever|never|"
    r"probably|maybe|perhaps|actually|already|now|then|only|even|"
    r"right|well|pretty|about|nearly|hardly|scarcely|kinda|sorta"
)

PATTERN = re.compile(
    rf"""
    (?<![A-Za-z0-9_])
    (?P<marker>there|they|it)
    (?:
        \s+(?:{INTERVENING})
    ){{0,3}}
    \s*
    (?P<verb>
        wasn't|weren't|isn't|aren't|
        hain't|ain't|
        was|were|is|are|
        's|'re
    )
    (?![A-Za-z0-9_])
    """,
    re.IGNORECASE | re.VERBOSE,
)

PRESENT = {"is", "are", "'s", "'re", "isn't", "aren't", "ain't", "hain't"}
PAST = {"was", "were", "wasn't", "weren't"}
SINGULAR = {"is", "'s", "was", "isn't", "wasn't"}
PLURAL = {"are", "'re", "were", "aren't", "weren't"}
NEGATIVE = {"isn't", "aren't", "wasn't", "weren't", "ain't", "hain't"}
CONTRACTED = {"'s", "'re", "isn't", "aren't", "wasn't", "weren't", "ain't", "hain't"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument(
        "--output_csv", 
        type=Path,
        default="aapcappe_existentials.csv", 
        help="Path to the output file (default: aapcappe_existentials.csv)"
    )
    parser.add_argument(
        "--speaker-column",
        type=int,
        required=False,
        default=0,
        help="Zero-based speaker-ID column.",
    )
    parser.add_argument(
        "--text-column",
        type=int,
        required=False,
        default=2,
        help="Zero-based transcript-text column.",
    )
    return parser.parse_args()


def normalize(text: str) -> str:
    text = text.translate(APOSTROPHES)
    return re.sub(r"\s+", " ", text).strip()


def classify(marker: str, verb: str) -> dict[str, object]:
    marker = marker.lower()
    verb = verb.lower()

    if verb in PRESENT:
        tense = "present"
    elif verb in PAST:
        tense = "past"
    else:
        tense = "unknown"

    if verb in SINGULAR:
        verb_number = "singular"
        outcome = 1
    elif verb in PLURAL:
        verb_number = "plural"
        outcome = 0
    else:
        # ain't and hain't are not transparently singular/plural.
        verb_number = "unmarked"
        outcome = ""

    polarity = "negative" if verb in NEGATIVE else "affirmative"
    contracted = int(verb in CONTRACTED)

    if verb in {"'s", "'re"}:
        construction = f"{marker}{verb}"
    else:
        construction = f"{marker} {verb}"

    # THERE is usually unambiguous. THEY and IT to be checked manually.
    manual_review = int(marker in {"they", "it"})

    return {
        "marker": marker,
        "verb_form": verb,
        "construction": construction,
        "tense": tense,
        "verb_number": verb_number,
        "outcome_singular": outcome,
        "polarity": polarity,
        "contracted": contracted,
        "manual_review": manual_review,
    }


def main() -> int:
    args = parse_args()

    if not args.input_csv.exists():
        print(f"Error: file not found: {args.input_csv}", file=sys.stderr)
        return 1

    with args.input_csv.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    if not rows:
        print("Error: input CSV is empty.", file=sys.stderr)
        return 1

    width = max(len(row) for row in rows)
    original_headers = [f"column_{i}" for i in range(width)]

    added_headers = [
        "speaker_id",
        "source_row",
        "token_number",
        "matched_text",
        "marker",
        "verb_form",
        "construction",
        "tense",
        "verb_number",
        "outcome_singular",
        "polarity",
        "contracted",
        "manual_review",
    ]

    tokens_written = 0

    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=original_headers + added_headers,
        )
        writer.writeheader()

        for source_row, original_row in enumerate(rows, start=1):
            row = original_row + [""] * (width - len(original_row))

            if max(args.speaker_column, args.text_column) >= len(row):
                continue

            speaker_id = row[args.speaker_column].strip()
            text = normalize(row[args.text_column])

            matches = list(PATTERN.finditer(text))

            for token_number, match in enumerate(matches, start=1):
                features = classify(
                    match.group("marker"),
                    match.group("verb"),
                )

                output = dict(zip(original_headers, row))
                output.update({
                    "speaker_id": speaker_id,
                    "source_row": source_row,
                    "token_number": token_number,
                    "matched_text": match.group(0),
                    **features,
                })

                writer.writerow(output)
                tokens_written += 1

    print(f"Wrote {tokens_written} token(s) to {args.output_csv}")
    print(
        "outcome_singular: 1 = singular BE, 0 = plural BE, "
        "blank = unmarked ain't/hain't"
    )
    print(
        "manual_review: 1 = existential THEY/IT candidate; "
        "0 = existential THERE"
    )

    return 0


if __name__ == "__main__":
    main()