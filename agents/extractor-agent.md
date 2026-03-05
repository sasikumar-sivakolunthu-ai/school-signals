# Extractor Agent

The Extractor Agent converts raw admission updates into structured data.

It processes text pasted by administrators or collected from external sources.

Example input:

Wallington High School for Girls waiting list moved to rank 108 on April 12.

---

## Responsibilities

Identify the school name

Extract waiting list rank

Extract update date

Determine source type

Generate a confidence score

---

## Input

Raw text update

Example:

Wallington Girls waiting list moved to rank 108 today.

---

## Output JSON

{
  "school_name": "Wallington High School for Girls",
  "rank_position": 108,
  "update_date": "2026-04-12",
  "source": "school website",
  "confidence_score": 0.92
}

---

## Processing Logic

1. Identify school name from text
2. Extract numerical rank
3. Detect date references
4. Classify source
5. Generate confidence score
