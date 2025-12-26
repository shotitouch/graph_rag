import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PERSIST_DIR = os.getenv("PERSIST_DIR", "./chroma_db")
MAX_HISTORY = 5
