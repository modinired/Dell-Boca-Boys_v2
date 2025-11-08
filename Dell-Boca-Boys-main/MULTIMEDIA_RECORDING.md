# Multimedia Recording Integration

## Overview

The N8n-agent now includes comprehensive multimedia recording capabilities for enhanced workflow documentation and daily summaries. This system captures both visual (screenshots/screen recordings) and audio data, with automatic transcription support.

---

## Features

### Screen Recording
- **Screenshots**: Capture individual screen states
- **Screen Recordings**: Sequential screenshot capture at configurable intervals
- **Multi-Monitor Support**: Record from specific monitors or all monitors
- **Organized Storage**: Automatically organized by date

### Audio Recording
- **Microphone Recording**: Capture audio from system microphone
- **WAV Format**: High-quality 16kHz mono audio
- **Automatic Transcription**: Speech-to-text using OpenAI Whisper
- **Organized Storage**: Automatically organized by date

### Journal Integration
- **Multimedia Summaries**: Recordings automatically included in daily/weekly/monthly summaries
- **Interaction Logging**: Screenshots and audio linked to specific workflow interactions
- **Reflective Summaries**: Chiccki includes multimedia observations in daily reflections

---

## Installation

### Required Dependencies

```bash
# Screen recording
pip install mss pillow

# Audio recording
pip install pyaudio

# Audio transcription (optional, requires OpenAI API key)
pip install openai
```

### Platform-Specific Notes

**macOS**:
```bash
brew install portaudio
pip install pyaudio
```

**Linux**:
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Windows**:
```bash
pip install pyaudio
```

---

## Configuration

### Environment Variables

```bash
# Code workspace (recordings stored in workspace/recordings/)
CODE_WORKSPACE=/path/to/workspace

# OpenAI API key for transcription (optional)
OPENAI_API_KEY=sk-...
```

### Directory Structure

Recordings are automatically organized:

```
workspace/
└── recordings/
    ├── screenshots/
    │   ├── 2025-01-15/
    │   │   ├── screenshot_10-30-00.png
    │   │   └── screenshot_14-25-10.png
    │   └── 2025-01-16/
    │       └── screenshot_09-15-30.png
    ├── audio/
    │   ├── 2025-01-15/
    │   │   ├── meeting_notes_10-30-00.wav
    │   │   └── workflow_demo_14-25-10.wav
    │   └── transcriptions/
    │       └── 2025-01-15/
    │           ├── meeting_notes_10-30-00_transcription.json
    │           └── workflow_demo_14-25-10_transcription.json
    └── 2025-01-15/
        └── workflow_test_1/
            ├── frame_001.png
            ├── frame_002.png
            └── frame_003.png
```

---

## API Endpoints

### Screen Recording

#### Capture Screenshot
```http
POST /api/v1/recording/screenshot
```

**Request:**
```json
{
  "monitor": 1,
  "description": "Workflow execution screenshot"
}
```

**Response:**
```json
{
  "success": true,
  "filepath": "/workspace/recordings/screenshots/2025-01-15/screenshot_10-30-00.png",
  "timestamp": "2025-01-15T10:30:00",
  "monitor": 1,
  "width": 1920,
  "height": 1080,
  "description": "Workflow execution screenshot"
}
```

#### Start Screen Recording
```http
POST /api/v1/recording/screen/start
```

**Request:**
```json
{
  "recording_id": "workflow_test_1",
  "monitor": 1,
  "interval_seconds": 2.0,
  "description": "Testing order processing workflow"
}
```

**Response:**
```json
{
  "success": true,
  "recording_id": "workflow_test_1",
  "session": {
    "recording_id": "workflow_test_1",
    "monitor": 1,
    "interval_seconds": 2.0,
    "start_time": "2025-01-15T10:30:00",
    "frame_count": 0
  }
}
```

#### Capture Recording Frame
```http
POST /api/v1/recording/screen/{recording_id}/capture-frame
```

**Response:**
```json
{
  "success": true,
  "filepath": "/workspace/recordings/2025-01-15/workflow_test_1/frame_001.png",
  "timestamp": "2025-01-15T10:30:02",
  "frame_number": 1
}
```

#### Stop Screen Recording
```http
POST /api/v1/recording/screen/{recording_id}/stop
```

**Response:**
```json
{
  "success": true,
  "recording_id": "workflow_test_1",
  "session": {
    "recording_id": "workflow_test_1",
    "start_time": "2025-01-15T10:30:00",
    "end_time": "2025-01-15T10:32:00",
    "duration_seconds": 120,
    "frame_count": 60
  }
}
```

---

### Audio Recording

#### Start Audio Recording
```http
POST /api/v1/recording/audio/start?recording_id=meeting_notes_1&description=Daily standup
```

**Response:**
```json
{
  "success": true,
  "recording_id": "meeting_notes_1",
  "filepath": "/workspace/recordings/audio/2025-01-15/meeting_notes_1_10-30-00.wav",
  "start_time": "2025-01-15T10:30:00"
}
```

#### Capture Audio Chunk
```http
POST /api/v1/recording/audio/{recording_id}/capture-chunk
```

**Response:**
```json
{
  "success": true,
  "chunk_number": 10,
  "chunk_size": 1024
}
```

**Note**: Call this endpoint repeatedly (e.g., in a loop) to continuously capture audio during recording.

#### Stop Audio Recording
```http
POST /api/v1/recording/audio/{recording_id}/stop
```

**Response:**
```json
{
  "success": true,
  "recording_id": "meeting_notes_1",
  "filepath": "/workspace/recordings/audio/2025-01-15/meeting_notes_1_10-30-00.wav",
  "duration_seconds": 120,
  "file_size_bytes": 3840000,
  "file_size_mb": 3.66,
  "chunks_captured": 120
}
```

#### Transcribe Audio
```http
POST /api/v1/recording/audio/transcribe
```

**Request:**
```json
{
  "audio_filepath": "/workspace/recordings/audio/2025-01-15/meeting_notes_1_10-30-00.wav",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "transcription": "Today we discussed the new order processing workflow. The team agreed to implement error handling for invalid customer data...",
  "transcription_filepath": "/workspace/recordings/audio/transcriptions/2025-01-15/meeting_notes_1_10-30-00_transcription.json",
  "audio_filepath": "/workspace/recordings/audio/2025-01-15/meeting_notes_1_10-30-00.wav",
  "language": "en",
  "character_count": 150
}
```

---

### Statistics and Summaries

#### Get Recording Stats
```http
GET /api/v1/recording/stats
```

**Response:**
```json
{
  "success": true,
  "screen_recordings": {
    "total_recordings": 5,
    "total_screenshots": 42,
    "total_size_mb": 15.3,
    "active_recordings": 0,
    "dates_with_recordings": ["2025-01-15", "2025-01-16"],
    "recordings_dir": "/workspace/recordings"
  },
  "audio_recordings": {
    "total_recordings": 3,
    "total_transcriptions": 2,
    "total_size_mb": 12.5,
    "active_recordings": 0,
    "dates_with_recordings": ["2025-01-15"],
    "recordings_dir": "/workspace/recordings/audio"
  }
}
```

#### Get Multimedia Summary for Journal Period
```http
GET /api/v1/journal/multimedia/daily?reference_date=2025-01-15
```

**Response:**
```json
{
  "success": true,
  "multimedia_summary": {
    "period": "daily",
    "start_date": "2025-01-15",
    "end_date": "2025-01-16",
    "screenshots": [
      {
        "filepath": "/workspace/recordings/screenshots/2025-01-15/screenshot_10-30-00.png",
        "timestamp": "2025-01-15 10:30:00",
        "size_bytes": 524288
      }
    ],
    "audio_recordings": [
      {
        "filepath": "/workspace/recordings/audio/2025-01-15/meeting_notes_1_10-30-00.wav",
        "transcription": "Today we discussed...",
        "size_mb": 3.66
      }
    ],
    "total_screenshots": 42,
    "total_audio_recordings": 3,
    "total_transcriptions": 2
  }
}
```

---

## Python API

### Screen Recorder

```python
from app.tools.screen_recorder import screen_recorder

# Capture screenshot
result = screen_recorder.capture_screenshot(
    monitor=1,
    save=True,
    description="Workflow execution"
)
print(f"Screenshot saved to: {result['filepath']}")

# Start screen recording
session = screen_recorder.start_recording(
    recording_id="demo_1",
    monitor=1,
    interval_seconds=2.0,
    description="Demo recording"
)

# Capture frames (call repeatedly)
for i in range(30):
    screen_recorder.capture_recording_frame("demo_1")
    time.sleep(2)

# Stop recording
summary = screen_recorder.stop_recording("demo_1")
print(f"Captured {summary['session']['frame_count']} frames")

# Get recordings for today
recordings = screen_recorder.get_screenshots_for_date()
print(f"Today's screenshots: {len(recordings)}")
```

### Audio Recorder

