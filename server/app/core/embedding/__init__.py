"""
Embedding layer initialization.
Exposes chunking and embedding operations for the PDF pipeline.
"""

from app.core.embedding.chunker import chunk_content_blocks
from app.core.embedding.embedder import embed_chunks

__all__ = ["chunk_content_blocks", "embed_chunks"]
