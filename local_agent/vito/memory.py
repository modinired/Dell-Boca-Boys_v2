"""
Memory system for Vito agent
Maintains coding context across sessions
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

from .config import get_config

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A message in the conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Session:
    """A conversation session"""
    session_id: str
    start_time: str
    last_active: str
    messages: List[Message]
    context_summary: Optional[str] = None
    project_path: Optional[str] = None


@dataclass
class CodeContext:
    """Context about code files"""
    file_path: str
    content_hash: str
    last_modified: str
    language: str
    relevance_score: float
    summary: Optional[str] = None


class MemorySystem:
    """
    Persistent memory system for coding context

    Features:
    - Session history (conversations)
    - Code context (relevant files)
    - Code snippets (reusable patterns)
    - Project knowledge (structure, conventions)
    """

    def __init__(self, config: Optional[Any] = None):
        """Initialize memory system"""

        self.config = config or get_config()
        self.db_path = self.config.memory_db_path
        self.enabled = self.config.enable_memory

        if not self.enabled:
            logger.info("Memory system disabled")
            return

        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        # Current session
        self.current_session_id = self._create_session()

        logger.info(f"Memory system initialized: {self.db_path}")

    def _init_database(self):
        """Initialize SQLite database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                last_active TEXT NOT NULL,
                context_summary TEXT,
                project_path TEXT
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Code context table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                language TEXT,
                relevance_score REAL DEFAULT 1.0,
                summary TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)

        # Code snippets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snippet_id TEXT UNIQUE NOT NULL,
                language TEXT NOT NULL,
                code TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0
            )
        """)

        # Project knowledge table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_path TEXT UNIQUE NOT NULL,
                structure TEXT,
                tech_stack TEXT,
                conventions TEXT,
                last_updated TEXT NOT NULL
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_code_context_session ON code_context(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snippets_language ON code_snippets(language)")

        conn.commit()
        conn.close()

        logger.info("Database initialized")

    def _create_session(self) -> str:
        """Create new session"""

        if not self.enabled:
            return "memory-disabled"

        session_id = hashlib.md5(
            datetime.now().isoformat().encode()
        ).hexdigest()[:16]

        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (session_id, start_time, last_active)
            VALUES (?, ?, ?)
        """, (session_id, now, now))

        conn.commit()
        conn.close()

        logger.info(f"Created session: {session_id}")

        return session_id

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add message to current session"""

        if not self.enabled:
            return

        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages (session_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self.current_session_id,
            role,
            content,
            now,
            json.dumps(metadata) if metadata else None
        ))

        # Update session last_active
        cursor.execute("""
            UPDATE sessions
            SET last_active = ?
            WHERE session_id = ?
        """, (now, self.current_session_id))

        conn.commit()
        conn.close()

    def get_session_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Message]:
        """Get messages from a session"""

        if not self.enabled:
            return []

        sid = session_id or self.current_session_id

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT role, content, timestamp, metadata
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (sid, limit))

        rows = cursor.fetchall()
        conn.close()

        messages = []
        for row in rows:
            messages.append(Message(
                role=row[0],
                content=row[1],
                timestamp=row[2],
                metadata=json.loads(row[3]) if row[3] else None
            ))

        return list(reversed(messages))  # Return in chronological order

    def add_code_context(
        self,
        file_path: str,
        content: Optional[str] = None,
        language: Optional[str] = None,
        relevance_score: float = 1.0,
        summary: Optional[str] = None
    ):
        """Add code file to context"""

        if not self.enabled:
            return

        # Calculate content hash
        if content:
            content_hash = hashlib.md5(content.encode()).hexdigest()
        else:
            # Read file if not provided
            try:
                path = Path(file_path)
                if path.exists():
                    content = path.read_text()
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                else:
                    logger.warning(f"File not found: {file_path}")
                    return
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return

        # Detect language if not provided
        if not language:
            language = self._detect_language(file_path)

        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO code_context
            (session_id, file_path, content_hash, last_modified, language, relevance_score, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.current_session_id,
            file_path,
            content_hash,
            now,
            language,
            relevance_score,
            summary
        ))

        conn.commit()
        conn.close()

        logger.info(f"Added code context: {file_path}")

    def get_code_context(
        self,
        session_id: Optional[str] = None,
        min_relevance: float = 0.5
    ) -> List[CodeContext]:
        """Get code context for a session"""

        if not self.enabled:
            return []

        sid = session_id or self.current_session_id

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT file_path, content_hash, last_modified, language, relevance_score, summary
            FROM code_context
            WHERE session_id = ? AND relevance_score >= ?
            ORDER BY relevance_score DESC
        """, (sid, min_relevance))

        rows = cursor.fetchall()
        conn.close()

        contexts = []
        for row in rows:
            contexts.append(CodeContext(
                file_path=row[0],
                content_hash=row[1],
                last_modified=row[2],
                language=row[3],
                relevance_score=row[4],
                summary=row[5]
            ))

        return contexts

    def save_snippet(
        self,
        code: str,
        language: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Save reusable code snippet"""

        if not self.enabled:
            return ""

        snippet_id = hashlib.md5(
            f"{language}{code}{datetime.now()}".encode()
        ).hexdigest()[:16]

        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO code_snippets
            (snippet_id, language, code, description, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            snippet_id,
            language,
            code,
            description,
            json.dumps(tags) if tags else None,
            now
        ))

        conn.commit()
        conn.close()

        logger.info(f"Saved snippet: {snippet_id}")

        return snippet_id

    def search_snippets(
        self,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for code snippets"""

        if not self.enabled:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT snippet_id, language, code, description, tags, created_at, usage_count FROM code_snippets"
        params = []

        if language:
            query += " WHERE language = ?"
            params.append(language)

        query += " ORDER BY usage_count DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        snippets = []
        for row in rows:
            snippet = {
                "snippet_id": row[0],
                "language": row[1],
                "code": row[2],
                "description": row[3],
                "tags": json.loads(row[4]) if row[4] else [],
                "created_at": row[5],
                "usage_count": row[6]
            }

            # Filter by tags if provided
            if tags:
                snippet_tags = snippet["tags"]
                if any(tag in snippet_tags for tag in tags):
                    snippets.append(snippet)
            else:
                snippets.append(snippet)

        return snippets

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sessions"""

        if not self.enabled:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, start_time, last_active, context_summary, project_path
            FROM sessions
            ORDER BY last_active DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        sessions = []
        for row in rows:
            sessions.append({
                "session_id": row[0],
                "start_time": row[1],
                "last_active": row[2],
                "context_summary": row[3],
                "project_path": row[4]
            })

        return sessions

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""

        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".rs": "rust",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown"
        }

        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, "unknown")

    def get_context_for_prompt(
        self,
        include_history: bool = True,
        history_limit: int = 10
    ) -> str:
        """
        Get context to include in LLM prompt

        Returns formatted string with:
        - Recent conversation history
        - Relevant code files
        - Project information
        """

        if not self.enabled:
            return ""

        context_parts = []

        # Add conversation history
        if include_history:
            messages = self.get_session_history(limit=history_limit)
            if messages:
                context_parts.append("## Recent Conversation")
                for msg in messages:
                    context_parts.append(f"{msg.role}: {msg.content[:200]}...")

        # Add code context
        code_contexts = self.get_code_context()
        if code_contexts:
            context_parts.append("\n## Relevant Code Files")
            for ctx in code_contexts[:5]:  # Top 5 most relevant
                context_parts.append(f"- {ctx.file_path} ({ctx.language})")
                if ctx.summary:
                    context_parts.append(f"  {ctx.summary}")

        return "\n".join(context_parts)


# Global instance
_memory: Optional[MemorySystem] = None


def get_memory() -> MemorySystem:
    """Get global memory system instance"""
    global _memory
    if _memory is None:
        _memory = MemorySystem()
    return _memory
