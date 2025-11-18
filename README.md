# KIT CampusAI - AI-Powered Campus Assistant

<div align="center">

![KIT CampusAI](https://img.shields.io/badge/KIT-CampusAI-blue?style=for-the-badge)
![Phase 1](https://img.shields.io/badge/Phase-1-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-green?style=for-the-badge)

**AI-powered knowledge base chatbot with secure communication and compliance guardrails**

[Features](#features) • [Architecture](#architecture) • [Quick Start](#quick-start) • [Deployment](#deployment) • [Documentation](#documentation)

</div>

---

## 📋 Overview

KIT CampusAI is a comprehensive AI-powered platform designed for Kalaimagal Institute of Technology (KIT). It provides students and faculty with instant access to campus information through an intelligent chatbot backed by RAG (Retrieval-Augmented Generation) technology.

### Key Highlights

- ✅ **Phase 1**: Knowledge Base RAG Chatbot (Current)
- 🔄 **Phase 2**: Secure Teacher-Student Chat (Planned)
- 🛡️ **AI Guardrails**: PII protection, content filtering, violation detection
- 🔐 **Authentication**: Google OAuth + JWT tokens
- 📱 **Mobile-First**: Flutter Android app with identical web experience
- 🆓 **Free Hosting**: Render.com + Supabase compatible

---

## ✨ Features

### Phase 1 - Knowledge Base Chatbot

- **RAG-Powered Q&A**: Semantic search using pgvector and Google Gemini
- **Document Management**: Upload PDF, DOCX, TXT files to knowledge base
- **Web Scraping**: Automatic indexing of KIT website (https://kitcbe.com/)
- **AI Tools Framework**: Extensible tool system for Gemini function calling
- **Source Citations**: Every response includes source documents
- **Chat History**: Persistent conversation storage
- **Admin Portal**: Document upload, user management, system monitoring

### Security & Compliance

- **Input Guardrails**: SQL injection, prompt injection, jailbreak detection
- **Output Guardrails**: PII detection (email, phone, SSN, Aadhar), financial data filtering
- **Tamper-Proof Logging**: Append-only violation logs with audit trail
- **Role-Based Access**: Student, Teacher, HOD, Admin roles
- **Data Masking**: Automatic PII redaction in responses

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  Mobile App (Android)    │    Web Admin (Flutter Web)       │
│  - Flutter Mobile        │    - Firebase Auth               │
│  - Google Sign-In        │    - KB Management               │
│  - Chat UI               │    - Document Upload             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                           │
├─────────────────────────────────────────────────────────────┤
│  - Google OAuth + JWT                                        │
│  - RAG Service (Gemini)                                      │
│  - Guardrail Service                                         │
│  - Document Processing                                       │
│  - Web Scraper                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL + PGVECTOR                           │
├─────────────────────────────────────────────────────────────┤
│  - Users, Documents, Chat Sessions                           │
│  - Knowledge Chunks with Embeddings                          │
│  - AI Tools & Tool Data                                      │
│  - Violation Logs (Append-Only)                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                               │
├─────────────────────────────────────────────────────────────┤
│  Google OAuth  │  Gemini API  │  KIT Website Scraper        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.9+, PostgreSQL 13+ with pgvector
- **Mobile**: Flutter 3.0+, Android SDK
- **APIs**: Google Cloud account (Gemini API, OAuth)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Setup database
createdb kit_campusai
psql kit_campusai -c "CREATE EXTENSION vector;"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Backend runs at**: `http://localhost:8000`
**API docs**: `http://localhost:8000/docs`

### 2. Mobile App Setup

```bash
cd mobile/android_app

# Install dependencies
flutter pub get

# Configure Google Sign-In (see mobile/android_app/README.md)

# Run app
flutter run
```

### 3. Initial Data Setup

1. Sign in with Google
2. Upload documents via admin portal
3. Initialize KIT website scraper tool
4. Start chatting!

---

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 13+ with pgvector
- **AI/ML**: Google Gemini API
- **Authentication**: Google OAuth 2.0, JWT
- **Document Processing**: PyPDF2, python-docx
- **Web Scraping**: BeautifulSoup4, httpx

### Mobile
- **Framework**: Flutter 3.0+
- **State Management**: Riverpod
- **Authentication**: google_sign_in, firebase_auth
- **HTTP**: Dio
- **Storage**: flutter_secure_storage, Hive

### Deployment
- **Backend**: Render.com (free tier)
- **Database**: PostgreSQL / Supabase
- **Mobile**: APK / Google Play Store

---

## 🌐 Deployment

### Render.com (Recommended for POC)

1. **Connect Repository**:
   ```bash
   # Push to GitHub
   git push origin main
   ```

2. **Create Web Service** on Render.com:
   - Connect GitHub repo
   - Use `render.yaml` for configuration
   - Set environment variables

3. **Deploy**:
   - Render automatically deploys on push to main
   - Database migrations run automatically

### Environment Variables

Required environment variables (see `.env.example`):

```env
DATABASE_URL=postgresql://...
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GEMINI_API_KEY=xxx
JWT_SECRET=xxx
```

### Supabase Migration (For Production)

1. Create Supabase project
2. Enable pgvector extension
3. Run migration scripts
4. Update `DATABASE_URL`
5. Configure Row Level Security policies

---

## 📚 Documentation

### Project Files

```
Camp-AI-Bot/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   ├── tests/              # Unit tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Docker configuration
│
├── mobile/android_app/      # Flutter mobile app
│   ├── lib/
│   │   ├── models/         # Data models
│   │   ├── services/       # API & auth services
│   │   ├── screens/        # UI screens
│   │   └── main.dart       # App entry point
│   └── pubspec.yaml        # Flutter dependencies
│
├── docs/                    # Additional documentation
├── PROJECT_REQUIREMENTS.md  # Complete specification
└── README.md               # This file
```

### API Endpoints

#### Authentication
- `POST /api/v1/auth/google` - Google OAuth login
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `GET /api/v1/auth/me` - Get current user

#### Chat
- `POST /api/v1/chat/query` - Submit RAG query
- `GET /api/v1/chat/history/{id}` - Get conversation history
- `GET /api/v1/chat/sessions` - List all chat sessions

#### Admin (Requires Admin/HOD Role)
- `POST /api/v1/admin/kb/upload-document` - Upload document
- `GET /api/v1/admin/kb/documents` - List documents
- `DELETE /api/v1/admin/kb/documents/{id}` - Delete document
- `GET /api/v1/admin/violations` - View violation logs
- `GET /api/v1/admin/stats` - System statistics

---

## 🛡️ Guardrail Rules

### Input Guardrails

| Rule | Severity | Action |
|------|----------|--------|
| SQL_INJECTION | HIGH | Block & log |
| PROMPT_INJECTION | HIGH | Block & log |
| JAILBREAK | HIGH | Block & log |
| QUERY_LENGTH | LOW | Truncate |

### Output Guardrails

| Rule | Pattern | Action |
|------|---------|--------|
| PII_SHARING | Email, phone, SSN, Aadhar | Redact & flag |
| FINANCIAL_DATA | Salary, budget, costs | Redact & flag |
| KNOWLEDGE_BASE | Grounding check | Warn if not grounded |

---

## 🔮 Roadmap

### Phase 1 (Current) ✅
- [x] Knowledge Base RAG chatbot
- [x] Google OAuth authentication
- [x] Document upload and processing
- [x] Web scraping for KIT website
- [x] AI guardrails
- [x] Admin portal
- [x] Android mobile app

### Phase 2 (Planned) 🔄
- [ ] Teacher-Student secure chat
- [ ] Real-time messaging with WebSocket
- [ ] Department-based access control
- [ ] Advanced violation alerting
- [ ] Principal/HOD monitoring dashboard
- [ ] iOS mobile app

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 👥 Authors

Built for Kalaimagal Institute of Technology

---

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- FastAPI for excellent Python web framework
- Flutter team for amazing mobile framework
- pgvector for vector similarity search

---

<div align="center">

**Made with ❤️ for KIT Students and Faculty**

[Report Bug](https://github.com/SRD-personal/Camp-AI-Bot/issues) • [Request Feature](https://github.com/SRD-personal/Camp-AI-Bot/issues)

</div>
