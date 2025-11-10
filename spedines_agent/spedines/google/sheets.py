"""
Google Sheets Logger
Audit logging and training data collection to Google Sheets
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import time

from googleapiclient.errors import HttpError
import gspread
from gspread.exceptions import SpreadsheetNotFound, APIError

from .auth import GoogleAuthManager

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Structure for a log entry"""
    timestamp: str
    event_type: str
    user_query: str
    assistant_response: str
    llm_used: str
    tokens_used: int
    latency_ms: float
    cost_usd: float
    success: bool
    metadata: Dict[str, Any]


class GoogleSheetsLogger:
    """
    Log interactions and training data to Google Sheets

    Provides audit trail and data collection for continual learning
    """

    # Default sheet structure
    LOG_HEADERS = [
        "Timestamp",
        "Event Type",
        "User Query",
        "Assistant Response",
        "LLM Used",
        "Tokens Used",
        "Latency (ms)",
        "Cost (USD)",
        "Success",
        "Metadata"
    ]

    TRAINING_HEADERS = [
        "Timestamp",
        "Prompt",
        "Completion",
        "Source",
        "Quality Rating",
        "User Feedback",
        "Tags",
        "Used for Training"
    ]

    def __init__(
        self,
        auth_manager: GoogleAuthManager,
        spreadsheet_id: str,
        log_sheet_name: str = "Interaction Log",
        training_sheet_name: str = "Training Data",
        auto_create_sheets: bool = True
    ):
        """
        Initialize Google Sheets logger

        Args:
            auth_manager: GoogleAuthManager instance
            spreadsheet_id: Google Sheets spreadsheet ID
            log_sheet_name: Name of sheet for interaction logs
            training_sheet_name: Name of sheet for training data
            auto_create_sheets: Automatically create sheets if they don't exist
        """

        self.auth_manager = auth_manager
        self.spreadsheet_id = spreadsheet_id
        self.log_sheet_name = log_sheet_name
        self.training_sheet_name = training_sheet_name

        # Get gspread client
        self.gspread_client = auth_manager.get_gspread_client()

        logger.info(f"Initializing Google Sheets logger: {spreadsheet_id}")

        # Open spreadsheet
        try:
            self.spreadsheet = self.gspread_client.open_by_key(spreadsheet_id)
            logger.info(f"Opened spreadsheet: {self.spreadsheet.title}")

        except SpreadsheetNotFound:
            raise SheetsError(
                f"Spreadsheet not found: {spreadsheet_id}\n"
                f"Make sure the spreadsheet exists and is shared with the service account:\n"
                f"{auth_manager.credentials.service_account_email}"
            )
        except Exception as e:
            raise SheetsError(f"Failed to open spreadsheet: {e}")

        # Get or create sheets
        if auto_create_sheets:
            self._ensure_sheets_exist()

        # Metrics
        self.logs_written = 0
        self.training_data_written = 0
        self.errors = 0

    def _ensure_sheets_exist(self):
        """Ensure required sheets exist with proper headers"""

        # Check/create log sheet
        try:
            self.log_sheet = self.spreadsheet.worksheet(self.log_sheet_name)
            logger.debug(f"Found existing log sheet: {self.log_sheet_name}")

        except gspread.exceptions.WorksheetNotFound:
            logger.info(f"Creating log sheet: {self.log_sheet_name}")
            self.log_sheet = self.spreadsheet.add_worksheet(
                title=self.log_sheet_name,
                rows=1000,
                cols=len(self.LOG_HEADERS)
            )

            # Add headers
            self.log_sheet.append_row(self.LOG_HEADERS)
            logger.info(f"Created log sheet with headers")

        # Check/create training sheet
        try:
            self.training_sheet = self.spreadsheet.worksheet(self.training_sheet_name)
            logger.debug(f"Found existing training sheet: {self.training_sheet_name}")

        except gspread.exceptions.WorksheetNotFound:
            logger.info(f"Creating training sheet: {self.training_sheet_name}")
            self.training_sheet = self.spreadsheet.add_worksheet(
                title=self.training_sheet_name,
                rows=1000,
                cols=len(self.TRAINING_HEADERS)
            )

            # Add headers
            self.training_sheet.append_row(self.TRAINING_HEADERS)
            logger.info(f"Created training sheet with headers")

    def log_interaction(
        self,
        event_type: str,
        user_query: str,
        assistant_response: str,
        llm_used: str = "unknown",
        tokens_used: int = 0,
        latency_ms: float = 0.0,
        cost_usd: float = 0.0,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an interaction to the sheet

        Args:
            event_type: Type of interaction (query, reflection, error, etc.)
            user_query: User's input
            assistant_response: Spedines' response
            llm_used: Which LLM was used
            tokens_used: Token count
            latency_ms: Response latency
            cost_usd: API cost
            success: Whether interaction was successful
            metadata: Additional metadata

        Returns:
            True if logged successfully
        """

        try:
            timestamp = datetime.now().isoformat()

            # Truncate long texts for readability
            query_truncated = self._truncate(user_query, 500)
            response_truncated = self._truncate(assistant_response, 1000)

            # Format metadata as JSON string
            metadata_str = str(metadata) if metadata else ""

            row = [
                timestamp,
                event_type,
                query_truncated,
                response_truncated,
                llm_used,
                tokens_used,
                round(latency_ms, 2),
                round(cost_usd, 6),
                "Yes" if success else "No",
                metadata_str
            ]

            self.log_sheet.append_row(row)

            self.logs_written += 1

            logger.debug(f"Logged interaction: {event_type}")

            return True

        except APIError as e:
            logger.error(f"API error logging to Sheets: {e}")
            self.errors += 1

            # Don't raise - logging shouldn't break the application
            return False

        except Exception as e:
            logger.error(f"Failed to log interaction: {e}", exc_info=True)
            self.errors += 1
            return False

    def log_training_data(
        self,
        prompt: str,
        completion: str,
        source: str = "interaction",
        quality_rating: Optional[int] = None,
        user_feedback: Optional[str] = None,
        tags: Optional[List[str]] = None,
        used_for_training: bool = False
    ) -> bool:
        """
        Log potential training data

        Args:
            prompt: Input prompt
            completion: Model completion
            source: Source of data (interaction, reflection, manual, etc.)
            quality_rating: Optional quality rating (1-5)
            user_feedback: Optional user feedback
            tags: Optional list of tags
            used_for_training: Whether this was used for training

        Returns:
            True if logged successfully
        """

        try:
            timestamp = datetime.now().isoformat()

            # Truncate for readability
            prompt_truncated = self._truncate(prompt, 1000)
            completion_truncated = self._truncate(completion, 2000)

            # Format tags
            tags_str = ", ".join(tags) if tags else ""

            row = [
                timestamp,
                prompt_truncated,
                completion_truncated,
                source,
                quality_rating or "",
                user_feedback or "",
                tags_str,
                "Yes" if used_for_training else "No"
            ]

            self.training_sheet.append_row(row)

            self.training_data_written += 1

            logger.debug(f"Logged training data from {source}")

            return True

        except Exception as e:
            logger.error(f"Failed to log training data: {e}")
            self.errors += 1
            return False

    def log_batch(
        self,
        entries: List[LogEntry],
        max_retries: int = 3
    ) -> int:
        """
        Log multiple entries in batch (more efficient)

        Args:
            entries: List of LogEntry objects
            max_retries: Maximum retry attempts

        Returns:
            Number of entries successfully logged
        """

        if not entries:
            return 0

        try:
            # Convert entries to rows
            rows = []
            for entry in entries:
                row = [
                    entry.timestamp,
                    entry.event_type,
                    self._truncate(entry.user_query, 500),
                    self._truncate(entry.assistant_response, 1000),
                    entry.llm_used,
                    entry.tokens_used,
                    round(entry.latency_ms, 2),
                    round(entry.cost_usd, 6),
                    "Yes" if entry.success else "No",
                    str(entry.metadata)
                ]
                rows.append(row)

            # Batch append with retry
            for attempt in range(max_retries):
                try:
                    self.log_sheet.append_rows(rows)

                    self.logs_written += len(rows)

                    logger.info(f"Batch logged {len(rows)} entries")

                    return len(rows)

                except APIError as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Batch log failed, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        raise

        except Exception as e:
            logger.error(f"Batch log failed: {e}")
            self.errors += len(entries)
            return 0

    def get_recent_logs(
        self,
        n: int = 10,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent logs from sheet

        Args:
            n: Number of logs to retrieve
            event_type: Optional filter by event type

        Returns:
            List of log dictionaries
        """

        try:
            # Get all values
            all_values = self.log_sheet.get_all_values()

            if len(all_values) <= 1:  # Only headers
                return []

            headers = all_values[0]
            rows = all_values[1:]  # Skip headers

            # Convert to dictionaries
            logs = []
            for row in reversed(rows):  # Most recent first
                if len(row) < len(headers):
                    # Pad row if missing columns
                    row.extend([''] * (len(headers) - len(row)))

                log_dict = dict(zip(headers, row))

                # Filter by event type if specified
                if event_type and log_dict.get("Event Type") != event_type:
                    continue

                logs.append(log_dict)

                if len(logs) >= n:
                    break

            return logs

        except Exception as e:
            logger.error(f"Failed to retrieve logs: {e}")
            return []

    def search_logs(
        self,
        query: str,
        column: str = "User Query",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search logs by content

        Args:
            query: Search query
            column: Column to search in
            max_results: Maximum results to return

        Returns:
            List of matching log dictionaries
        """

        try:
            all_values = self.log_sheet.get_all_values()

            if len(all_values) <= 1:
                return []

            headers = all_values[0]
            rows = all_values[1:]

            # Find column index
            try:
                col_idx = headers.index(column)
            except ValueError:
                logger.error(f"Column not found: {column}")
                return []

            # Search
            results = []
            query_lower = query.lower()

            for row in reversed(rows):  # Most recent first
                if len(row) > col_idx and query_lower in row[col_idx].lower():
                    if len(row) < len(headers):
                        row.extend([''] * (len(headers) - len(row)))

                    results.append(dict(zip(headers, row)))

                    if len(results) >= max_results:
                        break

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_training_data(
        self,
        limit: Optional[int] = None,
        unused_only: bool = False,
        min_quality: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Retrieve training data from sheet

        Args:
            limit: Optional limit on results
            unused_only: Only get data not yet used for training
            min_quality: Minimum quality rating (1-5)

        Returns:
            List of training data dictionaries
        """

        try:
            all_values = self.training_sheet.get_all_values()

            if len(all_values) <= 1:
                return []

            headers = all_values[0]
            rows = all_values[1:]

            # Filter and convert
            training_data = []

            for row in rows:
                if len(row) < len(headers):
                    row.extend([''] * (len(headers) - len(row)))

                data_dict = dict(zip(headers, row))

                # Apply filters
                if unused_only and data_dict.get("Used for Training") == "Yes":
                    continue

                if min_quality:
                    try:
                        quality = int(data_dict.get("Quality Rating", 0))
                        if quality < min_quality:
                            continue
                    except (ValueError, TypeError):
                        continue

                training_data.append(data_dict)

                if limit and len(training_data) >= limit:
                    break

            return training_data

        except Exception as e:
            logger.error(f"Failed to retrieve training data: {e}")
            return []

    def mark_training_data_used(
        self,
        timestamps: List[str]
    ) -> bool:
        """
        Mark training data as used

        Args:
            timestamps: List of timestamps to mark as used

        Returns:
            True if successful
        """

        try:
            # Find and update rows
            # This is inefficient for large sheets, but works for moderate use
            all_values = self.training_sheet.get_all_values()

            if len(all_values) <= 1:
                return True

            headers = all_values[0]
            used_col_idx = headers.index("Used for Training")
            timestamp_col_idx = headers.index("Timestamp")

            updates = []

            for row_idx, row in enumerate(all_values[1:], start=2):  # Start at row 2 (after headers)
                if len(row) > timestamp_col_idx and row[timestamp_col_idx] in timestamps:
                    # Update this row
                    cell = gspread.utils.rowcol_to_a1(row_idx, used_col_idx + 1)
                    updates.append({
                        'range': cell,
                        'values': [['Yes']]
                    })

            if updates:
                self.training_sheet.batch_update(updates)
                logger.info(f"Marked {len(updates)} training entries as used")

            return True

        except Exception as e:
            logger.error(f"Failed to mark training data as used: {e}")
            return False

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text

        return text[:max_length - 3] + "..."

    def get_metrics(self) -> Dict[str, Any]:
        """Get logger metrics"""

        return {
            "spreadsheet_id": self.spreadsheet_id,
            "spreadsheet_title": self.spreadsheet.title,
            "logs_written": self.logs_written,
            "training_data_written": self.training_data_written,
            "errors": self.errors,
            "total_log_rows": self.log_sheet.row_count - 1,  # Exclude header
            "total_training_rows": self.training_sheet.row_count - 1
        }


class SheetsError(Exception):
    """Custom exception for Sheets operations"""
    pass


# Factory function

def create_sheets_logger(
    spreadsheet_id: str,
    credentials_path: Optional[str] = None,
    log_sheet_name: str = "Interaction Log",
    training_sheet_name: str = "Training Data"
) -> GoogleSheetsLogger:
    """
    Create Google Sheets logger with authentication

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        credentials_path: Path to service account JSON (or use env var)
        log_sheet_name: Name of interaction log sheet
        training_sheet_name: Name of training data sheet

    Returns:
        Initialized GoogleSheetsLogger

    Example:
        logger = create_sheets_logger(
            spreadsheet_id="1abc...xyz",
            credentials_path="./config/service-account.json"
        )

        logger.log_interaction(
            event_type="query",
            user_query="What's the weather?",
            assistant_response="I don't have real-time weather access.",
            llm_used="gemini",
            tokens_used=150
        )
    """

    from .auth import create_auth_manager

    # Create auth manager
    if credentials_path:
        auth = create_auth_manager(credentials_path=credentials_path, from_env=False)
    else:
        auth = create_auth_manager(from_env=True)

    # Create logger
    return GoogleSheetsLogger(
        auth_manager=auth,
        spreadsheet_id=spreadsheet_id,
        log_sheet_name=log_sheet_name,
        training_sheet_name=training_sheet_name
    )
