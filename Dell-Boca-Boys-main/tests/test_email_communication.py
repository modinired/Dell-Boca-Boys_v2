"""
Integration Tests for Dell Bocca Boys Email Communication System

Tests cover:
- Email client connection and authentication
- Email monitoring and message fetching
- Task classification and routing
- Response formatting and sending
- Error handling and recovery
"""

import asyncio
import logging
import os
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path

# Setup path for imports
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from core.communication.email_client import EmailMessage, GmailEmailClient
from core.communication.email_monitor import EmailMonitorService
from core.communication.email_task_router import (
    EmailTask,
    EmailTaskRouter,
    TaskPriority,
    TaskType,
)
from core.communication.email_service import DellBoccaBoysEmailService


class TestEmailClient(unittest.TestCase):
    """Test Gmail email client functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.email_address = "test@gmail.com"
        self.password = "test-password"

    def test_email_message_is_from_user(self):
        """Test EmailMessage.is_from_user property."""
        # Test with "Dell Bocca Boys"
        msg1 = EmailMessage(
            message_id="<test1@example.com>",
            from_address="user@example.com",
            to_address="agent@example.com",
            subject="Dell Bocca Boys - Question",
            body_text="Test message",
            body_html=None,
            received_at=datetime.utcnow()
        )
        self.assertTrue(msg1.is_from_user)

        # Test with "Dell Boca Boys" (alternative spelling)
        msg2 = EmailMessage(
            message_id="<test2@example.com>",
            from_address="user@example.com",
            to_address="agent@example.com",
            subject="Dell Boca Boys - Question",
            body_text="Test message",
            body_html=None,
            received_at=datetime.utcnow()
        )
        self.assertTrue(msg2.is_from_user)

        # Test without subject filter
        msg3 = EmailMessage(
            message_id="<test3@example.com>",
            from_address="user@example.com",
            to_address="agent@example.com",
            subject="Random Subject",
            body_text="Test message",
            body_html=None,
            received_at=datetime.utcnow()
        )
        self.assertFalse(msg3.is_from_user)

    def test_gmail_client_initialization(self):
        """Test Gmail client initialization."""
        client = GmailEmailClient(
            email_address=self.email_address,
            password=self.password
        )

        self.assertEqual(client.email_address, self.email_address)
        self.assertEqual(client.password, self.password)
        self.assertFalse(client.use_oauth)
        self.assertIsNone(client._imap_client)

    def test_gmail_client_env_defaults(self):
        """Test Gmail client uses environment defaults."""
        with patch.dict(os.environ, {
            "AGENT_EMAIL": "env@gmail.com",
            "AGENT_EMAIL_PASSWORD": "env-password"
        }):
            client = GmailEmailClient()
            self.assertEqual(client.email_address, "env@gmail.com")
            self.assertEqual(client.password, "env-password")

    @patch('core.communication.email_client.aioimaplib.AIOIMAP4_SSL')
    async def test_connect_success(self, mock_imap):
        """Test successful connection to Gmail."""
        # Setup mock
        mock_instance = AsyncMock()
        mock_instance.wait_hello_from_server = AsyncMock()
        mock_instance.login = AsyncMock(return_value=("OK", []))
        mock_imap.return_value = mock_instance

        # Test connection
        client = GmailEmailClient(
            email_address=self.email_address,
            password=self.password
        )
        success = await client.connect()

        self.assertTrue(success)
        mock_instance.login.assert_called_once_with(
            self.email_address,
            self.password
        )

    def test_extract_body_plain_text(self):
        """Test extracting plain text email body."""
        import email
        from email.mime.text import MIMEText

        # Create test email
        msg = MIMEText("This is a plain text email body")
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Subject"] = "Test"

        # Extract body
        client = GmailEmailClient()
        body_text, body_html = client._extract_body(msg)

        self.assertEqual(body_text, "This is a plain text email body")
        self.assertIsNone(body_html)


class TestEmailTaskRouter(unittest.TestCase):
    """Test email task routing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = EmailTaskRouter()

    def test_classify_task_type_question(self):
        """Test classification of question tasks."""
        # Test with question mark
        self.assertEqual(
            self.router._classify_task_type("What is Python?"),
            TaskType.QUESTION
        )

        # Test with question words
        self.assertEqual(
            self.router._classify_task_type("How do I implement binary search?"),
            TaskType.QUESTION
        )

        self.assertEqual(
            self.router._classify_task_type("Can you explain decorators?"),
            TaskType.QUESTION
        )

    def test_classify_task_type_coding(self):
        """Test classification of coding tasks."""
        self.assertEqual(
            self.router._classify_task_type("Write a function to parse JSON"),
            TaskType.CODING
        )

        self.assertEqual(
            self.router._classify_task_type("Debug this code snippet"),
            TaskType.CODING
        )

        self.assertEqual(
            self.router._classify_task_type("Implement an API endpoint"),
            TaskType.CODING
        )

    def test_classify_task_type_analysis(self):
        """Test classification of analysis tasks."""
        self.assertEqual(
            self.router._classify_task_type("Analyze the performance metrics"),
            TaskType.ANALYSIS
        )

        self.assertEqual(
            self.router._classify_task_type("Evaluate these options"),
            TaskType.ANALYSIS
        )

    def test_classify_task_type_research(self):
        """Test classification of research tasks."""
        self.assertEqual(
            self.router._classify_task_type("Research best practices for API design"),
            TaskType.RESEARCH
        )

        self.assertEqual(
            self.router._classify_task_type("Find out about microservices patterns"),
            TaskType.RESEARCH
        )

    def test_classify_task_type_planning(self):
        """Test classification of planning tasks."""
        self.assertEqual(
            self.router._classify_task_type("Plan a migration strategy"),
            TaskType.PLANNING
        )

        self.assertEqual(
            self.router._classify_task_type("Design the system architecture"),
            TaskType.PLANNING
        )

    def test_classify_task_type_review(self):
        """Test classification of review tasks."""
        self.assertEqual(
            self.router._classify_task_type("Review this pull request"),
            TaskType.REVIEW
        )

        self.assertEqual(
            self.router._classify_task_type("Check the code quality"),
            TaskType.REVIEW
        )

    def test_classify_priority_urgent(self):
        """Test classification of urgent priority."""
        self.assertEqual(
            self.router._classify_priority("URGENT: Fix the bug"),
            TaskPriority.URGENT
        )

        self.assertEqual(
            self.router._classify_priority("Need this ASAP"),
            TaskPriority.URGENT
        )

        self.assertEqual(
            self.router._classify_priority("This is critical!"),
            TaskPriority.URGENT
        )

    def test_classify_priority_high(self):
        """Test classification of high priority."""
        self.assertEqual(
            self.router._classify_priority("This is important"),
            TaskPriority.HIGH
        )

        self.assertEqual(
            self.router._classify_priority("Need this quickly"),
            TaskPriority.HIGH
        )

    def test_classify_priority_low(self):
        """Test classification of low priority."""
        self.assertEqual(
            self.router._classify_priority("No rush, whenever you can"),
            TaskPriority.LOW
        )

        self.assertEqual(
            self.router._classify_priority("Low priority task"),
            TaskPriority.LOW
        )

    def test_classify_priority_medium_default(self):
        """Test default medium priority classification."""
        self.assertEqual(
            self.router._classify_priority("Just a regular task"),
            TaskPriority.MEDIUM
        )

    async def test_parse_task(self):
        """Test task parsing from email context."""
        task_context = {
            "message_id": "<test@example.com>",
            "from_address": "user@example.com",
            "subject": "Dell Bocca Boys - Question",
            "received_at": datetime.utcnow(),
            "task_description": "How do I use asyncio in Python?"
        }

        task = await self.router._parse_task(task_context)

        self.assertEqual(task.task_type, TaskType.QUESTION)
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.from_address, "user@example.com")
        self.assertIn("asyncio", task.description)

    def test_format_response(self):
        """Test response formatting for email."""
        task = EmailTask(
            task_id="test_task_001",
            task_type=TaskType.QUESTION,
            priority=TaskPriority.MEDIUM,
            description="Test task description",
            from_address="user@example.com",
            message_id="<test@example.com>",
            received_at=datetime.utcnow(),
            context={}
        )

        response = {
            "response": "Here is your answer to the question.",
            "agents_consulted": ["terry_delmonaco", "victoria_sterling"]
        }

        formatted = self.router._format_response(task, response)

        self.assertIn("Thank you for your request", formatted)
        self.assertIn("Here is your answer", formatted)
        self.assertIn("terry_delmonaco", formatted)
        self.assertIn("victoria_sterling", formatted)
        self.assertIn("Task Type: Question", formatted)
        self.assertIn("Priority: MEDIUM", formatted)
        self.assertIn("test_task_001", formatted)

    def test_format_error_response(self):
        """Test error response formatting."""
        task = EmailTask(
            task_id="test_task_002",
            task_type=TaskType.CODING,
            priority=TaskPriority.HIGH,
            description="Test task",
            from_address="user@example.com",
            message_id="<test@example.com>",
            received_at=datetime.utcnow(),
            context={}
        )

        error_msg = "Connection timeout"
        formatted = self.router._format_error_response(task, error_msg)

        self.assertIn("error", formatted.lower())
        self.assertIn("Connection timeout", formatted)
        self.assertIn("test_task_002", formatted)


class TestEmailMonitor(unittest.TestCase):
    """Test email monitoring service."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock(spec=GmailEmailClient)
        self.mock_client.email_address = "test@gmail.com"

    async def test_monitor_initialization(self):
        """Test monitor service initialization."""
        monitor = EmailMonitorService(
            email_client=self.mock_client,
            poll_interval=30
        )

        self.assertEqual(monitor.poll_interval, 30)
        self.assertFalse(monitor.is_running)
        self.assertEqual(monitor.email_client, self.mock_client)

    async def test_extract_task_from_email(self):
        """Test task extraction from email message."""
        monitor = EmailMonitorService(email_client=self.mock_client)

        # Test simple email
        msg1 = EmailMessage(
            message_id="<test1@example.com>",
            from_address="user@example.com",
            to_address="agent@example.com",
            subject="Dell Bocca Boys - Task",
            body_text="Please help me with Python coding.",
            body_html=None,
            received_at=datetime.utcnow()
        )

        task1 = monitor._extract_task_from_email(msg1)
        self.assertEqual(task1, "Please help me with Python coding.")

        # Test email with signature
        msg2 = EmailMessage(
            message_id="<test2@example.com>",
            from_address="user@example.com",
            to_address="agent@example.com",
            subject="Dell Bocca Boys - Task",
            body_text="Please help me.\n\n--\nJohn Doe\nSoftware Engineer",
            body_html=None,
            received_at=datetime.utcnow()
        )

        task2 = monitor._extract_task_from_email(msg2)
        self.assertEqual(task2, "Please help me.")

        # Test empty email
        msg3 = EmailMessage(
            message_id="<test3@example.com>",
            from_address="user@example.com",
            to_address="agent@example.com",
            subject="Dell Bocca Boys",
            body_text="",
            body_html=None,
            received_at=datetime.utcnow()
        )

        task3 = monitor._extract_task_from_email(msg3)
        self.assertIsNone(task3)

    def test_monitor_stats(self):
        """Test monitor statistics."""
        monitor = EmailMonitorService(email_client=self.mock_client)

        stats = monitor.stats

        self.assertIn("is_running", stats)
        self.assertIn("poll_interval", stats)
        self.assertIn("agent_email", stats)
        self.assertEqual(stats["agent_email"], "test@gmail.com")
        self.assertEqual(stats["poll_interval"], 60)


class TestEmailService(unittest.TestCase):
    """Test main email service."""

    def test_service_initialization(self):
        """Test service initialization."""
        with patch.dict(os.environ, {
            "AGENT_EMAIL": "test@gmail.com",
            "AGENT_EMAIL_PASSWORD": "test-password"
        }):
            service = DellBoccaBoysEmailService()

            self.assertEqual(service.email_address, "test@gmail.com")
            self.assertEqual(service.password, "test-password")
            self.assertEqual(service.poll_interval, 60)
            self.assertIsNotNone(service.email_client)

    def test_service_missing_password(self):
        """Test service fails without password."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                DellBoccaBoysEmailService()

    def test_service_custom_config(self):
        """Test service with custom configuration."""
        service = DellBoccaBoysEmailService(
            email_address="custom@gmail.com",
            password="custom-password",
            poll_interval=30
        )

        self.assertEqual(service.email_address, "custom@gmail.com")
        self.assertEqual(service.password, "custom-password")
        self.assertEqual(service.poll_interval, 30)

    def test_service_stats(self):
        """Test service statistics."""
        with patch.dict(os.environ, {
            "AGENT_EMAIL_PASSWORD": "test-password"
        }):
            service = DellBoccaBoysEmailService()
            stats = service.get_stats()

            self.assertIn("service_running", stats)
            self.assertIn("email_address", stats)
            self.assertIn("poll_interval", stats)
            self.assertFalse(stats["service_running"])


def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == "__main__":
    # Setup logging for tests
    logging.basicConfig(level=logging.DEBUG)

    # Run tests
    unittest.main()
