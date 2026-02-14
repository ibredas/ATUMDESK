"""
ATUM DESK - AI Router Service
Multi-model routing for different task types
"""
import hashlib
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import requests
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

# Model routing configuration
MODEL_ROUTING = {
    # Fast tasks - simple categorization, quick responses
    "fast": {
        "model": "qwen2.5:0.5b",
        "temperature": 0.2,
        "max_tokens": 256,
        "use_case": "quick_triage,simple_classification"
    },
    # Standard copilot - general ticket analysis
    "standard": {
        "model": "ATUM-DESK-COPILOT:latest",
        "temperature": 0.15,
        "max_tokens": 512,
        "use_case": "ticket_analysis,reply_drafting,context"
    },
    # Elite - complex reasoning, sentiment analysis
    "elite": {
        "model": "ATUM-DESK-COPILOT:latest",
        "temperature": 0.1,
        "max_tokens": 768,
        "use_case": "complex_analysis,sentiment,risk_assessment"
    },
    # Deep thinking - for complex escalations
    "reasoning": {
        "model": "deepseek-r1:1.5b",
        "temperature": 0.05,
        "max_tokens": 1024,
        "use_case": "escalation_review,root_cause_analysis"
    }
}

# In-memory cache (production would use Redis or DB)
_response_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 1800  # 30 minutes


class AIRouter:
    """Intelligent AI request router with caching"""
    
    def __init__(self):
        self.cache = _response_cache
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model"""
        content = f"{model}:{prompt[:500]}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Check cache for existing response"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["timestamp"] < CACHE_TTL_SECONDS:
                logger.info(f"Cache hit for key {cache_key[:8]}...")
                return entry["response"]
            else:
                del self.cache[cache_key]
        return None
    
    def _set_cached_response(self, cache_key: str, response: str):
        """Cache the response"""
        self.cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
    
    def route_task(self, task_type: str, prompt: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Route task to appropriate model.
        
        task_type: fast|standard|elite|reasoning
        Returns: {model, response, cached, duration_ms}
        """
        start_time = time.time()
        
        # Get model configuration
        if task_type not in MODEL_ROUTING:
            task_type = "standard"
        
        config = MODEL_ROUTING[task_type]
        model = config["model"]
        
        # Check cache
        cache_key = None
        if use_cache:
            cache_key = self._get_cache_key(prompt, model)
            cached = self._get_cached_response(cache_key)
            if cached:
                return {
                    "model": model,
                    "response": cached,
                    "cached": True,
                    "duration_ms": int((time.time() - start_time) * 1000)
                }
        
        # Generate response
        try:
            response = self._generate(
                model=model,
                prompt=prompt,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )
            
            # Cache if enabled
            if use_cache and cache_key:
                self._set_cached_response(cache_key, response)
            
            return {
                "model": model,
                "response": response,
                "cached": False,
                "duration_ms": int((time.time() - start_time) * 1000)
            }
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return {
                "model": model,
                "error": str(e),
                "cached": False,
                "duration_ms": int((time.time() - start_time) * 1000)
            }
    
    def _generate(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        """Generate response from Ollama"""
        response = requests.post(
            f"{_settings.OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "num_predict": max_tokens
            },
            timeout=_settings.OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "")
    
    def batch_generate(self, prompts: List[str], task_type: str = "standard") -> List[Dict[str, Any]]:
        """Generate responses for multiple prompts"""
        results = []
        for prompt in prompts:
            result = self.route_task(task_type, prompt)
            results.append(result)
        return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all available models"""
        status = {
            "available_models": [],
            "cache_size": len(self.cache),
            "routing": MODEL_ROUTING
        }
        
        try:
            response = requests.get(
                f"{_settings.OLLAMA_URL}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                status["available_models"] = [m["name"] for m in models]
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        logger.info("AI response cache cleared")


# Singleton instance
ai_router = AIRouter()


def get_ai_router() -> AIRouter:
    return ai_router
