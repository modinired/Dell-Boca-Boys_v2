
from typing import Dict, Any

class OktaAdapter:
    def __init__(self, binding: Dict[str, Any], secret_resolver):
        self.binding = binding
        self.secret_resolver = secret_resolver
        self.token = None
        auth = binding.get("auth", {})
        ref = auth.get("secret_ref")
        if ref:
            self.token = secret_resolver(ref)

    def provision(self, user_id: str, access_group: str) -> Dict[str, Any]:
        return {"ok": True, "user_id": user_id, "group": access_group}
