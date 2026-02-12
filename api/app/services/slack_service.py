import logging
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

class SlackService:
    def __init__(self):
        self.settings = get_settings()

    async def send_notification(self, message: str):
        """Send a notification to Slack"""
        if not self.settings.SLACK_WEBHOOK_URL:
             # logger.debug("Slack webhook not configured.")
             return

        try:
            async with httpx.AsyncClient() as client:
                payload = {"text": message}
                response = await client.post(
                    self.settings.SLACK_WEBHOOK_URL, 
                    json=payload,
                    timeout=5.0
                )
                response.raise_for_status()
                logger.info("Slack notification sent.")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

slack_service = SlackService()
