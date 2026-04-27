import re
import uuid

from fastapi import HTTPException

from ask.schemas import ChatRequest
from shared.models import SourceEntry
from shared.logging import get_logger
from workflow.graph import agent_app as agent_graph

logger = get_logger(__name__)

NO_EVIDENCE_MESSAGE = "I couldn't verify an answer from the retrieved documents."
NOT_FOUND_MESSAGE = "Not found in context."
CITATION_PATTERN = re.compile(r"\[(S\d+)\]")


def build_initial_state(question: str) -> dict:
    return {
        "question": question,
        "thread_id": "",
        "request_id": "",
        "intent": "",
        "documents": [],
        "generation": "",
        "retry_count": 0,
        "is_grounded": "",
        "is_useful": "",
        "messages": [],
        "sources": [],
        "question_type": "",
        "coverage_type": "default_technical",
        "scope_type": "",
        "query_tickers": [],
        "query_year": None,
        "query_period": "",
        "multi_question": False,
        "focus_terms": [],
        "prepared_context": "",
    }


def validate_citations(answer: str, sources: list[SourceEntry]) -> tuple[bool, list[str]]:
    cited_ids = CITATION_PATTERN.findall(answer or "")
    valid_ids = {source.get("id") for source in sources}
    invalid_ids = sorted({citation for citation in cited_ids if citation not in valid_ids})
    return len(invalid_ids) == 0, invalid_ids


def build_safe_response(
    question: str,
    retry_count: int,
    failure_reason: str,
    sources: list[SourceEntry] | None = None,
) -> dict:
    safe_sources = sources or []
    return {
        "question": question,
        "answer": NO_EVIDENCE_MESSAGE,
        "sources": safe_sources,
        "metadata": {
            "retries": retry_count,
            "sources_count": len(safe_sources),
            "status": "abstained",
            "failure_reason": failure_reason,
        },
    }


async def ask_question_service(request: ChatRequest):
    try:
        request_id = uuid.uuid4().hex[:8]
        initial_state = build_initial_state(request.question)
        initial_state["thread_id"] = request.thread_id
        initial_state["request_id"] = request_id
        logger.info(
            "event=request_received route=ask thread_id=%s request_id=%s",
            request.thread_id,
            request_id,
        )

        config = {"configurable": {"thread_id": request.thread_id}}
        existing_state = await agent_graph.aget_state(config)

        if existing_state.values:
            inputs = {
                "question": request.question,
                "thread_id": request.thread_id,
                "request_id": request_id,
                "intent": "",
                "retry_count": 0,
                "is_grounded": "",
                "is_useful": "",
                "documents": [],
                "sources": [],
                "question_type": "",
                "coverage_type": "default_technical",
                "scope_type": "",
                "query_tickers": [],
                "query_year": None,
                "query_period": "",
                "multi_question": False,
                "focus_terms": [],
                "prepared_context": "",
            }
        else:
            inputs = initial_state

        final_state = await agent_graph.ainvoke(inputs, config=config)
        answer = (final_state.get("generation") or "").strip()
        sources = final_state.get("sources", [])
        retries = final_state.get("retry_count", 0)
        is_grounded = final_state.get("is_grounded")
        is_useful = final_state.get("is_useful")

        if not answer:
            logger.warning(
                "event=request_abstained route=ask thread_id=%s request_id=%s reason=empty_generation retry_count=%s",
                request.thread_id,
                request_id,
                retries,
            )
            return build_safe_response(request.question, retries, "empty_generation")

        if sources:
            citations_valid, invalid_ids = validate_citations(answer, sources)
            if not citations_valid:
                logger.warning(
                    "event=citation_validation_failed route=ask thread_id=%s request_id=%s invalid_ids=%s retry_count=%s",
                    request.thread_id,
                    request_id,
                    ",".join(invalid_ids),
                    retries,
                )
                return build_safe_response(
                    request.question,
                    retries,
                    f"invalid_citations:{','.join(invalid_ids)}",
                )
        elif is_useful == "yes" and is_grounded == "yes" and answer != NOT_FOUND_MESSAGE:
            logger.warning(
                "event=request_abstained route=ask thread_id=%s request_id=%s reason=missing_sources retry_count=%s",
                request.thread_id,
                request_id,
                retries,
            )
            return build_safe_response(request.question, retries, "missing_sources")

        if is_grounded == "no":
            logger.warning(
                "event=request_abstained route=ask thread_id=%s request_id=%s reason=hallucination_detected retry_count=%s",
                request.thread_id,
                request_id,
                retries,
            )
            return build_safe_response(request.question, retries, "hallucination_detected")

        if is_useful == "no":
            logger.warning(
                "event=request_abstained route=ask thread_id=%s request_id=%s reason=answer_not_useful retry_count=%s",
                request.thread_id,
                request_id,
                retries,
            )
            return build_safe_response(request.question, retries, "answer_not_useful")

        logger.info(
            "event=request_completed route=ask thread_id=%s request_id=%s status=answered retry_count=%s sources_count=%s",
            request.thread_id,
            request_id,
            retries,
            len(sources),
        )
        return {
            "question": request.question,
            "answer": answer,
            "sources": sources,
            "metadata": {
                "request_id": request_id,
                "retries": retries,
                "sources_count": len(sources),
                "status": "answered",
            },
        }
    except Exception as exc:
        logger.exception(
            "event=request_failed route=ask thread_id=%s request_id=%s",
            request.thread_id,
            request_id,
        )
        raise HTTPException(status_code=500, detail=str(exc))
