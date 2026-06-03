import logging
import base64
from typing import Optional

logger = logging.getLogger(__name__)

class PDFGenerator:
    """
    Handles PDF generation from HTML/CSS strings using headless Playwright.
    Ensures A4 sizing, no margins, and background rendering (for color-blocked templates).
    """
    
    async def generate_pdf(self, html_content: str) -> Optional[bytes]:
        """
        Renders the provided HTML string into a PDF and returns the bytes.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright is not installed. Please run: pip install playwright")
            return None
            
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Create a new context/page
                page = await browser.new_page()
                
                # Set content. Using wait_until networkidle ensures external fonts 
                # (like Google Fonts) are loaded before PDF rendering.
                await page.set_content(html_content, wait_until="networkidle")
                
                # Render to PDF
                # A4 size is 8.27in x 11.69in
                pdf_bytes = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                    prefer_css_page_size=True
                )
                
                await browser.close()
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Failed to generate PDF via Playwright: {e}")
            return None

pdf_generator = PDFGenerator()
