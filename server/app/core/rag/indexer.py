"""
LlamaIndex index builder.

Configures LlamaIndex to use our Qdrant collection for retrieval operations.
Note: In this architecture, LlamaIndex is used ONLY for retrieval, not for
the initial ingestion (which we handled custom via Docling + MiniLM + Qdrant directly).
"""

import logging
from app.core.rag.vector_store import COLLECTION_NAME

logger = logging.getLogger(__name__)

_index = None


def get_index():
    """
    Lazy load and configure the LlamaIndex VectorStoreIndex.
    """
    global _index
    if _index is None:
        try:
            import qdrant_client
            from llama_index.core import VectorStoreIndex
            from llama_index.vector_stores.qdrant import QdrantVectorStore
            from llama_index.core import StorageContext
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            from llama_index.core import Settings
            
            # Configure LlamaIndex to use the same MiniLM model for query embedding
            Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
            # We don't need an LLM for pure retrieval, but Settings requires one by default.
            # We can set it to None if we only do retrieval, or mock it.
            # For query engine, we will need an LLM (which we'll configure later).
            
            from app.core.rag.vector_store import _get_client
            
            # Use the shared client from vector_store to ensure memory DBs are the same instance
            client = _get_client()
                
            vector_store = QdrantVectorStore(
                client=client, 
                collection_name=COLLECTION_NAME
            )
            
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index from existing vector store (we already ingested data)
            _index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context
            )
            
            logger.info("LlamaIndex configured with Qdrant vector store.")
            
        except ImportError as e:
            logger.error(f"Missing LlamaIndex dependencies: {e}")
            raise
            
    return _index
