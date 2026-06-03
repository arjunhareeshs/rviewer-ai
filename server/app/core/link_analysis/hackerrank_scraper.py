import re
import logging
from typing import Optional
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class HackerRankAnalyzer(LinkAnalyzerBase):
    def __init__(self):
        super().__init__("HackerRank")
        
    def can_handle(self, url: str) -> bool:
        return "hackerrank.com" in url.lower()
        
    def extract_username(self, url: str) -> Optional[str]:
        match = re.search(r'hackerrank\.com/([^/?]+)', url)
        return match.group(1) if match else None
        
    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(platform=self.platform_name, valid_link=False, error="Invalid HackerRank URL")
            
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate and wait for the page to load
                await page.goto(f"https://www.hackerrank.com/{username}", wait_until="domcontentloaded", timeout=15000)
                
                # Check for 404
                if "404" in await page.title():
                    await browser.close()
                    return LinkPlatformData(platform=self.platform_name, username=username, valid_link=False, error="User not found")
                
                # Try to extract some basic metrics (badges, verified skills)
                # Since HackerRank's DOM changes, we wrap in try/except for elements
                try:
                    badges_count = await page.locator(".hacker-badge").count()
                except Exception:
                    badges_count = 0
                    
                try:
                    certificates = await page.locator(".certificate-heading").count()
                except Exception:
                    certificates = 0
                    
                await browser.close()
                
                metrics = {
                    "badges": badges_count,
                    "certificates": certificates
                }
                
                return LinkPlatformData(
                    platform=self.platform_name,
                    username=username,
                    valid_link=True,
                    metrics=metrics
                )
        except ImportError:
            return LinkPlatformData(
                platform=self.platform_name, 
                username=username, 
                valid_link=True, 
                error="Playwright not installed, skipping scrape",
                metrics={}
            )
        except Exception as e:
            logger.error(f"HackerRank scrape failed: {e}")
            return LinkPlatformData(platform=self.platform_name, username=username, valid_link=False, error=str(e))
