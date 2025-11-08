# Dell Bocca Boys Email Communication Guide

## Overview

The Dell Bocca Boys agents can now communicate with users through email! This guide covers setup, usage, and best practices for email-based agent communication.

**Official Agent Email:** `ace.llc.nyc@gmail.com`
**Subject Filter:** "Dell Bocca Boys"

## Features

- **Automated Email Monitoring**: Continuously monitors inbox for emails with subject "Dell Bocca Boys"
- **Intelligent Task Routing**: Routes tasks to appropriate CESAR agents based on content
- **Multi-Agent Collaboration**: Leverages the full CESAR network for comprehensive responses
- **Priority Detection**: Automatically detects urgent tasks and prioritizes accordingly
- **Email Threading**: Maintains proper email threads with replies
- **Error Handling**: Robust error recovery and user-friendly error messages

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Sends Email                         │
│              Subject: "Dell Bocca Boys"                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Gmail Email Client (IMAP)                      │
│  - Connects to ace.llc.nyc@gmail.com                       │
│  - Fetches emails with subject "Dell Bocca Boys"           │
│  - Parses email content and metadata                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Email Monitor Service                            │
│  - Polls inbox every 60 seconds (configurable)             │
│  - Extracts task description from email body                │
│  - Tracks processed messages to avoid duplicates            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            Email Task Router                                │
│  - Classifies task type (question, coding, analysis, etc.) │
│  - Detects priority (low, medium, high, urgent)            │
│  - Routes to appropriate CESAR agents                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            CESAR Multi-Agent Network                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Terry Delmonaco    - Technical & Quantitative       │  │
│  │ Victoria Sterling  - Strategic Operations           │  │
│  │ Marcus Chen        - Systems Architecture           │  │
│  │ Isabella Rodriguez - Creative Innovation            │  │
│  │ Eleanor Blackwood  - Academic Research              │  │
│  │ James O'Connor     - Project Management             │  │
│  └──────────────────────────────────────────────────────┘  │
│  - Agents collaborate based on task requirements            │
│  - Generate comprehensive, expert-level responses           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         Email Response Handler (SMTP)                       │
│  - Formats agent response for email                        │
│  - Maintains email threading                                │
│  - Sends reply to user                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                User Receives Response                       │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Gmail App Password

For security, use a Gmail App Password instead of your regular password:

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification**
3. Enable 2-Step Verification if not already enabled
4. Go to **App passwords**
5. Generate a new app password for "Mail"
6. Copy the 16-character password

### 2. Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# Required
AGENT_EMAIL_PASSWORD="your-gmail-app-password"

# Optional (defaults shown)
AGENT_EMAIL="ace.llc.nyc@gmail.com"
EMAIL_POLL_INTERVAL="60"
EMAIL_SERVICE_ENABLED="true"
```

### 3. Install Dependencies

```bash
pip install aioimaplib aiosmtplib
```

### 4. Start the Email Service

```bash
# From the repository root
python core/communication/email_service.py

# Or using Python module syntax
python -m core.communication.email_service
```

You should see output like:

```
============================================================
Starting Dell Bocca Boys Email Communication Service
============================================================
Agent Email: ace.llc.nyc@gmail.com
Poll Interval: 60 seconds
Subject Filter: 'Dell Bocca Boys'
============================================================
✓ Email Communication Service is now ACTIVE
✓ Monitoring inbox for 'Dell Bocca Boys' emails
✓ Ready to receive and process user tasks
```

## Usage

### Sending Emails to Agents

To communicate with the Dell Bocca Boys agents:

1. **Compose an email** to `ace.llc.nyc@gmail.com`
2. **Set the subject** to include "Dell Bocca Boys"
3. **Write your task** in the email body
4. **Send the email**
5. **Wait for the response** (typically within 1-2 minutes)

### Email Subject Examples

Valid subject lines that will be processed:

- "Dell Bocca Boys"
- "Dell Bocca Boys - Question about Python"
- "Urgent: Dell Bocca Boys Task"
- "Dell Boca Boys" (alternative spelling accepted)

### Task Types

The system automatically classifies your email into one of these task types:

| Task Type | Description | Example | Lead Agent(s) |
|-----------|-------------|---------|---------------|
| **Question** | Questions requiring explanations | "How does binary search work?" | All agents via User Question Router |
| **Analysis** | Data analysis, evaluation, assessment | "Analyze the performance metrics" | Victoria Sterling, Terry Delmonaco |
| **Coding** | Implementation, debugging, refactoring | "Write a Python function to parse JSON" | Terry Delmonaco, Marcus Chen |
| **Research** | Information gathering, investigation | "Research best practices for API design" | Eleanor Blackwood, Victoria Sterling |
| **Planning** | Strategy, roadmaps, design | "Plan a microservices architecture" | James O'Connor, Victoria Sterling |
| **Review** | Code review, quality assurance | "Review this SQL query for security issues" | James O'Connor, Terry Delmonaco |
| **General** | Other tasks | Any task not matching above | Full CESAR committee |

### Priority Keywords

The system detects priority based on keywords in your email:

| Priority | Keywords | Response Time |
|----------|----------|---------------|
| **Urgent** | urgent, asap, emergency, critical, immediate | Highest priority |
| **High** | important, priority, quickly, soon, deadline | High priority |
| **Medium** | (default) | Normal priority |
| **Low** | whenever, no rush, low priority, when you can | Lower priority |

### Example Emails

#### Example 1: Simple Question

```
To: ace.llc.nyc@gmail.com
Subject: Dell Bocca Boys - Python Question

