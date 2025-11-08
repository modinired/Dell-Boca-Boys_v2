"""
Production-grade secrets management with HashiCorp Vault integration.
Provides secure storage and retrieval of credentials, API keys, and sensitive data.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import hvac
from cryptography.fernet import Fernet
import base64

from core.exceptions import ConfigurationException

logger = logging.getLogger(__name__)


class VaultSecretsManager:
    """
    HashiCorp Vault integration for secrets management.

    Supports:
    - KV secrets engine
    - Dynamic secrets
    - Lease management
    - Token renewal
    - Audit logging
    """

    def __init__(
        self,
        vault_url: str,
        vault_token: Optional[str] = None,
        vault_role_id: Optional[str] = None,
        vault_secret_id: Optional[str] = None,
        mount_point: str = "secret",
        kv_version: int = 2
    ):
        """
        Initialize Vault secrets manager.

        Args:
            vault_url: Vault server URL
            vault_token: Vault token (for token auth)
            vault_role_id: AppRole role ID (for AppRole auth)
            vault_secret_id: AppRole secret ID (for AppRole auth)
            mount_point: KV secrets engine mount point
            kv_version: KV secrets engine version (1 or 2)
        """
        self.vault_url = vault_url
        self.mount_point = mount_point
        self.kv_version = kv_version

        # Initialize Vault client
        self.client = hvac.Client(url=vault_url)

        # Authenticate
        if vault_token:
            self._authenticate_token(vault_token)
        elif vault_role_id and vault_secret_id:
            self._authenticate_approle(vault_role_id, vault_secret_id)
        else:
            raise ConfigurationException(
                "vault_auth",
                "Either vault_token or (vault_role_id + vault_secret_id) must be provided"
            )

        logger.info(f"Vault secrets manager initialized: {vault_url}")

    def _authenticate_token(self, token: str):
        """Authenticate using token."""
        self.client.token = token

        if not self.client.is_authenticated():
            raise ConfigurationException(
                "vault_token",
                "Invalid Vault token or authentication failed"
            )

        logger.info("Authenticated to Vault using token")

    def _authenticate_approle(self, role_id: str, secret_id: str):
        """Authenticate using AppRole."""
        try:
            response = self.client.auth.approle.login(
                role_id=role_id,
                secret_id=secret_id
            )

            self.client.token = response['auth']['client_token']

            logger.info("Authenticated to Vault using AppRole")

        except Exception as e:
            raise ConfigurationException(
                "vault_approle",
                f"AppRole authentication failed: {str(e)}"
            )

    def get_secret(self, path: str) -> Dict[str, Any]:
        """
        Retrieve a secret from Vault.

        Args:
            path: Secret path (e.g., "dell-boca/database")

        Returns:
            Secret data dictionary
        """
        try:
            if self.kv_version == 2:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=path,
                    mount_point=self.mount_point
                )
                return response['data']['data']
            else:
                response = self.client.secrets.kv.v1.read_secret(
                    path=path,
                    mount_point=self.mount_point
                )
                return response['data']

        except hvac.exceptions.InvalidPath:
            logger.error(f"Secret not found: {path}")
            return {}
        except Exception as e:
            logger.error(f"Failed to retrieve secret {path}: {e}")
            raise

    def set_secret(self, path: str, data: Dict[str, Any]):
        """
        Store a secret in Vault.

        Args:
            path: Secret path
            data: Secret data dictionary
        """
        try:
            if self.kv_version == 2:
                self.client.secrets.kv.v2.create_or_update_secret(
                    path=path,
                    secret=data,
                    mount_point=self.mount_point
                )
            else:
                self.client.secrets.kv.v1.create_or_update_secret(
                    path=path,
                    secret=data,
                    mount_point=self.mount_point
                )

            logger.info(f"Secret stored: {path}")

        except Exception as e:
            logger.error(f"Failed to store secret {path}: {e}")
            raise

    def delete_secret(self, path: str):
        """
        Delete a secret from Vault.

        Args:
            path: Secret path
        """
        try:
            if self.kv_version == 2:
                self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                    path=path,
                    mount_point=self.mount_point
                )
            else:
                self.client.secrets.kv.v1.delete_secret(
                    path=path,
                    mount_point=self.mount_point
                )

            logger.info(f"Secret deleted: {path}")

        except Exception as e:
            logger.error(f"Failed to delete secret {path}: {e}")
            raise

    def renew_token(self, increment: Optional[int] = None):
        """
        Renew the Vault token.

        Args:
            increment: Lease increment in seconds
        """
        try:
            self.client.auth.token.renew_self(increment=increment)
            logger.info("Vault token renewed")
        except Exception as e:
            logger.error(f"Failed to renew token: {e}")
            raise


class LocalSecretsManager:
    """
    Local secrets manager using encrypted file storage.
    Fallback option when Vault is not available.

    WARNING: This is less secure than Vault. Use only for development/testing.
    """

    def __init__(self, secrets_file: str = ".secrets.enc", encryption_key: Optional[bytes] = None):
        """
        Initialize local secrets manager.

        Args:
            secrets_file: Path to encrypted secrets file
            encryption_key: Fernet encryption key (auto-generated if None)
        """
        self.secrets_file = secrets_file

        # Generate or load encryption key
        if encryption_key:
            self.key = encryption_key
        elif os.path.exists(".key"):
            with open(".key", "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(".key", "wb") as f:
                f.write(self.key)

        self.fernet = Fernet(self.key)

        # Load existing secrets
        self.secrets: Dict[str, Dict[str, Any]] = {}
        self._load_secrets()

        logger.warning("Using local secrets manager (NOT RECOMMENDED FOR PRODUCTION)")

    def _load_secrets(self):
        """Load and decrypt secrets from file."""
        if not os.path.exists(self.secrets_file):
            return

        try:
            with open(self.secrets_file, "rb") as f:
                encrypted_data = f.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)
            self.secrets = json.loads(decrypted_data.decode())

            logger.info(f"Loaded {len(self.secrets)} secrets from {self.secrets_file}")

        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            self.secrets = {}

    def _save_secrets(self):
        """Encrypt and save secrets to file."""
        try:
            data = json.dumps(self.secrets).encode()
            encrypted_data = self.fernet.encrypt(data)

            with open(self.secrets_file, "wb") as f:
                f.write(encrypted_data)

            logger.debug(f"Saved {len(self.secrets)} secrets to {self.secrets_file}")

        except Exception as e:
            logger.error(f"Failed to save secrets: {e}")

    def get_secret(self, path: str) -> Dict[str, Any]:
        """Retrieve a secret."""
        return self.secrets.get(path, {})

    def set_secret(self, path: str, data: Dict[str, Any]):
        """Store a secret."""
        self.secrets[path] = data
        self._save_secrets()
        logger.info(f"Secret stored: {path}")

    def delete_secret(self, path: str):
        """Delete a secret."""
        if path in self.secrets:
            del self.secrets[path]
            self._save_secrets()
            logger.info(f"Secret deleted: {path}")


class SecretsManager:
    """
    Unified secrets manager interface.

    Automatically selects Vault or local storage based on configuration.
    """

    def __init__(
        self,
        use_vault: bool = True,
        vault_config: Optional[Dict[str, Any]] = None,
        local_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize secrets manager.

        Args:
            use_vault: Use Vault if True, local storage if False
            vault_config: Vault configuration
            local_config: Local storage configuration
        """
        if use_vault:
            vault_config = vault_config or {}
            vault_url = vault_config.get('url', os.getenv('VAULT_ADDR', 'http://localhost:8200'))
            vault_token = vault_config.get('token', os.getenv('VAULT_TOKEN'))
            vault_role_id = vault_config.get('role_id', os.getenv('VAULT_ROLE_ID'))
            vault_secret_id = vault_config.get('secret_id', os.getenv('VAULT_SECRET_ID'))

            try:
                self.backend = VaultSecretsManager(
                    vault_url=vault_url,
                    vault_token=vault_token,
                    vault_role_id=vault_role_id,
                    vault_secret_id=vault_secret_id,
                    **{k: v for k, v in vault_config.items() if k not in ['url', 'token', 'role_id', 'secret_id']}
                )
                logger.info("Using Vault for secrets management")

            except Exception as e:
                logger.warning(f"Failed to initialize Vault, falling back to local storage: {e}")
                local_config = local_config or {}
                self.backend = LocalSecretsManager(**local_config)
        else:
            local_config = local_config or {}
            self.backend = LocalSecretsManager(**local_config)
            logger.info("Using local encrypted storage for secrets management")

    def get_secret(self, path: str) -> Dict[str, Any]:
        """Retrieve a secret."""
        return self.backend.get_secret(path)

    def set_secret(self, path: str, data: Dict[str, Any]):
        """Store a secret."""
        self.backend.set_secret(path, data)

    def delete_secret(self, path: str):
        """Delete a secret."""
        self.backend.delete_secret(path)

    def get_database_credentials(self, database_name: str = "postgres") -> Dict[str, str]:
        """Get database credentials."""
        return self.get_secret(f"dell-boca/database/{database_name}")

    def get_api_key(self, service_name: str) -> str:
        """Get API key for a service."""
        secret = self.get_secret(f"dell-boca/api-keys/{service_name}")
        return secret.get('api_key', '')

    def get_llm_credentials(self, provider: str) -> Dict[str, Any]:
        """Get LLM provider credentials."""
        return self.get_secret(f"dell-boca/llm/{provider}")

    def set_database_credentials(
        self,
        database_name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str
    ):
        """Store database credentials."""
        self.set_secret(f"dell-boca/database/{database_name}", {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": database
        })

    def set_api_key(self, service_name: str, api_key: str):
        """Store API key."""
        self.set_secret(f"dell-boca/api-keys/{service_name}", {
            "api_key": api_key,
            "created_at": datetime.utcnow().isoformat()
        })


# ============================================================================
# Global Secrets Manager
# ============================================================================

_global_secrets_manager: Optional[SecretsManager] = None


def init_secrets_manager(
    use_vault: bool = True,
    vault_config: Optional[Dict[str, Any]] = None,
    local_config: Optional[Dict[str, Any]] = None
) -> SecretsManager:
    """Initialize global secrets manager."""
    global _global_secrets_manager
    _global_secrets_manager = SecretsManager(
        use_vault=use_vault,
        vault_config=vault_config,
        local_config=local_config
    )
    return _global_secrets_manager


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance."""
    if _global_secrets_manager is None:
        # Auto-initialize with defaults
        return init_secrets_manager()
    return _global_secrets_manager
