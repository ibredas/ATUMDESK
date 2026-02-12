import asyncio
import email
import imaplib
import logging
from email.header import decode_header
from typing import Optional

from sqlalchemy import select
from app.config import get_settings
from app.db.base import AsyncSessionLocal
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.organization import Organization

logger = logging.getLogger(__name__)

class EmailIngestionService:
    def __init__(self):
        self.settings = get_settings()
        self.running = False

    async def start_polling(self):
        """Start the email polling loop"""
        if not self.settings.IMAP_HOST or not self.settings.IMAP_USER:
            logger.warning("IMAP not configured. Email ingestion disabled.")
            return

        self.running = True
        logger.info(f"Starting email ingestion from {self.settings.IMAP_HOST}...")

        while self.running:
            try:
                await self._poll_inbox()
            except Exception as e:
                logger.error(f"Error polling email: {e}")
            
            await asyncio.sleep(self.settings.EMAIL_POLL_INTERVAL)

    async def _poll_inbox(self):
        """Connect to IMAP and process unseen emails"""
        # Note: imaplib is blocking, so we run it in a thread executor if blocking is an issue.
        # For simplicity in this async loop, we'll use it directly but ideally should be to_thread.
        
        try:
            # Connect
            if self.settings.IMAP_SSL:
                mail = imaplib.IMAP4_SSL(self.settings.IMAP_HOST, self.settings.IMAP_PORT)
            else:
                mail = imaplib.IMAP4(self.settings.IMAP_HOST, self.settings.IMAP_PORT)

            # Login
            mail.login(self.settings.IMAP_USER, self.settings.IMAP_PASSWORD)
            mail.select(self.settings.IMAP_FOLDER)

            # Search Unseen
            _, messages = mail.search(None, 'UNSEEN')
            
            # Process
            for num in messages[0].split():
                if not num: continue
                
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)
                
                await self._process_email(message)
                
                # Mark as seen is automatic with fetch usually, but verify?
                # Usually fetching sets \Seen flag.

            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"IMAP Connection Error: {e}")
            raise

    async def _process_email(self, message):
        """Parse email and create ticket"""
        try:
            subject = self._decode_header(message["Subject"])
            sender = self._decode_header(message["From"])
            body = self._get_email_body(message)
            
            # Extract email address from sender
            email_addr = email.utils.parseaddr(sender)[1]
            
            async with AsyncSessionLocal() as session:
                # Find User
                result = await session.execute(select(User).where(User.email == email_addr))
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.info(f"Email from unknown user {email_addr}. Creating account/ticket?")
                    # For now, maybe log warning or create generic user?
                    # Let's verify if we should create users automatically.
                    # Assumption: Yes, standard helpdesk behavior.
                    
                    # Need Org
                    result = await session.execute(select(Organization).limit(1))
                    org = result.scalar_one_or_none()
                    if not org:
                         logger.error("No organization found to assign new user.")
                         return

                    user = User(
                        email=email_addr,
                        full_name=email_addr.split('@')[0],
                        password_hash="disabled", # No login
                        organization_id=org.id,
                        is_active=True,
                        email_verified=True
                    )
                    session.add(user)
                    await session.flush()
                
                # Create Ticket
                ticket = Ticket(
                    title=subject,
                    description=body,
                    status=TicketStatus.OPEN,
                    priority=TicketPriority.MEDIUM,
                    requester_id=user.id,
                    organization_id=user.organization_id
                )
                session.add(ticket)
                await session.commit()
                logger.info(f"Created Ticket from Email: {subject} (User: {email_addr})")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _decode_header(self, header_val):
        if not header_val: return ""
        decoded_list = decode_header(header_val)
        default_charset = 'utf-8'
        text = ""
        for decoded, charset in decoded_list:
            if isinstance(decoded, bytes):
                try:
                    text += decoded.decode(charset or default_charset)
                except:
                    text += decoded.decode(default_charset, errors='ignore')
            else:
                text += str(decoded)
        return text

    def _get_email_body(self, message):
        body = ""
        if message.is_multipart():
            for part in message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                
                # skip attachments
                if 'attachment' in cdispo:
                    continue
                
                if ctype == 'text/plain':
                     body += part.get_payload(decode=True).decode(errors='ignore')
                elif ctype == 'text/html' and not body:
                     # Fallback to HTML if no plain text
                     # Ideally strip tags
                     body += part.get_payload(decode=True).decode(errors='ignore')
        else:
             body = message.get_payload(decode=True).decode(errors='ignore')
        return body

email_ingestion_service = EmailIngestionService()
