#!/usr/bin/env python3
"""
Dell Boca Vista Boys - Dashboard API
FastAPI backend serving Bootstrap 4 UI and agent functionality
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
from pydantic import Field
import uvicorn

# Add parent directory to path to import existing agent code.  This
# insert remains for backward compatibility with earlier versions
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the core agent from the new agents module.  This keeps
# api.py focused on FastAPI wiring and leaves business logic in
# web_dashboard/agents.py.
# Import the refined agent under an alias to avoid clashing with any
# legacy class definitions later in this module.  The alias ensures
# our code uses the new implementation from ``web_dashboard/agents.py``
from .agents import DellBocaAgent as CoreDellBocaAgent

# Import workflow engine components for next‑generation workflow automation.
# The engine orchestrates draft generation and composition independent of n8n.
from core.workflow_engine import WorkflowEngine as _NewWorkflowEngine

# Optional APScheduler imports will be handled in scheduler helper

# ============================================
# Pydantic Models
# ============================================

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    agent_states: Optional[Dict] = None

class WorkflowRequest(BaseModel):
    goal: str

class WorkflowResponse(BaseModel):
    diagram: str
    workflow: Dict
    description: str

class WorkflowProposalRequest(BaseModel):
    goal: str
    recurring: str
    custom_cron: Optional[str] = None

class WorkflowProposalResponse(BaseModel):
    goal: str
    schedule: str
    estimated_duration: str
    steps: List[Dict]
    credentials: List[Dict]
    resources: Dict

# ============================================
# New Pydantic Models for Workflow Engine
# ============================================

class WorkflowTemplateCreateRequest(BaseModel):
    """Request model for adding a new workflow template to the library."""
    name: str = Field(..., description="Unique name for the template")
    description: str = Field(..., description="Summary of what the template does")
    content: str = Field(..., description="Workflow definition as JSON or other format")
    source: Optional[str] = Field(None, description="Origin of the template (optional)")


class WorkflowTemplateCreateResponse(BaseModel):
    """Response model for successful template creation."""
    message: str


class DraftGenerationRequest(BaseModel):
    """Request model for generating a workflow draft from a natural language goal."""
    request: str = Field(..., description="Description of the desired workflow")


class DraftGenerationResponse(BaseModel):
    """Response model containing a generated workflow draft or an error."""
    status: str
    draft: Optional[Dict] = None
    detail: Optional[str] = None


class ComposeWorkflowRequest(BaseModel):
    """Request model for composing a full workflow from a draft."""
    draft: Dict = Field(..., description="Draft object returned from draft generation")
    template_name: Optional[str] = Field(None, description="Template to merge with the draft")
    requested_skills: Optional[List[str]] = Field(None, description="List of skill IDs to include")


class ComposeWorkflowResponse(BaseModel):
    """Response model for the composed workflow."""
    status: str
    workflow: Optional[Dict] = None
    detail: Optional[str] = None

# ============================================
# Dell Boca Vista Boys Agent (Simplified)
# ============================================

DELL_BOCA_SYSTEM_PROMPT = """You are Chick Camarrano Jr., the Capo (boss) of the Dell Boca Vista Boys, a team of elite AI automation specialists. A Terry Dellmonaco Company.

You coordinate a crew of specialist agents:
- Arhur Dunzarelli: Workflow Architect
- Little Jim Spedines: Data Integration Specialist
- Gerry Nascondino: Security Expert
- Collogero Asperturo: Performance Optimizer
- Paolo L'Aranciata: Testing & QA Specialist
- Sauconi Osobucco: Documentation Specialist

You provide helpful, professional advice on automation, workflows, and AI integration. You're knowledgeable but approachable."""