```python
from app.tools.audio_recorder import audio_recorder
import time

# Start audio recording
result = audio_recorder.start_recording(
    recording_id="meeting_1",
    description="Team standup"
)
print(f"Recording to: {result['filepath']}")

# Capture audio (call repeatedly while recording)
for i in range(120):  # Record for 2 minutes
    audio_recorder.capture_audio_chunk("meeting_1")
    time.sleep(1)

# Stop recording
summary = audio_recorder.stop_recording("meeting_1")
print(f"Recording duration: {summary['duration_seconds']}s")

# Transcribe the recording
transcription = audio_recorder.transcribe_audio(
    audio_filepath=summary['filepath'],
    language="en"
)
print(f"Transcription: {transcription['transcription']}")

# Get recordings for today
recordings = audio_recorder.get_recordings_for_date()
for rec in recordings:
    print(f"- {rec['filename']}: {rec['size_mb']}MB")
    if rec['transcription']:
        print(f"  Transcription: {rec['transcription'][:100]}...")
```

### Journal Integration

```python
from app.tools.journal import daily_journal, InteractionRecord

# Log interaction with multimedia
record = InteractionRecord(
    user_goal="Create order processing workflow",
    persona="default",
    success=True,
    workflow_id="workflow_123",
    summary="Created robust workflow with error handling",
    qa_score=0.95,
    node_count=12,
    auto_stage=True,
    auto_activate=False,
    metadata={},
    screenshots=[
        "/workspace/recordings/screenshots/2025-01-15/screenshot_10-30-00.png",
        "/workspace/recordings/screenshots/2025-01-15/screenshot_10-35-00.png"
    ],
    audio_recordings=[
        "/workspace/recordings/audio/2025-01-15/meeting_notes_1_10-30-00.wav"
    ],
    transcriptions=[
        "Discussed workflow requirements and error handling strategies..."
    ]
)

daily_journal.log_interaction(record)

# Generate daily summary with multimedia
summary = daily_journal.generate_summary(period="daily")
print(summary['summary'])
print(summary['daily_thought'])

# Get multimedia summary
multimedia = daily_journal.get_multimedia_summary(period="daily")
print(f"Screenshots: {multimedia['total_screenshots']}")
print(f"Audio recordings: {multimedia['total_audio_recordings']}")
print(f"Transcriptions: {multimedia['total_transcriptions']}")
```

---

## Use Cases

### 1. Workflow Documentation

Capture screenshots during workflow execution to document the process:

```python
# Before workflow execution
screen_recorder.capture_screenshot(
    monitor=1,
    description="Initial state before workflow"
)

# Execute workflow
face_agent.generate_workflow(...)

# After workflow execution
screen_recorder.capture_screenshot(
    monitor=1,
    description="Final state after workflow"
)
```

### 2. Meeting Notes with Audio

Record team meetings and automatically transcribe:

```python
# Start recording
audio_recorder.start_recording(
    recording_id="standup_2025_01_15",
    description="Daily standup meeting"
)

# During meeting, capture chunks
while meeting_in_progress:
    audio_recorder.capture_audio_chunk("standup_2025_01_15")
    time.sleep(1)

# Stop and transcribe
summary = audio_recorder.stop_recording("standup_2025_01_15")
transcription = audio_recorder.transcribe_audio(summary['filepath'])

# Save transcription to knowledge base
memory.add_document(
    content=transcription['transcription'],
    source="meeting_notes",
    title="Daily Standup - 2025-01-15"
)
```

### 3. Automated Workflow Testing

Record screen activity during automated tests:

```python
# Start screen recording
screen_recorder.start_recording(
    recording_id="test_order_workflow",
    monitor=1,
    interval_seconds=1.0,
    description="Testing order processing workflow"
)

# Run automated test
while test_running:
    # Capture frame every second
    screen_recorder.capture_recording_frame("test_order_workflow")
    time.sleep(1)

# Stop recording
summary = screen_recorder.stop_recording("test_order_workflow")
print(f"Test recording: {summary['session']['frame_count']} frames in {summary['session']['duration_seconds']}s")
```

### 4. Daily Summary with Multimedia

Generate comprehensive daily summaries including all multimedia:

```python
from datetime import date

# Generate daily summary
summary = daily_journal.generate_summary(
    period="daily",
    reference_date=date.today()
)

# Get multimedia summary
multimedia = daily_journal.get_multimedia_summary(
    period="daily",
    reference_date=date.today()
)

print("=== Daily Summary ===")
print(summary['summary'])
print("\n=== Chiccki's Reflection ===")
print(summary['daily_thought'])
print("\n=== Multimedia Activity ===")
print(f"Screenshots: {multimedia['total_screenshots']}")
print(f"Audio Recordings: {multimedia['total_audio_recordings']}")
print(f"Transcriptions: {multimedia['total_transcriptions']}")

# List all screenshots
for screenshot in multimedia['screenshots']:
    print(f"  - {screenshot['timestamp']}: {screenshot['filepath']}")

# List all audio recordings with transcriptions
for recording in multimedia['audio_recordings']:
    print(f"  - {recording['filename']}: {recording['size_mb']}MB")
    if recording['transcription']:
        print(f"    Transcription: {recording['transcription'][:100]}...")
```

