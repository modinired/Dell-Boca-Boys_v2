
from .db import SessionLocal
from .models_sql import Workflow, StepAction

class Repo:
    def __init__(self):
        self.Session = SessionLocal

    def get_workflow_with_steps(self, workflow_id: str) -> Workflow | None:
        with self.Session() as s:
            return s.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()

    def list_steps(self, workflow_id: str):
        with self.Session() as s:
            return s.query(StepAction).filter(StepAction.workflow_id == workflow_id).order_by(StepAction.sequence).all()