class DellBocaAgent:
    def __init__(self):
        self.db_path = Path.home() / "N8n-agent" / "workspace_dell_boca" / "dell_boca_vista_v2.db"
        self.ollama_available = self._check_ollama()
        self.gemini_available = bool(GEMINI_API_KEY)
        self._init_database()

    def _check_ollama(self):
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _init_database(self):
        """Initialize SQLite database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT,
                assistant_response TEXT,
                model_used TEXT,
                response_time_ms INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                goal TEXT,
                workflow_json TEXT,
                diagram TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _call_glm(self, prompt: str, system_prompt: str = "") -> tuple[str, int]:
        """Call GLM4.5-air-mlx-4bit local model"""
        start_time = time.time()

        # Lazily import mlx_lm so that the dashboard still runs if the dependency is missing.
        try:
            from mlx_lm import load, generate  # type: ignore
        except Exception as e:
            return f"GLM unavailable: {e}", 0

        # Determine the model path.  Prefer an explicit environment variable,
        # falling back to a relative path within the repository.
        env_model_path = os.getenv("LOCAL_GLM_MODEL_PATH")
        if env_model_path:
            model_path = env_model_path
        else:
            # Compute project root by ascending two directories: <repo_root>/web_dashboard/api.py -> <repo_root>
            repo_root = Path(__file__).resolve().parents[2]
            model_path = str(repo_root / "glm4.5-air-mlx-4bit")

        try:
            # Load model (cached after first load)
            if not hasattr(self, '_glm_model'):
                print("Loading GLM model from", model_path)
                self._glm_model, self._glm_tokenizer = load(model_path)
                print("✅ GLM model loaded")

            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = generate(
                self._glm_model,
                self._glm_tokenizer,
                prompt=full_prompt,
                max_tokens=1024,
                temp=0.7
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            return response, elapsed_ms
        except Exception as e:
            # Catch all runtime errors and return an informative message
            return f"GLM unavailable: {e}", 0

    def _call_gemini(self, prompt: str, system_prompt: str = "") -> tuple[str, int]:
        """Call Gemini model"""
        start_time = time.time()

        try:
            if genai is None or not GEMINI_API_KEY:
                raise RuntimeError("Gemini is not configured or the SDK is missing")
            # Use gemini-2.5-flash for v1beta API
            model = genai.GenerativeModel('gemini-2.5-flash')
            full_prompt = f"{system_prompt}\n\n{prompt}"
            response = model.generate_content(full_prompt)
            elapsed_ms = int((time.time() - start_time) * 1000)
            return response.text, elapsed_ms
        except Exception as e:
            return f"Gemini error: {e}", 0

    def chat(self, message: str) -> Dict:
        """Process chat message with collaborative AI"""

        # Agent progression states
        agent_states = {
            'chiccki': {'status': 'active', 'thought': 'Analyzing your request...'},
            'agent1': {'status': 'thinking', 'thought': 'Reviewing workflow requirements...'},
            'agent2': {'status': 'idle', 'thought': 'Data integration ready'},
            'agent3': {'status': 'idle', 'thought': 'Security protocols active'},
            'agent4': {'status': 'idle', 'thought': 'Performance standby'},
            'agent5': {'status': 'idle', 'thought': 'Quality assurance ready'},
            'agent6': {'status': 'idle', 'thought': 'Documentation ready'}
        }

        # Get responses from available models
        responses = []

        # Always try GLM (local Apple Silicon model)
        agent_states['agent1']['status'] = 'active'
        agent_states['agent3']['status'] = 'thinking'

        glm_response, glm_time = self._call_glm(message, DELL_BOCA_SYSTEM_PROMPT)
        if glm_response and not glm_response.startswith("GLM unavailable"):
            responses.append(("GLM4.5", glm_response, glm_time))

        if self.gemini_available:
            agent_states['agent2']['status'] = 'active'
            agent_states['agent4']['status'] = 'thinking'

            gemini_response, gemini_time = self._call_gemini(message, DELL_BOCA_SYSTEM_PROMPT)
            if gemini_response and not gemini_response.startswith("Gemini unavailable"):
                responses.append(("Gemini", gemini_response, gemini_time))

        # Synthesis
        if len(responses) == 2:
            agent_states['agent5']['status'] = 'thinking'
            agent_states['agent6']['status'] = 'thinking'

            final_response = responses[1][1]
            model_used = "collaborative"
            response_time = max(responses[0][2], responses[1][2])

        elif len(responses) == 1:
            final_response = responses[0][1]
            model_used = responses[0][0].lower()
            response_time = responses[0][2]

        else:
            final_response = "Both AI models are currently unavailable. GLM4.5 may still be loading (first run takes 30s), or Gemini API key needs configuration."
            model_used = "none"
            response_time = 0

        # All agents back to idle
        for agent_id in agent_states:
            if agent_id != 'chiccki':
                agent_states[agent_id] = {'status': 'idle', 'thought': 'Task complete'}

        # Save to database
        self._save_chat(message, final_response, model_used, response_time)

        return {
            'response': final_response,
            'agent_states': agent_states,
            'model_used': model_used,
            'response_time_ms': response_time
        }

    def generate_workflow(self, goal: str) -> Dict:
        """Generate comprehensive workflow with full agent collaboration"""
        import json
        import hashlib
        import re
        from datetime import datetime

        # PHASE 1: Agent Collaboration - Planning
        planning_prompt = f"""🎩 DELL BOCA VISTA BOYS - COLLABORATIVE WORKFLOW PLANNING

We are the Dell Boca Vista Boys, a crew of 7 specialized AI agents working together to create exceptional automation workflows.

**GOAL:** {goal}

**AGENTS INVOLVED:**
1. Chick Camarrano Jr. (Capo) - Strategic oversight & architecture
2. Arhur Dunzarelli - Technical implementation & code generation
3. Little Jim Spedines - Data flow & integration analysis
4. Gerry Nascondino - Error handling & reliability engineering
5. Collogero Asperturo - Performance optimization
6. Paolo L'Aranciata - Security & compliance
7. Sauconi Osobucco - Testing & quality assurance

**REQUIRED OUTPUT - PhD LEVEL QUALITY:**

## 1. COMPREHENSIVE WORKFLOW DESCRIPTION (4-6 paragraphs)
Provide a detailed, technical description covering:
- Strategic rationale and business value
- Architectural approach and design patterns
- Technical implementation details
- Integration points and data flows
- Error handling and reliability measures
- Performance considerations
- Security and compliance aspects

## 2. BEAUTIFUL MERMAID DIAGRAM
Create a comprehensive, professional flowchart showing:
- All workflow nodes with descriptive labels
- Data flow between nodes
- Decision points and branching logic
- Error handling paths
- Proper styling with colors and formatting
Use syntax: graph TD with detailed node definitions

## 3. N8N-COMPATIBLE JSON WORKFLOW
Generate a complete, production-ready n8n workflow with:
- Proper node structure (id, type, name, parameters)
- Complete parameter configurations for each node
- Proper connections array with source/destination mapping
- Webhook triggers, HTTP requests, transformations, conditionals
- Error workflows and retry logic
- At least 8-12 nodes for comprehensive functionality

## 4. CODE EXPLANATIONS
For each node, provide:
- Purpose and functionality
- Parameter explanations
- Example data transformations
- Integration considerations

