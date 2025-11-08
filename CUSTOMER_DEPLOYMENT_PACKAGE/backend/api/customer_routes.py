"""
Customer Portal API Routes

FastAPI routes for the customer-facing portal, providing endpoints for:
- Authentication (login, register, token refresh)
- Workflow requests (CRUD operations, search, filtering)
- Completed workflows (view, execute, toggle status)
- Templates (browse, search, filtering)
- Analytics (metrics, trends, insights)
- Notifications (fetch, mark as read)
- File attachments (upload, download)

All routes require authentication except for login and register.
Uses JWT tokens for authentication with automatic refresh support.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import uuid

# Router setup
router = APIRouter(prefix="/api/customer", tags=["customer"])
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    industry: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    customer: dict


class WorkflowRequestCreate(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    business_value: Optional[str] = None
    technical_requirements: Optional[str] = None


class WorkflowRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    business_value: Optional[str] = None
    technical_requirements: Optional[str] = None


class CommentCreate(BaseModel):
    content: str


class PaginatedResponse(BaseModel):
    data: List[dict]
    total: int
    limit: int
    offset: int


# ============================================================================
# Authentication Utilities
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and extract customer ID"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id: str = payload.get("sub")
        if customer_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return customer_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# ============================================================================
# Authentication Routes
# ============================================================================

@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Customer login endpoint

    Validates credentials and returns access + refresh tokens.
    In production, this would verify against a database.
    """
    # TODO: Replace with actual database lookup
    # For now, accepting any email/password for demo purposes
    customer = {
        "id": str(uuid.uuid4()),
        "name": "Demo Customer",
        "email": request.email,
        "company_name": "Demo Company",
        "created_at": datetime.utcnow().isoformat(),
        "tier": "enterprise",
    }

    # Create tokens
    access_token = create_access_token(data={"sub": customer["id"]})
    refresh_token = create_refresh_token(data={"sub": customer["id"]})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        customer=customer
    )


@router.post("/auth/register")
async def register(request: RegisterRequest):
    """
    Customer registration endpoint

    Creates a new customer account.
    In production, this would:
    - Check if email already exists
    - Hash the password
    - Store in database
    - Send verification email
    """
    # TODO: Implement actual registration logic
    return {
        "message": "Registration successful. Please check your email for verification.",
        "customer_id": str(uuid.uuid4())
    }


