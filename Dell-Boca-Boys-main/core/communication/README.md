# Dell Bocca Boys Email Communication

> Enable agents to communicate with users through email

## Quick Start

**Official Agent Email:** `ace.llc.nyc@gmail.com`

### 1. Setup Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Generate an App Password for "Mail"
4. Copy the 16-character password

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your password
nano .env
```

Set in `.env`:
```bash
AGENT_EMAIL_PASSWORD="your-16-char-app-password"
```

### 3. Install Dependencies

```bash
pip install aioimaplib aiosmtplib
```

### 4. Start the Service

```bash
# Using the startup script
./start_email_service.sh

# Or directly with Python
python core/communication/email_service.py
```

## How It Works

1. **User sends email** to `ace.llc.nyc@gmail.com` with subject "Dell Bocca Boys"
2. **Service monitors inbox** and detects new emails
3. **Task router classifies** the task and determines priority
4. **CESAR agents process** the task collaboratively
5. **Response sent back** to user via email

## Sending Emails to Agents

### Basic Email

```
To: ace.llc.nyc@gmail.com
Subject: Dell Bocca Boys - My Question

How do I implement a binary search algorithm in Python?
```

### Urgent Task

```
To: ace.llc.nyc@gmail.com
Subject: Dell Bocca Boys - URGENT

URGENT: Production bug in authentication system.
Users getting "Invalid token" errors.
```

## Task Types

The system automatically routes tasks to appropriate agents:

| Type | Keywords | Example |
|------|----------|---------|
| **Question** | what, how, why, explain | "How does async/await work?" |
| **Coding** | code, implement, debug | "Write a Python script to parse CSV" |
| **Analysis** | analyze, evaluate, assess | "Analyze these performance metrics" |
| **Research** | research, investigate | "Research microservices patterns" |
| **Planning** | plan, design, strategy | "Plan a database migration" |
| **Review** | review, check, validate | "Review this code for security issues" |

## Response Format

```
Thank you for your request!

[Agent response here]

---
Agents consulted:
  • terry_delmonaco
  • victoria_sterling

---
Task Type: Question
Priority: MEDIUM
Task ID: email_task_20250107_143052
Processed: 2025-01-07 14:30:55 UTC
```

## Configuration

Environment variables in `.env`:

```bash
# Required
AGENT_EMAIL_PASSWORD="your-app-password"

# Optional
AGENT_EMAIL="ace.llc.nyc@gmail.com"
EMAIL_POLL_INTERVAL="60"  # seconds
EMAIL_SERVICE_ENABLED="true"
```

## Architecture

```
📧 User Email
    ↓
📥 Email Client (IMAP)
    ↓
🔍 Email Monitor
    ↓
🧭 Task Router
    ↓
🤖 CESAR Agents (6 specialists)
    ↓
📤 Response Handler (SMTP)
    ↓
📨 User Reply
```

## Programmatic Usage

### Send Email from Code

```python
from core.communication import send_agent_email

# Quick send
success = await send_agent_email(
    to_address="user@example.com",
    subject="Task Complete",
    body="Your analysis is ready!"
)
```

### Custom Integration

```python
from core.communication import DellBoccaBoysEmailService

async def main():
    service = DellBoccaBoysEmailService(
        poll_interval=30  # Check every 30 seconds
    )
    await service.start()

asyncio.run(main())
```

## Testing

Run integration tests:

```bash
python -m pytest tests/test_email_communication.py -v
```

## Troubleshooting

### "Failed to connect to Gmail"

- Verify `AGENT_EMAIL_PASSWORD` is correct
- Ensure 2-Step Verification is enabled
- Check that app password hasn't been revoked
- Verify IMAP is enabled in Gmail settings

### "No response to emails"

- Check subject includes "Dell Bocca Boys"
- Verify service is running (check logs)
- Check spam folder
- Look at `dell_bocca_boys_email_service.log`

### "Authentication failed"

- Regenerate Gmail app password
- Ensure no typos in `.env` file
- Check account isn't locked

## Documentation

Full documentation: [EMAIL_COMMUNICATION_GUIDE.md](../../docs/EMAIL_COMMUNICATION_GUIDE.md)

## Security

- ✅ Use app passwords (never real password)
- ✅ Store credentials in `.env` (not version control)
- ✅ Rotate app passwords regularly
- ✅ Monitor logs for suspicious activity
- ✅ Only "Dell Bocca Boys" subject emails processed

## Support

- **Documentation**: `docs/EMAIL_COMMUNICATION_GUIDE.md`
- **Tests**: `tests/test_email_communication.py`
- **Logs**: `dell_bocca_boys_email_service.log`

## Components

- `email_client.py` - Gmail IMAP/SMTP client
- `email_monitor.py` - Inbox monitoring service
- `email_task_router.py` - Task classification and routing
- `email_service.py` - Main service coordinator

---

**Version**: 1.0.0
**Last Updated**: 2025-01-07
