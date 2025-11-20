# 📚 Populate KIT Knowledge Base

This guide explains how to populate the knowledge base with content from the KIT website.

## ✅ Prerequisites

1. **Backend deployed** on Render.com with:
   - PostgreSQL database with pgvector extension
   - Environment variables configured (GEMINI_API_KEY, DATABASE_URL, etc.)
   - All migrations applied

2. **Python environment** with dependencies installed:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Basic Usage (Skip Existing URLs)

```bash
cd backend

# First time - scrapes and populates
python populate_knowledge_base.py

# Second time - automatically skips existing URLs (no duplicates!)
python populate_knowledge_base.py
```

### Full Refresh (Clear & Re-scrape)

```bash
# Delete all existing web documents and re-scrape everything
python populate_knowledge_base.py --clear-existing
```

### Scrape More Pages

```bash
# Scrape up to 100 pages instead of default 50
python populate_knowledge_base.py --max-pages 100
```

### Allow Duplicates (Disable Deduplication)

```bash
# Allow duplicate URLs (creates new documents even if URL exists)
python populate_knowledge_base.py --allow-duplicates
```

### Combine Options

```bash
# Full refresh with 100 pages
python populate_knowledge_base.py --clear-existing --max-pages 100
```

## 📖 What It Does

The scraper will:

1. **Crawl** https://kitcbe.com/ starting from homepage
2. **Extract** text content from all pages (up to 50 pages by default)
3. **Follow** internal links automatically
4. **Check** for duplicates - skips URLs that already exist (deduplication enabled by default)
5. **Chunk** content into ~1000 character segments with 200 char overlap
6. **Generate** embeddings using Gemini API
7. **Upload** to knowledge base automatically
8. **Save** backup to `kit_scraped_data.json`
9. **Report** summary with added vs skipped counts

## ⚙️ CLI Options

View all options:
```bash
python populate_knowledge_base.py --help
```

Available flags:

| Flag | Description | Default |
|------|-------------|---------|
| `--clear-existing` | Delete all web documents before scraping | False |
| `--allow-duplicates` | Disable deduplication (allow duplicates) | False |
| `--max-pages N` | Maximum pages to scrape | 50 |

**Deduplication Behavior:**
- ✅ **By default**: Skips URLs that already exist in database
- ⏭️ **On skip**: Logs message and increments skipped count
- 🆕 **On add**: Creates new document and increments added count
- 📊 **Summary**: Shows "Added: X, Skipped: Y" at the end

## 📊 Expected Output

### First Run (All New)

```
======================================================================
KIT Knowledge Base Population Script
======================================================================

[1/3] Scraping KIT website...
Deduplication enabled: Will skip existing URLs
Crawling: https://kitcbe.com/
✓ Scraped: Home - Kalaimagal Institute of Technology (2456 chars)
Crawling: https://kitcbe.com/about/
✓ Scraped: About KIT (1823 chars)
Progress: 10 pages scraped, 15 in queue
...
✓ Crawling complete! Scraped 50 pages
✓ Saved scraped data to kit_scraped_data.json

[2/3] Populating knowledge base...
Deduplication enabled: Will skip existing URLs
Processing: Home - Kalaimagal Institute of Technology
  Created 3 chunks
  ✓ Uploaded: Home - Kalaimagal Institute of Technology
Processing: About KIT
  Created 2 chunks
  ✓ Uploaded: About KIT
...
✓ Knowledge base population complete!
  Added: 50, Skipped: 0

[3/3] Summary
======================================================================
✓ Scraped 50 pages
✓ Added 50 new documents
✓ Skipped 0 existing documents
✓ Total content: 127,543 characters
======================================================================
```

### Second Run (With Existing Data)

```
[2/3] Populating knowledge base...
Deduplication enabled: Will skip existing URLs
Processing: Home - Kalaimagal Institute of Technology
  ⏭️  Skipping (already exists): Home - Kalaimagal Institute of Technology
Processing: About KIT
  ⏭️  Skipping (already exists): About KIT
Processing: New Course Page
  Created 2 chunks
  ✓ Uploaded: New Course Page
...
✓ Knowledge base population complete!
  Added: 5, Skipped: 45

[3/3] Summary
======================================================================
✓ Scraped 50 pages
✓ Added 5 new documents
✓ Skipped 45 existing documents
✓ Total content: 135,892 characters
======================================================================
```

## 🔍 Verify Knowledge Base

