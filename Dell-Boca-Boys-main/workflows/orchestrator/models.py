
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class ExecuteWorkflow(BaseModel):
    workflow_id: str
    trigger_payload: Dict[str, Any] = Field(default_factory=dict)

class ExecuteStep(BaseModel):
    step_id: str
    input: Dict[str, Any]

class Reflection(BaseModel):
    source_type: str
    source_id: str
    insight_type: str
    insight: Dict[str, Any]
    learning_signal: Dict[str, Any]
    proposed_actions: List[Dict[str, Any]]
