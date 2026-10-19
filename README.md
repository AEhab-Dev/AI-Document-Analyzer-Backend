# AI Document Analyzer - Backend

FastAPI backend for the AI Document Analyzer app. Supports PDF upload, text extraction, and AI-powered chat using Groq.

## Tech Stack

- **FastAPI** — REST API framework
- **SQLModel / SQLAlchemy** — ORM + database
- **Groq** — AI inference
- **pdfplumber** — PDF text extraction
- **python-jose + passlib** — JWT auth

## Local Development

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Environment Variables

Create a `.env` file in the project root:

```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key-here
UPLOAD_DIR=./uploads
```

## Deployment

Deployed on Railway. Set the environment variables above in the Railway dashboard.
