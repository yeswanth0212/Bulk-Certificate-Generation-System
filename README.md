# Bulk Certificate Generator API 📜

A robust, high-performance backend API built with **Python 3**, **FastAPI**, **SQLAlchemy**, and **Pillow** designed to handle bulk certificate generation for large events, courses, and workshops.

The system accepts recipient lists, validates inputs, asynchronously renders high-resolution customizable certificates (PDF & PNG) with embedded QR verification codes, tracks job progress, and provides endpoints to retrieve individual certificates or bulk ZIP archives.

---

## 🌟 Key Features

1. **Bulk Certificate Jobs (`POST /api/v1/jobs`)**: Submit a single API request with hundreds of recipients.
2. **Background Processing**: Jobs process asynchronously in the background so API responses remain non-blocking and lightning fast.
3. **Robust Error Handling & Fault Isolation**: An invalid recipient (e.g., malformed email or missing name) will fail gracefully for that specific recipient without aborting the rest of the job.
4. **Detailed Progress Tracking (`GET /api/v1/jobs/{job_id}`)**: Track real-time progress percentages, success/failure counts, and individual recipient statuses.
5. **Certificate Retrieval**:
   - Download individual certificates as PDF or PNG (`GET /api/v1/certificates/{id}/download`).
   - Download all successfully generated certificates in a job as a single `.zip` archive (`GET /api/v1/jobs/{job_id}/download-zip`).
6. **Public Certificate Verification (`GET /api/v1/certificates/{id}/verify`)**: Scan the embedded QR code on any certificate to instantly verify its authenticity against official records.
7. **Interactive Visual Dashboard**: Served directly at `http://localhost:8000/` featuring real-time progress bars, live job polling, and instant downloads.

---

## 🛠️ Technology Stack

- **Language**: Python 3.13
- **Web Framework**: FastAPI (Async, OpenAPI/Swagger docs, high performance)
- **Database**: SQLite (SQLAlchemy ORM) - configurable via `DATABASE_URL` for PostgreSQL/MySQL
- **Certificate Rendering Engine**: Pillow (PIL) + QR Code Generator + ReportLab
- **Testing**: Pytest & HTTPX TestClient

---

## 🚀 Setup & Installation Instructions

### Prerequisites
- Python 3.10+ installed on your machine.

### 1. Clone or Open Project Directory
```bash
cd intern
```

### 2. Create and Activate Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Running the Application

Start the Uvicorn development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- **Interactive UI Dashboard**: Open [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger UI)**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: Open [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests

Execute the automated test suite with Pytest:
```bash
pytest
```
Expected output:
```text
======================== 11 passed in 5.28s ========================
```

The test suite covers:
- Job creation and status tracking
- Input validation (empty recipient lists, invalid email formats, blank names)
- Image/PDF rendering output
- Fault isolation when individual certificates fail
- Download endpoints (individual PDF/PNG and bulk ZIP archives)
- Verification endpoint validation

---

## 📖 API Usage Guide & Examples

### 1. Submit a Bulk Certificate Job
**`POST /api/v1/jobs`**

#### Request Body (JSON):
```json
{
  "title": "Advanced Python & AI Engineering",
  "issuer": "DeepMind AI Institute",
  "issue_date": "October 7, 2026",
  "format": "pdf",
  "recipients": [
    {
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "custom_text": "Passed with High Distinction"
    },
    {
      "name": "Bob Smith",
      "email": "bob@example.com",
      "custom_text": "First Class Honors"
    }
  ]
}
```

#### cURL Example:
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Machine Learning Bootcamp",
       "issuer": "Global Tech Academy",
       "format": "pdf",
       "recipients": [
         {"name": "Alice Johnson", "email": "alice@example.com"},
         {"name": "Bob Smith", "email": "bob@example.com"}
       ]
     }'
