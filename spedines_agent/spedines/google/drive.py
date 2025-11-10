"""
Google Drive Ingestor
Automated ingestion of learning materials from Google Drive
"""

import logging
from typing import List, Dict, Optional, Any, Set
from datetime import datetime, timedelta
from pathlib import Path
import io
import time

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import hashlib

from .auth import GoogleAuthManager

logger = logging.getLogger(__name__)


class GoogleDriveIngestor:
    """
    Ingest files from Google Drive for learning

    Monitors a Drive folder and automatically downloads new files
    for processing and learning
    """

    # Supported file types
    SUPPORTED_MIMETYPES = {
        # Documents
        'application/pdf': '.pdf',
        'text/plain': '.txt',
        'text/markdown': '.md',
        'text/html': '.html',

        # Google Docs (export as PDF or text)
        'application/vnd.google-apps.document': '.docx',
        'application/vnd.google-apps.spreadsheet': '.xlsx',
        'application/vnd.google-apps.presentation': '.pptx',

        # Microsoft Office
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',

        # Code files
        'text/x-python': '.py',
        'text/javascript': '.js',
        'application/json': '.json',
        'text/x-java-source': '.java',
    }

    # Google Docs export MIME types
    GOOGLE_EXPORT_FORMATS = {
        'application/vnd.google-apps.document': 'application/pdf',
        'application/vnd.google-apps.spreadsheet': 'application/pdf',
        'application/vnd.google-apps.presentation': 'application/pdf',
    }

    def __init__(
        self,
        auth_manager: GoogleAuthManager,
        folder_id: str,
        download_dir: str,
        poll_interval_minutes: int = 60,
        max_file_size_mb: int = 50
    ):
        """
        Initialize Google Drive ingestor

        Args:
            auth_manager: GoogleAuthManager instance
            folder_id: Google Drive folder ID to monitor
            download_dir: Local directory to download files
            poll_interval_minutes: How often to check for new files
            max_file_size_mb: Maximum file size to download (MB)
        """

        self.auth_manager = auth_manager
        self.folder_id = folder_id
        self.download_dir = Path(download_dir)
        self.poll_interval_minutes = poll_interval_minutes
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

        # Create download directory
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Get Drive service
        self.drive_service = auth_manager.get_drive_service()

        logger.info(
            f"Initialized Drive ingestor: folder={folder_id}, "
            f"download_dir={download_dir}"
        )

        # Track processed files (by file ID)
        self.processed_files: Set[str] = set()
        self._load_processed_files()

        # Metrics
        self.files_downloaded = 0
        self.total_bytes_downloaded = 0
        self.errors = 0

    def _load_processed_files(self):
        """Load list of already processed files"""

        marker_file = self.download_dir / ".processed_files"

        if marker_file.exists():
            try:
                with open(marker_file, 'r') as f:
                    self.processed_files = set(line.strip() for line in f if line.strip())

                logger.info(f"Loaded {len(self.processed_files)} processed file IDs")

            except Exception as e:
                logger.error(f"Failed to load processed files list: {e}")

    def _save_processed_files(self):
        """Save list of processed files"""

        marker_file = self.download_dir / ".processed_files"

        try:
            with open(marker_file, 'w') as f:
                for file_id in sorted(self.processed_files):
                    f.write(f"{file_id}\n")

        except Exception as e:
            logger.error(f"Failed to save processed files list: {e}")

    def list_files(
        self,
        modified_since: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in monitored folder

        Args:
            modified_since: Only files modified after this time
            limit: Maximum number of files to return

        Returns:
            List of file metadata dictionaries
        """

        try:
            # Build query
            query = f"'{self.folder_id}' in parents and trashed = false"

            if modified_since:
                time_str = modified_since.isoformat().replace('+00:00', 'Z')
                query += f" and modifiedTime > '{time_str}'"

            # Fields to retrieve
            fields = (
                "nextPageToken, files(id, name, mimeType, size, createdTime, "
                "modifiedTime, md5Checksum, parents)"
            )

            # Execute query
            results = self.drive_service.files().list(
                q=query,
                pageSize=limit or 100,
                fields=fields,
                orderBy="createdTime desc"
            ).execute()

            files = results.get('files', [])

            logger.info(f"Found {len(files)} files in Drive folder")

            return files

        except HttpError as e:
            logger.error(f"Failed to list Drive files: {e}")
            self.errors += 1
            return []

        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            self.errors += 1
            return []

    def download_file(
        self,
        file_id: str,
        file_name: str,
        mime_type: str,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Download a file from Drive

        Args:
            file_id: Google Drive file ID
            file_name: File name
            mime_type: MIME type
            output_path: Optional custom output path

        Returns:
            Path to downloaded file or None if failed
        """

        try:
            # Check if supported
            if mime_type not in self.SUPPORTED_MIMETYPES:
                logger.warning(f"Unsupported MIME type: {mime_type} for {file_name}")
                return None

            # Determine output path
            if output_path is None:
                extension = self.SUPPORTED_MIMETYPES[mime_type]

                # Sanitize filename
                safe_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_', '.'))
                safe_name = safe_name.strip()

                # Ensure extension
                if not safe_name.endswith(extension):
                    safe_name += extension

                output_path = self.download_dir / safe_name

            # Check if Google Doc (needs export)
            if mime_type in self.GOOGLE_EXPORT_FORMATS:
                export_mime = self.GOOGLE_EXPORT_FORMATS[mime_type]

                logger.debug(f"Exporting Google Doc {file_name} as {export_mime}")

                request = self.drive_service.files().export_media(
                    fileId=file_id,
                    mimeType=export_mime
                )

            else:
                # Regular file download
                request = self.drive_service.files().get_media(fileId=file_id)

            # Download
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"Download progress: {int(status.progress() * 100)}%")

            # Check size limit
            file_size = fh.tell()
            if file_size > self.max_file_size_bytes:
                logger.warning(
                    f"File too large: {file_size / 1024 / 1024:.1f}MB "
                    f"(max: {self.max_file_size_bytes / 1024 / 1024:.1f}MB)"
                )
                return None

            # Write to file
            with open(output_path, 'wb') as f:
                f.write(fh.getvalue())

            self.files_downloaded += 1
            self.total_bytes_downloaded += file_size

            logger.info(
                f"Downloaded {file_name} ({file_size / 1024:.1f}KB) to {output_path}"
            )

            return output_path

        except HttpError as e:
            logger.error(f"HTTP error downloading {file_name}: {e}")
            self.errors += 1
            return None

        except Exception as e:
            logger.error(f"Failed to download {file_name}: {e}", exc_info=True)
            self.errors += 1
            return None

    def ingest_new_files(
        self,
        modified_since: Optional[datetime] = None,
        callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Ingest new files from Drive

        Args:
            modified_since: Only files modified after this time
            callback: Optional callback function(file_path, metadata)

        Returns:
            List of ingested file info dictionaries
        """

        logger.info("Checking for new files in Drive...")

        # List new files
        files = self.list_files(modified_since=modified_since)

        if not files:
            logger.info("No new files found")
            return []

        ingested = []

        for file_metadata in files:
            file_id = file_metadata['id']

            # Skip if already processed
            if file_id in self.processed_files:
                logger.debug(f"Skipping already processed file: {file_metadata['name']}")
                continue

            # Download file
            file_path = self.download_file(
                file_id=file_id,
                file_name=file_metadata['name'],
                mime_type=file_metadata['mimeType']
            )

            if file_path:
                # Mark as processed
                self.processed_files.add(file_id)
                self._save_processed_files()

                # Track ingestion
                ingestion_info = {
                    'file_id': file_id,
                    'file_name': file_metadata['name'],
                    'file_path': str(file_path),
                    'mime_type': file_metadata['mimeType'],
                    'size_bytes': file_metadata.get('size', 0),
                    'ingested_at': datetime.now().isoformat(),
                    'drive_created': file_metadata.get('createdTime'),
                    'drive_modified': file_metadata.get('modifiedTime')
                }

                ingested.append(ingestion_info)

                # Call callback if provided
                if callback:
                    try:
                        callback(file_path, ingestion_info)
                    except Exception as e:
                        logger.error(f"Callback error for {file_path}: {e}")

        logger.info(f"Ingested {len(ingested)} new files")

        return ingested

    def watch_folder(
        self,
        callback: callable,
        duration_minutes: Optional[int] = None
    ):
        """
        Continuously watch folder for new files

        Args:
            callback: Callback function(file_path, metadata) for each new file
            duration_minutes: How long to watch (None = forever)
        """

        logger.info(
            f"Starting Drive folder watch: poll every {self.poll_interval_minutes} minutes"
        )

        start_time = datetime.now()
        last_check = datetime.now() - timedelta(days=7)  # Look back 7 days initially

        while True:
            try:
                # Ingest new files
                ingested = self.ingest_new_files(
                    modified_since=last_check,
                    callback=callback
                )

                last_check = datetime.now()

                # Check if duration exceeded
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        logger.info(f"Watch duration reached: {duration_minutes} minutes")
                        break

                # Sleep until next poll
                logger.debug(f"Sleeping for {self.poll_interval_minutes} minutes...")
                time.sleep(self.poll_interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("Watch interrupted by user")
                break

            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)
                self.errors += 1

                # Sleep before retrying
                time.sleep(60)  # 1 minute backoff

    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific file

        Args:
            file_id: Google Drive file ID

        Returns:
            File metadata dictionary or None
        """

        try:
            file_metadata = self.drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, md5Checksum, parents"
            ).execute()

            return file_metadata

        except HttpError as e:
            logger.error(f"Failed to get file metadata: {e}")
            return None

    def delete_local_file(self, file_path: Path) -> bool:
        """
        Delete a downloaded file

        Args:
            file_path: Path to file

        Returns:
            True if deleted successfully
        """

        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted local file: {file_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete {file_path}: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get ingestor metrics"""

        return {
            "folder_id": self.folder_id,
            "download_dir": str(self.download_dir),
            "files_downloaded": self.files_downloaded,
            "total_bytes_downloaded": self.total_bytes_downloaded,
            "total_mb_downloaded": round(self.total_bytes_downloaded / 1024 / 1024, 2),
            "processed_files_count": len(self.processed_files),
            "errors": self.errors,
            "poll_interval_minutes": self.poll_interval_minutes
        }


class DriveError(Exception):
    """Custom exception for Drive operations"""
    pass


# Factory function

def create_drive_ingestor(
    folder_id: str,
    download_dir: str = "./data/drive_ingestion",
    credentials_path: Optional[str] = None,
    poll_interval_minutes: int = 60
) -> GoogleDriveIngestor:
    """
    Create Google Drive ingestor with authentication

    Args:
        folder_id: Google Drive folder ID to monitor
        download_dir: Local directory for downloads
        credentials_path: Path to service account JSON (or use env var)
        poll_interval_minutes: Polling interval

    Returns:
        Initialized GoogleDriveIngestor

    Example:
        ingestor = create_drive_ingestor(
            folder_id="1abc...xyz",
            download_dir="./data/learning_materials"
        )

        def process_file(file_path, metadata):
            print(f"New file: {file_path}")
            # Process the file (extract text, add to memory, etc.)

        ingestor.watch_folder(callback=process_file)
    """

    from .auth import create_auth_manager

    # Create auth manager
    if credentials_path:
        auth = create_auth_manager(credentials_path=credentials_path, from_env=False)
    else:
        auth = create_auth_manager(from_env=True)

    # Create ingestor
    return GoogleDriveIngestor(
        auth_manager=auth,
        folder_id=folder_id,
        download_dir=download_dir,
        poll_interval_minutes=poll_interval_minutes
    )
