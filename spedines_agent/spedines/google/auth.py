"""
Google Cloud Authentication Manager
Handles service account authentication for Google APIs
"""

import logging
from pathlib import Path
from typing import List, Optional
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import gspread

logger = logging.getLogger(__name__)


class GoogleAuthManager:
    """
    Manages Google Cloud authentication using service accounts

    Provides authenticated clients for various Google services
    """

    # Default scopes for common use cases
    SHEETS_SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]

    DRIVE_SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]

    ALL_SCOPES = list(set(SHEETS_SCOPES + DRIVE_SCOPES))

    def __init__(
        self,
        credentials_path: str,
        scopes: Optional[List[str]] = None
    ):
        """
        Initialize Google authentication manager

        Args:
            credentials_path: Path to service account JSON file
            scopes: Optional list of OAuth scopes (defaults to ALL_SCOPES)
        """

        self.credentials_path = Path(credentials_path)
        self.scopes = scopes or self.ALL_SCOPES

        # Validate credentials file exists
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Google credentials file not found: {self.credentials_path}\n"
                f"Please place your service account JSON file at this location."
            )

        logger.info(f"Initializing Google auth with credentials: {self.credentials_path}")

        # Load credentials
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=self.scopes
            )

            logger.info(
                f"Successfully loaded credentials for: "
                f"{self.credentials.service_account_email}"
            )

        except Exception as e:
            logger.error(f"Failed to load Google credentials: {e}")
            raise GoogleAuthError(f"Failed to load credentials: {e}")

        # Cache for API clients
        self._sheets_client = None
        self._drive_service = None
        self._gspread_client = None

    def get_sheets_service(self):
        """
        Get authenticated Google Sheets API service

        Returns:
            Google Sheets API service object
        """

        if self._sheets_client is None:
            try:
                self._sheets_client = build(
                    'sheets',
                    'v4',
                    credentials=self.credentials
                )

                logger.debug("Created Sheets API service")

            except Exception as e:
                logger.error(f"Failed to create Sheets service: {e}")
                raise GoogleAuthError(f"Failed to create Sheets service: {e}")

        return self._sheets_client

    def get_drive_service(self):
        """
        Get authenticated Google Drive API service

        Returns:
            Google Drive API service object
        """

        if self._drive_service is None:
            try:
                self._drive_service = build(
                    'drive',
                    'v3',
                    credentials=self.credentials
                )

                logger.debug("Created Drive API service")

            except Exception as e:
                logger.error(f"Failed to create Drive service: {e}")
                raise GoogleAuthError(f"Failed to create Drive service: {e}")

        return self._drive_service

    def get_gspread_client(self):
        """
        Get gspread client (higher-level Sheets library)

        Returns:
            gspread client object
        """

        if self._gspread_client is None:
            try:
                self._gspread_client = gspread.authorize(self.credentials)

                logger.debug("Created gspread client")

            except Exception as e:
                logger.error(f"Failed to create gspread client: {e}")
                raise GoogleAuthError(f"Failed to create gspread client: {e}")

        return self._gspread_client

    def test_connection(self) -> dict:
        """
        Test Google API connections

        Returns:
            Dictionary with connection test results
        """

        results = {
            "credentials_valid": False,
            "sheets_accessible": False,
            "drive_accessible": False,
            "errors": []
        }

        # Test credentials
        try:
            if self.credentials and self.credentials.service_account_email:
                results["credentials_valid"] = True
                results["service_account_email"] = self.credentials.service_account_email
        except Exception as e:
            results["errors"].append(f"Credentials error: {e}")

        # Test Sheets API
        try:
            sheets = self.get_sheets_service()
            # Try to create a simple request (won't execute)
            if sheets:
                results["sheets_accessible"] = True
        except Exception as e:
            results["errors"].append(f"Sheets API error: {e}")

        # Test Drive API
        try:
            drive = self.get_drive_service()
            # Try to list files (limited to 1 result)
            if drive:
                drive.files().list(pageSize=1).execute()
                results["drive_accessible"] = True
        except HttpError as e:
            if e.resp.status == 403:
                results["errors"].append("Drive API: Permission denied (check API is enabled)")
            else:
                results["errors"].append(f"Drive API error: {e}")
        except Exception as e:
            results["errors"].append(f"Drive API error: {e}")

        # Overall status
        results["status"] = "healthy" if (
            results["credentials_valid"] and
            results["sheets_accessible"] and
            results["drive_accessible"]
        ) else "degraded"

        return results

    @staticmethod
    def from_env(
        credentials_env_var: str = "GOOGLE_APPLICATION_CREDENTIALS",
        scopes: Optional[List[str]] = None
    ) -> "GoogleAuthManager":
        """
        Create GoogleAuthManager from environment variable

        Args:
            credentials_env_var: Name of environment variable with credentials path
            scopes: Optional list of OAuth scopes

        Returns:
            Initialized GoogleAuthManager

        Raises:
            GoogleAuthError: If environment variable not set
        """

        credentials_path = os.getenv(credentials_env_var)

        if not credentials_path:
            raise GoogleAuthError(
                f"Environment variable {credentials_env_var} not set.\n"
                f"Please set it to the path of your service account JSON file."
            )

        return GoogleAuthManager(credentials_path, scopes)


class GoogleAuthError(Exception):
    """Custom exception for Google authentication errors"""
    pass


# Helper function for common use case

def create_auth_manager(
    credentials_path: Optional[str] = None,
    from_env: bool = True
) -> GoogleAuthManager:
    """
    Create Google auth manager with sensible defaults

    Args:
        credentials_path: Path to credentials (if not using env var)
        from_env: Load from GOOGLE_APPLICATION_CREDENTIALS env var

    Returns:
        Initialized GoogleAuthManager

    Example:
        # From environment variable
        auth = create_auth_manager()

        # From specific path
        auth = create_auth_manager(
            credentials_path="./config/service-account.json",
            from_env=False
        )
    """

    if from_env:
        return GoogleAuthManager.from_env()
    elif credentials_path:
        return GoogleAuthManager(credentials_path)
    else:
        raise ValueError("Must provide either credentials_path or set from_env=True")
