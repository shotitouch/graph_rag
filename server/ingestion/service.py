import time
import uuid

from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from unstructured.partition.pdf import partition_pdf

from filing_metadata.extractor import llm_extract_tenq_metadata, regex_extract_tenq_metadata
from filing_metadata.normalizer import normalize_tenq_metadata
from ingestion.schemas import IngestResult
from llm_runtime.client import llm
from retrieval.service import ensure_qdrant_collection, get_vectorstore
from shared.logging import get_logger

logger = get_logger(__name__)


def split_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )
    return splitter.split_text(text)


async def summarize_financial_image(base64_str: str) -> str:
    clean_base64 = base64_str.replace("\n", "").strip()
    prompt = (
        "This image is from a US SEC Form 10-Q filing.\n"
        "If it is a financial chart or table:\n"
        "- Identify the metric\n"
        "- Describe the trend\n"
        "- Extract any visible numbers\n"
        "If it is not financial, briefly describe the image.\n"
        "Do not speculate."
    )

    response = await llm.ainvoke([
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{clean_base64}"},
                },
            ],
        },
    ])
    return response.content.strip()


def extract_pdf_pages_fast(pdf_path: str) -> list[dict[str, str | int]]:
    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({
                "page": page_number,
                "text": text,
            })

    return pages


async def extract_metadata_from_cover_text(
    cover_text: str,
    filename: str,
) -> tuple[str, int | None, str | None, bool, bool]:
    metadata_start = time.perf_counter()
    regex_metadata = regex_extract_tenq_metadata(cover_text)
    ticker = regex_metadata.ticker
    year = regex_metadata.year
    period = regex_metadata.period
    used_llm = False

    if ticker is None or year is None or period is None:
        used_llm = True
        logger.info("event=metadata_llm_fallback_started filename=%s", filename)
        llm_metadata = await llm_extract_tenq_metadata(cover_text)

        if ticker is None:
            ticker = llm_metadata.ticker
        if year is None:
            year = llm_metadata.year
        if period is None:
            period = llm_metadata.period
        logger.info("event=metadata_llm_fallback_completed filename=%s", filename)

    normalized = normalize_tenq_metadata(ticker=ticker, year=year, period=period)
    normalized_ticker = normalized.ticker or "UNKNOWN"
    metadata_complete = (
        normalized_ticker != "UNKNOWN"
        and normalized.year is not None
        and normalized.period is not None
    )
    logger.info(
        "event=metadata_extracted filename=%s ticker=%s year=%s period=%s complete=%s used_llm=%s duration_ms=%.2f",
        filename,
        normalized_ticker,
        normalized.year,
        normalized.period,
        metadata_complete,
        used_llm,
        (time.perf_counter() - metadata_start) * 1000,
    )

    return normalized_ticker, normalized.year, normalized.period, metadata_complete, used_llm


async def ingest_10q_fast(file: UploadFile, pdf_path: str) -> IngestResult:
    ingest_start = time.perf_counter()
    logger.info(
        "event=ingest_started filename=%s content_type=%s mode=fast",
        file.filename,
        file.content_type,
    )

    extraction_start = time.perf_counter()
    logger.info("event=text_extraction_started filename=%s mode=fast", file.filename)
    pages = extract_pdf_pages_fast(pdf_path)
    logger.info(
        "event=text_extraction_completed filename=%s mode=fast pages=%s duration_ms=%.2f",
        file.filename,
        len(pages),
        (time.perf_counter() - extraction_start) * 1000,
    )

    if not pages:
        raise ValueError("No extractable text found in PDF")

    cover_text = "\n".join(page["text"] for page in pages[:3])[:3000]
    ticker, year, period, metadata_complete, used_llm = await extract_metadata_from_cover_text(
        cover_text,
        file.filename,
    )

    parent_id = str(uuid.uuid4())
    texts = []
    metadatas = []
    text_chunks_count = 0

    chunk_build_start = time.perf_counter()
    for page in pages:
        page_text = str(page["text"])
        page_number = int(page["page"])
        text_chunks = [page_text] if len(page_text) <= 500 else split_text(page_text)
        for chunk_idx, text_chunk in enumerate(text_chunks):
            if not text_chunk.strip():
                continue
            texts.append(text_chunk)
            metadatas.append({
                "parent_id": parent_id,
                "ticker": ticker,
                "year": year,
                "period": period,
                "filing_type": "10-Q",
                "ingest_mode": "fast",
                "metadata_complete": metadata_complete,
                "source": file.filename,
                "page": page_number,
                "chunk_id": f"{parent_id}_p{page_number}_c{chunk_idx}",
                "content_type": "text",
                "type": "narrative",
            })
            text_chunks_count += 1

    if not texts:
        raise ValueError("No ingestable text chunks extracted from 10-Q")

    logger.info(
        "event=chunk_build_completed filename=%s parent_id=%s mode=fast text_chunks=%s table_chunks=0 image_chunks=0 total_chunks=%s duration_ms=%.2f",
        file.filename,
        parent_id,
        text_chunks_count,
        len(texts),
        (time.perf_counter() - chunk_build_start) * 1000,
    )

    vector_write_start = time.perf_counter()
    logger.info(
        "event=vectorstore_write_started filename=%s parent_id=%s mode=fast chunks=%s",
        file.filename,
        parent_id,
        len(texts),
    )
    ensure_qdrant_collection()
    await get_vectorstore().aadd_texts(
        texts=texts,
        metadatas=metadatas,
    )
    logger.info(
        "event=vectorstore_write_completed filename=%s parent_id=%s mode=fast chunks=%s duration_ms=%.2f",
        file.filename,
        parent_id,
        len(texts),
        (time.perf_counter() - vector_write_start) * 1000,
    )
    logger.info(
        "event=ingest_completed filename=%s parent_id=%s mode=fast duration_ms=%.2f",
        file.filename,
        parent_id,
        (time.perf_counter() - ingest_start) * 1000,
    )

    return {
        "status": "success",
        "message": f"{file.filename} ingested successfully",
        "parent_id": parent_id,
        "ticker": ticker,
        "year": year,
        "period": period,
        "mode": "fast",
        "metadata_complete": metadata_complete,
        "used_llm_fallback": used_llm,
        "chunks_added": len(texts),
    }


