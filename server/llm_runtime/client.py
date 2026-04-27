from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from shared.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, OPENAI_EMBEDDING_MODEL

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_CHAT_MODEL,
    temperature=0,
    max_tokens=300,
)

embeddings = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model=OPENAI_EMBEDDING_MODEL,
)
