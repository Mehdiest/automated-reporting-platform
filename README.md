# Automated Reporting Platform

A production-ready FastAPI backend that automates the full reporting pipeline — from raw data ingestion to KPI extraction, PDF generation, scheduled delivery, email distribution, and multi-dataset consolidation.

Built as a portfolio project demonstrating clean architecture, background job management, and professional API design.

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
│   ├── main.py                       # App entry point, router registration
│   ├── api/
│   │   ├── routes.py                 # Document upload endpoints
│   │   ├── data_routes.py            # CSV/Excel upload and report generation
│   │   ├── scheduler_routes.py       # Scheduled job management
│   │   ├── email_routes.py           # Manual email delivery
│   │   └── multi_dataset_routes.py   # Multi-file upload and combined report
│   ├── core/
│   │   └── config.py                 # Environment-based configuration
│   ├── models/
│   │   └── schemas.py                # Pydantic request/response schemas
│   └── services/
│       ├── data_processor.py         # Data cleaning and transformation
│       ├── file_extractor.py         # Text extraction from PDF/DOCX
│       ├── kpi_engine.py             # KPI calculation logic
│       ├── report_generator.py       # Single-dataset PDF report builder
│       ├── multi_dataset_processor.py# Multi-file ingestion and KPI merging
│       ├── multi_report_generator.py # Multi-section PDF report builder
│       ├── scheduler.py              # APScheduler job management
│       └── email_service.py          # SMTP email delivery
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

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |

---

## Example: Schedule a Job with Email Delivery

```json
POST /scheduler/jobs
{
  "job_id": "daily_sales",
  "dataset_path": "data/sales.csv",
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

Never commit your `.env` file. Use `.env.example` as a reference template.

---

## Roadmap

- [x] Phase 1 — Core pipeline (upload, KPI, PDF, download)
- [x] Phase 2 — Automation (scheduling, email, multi-dataset)
- [ ] Phase 3 — Dashboard integration, multi-user system
- [ ] Phase 4 — AI insights, SaaS structure

---

## License

MIT
