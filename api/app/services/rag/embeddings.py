from langchain_ollama import OllamaEmbeddings
from app.config import get_settings

def get_embeddings() -> OllamaEmbeddings:
    settings = get_settings()
    return OllamaEmbeddings(
        model=settings.OLLAMA_EMBEDDING_MODEL,
        base_url=settings.OLLAMA_URL,
    )
