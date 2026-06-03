"""
HackerEarth profile scraper using Playwright
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class HackerEarthAnalyzer(LinkAnalyzerBase):
    """Scraper for HackerEarth profiles"""

    def __init__(self):
        super().__init__("HackerEarth")

    def can_handle(self, url: str) -> bool:
        return "hackerearth.com" in url.lower()

    def extract_username(self, url: str) -> Optional[str]:
        # HackerEarth URLs: hackerearth.com/@{username}
        match = re.search(r'hackerearth\.com/@([^/?]+)', url)
        if match:
            return match.group(1)
        return None

    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(
                platform=self.platform_name,
                valid_link=False,
                error="Invalid HackerEarth URL"
            )

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(f"https://www.hackerearth.com/@{username}",
                              wait_until="domcontentloaded",
                              timeout=15000)

                # Check for 404
                title = await page.title()
                if "404" in title or "Page Not Found" in title:
                    await browser.close()
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=False,
                        error="User not found"
                    )

                metrics = {}

                # Extract points/reputation
                try:
                    points_selectors = [
                        ".points",
                        "[class*='points']",
                        ".reputation",
                        "[class*='score']",
                    ]
                    for selector in points_selectors:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.text_content()
                            if text and any(c.isdigit() for c in text):
                                metrics["points"] = text.strip()
                                break
                except Exception as e:
                    logger.debug(f"Failed to scrape HackerEarth points: {e}")

                # Extract skills
                try:
                    skill_elements = await page.query_selector_all("[class*='skill'], .skill-name")
                    skills = []
                    for elem in skill_elements[:10]:
                        text = await elem.text_content()
                        if text and len(text) < 40:
                            skills.append(text.strip())
                    if skills:
                        metrics["skills"] = skills
                except Exception as e:
                    logger.debug(f"Failed to scrape HackerEarth skills: {e}")

                # Extract badges
                try:
                    badge_elements = await page.query_selector_all("[class*='badge']")
                    metrics["badge_count"] = len(badge_elements)
                except Exception as e:
                    logger.debug(f"Failed to scrape HackerEarth badges: {e}")

                # Extract location
                try:
                    location_element = await page.query_selector("[class*='location']")
                    if location_element:
                        location_text = await location_element.text_content()
                        metrics["location"] = location_text.strip() if location_text else ""
                except Exception as e:
                    logger.debug(f"Failed to scrape HackerEarth location: {e}")

                # Extract company/college
                try:
                    org_element = await page.query_selector("[class*='organization'], [class*='company']")
                    if org_element:
                        org_text = await org_element.text_content()
                        metrics["organization"] = org_text.strip() if org_text else ""
                except Exception as e:
                    logger.debug(f"Failed to scrape HackerEarth organization: {e}")

                await browser.close()

                if not metrics:
                    return LinkPlatformData(
                        platform=self.platform_name,
                        username=username,
                        valid_link=True,
                        error="Could not extract detailed metrics",
                        metrics={"note": "Profile exists but limited data"}
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
            logger.error(f"HackerEarth scrape failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )