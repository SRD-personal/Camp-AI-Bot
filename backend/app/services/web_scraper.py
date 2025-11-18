"""
Web scraping service for AI tools
"""
import asyncio
from typing import List, Dict, Any, Set
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_tools import AITool, ToolData
from app.core.config import settings


class WebScraperService:
    """Service for web scraping and indexing"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # Configure Gemini for embeddings
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.embedding_model = 'models/embedding-001'
        
        self.max_pages = settings.SCRAPE_MAX_PAGES
        self.timeout = settings.SCRAPE_TIMEOUT_SECONDS
        self.user_agent = settings.USER_AGENT
    
    async def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single web page
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped page data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {'User-Agent': self.user_agent}
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = soup.title.string if soup.title else url
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Extract links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(url, href)
                    links.append(absolute_url)
                
                return {
                    'url': url,
                    'title': title,
                    'content': text,
                    'links': links,
                    'status': 'success'
                }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'failed'
            }
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text[:10000],  # Limit text length
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")
    
    async def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    async def scrape_website(
        self,
        tool: AITool,
        start_url: str,
        allowed_domains: List[str],
        max_pages: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Scrape an entire website
        
        Args:
            tool: AI tool to store data for
            start_url: Starting URL
            allowed_domains: List of allowed domains
            max_pages: Maximum pages to scrape
            
        Returns:
            Scraping result summary
        """
        if max_pages is None:
            max_pages = self.max_pages
        
        visited: Set[str] = set()
        to_visit: List[str] = [start_url]
        scraped_count = 0
        failed_count = 0
        
        while to_visit and scraped_count < max_pages:
            url = to_visit.pop(0)
            
            # Check if already visited
            if url in visited:
                continue
            
            # Check if URL is in allowed domains
            parsed = urlparse(url)
            if not any(domain in parsed.netloc for domain in allowed_domains):
                continue
            
            visited.add(url)
            
            # Scrape page
            page_data = await self.scrape_page(url)
            
            if page_data['status'] == 'success':
                # Chunk content
                chunks = await self.chunk_text(page_data['content'])
                
                # Store each chunk
                for i, chunk in enumerate(chunks):
                    try:
                        # Generate embedding
                        embedding = await self.generate_embedding(chunk)
                        
                        # Create tool data entry
                        tool_data = ToolData(
                            tool_id=tool.id,
                            source_url=url,
                            source_type='web_page',
                            title=f"{page_data['title']} - Part {i+1}",
                            content=chunk,
                            embedding=embedding,
                            metadata={
                                'chunk_index': i,
                                'total_chunks': len(chunks),
                                'page_title': page_data['title']
                            }
                        )
                        
                        self.db.add(tool_data)
                    except Exception as e:
                        print(f"Failed to process chunk {i} from {url}: {str(e)}")
                
                # Add new links to visit
                for link in page_data['links']:
                    if link not in visited and link not in to_visit:
                        to_visit.append(link)
                
                scraped_count += 1
                
                # Commit every 10 pages
                if scraped_count % 10 == 0:
                    await self.db.commit()
            else:
                failed_count += 1
            
            # Small delay to be respectful
            await asyncio.sleep(1)
        
        # Final commit
        await self.db.commit()
        
        return {
            'tool_id': str(tool.id),
            'start_url': start_url,
            'pages_scraped': scraped_count,
            'pages_failed': failed_count,
            'pages_visited': len(visited),
            'status': 'completed'
        }
