"""
Hybrid Retriever.

Combines Semantic search (Cosine similarity) and Keyword search (BM25)
for retrieving resume sections. Supports metadata filtering by doc_id and section.
"""

import logging
from typing import List, Optional
from uuid import UUID

from app.core.rag.indexer import get_index
from app.schemas.resume import RetrievalResult

logger = logging.getLogger(__name__)


async def hybrid_retrieve(
    resume_id: UUID, 
    query: str, 
    section_filter: Optional[str] = None,
    top_k: int = 5,
    semantic_weight: float = 0.7
) -> List[RetrievalResult]:
    """
    Perform a hybrid retrieval query scoped to a specific resume.
    """
    try:
        from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
        from llama_index.core.retrievers import VectorIndexRetriever
        
        index = get_index()
        
        # Build metadata filters to scope to this specific resume
        filters_list = [
            ExactMatchFilter(key="doc_id", value=str(resume_id))
        ]
        
        if section_filter:
            filters_list.append(
                ExactMatchFilter(key="section", value=section_filter.lower())
            )
            
        filters = MetadataFilters(filters=filters_list)
        
        # Configure retriever
        # Upgraded to Hybrid retrieval (BM25 Keyword + Vector) combining score
        
        # We will use RouterRetriever or QueryFusionRetriever to combine vector search and BM25.
        from llama_index.retrievers.bm25 import BM25Retriever
        from llama_index.core.retrievers import QueryFusionRetriever
        
        vector_retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=top_k,
            filters=filters,
        )
        
        # Build local BM25 retriever for the filtered resume nodes
        # If the number of documents is small per resume, instantiating BM25 dynamically is cheap.
        try:
            from app.core.rag.vector_store import _get_client, COLLECTION_NAME
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue
            from llama_index.core.schema import TextNode
            
            client = _get_client()
            scroll_results = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=str(resume_id))
                        )
                    ]
                ),
                limit=100,
                with_payload=True,
                with_vectors=False
            )
            points = scroll_results[0]
            doc_nodes = []
            for point in points:
                payload = point.payload
                text = payload.get("text", payload.get("raw_text", ""))
                node = TextNode(
                    text=text,
                    id_=point.id,
                    metadata={
                        "doc_id": payload.get("doc_id"),
                        "section": payload.get("section"),
                        "chunk_index": payload.get("chunk_index"),
                    }
                )
                doc_nodes.append(node)
                
            if not doc_nodes:
                raise ValueError("No nodes found in Qdrant for this resume_id to build BM25 index")

            bm25_retriever = BM25Retriever.from_defaults(nodes=doc_nodes, similarity_top_k=top_k)
            
            retriever = QueryFusionRetriever(
                [vector_retriever, bm25_retriever],
                similarity_top_k=top_k,
                num_queries=1,  # Keep it 1 for strict querying (no rewrite)
                mode="reciprocal_rank",
                use_async=False,
            )
        except Exception as e:
            logger.warning(f"Failed to setup BM25 hybrid search, falling back to pure vector: {e}")
            retriever = vector_retriever
        
        logger.info(f"Executing retrieval for resume {resume_id}, section: {section_filter}")
        nodes = retriever.retrieve(query)
        
        results = []
        for node in nodes:
            # node is a NodeWithScore
            payload = node.node.metadata
            results.append(
                RetrievalResult(
                    chunk_text=node.node.get_content(),
                    section=payload.get("section", "unknown"),
                    score=node.score or 0.0,
                    chunk_index=payload.get("chunk_index", 0)
                )
            )
            
        # Sort by chunk_index to maintain reading order if scores are close
        # (Alternatively, just return by score)
        
        return results
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise
