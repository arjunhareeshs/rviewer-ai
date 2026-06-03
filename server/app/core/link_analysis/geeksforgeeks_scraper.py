"""
GeeksforGeeks profile scraper using Playwright
"""
import re
import logging
from typing import Optional, Dict, Any
from .analyzer import LinkAnalyzerBase
from app.core.analysis.schemas import LinkPlatformData

logger = logging.getLogger(__name__)

class GeeksforGeeksAnalyzer(LinkAnalyzerBase):
    """Scraper for GeeksforGeeks profiles"""

    def __init__(self):
        super().__init__("GeeksforGeeks")

    def can_handle(self, url: str) -> bool:
        return "geeksforgeeks.org" in url.lower()

    def extract_username(self, url: str) -> Optional[str]:
        # GfG URLs: geeksforgeeks.org/user/{username}
        match = re.search(r'geeksforgeeks\.org/user/([^/?]+)', url)
        if match:
            return match.group(1)
        # Alternative: practice.geeksforgeeks.org/user/{username}
        match = re.search(r'practice\.geeksforgeeks\.org/user/([^/?]+)', url)
        if match:
            return match.group(1)
        return None

    async def extract(self, url: str) -> LinkPlatformData:
        username = self.extract_username(url)
        if not username:
            return LinkPlatformData(
                platform=self.platform_name,
                valid_link=False,
                error="Invalid GeeksforGeeks URL"
            )

        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Try main site first, then practice
                try:
                    await page.goto(f"https://auth.geeksforgeeks.org/user/{username}",
                                  wait_until="domcontentloaded",
                                  timeout=15000)
                except Exception as e:
                    logger.debug(f"Main site lookup failed, trying practice site: {e}")
                    await page.goto(f"https://practice.geeksforgeeks.org/user/{username}",
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

                # Extract problem solved count
                try:
                    # Look for problem solved section
                    problem_selectors = [
                        ".problems_solved a",
                        "[class*='problem'] a",
                        ".section_problems_solved",
                    ]
                    for selector in problem_selectors:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.text_content()
                            if text and any(c.isdigit() for c in text):
                                metrics["problems_solved"] = text.strip()
                                break
                except Exception as e:
                    logger.debug(f"Failed to scrape GfG problems solved: {e}")

                # Extract coding score/rank
                try:
                    score_selectors = [
                        "[class*='score']",
                        ".coding-score",
                        "[class*='rank']",
                    ]
                    for selector in score_selectors:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.text_content()
                            if text:
                                metrics["coding_score"] = text.strip()
                                break
                except Exception as e:
                    logger.debug(f"Failed to scrape GfG coding score: {e}")

                # Extract institute/college if shown
                try:
                    institute_element = await page.query_selector("[class*='institute']")
                    if institute_element:
                        institute_text = await institute_element.text_content()
                        metrics["institute"] = institute_text.strip() if institute_text else ""
                except Exception as e:
                    logger.debug(f"Failed to scrape GfG institute: {e}")

                # Extract language proficiency
                try:
                    lang_elements = await page.query_selector_all("[class*='language']")
                    languages = []
                    for elem in lang_elements[:5]:
                        text = await elem.text_content()
                        if text and len(text) < 30:
                            languages.append(text.strip())
                    if languages:
                        metrics["languages"] = languages
                except Exception as e:
                    logger.debug(f"Failed to scrape GfG languages: {e}")

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
            logger.error(f"GeeksforGeeks scrape failed: {e}")
            return LinkPlatformData(
                platform=self.platform_name,
                username=username,
                valid_link=False,
                error=str(e)
            )