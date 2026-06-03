"""
Kaggle profile scraper using Playwright + Kaggle API
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class KaggleAnalyzer(LinkAnalyzerBase):
    """Scraper for Kaggle profiles"""

    def __init__(self):
        super().__init__("Kaggle")

    def can_handle(self, url: str) -> bool:
        return "kaggle.com" in url.lower() and "/" in url

    def extract_username(self, url: str) -> Optional[str]:
        # Kaggle URLs: kaggle.com/{username}
        match = re.search(r'kaggle\.com/([^/?]+)', url)
        if match:
            username = match.group(1)
            # Skip if it's a generic kaggle path
            if username in ['users', 'competitions', 'datasets', 'notebooks', 'courses']:
                return None
            return username
        return None

    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(
                platform=self.platform_name,
                valid_link=False,
                error="Invalid Kaggle URL"
            )

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Try to go to the profile page
                await page.goto(f"https://www.kaggle.com/{username}",
                              wait_until="domcontentloaded",
                              timeout=15000)

                # Check if page loaded properly
                title = await page.title()
                if "404" in title or "Page Not Found" in title:
                    await browser.close()
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error="User not found"
                    )

                # Extract metrics from the page
                metrics = {}

                try:
                    # Look for competition participation
                    comp_selector = "[data-testid='competition-count'], .competition-count, a[href*='competitions']"
                    comp_element = await page.query_selector(comp_selector)
                    if comp_element:
                        comp_text = await comp_element.text_content()
                        metrics["competitions"] = comp_text.strip() if comp_text else "0"
                except Exception as e:
                    logger.debug(f"Failed to scrape Kaggle competitions from {url}: {e}")

                try:
                    # Look for datasets
                    dataset_selector = "[data-testid='dataset-count'], .dataset-count"
                    dataset_element = await page.query_selector(dataset_selector)
                    if dataset_element:
                        dataset_text = await dataset_element.text_content()
                        metrics["datasets"] = dataset_text.strip() if dataset_text else "0"
                except Exception as e:
                    logger.debug(f"Failed to scrape Kaggle datasets from {url}: {e}")

                try:
                    # Look for notebooks
                    notebook_selector = "[data-testid='notebook-count'], .notebook-count"
                    notebook_element = await page.query_selector(notebook_selector)
                    if notebook_element:
                        notebook_text = await notebook_element.text_content()
                        metrics["notebooks"] = notebook_text.strip() if notebook_text else "0"
                except Exception as e:
                    logger.debug(f"Failed to scrape Kaggle notebooks from {url}: {e}")

                try:
                    # Look for followers
                    follower_selector = "[data-testid='follower-count'], .follower-count"
                    follower_element = await page.query_selector(follower_selector)
                    if follower_element:
                        follower_text = await follower_element.text_content()
                        metrics["followers"] = follower_text.strip() if follower_text else "0"
                except Exception as e:
                    logger.debug(f"Failed to scrape Kaggle followers from {url}: {e}")

                # Try to get bio/description
                try:
                    bio_selector = ".profile-bio, [data-testid='bio'], .bio"
                    bio_element = await page.query_selector(bio_selector)
                    if bio_element:
                        bio_text = await bio_element.text_content()
                        metrics["bio"] = bio_text.strip()[:200] if bio_text else ""
                except Exception as e:
                    logger.debug(f"Failed to scrape Kaggle bio from {url}: {e}")

                await browser.close()

                # If no metrics found, try alternative approach using Kaggle API approach
                if not metrics:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=True,
                        error="Could not extract detailed metrics",
                        metrics={"note": "Profile exists but metrics unavailable"}
                    )

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
                error="Playwright not installed",
                metrics={}
            )
        except Exception as e:
            logger.error(f"Kaggle scrape failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )