# 🚀 Quick Start - Get Running in 15 Minutes

Follow these steps to get KIT CampusAI running locally.

## Step 1: Get Google Cloud Credentials (5 minutes)

### A. Create Google Cloud Project & Get Gemini API Key

1. **Go to Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Click "Create API Key"**
3. **Copy the API key** - You'll need this for `GEMINI_API_KEY`

### B. Setup Google OAuth (Web)

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project** (or create new one)
3. **Go to**: APIs & Services > Credentials
4. **Click**: Create Credentials > OAuth client ID
5. **Configure consent screen** (if needed):
   - User Type: External
   - App name: KIT CampusAI
   - User support email: your email
   - Developer contact: your email
6. **Create OAuth client**:
   - Application type: Web application
   - Name: KIT CampusAI Web
   - Authorized redirect URIs: `http://localhost:8000/auth/callback`
7. **Copy Client ID and Client Secret**

### C. Setup Google OAuth (Android)

1. **In same Credentials page**: Create Credentials > OAuth client ID
2. **Application type**: Android
3. **Package name**: `com.kitcampusai.android_app`
4. **Get SHA-1 fingerprint**:
   ```bash
   keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android | grep SHA1
   ```
5. **Paste SHA-1** and click Create

**Save these values:**
- ✅ Gemini API Key
- ✅ Web OAuth Client ID
- ✅ Web OAuth Client Secret

---

## Step 2: Setup Database (3 minutes)

### Install PostgreSQL with pgvector

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgresql-15-pgvector
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql@15 pgvector
brew services start postgresql@15
```

### Create Database

```bash
# Access PostgreSQL
sudo -u postgres psql

# Run these commands:
CREATE DATABASE kit_campusai;
\c kit_campusai
CREATE EXTENSION vector;
CREATE USER kit_admin WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE kit_campusai TO kit_admin;
\q
```

---

## Step 3: Configure Backend (2 minutes)

```bash
cd /home/user/Camp-AI-Bot/backend

# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Update these values in `.env`:**
```env
# Replace with your actual values
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/kit_campusai
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GEMINI_API_KEY=your-gemini-api-key
JWT_SECRET=your-random-secret-here
```

**Generate JWT Secret:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Step 4: Start Backend (2 minutes)

```bash
cd /home/user/Camp-AI-Bot/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test it:**
- Open browser: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Step 5: Setup Firebase (3 minutes)

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Create new project**: "KIT-CampusAI"
3. **Add Android app**:
   - Package name: `com.kitcampusai.android_app`
   - App nickname: KIT CampusAI
   - Click Register
4. **Download `google-services.json`**
5. **Place file**: `/home/user/Camp-AI-Bot/mobile/android_app/android/app/google-services.json`

---

## Step 6: Run Mobile App (Optional - if Flutter installed)

```bash
cd /home/user/Camp-AI-Bot/mobile/android_app

# Update API URL for local testing
# Edit lib/services/api_service.dart and lib/services/auth_service.dart
# Change: static const String _baseUrl = 'http://10.0.2.2:8000/api/v1';

# Install dependencies
flutter pub get

# Run app (with emulator or device connected)
flutter run
```

---

## ✅ Verification Checklist

After completing setup:

- [ ] Backend running at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Database has all tables (check with `\dt` in psql)
- [ ] Mobile app connects to backend (if Flutter installed)

---

## 🐛 Common Issues

**Database connection error:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Verify DATABASE_URL in .env matches your setup
```

**Gemini API error:**
```bash
# Verify API key is correct
# Check quota at: https://makersuite.google.com/app/apikey
```

**OAuth error:**
```bash
# Verify Client ID and Secret in .env
# Check redirect URIs in Google Cloud Console
```

**Module not found:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 Next Steps

Once backend is running:

1. **Create first admin user**:
   - Sign in via mobile app or use curl to call `/api/v1/auth/google`
   - Update user role in database:
     ```sql
     UPDATE users SET role = 'admin' WHERE email = 'your-email@gmail.com';
     ```

2. **Upload first document**:
   - Use admin API: `POST /api/v1/admin/kb/upload-document`
   - Or wait for web admin interface

3. **Test RAG chatbot**:
   - Use mobile app or call `POST /api/v1/chat/query`
   - Ask: "What is KIT?"

---

**Need Help?** Check `SETUP_GUIDE.md` for detailed troubleshooting.
