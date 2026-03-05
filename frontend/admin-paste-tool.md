# Admin Paste Tool

The Admin Paste Tool allows administrators to paste updates from school websites, emails or parent reports.

Example input:

Wallington High School for Girls waiting list moved to rank 108 on April 12.

The system will send the text to the Extractor Agent which converts it into structured data.

---

## Input Fields

School name

Raw update text

Date of update

Source type
- school website
- parent report
- forum

---

## Processing Flow

Admin pastes update

↓

Extractor Agent processes text

↓

Structured record created

↓

Saved in Supabase table `waiting_list_updates`

↓

Timeline dashboard updated
