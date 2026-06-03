"""
Embedding generation using HuggingFace all-MiniLM-L6-v2.

Loads the model once at startup and provides functions to embed
a list of EnrichedChunks.
"""

import logging
from typing import List, Tuple
from app.core.embedding.chunker import EnrichedChunk

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazy load the embedding model to avoid startup delay if not used."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformers/all-MiniLM-L6-v2...")
            # We use all-MiniLM-L6-v2 as specified for fast, local, high-quality embeddings (384-dim)
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully.")
        except ImportError as e:
            logger.error("sentence-transformers is not installed.")
            raise ImportError(
                "sentence-transformers is required for embedding. "
                "Install it with: pip install sentence-transformers"
            ) from e
    return _model


async def embed_chunks(chunks: List[EnrichedChunk]) -> List[Tuple[EnrichedChunk, List[float]]]:
    """
    Generate vector embeddings for a list of EnrichedChunks.
    Returns a list of tuples: (chunk, vector)
    """
    if not chunks:
        return []

    try:
        model = _get_model()
        
        # Extract text for embedding
        texts_to_embed = [chunk.raw_text for chunk in chunks]
        
        # Encode (this blocks the event loop; in a real prod env with high traffic, 
        # run in a ThreadPoolExecutor or external process)
        logger.info(f"Embedding {len(texts_to_embed)} chunks...")
        embeddings = model.encode(texts_to_embed, convert_to_numpy=True)
        
        # Zip chunks with their corresponding vectors
        result = []
        for chunk, embedding in zip(chunks, embeddings):
            # Convert numpy array to list of floats for vector DB insertion
            vector = embedding.tolist()
            result.append((chunk, vector))
            
        logger.info(f"Successfully generated {len(result)} embeddings.")
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise
