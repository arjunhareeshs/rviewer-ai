"""
Stack Overflow profile scraper using REST API
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class StackOverflowAnalyzer(LinkAnalyzerBase):
    """Scraper for Stack Overflow profiles using the Stack Exchange API"""

    def __init__(self):
        super().__init__("Stack Overflow")
        self.base_url = "https://api.stackexchange.com/2.3"

    def can_handle(self, url: str) -> bool:
        return "stackoverflow.com" in url.lower()

    def extract_username(self, url: str) -> Optional[str]:
        # Stack Overflow URLs: stackoverflow.com/users/{id}/{username}
        match = re.search(r'stackoverflow\.com/users/\d+/([^/?]+)', url)
        if match:
            return match.group(1)
        # Direct username: stackoverflow.com/{username}
        match = re.search(r'stackoverflow\.com/([^/?]+)', url)
        if match:
            username = match.group(1)
            if username not in ['users', 'questions', 'answers', 'tags']:
                return username
        return None

    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(
                platform=self.platform_name,
                valid_link=False,
                error="Invalid Stack Overflow URL"
            )

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                # Get user by name (note: might need user ID for reliable lookup)
                response = await client.get(
                    f"{self.base_url}/users",
                    params={
                        "inname": username,
                        "site": "stackoverflow",
                        "pagesize": 1
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error=f"API Error: {response.status_code}"
                    )

                data = response.json()
                items = data.get("items", [])

                if not items:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error="User not found"
                    )

                user = items[0]
                user_id = user.get("user_id")

                # Get user reputation and badges
                metrics = {
                    "reputation": user.get("reputation", 0),
                    "badge_counts": user.get("badge_counts", {}),
                    "display_name": user.get("display_name", ""),
                    "location": user.get("location", ""),
                    "creation_date": user.get("creation_date", ""),
                }

                # Get answer count if available
                if user_id:
                    try:
                        ans_response = await client.get(
                            f"{self.base_url}/users/{user_id}/answers",
                            params={"site": "stackoverflow", "pagesize": 1},
                            timeout=10.0
                        )
                        if ans_response.status_code == 200:
                            ans_data = ans_response.json()
                            metrics["answer_count"] = ans_data.get("total", 0)
                    except Exception as e:
                        logger.debug(f"Failed to scrape SO answers count: {e}")

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
            logger.error(f"Stack Overflow scrape failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )