# Automated Reporting Platform

A production-ready FastAPI backend that automates the full reporting pipeline — from raw data ingestion to KPI extraction, PDF generation, scheduled delivery, email distribution, multi-dataset consolidation, multi-user authentication, a live reporting dashboard, AI-powered insights, and a multi-tenant SaaS subscription layer.

Built as a portfolio project demonstrating clean architecture, background job management, secure JWT authentication, multi-tenancy with usage quotas, and professional API design.

---

## Features

### Phase 1 — Core Pipeline
- Upload CSV or Excel files via REST API
- Automatic KPI extraction (revenue, orders, customers, growth, top products)
- PDF report generation with structured KPI tables
- Download generated reports

### Phase 2 — Automation
- Schedule recurring report jobs at custom intervals (APScheduler)
- Email delivery of PDF reports via SMTP (Mailtrap)
- Per-job email configuration with custom recipient and subject
- Upload multiple datasets simultaneously and generate a single consolidated report
- Per-dataset KPI breakdown plus merged aggregate summary

### Phase 3 — Multi-User System & Dashboard
- **User accounts** backed by SQLite + SQLAlchemy (`users` table auto-created on startup)
- **Secure registration** with bcrypt password hashing — plaintext passwords are never stored
- **JWT authentication** — login issues a signed Bearer token (HS256) with configurable expiry
- **Protected endpoints** via a reusable `get_current_user` dependency (`/auth/me`)
- **Reporting dashboard** — an HTML page plus JSON endpoints that aggregate KPI stats and catalogue every generated report on disk

### Phase 4 — AI Insights & SaaS Structure
- **AI insights** — generate natural-language business insights from a dataset's KPIs
  - Uses an OpenAI chat model when `OPENAI_API_KEY` is set
  - Falls back to a built-in, deterministic rule-based generator when no key is configured (so the feature always works and is testable offline)
- **Multi-tenant SaaS layer** — Organizations (tenants) on subscription plans (`Free`, `Pro`, `Enterprise`)
- **Subscription plans** with feature flags and monthly limits (reports, datasets-per-report, AI insights)
- **Usage metering & quota enforcement** — every billable action is logged and checked against the plan's monthly quota
- **Plan management endpoints** — create an organization, view plan & usage, and upgrade plans (owner-only)

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Data Processing | Pandas, OpenPyXL |
| PDF Generation | ReportLab |
| Scheduling | APScheduler |
| Email Delivery | SMTP (Mailtrap) |
| Database / ORM | SQLite + SQLAlchemy |
| Authentication | JWT (python-jose) + bcrypt (passlib) |
| AI Insights | OpenAI (optional) + rule-based fallback |
| Settings | Pydantic Settings + python-dotenv |

---

## Project Structure

```
automated-reporting-platform/
├── app/
│   ├── main.py                       # App entry point, router registration, lifespan
│   ├── api/
│   │   ├── routes.py                 # Document upload endpoints
│   │   ├── data_routes.py            # CSV/Excel upload and KPI extraction
│   │   ├── scheduler_routes.py       # Scheduled job management
│   │   ├── email_routes.py           # Manual email delivery
│   │   ├── multi_dataset_routes.py   # Multi-file upload and combined report
│   │   ├── auth_routes.py            # Register / login / me
│   │   ├── dashboard_routes.py       # Dashboard page + stats + report catalogue
│   │   ├── saas_routes.py            # Organizations, plans, usage, upgrades (Phase 4)
│   │   └── insights_routes.py        # AI insights generation (Phase 4)
│   ├── core/
│   │   ├── config.py                 # Environment-based configuration
│   │   ├── database.py               # SQLite + SQLAlchemy engine, session, init_db
│   │   └── dependencies.py           # JWT auth dependency (get_current_user)
│   ├── models/
│   │   ├── schemas.py                # Pydantic request/response schemas
│   │   ├── user.py                   # SQLAlchemy User ORM model (+ organization link)
│   │   └── organization.py           # Organization & UsageRecord models (Phase 4)
│   ├── services/
│   │   ├── data_processor.py         # Data cleaning and transformation
│   │   ├── file_extractor.py         # Text extraction from PDF/DOCX
│   │   ├── kpi_engine.py             # KPI calculation logic
│   │   ├── report_generator.py       # Single-dataset PDF report builder
│   │   ├── multi_dataset_processor.py# Multi-file ingestion and KPI merging
│   │   ├── multi_report_generator.py # Multi-section PDF report builder
│   │   ├── scheduler.py              # APScheduler job management
│   │   ├── email_service.py          # SMTP email delivery
│   │   ├── auth_service.py           # Password hashing + JWT generation/validation
│   │   ├── subscription_service.py   # SaaS plans + monthly quota enforcement (Phase 4)
│   │   └── ai_insights.py            # AI / rule-based insight generation (Phase 4)
│   └── static/
│       └── dashboard.html            # Reporting dashboard frontend
├── data/                             # Input datasets
├── reports/                          # Generated PDF reports
├── test/                             # Test scripts
├── .env.example                      # Environment variable template
├── .gitignore
└── requirements.txt
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Mehdiest/automated-reporting-platform.git
cd automated-reporting-platform
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `bcrypt` is pinned to `<4.1` because `passlib 1.7.4` is incompatible with newer bcrypt releases (registration would fail with a 500 error). Keep this pin in place.

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
# Email delivery via Mailtrap SMTP
EMAIL_SENDER=hello@demomailtrap.co
EMAIL_PASSWORD=your_mailtrap_api_token

# JWT Authentication
JWT_SECRET_KEY=change-this-to-a-long-random-secret
JWT_EXPIRE_MINUTES=60
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

On startup the app loads `.env`, creates the SQLite database (`reporting_platform.db`) with the `users`, `organizations`, and `usage_records` tables, and starts the background scheduler.

> **Upgrading from Phase 3?** The `users` table gained `organization_id` and `role` columns in Phase 4. SQLite's auto-create does not alter existing tables, so delete the old database once before the first run: `rm reporting_platform.db` (PowerShell: `Remove-Item reporting_platform.db`). You will need to register your user again.

### 5. Open the API docs

```
http://127.0.0.1:8000/docs
```

---

## API Overview

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a new user account |
| POST | `/auth/login` | Authenticate and receive a JWT Bearer token |
| GET | `/auth/me` | Return the current authenticated user (requires Bearer token) |

### Data & Reports
| Method | Endpoint | Description |
|---|---|---|
| POST | `/data/upload-data` | Upload CSV/Excel and extract KPIs |
| POST | `/docs/upload-document` | Upload a PDF/DOCX/TXT and extract text |

### Multi-Dataset
| Method | Endpoint | Description |
|---|---|---|
| POST | `/multi/upload-and-report` | Upload multiple files and generate a combined PDF |
| GET | `/multi/download-report` | Download the combined PDF report |

### Scheduler
| Method | Endpoint | Description |
|---|---|---|
| POST | `/scheduler/jobs` | Register a recurring report job |
| GET | `/scheduler/jobs` | List all active jobs |
| DELETE | `/scheduler/jobs/{job_id}` | Remove a job |

### Email
| Method | Endpoint | Description |
|---|---|---|
| POST | `/email/send-report` | Send a PDF report via email |

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/` | Serve the reporting dashboard HTML page |
| GET | `/dashboard/stats` | Aggregated KPI / report statistics |
| GET | `/dashboard/reports` | Catalogue of all generated PDF reports on disk |

