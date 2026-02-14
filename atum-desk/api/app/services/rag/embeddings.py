"""
RAG Embeddings - Pure Ollama (No LangChain)
"""
import logging
import requests
from typing import List, Optional
from app.config import get_settings

logger = logging.getLogger(__name__)

_settings = get_settings()

# Singleton embedding dimension (autodetected on first call)
_cached_embed_dim: Optional[int] = None


def get_embedding(text: str) -> List[float]:
    """
    Get embedding for text using Ollama.
    Uses ATUM-DESK-AI model.
    Returns list of floats (1536 dimensions for ATUM-DESK-AI).
    """
    global _cached_embed_dim
    
    try:
        response = requests.post(
            f"{_settings.OLLAMA_URL}/api/embeddings",
            json={
                "model": _settings.OLLAMA_EMBEDDING_MODEL,
                "prompt": text,
            },
            timeout=_settings.OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        
        result = response.json()
        embedding = result.get("embedding", [])
        
        if embedding and _cached_embed_dim is None:
            _cached_embed_dim = len(embedding)
            logger.info(f"Autodetected embedding dimension: {_cached_embed_dim}")
        
        return embedding
        
    except Exception as e:
        logger.error(f"Failed to get embedding: {e}")
        return [0.0] * (_cached_embed_dim or _settings.RAG_EMBED_DIM)


def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for multiple texts.
    Note: Ollama doesn't have batch API, so we call sequentially.
    """
    return [get_embedding(text) for text in texts]


def get_embed_dimension() -> int:
    """Get current embedding dimension"""
    global _cached_embed_dim
    if _cached_embed_dim:
        return _cached_embed_dim
    return _settings.RAG_EMBED_DIM
