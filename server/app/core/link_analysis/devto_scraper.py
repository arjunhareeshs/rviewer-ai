"""
Dev.to profile scraper using REST API
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class DevToAnalyzer(LinkAnalyzerBase):
    """Scraper for Dev.to profiles using the Dev.to API"""

    def __init__(self):
        super().__init__("Dev.to")
        self.base_url = "https://dev.to/api"

    def can_handle(self, url: str) -> bool:
        return "dev.to" in url.lower() or "dev.to" in url.lower()

    def extract_username(self, url: str) -> Optional[str]:
        # Dev.to URLs: dev.to/{username}
        match = re.search(r'dev\.to/([^/?]+)', url)
        if match:
            username = match.group(1)
            # Skip if it's an article path
            if username in ['articles', 'new', 'organizations', 'tags', 'welcome']:
                return None
            return username
        return None

    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(
                platform=self.platform_name,
                valid_link=False,
                error="Invalid Dev.to URL"
            )

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                # Get user profile
                response = await client.get(
                    f"{self.base_url}/users/{username}",
                    timeout=10.0
                )

                if response.status_code != 200:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error=f"User not found (status: {response.status_code})"
                    )

                data = response.json()

                metrics = {
                    "name": data.get("name", ""),
                    "username": data.get("username", ""),
                    "bio": data.get("bio", "")[:200] if data.get("bio") else "",
                    "twitter_username": data.get("twitter_username", ""),
                    "github_username": data.get("github_username", ""),
                    "website_url": data.get("website_url", ""),
                    "location": data.get("location", ""),
                    "joined_at": data.get("joined_at", ""),
                }

                # Get articles count
                articles_response = await client.get(
                    f"{self.base_url}/articles",
                    params={"username": username, "per_page": 1},
                    timeout=10.0
                )

                if articles_response.status_code == 200:
                    articles_data = articles_response.json()
                    metrics["article_count"] = len(articles_data) if isinstance(articles_data, list) else 0
                    # If we got articles, count total from pagination header
                    if hasattr(articles_response, 'headers'):
                        total = articles_response.headers.get('total', '')
                        if total:
                            metrics["total_articles"] = int(total)

                # Get followers count (Dev.to doesn't expose this in user endpoint directly)
                # But we can estimate from the user object
                metrics["user_id"] = data.get("user_id", "")

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
                error="httpx not installed",
                metrics={}
            )
        except Exception as e:
            logger.error(f"Dev.to scrape failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )