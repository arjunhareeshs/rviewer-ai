"""
Docling-based PDF extraction with layout-aware column detection.

Docling detects document structure: columns, bounding boxes, reading order,
and block types. All structural metadata is pipeline-internal — none of it
is surfaced to the frontend.

Output: ordered list of ContentBlocks tagged with block_type, font_size,
text_weight, and reading_order_index.
"""

import logging
from typing import List

from app.core.extraction import ContentBlock, ExtractionResult
from app.core.extraction.column_detector import reorder_by_columns
from app.core.extraction.text_cleaner import clean_text

logger = logging.getLogger(__name__)


async def extract_pdf(file_path: str) -> ExtractionResult:
    """
    Run Docling on a PDF file and return structured ContentBlocks.

    Pipeline:
      1. Docling parses the PDF → document structure with layout info
      2. Column detector reorders blocks for correct reading flow
      3. Text cleaner normalizes each block's raw_text
      4. Blocks are mapped to ContentBlock dataclass instances
    """
    try:
        # Lazy import so Docling is only loaded when needed
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import PdfFormatOption
        from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

        logger.info(f"Starting Docling extraction for: {file_path}")

        # Initialize Docling converter with PDF pipeline
        converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_cls=StandardPdfPipeline)
            }
        )

        # Parse the document
        result = converter.convert(file_path)
        doc = result.document

        # Extract content blocks from Docling's document model
        raw_blocks: List[ContentBlock] = []
        order_index = 0

        for element in doc.texts:
            text = ""
            block_type = "body"
            font_size = 11.0
            text_weight = "normal"

            # Extract text content
            if hasattr(element, "text"):
                text = element.text

            if not text or not text.strip():
                continue

            # Determine block type from Docling's label
            label = ""
            if hasattr(element, "label"):
                label = str(element.label).lower()

            if "heading" in label or "title" in label:
                block_type = "heading"
                font_size = 14.0
                text_weight = "bold"
            elif "section" in label:
                block_type = "subheading"
                font_size = 12.0
                text_weight = "bold"
            elif "list" in label:
                block_type = "list_item"
            elif "caption" in label or "label" in label:
                block_type = "label"
            else:
                block_type = "body"

            # Extract bounding box info if available (used by column_detector)
            bbox = None
            if hasattr(element, "prov") and element.prov:
                prov = element.prov[0] if isinstance(element.prov, list) else element.prov
                if hasattr(prov, "bbox"):
                    bbox = prov.bbox

            # Calculate font size from bounding box height (metadata only).
            # We do NOT override block_type here — Docling's label is the
            # authoritative source for structural classification.  The bbox
            # height is unreliable for classification because it includes
            # padding/margins and varies wildly across PDFs.
            if bbox:
                t = getattr(bbox, "t", getattr(bbox, "y", getattr(bbox, "y1", 0)))
                b = getattr(bbox, "b", getattr(bbox, "y0", 0))
                height = abs(t - b)
                if height > 0:
                    # Normalize by number of text lines
                    num_lines = max(1, text.count("\n") + 1)
                    font_size = round(height / num_lines, 1)

            # Detect symbols for lists
            stripped_text = text.strip()
            if stripped_text.startswith("•") or stripped_text.startswith("-") or stripped_text.startswith("▪") or stripped_text.startswith("*"):
                block_type = "list_item"

            block = ContentBlock(
                block_type=block_type,
                font_size=font_size,
                text_weight=text_weight,
                reading_order_index=order_index,
                raw_text=clean_text(text),
            )
            # Attach bbox as a transient attribute for column_detector
            block._bbox = bbox  # type: ignore[attr-defined]
            raw_blocks.append(block)
            order_index += 1

        logger.info(f"Docling extracted {len(raw_blocks)} content blocks")

        # Reorder blocks by column layout (left-to-right, top-to-bottom)
        ordered_blocks = reorder_by_columns(raw_blocks)

        # Reassign reading_order_index after reordering
        for i, block in enumerate(ordered_blocks):
            block.reading_order_index = i

        # Build full raw text
        raw_text = "\n".join(b.raw_text for b in ordered_blocks)

        logger.info(f"PDF extraction complete: {len(ordered_blocks)} blocks, {len(raw_text)} chars")

        return ExtractionResult(
            method="docling",
            raw_text=raw_text,
            content_blocks=ordered_blocks,
            sections=None,  # Sections are built downstream by the chunker
            metadata={
                "total_blocks": len(ordered_blocks),
                "total_chars": len(raw_text),
                "block_types": _count_block_types(ordered_blocks),
            }
        )

    except ImportError as e:
        logger.error(f"Docling is not installed: {e}")
        raise ImportError(
            "Docling is required for PDF extraction. "
            "Install it with: pip install docling"
        ) from e
    except Exception as e:
        logger.error(f"Docling extraction failed for {file_path}: {e}")
        raise


def _count_block_types(blocks: List[ContentBlock]) -> dict:
    """Count occurrences of each block type for metadata."""
    counts: dict = {}
    for b in blocks:
        counts[b.block_type] = counts.get(b.block_type, 0) + 1
    return counts
