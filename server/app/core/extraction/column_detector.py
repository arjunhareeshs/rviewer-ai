"""
Column detector — reorders ContentBlocks based on spatial layout analysis.

Uses bounding box data from Docling to detect column count and reorder
blocks column-by-column, top-to-bottom. This ensures multi-column resumes
are read in the correct natural order instead of line-by-line across columns.

This is a purely internal pipeline operation — column layout metadata
is never surfaced to the frontend.
"""

import logging
from typing import List
from app.core.extraction import ContentBlock

logger = logging.getLogger(__name__)

# Horizontal overlap threshold to consider two blocks in the same column
COLUMN_GAP_THRESHOLD = 0.3  # 30% of page width


def reorder_by_columns(blocks: List[ContentBlock]) -> List[ContentBlock]:
    """
    Analyze bounding boxes and reorder blocks by column (left-to-right),
    then by vertical position (top-to-bottom) within each column.

    If no bounding box data is available, returns blocks in original order.
    """
    # Separate blocks with and without bbox
    blocks_with_bbox = []
    blocks_without_bbox = []

    for block in blocks:
        bbox = getattr(block, "_bbox", None)
        if bbox is not None:
            blocks_with_bbox.append(block)
        else:
            blocks_without_bbox.append(block)

    # If no bbox data, return original order
    if not blocks_with_bbox:
        logger.debug("No bounding box data available — using original reading order")
        return blocks

    # Extract x-coordinates to detect columns
    columns = _detect_columns(blocks_with_bbox)

    if len(columns) <= 1:
        logger.debug("Single column layout detected — no reordering needed")
        return blocks

    logger.info(f"Multi-column layout detected: {len(columns)} columns")

    # Reorder: process columns left-to-right, blocks top-to-bottom within each column
    reordered: List[ContentBlock] = []
    for col_blocks in columns:
        # Sort by vertical position (descending = top to bottom in PDF coordinates where Y is bottom-up)
        col_blocks.sort(key=lambda b: _get_top(b), reverse=True)
        reordered.extend(col_blocks)

    # Append any blocks without bbox at the end
    reordered.extend(blocks_without_bbox)

    return reordered


def _detect_columns(blocks: List[ContentBlock]) -> List[List[ContentBlock]]:
    """
    Cluster blocks into columns based on their horizontal (x) position.

    Strategy:
    1. Collect the left-edge x-coordinate of each block's bbox
    2. Sort unique x-positions and cluster them if they're within threshold
    3. Assign each block to its column cluster
    4. Sort columns by their average x-position (left to right)
    """
    if not blocks:
        return []

    # Get x-positions (left edge of each block)
    x_positions = []
    for block in blocks:
        left_x = _get_left(block)
        if left_x is not None:
            x_positions.append(left_x)

    if not x_positions:
        return [blocks]

    # Estimate page width from the data
    min_x = min(x_positions)
    max_x = max(x_positions)
    page_width = max_x - min_x if max_x > min_x else 1.0
    gap = page_width * COLUMN_GAP_THRESHOLD

    # Sort unique x-positions and cluster
    sorted_xs = sorted(set(x_positions))
    column_centers: List[float] = [sorted_xs[0]]

    for x in sorted_xs[1:]:
        # If this x is far from all existing column centers, start a new column
        if all(abs(x - center) > gap for center in column_centers):
            column_centers.append(x)

    # Assign blocks to nearest column
    columns: List[List[ContentBlock]] = [[] for _ in column_centers]

    for block in blocks:
        left_x = _get_left(block)
        if left_x is None:
            columns[0].append(block)
            continue

        # Find nearest column center
        min_dist = float("inf")
        best_col = 0
        for i, center in enumerate(column_centers):
            dist = abs(left_x - center)
            if dist < min_dist:
                min_dist = dist
                best_col = i
        columns[best_col].append(block)

    # Sort columns by their center x-position (left to right)
    paired = list(zip(column_centers, columns))
    paired.sort(key=lambda p: p[0])
    return [col for _, col in paired]


def _get_left(block: ContentBlock) -> float | None:
    """Get the left x-coordinate from a block's bbox."""
    bbox = getattr(block, "_bbox", None)
    if bbox is None:
        return None
    # Docling bbox can be BoundingBox object or dict/list
    if hasattr(bbox, "l"):
        return float(bbox.l)
    if hasattr(bbox, "x"):
        return float(bbox.x)
    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
        return float(bbox[0])
    if isinstance(bbox, dict):
        return float(bbox.get("l", bbox.get("x", bbox.get("x0", 0))))
    return None


def _get_top(block: ContentBlock) -> float:
    """Get the top y-coordinate from a block's bbox (for vertical sorting)."""
    bbox = getattr(block, "_bbox", None)
    if bbox is None:
        return float(getattr(block, "reading_order_index", 0))
    if hasattr(bbox, "t"):
        return float(bbox.t)
    if hasattr(bbox, "y"):
        return float(bbox.y)
    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
        return float(bbox[1])
    if isinstance(bbox, dict):
        return float(bbox.get("t", bbox.get("y", bbox.get("y0", 0))))
    return 0.0
