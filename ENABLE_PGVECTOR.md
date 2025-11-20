# 🔧 Urgent: Enable pgvector Extension

## Current Error
```
syntax error at or near ":"
```

This error suggests the **pgvector extension is not enabled** in your PostgreSQL database.

---

## ✅ Solution: Enable pgvector Extension

### Step 1: Go to Render Database
1. Open Render Dashboard
2. Click on your **PostgreSQL database** (not the web service)
3. Should be named something like `kit-campusai-db`

### Step 2: Open Database Shell
1. Click the **"Shell"** tab (or "Connect" → "PSQL Command")
2. You'll see a terminal interface

### Step 3: Enable pgvector
Run this command in the shell:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**Expected output:**
```
CREATE EXTENSION
```

### Step 4: Verify Extension is Installed
Run this to confirm:

```sql
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
```

**Expected output:**
```
 extname | extversion
---------+------------
 vector  | 0.5.0
(1 row)
```

If you see this, pgvector is installed! ✅

---

## 🔄 After Enabling pgvector

Once the extension is enabled:

1. **Redeploy your backend** (or just restart it):
   - Go to Web Service → Manual Deploy
   - Or it will auto-redeploy on next commit

2. **Test the endpoint again**

3. **It should work!** The vector queries will now execute properly.

---

## ⚠️ If CREATE EXTENSION Fails

If you get an error like:
```
ERROR: could not open extension control file
```

**Solution:**
- pgvector might not be available on your PostgreSQL instance
- Check Render's documentation or contact support
- Alternative: Use a different hosting provider that supports pgvector (like Supabase)

---

## 📊 What This Fixes

With pgvector enabled, PostgreSQL will:
- Recognize the `vector` data type
- Support the `<=>` cosine distance operator
- Allow vector similarity search queries
- Enable the RAG system to work properly

---

**Enable the extension and let me know if it works!** 🚀
