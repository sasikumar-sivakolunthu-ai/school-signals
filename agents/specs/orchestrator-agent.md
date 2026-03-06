# Orchestrator Agent

The Orchestrator Agent coordinates the entire School Signal workflow.

It receives raw updates and decides which agents to invoke in sequence.

---

## Responsibilities

Receive raw admission updates

Trigger Extractor Agent

Send extracted data to Verifier Agent

Send verified records to Publisher Agent

Handle errors or missing data

---

## Workflow

Admin paste update

↓

Orchestrator receives raw text

↓

Call Extractor Agent

↓

Receive structured data

↓

Call Verifier Agent

↓

Receive verification result

↓

If status = accepted

↓

Call Publisher Agent

↓

Update dashboard

---

## Failure Handling

If data extraction fails → request manual review.

If verification status = review_required → flag for admin.

If verification status = rejected → discard record.

---

## Example Flow

Input:

Wallington Girls waiting list moved to rank 108 today.

Orchestrator steps:

1. Send text to Extractor Agent
2. Receive structured data
3. Send data to Verifier Agent
4. If accepted → send to Publisher Agent
5. Update dashboard timeline
