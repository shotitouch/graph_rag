from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENAI_CHAT_MODEL

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_CHAT_MODEL,
    temperature=0,
    max_tokens=300,
)
