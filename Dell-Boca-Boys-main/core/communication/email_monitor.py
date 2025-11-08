"""
Email Monitoring Service for Dell Bocca Boys Agents

This service continuously monitors the agent email inbox for new messages
with subject "Dell Bocca Boys" and routes them to appropriate agents for processing.

Features:
- Continuous monitoring with configurable polling intervals
- Automatic task routing to CESAR agents
- Email response handling
- Error recovery and retry logic
- Graceful shutdown
"""

import asyncio
import logging
import signal
from datetime import datetime
from typing import Callable, Dict, List, Optional

from .email_client import EmailMessage, GmailEmailClient

logger = logging.getLogger(__name__)


class EmailMonitorService:
    """
    Email monitoring service for Dell Bocca Boys agent communication.

    Monitors the agent email inbox for new messages with subject "Dell Bocca Boys"
    and routes them to appropriate agents for processing.
    """

    def __init__(
        self,
        email_client: Optional[GmailEmailClient] = None,
        poll_interval: int = 60,
        task_handler: Optional[Callable] = None
    ):
        """
        Initialize email monitoring service.

        Args:
            email_client: Gmail email client (creates new if not provided)
            poll_interval: Seconds between inbox checks (default: 60)
            task_handler: Async function to handle incoming email tasks
        """
        self.email_client = email_client or GmailEmailClient()
        self.poll_interval = poll_interval
        self.task_handler = task_handler

        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._processed_message_ids: set = set()

    async def start(self):
        """Start the email monitoring service."""
        if self._running:
            logger.warning("Email monitor is already running")
            return

        logger.info("Starting Dell Bocca Boys email monitoring service...")

        # Connect to Gmail
        connected = await self.email_client.connect()
        if not connected:
            logger.error("Failed to connect to Gmail. Email monitoring not started.")
            return

        self._running = True

        # Start monitoring loop
        self._monitor_task = asyncio.create_task(self._monitor_loop())

        logger.info(
            f"Email monitoring service started. "
            f"Checking inbox every {self.poll_interval} seconds for 'Dell Bocca Boys' emails."
        )

    async def stop(self):
        """Stop the email monitoring service."""
        if not self._running:
            logger.warning("Email monitor is not running")
            return

        logger.info("Stopping email monitoring service...")
        self._running = False

        # Cancel monitoring task
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        # Disconnect from Gmail
        await self.email_client.disconnect()

        logger.info("Email monitoring service stopped")

    async def _monitor_loop(self):
        """Main monitoring loop that checks for new emails."""
        consecutive_errors = 0
        max_consecutive_errors = 5

        while self._running:
            try:
                # Fetch new messages
                messages = await self.email_client.fetch_new_messages(
                    subject_filter="Dell Bocca Boys"
                )

                # Process each new message
                for message in messages:
                    # Skip if already processed
                    if message.message_id in self._processed_message_ids:
                        continue

                    # Process message
                    await self._process_message(message)

                    # Mark as processed
                    self._processed_message_ids.add(message.message_id)

                # Reset error counter on successful check
                consecutive_errors = 0

                # Wait before next check
                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                logger.info("Monitor loop cancelled")
                break

            except Exception as e:
                consecutive_errors += 1
                logger.error(
                    f"Error in email monitor loop (attempt {consecutive_errors}/{max_consecutive_errors}): {e}",
                    exc_info=True
                )

                # If too many consecutive errors, stop monitoring
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical(
                        f"Too many consecutive errors ({max_consecutive_errors}). "
                        "Stopping email monitoring service."
                    )
                    self._running = False
                    break

                # Wait before retrying
                await asyncio.sleep(min(self.poll_interval, 30))

    async def _process_message(self, message: EmailMessage):
        """
        Process an incoming email message.

        Args:
            message: EmailMessage object to process
        """
        logger.info(
            f"Processing email from {message.from_address} - Subject: {message.subject}"
        )

        try:
            # Extract task from email body
            task_description = self._extract_task_from_email(message)

            if not task_description:
                logger.warning(f"Could not extract task from email {message.message_id}")
                await self._send_error_response(
                    message,
                    "I couldn't understand your request. Please provide a clear task description."
                )
                return

            # Route task to handler
            if self.task_handler:
                await self._route_task_to_handler(message, task_description)
            else:
                logger.warning(
                    "No task handler configured. Email received but not processed."
                )
                await self._send_error_response(
                    message,
                    "Email monitoring is active but task processing is not configured. "
                    "Please contact the system administrator."
                )

        except Exception as e:
            logger.error(f"Error processing email {message.message_id}: {e}", exc_info=True)
            await self._send_error_response(
                message,
                f"An error occurred while processing your request: {str(e)}"
            )

    def _extract_task_from_email(self, message: EmailMessage) -> Optional[str]:
        """
        Extract task description from email body.

        Args:
            message: EmailMessage object

        Returns:
            Task description string or None if extraction failed
        """
        body = message.body_text.strip()

        if not body:
            return None

        # Remove email signatures and quoted replies
        lines = body.split("\n")
        clean_lines = []

        for line in lines:
            # Stop at common signature markers
            if line.strip() in ["--", "___", "Sent from my iPhone", "Sent from my Android"]:
                break

            # Skip quoted replies
            if line.startswith(">") or line.startswith("On ") and "wrote:" in line:
                continue

            clean_lines.append(line)

        task_description = "\n".join(clean_lines).strip()

        # Basic validation
        if len(task_description) < 10:
            return None

        return task_description

    async def _route_task_to_handler(self, message: EmailMessage, task_description: str):
        """
        Route task to the configured task handler.

        Args:
            message: EmailMessage object
            task_description: Extracted task description
        """
        try:
            # Call task handler with context
            task_context = {
                "message_id": message.message_id,
                "from_address": message.from_address,
                "subject": message.subject,
                "received_at": message.received_at,
                "task_description": task_description
            }

            # Handler should return response text
            response = await self.task_handler(task_context)

            # Send response email
            if response:
                await self._send_success_response(message, response)
            else:
                logger.warning("Task handler returned no response")

        except Exception as e:
            logger.error(f"Error routing task to handler: {e}", exc_info=True)
            raise

    async def _send_success_response(self, original_message: EmailMessage, response: str):
        """
        Send successful task completion response.

        Args:
            original_message: Original email message
            response: Response text from agent
        """
        # Prepare subject
        subject = f"Re: {original_message.subject}"

        # Create response body
        body = f"""Hello,

{response}

---
Dell Bocca Boys Agent Team
Processed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Task ID: {original_message.message_id}
"""

        # Update references for threading
        references = original_message.references or []
        if original_message.message_id not in references:
            references.append(original_message.message_id)

        # Send reply
        success = await self.email_client.send_reply(
            to_address=original_message.from_address,
            subject=subject,
            body_text=body,
            in_reply_to=original_message.message_id,
            references=references
        )

        if success:
            logger.info(f"Sent success response to {original_message.from_address}")
        else:
            logger.error(f"Failed to send response to {original_message.from_address}")

    async def _send_error_response(self, original_message: EmailMessage, error_message: str):
        """
        Send error response to user.

        Args:
            original_message: Original email message
            error_message: Error message to send
        """
        # Prepare subject
        subject = f"Re: {original_message.subject}"

        # Create error response body
        body = f"""Hello,

I encountered an issue processing your request:

{error_message}

Please try again or contact support if the problem persists.

---
Dell Bocca Boys Agent Team
Processed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Task ID: {original_message.message_id}
"""

        # Update references for threading
        references = original_message.references or []
        if original_message.message_id not in references:
            references.append(original_message.message_id)

        # Send reply
        await self.email_client.send_reply(
            to_address=original_message.from_address,
            subject=subject,
            body_text=body,
            in_reply_to=original_message.message_id,
            references=references
        )

    @property
    def is_running(self) -> bool:
        """Check if monitoring service is running."""
        return self._running

    @property
    def stats(self) -> Dict:
        """Get monitoring statistics."""
        return {
            "is_running": self._running,
            "poll_interval": self.poll_interval,
            "processed_messages": len(self._processed_message_ids),
            "agent_email": self.email_client.email_address
        }


