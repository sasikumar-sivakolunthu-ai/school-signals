# school-signals

AI-powered school admissions intelligence platform focused on grammar school waiting list movement.

## What it does
- Collects official admissions signals and parent-reported waiting list positions
- Verifies submissions using confidence scoring and anomaly checks
- Publishes a simple timeline dashboard showing movement trends

## MVP scope (48 hours)
1. Admin paste tool for updates
2. Extractor agent to structure pasted text into records
3. Timeline dashboard that plots waiting list movement over time

## Architecture (high level)
- Frontend: Next.js dashboard
- Backend: Supabase (Postgres, Auth, Storage)
- Agents: Python (Extractor, Verifier, Publisher)
- Hosting: Vercel or Supabase hosting

## Repo structure
/frontend
/agents
/database
/docs
