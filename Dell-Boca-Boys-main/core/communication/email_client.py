"""
Gmail Email Client for Dell Bocca Boys Agent Communication

This module provides email communication capabilities for agents to:
- Read incoming emails with subject "Dell Bocca Boys"
- Send email responses back to users
- Authenticate securely with Gmail using OAuth2 or App Passwords

Official Agent Email: ace.llc.nyc@gmail.com
"""

import asyncio
import base64
import email
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from imaplib import IMAP4_SSL
from smtplib import SMTP_SSL
from typing import Dict, List, Optional, Tuple

import aiosmtplib
from aioimaplib import aioimaplib

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Represents an email message."""

    message_id: str
    from_address: str
    to_address: str
    subject: str
    body_text: str
    body_html: Optional[str]
    received_at: datetime
    in_reply_to: Optional[str] = None
    references: Optional[List[str]] = None
    attachments: Optional[List[Dict]] = None

    @property
    def is_from_user(self) -> bool:
        """Check if email is from a user (subject contains 'Dell Bocca Boys')."""
        return "Dell Bocca Boys" in self.subject or "Dell Boca Boys" in self.subject


class GmailEmailClient:
    """
    Gmail email client for Dell Bocca Boys agent communication.

    Supports both App Password and OAuth2 authentication.
    """

    AGENT_EMAIL = "ace.llc.nyc@gmail.com"
    IMAP_SERVER = "imap.gmail.com"
    SMTP_SERVER = "smtp.gmail.com"
    IMAP_PORT = 993
    SMTP_PORT = 465

    def __init__(
        self,
        email_address: Optional[str] = None,
        password: Optional[str] = None,
        use_oauth: bool = False
    ):
        """
        Initialize Gmail email client.

        Args:
            email_address: Gmail address (defaults to ace.llc.nyc@gmail.com)
            password: App password or OAuth token
            use_oauth: Whether to use OAuth2 instead of app password
        """
        self.email_address = email_address or os.getenv("AGENT_EMAIL", self.AGENT_EMAIL)
        self.password = password or os.getenv("AGENT_EMAIL_PASSWORD")
        self.use_oauth = use_oauth

        if not self.password and not use_oauth:
            logger.warning(
                "No email password configured. Set AGENT_EMAIL_PASSWORD environment variable "
                "or configure OAuth2 authentication."
            )

        self._imap_client: Optional[aioimaplib.AIOIMAP4_SSL] = None
        self._last_check_uid: int = 0

    async def connect(self) -> bool:
        """
        Connect to Gmail IMAP server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._imap_client = aioimaplib.AIOIMAP4_SSL(
                host=self.IMAP_SERVER,
                port=self.IMAP_PORT
            )
            await self._imap_client.wait_hello_from_server()

            if self.use_oauth:
                # OAuth2 authentication (placeholder for future implementation)
                logger.error("OAuth2 authentication not yet implemented. Use app password.")
                return False
            else:
                # App password authentication
                await self._imap_client.login(self.email_address, self.password)

            logger.info(f"Successfully connected to Gmail as {self.email_address}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Gmail: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Gmail IMAP server."""
        if self._imap_client:
            try:
                await self._imap_client.logout()
                logger.info("Disconnected from Gmail")
            except Exception as e:
                logger.error(f"Error disconnecting from Gmail: {e}")

    async def fetch_new_messages(
        self,
        folder: str = "INBOX",
        subject_filter: str = "Dell Bocca Boys"
    ) -> List[EmailMessage]:
        """
        Fetch new unread emails with specified subject filter.

        Args:
            folder: Gmail folder to check (default: INBOX)
            subject_filter: Filter emails by subject (default: "Dell Bocca Boys")

        Returns:
            List of new EmailMessage objects
        """
        if not self._imap_client:
            logger.error("Not connected to Gmail. Call connect() first.")
            return []

        try:
            # Select inbox
            await self._imap_client.select(folder)

            # Search for unread messages with subject filter
            search_criteria = f'UNSEEN SUBJECT "{subject_filter}"'
            status, data = await self._imap_client.search(search_criteria)

            if status != "OK":
                logger.error(f"Failed to search emails: {status}")
                return []

            email_ids = data[0].split()
            if not email_ids:
                logger.debug(f"No new emails with subject '{subject_filter}'")
                return []

            messages = []
            for email_id in email_ids:
                msg = await self._fetch_email_by_id(email_id)
                if msg:
                    messages.append(msg)

            logger.info(f"Fetched {len(messages)} new messages with subject '{subject_filter}'")
            return messages

        except Exception as e:
            logger.error(f"Error fetching new messages: {e}")
            return []

    async def _fetch_email_by_id(self, email_id: bytes) -> Optional[EmailMessage]:
        """
        Fetch a single email by ID.

        Args:
            email_id: Email ID from IMAP search

        Returns:
            EmailMessage object or None if fetch failed
        """
        try:
            status, data = await self._imap_client.fetch(email_id, "(RFC822)")

            if status != "OK":
                logger.error(f"Failed to fetch email {email_id}: {status}")
                return None

            # Parse email
            raw_email = data[1]
            email_message = email.message_from_bytes(raw_email)

            # Extract email components
            message_id = email_message.get("Message-ID", "")
            from_address = email_message.get("From", "")
            to_address = email_message.get("To", "")
            subject = email_message.get("Subject", "")
            date_str = email_message.get("Date", "")
            in_reply_to = email_message.get("In-Reply-To")
            references_str = email_message.get("References")

            # Parse date
            try:
                received_at = email.utils.parsedate_to_datetime(date_str)
            except Exception:
                received_at = datetime.utcnow()

            # Parse references
            references = []
            if references_str:
                references = re.findall(r'<[^>]+>', references_str)

            # Extract body
            body_text, body_html = self._extract_body(email_message)

            return EmailMessage(
                message_id=message_id,
                from_address=from_address,
                to_address=to_address,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                received_at=received_at,
                in_reply_to=in_reply_to,
                references=references
            )

        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            return None

    def _extract_body(self, email_message) -> Tuple[str, Optional[str]]:
        """
        Extract plain text and HTML body from email message.

        Args:
            email_message: Parsed email.message object

        Returns:
            Tuple of (plain_text, html_body)
        """
        body_text = ""
        body_html = None

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue

                    charset = part.get_content_charset() or "utf-8"
                    decoded = payload.decode(charset, errors="ignore")

                    if content_type == "text/plain":
                        body_text = decoded
                    elif content_type == "text/html":
                        body_html = decoded

                except Exception as e:
                    logger.error(f"Error extracting email body part: {e}")
        else:
            try:
                payload = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset() or "utf-8"
                body_text = payload.decode(charset, errors="ignore")
            except Exception as e:
                logger.error(f"Error extracting email body: {e}")

        return body_text.strip(), body_html

    async def send_reply(
        self,
        to_address: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email reply.

        Args:
            to_address: Recipient email address
            subject: Email subject
            body_text: Plain text email body
            body_html: Optional HTML email body
            in_reply_to: Message-ID of email being replied to
            references: List of Message-IDs in conversation thread

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email_address
            msg["To"] = to_address
            msg["Subject"] = subject

            if in_reply_to:
                msg["In-Reply-To"] = in_reply_to

            if references:
                msg["References"] = " ".join(references)

            # Attach plain text body
            msg.attach(MIMEText(body_text, "plain"))

            # Attach HTML body if provided
            if body_html:
                msg.attach(MIMEText(body_html, "html"))

            # Send via SMTP
            async with aiosmtplib.SMTP(
                hostname=self.SMTP_SERVER,
                port=self.SMTP_PORT,
                use_tls=True
            ) as smtp:
                await smtp.login(self.email_address, self.password)
                await smtp.send_message(msg)

            logger.info(f"Successfully sent email to {to_address}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def mark_as_read(self, email_id: bytes):
        """
        Mark an email as read.

        Args:
            email_id: Email ID from IMAP
        """
        try:
            await self._imap_client.store(email_id, "+FLAGS", "\\Seen")
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")

    async def archive_email(self, email_id: bytes):
        """
        Archive an email (move to All Mail, remove from Inbox).

        Args:
            email_id: Email ID from IMAP
        """
        try:
            await self._imap_client.copy(email_id, "[Gmail]/All Mail")
            await self._imap_client.store(email_id, "+FLAGS", "\\Deleted")
            await self._imap_client.expunge()
            logger.info(f"Archived email {email_id}")
        except Exception as e:
            logger.error(f"Failed to archive email: {e}")


# Convenience function for quick email sending
async def send_agent_email(
    to_address: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Quick function to send an email from the Dell Bocca Boys agent.

    Args:
        to_address: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body

    Returns:
        True if email sent successfully, False otherwise
    """
    client = GmailEmailClient()

    if not await client.connect():
        return False

    try:
        return await client.send_reply(
            to_address=to_address,
            subject=subject,
            body_text=body,
            body_html=html_body
        )
    finally:
        await client.disconnect()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create email client
        client = GmailEmailClient()

        # Connect
        if not await client.connect():
            print("Failed to connect to Gmail")
            return

        try:
            # Fetch new messages
            messages = await client.fetch_new_messages(subject_filter="Dell Bocca Boys")

            for msg in messages:
                print(f"\n{'='*60}")
                print(f"From: {msg.from_address}")
                print(f"Subject: {msg.subject}")
                print(f"Received: {msg.received_at}")
                print(f"Body:\n{msg.body_text[:200]}...")

        finally:
            await client.disconnect()

    # Run example
    asyncio.run(main())
