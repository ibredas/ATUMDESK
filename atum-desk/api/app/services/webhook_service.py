import logging
import hmac
import hashlib
import json
import httpx
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import select
from app.models.webhook import Webhook
from app.db.base import AsyncSessionLocal

logger = logging.getLogger(__name__)

class WebhookService:
    async def dispatch_event(self, organization_id, event_type: str, payload: Dict[str, Any]):
        """
        Dispatch an event to all active webhooks for the organization
        that subscribe to this event_type.
        """
        async with AsyncSessionLocal() as session:
            # Find active webhooks for this org
            result = await session.execute(
                select(Webhook).where(
                    Webhook.organization_id == organization_id,
                    Webhook.is_active == True
                )
            )
            webhooks = result.scalars().all()
            
            if not webhooks:
                return

            # Filter relevant webhooks
            targets = []
            for wh in webhooks:
                # Check wildcard or exact match
                if "*" in wh.event_types or event_type in wh.event_types:
                    targets.append(wh)
            
            if not targets:
                return

            logger.info(f"Dispatching webhook event '{event_type}' to {len(targets)} targets")
            
            # Send (could be parallelized)
            async with httpx.AsyncClient(timeout=10.0) as client:
                for target in targets:
                    await self._send_webhook(client, target, event_type, payload, session)

    async def _send_webhook(self, client, webhook: Webhook, event_type: str, payload: Dict[str, Any], session):
        """Send a single webhook request"""
        body = json.dumps({
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        }).encode("utf-8")
        
        # Calculate Signature
        signature = hmac.new(
            webhook.secret.encode("utf-8"),
            body,
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "X-Atum-Signature": f"sha256={signature}",
            "X-Atum-Event": event_type
        }
        
        try:
            response = await client.post(webhook.url, content=body, headers=headers)
            response.raise_for_status()
            
            # Update success stats
            webhook.last_triggered_at = datetime.utcnow()
            webhook.failure_count = 0 
            # Note: session commit needed if we want to persist stats
            session.add(webhook)
            await session.commit()
            
        except Exception as e:
            logger.error(f"Webhook delivery failed to {webhook.url}: {e}")
            # Update failure stats
            webhook.last_failure_reason = str(e)[:1000]
            webhook.failure_count += 1
            session.add(webhook)
            await session.commit()

webhook_service = WebhookService()
