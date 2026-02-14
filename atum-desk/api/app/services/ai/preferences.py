"""
AI Preferences Service - Per-Organization AI Configuration
Manages AI model preferences and feature flags per organization
"""
import logging
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.config import get_settings

logger = logging.getLogger(__name__)
_settings = get_settings()

DEFAULT_AI_PREFERENCES = {
    "auto_triage": True,
    "auto_assign": True,
    "sentiment_analysis": True,
    "smarter_reply": True,
    "sla_prediction": True,
    "model_tier": "standard",  # fast, standard, elite, reasoning
    "fast_model": "qwen2.5:0.5b",
    "standard_model": "ATUM-DESK-COPILOT:latest",
    "elite_model": "ATUM-DESK-COPILOT:latest",
    "reasoning_model": "deepseek-r1:1.5b",
    "cache_enabled": True,
    "cache_ttl_minutes": 30,
}


class AIPreferencesService:
    """Service for managing organization-specific AI preferences"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_preferences(
        self,
        organization_id: UUID
    ) -> Dict[str, Any]:
        """Get AI preferences for an organization"""
        result = await self.db.get(Organization, organization_id)
        if not result:
            return DEFAULT_AI_PREFERENCES.copy()
        
        org_settings = result.settings or {}
        ai_prefs = org_settings.get("ai_preferences", {})
        
        # Merge with defaults
        return {**DEFAULT_AI_PREFERENCES, **ai_prefs}
    
    async def update_preferences(
        self,
        organization_id: UUID,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update AI preferences for an organization"""
        result = await self.db.get(Organization, organization_id)
        if not result:
            raise ValueError(f"Organization {organization_id} not found")
        
        org_settings = result.settings or {}
        
        # Update AI preferences
        org_settings["ai_preferences"] = {
            **DEFAULT_AI_PREFERENCES,
            **preferences
        }
        
        result.settings = org_settings
        await self.db.commit()
        await self.db.refresh(result)
        
        logger.info(f"Updated AI preferences for org {organization_id}")
        return org_settings["ai_preferences"]
    
    async def get_model_for_task(
        self,
        organization_id: UUID,
        task_type: str
    ) -> str:
        """Get the configured model for a specific task type"""
        prefs = await self.get_preferences(organization_id)
        
        model_map = {
            "fast": prefs.get("fast_model"),
            "standard": prefs.get("standard_model"),
            "elite": prefs.get("elite_model"),
            "reasoning": prefs.get("reasoning_model"),
        }
        
        return model_map.get(task_type, prefs.get("standard_model"))
    
    async def is_feature_enabled(
        self,
        organization_id: UUID,
        feature: str
    ) -> bool:
        """Check if an AI feature is enabled for the organization"""
        prefs = await self.get_preferences(organization_id)
        return prefs.get(feature, True)


async def get_ai_preferences(db: AsyncSession, organization_id: UUID) -> Dict[str, Any]:
    """Helper to get AI preferences"""
    service = AIPreferencesService(db)
    return await service.get_preferences(organization_id)


async def update_ai_preferences(
    db: AsyncSession,
    organization_id: UUID,
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """Helper to update AI preferences"""
    service = AIPreferencesService(db)
    return await service.update_preferences(organization_id, preferences)