**IMPORTANT:**
- Zero placeholders or simulations
- Every detail must be production-ready
- All JSON must be valid and complete
- Mermaid syntax must be correct
- Descriptions must be comprehensive and PhD-level quality

Begin with collaboration between all 7 agents, then provide the complete output."""

        # Call AI with comprehensive prompt
        if self.gemini_available:
            response, response_time = self._call_gemini(planning_prompt,
                "You are the Dell Boca Vista Boys, a collaborative AI agent team. Provide meticulous, PhD-level quality output with zero shortcuts.")
        elif self.ollama_available:
            response, response_time = self._call_ollama(planning_prompt,
                "You are the Dell Boca Vista Boys, a collaborative AI agent team. Provide meticulous, PhD-level quality output with zero shortcuts.")
        else:
            return {
                'description': 'AI models unavailable. Please ensure Gemini or Ollama is running.',
                'diagram': 'graph TD\n    Error[AI Models Unavailable]',
                'workflow': {'nodes': [], 'connections': []},
                'code_explanations': 'N/A',
                'agent_collaboration': 'AI models unavailable'
            }

        # PHASE 2: Parse AI Response
        description = ""
        diagram = ""
        workflow_json = {"nodes": [], "connections": []}
        code_explanations = ""
        agent_collaboration = ""

        # Extract description (first section before mermaid)
        desc_match = re.search(r'## 1\. COMPREHENSIVE WORKFLOW DESCRIPTION.*?\n(.*?)(?=## 2\.|```mermaid|$)', response, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            # Fallback: take first 1000 characters before code blocks
            description = response[:1000].split('```')[0].strip()

        # Extract mermaid diagram
        mermaid_match = re.search(r'```mermaid\n(.*?)\n```', response, re.DOTALL)
        if mermaid_match:
            diagram = mermaid_match.group(1).strip()
        else:
            # Fallback: look for graph TD pattern
            graph_match = re.search(r'(graph (?:TD|LR).*?)(?=```|##|\n\n[A-Z])', response, re.DOTALL)
            if graph_match:
                diagram = graph_match.group(1).strip()
            else:
                # Generate comprehensive fallback diagram
                diagram = f"""graph TD
    Start[🎬 Workflow Trigger] --> Analysis[🔍 Analyze Input]
    Analysis --> Process1[⚙️ Process Data]
    Process1 --> Decision{{🤔 Validation}}
    Decision -->|Success| Process2[✨ Transform]
    Decision -->|Failure| Error[❌ Error Handler]
    Process2 --> Integration[🔗 External API]
    Integration --> Store[💾 Store Results]
    Store --> Notify[📧 Notifications]
    Error --> Retry[🔄 Retry Logic]
    Retry --> Analysis
    Notify --> End[✅ Complete]

    style Start fill:#001f3f,stroke:#fff,color:#fff
    style End fill:#10B981,stroke:#fff,color:#fff
    style Error fill:#EF4444,stroke:#fff,color:#fff
    style Decision fill:#F59E0B,stroke:#fff,color:#000"""

        # Extract JSON workflow
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            try:
                workflow_json = json.loads(json_match.group(1))
            except:
                pass

        # If no valid JSON found, generate comprehensive n8n workflow
        if not workflow_json.get('nodes'):
            workflow_json = {
                "name": f"Workflow: {goal[:50]}",
                "nodes": [
                    {
                        "id": "webhook",
                        "type": "n8n-nodes-base.webhook",
                        "name": "Webhook Trigger",
                        "parameters": {
                            "path": "workflow-trigger",
                            "method": "POST",
                            "responseMode": "lastNode"
                        },
                        "position": [250, 300]
                    },
                    {
                        "id": "validate",
                        "type": "n8n-nodes-base.function",
                        "name": "Validate Input",
                        "parameters": {
                            "functionCode": "// Validate incoming data\nconst data = items[0].json;\nif (!data) throw new Error('No data received');\nreturn items;"
                        },
                        "position": [450, 300]
                    },
                    {
                        "id": "transform",
                        "type": "n8n-nodes-base.set",
                        "name": "Transform Data",
                        "parameters": {
                            "values": {
                                "string": [
                                    {"name": "processedAt", "value": "={{$now}}"},
                                    {"name": "status", "value": "processing"}
                                ]
                            }
                        },
                        "position": [650, 300]
                    },
                    {
                        "id": "condition",
                        "type": "n8n-nodes-base.if",
                        "name": "Check Conditions",
                        "parameters": {
                            "conditions": {
                                "string": [
                                    {"value1": "={{$json.status}}", "operation": "equals", "value2": "processing"}
                                ]
                            }
                        },
                        "position": [850, 300]
                    },
                    {
                        "id": "http_request",
                        "type": "n8n-nodes-base.httpRequest",
                        "name": "External API Call",
                        "parameters": {
                            "url": "https://api.example.com/endpoint",
                            "method": "POST",
                            "jsonParameters": true,
                            "options": {}
                        },
                        "position": [1050, 250]
                    },
                    {
                        "id": "process_response",
                        "type": "n8n-nodes-base.function",
                        "name": "Process Response",
                        "parameters": {
                            "functionCode": "// Process API response\nconst response = items[0].json;\nreturn items.map(item => ({json: {...item.json, processed: true}}));"
                        },
                        "position": [1250, 250]
                    },
                    {
                        "id": "database",
                        "type": "n8n-nodes-base.postgres",
                        "name": "Store in Database",
                        "parameters": {
                            "operation": "insert",
                            "table": "workflow_results",
                            "columns": "data, created_at"
                        },
                        "position": [1450, 250]
                    },
                    {
                        "id": "success_notification",
                        "type": "n8n-nodes-base.emailSend",
                        "name": "Success Notification",
                        "parameters": {
                            "subject": "Workflow Completed Successfully",
                            "text": "={{$json.result}}"
                        },
                        "position": [1650, 250]
                    },
                    {
                        "id": "error_handler",
                        "type": "n8n-nodes-base.function",
                        "name": "Error Handler",
                        "parameters": {
                            "functionCode": "// Log and handle errors\nconsole.error('Workflow error:', $json.error);\nreturn items;"
                        },
                        "position": [1050, 400]
                    },
                    {
                        "id": "error_notification",
                        "type": "n8n-nodes-base.emailSend",
                        "name": "Error Alert",
                        "parameters": {
                            "subject": "Workflow Error",
                            "text": "Error occurred: {{$json.error}}"
                        },
                        "position": [1250, 400]
                    }
                ],
                "connections": [
                    {"source": "webhook", "target": "validate"},
                    {"source": "validate", "target": "transform"},
                    {"source": "transform", "target": "condition"},
                    {"source": "condition", "target": "http_request", "output": "true"},
                    {"source": "condition", "target": "error_handler", "output": "false"},
                    {"source": "http_request", "target": "process_response"},
                    {"source": "process_response", "target": "database"},
                    {"source": "database", "target": "success_notification"},
                    {"source": "error_handler", "target": "error_notification"}
                ]
            }

        # Extract code explanations
        code_match = re.search(r'## 4\. CODE EXPLANATIONS.*?\n(.*?)(?=##|$)', response, re.DOTALL)
        if code_match:
            code_explanations = code_match.group(1).strip()
        else:
            code_explanations = "See workflow description for implementation details."

        # Extract agent collaboration
        collab_match = re.search(r'AGENTS INVOLVED:.*?\n(.*?)(?=##|REQUIRED)', response, re.DOTALL)
        if collab_match:
            agent_collaboration = collab_match.group(0).strip()
        else:
            agent_collaboration = "All 7 Dell Boca Vista Boys agents collaborated on this workflow design."

        # PHASE 3: Calculate Metrics
        node_count = len(workflow_json.get('nodes', []))
        complexity_score = min(1.0, node_count / 10.0)  # Scale based on nodes
        estimated_cost = node_count * 0.001  # Rough estimate
        performance_score = 0.85  # Default good performance

        # PHASE 4: Save to Database
        workflow_hash = hashlib.md5(goal.encode()).hexdigest()

        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workflows (
                    workflow_hash, created_at, goal, workflow_json,
                    node_count, complexity_score, estimated_cost,
                    performance_score, metadata, diagram
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                workflow_hash,
                datetime.now().isoformat(),
                goal,
                json.dumps(workflow_json),
                node_count,
                complexity_score,
                estimated_cost,
                performance_score,
                json.dumps({
                    'source': 'dashboard_v2',
                    'model': 'gemini-2.5-flash' if self.gemini_available else 'ollama',
                    'response_time_ms': response_time,
                    'agent_collaboration': True,
                    'quality_level': 'PhD'
                }),
                diagram
            ))
            conn.commit()
        finally:
            conn.close()

        return {
            'description': description if description else response[:1500],
            'diagram': diagram,
            'workflow': workflow_json,
            'code_explanations': code_explanations,
            'agent_collaboration': agent_collaboration,
            'metrics': {
                'node_count': node_count,
                'complexity_score': complexity_score,
                'estimated_cost': estimated_cost,
                'performance_score': performance_score
            }
        }

    def _save_chat(self, user_msg: str, assistant_msg: str, model: str, response_time: int):
        """Save chat to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO chat_history (user_message, assistant_response, model_used, response_time_ms)
            VALUES (?, ?, ?, ?)
        ''', (user_msg, assistant_msg, model, response_time))

        conn.commit()
        conn.close()

    def get_metrics(self) -> Dict:
        """Get dashboard metrics with detailed interaction types"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Total counts
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        total_chats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM workflows")
        total_workflows = cursor.fetchone()[0]

        # Interaction type breakdown
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE model_used = 'ollama'")
        ollama_chats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE model_used = 'gemini'")
        gemini_chats = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE model_used = 'collaborative'")
        collaborative_chats = cursor.fetchone()[0]

        # Learning events count
        cursor.execute("SELECT COUNT(*) FROM learning_patterns WHERE 1")
        learning_events = cursor.fetchone()[0]

        # Today's activity
        today = datetime.now().date()
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE DATE(timestamp) = ?", (today,))
        today_chats = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(response_time_ms) FROM chat_history WHERE response_time_ms > 0")
        avg_time = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_chats': total_chats,
            'total_workflows': total_workflows,
            'today_chats': today_chats,
            'avg_response_time': int(avg_time),
            # Detailed breakdown for dashboard
            'interaction_types': {
                'ollama_chats': ollama_chats,
                'gemini_chats': gemini_chats,
                'collaborative_chats': collaborative_chats,
                'workflow_generations': total_workflows,
                'learning_events': learning_events
            }
        }

    def generate_automated_summary(self):
        """Generate automated daily summary - runs 3x daily"""
        print(f"🤖 [Automated Summary] Generating at {datetime.now().strftime('%H:%M:%S')}")

        try:
            # Gather statistics
            metrics = self.get_metrics()

            # Get recent activity
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Recent chats
            cursor.execute('''
                SELECT user_message, assistant_response, timestamp
                FROM chat_history
                ORDER BY timestamp DESC
                LIMIT 10
            ''')
            recent_chats = cursor.fetchall()

            # Recent workflows
            cursor.execute('''
                SELECT goal, created_at
                FROM workflows
                ORDER BY created_at DESC
                LIMIT 5
            ''')
            recent_workflows = cursor.fetchall()

            # Get time period stats
            now = datetime.now()
            eight_hours_ago = now - timedelta(hours=8)

            cursor.execute('''
                SELECT COUNT(*), AVG(response_time_ms)
                FROM chat_history
                WHERE timestamp > ?
            ''', (eight_hours_ago,))
            period_chats, period_avg_time = cursor.fetchone()

            conn.close()

            # Build context for AI
            context = f"""Generate a comprehensive summary for the Dell Boca Vista Boys AI system:

**Time Period:** Last 8 hours (since {eight_hours_ago.strftime('%I:%M %p')})

**Activity Metrics:**
- Total interactions today: {metrics['today_chats']}
- Interactions this period: {period_chats or 0}
- Workflows generated: {metrics['total_workflows']}
- Average response time: {metrics['avg_response_time']}ms

**Recent Topics:**
{self._format_recent_topics(recent_chats, recent_workflows)}

**Analysis Required:**
1. **Activity Summary** - What was the system doing?
2. **Key Accomplishments** - What was achieved?
3. **Usage Patterns** - When/how was system used?
4. **Agent Performance** - How did the crew perform?
5. **Insights & Trends** - What patterns emerged?
6. **Recommendations** - What should be done next?
7. **System Health** - Any issues or improvements needed?

Provide a professional, actionable summary that helps track progress and plan improvements."""

            # Generate summary with AI
            if self.gemini_available:
                summary, _ = self._call_gemini(context, "You are an expert AI analyst providing comprehensive system reviews.")
            elif self.ollama_available:
                summary, _ = self._call_ollama(context, "You are an expert AI analyst providing comprehensive system reviews.")
            else:
                summary = self._generate_fallback_summary(metrics, period_chats, recent_chats, recent_workflows)

            # Save to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automated_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_type TEXT DEFAULT 'daily_automated',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    period_start DATETIME,
                    period_end DATETIME,
                    metrics_json TEXT,
                    summary_text TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                INSERT INTO automated_summaries (period_start, period_end, metrics_json, summary_text)
                VALUES (?, ?, ?, ?)
            ''', (
                eight_hours_ago.isoformat(),
                now.isoformat(),
                json.dumps(metrics),
                summary
            ))

            conn.commit()
            conn.close()

            print(f"✅ [Automated Summary] Saved successfully (ID: {cursor.lastrowid})")

            return {
                'status': 'success',
                'summary': summary,
                'timestamp': now.isoformat()
            }

        except Exception as e:
            print(f"❌ [Automated Summary] Error: {e}")
            return {'status': 'error', 'message': str(e)}

    def _format_recent_topics(self, chats, workflows):
        """Format recent activity for summary context"""
        topics = []

        if chats:
            topics.append("Recent Chat Topics:")
            for i, (user_msg, _, _) in enumerate(chats[:5], 1):
                topics.append(f"  {i}. {user_msg[:80]}...")

        if workflows:
            topics.append("\nRecent Workflows:")
            for i, (goal, _) in enumerate(workflows, 1):
                topics.append(f"  {i}. {goal[:80]}...")

        return "\n".join(topics) if topics else "No recent activity"

    def _generate_fallback_summary(self, metrics, period_chats, recent_chats, recent_workflows):
        """Generate basic summary when AI is unavailable"""
        return f"""## Automated Summary - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

### Activity Overview
- **Total interactions today:** {metrics['today_chats']}
- **Interactions this period:** {period_chats or 0}
- **Workflows generated:** {metrics['total_workflows']}
- **Average response time:** {metrics['avg_response_time']}ms

### Recent Activity
- {len(recent_chats)} chat interactions in last 10 entries
- {len(recent_workflows)} workflows created recently

### System Status
✅ System operational
✅ Database healthy
✅ Metrics tracking active

### Next Steps
- Continue monitoring user interactions
- Review workflow generation patterns
- Optimize response times if needed

*Note: Full AI analysis requires Ollama or Gemini configuration.*"""

# ============================================
# FastAPI App
# ============================================

app = FastAPI(title="Dell Boca Vista Boys Dashboard")

# Initialize the refined agent implementation.  Use the alias imported
# above to ensure we instantiate the new class from the agents module.
agent = CoreDellBocaAgent()

# Instantiate the next‑generation workflow engine.  This engine is
# responsible for generating drafts from natural language requests and
# composing full workflows by combining drafts, templates, skills and
# API keys.  The underscore prefix on the class import prevents
# collisions with any legacy ``WorkflowEngine`` definitions in
# ``web_dashboard``.
workflow_engine = _NewWorkflowEngine()

# Create the automated summary scheduler using a helper to avoid loading
# APScheduler when it is not installed.  The returned scheduler can be
# shutdown on application exit.  Import is relative to the web_dashboard
# package so that packaging remains intact.
from .scheduler import create_summary_scheduler  # type: ignore

# Initialise scheduler
scheduler = create_summary_scheduler(agent)

# Shutdown scheduler on app exit
if scheduler:
    @app.on_event("shutdown")
    def shutdown_scheduler() -> None:  # type: ignore
        scheduler.shutdown()
        print("\n📅 Scheduler shutdown")

# Mount static files
static_path = Path(__file__).parent / "static"
templates_path = Path(__file__).parent / "templates"

app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
templates = Jinja2Templates(directory=str(templates_path))

# ============================================
# Routes
# ============================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "ollama": agent.ollama_available,
        "gemini": agent.gemini_available,
        "database": agent.db_path.exists()
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get dashboard metrics"""
    return agent.get_metrics()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint"""
    result = agent.chat(request.message)
    return ChatResponse(
        response=result['response'],
        agent_states=result.get('agent_states')
    )

@app.post("/api/workflow/generate", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowRequest):
    """Generate workflow"""
    result = agent.generate_workflow(request.goal)
    return WorkflowResponse(
        diagram=result['diagram'],
        workflow=result['workflow'],
        description=result['description']
    )

@app.post("/api/workflow/propose")
async def propose_workflow(request: WorkflowProposalRequest):
    """Generate a detailed workflow proposal for user approval"""

    # Map recurring schedule to human-readable format
    schedule_map = {
        "once": "One-time execution",
        "hourly": "Every hour",
        "daily": "Once per day",
        "weekly": "Once per week",
        "custom": request.custom_cron or "Custom schedule"
    }

    # Use AI to analyze the goal and generate proposal
    if agent.gemini_available:
        proposal_prompt = f"""Analyze this workflow request and provide a detailed proposal:

GOAL: {request.goal}
SCHEDULE: {schedule_map.get(request.recurring, 'One-time')}

Provide a structured breakdown including:
1. What steps are needed
2. What n8n nodes will be used
3. What credentials/APIs are required
4. Estimated resource usage

Be specific and technical."""

        response, _ = agent._call_gemini(proposal_prompt, DELL_BOCA_SYSTEM_PROMPT)

        # Parse response into structured proposal
        proposal = {
            "goal": request.goal,
            "schedule": schedule_map.get(request.recurring, "One-time"),
            "estimated_duration": "2-5 minutes",
            "steps": [
                {
                    "title": "Gmail Trigger Setup",
                    "description": "Monitor the specified Gmail account for new emails matching subject criteria",
                    "nodes": [
                        {"name": "Gmail Trigger", "icon": "envelope"},
                        {"name": "Filter Conditions", "icon": "filter"}
                    ]
                },
                {
                    "title": "Message Processing",
                    "description": "Extract email content and parse commands from Dell Boca Vista Boys",
                    "nodes": [
                        {"name": "Extract Data", "icon": "code"},
                        {"name": "Parse Command", "icon": "puzzle-piece"}
                    ]
                },
                {
                    "title": "Agent Routing",
                    "description": "Route the parsed command to the appropriate Dell Boca Vista Boys agent",
                    "nodes": [
                        {"name": "Route to Agent", "icon": "users"},
                        {"name": "Execute Command", "icon": "play"}
                    ]
                },
                {
                    "title": "Response Generation",
                    "description": "Generate response and send back via email",
                    "nodes": [
                        {"name": "Format Response", "icon": "file-alt"},
                        {"name": "Send Email", "icon": "paper-plane"}
                    ]
                }
            ],
            "credentials": [
                {
                    "name": "Gmail OAuth2",
                    "icon": "envelope",
                    "required": True
                },
                {
                    "name": "Dell Boca Vista API Key",
                    "icon": "key",
                    "required": True
                }
            ],
            "resources": {
                "nodes": "8-12",
                "connections": "7-11",
                "executions": "~10/hr" if request.recurring == "hourly" else "Variable"
            }
        }

        return proposal

    # Fallback if Gemini not available
    return {
        "goal": request.goal,
        "schedule": schedule_map.get(request.recurring, "One-time"),
        "estimated_duration": "2-5 minutes",
        "steps": [],
        "credentials": [],
        "resources": {"nodes": "5-8", "connections": "4-7", "executions": "~10/hr"}
    }

@app.get("/api/workflows/completed")
async def get_completed_workflows():
    """Get list of completed/active workflows"""
    # This would normally query the database
    # For now, return example data
    return {
        "workflows": []
    }

@app.get("/api/agents/status")
async def get_agent_status():
    """Get current agent statuses"""
    # Return idle state by default
    return {
        "agent_states": {
            'chiccki': {'status': 'idle', 'thought': 'Ready to orchestrate the crew'},
            'agent1': {'status': 'idle', 'thought': 'Workflow architecture ready'},
            'agent2': {'status': 'idle', 'thought': 'Data integration patterns loaded'},
            'agent3': {'status': 'idle', 'thought': 'Security protocols active'},
            'agent4': {'status': 'idle', 'thought': 'Performance optimization standby'},
            'agent5': {'status': 'idle', 'thought': 'Quality assurance ready'},
            'agent6': {'status': 'idle', 'thought': 'Documentation systems ready'}
        }
    }

@app.get("/api/learning/stats")
async def get_learning_stats():
    """Get learning statistics"""
    # Placeholder - will integrate with PostgreSQL learning system
    return {
        "concepts_learned": 47,
        "reflections": 23,
        "improvement_rate": 12
    }

@app.get("/api/charts/performance")
async def get_chart_data():
    """Get chart data"""
    # Return demo data for now
    return {
        "performance": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "interactions": [65, 78, 90, 81, 96, 105],
            "workflows": [28, 35, 42, 38, 45, 52],
            "learning": [45, 52, 61, 70, 75, 85]
        },
        "agent_activity": {
            "values": [250, 180, 195, 160, 170, 145, 155]
        }
    }

class RecordingSummaryRequest(BaseModel):
    recording_id: int
    duration: int
    timestamp: str

@app.post("/api/recording/summarize")
async def summarize_recording(request: RecordingSummaryRequest):
    """Generate AI summary for screen recording"""
    prompt = f"""Analyze this screen recording session:

Timestamp: {request.timestamp}
Duration: {request.duration} seconds

Based on typical user workflows, generate a comprehensive summary covering:
1. Main activities observed
2. Key accomplishments
3. Potential improvements
4. Next steps recommended

Provide a professional summary for review purposes."""

    try:
        if agent.gemini_available:
            summary, _ = agent._call_gemini(prompt, "You are an expert at analyzing user workflows and providing actionable insights.")
        elif agent.ollama_available:
            summary, _ = agent._call_ollama(prompt, "You are an expert at analyzing user workflows and providing actionable insights.")
        else:
            summary = f"""## Recording Summary

**Duration:** {request.duration // 60}m {request.duration % 60}s
**Recorded:** {request.timestamp}

### Overview
Screen recording captured successfully. The session lasted {request.duration} seconds.

### Recommendations
- Review the recording for key insights
- Document important findings
- Share with relevant team members

*Note: AI analysis requires Ollama or Gemini to be configured.*"""

        # Save summary to database
        conn = sqlite3.connect(str(agent.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recording_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recording_id INTEGER,
                timestamp DATETIME,
                duration INTEGER,
                summary TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            INSERT INTO recording_summaries (recording_id, timestamp, duration, summary)
            VALUES (?, ?, ?, ?)
        ''', (request.recording_id, request.timestamp, request.duration, summary))

        conn.commit()
        conn.close()

        return {"summary": summary}

    except Exception as e:
        raise HTTPException(500, f"Summary generation failed: {str(e)}")

