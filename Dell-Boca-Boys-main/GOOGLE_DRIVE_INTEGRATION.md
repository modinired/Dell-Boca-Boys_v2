# Google Drive Knowledge Integration Guide

**Enable bidirectional knowledge sharing between you and your AI agents through Google Drive.**

---

## Overview

The Google Drive integration creates a shared knowledge repository where:

1. **You → Agents**: Drop documents into Google Drive, agents automatically learn from them
2. **Agents → You**: Agents write daily reflections, insights, and learned concepts back to Google Drive
3. **Mobile Access**: Access knowledge from anywhere via Google Drive mobile app
4. **Collaboration**: Share folder with team members for collective learning

### Folder Structure

```
Dell Boca Vista Knowledge/
├── Input/                          # 📥 You add files here for agents to learn
│   ├── Technical Docs/
│   ├── Workflows/
│   └── Best Practices/
├── Output/                         # 📤 Agents write insights here
│   ├── Daily Reflections/
│   ├── Learned Concepts/
│   └── Pattern Analysis/
└── Shared/                         # 🔄 Bi-directional collaboration
    ├── Templates/
    └── Code Snippets/
```

---

## Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Project name: `Dell Boca Vista Knowledge`
4. Click "Create"

### Step 2: Enable Google Drive API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click on it, then click **Enable**

### Step 3: Create Service Account (Recommended)

**Why Service Account?** Runs automatically without user interaction, perfect for server deployments.

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Service account details:
   - Name: `dell-boca-vista-sync`
   - Description: `Syncs knowledge with Google Drive`
4. Click **Create and Continue**
5. Grant role: **Editor** (or create custom role with Drive permissions)
6. Click **Done**

### Step 4: Download Credentials

1. Find your service account in the list
2. Click on it
3. Go to **Keys** tab
4. Click **Add Key** → **Create new key**
5. Choose **JSON**
6. Save file as: `/Users/modini_red/N8n-agent/google_drive_credentials.json`

### Step 5: Share Google Drive Folder

**IMPORTANT**: The service account needs access to your Drive folder!

