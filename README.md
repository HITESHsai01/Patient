# 🏥 SentinelOps-Patient

> **Target "Patient" Web Application monitored by SentinelOps-AI Doctor.**

SentinelOps-Patient is an independent, realistic Customer Dashboard web application designed to be monitored, diagnosed, and autonomously healed by **SentinelOps-AI**.

---

## 🎯 Architecture Overview

```
                      SENTINELOPS-AI
                         "DOCTOR"
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
         GitHub Repository          Deployed URL
         (Source Inspection)      (Health Probes)
               └────────────┬────────────┘
                            ▼
                   SENTINELOPS-PATIENT
                        "PATIENT"
                            │
                     Intentional Fault
                   (GET /api/user/999)
                            │
                    Unhandled Exception
                            │
                      logs/app.log
                            │
                   SentinelOps Doctor
                 Detect → Diagnose → Fix
                            │
                     Verify Recovery
```

This application is **completely independent**:
- No dependencies on SentinelOps-AI codebase.
- In-memory data store (no database, no cloud infrastructure, no external APIs).
- Independent FastAPI backend and vanilla JavaScript frontend.

---

## 🚀 Installation & Getting Started

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

Activate the environment:
- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Application
```bash
uvicorn app.main:app --reload --port 8001
```

Access the dashboard in your browser:
👉 **`http://localhost:8001/`**

---

## 📡 API Endpoints

| Method | Endpoint | Description | Expected Status |
|---|---|---|---|
| `GET` | `/` | Serves the customer dashboard UI | `200 OK` (HTML) |
| `GET` | `/api/health` | Liveness health check | `200 OK` (`{"status": "healthy", "service": "sentinelops-patient"}`) |
| `GET` | `/api/users` | Lists all customer profiles | `200 OK` (JSON Array) |
| `GET` | `/api/user/{user_id}` | Look up a single customer by ID | `200 OK` for valid IDs (1, 2, 3) |

---

## ⚡ Reproducing the Intentional Failure

The application contains **one deterministic bug** in `app/routes.py`:

```python
@router.get("/api/user/{user_id}")
def get_user_by_id(user_id: int):
    matching = [u for u in USERS if u["id"] == user_id]
    
    # SENTINELOPS_TEST_BUG
    return matching[0]
```

### How to Trigger:
1. **Via Browser UI**: Click the red button **"Simulate Fault (GET /api/user/999)"** on the dashboard.
2. **Via curl**:
   ```bash
   curl http://localhost:8001/api/user/999
   ```

### Observed Behavior:
- **Status Code**: `HTTP 500 Internal Server Error`
- **Error Payload**:
  ```json
  {
    "error": "Internal Server Error",
    "exception_type": "IndexError",
    "message": "list index out of range",
    "path": "/api/user/999"
  }
  ```
- **Server Status**: **The server remains alive.** The global exception handler traps the error so that subsequent requests and `GET /api/health` continue to return `HTTP 200`.

---

## 📝 Error Logs

Every unhandled error is written to:
📂 **`logs/app.log`**

Each entry is formatted as structured JSON for easy parsing by SentinelOps AI agents:

```json
{
  "timestamp": "2026-10-05T14:30:00.123456+00:00",
  "method": "GET",
  "path": "/api/user/999",
  "exception_type": "IndexError",
  "message": "list index out of range",
  "traceback": "Traceback (most recent call last):\n  File ... in get_user_by_id\n    return matching[0]\nIndexError: list index out of range"
}
```

---

## 🧪 Running Tests

Execute the automated test suite with pytest:

```bash
pytest
```
or with python standard unittest:
```bash
python -m unittest discover -s tests
```

---

## 🩹 Expected Healthy Behavior After Bug Fix

When SentinelOps heals the application, it will patch `app/routes.py`:

```python
@router.get("/api/user/{user_id}")
def get_user_by_id(user_id: int):
    matching = [u for u in USERS if u["id"] == user_id]
    if not matching:
        raise HTTPException(status_code=404, detail="Customer not found")
    return matching[0]
```

After this patch:
- `GET /api/user/999` returns `HTTP 404 Customer not found` instead of `HTTP 500 IndexError`.
- No unhandled exceptions are raised.
- `GET /api/health` continues to return `HTTP 200`.
