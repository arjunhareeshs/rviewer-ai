import httpx
import re
from typing import Dict, Any, Optional
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

class GithubAnalyzer(LinkAnalyzerBase):
    def __init__(self):
        super().__init__("GitHub")
        
    def can_handle(self, url: str) -> bool:
        return "github.com" in url.lower()
        
    def extract_username(self, url: str) -> Optional[str]:
        match = re.search(r'github\.com/([^/]+)', url)
        return match.group(1) if match else None
        
    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(platform=self.platform_name, valid_link=False, error="Invalid GitHub URL")
            
        try:
            async with httpx.AsyncClient() as client:
                # Use authenticated API if token is available (5000 req/hr vs 60)
                from app.config import get_settings
                _settings = get_settings()
                headers = {}
                if _settings.GITHUB_TOKEN:
                    headers["Authorization"] = f"Bearer {_settings.GITHUB_TOKEN}"
                
                response = await client.get(f"https://api.github.com/users/{username}", headers=headers)
                
                if response.status_code != 200:
                    return LinkPlatformData(
                        platform=self.platform_name, 
                        username=username,
                        valid_link=False,
                        error=f"API Error {response.status_code}"
                    )
                    
                data = response.json()
                
                # Fetch repositories for stars and forks
                repos_response = await client.get(f"https://api.github.com/users/{username}/repos?per_page=100&sort=pushed", headers=headers)
                
                total_stars = 0
                total_forks = 0
                top_repos = []
                
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                    
                    for repo in repos_data:
                        if not repo.get("fork"): # exclude forks
                            total_stars += repo.get("stargazers_count", 0)
                            total_forks += repo.get("forks_count", 0)
                    
                    # Sort by stars
                    sorted_repos = sorted([r for r in repos_data if not r.get("fork")], key=lambda x: x.get("stargazers_count", 0), reverse=True)
                    top_repos = [{"name": r.get("name"), "stars": r.get("stargazers_count", 0), "url": r.get("html_url"), "description": r.get("description")} for r in sorted_repos[:3]]
                
                metrics = {
                    "public_repos": data.get("public_repos", 0),
                    "followers": data.get("followers", 0),
                    "following": data.get("following", 0),
                    "total_stars": total_stars,
                    "total_forks": total_forks,
                    "top_repos": top_repos,
                    "bio": data.get("bio", ""),
                }
                
                # We can construct a heatmap URL for the frontend
                activity_data = {
                    "heatmap_url": f"https://ghchart.rshah.org/409ba5/{username}"
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
