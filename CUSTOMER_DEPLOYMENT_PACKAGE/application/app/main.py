"""
Dell Boca Boys V2 - Main FastAPI Application
The Family of AI Agents for n8n Workflow Automation

This is the main entry point for the Dell Boca Boys system.
Chiccki Cammarano (Face Agent) receives all user requests and coordinates the crew.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rulebook_enforcement import RulebookEnforcer, enforce_rules, get_enforcer
from llm_collaboration_simple import LLMCollaborator, CollaborationMode

# Import agents
from agent_face_chiccki import ChicckiCammarano
from crew.agent_pattern_analyst import ArthurDunzarelli
from crew.agent_crawler import LittleJimSpedines
from crew.agent_qa_fighter import GerryNascondino
from crew.agent_flow_planner import CollogeroAspertuno
from crew.agent_deploy_capo import PaoloEndrangheta
from crew.agent_json_compiler import SilvioPerdoname
from crew.agent_code_generator import GiancarloSaltimbocca

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Dell Boca Boys V2",
    description="The Family of AI Agents - World-class n8n workflow automation",
    version="2.0.0"
)

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load agent personalities
PERSONALITIES_PATH = Path(__file__).parent.parent / "config" / "agent_personalities.json"
with open(PERSONALITIES_PATH) as f:
    PERSONALITIES = json.load(f)

# Initialize LLM Collaborator
llm_collaborator = LLMCollaborator()

# Initialize Rulebook Enforcer
rulebook_enforcer = get_enforcer()


class UserRequest(BaseModel):
    """User request model"""
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: str = "modine"  # Default user is Modine (the boss)


class AgentResponse(BaseModel):
    """Agent response model"""
    success: bool
    message: str
    agent: str
    agent_emoji: str
    data: Optional[Dict[str, Any]] = None
    compliance_score: float
    timestamp: str


class CrewCoordinator:
    """
    🎩 Chiccki Cammarano coordinates the entire crew

    This class manages all the Dell Boca Boys agents and orchestrates their work.
    Chiccki is the face - he receives requests and delegates to specialists.
    """

    def __init__(self):
        """Initialize the crew"""
        logger.info("🎩 Chiccki: Assembling the crew...")

        # Initialize the Face Agent (Chiccki himself)
        self.face_agent = ChicckiCammarano(
            llm_collaborator=llm_collaborator,
            rulebook_enforcer=rulebook_enforcer
        )

        # Initialize all specialist agents
        self.specialists = {
            "pattern_analyst": ArthurDunzarelli(llm_collaborator, rulebook_enforcer),
            "crawler": LittleJimSpedines(llm_collaborator, rulebook_enforcer),
            "qa_fighter": GerryNascondino(llm_collaborator, rulebook_enforcer),
            "flow_planner": CollogeroAspertuno(llm_collaborator, rulebook_enforcer),
            "deploy_capo": PaoloEndrangheta(llm_collaborator, rulebook_enforcer),
            "json_compiler": SilvioPerdoname(llm_collaborator, rulebook_enforcer),
            "code_generator": GiancarloSaltimbocca(llm_collaborator, rulebook_enforcer),
        }

        logger.info("🎩 Chiccki: The crew is ready. Let's get to work.")

    @enforce_rules
    async def handle_request(self, request: UserRequest) -> AgentResponse:
        """
        Main entry point for all user requests
        Chiccki receives the request and coordinates the crew
        """
        logger.info(f"🎩 Chiccki: Got a request from {request.user_id}: {request.message[:100]}...")

        try:
            # Chiccki analyzes the request and determines which specialists to bring in
            response = await self.face_agent.process_request(
                message=request.message,
                context=request.context or {},
                specialists=self.specialists
            )

            return response

        except Exception as e:
            logger.error(f"🎩 Chiccki: We hit a snag - {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing request: {str(e)}"
            )

    async def get_crew_status(self) -> Dict[str, Any]:
        """Get status of all crew members"""
        return {
            "crew_name": PERSONALITIES["crew_name"],
            "tagline": PERSONALITIES["tagline"],
            "agents": {
                name: {
                    "name": agent.name,
                    "nickname": agent.nickname,
                    "emoji": agent.emoji,
                    "status": "ready"
                }
                for name, agent in self.specialists.items()
            },
            "face_agent": {
                "name": self.face_agent.name,
                "nickname": self.face_agent.nickname,
                "emoji": self.face_agent.emoji,
                "status": "ready"
            }
        }


# Initialize the crew coordinator
crew_coordinator = CrewCoordinator()


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - Welcome message"""
    return {
        "service": "Dell Boca Boys V2",
        "tagline": PERSONALITIES["tagline"],
        "greeting": PERSONALITIES["user_interaction"]["greeting"],
        "version": "2.0.0",
        "status": "ready"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "crew": "ready"
    }


