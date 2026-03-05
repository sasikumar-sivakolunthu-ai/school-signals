# School Signal Architecture

School Signal is an AI-powered platform that tracks grammar school waiting list movements and admissions signals.

The system collects information from official sources and parent submissions, verifies it using AI agents and publishes a timeline dashboard.

---

## Core Components

### 1. Frontend Dashboard

Displays:

- waiting list movement timeline
- school admission insights
- latest updates

Technology:

- Next.js
- Tailwind CSS
- Supabase client

---

### 2. Admin Paste Tool

Internal interface used to paste updates from:

- school websites
- admission emails
- parent reports

The pasted text is processed by the Extractor Agent.

---

### 3. AI Agents

The system uses multiple agents.

Collector Agent  
Collects raw admissions signals.

Extractor Agent  
Extracts structured data from text.

Verifier Agent  
Validates submissions and calculates confidence score.

Publisher Agent  
Updates the timeline dashboard.

---

### 4. Supabase Backend

Supabase provides:

Database  
Authentication  
API layer  
Storage

Database tables include:

schools  
waiting_list_updates  
parent_reports

---

### 5. Timeline Engine

Aggregates updates and produces a visual movement timeline for each school.

---

## High-Level Flow

Parent submission or official update

↓

Admin paste tool

↓

Extractor agent

↓

Verifier agent

↓

Database storage

↓

Timeline dashboard update
