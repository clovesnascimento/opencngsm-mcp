"""
OpenCngsm v3.0 - Web Scraping Skill
Native Python implementation using BeautifulSoup4 and requests
"""
from bs4 import BeautifulSoup
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class WebScrapingSkill:
    """
    Web scraping using BeautifulSoup4 and requests
    
    Features:
    - Extract text, HTML, and metadata
    - Parse tables
    - Extract links and images
    - Support for Open Graph and Twitter Cards
    - Retry logic and timeout handling
    """
    
    def __init__(
        self,
        timeout: int = 15,
        max_retries: int = 2,
        user_agent: str = None
    ):
        """
        Initialize Web Scraping skill
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Create session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        })
    
    async def scrape(
        self,
        url: str,
        extract_tables: bool = True,
        extract_links: bool = False,
        extract_images: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape webpage and extract content
        
        Args:
            url: URL to scrape
            extract_tables: Extract HTML tables
            extract_links: Extract all links
            extract_images: Extract all images
        
        Returns:
            Dictionary with:
            - url: Original URL
            - text: Clean text content
            - html: Raw HTML
            - metadata: Page metadata (title, description, OG tags)
            - tables: List of tables (if extract_tables=True)
            - links: List of links (if extract_links=True)
            - images: List of images (if extract_images=True)
        
        Example:
            scraper = WebScrapingSkill()
            data = await scraper.scrape('https://example.com')
            print(data['metadata']['title'])
            print(data['text'][:200])
        """
        try:
            # Fetch with retries
            response = self._fetch_with_retry(url)
            if not response:
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract clean text
            text = self._extract_text(soup)
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            # Build result
            result = {
                'url': url,
                'text': text,
                'html': str(soup),
                'metadata': metadata
            }
            
            # Optional extractions
            if extract_tables:
                result['tables'] = self._extract_tables(soup)
            
            if extract_links:
                result['links'] = self._extract_links(soup, url)
            
            if extract_images:
                result['images'] = self._extract_images(soup, url)
            
            logger.info(f"✅ Scraped {url}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to scrape {url}: {e}")
            return None
    
    async def get_text(self, url: str) -> Optional[str]:
        """
        Extract only clean text from URL
        
        Args:
            url: URL to scrape
        
        Returns:
            Clean text content or None
        """
        result = await self.scrape(url, extract_tables=False)
        return result['text'] if result else None
    
    async def get_metadata(self, url: str) -> Optional[Dict]:
        """
        Extract only metadata from URL
        
        Args:
            url: URL to scrape
        
        Returns:
            Metadata dictionary or None
        """
        result = await self.scrape(url, extract_tables=False)
        return result['metadata'] if result else None
    
    async def get_tables(self, url: str) -> Optional[List[Dict]]:
        """
        Extract only tables from URL
        
        Args:
            url: URL to scrape
        
        Returns:
            List of table dictionaries or None
        """
        result = await self.scrape(url, extract_tables=True)
        return result['tables'] if result else None
    
    def _fetch_with_retry(self, url: str) -> Optional[requests.Response]:
        """Fetch URL with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {url}: {e}")
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} retries")
                    return None
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text from soup"""
        # Remove unwanted tags
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg']):
            tag.decompose()
        
        # Get text and clean
        text = soup.get_text(separator=' ', strip=True)
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract page metadata"""
        metadata = {
            'url': url,
            'title': '',
            'description': '',
            'og': {},
            'twitter': {}
        }
        
        # Title
        if soup.title:
            metadata['title'] = soup.title.string.strip()
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
        
        # Open Graph tags
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            key = meta.get('property', '').replace('og:', '')
            metadata['og'][key] = meta.get('content', '')
        
        # Twitter Card tags
        for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            key = meta.get('name', '').replace('twitter:', '')
            metadata['twitter'][key] = meta.get('content', '')
        
        return metadata
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all tables from page"""
        tables = []
        
        for idx, table in enumerate(soup.find_all('table')):
            rows = []
            
            for tr in table.find_all('tr'):
                cells = [
                    td.get_text(strip=True)
                    for td in tr.find_all(['td', 'th'])
                ]
                if cells:
                    rows.append(cells)
            
            if rows:
                tables.append({
                    'index': idx,
                    'headers': rows[0] if rows else [],
                    'rows': rows[1:] if len(rows) > 1 else [],
                    'row_count': len(rows) - 1
                })
        
        return tables
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all links from page"""
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'text': a.get_text(strip=True),
                'href': href,
                'absolute_url': absolute_url,
                'is_external': urlparse(absolute_url).netloc != urlparse(base_url).netloc
            })
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all images from page"""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            
            images.append({
                'src': src,
                'absolute_url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        return images


# Skill metadata
SKILL_NAME = "webscraping"
SKILL_CLASS = WebScrapingSkill
SKILL_DESCRIPTION = "Scrape web pages and extract content using BeautifulSoup4"


# Auto-register
from . import register_skill
register_skill(SKILL_NAME, SKILL_CLASS, SKILL_DESCRIPTION)
