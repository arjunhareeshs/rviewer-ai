"""
PDF-to-Image converter using PyMuPDF (fitz).

Converts each page of a PDF into a base64-encoded PNG image suitable
for sending to a Vision Language Model.
"""

import base64
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def pdf_to_base64_images(file_path: str, dpi: int = 200) -> List[str]:
    """
    Convert a PDF file into a list of base64-encoded PNG images.
    Stitches multiple pages vertically into a single image to bypass VLM 1-image limits.
    """
    import fitz  # PyMuPDF
    from PIL import Image
    import io

    doc = fitz.open(file_path)

    zoom = dpi / 72  # 72 is the default DPI for PDF
    matrix = fitz.Matrix(zoom, zoom)
    
    pil_images = []
    total_height = 0
    max_width = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=matrix)
        png_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(png_bytes))
        
        # Ensure RGB format
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        pil_images.append(img)
        total_height += img.height
        max_width = max(max_width, img.width)
        logger.info(f"Converted page {page_num + 1}/{len(doc)} to image ({len(png_bytes)} bytes)")

    doc.close()
    
    if not pil_images:
        logger.warning(f"No pages found in PDF: {file_path}")
        return []

    # Stitch vertically
    stitched = Image.new('RGB', (max_width, total_height), (255, 255, 255))
    y_offset = 0
    for img in pil_images:
        stitched.paste(img, (0, y_offset))
        y_offset += img.height

    # Scale down if it exceeds NVIDIA NIM max dimension (1120)
    MAX_DIM = 1120
    if stitched.width > MAX_DIM or stitched.height > MAX_DIM:
        ratio = min(MAX_DIM / stitched.width, MAX_DIM / stitched.height)
        new_size = (int(stitched.width * ratio), int(stitched.height * ratio))
        stitched = stitched.resize(new_size, Image.Resampling.LANCZOS)
        logger.info(f"Resized stitched image to {stitched.width}x{stitched.height} to fit NVIDIA NIM limits")
        
    buffer = io.BytesIO()
    stitched.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    logger.info(f"PDF converted and stitched: {len(pil_images)} pages into 1 image")
    return [b64]