After running the scraper, you can verify content was added:

### Using PostgreSQL Shell (Render)

1. Go to Render Dashboard → PostgreSQL database
2. Click "Shell" tab
3. Run:
   ```sql
   -- Check number of documents
   SELECT COUNT(*) FROM documents WHERE file_type = 'web';

   -- Check number of chunks
   SELECT COUNT(*) FROM knowledge_chunks;

   -- Sample content
   SELECT title, description FROM documents WHERE file_type = 'web' LIMIT 10;
   ```

### Using API

```bash
# This requires admin authentication
curl https://kit-campusai-backend.onrender.com/api/v1/admin/kb/documents \
  -H "Authorization: Bearer <admin_token>"
```

## 🧪 Test the Knowledge Base

Once populated, test with queries:

```bash
# Get auth token first (see GOOGLE_OAUTH_SETUP.md)
# Then query the chatbot

curl -X POST https://kit-campusai-backend.onrender.com/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "query": "What is KIT?"
  }'
```

Expected response:
```json
{
  "message_id": "...",
  "response": "Kalaimagal Institute of Technology (KIT) is...",
  "sources": [
    {
      "content": "...",
      "document_title": "About KIT",
      "similarity_score": 0.87
    }
  ],
  "confidence": 0.85
}
```

## 🔧 Troubleshooting

### Error: Database connection failed
- Verify DATABASE_URL is set correctly
- Check database is "Available" in Render Dashboard
- Ensure URL uses `postgresql+asyncpg://` format

### Error: Failed to generate embedding
- Check GEMINI_API_KEY is valid
- Verify API quota hasn't been exceeded
- Check network connectivity to Google APIs

### Error: pgvector extension not found
```sql
-- Run in database shell
CREATE EXTENSION IF NOT EXISTS vector;
```

### Scraper is too slow
- Reduce `max_pages` parameter
- Increase rate limit delay in scraper (currently 1 second)
- Run during off-peak hours

### No pages scraped
- Check https://kitcbe.com/ is accessible
- Look for robots.txt restrictions
- Check firewall/network settings

## 📝 Backup & Recovery

The scraper creates a backup JSON file:
```bash
# Backup location
backend/kit_scraped_data.json

# To re-import from backup without re-scraping:
# Edit populate_knowledge_base.py main() to skip scraping:

async def main():
    # Load from existing JSON instead of scraping
    with open('kit_scraped_data.json', 'r') as f:
        scraped_pages = json.load(f)

    populator = KnowledgeBasePopulator()
    await populator.populate(scraped_pages)
```

## 🔄 Re-running the Scraper

**Good News**: Deduplication is now **automatic**! You can safely re-run the scraper.

### Behavior on Re-run

**Default (Recommended)**:
```bash
python populate_knowledge_base.py
```
- ✅ Skips existing URLs automatically
- 🆕 Only adds new pages that weren't in the database
- 📊 Shows "Added: X, Skipped: Y" in summary

**Full Refresh (Clear & Re-scrape)**:
```bash
python populate_knowledge_base.py --clear-existing
```
- 🗑️ Deletes all existing web documents first
- 🔄 Scrapes everything fresh
- ✅ Useful when website content has changed significantly

**Allow Duplicates (Not Recommended)**:
```bash
python populate_knowledge_base.py --allow-duplicates
```
- ⚠️ Creates duplicate documents for same URLs
- ❌ Will result in duplicate search results
- 🔧 Only use for testing or special cases

## 🎯 Next Steps

After populating the knowledge base:

1. ✅ Test queries via API
2. ✅ Build Android APK with production URL
3. ✅ Test end-to-end with mobile app
4. ✅ Monitor usage and add more documents as needed

## 📚 Adding More Content

### From Files (PDF, DOCX, TXT)

Use the admin upload endpoint:
```bash
curl -X POST https://kit-campusai-backend.onrender.com/api/v1/admin/kb/upload-document \
  -H "Authorization: Bearer <admin_token>" \
  -F "file=@document.pdf" \
  -F "title=Course Syllabus" \
  -F "department=Computer Science"
```

### From Other Websites

Modify the scraper:
```python
scraper = KITWebScraper("https://other-website.com/")
await scraper.crawl(max_pages=20)
```

### Manual Content Entry

Use the document creation API or add directly to database.

---

**Created**: 2025-11-20
**Script**: `backend/populate_knowledge_base.py`
**Status**: ✅ Ready to use