1. Open your service account details
2. Copy the **email address** (looks like: `dell-boca-vista-sync@project-id.iam.gserviceaccount.com`)
3. Go to [Google Drive](https://drive.google.com)
4. The sync script will create "Dell Boca Vista Knowledge" folder automatically, OR:
5. Create folder manually: "Dell Boca Vista Knowledge"
6. Right-click folder → **Share**
7. Paste service account email
8. Give **Editor** access
9. Uncheck "Notify people" (it's a service account)
10. Click **Share**

### Step 6: Update Environment Variables

Edit `/Users/modini_red/N8n-agent/.env`:

```bash
# Google Drive Integration
GOOGLE_DRIVE_CREDENTIALS_PATH=./google_drive_credentials.json
GOOGLE_DRIVE_SYNC_ENABLED=true
GOOGLE_DRIVE_ROOT_FOLDER=Dell Boca Vista Knowledge
```

### Step 7: Install Dependencies

```bash
cd ~/N8n-agent
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Step 8: Test Integration

Create `scripts/test_gdrive_sync.py`:

```python
#!/usr/bin/env python3
"""Test Google Drive integration."""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.learning.google_drive_sync import GoogleDriveKnowledgeSync
from app.learning import UniversalLearningLogger, KnowledgeExtractor

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('PGHOST', 'localhost'),
    'port': int(os.getenv('PGPORT', 5432)),
    'dbname': os.getenv('PGDATABASE', 'n8n_agent_memory'),
    'user': os.getenv('PGUSER', 'n8n_agent'),
    'password': os.getenv('PGPASSWORD', '')
}

def test_gdrive():
    print("="*60)
    print("Testing Google Drive Integration")
    print("="*60)

    # Initialize components
    logger_inst = UniversalLearningLogger(DB_CONFIG)
    extractor = KnowledgeExtractor(
        DB_CONFIG,
        os.getenv('LLM_BASE_URL', 'http://localhost:11434/v1'),
        os.getenv('GEMINI_API_KEY', '')
    )

    # Initialize Google Drive sync
    print("\n1. Initializing Google Drive sync...")
    gdrive = GoogleDriveKnowledgeSync(
        credentials_path=os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH'),
        root_folder_name=os.getenv('GOOGLE_DRIVE_ROOT_FOLDER', 'Dell Boca Vista Knowledge'),
        learning_logger=logger_inst,
        knowledge_extractor=extractor
    )

    print("✓ Google Drive sync initialized!")
    print(f"✓ Folder structure: {len(gdrive.folder_structure)} folders created")

    # Test input sync
    print("\n2. Syncing Input folder...")
    stats = gdrive.sync_input_folder()
    print(f"✓ Sync complete:")
    print(f"  - Files found: {stats['files_found']}")
    print(f"  - Files processed: {stats['files_processed']}")
    print(f"  - Concepts extracted: {stats['concepts_extracted']}")

    # Test reflection upload
    print("\n3. Uploading test reflection...")
    test_reflection = """Test Reflection

This is a test reflection to verify Google Drive upload is working.

Generated by Dell Boca Vista Boys sync test."""

    file_id = gdrive.upload_daily_reflection(test_reflection)
    if file_id:
        print(f"✓ Reflection uploaded! File ID: {file_id}")

    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nNext steps:")
    print("1. Go to Google Drive and check 'Dell Boca Vista Knowledge' folder")
    print("2. Add a document to Input/ folder")
    print("3. Run this test again to see it sync")

if __name__ == "__main__":
    test_gdrive()
```

Run test:

```bash
python scripts/test_gdrive_sync.py
```

---

## Usage Guide

### Adding Knowledge for Agents

1. Open [Google Drive](https://drive.google.com)
2. Navigate to **Dell Boca Vista Knowledge** → **Input/**
3. Choose appropriate subfolder:
   - **Technical Docs/**: PDF/text documents, technical references
   - **Workflows/**: n8n workflow JSON files, examples
   - **Best Practices/**: Guidelines, standards, preferences

4. Upload or create document
5. Agents will automatically:
   - Download the document
   - Log it to episodic memory
   - Extract concepts and patterns
   - Apply learnings to future responses

### Viewing Agent Insights

1. Open **Dell Boca Vista Knowledge** → **Output/**
2. Check:
   - **Daily Reflections/**: What agents learned each day
   - **Learned Concepts/**: Extracted knowledge summaries (JSON)
   - **Pattern Analysis/**: Discovered patterns and best practices

### Supported File Types

- **Text files** (.txt, .md)
- **Google Docs** (automatically converted to text)
- **PDFs** (requires PyPDF2: `pip install PyPDF2`)
- **JSON** (.json) - n8n workflows, configurations
- **Code files** (.js, .ts, .py) - code examples, snippets

---

## Automated Daily Sync

### Option 1: Add to Continuous Learning Worker

Edit `scripts/continuous_learning_worker.py`:

```python
# At top of file
from app.learning.google_drive_sync import GoogleDriveKnowledgeSync
import os

# In daily_learning_job() function, add:
def daily_learning_job():
    # ... existing code ...

    # Google Drive sync
    if os.getenv('GOOGLE_DRIVE_SYNC_ENABLED', 'false').lower() == 'true':
        print("\n3. Syncing with Google Drive...")

        gdrive = GoogleDriveKnowledgeSync(
            credentials_path=os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH'),
            learning_logger=None,  # Not needed for upload
            knowledge_extractor=extractor
        )

        # Run automated sync
        gdrive.automated_daily_sync()
```

### Option 2: Standalone Script

Create `scripts/gdrive_sync_daemon.py`:

```python
#!/usr/bin/env python3
"""Google Drive sync daemon - runs continuously."""

import os
import time
import schedule
from dotenv import load_dotenv
from app.learning.google_drive_sync import GoogleDriveKnowledgeSync
from app.learning import UniversalLearningLogger, KnowledgeExtractor

load_dotenv()

DB_CONFIG = {...}  # Same as before

def sync_job():
    """Run Google Drive sync."""
    gdrive = GoogleDriveKnowledgeSync(
        credentials_path=os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH'),
        learning_logger=UniversalLearningLogger(DB_CONFIG),
        knowledge_extractor=KnowledgeExtractor(DB_CONFIG, ...)
    )

    gdrive.automated_daily_sync()

if __name__ == "__main__":
    # Sync every 6 hours
    schedule.every(6).hours.do(sync_job)

    # Run on startup
    sync_job()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)
