import re
import httpx
from typing import Dict, Any, Optional
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

class LinkedInAnalyzer(LinkAnalyzerBase):
    def __init__(self):
        super().__init__("LinkedIn")
        
    def can_handle(self, url: str) -> bool:
        return "linkedin.com" in url.lower()
        
    def extract_username(self, url: str) -> Optional[str]:
        # match linkedin.com/in/username
        match = re.search(r'linkedin\.com/in/([^/]+)', url.lower())
        return match.group(1) if match else None
        
    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(platform=self.platform_name, valid_link=False, error="Invalid LinkedIn URL format. Must be /in/username")
            
        # LinkedIn heavily blocks unauthenticated scraping.
        # We will attempt to fetch the public page for basic validation, 
        # but even if it returns 999 or 401, we might just assume the link is structurally valid
        # and extract the username for display.
        
        try:
            # We don't strictly need to scrape to provide value. Just returning the username 
            # tells the frontend the link was successfully parsed.
            metrics = {
                "profile_id": username,
            }
            
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=True,
                metrics=metrics
            )
        except Exception as e:
            return LinkPlatformData(platform=self.platform_name, username=username, valid_link=False, error=str(e))
