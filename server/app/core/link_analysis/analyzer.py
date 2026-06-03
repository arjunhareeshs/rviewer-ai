import logging
import asyncio
from typing import List, Dict, Any
from app.core.analysis.schemas import LinkPlatformData, LinkAnalysisResult

logger = logging.getLogger(__name__)

class LinkAnalyzerBase:
    """Base class for all link scrapers"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        
    def can_handle(self, url: str) -> bool:
        """Check if this analyzer can handle the given URL"""
        raise NotImplementedError
        
    async def extract(self, url: str) -> LinkPlatformData:
        """Extract data from the URL"""
        raise NotImplementedError

class LinkAnalysisOrchestrator:
    def __init__(self):
        self._analyzers = []
        
    def register_analyzer(self, analyzer: LinkAnalyzerBase):
        self._analyzers.append(analyzer)
        
    async def analyze_links(self, urls: List[str]) -> LinkAnalysisResult:
        tasks = []
        for url in urls:
            analyzer_found = False
            for analyzer in self._analyzers:
                if analyzer.can_handle(url):
                    tasks.append(analyzer.extract(url))
                    analyzer_found = True
                    break
            
            if not analyzer_found:
                # Fallback to portfolio scraper if no specific match
                from .portfolio_scraper import PortfolioAnalyzer
                portfolio_analyzer = PortfolioAnalyzer()
                tasks.append(portfolio_analyzer.extract(url))
                
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_platforms = []
        score = 0
        
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Error extracting link: {res}")
            elif isinstance(res, LinkPlatformData):
                valid_platforms.append(res)
                if res.valid_link and res.metrics:
                    score += 20  # Base score for valid connected profile with data
                    
        # Ensure standard platforms are present for the frontend
        required_platforms = ["GitHub", "LeetCode", "LinkedIn"]
        found_names = [p.platform for p in valid_platforms]
        
        for req in required_platforms:
            if req not in found_names:
                valid_platforms.append(
                    LinkPlatformData(
                        platform=req,
                        valid_link=False,
                        error="No link found in resume"
                    )
                )

        overall_score = min(100, score)
        
        return LinkAnalysisResult(
            platforms=valid_platforms,
            overall_presence_score=overall_score
        )

# Global orchestrator instance
link_orchestrator = LinkAnalysisOrchestrator()
