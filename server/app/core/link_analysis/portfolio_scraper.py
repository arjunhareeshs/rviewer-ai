import httpx
from bs4 import BeautifulSoup
import logging
from typing import Optional
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class PortfolioAnalyzer(LinkAnalyzerBase):
    def __init__(self):
        super().__init__("Portfolio/Personal Site")
        
    def can_handle(self, url: str) -> bool:
        # Fallback analyzer handles everything that isn't handled by specific scrapers
        return True
        
    async def extract(self, url: str) -> LinkPlatformData:
        try:
            # Ensure URL has scheme
            if not url.startswith('http'):
                url = f"https://{url}"
                
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=10.0)
                
                if response.status_code != 200:
                    return LinkPlatformData(
                        platform=self.platform_name, 
                        valid_link=False, 
                        error=f"HTTP Error {response.status_code}"
                    )
                    
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # Check responsiveness
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                is_responsive = viewport is not None
                
                # Basic content quality checks
                text_length = len(soup.get_text(separator=' ', strip=True))
                has_projects = bool(soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'section', 'div'] and 'project' in tag.get_text().lower()))
                
                metrics = {
                    "is_responsive": is_responsive,
                    "content_length": text_length,
                    "has_projects_section": has_projects,
                    "title": soup.title.string if soup.title else "No Title"
                }
                
                return LinkPlatformData(
                    platform=self.platform_name,
                    valid_link=True,
                    metrics=metrics
                )
        except Exception as e:
            logger.error(f"Portfolio scrape failed for {url}: {e}")
            return LinkPlatformData(platform=self.platform_name, valid_link=False, error=str(e))
