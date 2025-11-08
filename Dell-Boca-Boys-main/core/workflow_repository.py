"""
Production-grade PostgreSQL-based workflow repository.
Replaces SQLite with enterprise-grade storage and querying.
"""
import uuid
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, Column, String, JSON, DateTime, Float, Integer, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import select, update, delete, and_, or_
import asyncio

from core.exceptions import WorkflowNotFoundError, WorkflowValidationError, DatabaseException

logger = logging.getLogger(__name__)

Base = declarative_base()


# ============================================================================
# Models
# ============================================================================

class WorkflowStatus(str):
    """Workflow status enum."""
    CREATED = "created"
    VALIDATED = "validated"
    STAGED = "staged"
    ACTIVE = "active"
    FAILED = "failed"
    ARCHIVED = "archived"


class ExecutionStatus(str):
    """Execution status enum."""
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    WAITING = "waiting"
    CANCELED = "canceled"


class ExecutionMode(str):
    """Execution mode enum."""
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Workflow(Base):
    """Workflow model."""
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    user_goal = Column(Text, nullable=False)
    workflow_json = Column(JSONB, nullable=False)
    n8n_workflow_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default=WorkflowStatus.CREATED)
    validation_errors = Column(JSONB, default=list)
    best_practices_score = Column(Float, nullable=True)
    test_results = Column(JSONB, nullable=True)
    provenance = Column(JSONB, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    staged_at = Column(DateTime, nullable=True)
    activated_at = Column(DateTime, nullable=True)
    created_by = Column(String, default="system")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "user_goal": self.user_goal,
            "workflow_json": self.workflow_json,
            "n8n_workflow_id": self.n8n_workflow_id,
            "status": self.status,
            "validation_errors": self.validation_errors,
            "best_practices_score": self.best_practices_score,
            "test_results": self.test_results,
            "provenance": self.provenance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "staged_at": self.staged_at.isoformat() if self.staged_at else None,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "created_by": self.created_by
        }


class Execution(Base):
    """Workflow execution model."""
    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), nullable=False)
    n8n_execution_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_data = Column(JSONB, nullable=True)
    test_payload = Column(JSONB, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "workflow_id": str(self.workflow_id),
            "n8n_execution_id": self.n8n_execution_id,
            "status": self.status,
            "mode": self.mode,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "error_message": self.error_message,
            "execution_data": self.execution_data,
            "test_payload": self.test_payload
        }


# ============================================================================
# Repository
# ============================================================================

