from langchain_openai import OpenAIEmbeddings
from config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

embeddings = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model=OPENAI_EMBEDDING_MODEL,
)
