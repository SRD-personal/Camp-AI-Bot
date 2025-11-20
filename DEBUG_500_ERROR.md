# 🔧 Debugging the 500 Error on Chat Endpoint

## Current Status
The backend is deployed and responding, but `/api/v1/chat/query` returns **500 Internal Server Error**.

## ✅ What I've Added

### 1. Comprehensive Logging
Added detailed logging throughout the entire chat query flow:

**Chat endpoint (`backend/app/api/chat.py`):**
- Logs every step of processing
- Logs RAG service queries
- Logs guardrail checks
- Logs database operations
- Full traceback on errors

**Main app (`backend/app/main.py`):**
- Configured DEBUG-level logging
- Enhanced exception handler with full tracebacks
- Startup/shutdown logging

### 2. Debug Mode Features
When `DEBUG=True`:
- Detailed log output (DEBUG level)
- Full tracebacks in API responses
- Exception types and details exposed

---

## 🚀 Enable Debug Mode on Render

### Step 1: Add DEBUG Environment Variable
1. Go to Render Dashboard → **kit-campusai-backend** service
2. Click **"Environment"** in left sidebar
3. Click **"Add Environment Variable"**
4. Add:
   ```
   Key: DEBUG
   Value: True
   ```
5. Click **"Save Changes"**
6. Render will automatically redeploy

### Step 2: Check Logs
After redeploy completes:
1. Go to **"Logs"** tab
2. You should see:
   ```
   📊 Log level: DEBUG
   ```
3. Try the `/api/v1/chat/query` endpoint again
4. Watch the logs in real-time

---

## 📋 What to Look For in Logs

The logs will now show exactly where the error occurs:

### Success Path:
```
INFO - Chat query received from user <uuid>: <query>
DEBUG - Initializing services...
DEBUG - Services initialized successfully
DEBUG - Checking input guardrails...
DEBUG - Input guardrail check complete: safe=True
DEBUG - Getting/creating chat session...
DEBUG - Created new session: <session_id>
DEBUG - Fetching chat history...
DEBUG - Found 0 previous messages
INFO - Querying RAG service for: <query>
INFO - RAG query successful. Found X sources
```

### Failure Points to Watch:

**1. Service Initialization:**
```
ERROR - RAG service error: ...
```
**Cause:** Issues with RAG service, Gemini API, or database connection

**2. Database Operations:**
```
ERROR - Failed to create session
ERROR - sqlalchemy.exc...
```
**Cause:** Database schema issues, migration problems

**3. Guardrail Checks:**
```
ERROR - Guardrail service error
```
**Cause:** Issues with PII detection or validation

**4. RAG Query:**
```
ERROR - RAG service error: ...
RAG traceback: ...
```
**Cause:** Most likely - Gemini API issues, embedding generation, or vector search

---

## 🔍 Common Errors and Fixes

### Error 1: "no such table: knowledge_chunks"
**Cause:** Database migrations haven't run

**Fix:**
```bash
# In Render Dashboard → Service → Manual Deploy
# Clear build cache & deploy
```

Or check if Alembic migrations ran:
```
==> Running 'alembic upgrade head'
```

### Error 2: "relation 'vector' does not exist"
**Cause:** pgvector extension not enabled

**Fix:**
1. Go to Render Dashboard → **PostgreSQL database**
2. Click **"Shell"** tab
3. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Error 3: "GEMINI_API_KEY not set"
**Cause:** Environment variable missing

**Fix:**
- Check Environment tab has `GEMINI_API_KEY` set

### Error 4: "401 Unauthorized" from Gemini
**Cause:** Invalid API key or quota exceeded

**Fix:**
- Verify API key at: https://makersuite.google.com/app/apikey
- Check quota limits

### Error 5: "department" attribute not found
**Cause:** User model missing department field

**Fix:**
- Database schema mismatch
- Run migrations again

---

## 🧪 Testing the Chat Endpoint

Once you have DEBUG mode enabled and can see logs:

### Test 1: Simple Query (No Auth)
```bash
curl -X POST https://kit-campusai-backend.onrender.com/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello"}'
```

**Expected:** `401 Unauthorized` (needs auth token)

### Test 2: With Auth Token
First, you need to get an auth token (see GOOGLE_OAUTH_SETUP.md)

Then:
```bash
curl -X POST https://kit-campusai-backend.onrender.com/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"query": "What is KIT?"}'
```

**Expected:** Either success or detailed error in DEBUG mode

---

## 📊 Log Analysis

### Example Error Log:
```
2025-11-19 02:10:15 - app.api.chat - INFO - Chat query received from user abc-123: What is KIT?
2025-11-19 02:10:15 - app.api.chat - DEBUG - Initializing services...
2025-11-19 02:10:15 - app.api.chat - DEBUG - Services initialized successfully
2025-11-19 02:10:15 - app.api.chat - DEBUG - Checking input guardrails...
2025-11-19 02:10:15 - app.api.chat - DEBUG - Input guardrail check complete: safe=True
2025-11-19 02:10:15 - app.api.chat - DEBUG - Getting/creating chat session...
2025-11-19 02:10:15 - app.api.chat - ERROR - Chat query failed: 'NoneType' object has no attribute 'department'
2025-11-19 02:10:15 - app.api.chat - ERROR - Full traceback:
Traceback (most recent call last):
  File "/opt/render/project/src/backend/app/api/chat.py", line 160, in chat_query
    department=user.department,
                ^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'department'
```

**This tells us:** The user object doesn't have a department attribute - need to check User model

---

## 🎯 Next Steps

1. **Enable DEBUG=True** on Render
2. **Wait for redeploy** (~3 minutes)
3. **Try the chat endpoint** with/without auth
4. **Share the logs** from the Logs tab
5. I'll identify the exact issue and provide a fix

---

## 🔄 After Debugging

Once we fix the issue:

1. **Set DEBUG=False** for production
   ```
   DEBUG=False
   ```

2. **Redeploy** with the fix

3. **Test** to verify it works

4. **Monitor logs** for any other issues

---

## 📝 What to Share

When you enable DEBUG mode and test the endpoint, please share:

1. **The full error traceback** from logs
2. **The exact request** you're sending
3. **Environment variables** status (all set?)
4. **Database status** (Available?)

This will allow me to provide an exact fix!

---

**Created:** 2025-11-19
**Latest Commit:** 84f5350 - feat: Add comprehensive logging and debug mode