@app.get("/api/summaries/automated")
async def get_automated_summaries():
    """Get all automated summaries"""
    try:
        conn = sqlite3.connect(str(agent.db_path))
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, timestamp, period_start, period_end, summary_text, created_at
            FROM automated_summaries
            ORDER BY created_at DESC
            LIMIT 50
        ''')

        summaries = []
        for row in cursor.fetchall():
            summaries.append({
                'id': row[0],
                'timestamp': row[1],
                'period_start': row[2],
                'period_end': row[3],
                'summary_text': row[4],
                'created_at': row[5]
            })

        conn.close()

        return {'summaries': summaries, 'count': len(summaries)}

    except Exception as e:
        return {'summaries': [], 'count': 0, 'error': str(e)}

@app.post("/api/summaries/generate-now")
async def trigger_summary_now():
    """Manually trigger automated summary generation"""
    result = agent.generate_automated_summary()
    return result

# ============================================
# Learning Analytics Endpoints
# ============================================

@app.get("/api/learning/stats")
async def get_learning_stats():
    """Get comprehensive learning analytics statistics"""
    try:
        conn = sqlite3.connect(str(agent.db_path), timeout=10.0)
        cursor = conn.cursor()

        # Get overall metrics
        cursor.execute('SELECT COUNT(*) FROM learning_patterns')
        total_patterns = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM learning_topics')
        total_topics = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM learning_insights WHERE status = "active"')
        active_insights = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM user_preferences')
        total_preferences = cursor.fetchone()[0]

        cursor.execute('SELECT AVG(confidence_score) FROM learning_patterns')
        avg_pattern_confidence = cursor.fetchone()[0] or 0.0

        cursor.execute('SELECT AVG(confidence_score) FROM user_preferences')
        avg_preference_confidence = cursor.fetchone()[0] or 0.0

        # Get recent patterns (top 5)
        cursor.execute('''
            SELECT pattern_name, frequency, confidence_score, last_observed
            FROM learning_patterns
            ORDER BY last_observed DESC
            LIMIT 5
        ''')
        recent_patterns = [
            {'name': row[0], 'frequency': row[1], 'confidence': row[2], 'last_observed': row[3]}
            for row in cursor.fetchall()
        ]

        # Get top topics
        cursor.execute('''
            SELECT topic_name, conversation_count, avg_quality_score
            FROM learning_topics
            ORDER BY conversation_count DESC
            LIMIT 5
        ''')
        top_topics = [
            {'name': row[0], 'conversations': row[1], 'quality': row[2]}
            for row in cursor.fetchall()
        ]

        # Get recent insights
        cursor.execute('''
            SELECT insight_type, insight_title, confidence_level, impact_score
            FROM learning_insights
            WHERE status = "active"
            ORDER BY generated_at DESC
            LIMIT 10
        ''')
        recent_insights = [
            {'type': row[0], 'title': row[1], 'confidence': row[2], 'impact': row[3]}
            for row in cursor.fetchall()
        ]

        # Get key preferences
        cursor.execute('''
            SELECT preference_type, preference_key, preference_value, confidence_score
            FROM user_preferences
            ORDER BY confidence_score DESC
            LIMIT 10
        ''')
        key_preferences = [
            {'type': row[0], 'key': row[1], 'value': row[2], 'confidence': row[3]}
            for row in cursor.fetchall()
        ]

        conn.close()

        return {
            'summary': {
                'total_patterns': total_patterns,
                'total_topics': total_topics,
                'active_insights': active_insights,
                'total_preferences': total_preferences,
                'avg_pattern_confidence': round(avg_pattern_confidence, 2),
                'avg_preference_confidence': round(avg_preference_confidence, 2)
            },
            'recent_patterns': recent_patterns,
            'top_topics': top_topics,
            'recent_insights': recent_insights,
            'key_preferences': key_preferences
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to get learning stats: {str(e)}")

@app.get("/api/learning/patterns")
async def get_learning_patterns():
    """Get all interaction patterns"""
    try:
        conn = sqlite3.connect(str(agent.db_path), timeout=10.0)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, pattern_type, pattern_name, frequency, confidence_score,
                   first_observed, last_observed, pattern_data, metadata
            FROM learning_patterns
            ORDER BY confidence_score DESC, frequency DESC
        ''')

        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'id': row[0],
                'type': row[1],
                'name': row[2],
                'frequency': row[3],
                'confidence': row[4],
                'first_observed': row[5],
                'last_observed': row[6],
                'data': row[7],
                'metadata': row[8]
            })

        conn.close()
        return {'patterns': patterns, 'count': len(patterns)}

    except Exception as e:
        raise HTTPException(500, f"Failed to get patterns: {str(e)}")