```

#### Response (`202 Accepted`):
```json
{
  "id": "e6a2b890-7d1f-4b0d-9a0d-3e5f1b2c4a5d",
  "title": "Machine Learning Bootcamp",
  "issuer": "Global Tech Academy",
  "issue_date": "October 07, 2026",
  "status": "PENDING",
  "total_recipients": 2,
  "processed_count": 0,
  "success_count": 0,
  "failure_count": 0,
  "progress_percentage": 0.0,
  "created_at": "2026-10-07T20:50:00Z",
  "completed_at": null,
  "recipients": [ ... ],
  "zip_download_url": null
}
```

*Note: You can pass `?sync=true` in the query parameters during development/testing if you prefer synchronous execution.*

---

### 2. Check Job Progress & Status
**`GET /api/v1/jobs/{job_id}`**

#### cURL Example:
```bash
curl -X GET "http://localhost:8000/api/v1/jobs/e6a2b890-7d1f-4b0d-9a0d-3e5f1b2c4a5d"
```

#### Response (`200 OK`):
```json
{
  "id": "e6a2b890-7d1f-4b0d-9a0d-3e5f1b2c4a5d",
  "status": "COMPLETED",
  "total_recipients": 2,
  "processed_count": 2,
  "success_count": 2,
  "failure_count": 0,
  "progress_percentage": 100.0,
  "recipients": [
    {
      "id": "c1f2e3d4-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
      "recipient_name": "Alice Johnson",
      "recipient_email": "alice@example.com",
      "status": "SUCCESS",
      "download_url": "http://localhost:8000/api/v1/certificates/c1f2e3d4-5a6b-7c8d-9e0f-1a2b3c4d5e6f/download",
      "verify_url": "http://localhost:8000/api/v1/certificates/c1f2e3d4-5a6b-7c8d-9e0f-1a2b3c4d5e6f/verify"
    }
  ],
  "zip_download_url": "http://localhost:8000/api/v1/jobs/e6a2b890-7d1f-4b0d-9a0d-3e5f1b2c4a5d/download-zip"
}
```

---

### 3. Download Generated Certificate
**`GET /api/v1/certificates/{certificate_id}/download`**

Downloads the rendered certificate file (`.pdf` or `.png`).

---

### 4. Download All Job Certificates (ZIP)
**`GET /api/v1/jobs/{job_id}/download-zip`**

Downloads a `.zip` archive containing all successfully generated certificates for the specified job.

---

### 5. Verify Certificate Authenticity
**`GET /api/v1/certificates/{certificate_id}/verify`**

#### Response:
```json
{
  "valid": true,
  "certificate_id": "c1f2e3d4-5a6b-7c8d-9e0f-1a2b3c4d5e6f",
  "recipient_name": "Alice Johnson",
  "recipient_email": "alice@example.com",
  "title": "Machine Learning Bootcamp",
  "issuer": "Global Tech Academy",
  "issue_date": "October 07, 2026",
  "custom_text": "Passed with High Distinction",
  "verification_message": "OFFICIAL CERTIFICATE VERIFIED. Authenticity confirmed by issuing authority."
}
```

---

## 📐 Architecture & Design Decisions

### 1. Background Task Queue vs API Latency
Generating hundreds of high-resolution graphic certificates and converting them to PDFs takes CPU time. Performing this synchronously inside a single HTTP request handler would cause client HTTP timeouts.
- **Decision**: `POST /api/v1/jobs` validates payload schemas upfront, creates database records in `PENDING` state, returns a `202 Accepted` response with the `job_id`, and delegates certificate rendering to FastAPI `BackgroundTasks` (with dedicated thread-level DB sessions).
- **Job Status Transition State**: `PENDING` -> `PROCESSING` -> (`COMPLETED` | `PARTIAL_SUCCESS` | `FAILED`).

### 2. Fault Isolation & Recipient Failure Handling
- A bulk job should not fail completely if 1 out of 500 email addresses is invalid or if a specific rendering step encounters an error.
- **Decision**: In `job_service.py`, each recipient is processed inside an isolated `try...except` block. If rendering fails for recipient $N$, recipient $N$'s status is marked as `FAILED` with the exact `error_message` logged. The loop continues to process recipient $N+1$. The overall job status reflects `PARTIAL_SUCCESS` if some succeed and some fail.

### 3. Dynamic QR Verification & Certificate Security
- **Decision**: Every generated certificate features an embedded QR code at the bottom right. Scanning the QR code points directly to `/api/v1/certificates/{id}/verify`. This allows employers and institutions to verify that the certificate is genuine and was issued by the platform.

### 4. Database & ORM
- **Decision**: SQLAlchemy with SQLite was chosen for zero-dependency local execution. The models use clean UUID primary keys for certificate IDs and foreign keys to link jobs to recipients. The database engine configuration supports switching to PostgreSQL or MySQL simply by setting `DATABASE_URL`.

---

## 📂 Project Structure

```text
intern/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app initialization, middleware, routes
│   ├── config.py              # Application settings (Pydantic Settings)
│   ├── database.py            # SQLAlchemy engine & session maker
│   ├── models.py              # ORM models (CertificateJob, RecipientCertificate)
│   ├── schemas.py             # Pydantic schemas (JobCreate, RecipientInput, etc.)
│   ├── services/
│   │   ├── generator.py       # Pillow certificate layout & QR code renderer
│   │   ├── job_service.py     # Background job processing & error isolation logic
│   │   └── zip_service.py     # Packaging certificates into ZIP archives
│   ├── api/
│   │   └── v1/
│   │       ├── router.py      # Main v1 API router
│   │       ├── jobs.py        # Bulk job endpoints
│   │       ├── certificates.py # Download & verification endpoints
│   │       └── health.py      # Health check endpoint
│   └── static/
│       ├── index.html         # Interactive web UI dashboard
│       ├── css/style.css      # Dark mode glassmorphism UI styles
│       └── js/app.js          # Live polling & UI interactions
├── generated_certificates/    # Local storage for output PDFs and ZIP files
├── tests/
│   ├── conftest.py            # Pytest DB fixtures and TestClient setup
│   ├── test_jobs.py           # Job endpoints & ZIP archive tests
│   ├── test_validation.py     # Input schema validation tests
│   ├── test_generator.py      # Rendering engine & failure isolation tests
│   └── test_certificates.py   # Download & verification tests
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest runner configuration
└── README.md                  # System documentation
```
