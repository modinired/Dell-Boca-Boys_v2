
import os, json, hashlib, time
from typing import Dict, Any
from .registry import SchemaRegistry
from .secrets import SecretProvider

class OrchestratorRuntime:
    def __init__(self):
        reg_path = os.getenv("SCHEMA_REGISTRY_PATH", "./schema_registry")
        self.registry = SchemaRegistry(reg_path)
        self.secrets = SecretProvider(os.getenv("LOCAL_SECRETS_PATH","./local_secrets.json"))

    def checksum(self, obj: Dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

    def validate_event(self, subject: str, payload: Dict[str, Any]):
        self.registry.validate_payload(subject, payload)

    def resolve_secret(self, secret_ref: str) -> str:
        return self.secrets.get(secret_ref)


def adapter_from_binding(self, binding: dict):
    adapter = binding.get("adapter")
    if adapter == "aws_textract_v2":
        from .adapters.aws_textract_v2 import AwsTextractV2Adapter
        return AwsTextractV2Adapter(binding, self.resolve_secret)
    if adapter == "sap_rest":
        from .adapters.sap_rest import SapRestAdapter
        return SapRestAdapter(binding, self.resolve_secret)
    if adapter == "okta":
        from .adapters.okta import OktaAdapter
        return OktaAdapter(binding, self.resolve_secret)
    if adapter == "workday":
        from .adapters.workday import WorkdayAdapter
        return WorkdayAdapter(binding, self.resolve_secret)
    if adapter == "builtin":
        return None
    raise ValueError(f"Unsupported adapter: {adapter}")
