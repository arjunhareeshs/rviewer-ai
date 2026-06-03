import httpx
import re
from typing import Dict, Any, Optional
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

class CodeforcesAnalyzer(LinkAnalyzerBase):
    def __init__(self):
        super().__init__("Codeforces")
        
    def can_handle(self, url: str) -> bool:
        return "codeforces.com" in url.lower()
        
    def extract_username(self, url: str) -> Optional[str]:
        match = re.search(r'codeforces\.com/profile/([^/]+)', url)
        return match.group(1) if match else None
        
    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(platform=self.platform_name, valid_link=False, error="Invalid Codeforces URL")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://codeforces.com/api/user.info?handles={username}")
                
                if response.status_code != 200:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error=f"API Error {response.status_code}"
                    )
                    
                data = response.json()
                
                if data.get("status") != "OK" or not data.get("result"):
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error="User not found"
                    )
                    
                user_info = data["result"][0]
                
                metrics = {
                    "rating": user_info.get("rating", 0),
                    "maxRating": user_info.get("maxRating", 0),
                    "rank": user_info.get("rank", "Unrated"),
                    "maxRank": user_info.get("maxRank", "Unrated")
                }
                
                return LinkPlatformData(
                    platform=self.platform_name,
                    username=username,
                    valid_link=True,
                    metrics=metrics
                )
        except Exception as e:
            return LinkPlatformData(platform=self.platform_name, username=username, valid_link=False, error=str(e))
