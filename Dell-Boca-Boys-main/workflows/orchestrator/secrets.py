
import os, json
from typing import Optional
try:
    import hvac
except Exception:
    hvac = None

class SecretProvider:
    def __init__(self, local_path: str):
        self.local_path = local_path
        self._local = {}
        if os.path.exists(local_path):
            with open(local_path, "r") as f:
                self._local = json.load(f)

        self.vault_addr = os.getenv("VAULT_ADDR")
        self.vault_token = os.getenv("VAULT_TOKEN")
        self._vault = None
        if self.vault_addr and self.vault_token and hvac is not None:
            client = hvac.Client(url=self.vault_addr, token=self.vault_token)
            if client.is_authenticated():
                self._vault = client

    def get(self, ref: str) -> Optional[str]:
        # ref format: "vault:kv/path#key" or "local:keypath#field"
        if ref.startswith("vault:"):
            if not self._vault:
                raise RuntimeError("Vault configured but hvac not available or not authenticated")
            path, key = ref[len("vault:"):].split("#", 1)
            secret = self._vault.secrets.kv.v2.read_secret_version(path=path)
            return secret["data"]["data"][key]
        else:
            # local: kv/path#key
            path, key = ref.split("#", 1)
            node = self._local
            for seg in path.split("/"):
                node = node.get(seg, {})
            return node.get(key)
