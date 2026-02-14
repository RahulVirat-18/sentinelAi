# Sentinel AI (Project Overview) ✅

> Concise, interview-ready summary of the repository: core components, flows, endpoints, data model, runtime/setup, and system architecture.

---

## 1) Project Summary 💡
- **What it is:** A Flask-based web application for managing investigation **Cases** and **Evidence**, performing AI-based video forensic analysis (using Google Gemini), storing analysis outputs in MySQL and a vector store (ChromaDB), and providing a RAG-style chat interface per case.
- **Primary features observed in code:**
  - User **authentication** (register, login, 2FA, forgot/reset password)
  - **Case** management (create/delete)
  - **Evidence** upload (video files: mp4/avi/mov/mkv), timestamped filenames
  - **AI analysis** pipeline using `google.generativeai` (upload → process → generate report)
  - **Memory** storage with ChromaDB (embeddings via Gemini) for RAG chat
  - **Email** support via SMTP (`app.email_service`) for OTPs and alerts
  - Helper scripts: `verify_flow.py`, `debug_db.py`, `view_memory.py`

---

## 2) Tech Stack / Dependencies 🔧
- Framework: **Flask**
- DB: **MySQL** (accessed via `mysql.connector`) — DB connection handled in `app/db_connector.py`
- AI: **Google Gemini** via `google.generativeai` (video upload + generative model + embeddings)
- Vector DB: **ChromaDB** (persistent client using `chroma_db/` folder)
- Auth: **bcrypt** for password hashing
- Env config: **python-dotenv** (.env usage in code)
- Mail: standard **smtplib** (wrapped in `app/email_service.py`)
- Utilities: `werkzeug.utils.secure_filename` for safe uploads

> Note: `requirements.txt` is empty; packages are inferred from source imports.

---

## 3) Important Environment Variables (.env) 🧾
Use a `.env` file or environment variables; these are referenced in code:

```
SECRET_KEY (optional)  # fallback is 'dev_key' in code
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
GEMINI_API_KEY
MAIL_SERVER
MAIL_PORT
MAIL_USERNAME
MAIL_PASSWORD
```

---

## 4) Database Models (inferred from queries) 🗄️
- `users` (used columns): `id`, `full_name`, `email`, `password_hash`, `is_2fa_enabled`, `otp_code`, `otp_expiry`, `setting_login_alerts`, `setting_theme`
- `cases` (used columns): `id`, `user_id`, `case_unique_id`, `case_name`, `description`, `created_at`
- `evidence` (used columns): `id`, `case_id`, `title`, `file_path`, `analysis_report`, `uploaded_at`

> These columns appear across `auth`, `dashboard`, `case_manager`, and debug scripts.

---

## 5) Key Endpoints & Routes 📍
- `GET  /` — Landing page (redirects to dashboard if logged in)
- `GET/POST  /login`, `GET/POST /register`, `GET/POST /forgot-password`, `GET/POST /reset-password`, `GET/POST /verify-2fa` — Auth flows
- `GET /dashboard` — User dashboard (list of cases)
- `POST /create_case` — Create a case
- `GET /delete_case/<case_id>` — Delete a case
- `GET /case/<case_id>/overview` — Case overview
- `GET/POST /case/<case_id>/evidence` — Evidence upload and listing
- `POST /analyze/<evidence_id>` — Trigger AI analysis for an evidence item (core flow)
- `POST /case/<case_id>/chat` — RAG-based chat using ChromaDB + Gemini
- `POST /case/<case_id>/email_report` — Trigger (mocked) email of a report
- `GET /features`, `GET /privacy` — Static pages

---

## 6) Core Flows (step-by-step) 🔁
1. Upload evidence
   - File saved to `static/uploads/` with timestamp prefix
   - Record inserted into `evidence` table (path saved)
2. Analyze evidence (`/analyze/<evidence_id>`)
   - Loads file path → calls `analyze_video(full_path)` in `app/ai_engine.py`
   - `analyze_video` uploads file to Gemini, waits processing, asks `gemini-2.5-flash` for a forensic report
   - The returned text is saved to `analysis_report` in `evidence` table (committed)
   - Report text also stored via `memory_engine.save_memory` into ChromaDB after embedding with Gemini
