# routers/ingest.py
import os
import asyncio
from fastapi import APIRouter, UploadFile, HTTPException, status
from tempfile import NamedTemporaryFile
from langchain_community.document_loaders import PyPDFLoader

from core.retriever import vectorstore   # global Chroma instance
from utils.text_splitter import split_text

router = APIRouter(prefix="/ingest")

def prepare_chunks(pages, filename):
    # Convert each page → chunks → store metadata
    texts = []
    metadatas = []

    for page_num, page in enumerate(pages):
        chunks = split_text(page.page_content)

        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = f"{filename}_p{page_num}_c{chunk_idx}"

            texts.append(chunk)
            metadatas.append({
                "source": filename,
                "page": page_num + 1,
                "chunk_id": chunk_id,
                "content_type": "text"
            })

    return texts, metadatas


@router.post("/")
async def ingest_pdf(file: UploadFile):
    """
    Upload a PDF → Extract text → Chunk → Store in Chroma
    with metadata (filename, page number)
    """

    # 0. Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDFs are allowed."
        )
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File extension must be .pdf"
        )

    # 1. Save uploaded PDF temporarily
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # 2. Load PDF pages
        loader = PyPDFLoader(tmp_path)
        pages = await asyncio.to_thread(loader.load)

        os.unlink(tmp_path)

        # 3. Convert each page → chunks → store metadata
        texts, metadatas = await asyncio.to_thread(prepare_chunks, pages, file.filename)
        
        # 4. Add chunks + metadata to vectorstore
        await vectorstore.aadd_texts(
            texts=texts,
            metadatas=metadatas
        )

        # 5. Persist to disk
        # vectorstore.persist()

        # 6. Return summary
        return {
            "message": f"{file.filename} ingested successfully",
            "pages": len(pages),
            "chunks_added": len(texts),
        }
    
    except Exception as e:
        # Cleanup if logic fails before unlink
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

        raise HTTPException(
            status_code=500, 
            detail=f"Ingestion failed: {str(e)}"
        )