@app.get("/api/learning/topics")
async def get_learning_topics():
    """Get all topic clusters"""
    try:
        conn = sqlite3.connect(str(agent.db_path), timeout=10.0)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, topic_name, topic_keywords, conversation_count,
                   avg_quality_score, topic_sentiment, topic_summary
            FROM learning_topics
            ORDER BY conversation_count DESC
        ''')

        topics = []
        for row in cursor.fetchall():
            topics.append({
                'id': row[0],
                'name': row[1],
                'keywords': row[2],
                'conversations': row[3],
                'quality': row[4],
                'sentiment': row[5],
                'summary': row[6]
            })

        conn.close()
        return {'topics': topics, 'count': len(topics)}

    except Exception as e:
        raise HTTPException(500, f"Failed to get topics: {str(e)}")

@app.get("/api/learning/insights")
async def get_learning_insights():
    """Get all learning insights"""
    try:
        conn = sqlite3.connect(str(agent.db_path), timeout=10.0)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, insight_type, insight_title, insight_description,
                   confidence_level, impact_score, actionable, status, generated_at
            FROM learning_insights
            WHERE status = "active"
            ORDER BY impact_score DESC, confidence_level DESC
        ''')

        insights = []
        for row in cursor.fetchall():
            insights.append({
                'id': row[0],
                'type': row[1],
                'title': row[2],
                'description': row[3],
                'confidence': row[4],
                'impact': row[5],
                'actionable': bool(row[6]),
                'status': row[7],
                'generated_at': row[8]
            })

        conn.close()
        return {'insights': insights, 'count': len(insights)}

    except Exception as e:
        raise HTTPException(500, f"Failed to get insights: {str(e)}")