### SaaS / Organizations (auth required)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/saas/plans` | List available subscription plans |
| POST | `/saas/organizations` | Create an organization (caller becomes owner) |
| GET | `/saas/organizations/me` | Current organization, plan, and usage |
| POST | `/saas/organizations/upgrade` | Change the organization's plan (owner only) |

### AI Insights (auth required)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/insights/generate` | Upload a CSV/Excel file → KPIs + natural-language insights |

**Subscription plans**

| Plan | Reports / month | Datasets / report | AI insights / month |
|---|---|---|---|
| Free | 5 | 2 | — (not included) |
| Pro | 100 | 10 | 50 |
| Enterprise | unlimited | unlimited | unlimited |

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |

---

## Example: Register, Log In, and Access a Protected Endpoint

```bash
# 1. Register
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "mehdi", "email": "mehdi@example.com", "password": "securepassword"}'

# 2. Log in → returns { "access_token": "...", "token_type": "bearer" }
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "mehdi", "password": "securepassword"}'

# 3. Call a protected endpoint with the token
curl -X GET "http://127.0.0.1:8000/auth/me" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Example: Create an Organization and Generate AI Insights

```bash
# (after logging in and obtaining <ACCESS_TOKEN>)

# 1. Create an organization on the Pro plan (includes AI insights)
curl -X POST "http://127.0.0.1:8000/saas/organizations" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Analytics", "plan": "pro"}'

# 2. Generate AI insights from a dataset
curl -X POST "http://127.0.0.1:8000/insights/generate" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@data/sample.csv"

# 3. Check plan + usage
curl -X GET "http://127.0.0.1:8000/saas/organizations/me" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Example: Schedule a Job with Email Delivery

```json
POST /scheduler/jobs
{
  "job_id": "daily_sales",
  "dataset_path": "data/sample.csv",
  "interval_minutes": 60,
  "output_dir": "reports",
  "email_recipient": "client@example.com",
  "email_subject": "Daily Sales Report"
}
```

## Example: Combined Report from Multiple Datasets

```bash
curl -X POST "http://127.0.0.1:8000/multi/upload-and-report" \
  -F "files=@data/sales.csv" \
  -F "files=@data/inventory.csv"
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `EMAIL_SENDER` | Sender email address (Mailtrap sandbox address) |
| `EMAIL_PASSWORD` | Mailtrap API token |
| `JWT_SECRET_KEY` | Secret used to sign JWT tokens (use a long random value in production) |
| `JWT_EXPIRE_MINUTES` | Access-token lifetime in minutes (default: 60) |
| `OPENAI_API_KEY` | *(Optional)* OpenAI key for AI insights. If empty, a rule-based fallback is used |
| `OPENAI_MODEL` | *(Optional)* OpenAI model for insights (default: `gpt-4o-mini`) |

Never commit your `.env` file. Use `.env.example` as a reference template.

---

## Roadmap

- [x] Phase 1 — Core pipeline (upload, KPI, PDF, download)
- [x] Phase 2 — Automation (scheduling, email, multi-dataset)
- [x] Phase 3 — Multi-user system (SQLite, JWT auth) & reporting dashboard
- [x] Phase 4 — AI insights & multi-tenant SaaS structure (plans + usage quotas)

---

## License

MIT
