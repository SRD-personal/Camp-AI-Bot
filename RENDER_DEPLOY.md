# 🚀 One-Click Render.com Deployment

This repository is configured for automatic deployment to Render.com using `render.yaml`.

## Quick Deploy (3 Steps)

### Step 1: Connect Render to GitHub

1. Go to: https://render.com/
2. Sign up/Login with GitHub
3. Grant Render access to this repository: `SRD-personal/Camp-AI-Bot`

### Step 2: Create New Blueprint

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Select repository: **`SRD-personal/Camp-AI-Bot`**
3. Branch: **`claude/build-camp-ai-bot-phase1-01CSwb6bLtAfHkKW5EYTX7sS`**
4. Render will detect `render.yaml` automatically

### Step 3: Add Environment Variables

Render will prompt you to provide these values (marked as `sync: false`):

```env
GOOGLE_CLIENT_ID=<your Google OAuth Client ID>
GOOGLE_CLIENT_SECRET=<your Google OAuth Client Secret>
GEMINI_API_KEY=<your Gemini API Key>
```

**Use the credentials from your `.env` file**

Click **"Apply"** and Render will:
- Create PostgreSQL database with pgvector
- Create web service
- Install dependencies
- Run database migrations
- Deploy backend

**Deployment takes ~5 minutes!**

---

## Post-Deployment Steps

### 1. Enable pgvector Extension

Once the database is created:

1. Go to your database in Render Dashboard
2. Click **"Shell"** tab
3. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   SELECT extname FROM pg_extension WHERE extname = 'vector';
   ```

### 2. Verify Deployment

Your API will be live at: `https://kit-campusai-backend.onrender.com`

Test it:
```bash
curl https://kit-campusai-backend.onrender.com/health
# Should return: {"status":"healthy"}
```

Visit API docs: `https://kit-campusai-backend.onrender.com/docs`

### 3. Update OAuth Redirect URI

Add your production URL to Google Cloud Console:

Go to: https://console.cloud.google.com/apis/credentials

Add to authorized redirect URIs:
```
https://kit-campusai-backend.onrender.com/api/v1/auth/google
```

---

## What Gets Deployed

From `render.yaml`:

✅ **PostgreSQL Database**
- Name: `kit-campusai-db`
- Plan: Free
- Region: Oregon
- PostgreSQL 15 with pgvector extension

✅ **Web Service**
- Name: `kit-campusai-backend`
- Runtime: Python 3.11
- Plan: Free
- Health check: `/health`
- Auto-deploy on git push

✅ **Environment Variables**
- Database URL: Auto-linked
- JWT Secret: Auto-generated
- API credentials: You provide manually

---

## Monitoring

In Render Dashboard you can:
- View real-time logs
- Monitor resource usage
- Set up alerts
- Configure auto-scaling (paid plans)

---

## Troubleshooting

### Build fails
- Check logs in Render Dashboard
- Verify Python version matches requirements
- Ensure all dependencies in requirements.txt are valid

### Database connection error
- Verify pgvector extension is enabled
- Check DATABASE_URL is correctly linked
- Ensure database and web service are in same region

### Gemini API error
- Verify GEMINI_API_KEY is correct
- Check API quota at https://makersuite.google.com/app/apikey
- Ensure Gemini API is enabled in Google Cloud

---

## Cost

Everything runs on **FREE TIER**:
- Web Service: 750 hours/month free
- PostgreSQL: Free for 90 days, then $7/month
- No credit card required for free tier

---

**Your backend will be live in production within 5 minutes! 🎉**
