"""
Section-anchored chunking with font-size hierarchy.

Groups Docling ContentBlocks into chunks, using font-size data to distinguish
top-level section headers (PROJECTS, EDUCATION, SKILLS) from sub-item titles
(individual project names, school names) that should remain grouped under
their parent section.

Each chunk carries font_size and font_weight metadata so the embedding
pipeline can persist this information in the vector store.
"""

import logging
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from app.core.extraction import ContentBlock

logger = logging.getLogger(__name__)

# Max characters per chunk (approx. 200-300 tokens)
MAX_CHUNK_CHARS = 1000

# If a heading's font_size is below (median_heading_size - this margin),
# it is treated as a sub-item, not a new section.
SECTION_MARGIN = 1.5


@dataclass
class EnrichedChunk:
    """A semantic chunk ready for embedding and indexing."""
    raw_text: str
    section_label: str
    chunk_index: int
    metadata: Dict[str, Any]


def _compute_section_font_threshold(blocks: List[ContentBlock]) -> float:
    """
    Compute the font-size threshold that separates top-level section headers
    from sub-item headings (e.g. project titles).

    Strategy:
      - Collect font sizes of all heading/subheading blocks.
      - Compute the median.  Top-level sections in resumes are typically
        rendered at the same size (e.g. 13.2pt) while sub-items are smaller
        (e.g. 10.3pt).  The threshold = median - SECTION_MARGIN catches this.
    """
    heading_sizes = [
        b.font_size
        for b in blocks
        if b.block_type in ("heading", "subheading") and b.font_size > 0
    ]

    if not heading_sizes:
        return 0.0

    median = statistics.median(heading_sizes)
    threshold = median - SECTION_MARGIN
    logger.debug(
        f"Heading font sizes: {sorted(heading_sizes)}, "
        f"median={median:.1f}, section threshold={threshold:.1f}"
    )
    return threshold


def chunk_content_blocks(
    blocks: List[ContentBlock],
) -> Tuple[List[EnrichedChunk], Dict[str, str]]:
    """
    Process ordered ContentBlocks into semantic, section-anchored chunks,
    and simultaneously assemble the full text per section for the structured store.

    Font-size hierarchy logic:
      - A heading/subheading whose font_size >= threshold starts a NEW section.
      - A heading/subheading whose font_size <  threshold is a sub-item title
        and stays inside the current section (like a project name under PROJECTS).
    """
    chunks: List[EnrichedChunk] = []
    sections_dict: Dict[str, str] = {}

    current_section = "Summary"  # Default section if no heading appears first
    current_chunk_text = ""
    current_section_full_text: List[str] = []

    # Track per-chunk font metadata
    chunk_font_sizes: List[float] = []
    chunk_has_bold = False

    chunk_idx = 0

    # Compute the font-size threshold that separates real sections from sub-items
    section_threshold = _compute_section_font_threshold(blocks)

    def finalize_chunk(text: str, section: str):
        nonlocal chunk_idx, chunk_font_sizes, chunk_has_bold
        if not text.strip():
            chunk_font_sizes = []
            chunk_has_bold = False
            return

        # If it's not a heading chunk, prepend the section label for context
        if not text.lower().startswith(section.lower()):
            contextual_text = f"{section}: {text.strip()}"
        else:
            contextual_text = text.strip()

        # Compute average font size for this chunk's blocks
        avg_font = (
            round(statistics.mean(chunk_font_sizes), 1)
            if chunk_font_sizes
            else 0.0
        )

        chunks.append(EnrichedChunk(
            raw_text=contextual_text,
            section_label=section.lower(),
            chunk_index=chunk_idx,
            metadata={
                "section": section.lower(),
                "chunk_index": chunk_idx,
                "avg_font_size": avg_font,
                "has_bold": chunk_has_bold,
            }
        ))
        chunk_idx += 1
        chunk_font_sizes = []
        chunk_has_bold = False

    for block in blocks:
        text = block.raw_text.strip()
        if not text:
            continue

        # Track font metadata for every block we consume
        chunk_font_sizes.append(block.font_size)
        if block.text_weight == "bold":
            chunk_has_bold = True

        # Detect section boundary —
        # ONLY if the heading's font is large enough to be a real section header.
        is_heading = block.block_type in ("heading", "subheading")
        is_section_level = block.font_size >= section_threshold

        if is_heading and is_section_level:
            # ---------- NEW SECTION ----------
            # Finalize previous chunk and section
            finalize_chunk(current_chunk_text, current_section)
            current_chunk_text = ""

            if current_section_full_text:
                sections_dict[current_section.lower()] = "\n".join(
                    current_section_full_text
                ).strip()
                current_section_full_text = []

            # Start new section
            clean_heading = text.replace('\n', ' ').strip(': ')
            current_section = clean_heading if len(clean_heading) > 2 else current_section

            # Start the new chunk with the heading itself
            current_chunk_text = text
            current_section_full_text.append(text)

        elif is_heading and not is_section_level:
            # ---------- SUB-ITEM TITLE (e.g. project name) ----------
            # Keep it inside the current section as content, not a new section
            current_section_full_text.append(text)

            if len(current_chunk_text) + len(text) > MAX_CHUNK_CHARS and current_chunk_text:
                finalize_chunk(current_chunk_text, current_section)
                current_chunk_text = text
            else:
                current_chunk_text = f"{current_chunk_text}\n{text}" if current_chunk_text else text

        else:
            # ---------- BODY / LIST ITEM ----------
            current_section_full_text.append(text)

            if len(current_chunk_text) + len(text) > MAX_CHUNK_CHARS and current_chunk_text:
                finalize_chunk(current_chunk_text, current_section)
                current_chunk_text = text
            else:
                current_chunk_text = f"{current_chunk_text}\n{text}" if current_chunk_text else text

    # Finalize the last chunk and section
    finalize_chunk(current_chunk_text, current_section)
    if current_section_full_text:
        sections_dict[current_section.lower()] = "\n".join(
            current_section_full_text
        ).strip()

    logger.info(
        f"Chunking complete: {len(chunks)} chunks across {len(sections_dict)} sections "
        f"(section font threshold: {section_threshold:.1f}pt)"
    )

    return chunks, sections_dict
