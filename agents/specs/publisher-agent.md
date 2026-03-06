# Publisher Agent

The Publisher Agent publishes verified waiting list updates and generates summaries for the dashboard.

It converts verified admission data into timeline updates and trend insights.

---

## Responsibilities

Update waiting list movement timeline

Generate summary insights

Publish updates to dashboard

Provide simple explanations for users

---

## Input

Validated record from Verifier Agent.

Example:

{
  "school_name": "Wallington High School for Girls",
  "rank_position": 108,
  "update_date": "2026-04-12",
  "verification_score": 0.82,
  "status": "accepted"
}

---

## Output

Dashboard update record.

Example:

{
  "school": "Wallington High School for Girls",
  "timeline_event": "Waiting list moved to rank 108",
  "date": "2026-04-12",
  "confidence": "High"
}

---

## Dashboard Summary Example

Wallington High School for Girls waiting list moved to rank 108 on April 12.

Movement trend: slow progression.

Confidence level: high.
