"""
RAG (Retrieval-Augmented Generation) and Storage layer.
"""

from app.core.rag.structured_store import store_sections, get_full_resume_json
from app.core.rag.vector_store import store_chunks, delete_document

__all__ = [
    "store_sections",
    "get_full_resume_json",
    "store_chunks",
    "delete_document",
]