class WorkflowRepository:
    """
    PostgreSQL-based workflow repository.

    Provides async CRUD operations for workflows and executions.
    """

    def __init__(self, database_url: str):
        """
        Initialize workflow repository.

        Args:
            database_url: PostgreSQL connection URL
                         Format: postgresql+asyncpg://user:pass@host:port/db
        """
        self.database_url = database_url

        # Create async engine
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600
        )

        # Create async session factory
        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info(f"Workflow repository initialized")

    async def initialize(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")

    @asynccontextmanager
    async def session(self):
        """Get async database session."""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # ========================================================================
    # Workflow CRUD Operations
    # ========================================================================

    async def create_workflow(
        self,
        name: str,
        user_goal: str,
        workflow_json: Dict[str, Any],
        created_by: str = "system",
        **kwargs
    ) -> Workflow:
        """
        Create a new workflow.

        Args:
            name: Workflow name
            user_goal: User's goal/description
            workflow_json: n8n workflow JSON
            created_by: Creator identifier
            **kwargs: Additional workflow fields

        Returns:
            Created workflow
        """
        try:
            async with self.session() as session:
                workflow = Workflow(
                    name=name,
                    user_goal=user_goal,
                    workflow_json=workflow_json,
                    created_by=created_by,
                    **kwargs
                )

                session.add(workflow)
                await session.flush()
                await session.refresh(workflow)

                logger.info(f"Created workflow: {workflow.id}")
                return workflow

        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise DatabaseException("workflow_create", str(e))

    async def get_workflow(self, workflow_id: uuid.UUID) -> Workflow:
        """
        Get workflow by ID.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Workflow

        Raises:
            WorkflowNotFoundError: If workflow not found
        """
        async with self.session() as session:
            result = await session.execute(
                select(Workflow).where(Workflow.id == workflow_id)
            )
            workflow = result.scalar_one_or_none()

            if not workflow:
                raise WorkflowNotFoundError(str(workflow_id))

            return workflow

    async def list_workflows(
        self,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Workflow]:
        """
        List workflows with filtering.

        Args:
            status: Filter by status
            created_by: Filter by creator
            limit: Maximum results
            offset: Result offset

        Returns:
            List of workflows
        """
        async with self.session() as session:
            query = select(Workflow)

            # Apply filters
            if status:
                query = query.where(Workflow.status == status)
            if created_by:
                query = query.where(Workflow.created_by == created_by)

            # Order and limit
            query = query.order_by(Workflow.created_at.desc())
            query = query.limit(limit).offset(offset)

            result = await session.execute(query)
            workflows = result.scalars().all()

            return list(workflows)

    async def update_workflow(
        self,
        workflow_id: uuid.UUID,
        **updates
    ) -> Workflow:
        """
        Update workflow fields.

        Args:
            workflow_id: Workflow UUID
            **updates: Fields to update

        Returns:
            Updated workflow
        """
        try:
            async with self.session() as session:
                result = await session.execute(
                    select(Workflow).where(Workflow.id == workflow_id)
                )
                workflow = result.scalar_one_or_none()

                if not workflow:
                    raise WorkflowNotFoundError(str(workflow_id))

                for key, value in updates.items():
                    if hasattr(workflow, key):
                        setattr(workflow, key, value)

                workflow.updated_at = datetime.utcnow()

                await session.flush()
                await session.refresh(workflow)

                logger.info(f"Updated workflow: {workflow_id}")
                return workflow

        except WorkflowNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            raise DatabaseException("workflow_update", str(e))

    async def delete_workflow(self, workflow_id: uuid.UUID):
        """
        Delete workflow.

        Args:
            workflow_id: Workflow UUID
        """
        try:
            async with self.session() as session:
                result = await session.execute(
                    delete(Workflow).where(Workflow.id == workflow_id)
                )

                if result.rowcount == 0:
                    raise WorkflowNotFoundError(str(workflow_id))

                logger.info(f"Deleted workflow: {workflow_id}")

        except WorkflowNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            raise DatabaseException("workflow_delete", str(e))

    async def update_workflow_status(
        self,
        workflow_id: uuid.UUID,
        new_status: str
    ) -> Workflow:
        """
        Update workflow status.

        Args:
            workflow_id: Workflow UUID
            new_status: New status

        Returns:
            Updated workflow
        """
        updates = {"status": new_status}

        # Set timestamp fields based on status
        if new_status == WorkflowStatus.STAGED:
            updates["staged_at"] = datetime.utcnow()
        elif new_status == WorkflowStatus.ACTIVE:
            updates["activated_at"] = datetime.utcnow()

        return await self.update_workflow(workflow_id, **updates)

    # ========================================================================
    # Execution CRUD Operations
    # ========================================================================

    async def create_execution(
        self,
        workflow_id: uuid.UUID,
        mode: str,
        status: str = ExecutionStatus.RUNNING,
        **kwargs
    ) -> Execution:
        """
        Create workflow execution record.

        Args:
            workflow_id: Workflow UUID
            mode: Execution mode
            status: Initial status
            **kwargs: Additional execution fields

        Returns:
            Created execution
        """
        try:
            async with self.session() as session:
                execution = Execution(
                    workflow_id=workflow_id,
                    mode=mode,
                    status=status,
                    **kwargs
                )

                session.add(execution)
                await session.flush()
                await session.refresh(execution)

                logger.info(f"Created execution: {execution.id} for workflow {workflow_id}")
                return execution

        except Exception as e:
            logger.error(f"Failed to create execution: {e}")
            raise DatabaseException("execution_create", str(e))

    async def get_execution(self, execution_id: uuid.UUID) -> Execution:
        """Get execution by ID."""
        async with self.session() as session:
            result = await session.execute(
                select(Execution).where(Execution.id == execution_id)
            )
            execution = result.scalar_one_or_none()

            if not execution:
                raise ValueError(f"Execution not found: {execution_id}")

            return execution

    async def list_executions(
        self,
        workflow_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        limit: int = 100
    ) -> List[Execution]:
        """List executions with filtering."""
        async with self.session() as session:
            query = select(Execution)

            if workflow_id:
                query = query.where(Execution.workflow_id == workflow_id)
            if status:
                query = query.where(Execution.status == status)
            if mode:
                query = query.where(Execution.mode == mode)

            query = query.order_by(Execution.started_at.desc()).limit(limit)

            result = await session.execute(query)
            executions = result.scalars().all()

            return list(executions)

    async def update_execution(
        self,
        execution_id: uuid.UUID,
        **updates
    ) -> Execution:
        """Update execution fields."""
        try:
            async with self.session() as session:
                result = await session.execute(
                    select(Execution).where(Execution.id == execution_id)
                )
                execution = result.scalar_one_or_none()

                if not execution:
                    raise ValueError(f"Execution not found: {execution_id}")

                for key, value in updates.items():
                    if hasattr(execution, key):
                        setattr(execution, key, value)

                await session.flush()
                await session.refresh(execution)

                logger.info(f"Updated execution: {execution_id}")
                return execution

        except Exception as e:
            logger.error(f"Failed to update execution {execution_id}: {e}")
            raise DatabaseException("execution_update", str(e))

    async def complete_execution(
        self,
        execution_id: uuid.UUID,
        status: str,
        error_message: Optional[str] = None,
        execution_data: Optional[Dict[str, Any]] = None
    ) -> Execution:
        """Mark execution as complete."""
        return await self.update_execution(
            execution_id,
            status=status,
            finished_at=datetime.utcnow(),
            error_message=error_message,
            execution_data=execution_data
        )

    # ========================================================================
    # Query Operations
    # ========================================================================

    async def search_workflows(self, search_term: str, limit: int = 20) -> List[Workflow]:
        """
        Search workflows by name or goal.

        Args:
            search_term: Search term
            limit: Maximum results

        Returns:
            List of matching workflows
        """
        async with self.session() as session:
            # PostgreSQL full-text search
            query = select(Workflow).where(
                or_(
                    Workflow.name.ilike(f"%{search_term}%"),
                    Workflow.user_goal.ilike(f"%{search_term}%")
                )
            ).order_by(Workflow.created_at.desc()).limit(limit)

            result = await session.execute(query)
            workflows = result.scalars().all()

            return list(workflows)

    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        async with self.session() as session:
            # Count by status
            from sqlalchemy import func

            status_counts = await session.execute(
                select(Workflow.status, func.count(Workflow.id))
                .group_by(Workflow.status)
            )

            return {
                "total_workflows": await session.scalar(select(func.count(Workflow.id))),
                "by_status": dict(status_counts.all()),
                "avg_best_practices_score": await session.scalar(
                    select(func.avg(Workflow.best_practices_score))
                    .where(Workflow.best_practices_score.isnot(None))
                ) or 0.0
            }

    async def close(self):
        """Close database connections."""
        await self.engine.dispose()
        logger.info("Workflow repository closed")


# ============================================================================
# Global Repository Instance
# ============================================================================

_global_workflow_repo: Optional[WorkflowRepository] = None


async def init_workflow_repository(database_url: str) -> WorkflowRepository:
    """Initialize global workflow repository."""
    global _global_workflow_repo
    _global_workflow_repo = WorkflowRepository(database_url)
    await _global_workflow_repo.initialize()
    return _global_workflow_repo


def get_workflow_repository() -> WorkflowRepository:
    """Get global workflow repository instance."""
    if _global_workflow_repo is None:
        raise RuntimeError("Workflow repository not initialized. Call init_workflow_repository() first.")
    return _global_workflow_repo
