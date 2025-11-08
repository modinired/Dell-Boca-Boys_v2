"""
FastAPI Backend for Dell Bocca Boys Dashboard
Provides REST API and WebSocket endpoints for real-time updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import json
import logging

# Import core modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.intelligence.cesar_multi_agent_network import CESARMultiAgentNetwork
from core.communication.email_service import DellBoccaBoysEmailService
from core.websocket.manager import WebSocketManager

logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Dell Bocca Boys Dashboard API",
    description="REST API and WebSocket endpoints for the Dell Bocca Boys multi-agent dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services
ws_manager = WebSocketManager()
email_service: Optional[DellBoccaBoysEmailService] = None
cesar_network: Optional[CESARMultiAgentNetwork] = None

# Pydantic models
class AgentStatus(BaseModel):
    id: str
    name: str
    role: str
    status: str
    current_task: Optional[str]
    tasks_completed: int
    performance: Dict[str, Any]
    last_active: datetime

class Task(BaseModel):
    id: str
    type: str
    priority: str
    status: str
    title: str
    description: str
    assigned_agents: List[str]
    created_at: datetime
    updated_at: datetime

class EmailMessage(BaseModel):
    id: str
    message_id: str
    from_address: str
    to_address: str
    subject: str
    body_text: str
    received_at: datetime
    processed: bool
    task_id: Optional[str]

class SystemStats(BaseModel):
    total_tasks: int
    tasks_today: int
    active_agents: int
    emails_processed: int
    average_response_time: float
    success_rate: float
    uptime: int

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")

manager = ConnectionManager()

# ============================================================================
# REST API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "Dell Bocca Boys Dashboard API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/agents", response_model=List[AgentStatus])
async def get_agents():
    """Get all CESAR agents and their current status"""
    # TODO: Integrate with actual CESAR network
    # For now, return mock data
    agents = [
        {
            "id": "terry_delmonaco",
            "name": "Terry Delmonaco",
            "role": "Chief Technology & Quantitative Officer",
            "status": "active",
            "current_task": None,
            "tasks_completed": 42,
            "performance": {
                "success_rate": 0.95,
                "average_time": 120,
                "tasks_today": 8
            },
            "last_active": datetime.utcnow()
        },
        # Add other agents...
    ]
    return agents

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks(status: Optional[str] = None):
    """Get all tasks, optionally filtered by status"""
    # TODO: Integrate with task database
    tasks = []
    return tasks

@app.post("/api/tasks")
async def create_task(task: Task):
    """Create a new task"""
    # TODO: Create task and route to appropriate agents
    await manager.broadcast({
        "type": "task_update",
        "action": "created",
        "task": task.dict()
    })
    return {"status": "created", "task_id": task.id}

@app.get("/api/emails", response_model=List[EmailMessage])
async def get_emails(processed: Optional[bool] = None):
    """Get all emails, optionally filtered by processed status"""
    # TODO: Integrate with email storage
    emails = []
    return emails

@app.get("/api/email-service/status")
async def get_email_service_status():
    """Get email service status"""
    if email_service:
        return {
            "is_running": email_service.is_running,
            "email_address": email_service.email_address,
            "poll_interval": email_service.poll_interval,
            "processed_messages": 0,  # TODO: Get from service
            "last_check": datetime.utcnow(),
            "error": None
        }
    return {
        "is_running": False,
        "email_address": "ace.llc.nyc@gmail.com",
        "poll_interval": 60,
        "processed_messages": 0,
        "last_check": None,
        "error": "Service not initialized"
    }

@app.post("/api/email-service/start")
async def start_email_service():
    """Start the email monitoring service"""
    global email_service
    try:
        if not email_service:
            email_service = DellBoccaBoysEmailService()
        # Start service in background
        asyncio.create_task(email_service.start())
        return {"status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/email-service/stop")
async def stop_email_service():
    """Stop the email monitoring service"""
    if email_service:
        await email_service.stop()
        return {"status": "stopped"}
    return {"status": "not_running"}

@app.get("/api/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system-wide statistics"""
    return {
        "total_tasks": 156,
        "tasks_today": 24,
        "active_agents": 4,
        "emails_processed": 89,
        "average_response_time": 2500,  # ms
        "success_rate": 0.94,
        "uptime": 7200  # seconds
    }

@app.get("/api/collaborations")
async def get_collaborations():
    """Get agent collaborations"""
    # TODO: Get from collaboration tracking
    return []

@app.get("/api/workflows")
async def get_workflows():
    """Get all workflows"""
    # TODO: Get from workflow database
    return []

@app.post("/api/workflows")
async def create_workflow(workflow: dict):
    """Create a new workflow"""
    # TODO: Save workflow
    return {"status": "created", "workflow_id": workflow.get("id")}

@app.get("/api/notifications")
async def get_notifications():
    """Get system notifications"""
    # TODO: Get from notification system
    return []

# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle subscription requests
            if message.get("action") == "subscribe":
                topic = message.get("topic")
                logger.info(f"Client subscribed to topic: {topic}")
                await websocket.send_json({
                    "type": "subscription",
                    "topic": topic,
                    "status": "subscribed"
                })

            # Echo other messages for testing
            else:
                await websocket.send_json({
                    "type": "echo",
                    "data": message
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")

# ============================================================================
# Background Tasks
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Dell Bocca Boys Dashboard API...")

    # Initialize CESAR network
    global cesar_network
    try:
        from core.intelligence.cesar_multi_agent_network import CESARMultiAgentNetwork
        cesar_network = CESARMultiAgentNetwork()
        logger.info("CESAR multi-agent network initialized")
    except Exception as e:
        logger.error(f"Failed to initialize CESAR network: {e}")

    # Start background task for periodic broadcasts
    asyncio.create_task(broadcast_updates())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Dell Bocca Boys Dashboard API...")
    if email_service:
        await email_service.stop()

async def broadcast_updates():
    """Periodically broadcast system updates to all connected clients"""
    while True:
        await asyncio.sleep(5)  # Broadcast every 5 seconds

        try:
            # Broadcast system stats update
            stats = await get_system_stats()
            await manager.broadcast({
                "type": "system_update",
                "stats": stats.dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error broadcasting updates: {e}")

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
