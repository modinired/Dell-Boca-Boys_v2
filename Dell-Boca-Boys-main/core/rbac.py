"""
Production-grade Role-Based Access Control (RBAC) system with JWT authentication.
Implements fine-grained permissions, role hierarchies, and audit logging.
"""
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

from passlib.context import CryptContext
from pydantic import BaseModel, validator

from core.exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)


# ============================================================================
# Models and Enums
# ============================================================================

class Permission(str, Enum):
    """System permissions."""
    # Agent permissions
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"

    # Workflow permissions
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_UPDATE = "workflow:update"
    WORKFLOW_DELETE = "workflow:delete"
    WORKFLOW_EXECUTE = "workflow:execute"
    WORKFLOW_DEPLOY = "workflow:deploy"

    # Memory permissions
    MEMORY_CREATE = "memory:create"
    MEMORY_READ = "memory:read"
    MEMORY_UPDATE = "memory:update"
    MEMORY_DELETE = "memory:delete"

    # System permissions
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_METRICS = "system:metrics"
    SYSTEM_AUDIT = "system:audit"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"


class Role(str, Enum):
    """Predefined roles with permission sets."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    OPERATOR = "operator"
    VIEWER = "viewer"
    GUEST = "guest"


@dataclass
class User:
    """User model."""
    user_id: str
    username: str
    email: str
    hashed_password: str
    roles: Set[Role] = field(default_factory=set)
    permissions: Set[Permission] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: str  # Subject (user_id)
    username: str
    roles: List[str]
    permissions: List[str]
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    jti: str  # JWT ID (unique token identifier)

    @validator('exp')
    def check_expiration(cls, v):
        if v < int(datetime.utcnow().timestamp()):
            raise ValueError("Token has expired")
        return v


# ============================================================================
# RBAC Manager
# ============================================================================

class RBACManager:
    """
    Comprehensive RBAC management system.

    Features:
    - Role-based access control
    - Fine-grained permissions
    - JWT token generation and validation
    - Password hashing and verification
    - Audit logging
    - Session management
    """

    # Role permission mappings
    ROLE_PERMISSIONS = {
        Role.ADMIN: {
            # Full system access
            Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE,
            Permission.AGENT_DELETE, Permission.AGENT_EXECUTE,
            Permission.WORKFLOW_CREATE, Permission.WORKFLOW_READ, Permission.WORKFLOW_UPDATE,
            Permission.WORKFLOW_DELETE, Permission.WORKFLOW_EXECUTE, Permission.WORKFLOW_DEPLOY,
            Permission.MEMORY_CREATE, Permission.MEMORY_READ, Permission.MEMORY_UPDATE,
            Permission.MEMORY_DELETE,
            Permission.SYSTEM_ADMIN, Permission.SYSTEM_CONFIG, Permission.SYSTEM_METRICS,
            Permission.SYSTEM_AUDIT,
            Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
            Permission.USER_DELETE,
        },
        Role.DEVELOPER: {
            # Development and deployment
            Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE,
            Permission.AGENT_EXECUTE,
            Permission.WORKFLOW_CREATE, Permission.WORKFLOW_READ, Permission.WORKFLOW_UPDATE,
            Permission.WORKFLOW_EXECUTE, Permission.WORKFLOW_DEPLOY,
            Permission.MEMORY_CREATE, Permission.MEMORY_READ, Permission.MEMORY_UPDATE,
            Permission.SYSTEM_METRICS,
        },
        Role.ANALYST: {
            # Read and analysis
            Permission.AGENT_READ, Permission.AGENT_EXECUTE,
            Permission.WORKFLOW_READ, Permission.WORKFLOW_EXECUTE,
            Permission.MEMORY_READ,
            Permission.SYSTEM_METRICS,
        },
        Role.OPERATOR: {
            # Execute and monitor
            Permission.AGENT_READ, Permission.AGENT_EXECUTE,
            Permission.WORKFLOW_READ, Permission.WORKFLOW_EXECUTE,
            Permission.MEMORY_READ,
            Permission.SYSTEM_METRICS,
        },
        Role.VIEWER: {
            # Read-only access
            Permission.AGENT_READ,
            Permission.WORKFLOW_READ,
            Permission.MEMORY_READ,
            Permission.SYSTEM_METRICS,
        },
        Role.GUEST: {
            # Minimal access
            Permission.WORKFLOW_READ,
        },
    }

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 30
    ):
        """
        Initialize RBAC manager.

        Args:
            secret_key: Secret key for JWT signing (auto-generated if None)
            algorithm: JWT algorithm
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
        """
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

        # Password hashing context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # In-memory user store (replace with database in production)
        self.users: Dict[str, User] = {}

        # Revoked tokens (for logout)
        self.revoked_tokens: Set[str] = set()

        logger.info("RBAC Manager initialized")

    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        return secrets.token_urlsafe(32)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[Set[Role]] = None,
        additional_permissions: Optional[Set[Permission]] = None
    ) -> User:
        """
        Create a new user.

        Args:
            username: Username
            email: Email address
            password: Plain text password
            roles: User roles
            additional_permissions: Additional permissions beyond role defaults

        Returns:
            Created user
        """
        user_id = hashlib.sha256(f"{username}{email}{datetime.utcnow()}".encode()).hexdigest()[:16]

        # Calculate effective permissions
        effective_permissions = set()
        for role in (roles or {Role.VIEWER}):
            effective_permissions.update(self.ROLE_PERMISSIONS.get(role, set()))

        if additional_permissions:
            effective_permissions.update(additional_permissions)

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            hashed_password=self.hash_password(password),
            roles=roles or {Role.VIEWER},
            permissions=effective_permissions
        )

        self.users[user_id] = user
        logger.info(f"Created user: {username} (ID: {user_id})")

        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        # Find user by username
        user = next((u for u in self.users.values() if u.username == username), None)

        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {username}")
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password - {username}")
            return None

        # Update last login
        user.last_login = datetime.utcnow()

        logger.info(f"User authenticated: {username}")
        return user

    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.

        Args:
            user: User object
            expires_delta: Token expiration delta (overrides default)

        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        )

        payload = {
            "sub": user.user_id,
            "username": user.username,
            "roles": [role.value for role in user.roles],
            "permissions": [perm.value for perm in user.permissions],
            "exp": int(expire.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created access token for user: {user.username}")

        return token

    def create_refresh_token(self, user: User) -> str:
        """
        Create JWT refresh token.

        Args:
            user: User object

        Returns:
            JWT refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user.user_id,
            "username": user.username,
            "type": "refresh",
            "exp": int(expire.timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "jti": secrets.token_urlsafe(16)
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created refresh token for user: {user.username}")

        return token

    def verify_token(self, token: str) -> TokenPayload:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Check if token is revoked
            jti = payload.get("jti")
            if jti in self.revoked_tokens:
                raise AuthenticationError("Token has been revoked")

            # Validate payload structure
            token_data = TokenPayload(**payload)

            return token_data

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")

    def revoke_token(self, token: str):
        """
        Revoke a token (logout).

        Args:
            token: JWT token string
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Don't verify expiration for revocation
            )
            jti = payload.get("jti")
            if jti:
                self.revoked_tokens.add(jti)
                logger.info(f"Token revoked: {jti}")
        except jwt.JWTError as e:
            logger.warning(f"Failed to revoke token: {e}")

    def check_permission(
        self,
        user: User,
        required_permission: Permission
    ) -> bool:
        """
        Check if user has a specific permission.

        Args:
            user: User object
            required_permission: Required permission

        Returns:
            True if user has permission
        """
        # Admins have all permissions
        if Role.ADMIN in user.roles:
            return True

        return required_permission in user.permissions

    def check_permissions(
        self,
        user: User,
        required_permissions: Set[Permission],
        require_all: bool = True
    ) -> bool:
        """
        Check if user has multiple permissions.

        Args:
            user: User object
            required_permissions: Set of required permissions
            require_all: If True, user must have all permissions.
                        If False, user must have at least one.

        Returns:
            True if permission check passes
        """
        # Admins have all permissions
        if Role.ADMIN in user.roles:
            return True

        if require_all:
            return required_permissions.issubset(user.permissions)
        else:
            return bool(required_permissions.intersection(user.permissions))

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def update_user_roles(self, user_id: str, new_roles: Set[Role]) -> User:
        """
        Update user roles.

        Args:
            user_id: User ID
            new_roles: New role set

        Returns:
            Updated user

        Raises:
            ValueError: If user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        user.roles = new_roles

        # Recalculate permissions
        effective_permissions = set()
        for role in new_roles:
            effective_permissions.update(self.ROLE_PERMISSIONS.get(role, set()))

        user.permissions = effective_permissions

        logger.info(f"Updated roles for user {user.username}: {[r.value for r in new_roles]}")

        return user

    def add_user_permission(self, user_id: str, permission: Permission) -> User:
        """Add a custom permission to a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        user.permissions.add(permission)
        logger.info(f"Added permission {permission.value} to user {user.username}")

        return user

    def remove_user_permission(self, user_id: str, permission: Permission) -> User:
        """Remove a permission from a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User not found: {user_id}")

        user.permissions.discard(permission)
        logger.info(f"Removed permission {permission.value} from user {user.username}")

        return user


# ============================================================================
# Decorators
# ============================================================================

def require_permission(permission: Permission):
    """
    Decorator to require a specific permission.

    Example:
        @require_permission(Permission.WORKFLOW_EXECUTE)
        async def execute_workflow(user: User, workflow_id: str):
            ...
    """
    def decorator(func):
        async def wrapper(*args, user: User, **kwargs):
            rbac = get_global_rbac()
            if not rbac.check_permission(user, permission):
                raise AuthorizationError(
                    user_id=user.user_id,
                    resource=func.__name__,
                    action=permission.value
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Decorator to require a specific role.

    Example:
        @require_role(Role.ADMIN)
        async def admin_function(user: User):
            ...
    """
    def decorator(func):
        async def wrapper(*args, user: User, **kwargs):
            if role not in user.roles:
                raise AuthorizationError(
                    user_id=user.user_id,
                    resource=func.__name__,
                    action=f"role:{role.value}"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Global RBAC Instance
# ============================================================================

_global_rbac: Optional[RBACManager] = None


def init_rbac(secret_key: Optional[str] = None, **kwargs) -> RBACManager:
    """Initialize global RBAC manager."""
    global _global_rbac
    _global_rbac = RBACManager(secret_key=secret_key, **kwargs)
    return _global_rbac


def get_global_rbac() -> RBACManager:
    """Get global RBAC manager instance."""
    if _global_rbac is None:
        raise RuntimeError("RBAC manager not initialized. Call init_rbac() first.")
    return _global_rbac