async def ingest_10q_full(file: UploadFile, pdf_path: str) -> IngestResult:
    ingest_start = time.perf_counter()
    logger.info(
        "event=ingest_started filename=%s content_type=%s mode=full",
        file.filename,
        file.content_type,
    )

    partition_start = time.perf_counter()
    logger.info("event=partition_started filename=%s mode=full", file.filename)
    elements = partition_pdf(
        filename=pdf_path,
        strategy="auto",
        extract_images_in_pdf=True,
        infer_table_structure=True,
        chunking_strategy=None,
    )
    logger.info(
        "event=partition_completed filename=%s mode=full elements=%s duration_ms=%.2f",
        file.filename,
        len(elements),
        (time.perf_counter() - partition_start) * 1000,
    )

    cover_text = "\n".join(
        el.text for el in elements[:20]
        if hasattr(el, "text") and el.text
    )[:3000]

    ticker, year, period, metadata_complete, used_llm = await extract_metadata_from_cover_text(
        cover_text,
        file.filename,
    )

    parent_id = str(uuid.uuid4())
    texts = []
    metadatas = []
    image_chunks = 0
    table_chunks = 0
    text_chunks_count = 0

    chunk_build_start = time.perf_counter()
    for idx, el in enumerate(elements):
        page_number = getattr(el.metadata, "page_number", None) or 1
        element_chunk_id = f"{parent_id}_e{idx}"
        base_meta = {
            "parent_id": parent_id,
            "ticker": ticker,
            "year": year,
            "period": period,
            "filing_type": "10-Q",
            "ingest_mode": "full",
            "metadata_complete": metadata_complete,
            "source": file.filename,
            "page": page_number,
            "element_index": idx,
        }

        if el.category == "Image" and getattr(el.metadata, "image_base64", None):
            logger.info(
                "event=image_summary_started filename=%s parent_id=%s element_index=%s page=%s",
                file.filename,
                parent_id,
                idx,
                page_number,
            )
            summary = await summarize_financial_image(el.metadata.image_base64)
            logger.info(
                "event=image_summary_completed filename=%s parent_id=%s element_index=%s page=%s",
                file.filename,
                parent_id,
                idx,
                page_number,
            )
            if summary:
                texts.append(summary)
                metadatas.append({
                    **base_meta,
                    "chunk_id": element_chunk_id,
                    "content_type": "image",
                    "type": "chart",
                })
                image_chunks += 1

        elif el.category == "Table":
            table_html = getattr(el.metadata, "text_as_html", None) or el.text
            if table_html:
                texts.append(table_html)
                metadatas.append({
                    **base_meta,
                    "chunk_id": element_chunk_id,
                    "content_type": "table",
                    "type": "financial_table",
                })
                table_chunks += 1

        elif hasattr(el, "text") and el.text:
            text_chunks = [el.text]
            if len(el.text) > 500:
                text_chunks = split_text(el.text)
            for chunk_idx, text_chunk in enumerate(text_chunks):
                if not text_chunk.strip():
                    continue
                texts.append(text_chunk)
                metadatas.append({
                    **base_meta,
                    "chunk_id": f"{element_chunk_id}_c{chunk_idx}",
                    "content_type": "text",
                    "type": "narrative",
                })
                text_chunks_count += 1

    if not texts:
        raise ValueError("No ingestable content extracted from 10-Q")

    logger.info(
        "event=chunk_build_completed filename=%s parent_id=%s mode=full text_chunks=%s table_chunks=%s image_chunks=%s total_chunks=%s duration_ms=%.2f",
        file.filename,
        parent_id,
        text_chunks_count,
        table_chunks,
        image_chunks,
        len(texts),
        (time.perf_counter() - chunk_build_start) * 1000,
    )

    vector_write_start = time.perf_counter()
    logger.info(
        "event=vectorstore_write_started filename=%s parent_id=%s mode=full chunks=%s",
        file.filename,
        parent_id,
        len(texts),
    )
    ensure_qdrant_collection()
    await get_vectorstore().aadd_texts(
        texts=texts,
        metadatas=metadatas,
    )
    logger.info(
        "event=vectorstore_write_completed filename=%s parent_id=%s mode=full chunks=%s duration_ms=%.2f",
        file.filename,
        parent_id,
        len(texts),
        (time.perf_counter() - vector_write_start) * 1000,
    )
    logger.info(
        "event=ingest_completed filename=%s parent_id=%s mode=full duration_ms=%.2f",
        file.filename,
        parent_id,
        (time.perf_counter() - ingest_start) * 1000,
    )

    return {
        "status": "success",
        "message": f"{file.filename} ingested successfully",
        "parent_id": parent_id,
        "ticker": ticker,
        "year": year,
        "period": period,
        "mode": "full",
        "metadata_complete": metadata_complete,
        "used_llm_fallback": used_llm,
        "chunks_added": len(texts),
    }


async def ingest_pdf(file: UploadFile, pdf_path: str, mode: str) -> IngestResult:
    if mode == "fast":
        return await ingest_10q_fast(file, pdf_path)
    return await ingest_10q_full(file, pdf_path)
