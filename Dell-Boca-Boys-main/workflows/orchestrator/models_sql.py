
from sqlalchemy import Column, String, Integer, JSON, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

class Workflow(Base):
    __tablename__ = "workflow"
    workflow_id = Column(String(32), primary_key=True)
    workflow_name = Column(String(128), nullable=False)
    objective = Column(Text, nullable=False)
    constraints = Column(JSON, nullable=False)
    responsible_role_id = Column(String(32), nullable=False)
    genome = Column(JSON, nullable=False)
    status = Column(String(16), nullable=False, default="active")
    version = Column(String(24), nullable=False)
    lineage = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    steps = relationship("StepAction", back_populates="workflow", order_by="StepAction.sequence")

class StepAction(Base):
    __tablename__ = "step_action"
    step_id = Column(String(32), primary_key=True)
    workflow_id = Column(String(32), ForeignKey("workflow.workflow_id"), nullable=False)
    sequence = Column(Integer, nullable=False)
    action_type = Column(String(24), nullable=False)
    skill_id = Column(String(32), nullable=False)
    parameters = Column(JSON, nullable=False)
    next_step_logic = Column(JSON, nullable=False)
    timeout_ms = Column(Integer, nullable=False, default=300000)
    retries = Column(Integer, nullable=False, default=2)
    idempotency_key = Column(String(64))

    workflow = relationship("Workflow", back_populates="steps")
