"""
AI Category Classification Service
Automatically classifies tickets into categories using NLP
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

TICKET_CATEGORIES = [
    "TECHNICAL",
    "BILLING", 
    "ACCOUNT",
    "INQUIRY",
    "SECURITY",
    "INFRA",
    "SOFTWARE",
    "HARDWARE",
    "NETWORK",
    "OTHER"
]

CATEGORY_KEYWORDS = {
    "TECHNICAL": ["error", "bug", "issue", "not working", "crash", "broken", "fail", "exception", "debug", "code"],
    "BILLING": ["invoice", "payment", "charge", "refund", "subscription", "price", "cost", "bill", "receipt"],
    "ACCOUNT": ["password", "login", "access", "permission", "user", "profile", "email", "reset"],
    "INQUIRY": ["question", "how to", "help", "information", "what is", "where", "when", "can you"],
    "SECURITY": ["security", "breach", "hack", "vulnerability", "threat", "malware", "phishing", "suspicious"],
    "INFRA": ["server", "database", "storage", "backup", "infrastructure", "cloud", "deployment"],
    "SOFTWARE": ["install", "update", "upgrade", "license", "app", "application", "software"],
    "HARDWARE": ["laptop", "computer", "monitor", "printer", "keyboard", "mouse", "device", "hardware"],
    "NETWORK": ["wifi", "internet", "connection", "vpn", "network", "bandwidth", "latency"],
}


class CategoryClassifier:
    """AI-powered ticket category classifier"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def classify(
        self,
        subject: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Classify ticket into category with confidence score.
        Uses keyword matching + LLM for accuracy.
        """
        text = f"{subject} {description}".lower()
        
        # First pass: keyword matching
        category_scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                category_scores[category] = score
        
        # If high confidence keyword match, return immediately
        if category_scores:
            top_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[top_category]
            if max_score >= 3:
                return {
                    "category": top_category,
                    "confidence": min(0.95, 0.5 + (max_score * 0.1)),
                    "method": "keyword"
                }
        
        # Second pass: Use LLM for ambiguous cases
        if _settings.AI_ENABLED:
            try:
                llm_result = await self._classify_with_llm(subject, description)
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM classification failed: {e}")
        
        # Fallback: return top keyword match or default
        if category_scores:
            top = max(category_scores, key=category_scores.get)
            return {
                "category": top,
                "confidence": 0.4,
                "method": "keyword_fallback"
            }
        
        return {
            "category": "OTHER",
            "confidence": 0.3,
            "method": "default"
        }
    
    async def _classify_with_llm(
        self,
        subject: str,
        description: str
    ) -> Optional[Dict[str, Any]]:
        """Use LLM for more accurate classification"""
        import requests
        
        prompt = f"""Classify this support ticket into ONE of these categories:
{TICKET_CATEGORIES}

Respond with ONLY valid JSON:
{{"category": "CATEGORY_NAME", "confidence": 0.0-1.0}}

Ticket Subject: {subject[:200]}
Ticket Description: {description[:500]}"""
        
        try:
            response = requests.post(
                f"{_settings.OLLAMA_URL}/api/generate",
                json={
                    "model": _settings.AI_FAST_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                import json
                parsed = json.loads(result.get("response", "{}"))
                if parsed.get("category") in TICKET_CATEGORIES:
                    return {
                        "category": parsed["category"],
                        "confidence": parsed.get("confidence", 0.7),
                        "method": "llm"
                    }
        except Exception as e:
            logger.error(f"LLM classification error: {e}")
        
        return None
    
    async def batch_classify(
        self,
        tickets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Classify multiple tickets"""
        results = []
        for ticket in tickets:
            result = await self.classify(
                ticket.get("subject", ""),
                ticket.get("description", "")
            )
            results.append({
                "ticket_id": ticket.get("id"),
                **result
            })
        return results


async def classify_ticket(
    db: AsyncSession,
    subject: str,
    description: str
) -> Dict[str, Any]:
    """Helper function for ticket classification"""
    classifier = CategoryClassifier(db)
    return await classifier.classify(subject, description)
