"""
Dell Bocca Boys Email Communication Module

Enables agents to communicate with users via email.

Official Agent Email: ace.llc.nyc@gmail.com
Subject Filter: "Dell Bocca Boys"

Components:
- email_client: Gmail client for reading and sending emails
- email_monitor: Service that monitors inbox for new emails
- email_task_router: Routes tasks to appropriate CESAR agents
- email_service: Main service coordinator

Usage:
    from core.communication import DellBoccaBoysEmailService

    service = DellBoccaBoysEmailService()
    await service.start()
"""

from .email_client import (
    GmailEmailClient,
    EmailMessage,
    send_agent_email
)

from .email_monitor import (
    EmailMonitorService,
    create_email_monitor_with_shutdown_handler
)

from .email_task_router import (
    EmailTaskRouter,
    EmailTask,
    TaskType,
    TaskPriority,
    get_email_task_router
)

from .email_service import DellBoccaBoysEmailService

__all__ = [
    # Email Client
    "GmailEmailClient",
    "EmailMessage",
    "send_agent_email",

    # Email Monitor
    "EmailMonitorService",
    "create_email_monitor_with_shutdown_handler",

    # Email Task Router
    "EmailTaskRouter",
    "EmailTask",
    "TaskType",
    "TaskPriority",
    "get_email_task_router",

    # Main Service
    "DellBoccaBoysEmailService"
]
