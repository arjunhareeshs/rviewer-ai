"""
GitLab profile scraper using REST API
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class GitLabAnalyzer(LinkAnalyzerBase):
    """Scraper for GitLab profiles using the GitLab API"""

    def __init__(self):
        super().__init__("GitLab")
        self.base_url = "https://gitlab.com/api/v4"

    def can_handle(self, url: str) -> bool:
        return "gitlab.com" in url.lower()

    def extract_username(self, url: str) -> Optional[str]:
        # GitLab URLs: gitlab.com/{username}
        match = re.search(r'gitlab\.com/([^/?]+)', url)
        if match:
            username = match.group(1)
            # Skip common paths
            if username in ['users', 'dashboard', 'projects', 'groups', 'explore']:
                return None
            return username
        return None

    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(
                platform=self.platform_name,
                valid_link=False,
                error="Invalid GitLab URL"
            )

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                # Get user profile - GitLab API requires URL encoding for usernames
                import urllib.parse
                encoded_username = urllib.parse.quote(username, safe='')

                response = await client.get(
                    f"{self.base_url}/users",
                    params={"username": username},
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

                # Find exact match
                user = None
                for u in data:
                    if u.get("username", "").lower() == username.lower():
                        user = u
                        break

                if not user:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error="User not found"
                    )

                user_id = user.get("id")

                metrics = {
                    "name": user.get("name", ""),
                    "bio": user.get("bio", "")[:200] if user.get("bio") else "",
                    "public_repos": user.get("public_repos", 0),
                    "followers": user.get("followers", 0),
                    "following": user.get("following", 0),
                    "location": user.get("location", ""),
                    "website_url": user.get("website_url", ""),
                    "linkedin": user.get("linkedin", ""),
                    "twitter": user.get("twitter", ""),
                    "created_at": user.get("created_at", ""),
                }

                # Get more stats if we have user_id
                if user_id:
                    try:
                        # Get projects count
                        projects_response = await client.get(
                            f"{self.base_url}/users/{user_id}/projects",
                            params={"pagelen": 1},
                            timeout=10.0
                        )
                        if projects_response.status_code == 200:
                            proj_data = projects_response.json()
                            metrics["projects_count"] = len(proj_data) if isinstance(proj_data, list) else 0
                    except Exception as e:
                        logger.debug(f"Failed to fetch GitLab projects count: {e}")

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
            logger.error(f"GitLab scrape failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )