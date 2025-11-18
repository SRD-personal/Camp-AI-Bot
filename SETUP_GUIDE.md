# KIT CampusAI - Complete Setup Guide

This guide walks you through setting up KIT CampusAI from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Backend Setup](#backend-setup)
4. [Database Setup](#database-setup)
5. [Mobile App Setup](#mobile-app-setup)
6. [Deployment](#deployment)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Software Requirements

- **Python**: 3.9 or higher
- **PostgreSQL**: 13 or higher
- **Flutter**: 3.0 or higher
- **Git**: Latest version
- **Android Studio**: Latest version (for mobile development)

### Accounts Needed

1. **Google Cloud Account** (free tier available)
   - For Gemini API
   - For Google OAuth

2. **Render.com Account** (free tier available)
   - For backend hosting

3. **GitHub Account**
   - For version control and deployment

---

## Google Cloud Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Name: "KIT-CampusAI"
4. Click "Create"

### 2. Enable Required APIs

1. Go to "APIs & Services" > "Enable APIs and Services"
2. Enable the following APIs:
   - **Generative Language API** (for Gemini)
   - **Google Sign-In API**

### 3. Create API Keys

#### Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy and save the key

#### OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure consent screen if needed
4. Application type: "Web application"
5. Authorized redirect URIs:
   ```
   http://localhost:8000/auth/callback
   https://your-app.onrender.com/auth/callback
   ```
6. Save Client ID and Client Secret

#### Android OAuth Credentials

1. Create another OAuth client
2. Application type: "Android"
3. Package name: `com.kitcampusai.android_app`
4. Get SHA-1 fingerprint:
   ```bash
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
   ```
5. Enter SHA-1 in the form
6. Create

---

## Backend Setup

### 1. Clone Repository

```bash
git clone https://github.com/SRD-personal/Camp-AI-Bot.git
cd Camp-AI-Bot/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# Required - Update these values
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GEMINI_API_KEY=your-gemini-api-key
JWT_SECRET=your-secret-key-here-use-random-string

# Database (update after database setup)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/kit_campusai

# Optional - Keep defaults
ENVIRONMENT=development
DEBUG=True
API_VERSION=v1
```

Generate JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Database Setup

### 1. Install PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Windows
Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

### 2. Install pgvector Extension

```bash
# Ubuntu/Debian
sudo apt install postgresql-15-pgvector

# macOS
brew install pgvector

# Or build from source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 3. Create Database

```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE kit_campusai;

# Connect to database
\c kit_campusai;

# Create pgvector extension
CREATE EXTENSION vector;

# Create user (optional)
CREATE USER kit_admin WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE kit_campusai TO kit_admin;

# Exit
\q
```

### 4. Run Migrations

```bash
cd backend
alembic upgrade head
```

### 5. Verify Database

```bash
psql -U postgres -d kit_campusai

# Check tables
\dt

# Should see:
# - users
# - documents
# - knowledge_chunks
# - chat_sessions
# - messages
# - violation_logs
# - ai_tools
# - tool_data
# - tool_calls
```

---

## Backend Testing

### 1. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test API

Open browser: `http://localhost:8000/docs`

You should see FastAPI Swagger documentation.

### 3. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

---

## Mobile App Setup

### 1. Install Flutter

Follow official guide: https://docs.flutter.dev/get-started/install

Verify installation:
```bash
flutter doctor
```

### 2. Setup Android SDK

1. Install Android Studio
2. Install Android SDK (API 21+)
3. Create Android Emulator or connect physical device

### 3. Configure Project

```bash
cd mobile/android_app

# Install dependencies
flutter pub get
```

### 4. Firebase Setup (for Google Sign-In)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project: "KIT-CampusAI"
3. Add Android app:
   - Package name: `com.kitcampusai.android_app`
   - Download `google-services.json`
   - Place in `android/app/`

### 5. Update API Base URL

Edit `lib/services/api_service.dart`:

```dart
// For local development with emulator
static const String _baseUrl = 'http://10.0.2.2:8000/api/v1';

// For physical device on same network
static const String _baseUrl = 'http://YOUR_COMPUTER_IP:8000/api/v1';
```

### 6. Run Mobile App

```bash
# List devices
flutter devices

# Run on connected device/emulator
flutter run
```

---

## Deployment

### Deploy to Render.com

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Account**
   - Go to [Render.com](https://render.com/)
   - Sign up with GitHub

3. **Create Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repository
   - Select branch: `main`
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`

4. **Add Environment Variables**
   In Render dashboard, add:
   ```
   DATABASE_URL=<from Render PostgreSQL>
   GOOGLE_CLIENT_ID=<your value>
   GOOGLE_CLIENT_SECRET=<your value>
   GEMINI_API_KEY=<your value>
   JWT_SECRET=<your value>
   ENVIRONMENT=production
   DEBUG=False
   CORS_ORIGINS=*
   ```

5. **Create PostgreSQL Database**
   - Click "New +"
   - Select "PostgreSQL"
   - Name: "kit-campusai-db"
   - Region: Same as web service
   - Plan: Free
   - Create

6. **Enable pgvector**
   Connect to database and run:
   ```sql
   CREATE EXTENSION vector;
   ```

7. **Deploy**
   - Render will automatically deploy
   - Check logs for any errors
   - Access at: `https://your-app.onrender.com`

---

## Initial Data Setup

### 1. Create Admin User

First user to sign in with Google becomes admin. Or manually update:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@gmail.com';
```

### 2. Upload Documents

1. Sign in to mobile app or web admin
2. Navigate to admin panel
3. Upload PDF/DOCX/TXT files
4. Wait for processing to complete

### 3. Setup KIT Website Scraper

Create AI tool for KIT website:

```sql
INSERT INTO ai_tools (id, name, description, tool_type, status, source_urls, function_definition)
VALUES (
  gen_random_uuid(),
  'kit_campus_website',
  'Search KIT campus website for information',
  'web_scraper',
  'active',
  '["https://kitcbe.com"]',
  '{"name": "kit_campus_website", "description": "Search KIT website", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}}'
);
```

Then trigger scrape (via admin API or script).

---

## Testing

### Test Authentication

1. Open mobile app
2. Click "Sign in with Google"
3. Select Google account
4. Should redirect to home screen

### Test Chat

1. Navigate to "Knowledge Base Chat"
2. Send message: "What is KIT?"
3. Should receive AI response with sources

### Test Admin Features

1. Sign in as admin
2. Upload a document
3. Check processing status
4. Query about document content

---

## Troubleshooting

### Backend Issues

**Database Connection Error**
```
Solution: Check DATABASE_URL in .env
Verify PostgreSQL is running: sudo service postgresql status
```

**Gemini API Error**
```
Solution: Verify GEMINI_API_KEY is correct
Check API quota in Google Cloud Console
```

**OAuth Error**
```
Solution: Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
Verify redirect URIs match in Google Cloud Console
```

### Mobile Issues

**Google Sign-In Not Working**
```
Solution:
1. Verify SHA-1 fingerprint is correct
2. Check package name matches: com.kitcampusai.android_app
3. Ensure google-services.json is in android/app/
4. Clean and rebuild: flutter clean && flutter pub get
```

**API Connection Error**
```
Solution:
1. For emulator: Use 10.0.2.2 instead of localhost
2. For physical device: Use computer's local IP
3. Verify backend is running and accessible
4. Check firewall settings
```

**Build Errors**
```
Solution:
flutter clean
flutter pub get
flutter run
```

### Deployment Issues

**Render Build Failed**
```
Solution:
1. Check build logs in Render dashboard
2. Verify requirements.txt is complete
3. Ensure Python version is 3.9+
```

**Database Migration Error**
```
Solution:
1. Check DATABASE_URL is correct
2. Verify pgvector extension is installed
3. Run migrations manually: alembic upgrade head
```

---

## Next Steps

1. ✅ Complete Phase 1 setup
2. 📱 Deploy mobile app to Google Play Store
3. 🔐 Implement Phase 2 (Teacher-Student Chat)
4. 📊 Setup monitoring and analytics
5. 🎨 Customize branding and themes

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/SRD-personal/Camp-AI-Bot/issues
- Email: support@kitcampusai.com

---

**Congratulations! Your KIT CampusAI is now ready to use! 🎉**
