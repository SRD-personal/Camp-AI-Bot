# 🚀 Immediate Actions - Get Started NOW!

## ✅ Progress So Far

- ✅ **Backend code created** - All files are ready
- ✅ **Mobile app created** - Flutter app is ready  
- ✅ **Python dependencies** - Core packages installed in venv
- ✅ **.env file created** - With auto-generated JWT_SECRET
- ⏳ **PostgreSQL** - Needs manual setup (see below)
- ⏳ **API Credentials** - Need to get from Google Cloud

---

## 📋 What You Need to Do (20 minutes)

### Action 1: Get Google Cloud Credentials (10 minutes)

#### Step 1.1: Get Gemini API Key

1. Visit: **https://makersuite.google.com/app/apikey**
2. Click "Create API Key"
3. Copy the key

#### Step 1.2: Setup OAuth Web Credentials  

1. Visit: **https://console.cloud.google.com/apis/credentials**
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen if prompted (just fill basic info)
4. Application type: **Web application**
5. Authorized redirect URIs: `http://localhost:8000/auth/callback`
6. Copy **Client ID** and **Client Secret**

#### Step 1.3: Setup OAuth Android Credentials

1. Same credentials page → "Create Credentials" → "OAuth client ID"
2. Application type: **Android**
3. Package name: `com.kitcampusai.android_app`
4. Get SHA-1 fingerprint:
   ```bash
   keytool -list -v -keystore ~/.android/debug.keystore \
     -alias androiddebugkey -storepass android -keypass android | grep SHA1
   ```
5. Paste SHA-1 and create

#### Step 1.4: Update .env File

Edit `backend/.env` and add your credentials:

```bash
cd /home/user/Camp-AI-Bot/backend
nano .env  # or vim .env

# Add these values:
GEMINI_API_KEY=your-actual-gemini-api-key-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

---

### Action 2: Setup PostgreSQL Database (5 minutes)

The PostgreSQL server is already installed and running. Just need to create the database:

```bash
# Method 1: Using setup script
cd /home/user/Camp-AI-Bot
sudo -u postgres psql < setup_database.sql

# Method 2: Manual commands
sudo -u postgres psql <<EOF
CREATE DATABASE kit_campusai;
\c kit_campusai
CREATE EXTENSION vector;
\q
