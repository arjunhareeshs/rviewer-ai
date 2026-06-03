import os
import sys
import asyncio
import uuid
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")

# Add server directory to Python path
server_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../server'))
sys.path.insert(0, server_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(server_dir, '.env'))

from app.core.extraction import extract_resume
from app.core.embedding.chunker import chunk_content_blocks
from app.core.embedding.embedder import embed_chunks
from app.core.rag.vector_store import store_chunks
from app.core.rag.retriever import hybrid_retrieve
from app.core.rag.synthesizer import synthesizer

INPUTS_DIR = Path(os.path.join(os.path.dirname(__file__), '../inputs'))
OUTPUTS_DIR = Path(os.path.join(os.path.dirname(__file__), '../outputs'))

async def process_resume(file_path: Path):
    print(f"\n--- Processing {file_path.name} ---")
    
    # Generate a dummy UUID for this test run
    resume_id = uuid.uuid4()
    
    # 1. Extraction
    print("1. Extracting...")
    ext_result = await extract_resume(str(file_path))
    
    ext_md = f"# Extraction Results for {file_path.name}\n\n"
    ext_md += f"**Method**: {ext_result.method}\n"
    ext_md += f"**Metadata**: {json.dumps(ext_result.metadata, indent=2)}\n\n"
    
    if ext_result.method == 'docling' and ext_result.content_blocks:
        ext_md += "## Content Blocks\n\n"
        for idx, block in enumerate(ext_result.content_blocks):
            ext_md += f"**Block {idx}** ({block.block_type}, size: {block.font_size}, weight: {block.text_weight})\n"
            ext_md += f"> {block.raw_text.replace(chr(10), ' ')}\n\n"
    
    ext_md += "## Raw Text\n\n```\n" + ext_result.raw_text + "\n```\n"
    
    with open(OUTPUTS_DIR / f"{file_path.stem}_extraction.md", "w", encoding="utf-8") as f:
        f.write(ext_md)
        
    # 2. Chunking
    print("2. Chunking...")
    
    if ext_result.method == 'docling' and ext_result.content_blocks:
        chunks, sections_dict = chunk_content_blocks(ext_result.content_blocks)
    elif ext_result.method == 'vlm' and ext_result.sections:
        sections_dict = ext_result.sections
        from app.core.extraction import ContentBlock
        virtual_blocks = []
        reading_order = 0
        for section_label, content in ext_result.sections.items():
            if not content or not content.strip():
                continue
            virtual_blocks.append(ContentBlock(
                block_type="heading",
                font_size=12.0,
                text_weight="bold",
                reading_order_index=reading_order,
                raw_text=section_label.capitalize()
            ))
            reading_order += 1
            
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            for line in lines:
                if line.startswith(("-", "*", "•")):
                    block_type = "list_item"
                    clean_line = line.lstrip("-*• ").strip()
                else:
                    block_type = "body"
                    clean_line = line
                virtual_blocks.append(ContentBlock(
                    block_type=block_type,
                    font_size=10.0,
                    text_weight="normal",
                    reading_order_index=reading_order,
                    raw_text=clean_line
                ))
                reading_order += 1
        chunks, _ = chunk_content_blocks(virtual_blocks)
    else:
        print("Skipping chunking and embedding.")
        return
    
    # Save the fully structured sections to our JSON store
    with open(OUTPUTS_DIR / f"{file_path.stem}_stored.json", "w", encoding="utf-8") as f:
        json.dump(sections_dict, f, indent=2, ensure_ascii=False)
        
    print("2.5 Standardizing with LLM...")
    try:
        std_resume = await synthesizer.synthesize(sections_dict)
        with open(OUTPUTS_DIR / f"{file_path.stem}_standardized.json", "w", encoding="utf-8") as f:
            json.dump(std_resume.model_dump(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Standardization failed: {e}")
    
    chunk_md = f"# Chunking Results for {file_path.name}\n\n"
    chunk_md += "## Extracted Sections\n\n"
    for label, content in sections_dict.items():
        chunk_md += f"### {label}\n```\n{content}\n```\n\n"
        
    chunk_md += "## Semantic Chunks\n\n"
    for chunk in chunks:
        avg_fs = chunk.metadata.get("avg_font_size", "?")
        bold = chunk.metadata.get("has_bold", False)
        chunk_md += f"**Chunk {chunk.chunk_index}** (Section: {chunk.section_label}, avg_font: {avg_fs}, bold: {bold})\n"
        chunk_md += f"> {chunk.raw_text.replace(chr(10), ' ')}\n\n"
        
    with open(OUTPUTS_DIR / f"{file_path.stem}_chunks.md", "w", encoding="utf-8") as f:
        f.write(chunk_md)
        
    # 3. Embedding and Vector Storage
    print("3. Embedding...")
    chunks_with_vectors = await embed_chunks(chunks)
    
    print("4. Storing vectors in Qdrant (ensure docker-compose is running!)...")
    try:
        await store_chunks(resume_id, chunks_with_vectors)
    except Exception as e:
        print(f"Failed to store chunks: {e}. Is Qdrant running?")
        print("Continuing with retrieval assuming fallback memory client might work, but it usually doesn't across process boundaries without a persistent DB.")
        
    # 4. Retrieval
    print("5. Testing Retrieval...")
    test_queries = [
        "What are the technical skills or programming languages?",
        "Where did they go to school and what degree?",
        "Describe their work experience or projects."
    ]
    
    ret_md = f"# Retrieval Results for {file_path.name}\n\n"
    ret_md += f"Resume ID: {resume_id}\n\n"
    
    for query in test_queries:
        ret_md += f"## Query: {query}\n\n"
        try:
            results = await hybrid_retrieve(resume_id, query, top_k=3)
            if not results:
                ret_md += "*No results found.*\n\n"
            for i, res in enumerate(results):
                ret_md += f"**Result {i+1}** (Score: {res.score:.4f}, Section: {res.section})\n"
                ret_md += f"> {res.chunk_text.replace(chr(10), ' ')}\n\n"
        except Exception as e:
            ret_md += f"*Retrieval failed: {e}*\n\n"
            
    with open(OUTPUTS_DIR / f"{file_path.stem}_retrieval.md", "w", encoding="utf-8") as f:
        f.write(ret_md)
        
    print(f"Finished {file_path.name}. Outputs saved to test/outputs/")

async def main():
    if not INPUTS_DIR.exists() or not any(INPUTS_DIR.iterdir()):
        print(f"No files found in {INPUTS_DIR}")
        return
        
    for file_path in INPUTS_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.jpg', '.png']:
            await process_resume(file_path)

if __name__ == "__main__":
    # Workaround for Windows asyncio event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
