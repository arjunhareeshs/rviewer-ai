"""
Vector store integration (Qdrant).

Manages the storage of 384-dim MiniLM embeddings for PDF resumes.
This store is used exclusively by LlamaIndex for frontend section retrieval.
"""

import logging
from typing import List, Tuple
from uuid import UUID
import uuid

from app.core.embedding.chunker import EnrichedChunk

logger = logging.getLogger(__name__)

_qdrant_client = None
COLLECTION_NAME = "resume_chunks"


def _get_client():
    global _qdrant_client
    if _qdrant_client is None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams
            import os
            
            # Robust connection logic for Qdrant using settings
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
            
            try:
                _qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=10.0)
                # Check if collection exists
                _qdrant_client.get_collections()
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant at {qdrant_host}:{qdrant_port}. Error: {e}. Falling back to memory storage.")
                _qdrant_client = QdrantClient(":memory:")

            # Ensure collection exists
            collections = [c.name for c in _qdrant_client.get_collections().collections]
            if COLLECTION_NAME not in collections:
                _qdrant_client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
                
        except ImportError as e:
            logger.error("qdrant-client is not installed.")
            raise ImportError("qdrant-client is required. pip install qdrant-client") from e
            
    return _qdrant_client


async def store_chunks(resume_id: UUID, chunks_with_vectors: List[Tuple[EnrichedChunk, List[float]]]) -> None:
    """
    Store chunk vectors and metadata into Qdrant.
    """
    if not chunks_with_vectors:
        return
        
    try:
        from qdrant_client.http.models import PointStruct
        
        client = _get_client()
        points = []
        
        for chunk, vector in chunks_with_vectors:
            point_id = str(uuid.uuid4())
            payload = {
                "doc_id": str(resume_id),
                "section": chunk.section_label,
                "text": chunk.raw_text,  # Required by LlamaIndex fallback
                "raw_text": chunk.raw_text,
                "chunk_index": chunk.chunk_index,
            }
            # Add other metadata
            payload.update(chunk.metadata)
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
            
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        logger.info(f"Upserted {len(points)} vectors to Qdrant for resume {resume_id}")
        
    except Exception as e:
        logger.error(f"Failed to store vectors in Qdrant: {e}")
        raise


async def delete_document(resume_id: UUID) -> None:
    """
    Delete all vectors associated with a resume ID.
    """
    try:
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue
        
        client = _get_client()
        
        # We need to make sure the collection exists before trying to delete
        collections = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            return
            
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=str(resume_id))
                    )
                ]
            )
        )
        logger.info(f"Deleted vectors for resume {resume_id} from Qdrant")
        
    except Exception as e:
        logger.error(f"Failed to delete vectors from Qdrant: {e}")
        # Don't raise here, we don't want to break the main DB deletion if Qdrant fails