async def create_email_monitor_with_shutdown_handler(
    task_handler: Callable,
    poll_interval: int = 60
) -> EmailMonitorService:
    """
    Create email monitor service with graceful shutdown on SIGINT/SIGTERM.

    Args:
        task_handler: Async function to handle incoming email tasks
        poll_interval: Seconds between inbox checks

    Returns:
        EmailMonitorService instance
    """
    monitor = EmailMonitorService(
        poll_interval=poll_interval,
        task_handler=task_handler
    )

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def signal_handler(sig):
        logger.info(f"Received signal {sig}, initiating graceful shutdown...")
        asyncio.create_task(monitor.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))

    return monitor


if __name__ == "__main__":
    # Example usage
    async def example_task_handler(task_context: Dict) -> str:
        """
        Example task handler that echoes the task back.

        Args:
            task_context: Dictionary with email and task information

        Returns:
            Response string to send back to user
        """
        task = task_context["task_description"]
        from_addr = task_context["from_address"]

        logger.info(f"Handling task from {from_addr}: {task[:100]}...")

        # Simulate processing
        await asyncio.sleep(2)

        return f"I received your task: '{task[:100]}...'\n\nThis is a test response."

    async def main():
        # Create monitor with example handler
        monitor = await create_email_monitor_with_shutdown_handler(
            task_handler=example_task_handler,
            poll_interval=30  # Check every 30 seconds
        )

        # Start monitoring
        await monitor.start()

        # Keep running until interrupted
        try:
            while monitor.is_running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        # Ensure stopped
        if monitor.is_running:
            await monitor.stop()

    # Run example
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
