# Automated Reporting Platform

A production-ready FastAPI backend that automates the full reporting pipeline — from raw data ingestion to KPI extraction, PDF generation, scheduled delivery, and email distribution.

Built as a portfolio project demonstrating clean architecture, background job management, and professional API design.

---

## Features

### Phase 1 — Core Pipeline
- Upload CSV or Excel files via REST API
- Automatic KPI extraction (revenue, orders, customers, growth, top products)
- PDF report generation with structured KPI tables
- Download generated reports

### Phase 2 — Automation
- Schedule recurring report jobs (APScheduler)
- Email delivery of PDF reports via SMTP (Mailtrap / Gmail)
- Per-job email configuration with custom subject and recipient

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Data Processing | Pandas, OpenPyXL |
| PDF Generation | ReportLab |
| Scheduling | APScheduler |
| Email Delivery | SMTP (Mailtrap) |
| Settings | Pydantic Settings + python-dotenv |

---

## Project Structure

```
automated-reporting-platform/
├── app/
│   ├── main.py                  # App entry point, router registration
│   ├── api/
│   │   ├── routes.py            # Document upload endpoints
│   │   ├── data_routes.py       # CSV/Excel upload and report generation
│   │   ├── scheduler_routes.py  # Scheduled job management
│   │   └── email_routes.py      # Manual email delivery
│   ├── core/
│   │   └── config.py            # Environment-based configuration
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response schemas
│   └── services/
│       ├── data_processor.py    # Data cleaning and transformation
│       ├── file_extractor.py    # Text extraction from PDF/DOCX
│       ├── kpi_engine.py        # KPI calculation logic
│       ├── report_generator.py  # PDF report builder
│       ├── scheduler.py         # APScheduler job management
│       └── email_service.py     # SMTP email delivery
├── data/                        # Input datasets
├── reports/                     # Generated PDF reports
├── test/                        # Test scripts
├── .env.example                 # Environment variable template
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

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
EMAIL_SENDER=hello@demomailtrap.co
EMAIL_PASSWORD=your_mailtrap_api_token
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

### 5. Open the API docs

```
http://127.0.0.1:8000/docs
```

---

## API Overview

### Data & Reports
| Method | Endpoint | Description |
|---|---|---|
| POST | `/data/upload-data` | Upload CSV/Excel and generate PDF report |
| GET | `/data/download-report` | Download the generated PDF |

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

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |

---

## Environment Variables

| Variable | Description |
|---|---|
| `EMAIL_SENDER` | Sender email address (e.g. Mailtrap sandbox address) |
| `EMAIL_PASSWORD` | Mailtrap API token |

Never commit your `.env` file. Use `.env.example` as a reference template.

---

## License

MIT
