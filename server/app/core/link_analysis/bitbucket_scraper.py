"""
Bitbucket profile scraper using REST API
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class BitbucketAnalyzer(LinkAnalyzerBase):
    """Scraper for Bitbucket profiles using the Bitbucket API"""

    def __init__(self):
        super().__init__("Bitbucket")
        self.base_url = "https://api.bitbucket.org/2.0"

    def can_handle(self, url: str) -> bool:
        return "bitbucket.org" in url.lower()

    def extract_username(self, url: str) -> Optional[str]:
        # Bitbucket URLs: bitbucket.org/{username}
        match = re.search(r'bitbucket\.org/([^/?]+)', url)
        if match:
            username = match.group(1)
            if username not in ['dashboard', 'repo', 'projects', 'snippets']:
                return username
        return None

    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(
                platform=self.platform_name,
                valid_link=False,
                error="Invalid Bitbucket URL"
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

                # Get account info
                account = data.get("account_id", "")
                display_name = data.get("display_name", "")
                created_on = data.get("created_on", "")

                metrics = {
                    "display_name": display_name,
                    "account_id": account,
                    "created_on": created_on,
                }

                # Get repositories count
                repos_response = await client.get(
                    f"{self.base_url}/repositories/{username}",
                    params={"pagelen": 1},
                    timeout=10.0
                )

                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                    metrics["repo_count"] = repos_data.get("size", 0)

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
            logger.error(f"Bitbucket scrape failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )