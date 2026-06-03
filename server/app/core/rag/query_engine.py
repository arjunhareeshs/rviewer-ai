"""
Query Engine.

Wraps the retriever with a LlamaIndex query engine to synthesize
natural language responses using an LLM. Used for the Chat Assistant.
"""

import logging
from typing import Optional
from uuid import UUID

from app.core.rag.indexer import get_index
from app.config import get_settings

logger = logging.getLogger(__name__)


async def execute_query(
    resume_id: UUID, 
    query: str, 
    section_filter: Optional[str] = None
) -> str:
    """
    Execute a natural language query against the resume using RAG.
    """
    try:
        from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
        from llama_index.core.retrievers import VectorIndexRetriever
        from llama_index.core.query_engine import RetrieverQueryEngine
        from llama_index.llms.openai import OpenAI
        from llama_index.core import Settings
        
        settings = get_settings()
        
        # Configure the LLM for response synthesis (GPT-4o or similar)
        # In a real app, you might want to reuse a globally configured LLM
        llm = OpenAI(model="gpt-4o", api_key=settings.OPENAI_API_KEY)
        Settings.llm = llm
        
        index = get_index()
        
        # Build metadata filters
        filters_list = [
            ExactMatchFilter(key="doc_id", value=str(resume_id))
        ]
        
        if section_filter:
            filters_list.append(
                ExactMatchFilter(key="section", value=section_filter.lower())
            )
            
        filters = MetadataFilters(filters=filters_list)
        
        # Configure retriever
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=5,
            filters=filters,
        )
        
        # Create query engine
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            llm=llm
        )
        
        logger.info(f"Executing RAG query for resume {resume_id}: {query}")
        response = query_engine.query(query)
        
        return str(response)
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