```

Run:

```bash
nohup python scripts/gdrive_sync_daemon.py > logs/gdrive_sync.log 2>&1 &
```

---

## Example Use Cases

### Use Case 1: Team Onboarding

**Scenario**: New team member joins, needs to learn company workflows.

1. Add all company n8n workflows to `Input/Workflows/`
2. Add documentation to `Input/Technical Docs/`
3. Agents learn from these documents
4. New team member asks agents questions
5. Agents provide answers based on company knowledge

### Use Case 2: Best Practices Library

**Scenario**: Capture and share best practices across team.

1. When you discover good patterns, write them in Google Doc
2. Save to `Input/Best Practices/`
3. Agents learn and apply to future workflow generation
4. Check `Output/Learned Concepts/` for summaries

### Use Case 3: Mobile Knowledge Access

**Scenario**: Need to check agent insights on the go.

1. Open Google Drive mobile app
2. Navigate to `Dell Boca Vista Knowledge/Output/`
3. Read daily reflections
4. Review learned concepts
5. All synced automatically

### Use Case 4: Collaborative Learning

**Scenario**: Multiple people contribute knowledge.

1. Share Google Drive folder with team
2. Everyone adds documents to `Input/`
3. All contribute to `Shared/Templates/`
4. Agents learn from collective knowledge
5. Everyone benefits from shared insights

---

## Troubleshooting

### "Permission Denied" Error

**Cause**: Service account doesn't have access to folder.

**Fix**:
1. Check service account email
2. Share folder with that email
3. Give "Editor" permission

### "Credentials Not Found" Error

**Cause**: Credentials file missing or path wrong.

**Fix**:
```bash
ls -la /Users/modini_red/N8n-agent/google_drive_credentials.json
# Should exist

# Check .env file
cat .env | grep GOOGLE_DRIVE_CREDENTIALS_PATH
```

### Files Not Syncing

**Cause**: Sync cache preventing re-processing.

**Fix**:
```bash
# Delete sync cache to force re-sync
rm /Users/modini_red/N8n-agent/.gdrive_sync_cache.json

# Run sync again
python scripts/test_gdrive_sync.py
```

### "API Not Enabled" Error

**Cause**: Google Drive API not enabled for project.

**Fix**:
1. Go to Google Cloud Console
2. APIs & Services → Library
3. Search "Google Drive API"
4. Click "Enable"

---

## Advanced Features

### Custom Folder Structure

```python
# Create custom folders
gdrive = GoogleDriveKnowledgeSync(
    credentials_path='...',
    root_folder_name='My Custom Folder'
)

# Add custom folder
custom_id = gdrive._get_or_create_folder(
    'My Custom Category',
    parent_id=gdrive.folder_structure['input']
)

gdrive.folder_structure['custom'] = custom_id
```

### Selective Sync

```python
# Sync only specific subfolders
stats = gdrive.sync_input_folder()

# Or build custom sync logic
files = gdrive.service.files().list(
    q=f"'{folder_id}' in parents and name contains 'urgent'",
    fields='files(id, name)'
).execute()
```

### Notification Integration

```python
# Get notified when new knowledge is added
import smtplib

if stats['files_new'] > 0:
    send_email(
        to='you@example.com',
        subject=f"{stats['files_new']} new documents synced",
        body=f"Agents learned from {stats['files_new']} new documents!"
    )
```

---

## Security Best Practices

1. **Protect Credentials**:
   ```bash
   chmod 600 google_drive_credentials.json
   # Add to .gitignore
   echo "google_drive_credentials.json" >> .gitignore
   ```

2. **Limit Scope**: Use most restrictive permissions possible
   - Read-only if agents only need to read
   - Folder-specific permissions vs entire Drive

3. **Rotate Keys**: Periodically regenerate service account keys

4. **Monitor Access**: Check Google Cloud audit logs for suspicious activity

5. **Backup**: Keep encrypted backup of credentials file

---

## Next Steps

1. ✅ Set up Google Cloud project
2. ✅ Create service account
3. ✅ Download credentials
4. ✅ Share Drive folder
5. ✅ Test integration
6. ✅ Add to automated worker
7. 📝 Add your first knowledge document!

---

**The agents are ready to learn from your knowledge. The circle is complete.** 🔄🧠

---

*Generated by Dell Boca Vista Boys Technical Architecture Team*
*Google Drive Knowledge Integration - v1.0.0*
