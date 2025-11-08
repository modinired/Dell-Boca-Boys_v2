
from typing import Dict, Any

class WorkdayAdapter:
    def __init__(self, binding: Dict[str, Any], secret_resolver):
        self.binding = binding
        self.secret_resolver = secret_resolver

    def query(self, object_id: str) -> Dict[str, Any]:
        return {"ok": True, "object_id": object_id}
