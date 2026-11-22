# Decisions

## Decision: compare B value with A total_value
- Rejected: compare with base_value
- Why: B's amount represents the final A amount, while `total_value` is the base plus adjustment. The README and data contract state that this is the money field to match.

## Decision: store unreadable amounts as null
- Rejected: store blanks or junk as zero
- Why: A blank or bad amount means unknown and must not be mistaken for an exact $0. The raw text is retained by `value_raw`.

## Decision: normalize B references
- Rejected: exact string matching
- Why: Digits identify the record across formats such as `rec1034`, `REC - 1070`, and `1112`. The normalized form is `REC-<digits>`.

## Decision: treat two entries as a split only when they sum exactly
- Rejected: ignore every record with multiple B entries
- Why: Equal-amount duplicates do not sum unexpectedly in this rule, while two parts that sum to A's total are an accepted split.

## Decision: ignore VOIDED A records
- Rejected: compare voided records normally
- Why: For reconciliation purposes a voided A record is not an active disagreement. A separate B entry or missing entry will not create noise for the voided record.

## Decision: count date and location as disagreements
- Rejected: compare only value
- Why: The assignment explicitly asks for location and date mismatch rules as useful extra reasons.

## Decision: use SQLite and Decimal
- Rejected: float or another database
- Why: SQLite is supported by Django and fits the one-day local assessment. `DecimalField` keeps money comparisons exact.

## Decision: hide foreign location details
- Rejected: return both organizations' location IDs
- Why: Every API row belongs to the queried org. For a cross-org location mismatch, the foreign B location is omitted and only the A-side location is exposed.