---

## smolagents Tools

The multimedia recording features are also available as smolagents tools:

```python
from app.tools.screen_recorder import (
    capture_screenshot,
    start_screen_recording,
    capture_recording_frame,
    stop_screen_recording,
    get_todays_screenshots,
    get_screen_recording_stats
)

from app.tools.audio_recorder import (
    start_audio_recording,
    capture_audio_chunk,
    stop_audio_recording,
    transcribe_audio_file,
    get_todays_audio_recordings,
    get_audio_recording_stats
)

# Use in agent context
result = capture_screenshot(monitor=1, description="Workflow state")
```

---

## Database Schema Updates

The journal system has been updated to store multimedia references:

```sql
-- interaction_logs table now includes:
screenshots JSONB DEFAULT '[]'::jsonb,
audio_recordings JSONB DEFAULT '[]'::jsonb,
transcriptions JSONB DEFAULT '[]'::jsonb

-- journal_summaries table now includes:
multimedia_summary JSONB DEFAULT '{}'::jsonb
```

---

## Best Practices

### 1. Descriptive Naming
Use descriptive recording IDs and descriptions:
```python
# Good
recording_id="order_workflow_test_2025_01_15"
description="Testing order processing with error handling"

# Bad
recording_id="test1"
description="test"
```

### 2. Resource Management
Stop recordings when done to free resources:
```python
try:
    audio_recorder.start_recording("demo")
    # ... capture audio ...
finally:
    audio_recorder.stop_recording("demo")
```

### 3. Storage Management
Periodically clean up old recordings:
```python
from pathlib import Path
import shutil
from datetime import datetime, timedelta

# Delete recordings older than 30 days
recordings_dir = Path(settings.code_workspace) / "recordings"
cutoff_date = datetime.now() - timedelta(days=30)

for date_dir in recordings_dir.glob("*/2*"):
    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
    if dir_date < cutoff_date:
        shutil.rmtree(date_dir)
```

### 4. Transcription Costs
Be mindful of OpenAI Whisper API costs:
- Only transcribe important recordings
- Use language parameter when known to improve accuracy
- Consider batch processing transcriptions

---

## Troubleshooting

### Screen Recording Issues

**Problem**: `mss library not available`

**Solution**:
```bash
pip install mss pillow
```

**Problem**: Permission denied on macOS

**Solution**: Grant screen recording permissions in System Preferences → Security & Privacy → Privacy → Screen Recording

### Audio Recording Issues

**Problem**: `pyaudio library not available`

**Solution**:
```bash
# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Problem**: No audio input detected

**Solution**: Check microphone permissions and ensure a microphone is connected

### Transcription Issues

**Problem**: `OPENAI_API_KEY environment variable not set`

**Solution**:
```bash
export OPENAI_API_KEY=sk-...
```

**Problem**: Transcription fails with error

**Solution**: Ensure audio file is in supported format (WAV, MP3, etc.) and not corrupted

---

## Performance Considerations

### Screen Recording
- Screenshots are compressed PNG files (typically 500KB-2MB each)
- Recording at 1 frame/second for 1 hour = ~1.8GB
- Consider adjusting `interval_seconds` based on needs

### Audio Recording
- 16kHz mono WAV audio = ~1.9MB per minute
- 1 hour recording = ~115MB
- Transcription via Whisper API: ~$0.006 per minute

### Storage Recommendations
- Monitor disk space regularly
- Implement automatic cleanup of old recordings
- Consider compression for long-term storage

---

## Future Enhancements

Potential improvements for future versions:

1. **Video Recording**: Full video capture instead of sequential screenshots
2. **Cloud Storage**: Integration with S3/GCS for recordings
3. **Automatic Highlighting**: AI-powered detection of important moments
4. **Speaker Diarization**: Identify different speakers in audio transcriptions
5. **Real-time Transcription**: Live transcription during recording
6. **Searchable Transcriptions**: Full-text search across all transcriptions
7. **Annotation Support**: Add notes and markers to recordings

---

## Summary

The multimedia recording integration provides comprehensive documentation capabilities for the N8n-agent system:

✅ **Screen Recording**: Capture visual workflow states
✅ **Audio Recording**: Record meetings and commentary
✅ **Automatic Transcription**: Convert speech to searchable text
✅ **Journal Integration**: Link recordings to workflow interactions
✅ **Daily Summaries**: Include multimedia in reflective summaries
✅ **REST API**: Full API coverage for all features
✅ **Python API**: Direct access for scripting
✅ **smolagents Tools**: Integration with agent framework

The system is production-ready with proper error handling, organized storage, and comprehensive documentation.