@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token endpoint

    Takes a refresh token and returns a new access token.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        customer_id = payload.get("sub")
        new_access_token = create_access_token(data={"sub": customer_id})

        return {"access_token": new_access_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate refresh token")


# ============================================================================
# Workflow Request Routes
# ============================================================================

@router.get("/requests", response_model=PaginatedResponse)
async def get_workflow_requests(
    customer_id: str = Depends(verify_token),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    """
    Get workflow requests for the authenticated customer

    Supports pagination, filtering, and search.
    """
    # TODO: Replace with actual database query
    mock_requests = [
        {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "title": "Automated Invoice Processing",
            "description": "Process invoices from email attachments automatically",
            "category": "automation",
            "priority": "high",
            "status": "in_progress",
            "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "assigned_agents": ["chiccki_cammarano", "giancarlo_saltimbocca"],
            "tags": ["finance", "automation", "email"],
            "attachments": [],
            "comments": []
        },
        {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "title": "Customer Onboarding Flow",
            "description": "Automate new customer onboarding process",
            "category": "integration",
            "priority": "medium",
            "status": "testing",
            "created_at": (datetime.utcnow() - timedelta(days=12)).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "assigned_agents": ["collogero_aspertuno"],
            "tags": ["crm", "onboarding"],
            "attachments": [],
            "comments": []
        }
    ]

    # Apply filters (simplified for demo)
    filtered = mock_requests
    if status:
        filtered = [r for r in filtered if r["status"] == status]
    if priority:
        filtered = [r for r in filtered if r["priority"] == priority]
    if category:
        filtered = [r for r in filtered if r["category"] == category]

    return PaginatedResponse(
        data=filtered[offset:offset + limit],
        total=len(filtered),
        limit=limit,
        offset=offset
    )


@router.post("/requests", status_code=status.HTTP_201_CREATED)
async def create_workflow_request(
    request: WorkflowRequestCreate,
    customer_id: str = Depends(verify_token),
):
    """
    Create a new workflow request

    Creates a request and assigns it to the Dell Boca Boys crew.
    """
    # TODO: Store in database and trigger agent assignment
    new_request = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        **request.dict(),
        "status": "submitted",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "assigned_agents": [],
        "tags": [],
        "attachments": [],
        "comments": []
    }

    return new_request


@router.get("/requests/{request_id}")
async def get_workflow_request(
    request_id: str,
    customer_id: str = Depends(verify_token),
):
    """Get a specific workflow request by ID"""
    # TODO: Fetch from database and verify ownership
    return {
        "id": request_id,
        "customer_id": customer_id,
        "title": "Sample Request",
        "description": "Sample description",
        "category": "automation",
        "priority": "medium",
        "status": "in_progress",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "assigned_agents": ["chiccki_cammarano"],
        "tags": ["sample"],
        "attachments": [],
        "comments": []
    }


@router.patch("/requests/{request_id}")
async def update_workflow_request(
    request_id: str,
    request: WorkflowRequestUpdate,
    customer_id: str = Depends(verify_token),
):
    """Update a workflow request"""
    # TODO: Update in database and verify ownership
    return {"message": "Request updated successfully"}


@router.post("/requests/{request_id}/comments")
async def add_comment(
    request_id: str,
    comment: CommentCreate,
    customer_id: str = Depends(verify_token),
):
    """Add a comment to a workflow request"""
    # TODO: Store comment in database
    new_comment = {
        "id": str(uuid.uuid4()),
        "request_id": request_id,
        "author_id": customer_id,
        "author_name": "Customer",
        "content": comment.content,
        "created_at": datetime.utcnow().isoformat()
    }
    return new_comment


@router.post("/requests/{request_id}/attachments")
async def upload_attachment(
    request_id: str,
    file: UploadFile = File(...),
    customer_id: str = Depends(verify_token),
):
    """Upload an attachment to a workflow request"""
    # TODO: Store file and create database record
    return {
        "id": str(uuid.uuid4()),
        "request_id": request_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size": 0,  # Would calculate actual size
        "uploaded_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# Workflow Routes (Completed/Deployed)
# ============================================================================

@router.get("/workflows", response_model=PaginatedResponse)
async def get_completed_workflows(
    customer_id: str = Depends(verify_token),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    search: Optional[str] = None,
):
    """Get completed/deployed workflows for the customer"""
    # TODO: Fetch from database
    mock_workflows = [
        {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "name": "Invoice Processing Workflow",
            "description": "Automatically processes invoices from email",
            "category": "automation",
            "is_active": True,
            "execution_count": 1247,
            "success_rate": 0.987,
            "deployed_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "average_execution_time": 2340,
            "schedule": {
                "enabled": True,
                "cron": "0 */6 * * *",
                "next_run": (datetime.utcnow() + timedelta(hours=4)).isoformat()
            }
        }
    ]

    return PaginatedResponse(
        data=mock_workflows[offset:offset + limit],
        total=len(mock_workflows),
        limit=limit,
        offset=offset
    )


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    customer_id: str = Depends(verify_token),
):
    """Manually execute a workflow"""
    # TODO: Trigger workflow execution
    return {
        "execution_id": str(uuid.uuid4()),
        "workflow_id": workflow_id,
        "status": "running",
        "started_at": datetime.utcnow().isoformat()
    }


@router.patch("/workflows/{workflow_id}/status")
async def toggle_workflow_status(
    workflow_id: str,
    is_active: bool,
    customer_id: str = Depends(verify_token),
):
    """Activate or pause a workflow"""
    # TODO: Update workflow status in database
    return {
        "workflow_id": workflow_id,
        "is_active": is_active,
        "updated_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# Template Routes
# ============================================================================

@router.get("/templates", response_model=PaginatedResponse)
async def get_workflow_templates(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    """Get available workflow templates"""
    # TODO: Fetch from template repository
    mock_templates = [
        {
            "id": str(uuid.uuid4()),
            "name": "Invoice Processing",
            "description": "Automatically extract data from invoices and update accounting system",
            "category": "data_processing",
            "complexity": "moderate",
            "estimated_setup_time": "2-3 hours",
            "rating": 4.8,
            "review_count": 142,
            "usage_count": 1834,
            "tags": ["finance", "ocr", "automation"],
            "integrations": ["AWS Textract", "QuickBooks", "Email"]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Customer Onboarding",
            "description": "Streamline new customer setup across multiple systems",
            "category": "integration",
            "complexity": "simple",
            "estimated_setup_time": "1-2 hours",
            "rating": 4.9,
            "review_count": 89,
            "usage_count": 923,
            "tags": ["crm", "onboarding", "email"],
            "integrations": ["Salesforce", "Slack", "Email"]
        }
    ]

    return PaginatedResponse(
        data=mock_templates[offset:offset + limit],
        total=len(mock_templates),
        limit=limit,
        offset=offset
    )


# ============================================================================
# Analytics Routes
# ============================================================================

@router.get("/analytics")
async def get_customer_analytics(customer_id: str = Depends(verify_token)):
    """Get comprehensive analytics for the customer"""
    # TODO: Calculate actual analytics from database
    return {
        "total_requests": 24,
        "active_workflows": 8,
        "completed_workflows": 15,
        "total_executions": 12847,
        "success_rate": 0.972,
        "average_execution_time": 2340,
        "average_completion_time": 7.2,
        "total_saved_time": 458,  # hours
        "requests_trend": 15.3,
        "completion_trend": 8.7,
        "success_rate_trend": 2.1,
        "execution_history": [
            {"date": "2025-10-15", "count": 423},
            {"date": "2025-10-16", "count": 456},
            {"date": "2025-10-17", "count": 389},
            # ... more data points
        ],
        "success_rate_history": [
            {"date": "2025-10-15", "rate": 0.96},
            {"date": "2025-10-16", "rate": 0.98},
            {"date": "2025-10-17", "rate": 0.97},
            # ... more data points
        ],
        "category_distribution": {
            "automation": 12,
            "integration": 8,
            "data_processing": 6,
            "reporting": 4,
            "notification": 2,
        },
        "status_distribution": {
            "completed": 15,
            "in_progress": 5,
            "testing": 2,
            "in_review": 2,
        },
        "top_workflows": [
            {
                "id": str(uuid.uuid4()),
                "name": "Invoice Processing",
                "category": "automation",
                "execution_count": 3420,
                "success_rate": 0.99
            }
        ]
    }


# ============================================================================
# Notification Routes
# ============================================================================

@router.get("/notifications")
async def get_notifications(
    customer_id: str = Depends(verify_token),
    unread_only: bool = False,
):
    """Get notifications for the customer"""
    # TODO: Fetch from database
    mock_notifications = [
        {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "type": "success",
            "title": "Workflow Deployed",
            "message": "Your 'Invoice Processing' workflow has been successfully deployed",
            "read": False,
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "action_url": "/workflows/123"
        },
        {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "type": "info",
            "title": "Request Update",
            "message": "Your workflow request has been assigned to Giancarlo Saltimbocca",
            "read": True,
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "action_url": "/requests/456"
        }
    ]

    if unread_only:
        mock_notifications = [n for n in mock_notifications if not n["read"]]

    return mock_notifications


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    customer_id: str = Depends(verify_token),
):
    """Mark a notification as read"""
    # TODO: Update in database
    return {"message": "Notification marked as read"}


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_as_read(customer_id: str = Depends(verify_token)):
    """Mark all notifications as read"""
    # TODO: Update all in database
    return {"message": "All notifications marked as read"}
