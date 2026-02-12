import logging
import aiosmtplib
from email.message import EmailMessage
from app.config import get_settings

logger = logging.getLogger(__name__)

class EmailNotificationService:
    def __init__(self):
        self.settings = get_settings()

    async def send_email(self, to_email: str, subject: str, body_html: str):
        """Send an email using configured SMTP server"""
        if not self.settings.SMTP_HOST or not self.settings.SMTP_USER:
            logger.warning("SMTP not configured. Email sending skipped.")
            return

        message = EmailMessage()
        message["From"] = self.settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body_html, subtype="html")

        try:
            logger.info(f"Sending email to {to_email}: {subject}")
            await aiosmtplib.send(
                message,
                hostname=self.settings.SMTP_HOST,
                port=self.settings.SMTP_PORT,
                username=self.settings.SMTP_USER,
                password=self.settings.SMTP_PASSWORD,
                use_tls=self.settings.SMTP_TLS,
            )
            logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")

email_notification_service = EmailNotificationService()
