# KIT CampusAI - Project Requirements & Architecture

**Project Name:** KIT CampusAI  
**Version:** 1.0.0  
**Date:** November 14, 2025

---

## TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Authentication & Authorization](#authentication--authorization)
4. [Phase 1 Features](#phase-1-features)
5. [Phase 2 Features](#phase-2-features)
6. [Technology Stack](#technology-stack)
7. [Database Schema](#database-schema)
8. [API Specifications](#api-specifications)
9. [Guardrail Rules](#guardrail-rules)
10. [Deployment Strategy](#deployment-strategy)

---

## PROJECT OVERVIEW

KIT CampusAI is a comprehensive mobile and web platform designed for engineering college students and teachers. It provides:

- **Knowledge Base RAG Chatbot** - AI-powered Q&A system backed by college curriculum and documents
- **Admin Portal** - Document management, KB administration, and system monitoring
- **Real-time Chat** (Phase 2) - Teacher-student communication with AI guardrails
- **User Management** - Role-based access control (Student, Teacher, HOD, Admin)
- **Tamper-Proof Logging** - Append-only violation tracking for compliance and safety

### Key Design Principles
- **Privacy First** - No PII sharing, strict guardrails on AI responses
- **Scalability** - Local PostgreSQL → Supabase migration path
- **Free-Tier Friendly** - Render.com, Supabase free tier, Firebase
- **Mobile-First** - Flutter for iOS/Android with identical web experience

---

## SYSTEM ARCHITECTURE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Mobile App (iOS/Android)    │    Web Admin (Flutter Web)       │
│  - Flutter Mobile            │    - Flutter Web                 │
│  - Google Sign-In            │    - Firebase Auth               │
│  - Chat UI                   │    - KB Management               │
│  - Profile Management        │    - Document Upload             │
│  - Chat History              │    - Logging & Monitoring        │
└─────────────────────────────────────────────────────────────────┘
                                  ↓ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY / BACKEND                       │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Server                                                  │
│  - Authentication (Google OAuth + JWT)                          │
│  - Rate Limiting & Security Middleware                          │
│  - CORS Configuration                                            │
│  - Request/Response Logging                                     │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  Auth Service    │  │   KB Service     │  │ Chat Service │  │
│  │  - Google Token  │  │  - Document Mgmt │  │ - Guardrails │  │
│  │  - JWT Token     │  │  - Embeddings    │  │ - RAG Query  │  │
│  │  - User Mgmt     │  │  - Vector Search │  │ - Logging    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  Admin Service   │  │ Violation Service │                   │
│  │  - User CRUD     │  │ - Append-Only Log │                   │
│  │  - Role Mgmt     │  │ - Audit Trail     │                   │
│  │  - Stats         │  │ - Alert System    │                   │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL INTEGRATIONS                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Google OAuth │  │  Gemini API  │  │  PostgreSQL / pgvector│ │
│  │ - Token Auth │  │  - Embeddings│  │  - Vector DB         │  │
│  │ - User Info  │  │  - LLM Chat  │  │  - RAG Index         │  │
│  │              │  │  - Guardrail │  │  - User Management   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow - RAG Chatbot

```
User Query
    ↓
[Input Safety Check] ← Guardrail Rules
    ↓
[Vector Similarity Search] ← Embeddings Index
    ↓
[Retrieved Documents] → [Gemini LLM]
    ↓
[Generated Response]
    ↓
[Output Safety Check] ← Guardrail Rules
    ↓
[Chat History Log] → PostgreSQL
    ↓
Response to User
```

---

## AUTHENTICATION & AUTHORIZATION

### Google OAuth Flow

#### Mobile (Android/iOS)
1. User taps "Sign in with Google"
2. `google_sign_in` plugin opens Google sign-in dialog
3. Google returns ID token to app
4. App sends ID token to backend `/auth/google`
5. Backend verifies token with Google, creates/updates user
6. Backend issues JWT token
7. App stores JWT in secure storage (Keychain/Keystore)
8. All subsequent requests use JWT in `Authorization` header

#### Web (Flutter Web)
1. User taps "Sign in with Google"
2. Firebase Auth handles OAuth dialog
3. Firebase returns ID token to app
4. App sends ID token to backend `/auth/google`
5. Backend verifies and issues JWT
6. App stores JWT in secure storage
7. Same JWT flow as mobile

### JWT Token Structure

```json
{
  "sub": "user_id_from_db",
  "email": "user@example.com",
  "role": "student|teacher|hod|admin",
  "google_uid": "google_oauth_id",
  "iat": 1234567890,
  "exp": 1234671490
}
```

### Role-Based Access Control (RBAC)

| Role  | Knowledge Base | Chat | Admin Panel | Violation Logs |
|-------|----------------|------|-------------|----------------|
| Student | Read | Full Access | None | Own messages |
| Teacher | Read | Full Access | View only | Department only |
| HOD | Read/Write | Full Access | Full | Department |
| Admin | Read/Write | Full Access | Full | All |

---

## PHASE 1 FEATURES

### Knowledge Base RAG Chatbot with AI Tools

#### Features
- **Document Upload** - Admin can upload PDF, DOCX, TXT files
- **Automatic Embedding** - Uses Gemini API to create embeddings
- **Vector Search** - pgvector for semantic similarity search
- **RAG Response** - Combines retrieved docs with LLM generation
- **Chat History** - Stores all conversations
- **Audit Trail** - Logs all queries and responses
- **AI Tools** - Chatbot can select and invoke tools to answer questions
- **Web Scraping** - Automatic scraping of knowledge base sources (e.g., KIT website)
- **Tool Selection** - Gemini function calling to choose appropriate tools

#### AI Tools Framework

##### Tool Types
1. **Knowledge Base (KB Search)** - Search uploaded documents and knowledge base
2. **Web Scraper** - Scrape external websites (e.g., https://kitcbe.com/)
3. **Document Search** - Search specific document collections
4. **Calculator** - Perform numerical computations (future)
5. **Code Executor** - Execute code snippets safely (future)

##### Available Tools in Phase 1

**1. KIT Campus Website Tool**
- Type: Web Scraper
- URL: https://kitcbe.com/
- Function: Scrapes and indexes KIT website content (admissions, academics, campus info)
- Update Frequency: Weekly
- Data Stored: Pages, content, metadata, embeddings
- Usage: Chatbot automatically searches and includes KIT website info in answers

**2. Uploaded Documents KB**
- Type: Knowledge Base Search
- Function: Searches all uploaded documents via vector similarity
- Data: All user-uploaded PDFs, DOCX, TXT files
- Usage: Primary source for course materials and college documents

**3. System Documents Search**
- Type: Document Search
- Function: Specialized search over system documents by department/category
- Filters: Department, category, publication date
- Usage: Find specific documents or policies

##### Tool Invocation Flow

```
User Query
    ↓
[Input Safety Check] ← Guardrails
    ↓
[Determine Required Tools] ← Gemini Function Calling
    ↓
For each selected tool:
  ├─ [Invoke Tool] (KB Search, Web Search, etc.)
  ├─ [Get Results] with vector embeddings
  └─ [Track Tool Call] in database
    ↓
[Combine Retrieved Data from All Tools]
    ↓
[Generate Contextual Response] ← Gemini LLM
    ↓
[Output Safety Check] ← Guardrails
    ↓
[Log Tool Calls & Message] → PostgreSQL
    ↓
Response to User (with sources)
```

##### Gemini Function Calling Schema

Each tool is registered with Gemini as a callable function:

```json
{
  "name": "kit_campus_website",
  "description": "Search KIT campus website for information about admissions, academics, campus facilities",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query"
      }
    },
    "required": ["query"]
  }
}
```

Gemini can automatically call these functions when processing queries that need specific tools.

##### Tool Data Management

**Data Model:**
```sql
ai_tools (
  id: UUID PRIMARY KEY,
  name: VARCHAR,
  description: TEXT,
  tool_type: ENUM (knowledge_base, web_scraper, document_search, calculator, code_executor),
  status: ENUM (active, inactive, deprecated),
  config: JSONB (tool-specific configuration),
  source_urls: JSONB (for web scrapers),
  function_definition: JSONB (Gemini function schema),
  usage_count: INTEGER,
  success_count: INTEGER,
  failure_count: INTEGER,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP,
  last_used_at: TIMESTAMP
)

tool_data (
  id: UUID PRIMARY KEY,
  tool_id: UUID FOREIGN KEY,
  source_url: VARCHAR,
  source_type: VARCHAR (web_page, document, extracted_text),
  title: VARCHAR,
  content: TEXT,
  embedding: Vector(768),
  metadata: JSONB,
  created_at: TIMESTAMP,
  updated_at: TIMESTAMP,
  scraped_at: TIMESTAMP
)

tool_calls (
  id: UUID PRIMARY KEY,
  message_id: UUID FOREIGN KEY,
  tool_id: UUID FOREIGN KEY,
  input_params: JSONB,
  output_data: JSONB,
  status: ENUM (pending, executing, success, failed),
  error_message: TEXT,
  execution_time_ms: INTEGER,
  created_at: TIMESTAMP,
  executed_at: TIMESTAMP,
  completed_at: TIMESTAMP
)
```

##### Web Scraping for KIT Website

**Process:**
1. Admin initializes KIT Campus Website tool
2. Tool is configured with URLs: kitcbe.com, kitcbe.com/academics, etc.
3. Admin triggers scrape operation (manual or scheduled)
4. Service fetches HTML from each URL
5. BeautifulSoup parses HTML and extracts text
6. Content is split and chunked
7. Each chunk is embedded using Gemini Embeddings API
8. Embeddings stored in pgvector with source metadata
9. Tool data indexed and searchable

**Scraping Configuration:**
```json
{
  "description": "Automatically scrapes and indexes KIT website content",
  "scrape_frequency": "weekly",
  "max_pages": 500,
  "follow_links": true,
  "allowed_domains": ["kitcbe.com"],
  "respect_robots_txt": true,
  "user_agent": "KIT-CampusAI/1.0"
}
```

#### Guardrail Rules (Phase 1)

**Input Guardrails:**
- Check for SQL injection attempts
- Check for prompt injection
- Detect jailbreak attempts
- Validate query length (max 2000 chars)

**Output Guardrails:**
- No PII (emails, phone numbers, addresses, SSN, ID numbers)
- No internal financial data (salaries, budgets, costs)
- No confidential staff information (personal details, schedules)
- Only use knowledge base + public website information
- If unable to answer: respond with "I don't have this information right now."

**Tool-Specific Guardrails:**
- Web scraper: Only scrape whitelisted domains
- KB Search: Only return results with similarity > 0.5
- Document Search: Respect document access permissions
- All tools: Log access and usage for audit

**Severity Levels:**
- LOW - Minor policy violation (e.g., query about non-KB topic)
- MEDIUM - Attempted PII extraction or sensitive data request
- HIGH - Prompt injection, jailbreak attempt, repeated violations

---

## PHASE 2 FEATURES

### Real-Time Teacher-Student Chat

#### Features
- **One-on-One Messaging** - Student can message their department teacher
- **AI Guardrails** - Every message checked for violations
- **Instant Notifications** - WebSocket-based real-time delivery
- **Violation Alerts** - Sent to Principal, HOD, Dean
- **Tamper-Proof Logging** - Append-only violation records
- **Admin Monitoring** - View all chats and violations

#### Tamper-Proof Violation Log

Structure:
```sql
violation_logs (
  id: UUID PRIMARY KEY,
  message_id: UUID (foreign key to messages),
  sender_id: UUID (foreign key to users),
  violation_rule: VARCHAR (name of broken rule),
  severity: ENUM (LOW, MEDIUM, HIGH),
  original_message: TEXT,
  violation_details: JSONB (what was detected),
  timestamp: TIMESTAMP (cannot be updated),
  created_at: TIMESTAMP (cannot be deleted or modified)
)
```

**Database Constraints:**
- `violation_logs` table cannot be deleted by any user
- Only INSERT permitted on `violation_logs`
- SELECT and VIEW only by admin/HoD/principal
- No UPDATE, DELETE, TRUNCATE allowed
- Implemented via PostgreSQL RLS (Row Level Security)

#### WebSocket Implementation
- Socket.IO (Python python-socketio)
- Namespace: `/chat`
- Events: `message_sent`, `message_received`, `violation_detected`, `user_typing`
- Rooms: `user_{user_id}`, `chat_{chat_session_id}`

---

## TECHNOLOGY STACK

### Backend
- **Framework:** FastAPI (Python 3.9+)
- **Database:** PostgreSQL 13+ with pgvector extension
- **Authentication:** Google OAuth 2.0, PyJWT
- **AI/ML:** Google Gemini API (embeddings + LLM)
- **Document Processing:** PyPDF2, python-docx, nltk
- **Vector DB:** pgvector (PostgreSQL extension)
- **Real-time:** python-socketio (Phase 2)
- **Async:** asyncpg, httpx
- **Validation:** Pydantic
- **Testing:** pytest, pytest-asyncio
- **Production:** Uvicorn

### Database
- **Primary:** PostgreSQL 13+
- **Extensions:** pgvector
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Future:** Supabase PostgreSQL

### Mobile (Flutter)
- **Framework:** Flutter 3.10+
- **Language:** Dart
- **State Management:** Riverpod
- **Auth:** google_sign_in, flutter_secure_storage
- **HTTP:** dio, http
- **Local Storage:** hive, shared_preferences
- **UI:** flutter_chat_ui, intl, cached_network_image
- **Testing:** flutter_test, mockito

### Web (Flutter Web)
- **Framework:** Flutter 3.10+ for Web
- **Auth:** firebase_auth + google_sign_in_web
- **Features:** Same as mobile + admin features
- **Hosting:** Firebase Hosting or GitHub Pages

### Deployment
- **Backend:** Render.com (free tier)
- **Database:** Local PostgreSQL (dev) → Supabase (prod)
- **Storage:** Local filesystem (dev) → Supabase Storage (prod)
- **AI Services:** Google Cloud (Gemini API, free tier)
- **Auth:** Firebase (free tier)

---

## DATABASE SCHEMA

### ERD Overview

```
users
├── knowledge_base
│   └── documents
│       └── knowledge_chunks
│           └── embeddings
├── chat_sessions
│   └── messages
│       └── violation_logs
└── roles
```

### Tables

See `migrations/001_initial_schema.sql` for complete schema with constraints and indexes.

**Key Tables:**
- `users` - User accounts with roles
- `roles` - Role definitions (student, teacher, hod, admin)
- `documents` - Uploaded documents (PDF, DOCX, TXT)
- `knowledge_chunks` - Document chunks for embedding
- `embeddings` - Vector embeddings (pgvector)
- `chat_sessions` - Conversation groups
- `messages` - Individual messages
- `violation_logs` - Tamper-proof violation records (append-only)

---

## API SPECIFICATIONS

### Base URL
- Development: `http://localhost:8000`
- Production: `https://kit-campusai-backend.onrender.com`

### Authentication Endpoints

#### POST /api/v1/auth/google
**Verify Google token and issue JWT**

Request:
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ...",
  "user_data": {
    "email": "user@gmail.com",
    "name": "John Doe",
    "picture": "https://..."
  }
}
```

Response (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@gmail.com",
    "name": "John Doe",
    "role": "student",
    "department": "CSE",
    "picture": "https://..."
  }
}
```

#### POST /api/v1/auth/refresh
**Refresh JWT token**

Request:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Chat Endpoints

#### POST /api/v1/chat/query
**Submit a query to the RAG chatbot**

Request:
```json
{
  "query": "What is the curriculum for DSA?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Response (200):
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "response": "Based on the knowledge base, the DSA curriculum covers...",
  "sources": [
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440002",
      "chunk_index": 0,
      "content": "Digital Signal Analysis is a core course...",
      "similarity_score": 0.92
    }
  ],
  "timestamp": "2025-11-14T10:30:00Z",
  "guardrail_checks": {
    "input_safe": true,
    "output_safe": true,
    "violations": []
  }
}
```

#### GET /api/v1/chat/history/{conversation_id}
**Get chat history**

Response (200):
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "role": "user",
      "content": "What is DSA?",
      "timestamp": "2025-11-14T10:30:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "DSA is Digital Signal Analysis...",
      "timestamp": "2025-11-14T10:30:05Z"
    }
  ]
}
```

---

### Knowledge Base Admin Endpoints

#### POST /api/v1/admin/kb/upload-document
**Upload document for knowledge base**

Request: multipart/form-data
```
file: <PDF, DOCX, or TXT file>
title: "Operating Systems Lecture Notes"
description: "Chapter 1-3 of OS course"
department: "CSE"
```

Response (201):
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440003",
  "title": "Operating Systems Lecture Notes",
  "file_path": "documents/2025-11-14/os_lecture_notes.pdf",
  "chunks_count": 45,
  "embeddings_created": 45,
  "status": "processing",
  "created_at": "2025-11-14T10:30:00Z"
}
```

#### GET /api/v1/admin/kb/documents
**List all knowledge base documents**

Query params:
- `page`: 1
- `limit`: 20
- `department`: "CSE"
- `search`: "operating"

Response (200):
```json
{
  "total": 125,
  "page": 1,
  "limit": 20,
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "title": "Operating Systems Lecture Notes",
      "department": "CSE",
      "file_size": 2048000,
      "chunks_count": 45,
      "created_at": "2025-11-14T10:30:00Z",
      "last_embedded_at": "2025-11-14T10:32:00Z"
    }
  ]
}
```

#### PUT /api/v1/admin/kb/documents/{document_id}
**Update document metadata**

Request:
```json
{
  "title": "Operating Systems - Updated",
  "description": "Chapters 1-5 with examples"
}
```

Response (200): Updated document object

#### DELETE /api/v1/admin/kb/documents/{document_id}
**Delete document and associated chunks/embeddings**

Response (204): No content

#### POST /api/v1/admin/kb/rebuild-embeddings
**Rebuild all embeddings (useful after model updates)**

Request:
```json
{
  "document_ids": ["550e8400-e29b-41d4-a716-446655440003"]
}
```

Response (202):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440010",
  "status": "processing",
  "documents_count": 1,
  "started_at": "2025-11-14T10:30:00Z"
}
```

---

### Admin Management Endpoints

#### GET /api/v1/admin/users
**List all users**

Query params:
- `role`: "student"
- `department`: "CSE"
- `page`: 1
- `limit`: 20

Response (200):
```json
{
  "total": 250,
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@kit.edu.in",
      "name": "John Doe",
      "role": "student",
      "department": "CSE",
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

#### PUT /api/v1/admin/users/{user_id}/role
**Update user role**

Request:
```json
{
  "role": "teacher"
}
```

Response (200): Updated user object

#### GET /api/v1/admin/violations
**List violation logs (append-only)**

Query params:
- `severity`: "HIGH"
- `start_date`: "2025-11-01"
- `end_date": "2025-11-14"
- `page`: 1
- `limit`: 50

Response (200):
```json
{
  "total": 1250,
  "violations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "message_id": "550e8400-e29b-41d4-a716-446655440101",
      "sender_id": "550e8400-e29b-41d4-a716-446655440000",
      "sender_name": "John Doe",
      "violation_rule": "PII_SHARING",
      "severity": "HIGH",
      "original_message": "[REDACTED]",
      "violation_details": {
        "detected_pii": ["email@example.com"],
        "pii_type": "email"
      },
      "timestamp": "2025-11-14T10:30:00Z"
    }
  ]
}
```

#### GET /api/v1/admin/stats
**System statistics**

Response (200):
```json
{
  "users": {
    "total": 5000,
    "students": 4000,
    "teachers": 900,
    "hods": 50,
    "admins": 50
  },
  "knowledge_base": {
    "total_documents": 250,
    "total_chunks": 5000,
    "total_embeddings": 5000,
    "indexed_documents": 250
  },
  "chat": {
    "total_conversations": 15000,
    "total_messages": 125000,
    "avg_response_time_ms": 1250
  },
  "violations": {
    "total_violations": 150,
    "low_severity": 100,
    "medium_severity": 40,
    "high_severity": 10,
    "last_7_days": 25
  }
}
```

---

## GUARDRAIL RULES

### Input Guardrails

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| SQL_INJECTION | Detects SQL injection patterns | Block & log | HIGH |
| PROMPT_INJECTION | Detects prompt override attempts | Block & log | HIGH |
| JAILBREAK | Detects model jailbreak attempts | Block & log | HIGH |
| QUERY_LENGTH | Max query length exceeded | Truncate/Reject | LOW |
| RATE_LIMIT | User exceeds query limit | Throttle | MEDIUM |

### Output Guardrails

| Rule | Description | Pattern | Action |
|------|-------------|---------|--------|
| PII_SHARING | Detects PII in response | Email, phone, SSN, ID patterns | Remove & flag |
| FINANCIAL_DATA | Detects financial info | Salary, budget, cost keywords | Remove & flag |
| STAFF_INFO | Detects confidential staff data | Personal details, schedules | Remove & flag |
| KNOWLEDGE_BASE | Ensures answer uses KB only | Cross-reference retrieved docs | Flag if not grounded |

### Guardrail Implementation

```python
class GuardrailChecker:
    async def check_input(query: str) -> GuardrailResult
    async def check_output(response: str, sources: List) -> GuardrailResult
    
class GuardrailResult:
    is_safe: bool
    violations: List[Violation]
    original_text: str
    sanitized_text: str
    severity: str
```

---

## DEPLOYMENT STRATEGY

### Phase 1: Local Development
1. PostgreSQL 13+ with pgvector
2. FastAPI dev server on localhost:8000
3. Flutter app/web on localhost:3000
4. All APIs on localhost

### Phase 2: Staging
1. Render.com free tier for backend
2. Supabase PostgreSQL for database
3. Firebase for Flutter Web auth
4. GitHub Pages for Flutter Web admin

### Phase 3: Production
1. Render.com paid tier (scaling)
2. Supabase Pro tier
3. Firebase Pro
4. CDN for static assets
5. Monitoring: Sentry, New Relic

### Render.com Deployment

**Backend Setup:**
1. Connect GitHub repo to Render.com
2. Create new Web Service
3. Set environment variables
4. Deploy on push to main branch
5. Database migrations run automatically

**Environment Variables:**
```
DATABASE_URL=postgresql://user:pass@host:5432/kitcampusai
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
JWT_SECRET=your-secret-key
GEMINI_API_KEY=xxx
ENVIRONMENT=production
```

### Supabase Migration

**Step-by-step:**
1. Create Supabase project
2. Create PostgreSQL database
3. Enable pgvector extension
4. Run migration scripts
5. Update DATABASE_URL
6. Test all APIs
7. Configure RLS policies
8. Set up Storage buckets
9. Update document paths in code
10. Deploy to Render.com

---

## RUNNING LOCALLY

See `docs/LOCAL_SETUP.md` for complete step-by-step instructions.

**Quick Start:**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Flutter Mobile
cd flutter_mobile
flutter pub get
flutter run

# Flutter Web Admin
cd flutter_web_admin
flutter pub get
flutter run -d chrome
```

---

## REFERENCE DOCUMENTS

- Architecture Diagram: `docs/architecture.md`
- API Reference: `docs/API.md`
- Database Schema: `docs/DATABASE.md`
- Deployment Guide: `docs/DEPLOYMENT.md`
- Local Setup: `docs/LOCAL_SETUP.md`
- Security Policy: `docs/SECURITY.md`
