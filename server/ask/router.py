from fastapi import APIRouter

from ask.schemas import ChatRequest
from ask.service import ask_question_service

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("/")
async def ask_question(request: ChatRequest):
    return await ask_question_service(request)
