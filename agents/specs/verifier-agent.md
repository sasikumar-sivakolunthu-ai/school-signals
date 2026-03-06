# Verifier Agent

The Verifier Agent evaluates extracted waiting list updates and determines whether the data is credible.

It assigns a reliability score and flags suspicious entries.

---

## Responsibilities

Validate extracted waiting list updates

Compare new updates with historical data

Detect unrealistic rank changes

Assign a reliability score

Flag suspicious submissions

---

## Input

Structured JSON from the Extractor Agent

Example:

{
  "school_name": "Wallington High School for Girls",
  "rank_position": 108,
  "update_date": "2026-04-12",
  "source": "parent report",
  "confidence_score": 0.85
}

---

## Output

Validated record with reliability score.

Example:

{
  "school_name": "Wallington High School for Girls",
  "rank_position": 108,
  "update_date": "2026-04-12",
  "source": "parent report",
  "confidence_score": 0.85,
  "verification_score": 0.76,
  "status": "accepted"
}

---

## Validation Rules

Check historical trend for the school

Compare with previous waiting list updates

Reject unrealistic jumps

Example:

Previous rank: 120  
New rank: 118 → acceptable

Previous rank: 120  
New rank: 40 → suspicious

---

## Possible Status Values

accepted

review_required

rejected
