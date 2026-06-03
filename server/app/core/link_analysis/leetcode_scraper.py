import httpx
import re
from typing import Dict, Any, Optional
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

class LeetCodeAnalyzer(LinkAnalyzerBase):
    def __init__(self):
        super().__init__("LeetCode")
        
    def can_handle(self, url: str) -> bool:
        return "leetcode.com" in url.lower()
        
    def extract_username(self, url: str) -> Optional[str]:
        # match leetcode.com/username or leetcode.com/u/username
        match = re.search(r'leetcode\.com/(?:u/)?([^/]+)', url)
        return match.group(1) if match else None
        
    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(platform=self.platform_name, valid_link=False, error="Invalid LeetCode URL")
            
        graphql_query = {
            "query": """
            query getUserProfile($username: String!) {
                matchedUser(username: $username) {
                    submitStats: submitStatsGlobal {
                        acSubmissionNum {
                            difficulty
                            count
                        }
                    }
                    profile {
                        ranking
                        reputation
                        starRating
                    }
                    submissionCalendar
                }
            }
            """,
            "variables": {"username": username}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://leetcode.com/graphql",
                    json=graphql_query,
                    headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"}
                )
                
                if response.status_code != 200:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error=f"API Error {response.status_code}"
                    )
                    
                data = response.json()
                
                if "errors" in data or not data.get("data", {}).get("matchedUser"):
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error="User not found"
                    )
                    
                user_data = data["data"]["matchedUser"]
                submissions = user_data.get("submitStats", {}).get("acSubmissionNum", [])
                
                metrics = {
                    "ranking": user_data.get("profile", {}).get("ranking", 0),
                    "problems_solved": {
                        item["difficulty"]: item["count"] for item in submissions
                    }
                }
                
                import json
                calendar_str = user_data.get("submissionCalendar", "{}")
                try:
                    calendar_data = json.loads(calendar_str)
                except Exception:
                    calendar_data = {}
                    
                activity_data = {
                    "heatmap": calendar_data
                }
                
                return LinkPlatformData(
                    platform=self.platform_name,
                    username=username,
                    valid_link=True,
                    metrics=metrics,
                    activity_data=activity_data
                )
        except Exception as e:
            return LinkPlatformData(platform=self.platform_name, username=username, valid_link=False, error=str(e))
