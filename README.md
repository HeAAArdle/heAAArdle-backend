# HeAAArdle (backend)
This repository contains the backend API for the project, built with FastAPI.
The frontend is maintained in a separate repository and communicates with this backend via HTTP (REST).

---

## Tech Stack
- Python 3.1X
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- PostgreSQL
- SQLAlchemy + Alembic

---

## Project Structure
```
backend/
├── app/
│   ├── main.py               # App entry point
│   ├── api/
│   │   └── v1/               # API version 1
│   │       ├── api.py        # Central router
│   │       └── endpoints/    # Route handlers
│   ├── core/                 # Global configuration and shared utilities
│   │   └── config.py
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic models for request and response validation
│   ├── services/             # Business logic
│   ├── db/                   # Data
│   ├── utils/                # Utility functions used across the app
│   │   └── helpers/          # Helper modules
├── .env                      # Local environment variables
├── .env.example              # Example env file
├── requirements.txt          # Python package dependencies
├── .gitignore
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <backend-repo-url>
cd backend
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
```

Activate it:

* **Windows**

```bash
venv\Scripts\activate
```

* **macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```
ENV=development
```

You can refer to `.env.example` for required variables.

### 5. Run the Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

* **Base URL:** `http://127.0.0.1:8000`
* **API Docs (Swagger):** `http://127.0.0.1:8000/docs`
* **API Docs (ReDoc):** `http://127.0.0.1:8000/redoc`

## Health Check

A simple health endpoint is available:

```
GET /api/v1/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Frontend Integration

The frontend should use the following base URL:

```
http://localhost:8000/api/v1
```

Example request:

```
GET /health
```

The backend is **stateless** and communicates exclusively via JSON over HTTP.
