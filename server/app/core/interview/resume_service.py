import os
import logging
from pathlib import Path
from typing import Optional

from llama_index.core import VectorStoreIndex, Document, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter

from app.core.extraction import extract_resume

logger = logging.getLogger(__name__)

VECTOR_STORE_DIR = Path("data/vector_store")

class ResumeService:
    def __init__(self):
        self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    async def parse_resume(self, file_path: str) -> str:
        """Parse resume using existing extraction pipeline (Docling/VLM)."""
        logger.info(f"Parsing resume for interview: {file_path}")
        result = await extract_resume(file_path)
        return result.raw_text

    async def create_index_async(self, markdown_text: str, room_name: str) -> VectorStoreIndex:
        """Create FAISS index for the interview session."""
        logger.info(f"Creating vector index for room: {room_name}")
        
        # Create Document and parse into nodes
        doc = Document(text=markdown_text)
        nodes = self.node_parser.get_nodes_from_documents([doc])
        
        import faiss
        from llama_index.vector_stores.faiss import FaissVectorStore

        # 384 is dim for all-MiniLM-L6-v2
        faiss_index = faiss.IndexFlatL2(384)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=self.embed_model
        )
        
        # Persist to disk
        persist_dir = VECTOR_STORE_DIR / room_name
        persist_dir.mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=str(persist_dir))
        
        return index

    def load_index(self, room_name: str) -> Optional[VectorStoreIndex]:
        """Load persisted index from disk."""
        persist_dir = VECTOR_STORE_DIR / room_name
        if not persist_dir.exists():
            return None
            
        try:
            from llama_index.vector_stores.faiss import FaissVectorStore
            vector_store = FaissVectorStore.from_persist_dir(str(persist_dir))
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store, persist_dir=str(persist_dir)
            )
            
            index = load_index_from_storage(
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            return index
        except Exception as e:
            logger.error(f"Failed to load index for room {room_name}: {e}")
            return None

    def query_resume(self, index: VectorStoreIndex, query: str) -> str:
        """Query the resume context."""
        retriever = index.as_retriever(similarity_top_k=3)
        nodes = retriever.retrieve(query)
        return "\n\n".join([n.get_content() for n in nodes])

resume_service = ResumeService()
