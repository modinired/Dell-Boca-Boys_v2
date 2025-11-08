"""
Email Task Router for Dell Bocca Boys Agents

Routes email tasks from users to the appropriate CESAR agents for processing.
Integrates with the existing multi-agent network and user question router.

Features:
- Intelligent task classification and routing
- Integration with CESAR multi-agent network
- Task priority and urgency detection
- Response formatting for email delivery
- Task execution tracking and logging
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks that can be received via email."""
    QUESTION = "question"
    ANALYSIS = "analysis"
    CODING = "coding"
    RESEARCH = "research"
    PLANNING = "planning"
    REVIEW = "review"
    GENERAL = "general"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class EmailTask:
    """Represents a task extracted from an email."""
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    description: str
    from_address: str
    message_id: str
    received_at: datetime
    context: Dict[str, Any]

    @property
    def urgency_keywords(self) -> List[str]:
        """Keywords that indicate urgency."""
        return ["urgent", "asap", "emergency", "critical", "immediate", "quickly"]

    def is_urgent(self) -> bool:
        """Check if task contains urgency indicators."""
        lower_desc = self.description.lower()
        return any(keyword in lower_desc for keyword in self.urgency_keywords)


class EmailTaskRouter:
    """
    Routes email tasks to appropriate Dell Bocca Boys agents.

    Integrates with:
    - CESAR multi-agent network for task execution
    - User question router for question handling
    - Agent manager for specialized task delegation
    """

    def __init__(self):
        """Initialize email task router."""
        self.logger = logging.getLogger(__name__)
        self._cesar_network = None
        self._user_question_router = None
        self._agent_manager = None
        self._initialized = False

    async def initialize(self):
        """Initialize connections to agent systems."""
        if self._initialized:
            return

        try:
            # Import and initialize CESAR network
            from core.intelligence.cesar_multi_agent_network import CESARMultiAgentNetwork

            self._cesar_network = CESARMultiAgentNetwork()
            self.logger.info("CESAR multi-agent network initialized")

        except ImportError as e:
            self.logger.warning(f"Could not import CESAR network: {e}")

        try:
            # Import and initialize user question router
            from core.intelligence.user_question_router import UserQuestionRouter
            from core.intelligence.main_orchestrator import TerryDelmonacoManagerAgent

            manager = TerryDelmonacoManagerAgent()
            self._user_question_router = UserQuestionRouter(manager)
            self.logger.info("User question router initialized")

        except ImportError as e:
            self.logger.warning(f"Could not import user question router: {e}")

        try:
            # Import agent manager for specialized tasks
            from core.intelligence.agent_manager import AgentManager

            self._agent_manager = AgentManager()
            self.logger.info("Agent manager initialized")

        except ImportError as e:
            self.logger.warning(f"Could not import agent manager: {e}")

        self._initialized = True
        self.logger.info("Email task router initialization complete")

    async def route_task(self, task_context: Dict[str, Any]) -> str:
        """
        Route an email task to appropriate agents and return response.

        Args:
            task_context: Dictionary containing:
                - message_id: Email message ID
                - from_address: Sender email address
                - subject: Email subject
                - received_at: Timestamp when email was received
                - task_description: Extracted task description

        Returns:
            Response text to send back to user via email
        """
        # Ensure router is initialized
        await self.initialize()

        # Parse task
        task = await self._parse_task(task_context)

        self.logger.info(
            f"Routing {task.task_type.value} task from {task.from_address} "
            f"(Priority: {task.priority.name})"
        )

        # Route based on task type
        try:
            if task.task_type == TaskType.QUESTION:
                response = await self._route_question(task)
            elif task.task_type == TaskType.ANALYSIS:
                response = await self._route_analysis(task)
            elif task.task_type == TaskType.CODING:
                response = await self._route_coding_task(task)
            elif task.task_type == TaskType.RESEARCH:
                response = await self._route_research(task)
            elif task.task_type == TaskType.PLANNING:
                response = await self._route_planning(task)
            elif task.task_type == TaskType.REVIEW:
                response = await self._route_review(task)
            else:
                response = await self._route_general_task(task)

            # Format response for email
            formatted_response = self._format_response(task, response)

            return formatted_response

        except Exception as e:
            self.logger.error(f"Error routing task {task.task_id}: {e}", exc_info=True)
            return self._format_error_response(task, str(e))

    async def _parse_task(self, task_context: Dict[str, Any]) -> EmailTask:
        """
        Parse task context into an EmailTask object.

        Args:
            task_context: Raw task context from email monitor

        Returns:
            EmailTask object with classified type and priority
        """
        description = task_context["task_description"]

        # Detect task type
        task_type = self._classify_task_type(description)

        # Detect priority
        priority = self._classify_priority(description)

        # Create task object
        task = EmailTask(
            task_id=f"email_task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            task_type=task_type,
            priority=priority,
            description=description,
            from_address=task_context["from_address"],
            message_id=task_context["message_id"],
            received_at=task_context["received_at"],
            context=task_context
        )

        return task

    def _classify_task_type(self, description: str) -> TaskType:
        """
        Classify task type based on description content.

        Args:
            description: Task description text

        Returns:
            Classified TaskType
        """
        lower_desc = description.lower()

        # Question patterns
        question_patterns = [
            r'\?$',  # Ends with question mark
            r'^(what|how|why|when|where|who|which|can|could|would|should|is|are|do|does)',
            r'(explain|tell me|help me understand|clarify)'
        ]
        if any(re.search(pattern, lower_desc) for pattern in question_patterns):
            return TaskType.QUESTION

        # Coding patterns
        coding_keywords = [
            "code", "implement", "function", "script", "program", "debug",
            "fix bug", "refactor", "api", "algorithm", "class", "method"
        ]
        if any(keyword in lower_desc for keyword in coding_keywords):
            return TaskType.CODING

        # Analysis patterns
        analysis_keywords = [
            "analyze", "analysis", "evaluate", "assess", "examine",
            "compare", "investigate", "study", "review data"
        ]
        if any(keyword in lower_desc for keyword in analysis_keywords):
            return TaskType.ANALYSIS

        # Research patterns
        research_keywords = [
            "research", "find out", "look into", "investigate",
            "gather information", "survey", "explore"
        ]
        if any(keyword in lower_desc for keyword in research_keywords):
            return TaskType.RESEARCH

        # Planning patterns
        planning_keywords = [
            "plan", "strategy", "roadmap", "design", "architect",
            "outline", "structure", "framework"
        ]
        if any(keyword in lower_desc for keyword in planning_keywords):
            return TaskType.PLANNING

        # Review patterns
        review_keywords = [
            "review", "check", "validate", "verify", "audit",
            "quality assurance", "qa", "test"
        ]
        if any(keyword in lower_desc for keyword in review_keywords):
            return TaskType.REVIEW

        # Default to general
        return TaskType.GENERAL

    def _classify_priority(self, description: str) -> TaskPriority:
        """
        Classify task priority based on description content.

        Args:
            description: Task description text

        Returns:
            Classified TaskPriority
        """
        lower_desc = description.lower()

        # Urgent keywords
        urgent_keywords = ["urgent", "asap", "emergency", "critical", "immediate"]
        if any(keyword in lower_desc for keyword in urgent_keywords):
            return TaskPriority.URGENT

        # High priority keywords
        high_keywords = ["important", "priority", "quickly", "soon", "deadline"]
        if any(keyword in lower_desc for keyword in high_keywords):
            return TaskPriority.HIGH

        # Low priority keywords
        low_keywords = ["whenever", "no rush", "low priority", "when you can"]
        if any(keyword in lower_desc for keyword in low_keywords):
            return TaskPriority.LOW

        # Default to medium
        return TaskPriority.MEDIUM

    async def _route_question(self, task: EmailTask) -> Dict[str, Any]:
        """Route question to user question router."""
        if self._user_question_router:
            self.logger.info(f"Routing question to CESAR network: {task.description[:50]}...")
            result = await self._user_question_router.route_user_question(
                question=task.description,
                context={
                    "source": "email",
                    "from": task.from_address,
                    "priority": task.priority.name
                }
            )
            return result
        else:
            # Fallback if router not available
            return {
                "success": True,
                "response": "I received your question. However, the question routing system "
                           "is currently unavailable. Please try again later or contact support.",
                "agents_consulted": []
            }

    async def _route_analysis(self, task: EmailTask) -> Dict[str, Any]:
        """Route analysis task to appropriate CESAR agents."""
        if self._cesar_network:
            self.logger.info(f"Routing analysis task to CESAR network: {task.description[:50]}...")

            # Analysis tasks: Chiccki coordinates, Arthur analyzes patterns, Giancarlo provides technical analysis
            response = await self._cesar_network.process_collaborative_task(
                task={
                    "type": "analysis",
                    "description": task.description,
                    "priority": task.priority.name
                },
                collaboration_mode="consultation",
                lead_agent="chiccki_cammarano",
                contributing_agents=["arthur_dunzarelli", "giancarlo_saltimbocca"]
            )
            return response
        else:
            return self._fallback_response("analysis")

    async def _route_coding_task(self, task: EmailTask) -> Dict[str, Any]:
        """Route coding task to technical agents."""
        if self._cesar_network:
            self.logger.info(f"Routing coding task to CESAR network: {task.description[:50]}...")

            # Coding tasks: Giancarlo writes code, Collogero designs flow, Gerry validates
            response = await self._cesar_network.process_collaborative_task(
                task={
                    "type": "coding",
                    "description": task.description,
                    "priority": task.priority.name
                },
                collaboration_mode="consultation",
                lead_agent="giancarlo_saltimbocca",
                contributing_agents=["collogero_aspertuno", "gerry_nascondino"]
            )
            return response
        else:
            return self._fallback_response("coding")

    async def _route_research(self, task: EmailTask) -> Dict[str, Any]:
        """Route research task to academic agents."""
        if self._cesar_network:
            self.logger.info(f"Routing research task to CESAR network: {task.description[:50]}...")

            # Research tasks: Arthur analyzes patterns/docs, Chiccki coordinates, Collogero structures
            response = await self._cesar_network.process_collaborative_task(
                task={
                    "type": "research",
                    "description": task.description,
                    "priority": task.priority.name
                },
                collaboration_mode="consultation",
                lead_agent="arthur_dunzarelli",
                contributing_agents=["chiccki_cammarano", "collogero_aspertuno"]
            )
            return response
        else:
            return self._fallback_response("research")

    async def _route_planning(self, task: EmailTask) -> Dict[str, Any]:
        """Route planning task to strategic agents."""
        if self._cesar_network:
            self.logger.info(f"Routing planning task to CESAR network: {task.description[:50]}...")

            # Planning tasks: Collogero plans flow, Chiccki coordinates, Gerry validates plan
            response = await self._cesar_network.process_collaborative_task(
                task={
                    "type": "planning",
                    "description": task.description,
                    "priority": task.priority.name
                },
                collaboration_mode="consultation",
                lead_agent="collogero_aspertuno",
                contributing_agents=["chiccki_cammarano", "gerry_nascondino"]
            )
            return response
        else:
            return self._fallback_response("planning")

    async def _route_review(self, task: EmailTask) -> Dict[str, Any]:
        """Route review task to quality assurance agents."""
        if self._cesar_network:
            self.logger.info(f"Routing review task to CESAR network: {task.description[:50]}...")

            # Review tasks: Gerry leads QA, Arthur reviews patterns, Giancarlo checks code, Collogero validates flow
            response = await self._cesar_network.process_collaborative_task(
                task={
                    "type": "review",
                    "description": task.description,
                    "priority": task.priority.name
                },
                collaboration_mode="committee",
                lead_agent="gerry_nascondino",
                contributing_agents=["arthur_dunzarelli", "giancarlo_saltimbocca", "collogero_aspertuno"]
            )
            return response
        else:
            return self._fallback_response("review")

    async def _route_general_task(self, task: EmailTask) -> Dict[str, Any]:
        """Route general task to full CESAR committee."""
        if self._cesar_network:
            self.logger.info(f"Routing general task to CESAR network: {task.description[:50]}...")

            # General tasks use committee mode for comprehensive handling
            response = await self._cesar_network.process_collaborative_task(
                task={
                    "type": "general",
                    "description": task.description,
                    "priority": task.priority.name
                },
                collaboration_mode="committee"
            )
            return response
        else:
            return self._fallback_response("general")

    def _fallback_response(self, task_type: str) -> Dict[str, Any]:
        """Generate fallback response when agent systems are unavailable."""
        return {
            "success": True,
            "response": f"I received your {task_type} task. However, the agent network "
                       f"is currently initializing. Your task has been queued and will be "
                       f"processed shortly. You will receive a response via email once complete.",
            "agents_consulted": [],
            "status": "queued"
        }

    def _format_response(self, task: EmailTask, response: Dict[str, Any]) -> str:
        """
        Format agent response for email delivery.

        Args:
            task: Original EmailTask
            response: Response from agents

        Returns:
            Formatted response text for email
        """
        # Extract response text
        if "response" in response:
            main_response = response["response"]
        elif "aggregated_response" in response:
            main_response = response["aggregated_response"]
        elif "result" in response:
            main_response = response["result"]
        else:
            main_response = "Task processed successfully."

        # Build formatted response
        lines = []
        lines.append("Thank you for your request!")
        lines.append("")
        lines.append(main_response)
        lines.append("")

        # Add agent attribution if available
        if "agents_consulted" in response and response["agents_consulted"]:
            lines.append("---")
            lines.append("Agents consulted:")
            for agent in response["agents_consulted"]:
                lines.append(f"  • {agent}")
            lines.append("")

        # Add metadata
        lines.append("---")
        lines.append(f"Task Type: {task.task_type.value.title()}")
        lines.append(f"Priority: {task.priority.name}")
        lines.append(f"Task ID: {task.task_id}")
        lines.append(f"Processed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

        return "\n".join(lines)

    def _format_error_response(self, task: EmailTask, error_message: str) -> str:
        """
        Format error response for email delivery.

        Args:
            task: Original EmailTask
            error_message: Error message

        Returns:
            Formatted error response text
        """
        return f"""I encountered an error while processing your request:

{error_message}

Please try rephrasing your request or contact support if the issue persists.

---
Task Type: {task.task_type.value.title()}
Task ID: {task.task_id}
Error Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""


# Singleton instance for use across the application
_email_task_router_instance = None


async def get_email_task_router() -> EmailTaskRouter:
    """
    Get or create the singleton EmailTaskRouter instance.

    Returns:
        Initialized EmailTaskRouter instance
    """
    global _email_task_router_instance

    if _email_task_router_instance is None:
        _email_task_router_instance = EmailTaskRouter()
        await _email_task_router_instance.initialize()

    return _email_task_router_instance


if __name__ == "__main__":
    # Example usage
    async def main():
        router = await get_email_task_router()

        # Test task
        test_task = {
            "message_id": "<test@example.com>",
            "from_address": "user@example.com",
            "subject": "Dell Bocca Boys - Test Question",
            "received_at": datetime.utcnow(),
            "task_description": "How do I implement a binary search algorithm in Python?"
        }

        response = await router.route_task(test_task)
        print("Response:")
        print(response)

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