3. Chat / RAG (`/case/<case_id>/chat`)
   - Query facts with `memory_engine.query_memory` → get related documents
   - Build contextual system prompt and call Gemini for response
   - If user sends corrections, they’re saved as a new memory fact
4. Auth flows
   - Passwords hashed via bcrypt; 2FA via numeric OTP saved in DB and emailed (valid for 10 minutes)

---

## 7) Utilities & Debug Scripts 🧰
- `verify_flow.py` — Verifies evidence & report visibility and file-naming
- `debug_db.py` — Inspect evidence table schema & recent reports
- `view_memory.py` — View ChromaDB collections and stored facts

---

## 8) Security Notes & Observations ⚠️
- **Positive:** Passwords hashed with bcrypt; secure filename handling for uploads; SMTP uses TLS (`starttls()`)
- **Points to improve (observed in code):**
  - Default `SECRET_KEY` fallback = `'dev_key'` (should be set in prod)
  - No explicit file size/virus scanning limits on uploads
  - No rate-limiting or brute-force protections implemented
  - No explicit HTTPS enforcement in code (depends on deployment)

---

## 9) How to Run Locally (observed) ▶️
- Activate virtual env (example on Windows PowerShell):
  - `env\Scripts\Activate.ps1`
- Ensure required env vars are set
- Run the app:
  - `python run.py`  (this executes `app.create_app()` and runs Flask dev server)
- Helpful scripts:
  - `python verify_flow.py` — checks DB/report integrity
  - `python debug_db.py` — inspect evidence table
  - `python view_memory.py` — list memory collections

---

## 10) System Architecture (ASCII + Explanation) 🏗️

```
[ User Browser ]
      |
      | HTTPS
      v
[ Flask App (run.py -> create_app) ] -- static/uploads (files)
   |  \__ routes: /login, /dashboard, /case, /analyze, /chat
   |
   |---> [ MySQL ]  (users, cases, evidence)
   |
   |---> [ Google Gemini API ] (video upload, model generate_content, embeddings)
   |
   |---> [ ChromaDB (chroma_db/) ] (persistent embeddings & documents)
   |
   `---> [ SMTP Mail Server ] (OTP, alerts)
```

- Explanation: Flask accepts uploads and triggers AI analysis; analysis text is saved in MySQL and indexed into ChromaDB (embedding via Gemini). RAG chat uses ChromaDB to retrieve context and calls Gemini to generate answers.

---

## 11) Interview Prep — Likely Questions & Short Answers 🎯
(Use these exact points; all are directly referenced in code)

1. Q: How is AI analysis implemented?
   - A: `app/ai_engine.py` uses `google.generativeai` to upload video, polls for processing, then calls `gemini-2.5-flash` with a forensic prompt and returns a text report.

2. Q: How are analysis results stored and retrieved?
   - A: Saved into `evidence.analysis_report` (MySQL) and also saved into ChromaDB via `memory_engine.save_memory` for RAG retrieval.

3. Q: How does 2FA work?
   - A: OTP is generated, stored with expiry in `users` table, emailed via SMTP, and verified on `verify-2fa` route.

4. Q: How is RAG set up?
   - A: `query_memory` gets documents from a case collection in ChromaDB using Gemini embeddings, the context is prepended to the prompt for Gemini generation.

5. Q: Where are files stored?
   - A: File system under `app/static/uploads/` with unique timestamped filenames.

6. Q: What are obvious improvement areas you might mention in an interview?
   - A: Add file size checks, content validation, proper secret management, rate-limiting, and production-grade deployment (HTTPS, WSGI server, environment variable management).

---

## 12) Quick References / Files to Read 📚
- App entry & wiring: `run.py`, `app/__init__.py`
- Auth flows: `app/auth.py`
- Case/Evidence flows & AI: `app/case_manager.py`, `app/ai_engine.py`, `app/memory_engine.py`
- DB connection: `app/db_connector.py`
- Email: `app/email_service.py`
- Utilities: `verify_flow.py`, `debug_db.py`, `view_memory.py`

---

If you want, I can also:
- Generate a concise one-page cheat-sheet for interview answers based on these files (direct quotes from code), or
- Add/update a minimal `requirements.txt` inferred from imports.

---

*File created: `PROJECT_OVERVIEW.md` — review and tell me if you'd like it shortened further for a one-page cheat-sheet.* ✨