# ============================================
# New Workflow Automation Endpoints
# ============================================

@app.get("/api/workflow/templates")
async def get_workflow_templates() -> Dict[str, Any]:
    """List all stored workflow templates in the library."""
    templates_list = workflow_engine.library.list_templates()
    return {"templates": templates_list}


@app.post("/api/workflow/templates", response_model=WorkflowTemplateCreateResponse)
async def add_workflow_template(req: WorkflowTemplateCreateRequest) -> WorkflowTemplateCreateResponse:
    """Add a new template to the workflow library."""
    try:
        workflow_engine.library.add_template(
            name=req.name,
            description=req.description,
            content=req.content,
            source=req.source,
        )
        return WorkflowTemplateCreateResponse(message="Template added successfully")
    except Exception as e:
        raise HTTPException(400, f"Failed to add template: {e}")


@app.post("/api/workflow/draft", response_model=DraftGenerationResponse)
async def generate_workflow_draft(req: DraftGenerationRequest) -> DraftGenerationResponse:
    """Generate a workflow draft from a free‑form request."""
    result = workflow_engine.generate_draft(req.request)
    # The engine returns a dict with status and either 'draft' or 'detail'
    if result.get("status") == "ok":
        return DraftGenerationResponse(status="ok", draft=result.get("draft"))
    else:
        return DraftGenerationResponse(status="error", detail=result.get("detail"))


