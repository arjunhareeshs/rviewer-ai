"""
LeetCode Stats Card scraper - gets quick stats from the LeetCode stats card image
This provides an alternative quick way to get LeetCode stats without full GraphQL
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class LeetCodeStatsAnalyzer(LinkAnalyzerBase):
    """
    Alternative LeetCode scraper using the stats card API
    Note: This provides limited data but is faster
    """

    def __init__(self):
        super().__init__("LeetCode Stats")
        self.stats_url = "https://leetcode-stats-api.herokuapp.com"

    def can_handle(self, url: str) -> bool:
        # This is not a URL handler, it's a fallback for getting stats
        return False

    async def get_stats_by_username(self, username: str) -> LinkPlatformData:
        """Get LeetCode stats by username (alternative method)"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.stats_url}/{username}",
                    timeout=15.0
                )

                if response.status_code != 200:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error=f"Stats API Error: {response.status_code}"
                    )

                data = response.json()

                if data.get("status") != "success":
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error="User not found in stats API"
                    )

                metrics = {
                    "total_solved": data.get("totalSolved", 0),
                    "easy": data.get("easySolved", 0),
                    "medium": data.get("mediumSolved", 0),
                    "hard": data.get("hardSolved", 0),
                    "acceptance_rate": data.get("acceptanceRate", 0),
                    "ranking": data.get("ranking", 0),
                    "contribution_points": data.get("contributionPoints", 0),
                    "reputation": data.get("reputation", 0),
                }

                return LinkPlatformData(
                    platform="LeetCode",
                    username=username,
                    valid_link=True,
                    metrics=metrics
                )

        except ImportError:
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error="httpx not installed"
            )
        except Exception as e:
            logger.error(f"LeetCode stats API failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )

    # This analyzer doesn't handle URLs directly
    def can_handle(self, url: str) -> bool:
        return False

    async def extract(self, url: str) -> LinkPlatformData:
        return LinkPlatformData(
            platform=self.platform_name,
            valid_link=False,
            error="Use LeetCode main scraper for URL extraction"
        )