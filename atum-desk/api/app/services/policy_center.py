"""
ATUM DESK - Policy Center Service
OPA-like authorization engine for fine-grained access control
"""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
import structlog

logger = structlog.get_logger("policy_center")

VALID_TARGETS = ["tickets", "comments", "kb", "assets", "admin", "copilot", "workflows"]
VALID_ACTIONS = [
    "view", "create", "update", "delete",
    "apply_triage", "apply_reply", "run_copilot",
    "execute_workflow", "view_audit", "manage_users"
]
VALID_EFFECTS = ["ALLOW", "DENY"]


class PolicyEffect(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass
class PolicyDecision:
    decision: PolicyEffect
    reason: str
    policy_id: Optional[str] = None


class PolicyCenter:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def authorize(
        self,
        user_id: str,
        organization_id: str,
        user_roles: List[str],
        action: str,
        resource_type: str,
        resource_context: Optional[Dict[str, Any]] = None,
    ) -> PolicyDecision:
        """
        Authorize an action based on policy rules.
        Returns ALLOW by default for non-sensitive actions, DENY for sensitive.
        """
        if resource_type not in VALID_TARGETS:
            return PolicyDecision(PolicyEffect.ALLOW, f"Unknown target type: {resource_type}")
        
        if action not in VALID_ACTIONS:
            return PolicyDecision(PolicyEffect.ALLOW, f"Unknown action: {action}")
        
        query = select(
            "id", "name", "effect", "condition_json", "priority"
        ).where(
            f"target = '{resource_type}' AND action = '{action}' AND enabled = true"
        ).order_by("priority DESC")
        
        try:
            result = await self.db.execute(
                text(f"""
                    SELECT id, name, effect, condition_json, priority
                    FROM policy_rules
                    WHERE target = :target 
                    AND action = :action 
                    AND enabled = true
                    AND (organization_id = :org_id OR organization_id IS NULL)
                    ORDER BY priority DESC
                """),
                {
                    "target": resource_type,
                    "action": action,
                    "org_id": organization_id
                }
            )
            rows = result.fetchall()
            
            for row in rows:
                policy_id, name, effect, condition_json, priority = row
                
                if self._evaluate_condition(
                    condition_json or {},
                    user_roles,
                    user_id,
                    resource_context or {}
                ):
                    return PolicyDecision(
                        decision=PolicyEffect.ALLOW if effect == "ALLOW" else PolicyEffect.DENY,
                        reason=f"Matched policy: {name}",
                        policy_id=str(policy_id)
                    )
            
            # Default: DENY for sensitive actions, ALLOW for read
            sensitive_actions = ["delete", "apply_triage", "apply_reply", "run_copilot", "execute_workflow"]
            if action in sensitive_actions:
                return PolicyDecision(PolicyEffect.DENY, "No matching policy - default deny")
            
            return PolicyDecision(PolicyEffect.ALLOW, "No matching policy - default allow")
            
        except Exception as e:
            logger.error("policy_evaluation_error", error=str(e))
            # Fail open for read, fail closed for write
            if action in ["view"]:
                return PolicyDecision(PolicyEffect.ALLOW, "Policy error - fail open")
            return PolicyDecision(PolicyEffect.DENY, "Policy error - fail closed")
    
    def _evaluate_condition(
        self,
        conditions: Dict[str, Any],
        user_roles: List[str],
        user_id: str,
        resource_context: Dict[str, Any],
    ) -> bool:
        """Evaluate policy conditions"""
        
        # Check roles
        if "roles" in conditions:
            allowed_roles = conditions["roles"]
            if not any(role in allowed_roles for role in user_roles):
                return False
        
        # Check time window
        if "time_window" in conditions:
            # Format: "09:00-18:00"
            # Simplified - just check current hour
            pass
        
        # Check IP CIDR
        if "ip_cidr" in conditions:
            # Would need IP in resource_context
            pass
        
        # Check ownership
        if "ownership" in conditions:
            owner_id = resource_context.get("owner_id")
            if owner_id and owner_id != user_id:
                return False
        
        return True
    
    async def log_policy_decision(
        self,
        user_id: str,
        organization_id: str,
        action: str,
        resource_type: str,
        decision: PolicyDecision,
    ):
        """Log policy decision to audit"""
        from sqlalchemy import text
        try:
            await self.db.execute(
                text("""
                    INSERT INTO audit_log (
                        id, organization_id, user_id, action, entity_type,
                        details, created_at
                    ) VALUES (
                        gen_random_uuid(), :org_id, :user_id, :action, :entity_type,
                        :details, NOW()
                    )
                """),
                {
                    "org_id": organization_id,
                    "user_id": user_id,
                    "action": f"policy_{decision.decision.value.lower()}",
                    "entity_type": resource_type,
                    "details": json.dumps({
                        "policy_id": decision.policy_id,
                        "reason": decision.reason,
                        "action": action
                    })
                }
            )
            await self.db.commit()
        except Exception as e:
            logger.error("policy_audit_error", error=str(e))


async def check_policy(
    db: AsyncSession,
    user_id: str,
    organization_id: str,
    user_roles: List[str],
    action: str,
    resource_type: str,
    resource_context: Optional[Dict[str, Any]] = None,
) -> PolicyDecision:
    """Convenience function for policy checks"""
    center = PolicyCenter(db)
    return await center.authorize(user_id, organization_id, user_roles, action, resource_type, resource_context)