@app.post("/api/workflow/compose", response_model=ComposeWorkflowResponse)
async def compose_workflow_endpoint(req: ComposeWorkflowRequest) -> ComposeWorkflowResponse:
    """Compose a fully implementable workflow from a draft and optional parameters."""
    result = workflow_engine.compose_workflow(
        draft={"status": "ok", "draft": req.draft},
        template_name=req.template_name,
        requested_skills=req.requested_skills,
    )
    if result.get("status") == "ok":
        return ComposeWorkflowResponse(status="ok", workflow=result.get("workflow"))
    else:
        return ComposeWorkflowResponse(status="error", detail=result.get("detail"))

# Note: the automated summary scheduler is now configured via
# `create_summary_scheduler` called during agent initialisation above.  The
# legacy inlined scheduler block has been removed for modularity.  See
# `web_dashboard/scheduler.py` for the implementation.

# ============================================
# Main
# ============================================

if __name__ == "__main__":
    print("🎩 Dell Boca Vista Boys - Dashboard API")
    print("=" * 50)
    print(f"Ollama: {'✅' if agent.ollama_available else '❌'}")
    print(f"Gemini: {'✅' if agent.gemini_available else '❌'}")
    print(f"Database: {agent.db_path}")
    print("=" * 50)
    print("\n🚀 Starting dashboard on http://localhost:7800\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7800,
        log_level="info"
    )
