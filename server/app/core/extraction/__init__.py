"""
Extraction dispatcher — routes resume files to the correct extraction pipeline
based on file type: PDF → Docling, Image → VLM.
"""

import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContentBlock:
    """Single content block extracted by Docling from a PDF.
    This is an internal pipeline data structure — never surfaced to the frontend.
    """
    block_type: str          # heading | subheading | body | list_item | label
    font_size: float
    text_weight: str         # bold | normal
    reading_order_index: int
    raw_text: str


@dataclass
class ExtractionResult:
    """Unified result from either PDF or Image extraction pipeline."""
    method: str              # "docling" | "vlm"
    raw_text: str            # Full concatenated text
    content_blocks: Optional[List[ContentBlock]] = None  # PDF path only
    sections: Optional[Dict[str, str]] = None            # Both paths (VLM provides directly)
    metadata: Dict = field(default_factory=dict)


SUPPORTED_PDF_EXTENSIONS = {".pdf"}
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def detect_file_type(file_path: str) -> str:
    """Determine if file is PDF or Image based on extension."""
    ext = Path(file_path).suffix.lower()
    if ext in SUPPORTED_PDF_EXTENSIONS:
        return "pdf"
    elif ext in SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


async def extract_resume(file_path: str) -> ExtractionResult:
    """
    Main dispatcher: routes to VLM or Docling extraction based on configuration.

    VLM path:   file → VLM (PDF/Image) → section-wise JSON → structured store
    Docling path: file → Docling (PDF) → ContentBlocks → chunking → vector DB
    """
    from app.config import get_settings
    settings = get_settings()

    file_type = detect_file_type(file_path)
    extraction_method = settings.EXTRACTION_METHOD.lower()

    if extraction_method == "auto":
        if file_type == "pdf":
            logger.info(f"Auto extraction path selected (PDF) — routing to Docling: {file_path}")
            from app.core.extraction.docling_extractor import extract_pdf
            return await extract_pdf(file_path)
        else:
            logger.info(f"Auto extraction path selected (Image) — routing to VLM: {file_path}")
            from app.core.extraction.vlm_extractor import extract_image
            return await extract_image(file_path)

    if extraction_method == "vlm":
        logger.info(f"Forced extraction path selected — routing to VLM extractor: {file_path}")
        from app.core.extraction.vlm_extractor import extract_resume_vlm
        return await extract_resume_vlm(file_path)
        
    if extraction_method == "docling":
        logger.info(f"Forced extraction path selected — routing to Docling extractor: {file_path}")
        from app.core.extraction.docling_extractor import extract_pdf
        return await extract_pdf(file_path)

    raise ValueError(f"Cannot extract: unsupported extraction method '{extraction_method}' or file type '{file_type}'")
