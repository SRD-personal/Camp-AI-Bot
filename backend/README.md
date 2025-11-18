# KIT CampusAI Backend

FastAPI backend for KIT CampusAI knowledge base chatbot with AI guardrails.

## Features

- **Google OAuth Authentication** - Secure user authentication with JWT tokens
- **RAG Knowledge Base** - Semantic search using pgvector and Gemini embeddings
- **AI Guardrails** - Input/output safety checks with PII detection
- **Document Processing** - Support for PDF, DOCX, TXT files
- **Web Scraping** - Automated indexing of KIT website content
- **Tamper-Proof Logging** - Append-only violation logs for compliance
- **Admin Portal** - Document management and system monitoring

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 13+ with pgvector
- **AI/ML**: Google Gemini API
- **Authentication**: Google OAuth 2.0 + JWT
- **Python**: 3.9+

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+ with pgvector extension
- Google Cloud account (for Gemini API and OAuth)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Set up PostgreSQL with pgvector:
```sql
CREATE DATABASE kit_campusai;
\c kit_campusai;
CREATE EXTENSION vector;
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GEMINI_API_KEY` - Google Gemini API key
- `JWT_SECRET` - Secret key for JWT tokens

## API Endpoints

### Authentication
- `POST /api/v1/auth/google` - Authenticate with Google
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user

### Chat
- `POST /api/v1/chat/query` - Submit query to RAG chatbot
- `GET /api/v1/chat/history/{conversation_id}` - Get chat history
- `GET /api/v1/chat/sessions` - Get all chat sessions

### Admin
- `POST /api/v1/admin/kb/upload-document` - Upload document
- `GET /api/v1/admin/kb/documents` - List documents
- `DELETE /api/v1/admin/kb/documents/{id}` - Delete document
- `GET /api/v1/admin/violations` - List violations
- `GET /api/v1/admin/stats` - System statistics

## Development

### Running Tests
```bash
pytest tests/
```

### Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Deployment

### Render.com

1. Connect GitHub repository to Render.com
2. Create new Web Service
3. Set environment variables in Render dashboard
4. Deploy

### Docker

Build image:
```bash
docker build -t kit-campusai-backend .
```

Run container:
```bash
docker run -p 8000:8000 --env-file .env kit-campusai-backend
```

## License

MIT License
