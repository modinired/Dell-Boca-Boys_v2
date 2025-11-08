
import os, json, glob
from jsonschema import validate, Draft202012Validator

class SchemaRegistry:
    def __init__(self, path: str):
        self.path = path
        self._cache = {}
        self._load()

    def _load(self):
        for p in glob.glob(os.path.join(self.path, "*.json")):
            with open(p, "r") as f:
                obj = json.load(f)
            subject = os.path.basename(p).split(".v")[0]  # e.g., ap.invoice.received
            version = int(os.path.basename(p).split(".v")[1].split(".json")[0])
            self._cache[(subject, version)] = obj

    def latest(self, subject: str):
        versions = [v for (s, v) in self._cache.keys() if s == subject]
        if not versions:
            raise KeyError(f"No schema for subject {subject}")
        v = max(versions)
        return self._cache[(subject, v)], v

    def validate_payload(self, subject: str, payload: dict, version: int | None = None):
        if version is None:
            schema, _ = self.latest(subject)
        else:
            schema = self._cache[(subject, version)]
        Draft202012Validator.check_schema(schema)
        validate(instance=payload, schema=schema)
