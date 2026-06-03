"""
Link analysis module for extracting profiles from various platforms.
"""

from .analyzer import link_orchestrator
from .github_scraper import GithubAnalyzer
from .linkedin_scraper import LinkedInAnalyzer
from .leetcode_scraper import LeetCodeAnalyzer
from .codeforces_scraper import CodeforcesAnalyzer
from .hackerrank_scraper import HackerRankAnalyzer
from .portfolio_scraper import PortfolioAnalyzer
from .stackoverflow_scraper import StackOverflowAnalyzer
from .kaggle_scraper import KaggleAnalyzer
from .devto_scraper import DevToAnalyzer
from .geeksforgeeks_scraper import GeeksforGeeksAnalyzer
from .hackerearth_scraper import HackerEarthAnalyzer
from .bitbucket_scraper import BitbucketAnalyzer
from .gitlab_scraper import GitLabAnalyzer
from .leetcode_stats_scraper import LeetCodeStatsAnalyzer

# Register platform-specific analyzers (order matters - more specific first)
link_orchestrator.register_analyzer(GithubAnalyzer())       # GitHub
link_orchestrator.register_analyzer(LinkedInAnalyzer())     # LinkedIn
link_orchestrator.register_analyzer(GitLabAnalyzer())        # GitLab
link_orchestrator.register_analyzer(BitbucketAnalyzer())    # Bitbucket
link_orchestrator.register_analyzer(LeetCodeAnalyzer())     # LeetCode
link_orchestrator.register_analyzer(CodeforcesAnalyzer())    # Codeforces
link_orchestrator.register_analyzer(StackOverflowAnalyzer()) # Stack Overflow
link_orchestrator.register_analyzer(HackerRankAnalyzer())   # HackerRank
link_orchestrator.register_analyzer(HackerEarthAnalyzer())  # HackerEarth
link_orchestrator.register_analyzer(KaggleAnalyzer())      # Kaggle
link_orchestrator.register_analyzer(GeeksforGeeksAnalyzer()) # GeeksforGeeks
link_orchestrator.register_analyzer(DevToAnalyzer())         # Dev.to
# PortfolioAnalyzer is handled as a fallback in the orchestrator itself

__all__ = ["link_orchestrator"]