"""
Dell Bocca Boys Email Communication Service

Main entry point for email-based agent communication.
Coordinates email monitoring, task routing, and response handling.

Official Agent Email: ace.llc.nyc@gmail.com
Subject Filter: "Dell Bocca Boys"

Usage:
    python email_service.py

Environment Variables:
    AGENT_EMAIL: Gmail address (default: ace.llc.nyc@gmail.com)
    AGENT_EMAIL_PASSWORD: Gmail app password (required)
    EMAIL_POLL_INTERVAL: Seconds between inbox checks (default: 60)
    EMAIL_SERVICE_ENABLED: Enable/disable email service (default: true)
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Dict, Optional

# Setup path for imports
PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from core.communication.email_client import GmailEmailClient
from core.communication.email_monitor import EmailMonitorService
from core.communication.email_task_router import get_email_task_router

logger = logging.getLogger(__name__)


class DellBoccaBoysEmailService:
    """
    Main email communication service for Dell Bocca Boys agents.

    Orchestrates:
    - Email monitoring (checks inbox for "Dell Bocca Boys" emails)
    - Task routing (routes tasks to CESAR agents)
    - Response handling (sends email replies back to users)
    """

    def __init__(
        self,
        email_address: Optional[str] = None,
        password: Optional[str] = None,
        poll_interval: Optional[int] = None
    ):
        """
        Initialize Dell Bocca Boys email service.

        Args:
            email_address: Gmail address (defaults to env or ace.llc.nyc@gmail.com)
            password: Gmail app password (defaults to env)
            poll_interval: Seconds between inbox checks (defaults to env or 60)
        """
        # Configuration
        self.email_address = email_address or os.getenv(
            "AGENT_EMAIL", "ace.llc.nyc@gmail.com"
        )
        self.password = password or os.getenv("AGENT_EMAIL_PASSWORD")
        self.poll_interval = poll_interval or int(os.getenv("EMAIL_POLL_INTERVAL", "60"))

        # Validate configuration
        if not self.password:
            raise ValueError(
                "Gmail app password is required. Set AGENT_EMAIL_PASSWORD environment variable."
            )

        # Initialize components
        self.email_client = GmailEmailClient(
            email_address=self.email_address,
            password=self.password
        )

        self.email_monitor: Optional[EmailMonitorService] = None
        self._task_router = None
        self._shutdown_event = asyncio.Event()

        logger.info(
            f"Dell Bocca Boys Email Service initialized for {self.email_address}"
        )

    async def start(self):
        """Start the email communication service."""
        logger.info("=" * 60)
        logger.info("Starting Dell Bocca Boys Email Communication Service")
        logger.info("=" * 60)
        logger.info(f"Agent Email: {self.email_address}")
        logger.info(f"Poll Interval: {self.poll_interval} seconds")
        logger.info(f"Subject Filter: 'Dell Bocca Boys'")
        logger.info("=" * 60)

        try:
            # Initialize task router
            logger.info("Initializing email task router...")
            self._task_router = await get_email_task_router()
            logger.info("Email task router ready")

            # Create email monitor with task handler
            logger.info("Creating email monitor service...")
            self.email_monitor = EmailMonitorService(
                email_client=self.email_client,
                poll_interval=self.poll_interval,
                task_handler=self._handle_email_task
            )

            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()

            # Start monitoring
            logger.info("Starting email monitoring...")
            await self.email_monitor.start()

            logger.info("")
            logger.info("✓ Email Communication Service is now ACTIVE")
            logger.info("✓ Monitoring inbox for 'Dell Bocca Boys' emails")
            logger.info("✓ Ready to receive and process user tasks")
            logger.info("")

            # Wait until shutdown signal
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"Failed to start email service: {e}", exc_info=True)
            raise

        finally:
            await self.stop()

    async def stop(self):
        """Stop the email communication service."""
        logger.info("Stopping Dell Bocca Boys Email Communication Service...")

        if self.email_monitor and self.email_monitor.is_running:
            await self.email_monitor.stop()

        logger.info("Dell Bocca Boys Email Communication Service stopped")

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(sig):
            logger.info(f"Received signal {sig}, initiating graceful shutdown...")
            self._shutdown_event.set()

        # Register signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                signal.signal(sig, lambda s, f: signal_handler(s))

    async def _handle_email_task(self, task_context: Dict) -> str:
        """
        Handle incoming email task by routing to agents.

        Args:
            task_context: Dictionary with email and task information

        Returns:
            Response text to send back to user
        """
        try:
            logger.info(
                f"Processing email task from {task_context['from_address']}: "
                f"{task_context['task_description'][:100]}..."
            )

            # Route task to appropriate agents
            response = await self._task_router.route_task(task_context)

            logger.info(
                f"Task processed successfully for {task_context['from_address']}"
            )

            return response

        except Exception as e:
            logger.error(f"Error handling email task: {e}", exc_info=True)
            return f"An error occurred while processing your task: {str(e)}"

    @property
    def is_running(self) -> bool:
        """Check if email service is running."""
        return self.email_monitor and self.email_monitor.is_running

    def get_stats(self) -> Dict:
        """Get service statistics."""
        stats = {
            "service_running": self.is_running,
            "email_address": self.email_address,
            "poll_interval": self.poll_interval
        }

        if self.email_monitor:
            stats.update(self.email_monitor.stats)

        return stats


async def main():
    """Main entry point for email service."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("dell_bocca_boys_email_service.log")
        ]
    )

    # Check if service is enabled
    if os.getenv("EMAIL_SERVICE_ENABLED", "true").lower() == "false":
        logger.info("Email service is disabled (EMAIL_SERVICE_ENABLED=false)")
        return

    # Create and start service
    try:
        service = DellBoccaBoysEmailService()
        await service.start()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("")
        logger.error("Please set the following environment variables:")
        logger.error("  AGENT_EMAIL_PASSWORD: Your Gmail app password")
        logger.error("")
        logger.error("Optional environment variables:")
        logger.error("  AGENT_EMAIL: Gmail address (default: ace.llc.nyc@gmail.com)")
        logger.error("  EMAIL_POLL_INTERVAL: Seconds between checks (default: 60)")
        logger.error("  EMAIL_SERVICE_ENABLED: Enable/disable service (default: true)")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
