"""
Visualization data generator for link analysis results
Generates data structures for frontend charts and heatmaps
"""
from typing import List, Dict, Any, Optional
from app.core.analysis.schemas import LinkPlatformData, LinkAnalysisResult


class LinkVisualizationGenerator:
    """Generates visualization data from link analysis results"""

    def generate_activity_heatmap(self, platforms: List[LinkPlatformData]) -> List[List[int]]:
        """
        Generate GitHub-style activity heatmap data
        Returns: 52 weeks x 7 days matrix (0-10 scale per cell)
        """
        heatmap = [[0 for _ in range(7)] for _ in range(52)]

        for platform in platforms:
            if not platform.valid_link or not platform.metrics:
                continue

            activity_data = platform.activity_data

            # GitHub-style contribution data
            if platform.platform == "GitHub" and activity_data:
                contributions = activity_data.get("contributions", [])
                for i, val in enumerate(contributions[:364]):
                    week = i // 7
                    day = i % 7
                    if week < 52:
                        heatmap[week][day] += min(10, val // 10)

            # LeetCode submissions by day (mock data structure)
            elif platform.platform == "LeetCode":
                problems = platform.metrics.get("problems_solved", {})
                # Map difficulty to activity levels
                for difficulty, count in problems.items():
                    activity_level = min(10, count // 5)
                    # Distribute across the year
                    for _ in range(count):
                        week_idx = (hash(difficulty) % 52 + _) % 52
                        day_idx = _ % 7
                        heatmap[week_idx][day_idx] += activity_level

        return heatmap

    def generate_skill_radar(self, platforms: List[LinkPlatformData]) -> Dict[str, float]:
        """
        Generate skill radar chart data from platform data
        Returns: Dict of skill category -> score (0-100)
        """
        radar_data = {
            "Programming": 0,
            "Data Science": 0,
            "Web Dev": 0,
            "Mobile": 0,
            "DevOps": 0,
            "System Design": 0,
        }

        skill_weights = {
            "GitHub": {"Programming": 30, "System Design": 20},
            "LeetCode": {"Programming": 40, "System Design": 10},
            "Codeforces": {"Programming": 40, "System Design": 10},
            "Stack Overflow": {"Programming": 20, "Web Dev": 15},
            "Kaggle": {"Data Science": 40},
            "GeeksforGeeks": {"Programming": 20},
            "HackerRank": {"Programming": 15, "DevOps": 10},
            "HackerEarth": {"Programming": 15},
        }

        for platform in platforms:
            if not platform.valid_link:
                continue

            platform_name = platform.platform
            weights = skill_weights.get(platform_name, {})

            # Calculate score based on metrics
            score_boost = 0
            if platform.metrics:
                # Base score on presence
                score_boost = 50
                # Add more for significant activity
                for metric_key, metric_value in platform.metrics.items():
                    if isinstance(metric_value, int) and metric_value > 0:
                        score_boost += min(10, metric_value // 10)

            for skill, weight in weights.items():
                if skill in radar_data:
                    radar_data[skill] += score_boost * weight // 30

        # Normalize to 0-100
        for key in radar_data:
            radar_data[key] = min(100, radar_data[key])

        return radar_data

    def generate_engagement_bars(self, platforms: List[LinkPlatformData]) -> Dict[str, int]:
        """
        Generate engagement bar chart data
        Returns: Dict of platform -> engagement score (0-100)
        """
        engagement = {}

        # Engagement scoring based on platform and metrics
        platform_engagement_config = {
            "GitHub": {"repos": 10, "followers": 5, "stars": 2},
            "LeetCode": {"total_solved": 5, "ranking": -1},  # Lower ranking is better
            "Codeforces": {"rating": 2},
            "Stack Overflow": {"reputation": 1},
            "Kaggle": {"datasets": 10, "competitions": 15, "notebooks": 5},
            "HackerRank": {"score": 2},
            "HackerEarth": {"points": 2},
            "GeeksforGeeks": {"problems_solved": 3},
            "Dev.to": {"article_count": 10},
            "GitLab": {"public_repos": 10},
            "Bitbucket": {"repo_count": 10},
        }

        for platform in platforms:
            if not platform.valid_link or not platform.metrics:
                engagement[platform.platform] = 0
                continue

            score = 0
            config = platform_engagement_config.get(platform.platform, {})

            for metric_key, weight in config.items():
                value = platform.metrics.get(metric_key, 0)
                if isinstance(value, (int, float)):
                    if weight < 0:  # Negative weight means lower is better
                        if value > 0:
                            score += max(0, 100 - value // weight)
                    else:
                        score += value * weight

            engagement[platform.platform] = min(100, score)

        return engagement

    def generate_recency_timeline(self, platforms: List[LinkPlatformData]) -> List[Dict[str, Any]]:
        """
        Generate recency timeline for all platforms
        Returns: List of {platform, last_active, days_ago, status}
        """
        from datetime import datetime, timedelta

        timeline = []
        now = datetime.utcnow()

        for platform in platforms:
            last_active = None

            # Try to find last active date from various metrics
            if platform.activity_data:
                last_active = platform.activity_data.get("last_active")

            # Calculate days ago
            days_ago = None
            if last_active:
                try:
                    if isinstance(last_active, str):
                        last_active_dt = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
                    else:
                        last_active_dt = last_active
                    days_ago = (now - last_active_dt).days
                except Exception:
                    days_ago = None
            else:
                # If no activity data, assume "unknown" but profile is valid
                days_ago = -1  # -1 means unknown

            status = "active"
            if days_ago is not None and days_ago >= 0:
                if days_ago <= 7:
                    status = "active"
                elif days_ago <= 30:
                    status = "recent"
                elif days_ago <= 90:
                    status = "less_active"
                else:
                    status = "inactive"
            elif days_ago == -1:
                status = "unknown"

            timeline.append({
                "platform": platform.platform,
                "username": platform.username,
                "last_active_days_ago": days_ago,
                "status": status
            })

        return timeline

    def generate_all_viz(self, link_result: LinkAnalysisResult) -> Dict[str, Any]:
        """Generate all visualization data at once"""
        platforms = link_result.platforms

        return {
            "activity_heatmap": self.generate_activity_heatmap(platforms),
            "skill_radar": self.generate_skill_radar(platforms),
            "engagement_bars": self.generate_engagement_bars(platforms),
            "recency_timeline": self.generate_recency_timeline(platforms),
        }


# Singleton instance
link_viz_generator = LinkVisualizationGenerator()