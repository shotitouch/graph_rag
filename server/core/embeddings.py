from langchain_openai import OpenAIEmbeddings
from config import OPENROUTER_API_KEY

embeddings = OpenAIEmbeddings(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
