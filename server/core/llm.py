from langchain_openai import ChatOpenAI
from config import OPENROUTER_API_KEY

llm = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-4.1-mini",
    temperature=0,
    max_tokens=300,
)
