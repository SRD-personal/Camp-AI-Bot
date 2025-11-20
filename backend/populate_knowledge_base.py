#!/usr/bin/env python3
"""
Web scraper to populate KIT knowledge base
Crawls https://kitcbe.com/ and uploads content to the knowledge base
"""
import asyncio
import aiohttp
import re
import sys
import logging
import argparse
from typing import Set, List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import get_async_database_url, AsyncSessionLocal
from app.models.document import Document
from app.models.document import KnowledgeChunk
from app.services.rag_service import RAGService
from app.services.document_service import DocumentService
from sqlalchemy import select, delete
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KITWebScraper:
    """Web scraper for KIT website"""

    def __init__(self, base_url: str = "https://kitcbe.com/"):
        self.base_url = base_url.rstrip('/')
        self.visited_urls: Set[str] = set()
        self.scraped_pages: List[Dict[str, Any]] = []
        self.session: Optional[aiohttp.ClientSession] = None

        # URL patterns to skip
        self.skip_patterns = [
            r'\.pdf$',
            r'\.jpg$',
            r'\.jpeg$',
            r'\.png$',
            r'\.gif$',
            r'\.zip$',
            r'\.exe$',
            r'\.doc$',
            r'\.docx$',
            r'\.ppt$',
            r'\.pptx$',
            r'\.xls$',
            r'\.xlsx$',
            r'#',  # Skip anchor links
            r'mailto:',
            r'tel:',
            r'javascript:',
        ]

    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL should be crawled

        Args:
            url: URL to check

        Returns:
            True if URL is valid for crawling
        """
        # Skip already visited
        if url in self.visited_urls:
            return False

        # Skip external URLs
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        if parsed.netloc and parsed.netloc != base_parsed.netloc:
            return False

        # Skip patterns
        for pattern in self.skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True

    def extract_text_from_html(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract meaningful text content from HTML

        Args:
            html: HTML content
            url: Page URL

        Returns:
            Dictionary with extracted content
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract title
        title = soup.title.string if soup.title else url.split('/')[-1]
        title = title.strip()

        # Extract meta description
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"].strip()

        # Extract main content
        # Try to find main content area
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|main", re.I))

        if main_content:
            text_content = main_content.get_text(separator="\n", strip=True)
        else:
            text_content = soup.get_text(separator="\n", strip=True)

        # Clean up text
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        text_content = '\n'.join(lines)

        # Extract links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(url, href)
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)

        return {
            'url': url,
            'title': title,
            'description': description,
            'content': text_content,
            'links': list(set(links)),
            'scraped_at': datetime.utcnow().isoformat()
        }

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch page content

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        return await response.text()
                    else:
                        logger.warning(f"Skipping non-HTML content: {url} ({content_type})")
                        return None
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    async def crawl_page(self, url: str) -> List[str]:
        """
        Crawl a single page

        Args:
            url: URL to crawl

        Returns:
            List of new URLs found
        """
        if not self.is_valid_url(url):
            return []

        logger.info(f"Crawling: {url}")
        self.visited_urls.add(url)

        html = await self.fetch_page(url)
        if not html:
            return []

        # Extract content
        page_data = self.extract_text_from_html(html, url)

        # Only save pages with meaningful content
        if len(page_data['content']) > 100:
            self.scraped_pages.append(page_data)
            logger.info(f"✓ Scraped: {page_data['title']} ({len(page_data['content'])} chars)")
        else:
            logger.warning(f"Skipping page with minimal content: {url}")

        # Rate limiting
        await asyncio.sleep(1)

        return page_data['links']

    async def crawl(self, max_pages: int = 100):
        """
        Crawl the website

        Args:
            max_pages: Maximum number of pages to crawl
        """
        logger.info(f"Starting crawl from {self.base_url}")
        logger.info(f"Max pages: {max_pages}")

        # Initialize session
        self.session = aiohttp.ClientSession()

        try:
            # BFS crawling
            queue = [self.base_url]

            while queue and len(self.scraped_pages) < max_pages:
                url = queue.pop(0)

                if url in self.visited_urls:
                    continue

                new_links = await self.crawl_page(url)

                # Add new links to queue
                for link in new_links:
                    if link not in self.visited_urls and link not in queue:
                        queue.append(link)

                logger.info(f"Progress: {len(self.scraped_pages)} pages scraped, {len(queue)} in queue")

            logger.info(f"✓ Crawling complete! Scraped {len(self.scraped_pages)} pages")

        finally:
            await self.session.close()

    def save_to_json(self, filename: str = "kit_scraped_data.json"):
        """
        Save scraped data to JSON file

        Args:
            filename: Output filename
        """
        filepath = Path(__file__).parent / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_pages, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved scraped data to {filepath}")


class KnowledgeBasePopulator:
    """Populates knowledge base with scraped content"""

    def __init__(self):
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
        self.skipped_count = 0
        self.updated_count = 0
        self.added_count = 0

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or exclamation
                for i in range(end, max(start + self.chunk_size // 2, 0), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    async def clear_existing_documents(self):
        """
        Clear all existing web documents from knowledge base

        This is useful when you want to re-scrape and replace all content
        """
        logger.info("Clearing existing web documents...")

        async with AsyncSessionLocal() as db:
            try:
                # Delete all chunks for web documents
                stmt = delete(KnowledgeChunk).where(
                    KnowledgeChunk.document_id.in_(
                        select(Document.id).where(Document.file_type == 'web')
                    )
                )
                result = await db.execute(stmt)
                chunks_deleted = result.rowcount

                # Delete all web documents
                stmt = delete(Document).where(Document.file_type == 'web')
                result = await db.execute(stmt)
                docs_deleted = result.rowcount

                await db.commit()

                logger.info(f"✓ Deleted {docs_deleted} documents and {chunks_deleted} chunks")

            except Exception as e:
                logger.error(f"✗ Failed to clear existing documents: {str(e)}")
                await db.rollback()
                raise

    async def populate(self, scraped_pages: List[Dict[str, Any]], skip_existing: bool = True):
        """
        Populate knowledge base with scraped content

        Args:
            scraped_pages: List of scraped page data
            skip_existing: If True, skip URLs that already exist (default: True)
        """
        logger.info(f"Populating knowledge base with {len(scraped_pages)} pages")
        if skip_existing:
            logger.info("Deduplication enabled: Will skip existing URLs")

        # Create database session
        async with AsyncSessionLocal() as db:
            rag_service = RAGService(db)
            doc_service = DocumentService(db)

            for page in scraped_pages:
                try:
                    logger.info(f"Processing: {page['title']}")

                    # Check if URL already exists (deduplication)
                    if skip_existing:
                        stmt = select(Document).where(Document.file_name == page['url'])
                        result = await db.execute(stmt)
                        existing_doc = result.scalar_one_or_none()

                        if existing_doc:
                            logger.info(f"  ⏭️  Skipping (already exists): {page['title']}")
                            self.skipped_count += 1
                            continue

                    # Create document
                    document = Document(
                        id=uuid.uuid4(),
                        title=page['title'],
                        description=page.get('description', '')[:500],
                        file_name=page['url'],
                        file_type='web',
                        file_size=len(page['content']),
                        status='processing',
                        department='general'
                    )
                    db.add(document)
                    await db.commit()
                    await db.refresh(document)

                    # Chunk the content
                    chunks = self.chunk_text(page['content'])
                    logger.info(f"  Created {len(chunks)} chunks")

                    # Process chunks with document service
                    await doc_service.process_document_content(
                        document_id=document.id,
                        content=page['content'],
                        file_type='web'
                    )

                    # Update document status
                    document.status = 'ready'
                    await db.commit()

                    self.added_count += 1
                    logger.info(f"  ✓ Uploaded: {page['title']}")

                except Exception as e:
                    logger.error(f"  ✗ Failed to process {page['title']}: {str(e)}")
                    await db.rollback()
                    continue

        logger.info("✓ Knowledge base population complete!")
        logger.info(f"  Added: {self.added_count}, Skipped: {self.skipped_count}")


async def main(args):
    """Main entry point"""
    logger.info("=" * 70)
    logger.info("KIT Knowledge Base Population Script")
    logger.info("=" * 70)

    # Initialize populator
    populator = KnowledgeBasePopulator()

    # Step 0: Clear existing documents if requested
    if args.clear_existing:
        logger.info("\n[0/3] Clearing existing web documents...")
        await populator.clear_existing_documents()

    # Step 1: Scrape website
    logger.info("\n[1/3] Scraping KIT website...")
    scraper = KITWebScraper("https://kitcbe.com/")
    await scraper.crawl(max_pages=args.max_pages)

    # Save to JSON for backup
    scraper.save_to_json()

    # Step 2: Populate knowledge base
    logger.info("\n[2/3] Populating knowledge base...")
    await populator.populate(scraper.scraped_pages, skip_existing=not args.allow_duplicates)

    # Step 3: Summary
    logger.info("\n[3/3] Summary")
    logger.info("=" * 70)
    logger.info(f"✓ Scraped {len(scraper.scraped_pages)} pages")
    logger.info(f"✓ Added {populator.added_count} new documents")
    logger.info(f"✓ Skipped {populator.skipped_count} existing documents")
    logger.info(f"✓ Total content: {sum(len(p['content']) for p in scraper.scraped_pages):,} characters")
    logger.info("=" * 70)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Scrape KIT website and populate knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal run (skip existing URLs)
  python populate_knowledge_base.py

  # Clear existing documents before scraping
  python populate_knowledge_base.py --clear-existing

  # Allow duplicates (don't skip existing URLs)
  python populate_knowledge_base.py --allow-duplicates

  # Scrape more pages
  python populate_knowledge_base.py --max-pages 100

  # Combine options
  python populate_knowledge_base.py --clear-existing --max-pages 100
        """
    )

    parser.add_argument(
        '--clear-existing',
        action='store_true',
        help='Delete all existing web documents before scraping (useful for full refresh)'
    )

    parser.add_argument(
        '--allow-duplicates',
        action='store_true',
        help='Allow duplicate URLs (by default, existing URLs are skipped)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=50,
        help='Maximum number of pages to scrape (default: 50)'
    )

    args = parser.parse_args()

    # Run main function
    asyncio.run(main(args))