How do I read a CSV file in Python using pandas?
```

**Response:**
```
Thank you for your request!

To read a CSV file in Python using pandas, you can use the following approach:

import pandas as pd

# Read CSV file
df = pd.read_csv('your_file.csv')

# Display first few rows
print(df.head())

This is the most common way. The read_csv() function has many optional
parameters for handling different CSV formats...

---
Agents consulted:
  • terry_delmonaco
  • eleanor_blackwood

---
Task Type: Question
Priority: MEDIUM
Task ID: email_task_20250107_143052
Processed: 2025-01-07 14:30:55 UTC
```

#### Example 2: Urgent Coding Task

```
To: ace.llc.nyc@gmail.com
Subject: Dell Bocca Boys - URGENT: Bug Fix Needed

URGENT: Our authentication system is failing. Users cannot log in.
Need to fix ASAP. The error is "Invalid token signature".
```

**Response:**
```
Thank you for your request!

Terry here. He's looking at this authentication issue right away.
The "Invalid token signature" error typically indicates one of these problems:

1. Token Secret Mismatch: The secret used to sign the token doesn't match
   the secret used to verify it...

[Detailed analysis and solution from Terry Delmonaco and Marcus Chen]

---
Agents consulted:
  • terry_delmonaco
  • marcus_chen

---
Task Type: Coding
Priority: URGENT
Task ID: email_task_20250107_143102
Processed: 2025-01-07 14:31:05 UTC
```

#### Example 3: Strategic Planning

```
To: ace.llc.nyc@gmail.com
Subject: Dell Bocca Boys - Planning New Feature

We're planning to add a notification system to our app.
Need to design the architecture and choose the right tech stack.
The system should handle:
- Real-time notifications
- Email notifications
- Push notifications
- User preferences
```

**Response:**
```
Thank you for your request!

Let's architect this brilliantly, sweetheart. Here's our comprehensive
approach to your notification system:

**Strategic Architecture**
[Victoria Sterling's strategic analysis]

**Technical Implementation**
[Terry Delmonaco's technical recommendations]

**System Design**
[Marcus Chen's architectural patterns]

---
Agents consulted:
  • james_oconnor
  • victoria_sterling
  • marcus_chen
  • terry_delmonaco

---
Task Type: Planning
Priority: MEDIUM
Task ID: email_task_20250107_143112
Processed: 2025-01-07 14:31:15 UTC
```

## Advanced Features

### Email Threading

The system maintains proper email threading, so you can reply to agent responses and continue the conversation. Each reply will reference the previous messages, keeping the conversation organized in your email client.

### Automatic Retry Logic

If there are temporary network issues or Gmail API rate limits, the system automatically retries with exponential backoff to ensure reliable operation.

### Duplicate Prevention

The system tracks processed message IDs to prevent duplicate processing if the same email is fetched multiple times.

### Error Responses

If an error occurs while processing your task, you'll receive a user-friendly error message explaining what went wrong:

```
Hello,

I encountered an issue processing your request:

[Error description]

Please try again or contact support if the problem persists.

---
Dell Bocca Boys Agent Team
```

## Integration with Existing Systems

The email communication system integrates seamlessly with existing Dell Bocca Boys infrastructure:

- **CESAR Multi-Agent Network**: Routes tasks to specialized agents
- **User Question Router**: Handles questions with full agent collaboration
- **Agent Manager**: Manages agent lifecycle and performance
- **Memory System**: Stores email interactions for learning
- **WebSocket Manager**: Can notify connected clients of email activity

## Monitoring and Logs

### Log Files

The service logs all activity to:
- Console (stdout)
- `dell_bocca_boys_email_service.log`

### Log Levels

```python
# Set log level via environment
import logging
logging.basicConfig(level=logging.INFO)  # INFO, DEBUG, WARNING, ERROR
```

### Service Statistics

Get real-time statistics:

```python
from core.communication import DellBoccaBoysEmailService

service = DellBoccaBoysEmailService()
await service.start()

# Get stats
stats = service.get_stats()
print(stats)
# {
#   'service_running': True,
#   'email_address': 'ace.llc.nyc@gmail.com',
#   'poll_interval': 60,
#   'processed_messages': 15
# }
```

## Programmatic Usage

### As a Library

```python
from core.communication import DellBoccaBoysEmailService

async def main():
    # Create service with custom configuration
    service = DellBoccaBoysEmailService(
        email_address="custom@gmail.com",
        password="your-app-password",
        poll_interval=30  # Check every 30 seconds
    )

    # Start service
    await service.start()

main()
```

### Send Email from Agents

Agents can proactively send emails:

```python
from core.communication import send_agent_email

# Quick email sending
success = await send_agent_email(
    to_address="user@example.com",
    subject="Dell Bocca Boys - Task Complete",
    body="Your task has been completed successfully!"
)
```

### Custom Task Handler

```python
from core.communication import EmailMonitorService, GmailEmailClient

async def custom_task_handler(task_context):
    """Custom handler for email tasks."""
    task = task_context["task_description"]

    # Your custom processing logic
    response = f"Custom processing result for: {task}"

    return response

# Create monitor with custom handler
client = GmailEmailClient()
monitor = EmailMonitorService(
    email_client=client,
    poll_interval=60,
    task_handler=custom_task_handler
)

await monitor.start()
```

## Security Considerations

### App Passwords

- **Never commit passwords to version control**
- Use app passwords instead of account passwords
- Rotate app passwords regularly
- Revoke unused app passwords

### Email Content

- Agents do not store sensitive information in emails
- Emails are processed and then archived
- Use encryption for highly sensitive data
- Follow your organization's data handling policies

### Access Control

- Only emails with subject "Dell Bocca Boys" are processed
- Consider implementing sender whitelist if needed
- Monitor logs for suspicious activity

## Troubleshooting

### Service Won't Start

**Problem**: Service fails to connect to Gmail

**Solutions**:
1. Verify `AGENT_EMAIL_PASSWORD` is set correctly
2. Check that 2-Step Verification is enabled on Google Account
3. Ensure app password is valid (regenerate if needed)
4. Check internet connectivity
5. Verify Gmail IMAP is enabled in Gmail settings

### No Response to Emails

**Problem**: Emails are sent but no response received

**Solutions**:
1. Check email subject includes "Dell Bocca Boys"
2. Verify service is running (check logs)
3. Check spam/junk folder for responses
4. Verify sender email is not blocked
5. Check service logs for errors

### Delayed Responses

**Problem**: Responses take longer than expected

**Solutions**:
1. Decrease `EMAIL_POLL_INTERVAL` for faster checking
2. Check if CESAR network is properly initialized
3. Verify network latency is normal
4. Check CPU/memory usage on server

### Authentication Errors

**Problem**: IMAP login fails

**Solutions**:
1. Regenerate Gmail app password
2. Verify 2-Step Verification is enabled
3. Check for typos in email address
4. Try logging in via webmail to ensure account is not locked

## Performance Tuning

### Poll Interval

```bash
# Check more frequently (higher load)
EMAIL_POLL_INTERVAL="30"  # 30 seconds

# Check less frequently (lower load)
EMAIL_POLL_INTERVAL="120"  # 2 minutes
```

### Resource Usage

- **CPU**: Low (~2-5% during polling)
- **Memory**: ~100-200 MB depending on email volume
- **Network**: ~10-50 KB per poll cycle

### Scaling

For high email volumes:
1. Deploy multiple instances with different subject filters
2. Use message queuing for task distribution
3. Implement horizontal scaling with load balancers
4. Consider using Gmail API instead of IMAP for better performance

## Roadmap

Future enhancements planned:

- [ ] OAuth2 authentication support
- [ ] Attachment handling (documents, images, code files)
- [ ] Email templates for common responses
- [ ] Rich HTML email formatting
- [ ] Multi-language support
- [ ] Sender whitelist/blacklist
- [ ] Rate limiting per sender
- [ ] Email analytics dashboard
- [ ] Integration with Slack/Teams
- [ ] Calendar integration for scheduling tasks

## Support

For issues or questions:

1. Check this guide first
2. Review service logs
3. Check GitHub issues
4. Contact system administrator

## API Reference

See the following files for detailed API documentation:

- `core/communication/email_client.py` - Email client API
- `core/communication/email_monitor.py` - Monitoring service API
- `core/communication/email_task_router.py` - Task routing API
- `core/communication/email_service.py` - Main service API

## License

Part of the Dell Bocca Boys project. See main repository LICENSE file.

---

**Last Updated**: 2025-01-07
**Version**: 1.0.0
**Maintainer**: Dell Bocca Boys Team