@app.post("/request", response_model=AgentResponse)
async def handle_user_request(request: UserRequest):
    """
    Main endpoint for user requests

    🎩 Chiccki receives all requests here and coordinates the crew
    """
    response = await crew_coordinator.handle_request(request)
    return response


@app.get("/crew/status")
async def get_crew_status():
    """Get status of all crew members"""
    return await crew_coordinator.get_crew_status()


@app.get("/crew/members")
async def get_crew_members():
    """Get detailed info about all crew members"""
    return {
        "crew_name": PERSONALITIES["crew_name"],
        "agents": PERSONALITIES["agents"],
        "crew_dynamics": PERSONALITIES["crew_dynamics"]
    }


@app.post("/workflow/create")
async def create_workflow(request: UserRequest):
    """
    Create a new n8n workflow

    This is a high-level endpoint that goes through the full process:
    1. Chiccki receives request
    2. Arthur analyzes patterns
    3. Collogero plans the flow
    4. Silvio compiles the JSON
    5. Gerry validates
    6. Paolo deploys
    """
    logger.info("🎩 Chiccki: Workflow creation request. Bringing in the full crew.")

    # Add workflow creation context
    request.context = request.context or {}
    request.context["task_type"] = "workflow_creation"
    request.context["full_crew_needed"] = True

    response = await crew_coordinator.handle_request(request)
    return response


@app.post("/code/generate")
async def generate_code(request: UserRequest):
    """
    Generate Python/JavaScript code for n8n Code nodes

    🎩 Chiccki brings in Giancarlo (Code Generator)
    """
    logger.info("🎩 Chiccki: Code generation request. Bringing in Giancarlo.")

    request.context = request.context or {}
    request.context["task_type"] = "code_generation"
    request.context["specialist_needed"] = "code_generator"

    response = await crew_coordinator.handle_request(request)
    return response


@app.post("/templates/search")
async def search_templates(request: UserRequest):
    """
    Search n8n template gallery

    🎩 Chiccki brings in Little Jim (Crawler)
    """
    logger.info("🎩 Chiccki: Template search request. Bringing in Little Jim.")

    request.context = request.context or {}
    request.context["task_type"] = "template_search"
    request.context["specialist_needed"] = "crawler"

    response = await crew_coordinator.handle_request(request)
    return response


@app.post("/qa/validate")
async def validate_workflow(request: UserRequest):
    """
    Validate a workflow or JSON

    🎩 Chiccki brings in Gerry (QA Fighter)
    """
    logger.info("🎩 Chiccki: Validation request. Bringing in Gerry.")

    request.context = request.context or {}
    request.context["task_type"] = "validation"
    request.context["specialist_needed"] = "qa_fighter"

    response = await crew_coordinator.handle_request(request)
    return response


@app.get("/rulebook")
async def get_rulebook():
    """Get the 20 mandatory rules all agents follow"""
    rulebook_path = Path(__file__).parent.parent / "config" / "agent_rulebook.json"
    with open(rulebook_path) as f:
        return json.load(f)


@app.post("/rulebook/validate")
async def validate_compliance(data: Dict[str, Any]):
    """Validate data against the 20 rules"""
    compliance = rulebook_enforcer.validate_output(
        output=data.get("output"),
        context=data.get("context", {})
    )
    return compliance.dict()


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    logger.info("=" * 70)
    logger.info("🎩 Dell Boca Boys V2 - Starting Up")
    logger.info("=" * 70)
    logger.info(f"🎩 {PERSONALITIES['user_interaction']['greeting']}")
    logger.info("🎩 The crew is assembled and ready to work.")
    logger.info("=" * 70)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    logger.info("🎩 Chiccki: Shutting down. The crew is signing off.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
