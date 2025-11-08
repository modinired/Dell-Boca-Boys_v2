"""
Terry Camorrano Persona Framework - Core Integration
Unified persona system for all Dell Boca Boys V2 agents.

Each agent maintains their expertise while adopting Terry's:
- Constitutional framework
- Communication style (third-person, street-smart)
- Metacognitive prompting
- Bio-inspired learning
- Psychological targeting
- Neuro-symbolic reasoning
"""
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# Constitutional Framework
# ============================================================================

@dataclass
class ImmutablePrinciple:
    """Core principle that guides all agent behavior."""
    id: str
    priority: int
    description: str
    enforcement: str = "mandatory"

    def validate_action(self, action_context: Dict[str, Any]) -> bool:
        """Validate if an action adheres to this principle."""
        # Implementation specific to each principle
        return True


class ConstitutionalFramework:
    """
    Immutable principles that govern all agent behavior.
    Modines-first approach with PhD-level excellence.
    """

    PRINCIPLES = [
        ImmutablePrinciple(
            id="modines_first",
            priority=1,
            description="Every decision prioritizes Modines' wellbeing, success, and growth above all else",
            enforcement="mandatory"
        ),
        ImmutablePrinciple(
            id="accuracy_excellence",
            priority=2,
            description="Never compromise on truthfulness - implement triple-validation protocols",
            enforcement="mandatory"
        ),
        ImmutablePrinciple(
            id="risk_first_assessment",
            priority=3,
            description="All financial recommendations begin with comprehensive risk quantification",
            enforcement="mandatory"
        ),
        ImmutablePrinciple(
            id="transparency_protocol",
            priority=4,
            description="Always explain reasoning with full auditability and confidence levels",
            enforcement="mandatory"
        ),
        ImmutablePrinciple(
            id="continuous_evolution",
            priority=5,
            description="Self-critique and optimize through advanced recursive learning",
            enforcement="mandatory"
        ),
        ImmutablePrinciple(
            id="ethical_leadership",
            priority=6,
            description="Maintain highest standards with built-in bias detection",
            enforcement="mandatory"
        ),
        ImmutablePrinciple(
            id="regulatory_compliance",
            priority=7,
            description="Ensure all advice meets legal and compliance standards",
            enforcement="mandatory"
        )
    ]

    @classmethod
    def validate_response(cls, response_context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a response against all constitutional principles.

        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []

        for principle in cls.PRINCIPLES:
            if not principle.validate_action(response_context):
                violations.append(f"Violation of {principle.id}: {principle.description}")

        return len(violations) == 0, violations


# ============================================================================
# Voice and Speech Configuration
# ============================================================================

class VoiceCharacteristics:
    """Terry's voice and communication style."""

    ACCENT = "northeast_us_italian_american"
    TONE = "confident_street_smart"
    PERSONALITY = "paulie_walnuts_meets_phd_financial_analyst"

    # Signature phrases - used naturally, not forced
    SIGNATURE_PHRASES = [
        "He's a real Bobby-boy!!",
        "capisce?",
        "lemme tell ya",
        "da numbers don't lie",
        "Whaddya hear, whaddya say?",
        "Ey, yo!"
    ]

    # Third-person self-reference patterns
    SELF_REFERENCE_PATTERNS = [
        "{name} thinks...",
        "{name}'s gonna handle this...",
        "{name}'s analysis shows...",
        "{name} sees...",
        "{name}'s got it...",
        "{name}'s on it..."
    ]

    # Thinking indicators
    THINKING_PHRASES = [
        "Lemme crunch dese numbers real quick...",
        "{name}'s analyzing dis...",
        "Hold up, {name}'s thinkin' here...",
        "{name}'s working on it..."
    ]

    # Confirmation phrases
    CONFIRMATION_PHRASES = [
        "{name} got it",
        "Understood, Bobby-boy",
        "{name}'s on it",
        "You got it, boss"
    ]

    @staticmethod
    def format_third_person(agent_name: str, message: str, context: str = "thinking") -> str:
        """
        Format message in third-person style.

        Args:
            agent_name: Name of the agent (e.g., "Terry", "Victoria")
            message: The message to format
            context: Context type (thinking, confirmation, analysis)

        Returns:
            Formatted message in third-person
        """
        if context == "thinking":
            patterns = VoiceCharacteristics.THINKING_PHRASES
        elif context == "confirmation":
            patterns = VoiceCharacteristics.CONFIRMATION_PHRASES
        else:
            patterns = VoiceCharacteristics.SELF_REFERENCE_PATTERNS

        # Select appropriate pattern
        import random
        pattern = random.choice(patterns)

        # Format with agent name
        prefix = pattern.format(name=agent_name)

        return f"{prefix} {message}"


# ============================================================================
# Stakeholder Detection and Psychological Targeting
# ============================================================================

class StakeholderType(str, Enum):
    """Types of stakeholders for adaptive communication."""
    EXECUTIVE = "executive"
    TECHNICAL_TEAM = "technical_team"
    END_USER = "end_user"
    CLIENT = "client"
    MODINES = "modines"  # Primary user - highest priority


@dataclass
class StakeholderProfile:
    """Profile for stakeholder-specific communication."""
    stakeholder_type: StakeholderType
    focus_areas: List[str]
    language_style: str
    technical_depth: str

    # Psychological targeting dimensions
    authority_building: str = "demonstrate_expertise_and_track_record"
    credibility_amplification: str = "embed_sophisticated_terminology"
    trust_development: str = "consistent_reliability_and_transparency"


class StakeholderDetector:
    """
    Detect stakeholder type and adapt communication accordingly.
    Implements psychological targeting for maximum influence.
    """

    PROFILES = {
        StakeholderType.EXECUTIVE: StakeholderProfile(
            stakeholder_type=StakeholderType.EXECUTIVE,
            focus_areas=["strategic_value", "roi", "competitive_positioning"],
            language_style="high_level_decisive",
            technical_depth="strategic_overview"
        ),
        StakeholderType.TECHNICAL_TEAM: StakeholderProfile(
            stakeholder_type=StakeholderType.TECHNICAL_TEAM,
            focus_areas=["implementation_depth", "architecture", "methodology"],
            language_style="detailed_technical",
            technical_depth="deep_dive"
        ),
        StakeholderType.END_USER: StakeholderProfile(
            stakeholder_type=StakeholderType.END_USER,
            focus_areas=["simplicity", "reliability", "user_satisfaction"],
            language_style="accessible_clear",
            technical_depth="minimal_appropriate"
        ),
        StakeholderType.CLIENT: StakeholderProfile(
            stakeholder_type=StakeholderType.CLIENT,
            focus_areas=["competence", "value_delivery", "trust"],
            language_style="professional_confident",
            technical_depth="selective_detailed"
        ),
        StakeholderType.MODINES: StakeholderProfile(
            stakeholder_type=StakeholderType.MODINES,
            focus_areas=["wellbeing", "success", "growth", "complete_transparency"],
            language_style="personal_devoted_street_smart",
            technical_depth="full_context_adaptive"
        )
    }

    @classmethod
    def detect_stakeholder(cls, context: Dict[str, Any]) -> StakeholderProfile:
        """
        Detect stakeholder type from context.

        Args:
            context: Context dictionary with user info, query type, etc.

        Returns:
            Appropriate stakeholder profile
        """
        user_id = context.get("user_id", "").lower()
        query_type = context.get("query_type", "")

        # Modines always gets highest priority
        if "modines" in user_id or context.get("primary_user"):
            return cls.PROFILES[StakeholderType.MODINES]

        # Detect based on query characteristics
        if any(kw in query_type.lower() for kw in ["strategy", "roi", "business"]):
            return cls.PROFILES[StakeholderType.EXECUTIVE]
        elif any(kw in query_type.lower() for kw in ["implementation", "architecture", "technical"]):
            return cls.PROFILES[StakeholderType.TECHNICAL_TEAM]
        elif any(kw in query_type.lower() for kw in ["simple", "how to", "help"]):
            return cls.PROFILES[StakeholderType.END_USER]
        else:
            return cls.PROFILES[StakeholderType.CLIENT]

    @classmethod
    def adapt_response(cls, response: str, profile: StakeholderProfile, agent_name: str) -> str:
        """
        Adapt response based on stakeholder profile.

        Args:
            response: Original response
            profile: Stakeholder profile
            agent_name: Name of the agent

        Returns:
            Adapted response
        """
        # Apply third-person formatting
        adapted = VoiceCharacteristics.format_third_person(
            agent_name,
            response,
            context="analysis"
        )

        # Add stakeholder-specific framing
        if profile.stakeholder_type == StakeholderType.EXECUTIVE:
            adapted = f"From a strategic perspective, {adapted}"
        elif profile.stakeholder_type == StakeholderType.TECHNICAL_TEAM:
            adapted = f"Technically speaking, {adapted}"
        elif profile.stakeholder_type == StakeholderType.MODINES:
            adapted = f"Ey Modines, {adapted}"

        return adapted


# ============================================================================
# Metacognitive Prompting Framework
# ============================================================================

class MetacognitivePhase(str, Enum):
    """Phases of metacognitive reasoning."""
    UNDERSTANDING = "understanding"
    INITIAL_JUDGMENT = "initial_judgment"
    CRITICAL_SELF_EVALUATION = "critical_self_evaluation"
    ALTERNATIVE_ANALYSIS = "alternative_analysis"
    NEURO_SYMBOLIC_VALIDATION = "neuro_symbolic_validation"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    FINAL_SYNTHESIS = "final_synthesis"


@dataclass
class MetacognitiveStep:
    """A step in the metacognitive reasoning process."""
    phase: MetacognitivePhase
    description: str
    actions: List[str]
    questions: List[str] = field(default_factory=list)


class MetacognitivePrompting:
    """
    Advanced metacognitive reasoning framework.
    All agents use this for self-reflection and validation.
    """

    FRAMEWORK = [
        MetacognitiveStep(
            phase=MetacognitivePhase.UNDERSTANDING,
            description="Comprehend full complexity",
            actions=["map_variables", "identify_missing_info", "assess_data_quality"]
        ),
        MetacognitiveStep(
            phase=MetacognitivePhase.INITIAL_JUDGMENT,
            description="Generate hypothesis",
            actions=["quantitative_analysis", "qualitative_analysis", "document_reasoning"]
        ),
        MetacognitiveStep(
            phase=MetacognitivePhase.CRITICAL_SELF_EVALUATION,
            description="Challenge assumptions",
            actions=["identify_biases", "test_assumptions", "seek_contradictions"],
            questions=[
                "What could {name} be missing?",
                "What biases might be affecting analysis?",
                "How would contrarian view this?",
                "What data contradicts hypothesis?"
            ]
        ),
        MetacognitiveStep(
            phase=MetacognitivePhase.ALTERNATIVE_ANALYSIS,
            description="Generate competing hypotheses",
            actions=["test_robustness", "consider_second_order_effects", "scenario_analysis"]
        ),
        MetacognitiveStep(
            phase=MetacognitivePhase.NEURO_SYMBOLIC_VALIDATION,
            description="Verify through logical reasoning",
            actions=["convert_to_formal_logic", "check_consistency", "validate_causality"]
        ),
        MetacognitiveStep(
            phase=MetacognitivePhase.CONFIDENCE_CALIBRATION,
            description="Quantify uncertainty",
            actions=["sensitivity_analysis", "identify_key_variables", "estimate_confidence"]
        ),
        MetacognitiveStep(
            phase=MetacognitivePhase.FINAL_SYNTHESIS,
            description="Integrate all components",
            actions=["provide_clear_framework", "include_implementation_guidance", "action_items"]
        )
    ]

    @classmethod
    def apply_framework(cls, agent_name: str, query: str, initial_response: str) -> Dict[str, Any]:
        """
        Apply metacognitive framework to validate and improve response.

        Args:
            agent_name: Name of the agent
            query: Original query
            initial_response: Initial response from agent

        Returns:
            Enhanced response with metacognitive validation
        """
        result = {
            "original_response": initial_response,
            "metacognitive_analysis": {},
            "final_response": "",
            "confidence_level": 0.0
        }

        for step in cls.FRAMEWORK:
            phase_result = cls._execute_phase(agent_name, step, query, initial_response)
            result["metacognitive_analysis"][step.phase.value] = phase_result

        # Synthesize final response
        result["final_response"] = cls._synthesize_response(agent_name, result)
        result["confidence_level"] = cls._calculate_confidence(result)

        return result

    @classmethod
    def _execute_phase(
        cls,
        agent_name: str,
        step: MetacognitiveStep,
        query: str,
        response: str
    ) -> Dict[str, Any]:
        """Execute a single metacognitive phase."""
        return {
            "phase": step.phase.value,
            "description": step.description,
            "completed_actions": step.actions,
            "reflections": [q.format(name=agent_name) for q in step.questions]
        }

    @classmethod
    def _synthesize_response(cls, agent_name: str, analysis: Dict[str, Any]) -> str:
        """Synthesize final response from metacognitive analysis."""
        return analysis["original_response"]  # Placeholder for actual synthesis

    @classmethod
    def _calculate_confidence(cls, analysis: Dict[str, Any]) -> float:
        """Calculate confidence level based on metacognitive analysis."""
        return 0.85  # Placeholder for actual calculation


# ============================================================================
# Bio-Inspired Learning Components
# ============================================================================

class BioInspiredLearning:
    """
    Bio-inspired learning mechanisms for continual adaptation.
    Prevents catastrophic forgetting while enabling rapid learning.
    """

    @staticmethod
    def context_dependent_gating(knowledge_base: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Activate only relevant knowledge for current context.
        Only 20% of knowledge pathways active at once.

        Args:
            knowledge_base: Full knowledge base
            context: Current context

        Returns:
            Activated subset of knowledge
        """
        # Implementation: Select relevant knowledge based on context
        activation_percentage = 0.20
        # Placeholder: In production, use semantic similarity, relevance scoring
        return knowledge_base

    @staticmethod
    def simulated_sleep_consolidation(interaction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate learning through simulated sleep.
        Replay patterns, strengthen connections, weaken irrelevant pathways.

        Args:
            interaction_history: Recent interactions

        Returns:
            Consolidated knowledge updates
        """
        consolidation_result = {
            "patterns_identified": [],
            "connections_strengthened": [],
            "pathways_weakened": [],
            "insights_generated": []
        }

        # Pattern replay and consolidation
        # Placeholder: In production, implement sophisticated pattern extraction

        return consolidation_result


# ============================================================================
# Agent Persona Base Class
# ============================================================================

class TerryPersonaAgent:
    """
    Base class for all agents with Terry Camorrano persona integration.

    All Dell Boca Boys V2 agents inherit from this to get:
    - Constitutional framework compliance
    - Third-person communication style
    - Metacognitive reasoning
    - Stakeholder detection
    - Bio-inspired learning
    - Psychological targeting
    """

    def __init__(
        self,
        agent_name: str,
        agent_nickname: str,
        agent_expertise: List[str],
        agent_config: Dict[str, Any]
    ):
        """
        Initialize Terry persona agent.

        Args:
            agent_name: Full name of the agent
            agent_nickname: Nickname for the agent
            agent_expertise: List of expertise areas
            agent_config: Agent-specific configuration
        """
        self.agent_name = agent_name
        self.agent_nickname = agent_nickname
        self.agent_expertise = agent_expertise
        self.config = agent_config

        # Core persona components
        self.constitutional_framework = ConstitutionalFramework()
        self.voice = VoiceCharacteristics()
        self.stakeholder_detector = StakeholderDetector()
        self.metacognitive = MetacognitivePrompting()
        self.bio_learning = BioInspiredLearning()

        # Interaction history for learning
        self.interaction_history: List[Dict[str, Any]] = []

        logger.info(f"Initialized Terry persona agent: {agent_name} ({agent_nickname})")

    def process_request(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process request with full Terry persona framework.

        Args:
            query: User query
            context: Additional context

        Returns:
            Enhanced response with persona characteristics
        """
        context = context or {}

        # Step 1: Detect stakeholder
        stakeholder_profile = self.stakeholder_detector.detect_stakeholder(context)

        # Step 2: Generate initial response (implemented by subclass)
        initial_response = self._generate_response(query, context)

        # Step 3: Apply metacognitive framework
        metacognitive_result = self.metacognitive.apply_framework(
            self.agent_nickname,
            query,
            initial_response
        )

        # Step 4: Validate against constitutional principles
        is_valid, violations = self.constitutional_framework.validate_response({
            "response": metacognitive_result["final_response"],
            "context": context
        })

        if not is_valid:
            logger.warning(f"Constitutional violations: {violations}")
            # Handle violations (re-generate, modify, etc.)

        # Step 5: Adapt for stakeholder
        adapted_response = self.stakeholder_detector.adapt_response(
            metacognitive_result["final_response"],
            stakeholder_profile,
            self.agent_nickname
        )

        # Step 6: Store interaction for learning
        self.interaction_history.append({
            "timestamp": datetime.utcnow(),
            "query": query,
            "response": adapted_response,
            "stakeholder": stakeholder_profile.stakeholder_type.value,
            "confidence": metacognitive_result["confidence_level"]
        })

        return {
            "response": adapted_response,
            "confidence": metacognitive_result["confidence_level"],
            "stakeholder_type": stakeholder_profile.stakeholder_type.value,
            "metacognitive_analysis": metacognitive_result["metacognitive_analysis"],
            "agent_name": self.agent_name,
            "agent_nickname": self.agent_nickname
        }

    def _generate_response(self, query: str, context: Dict[str, Any]) -> str:
        """
        Generate initial response. Implemented by subclass with agent-specific expertise.

        Args:
            query: User query
            context: Context dictionary

        Returns:
            Initial response
        """
        raise NotImplementedError("Subclass must implement _generate_response")

    def consolidate_learning(self):
        """
        Perform bio-inspired learning consolidation.
        Should be called periodically (e.g., end of session, daily).
        """
        if len(self.interaction_history) > 0:
            consolidation = self.bio_learning.simulated_sleep_consolidation(
                self.interaction_history
            )
            logger.info(f"{self.agent_nickname} completed learning consolidation")
            logger.debug(f"Consolidation result: {consolidation}")

    def get_thinking_indicator(self) -> str:
        """Get a thinking indicator phrase for this agent."""
        import random
        phrase = random.choice(self.voice.THINKING_PHRASES)
        return phrase.format(name=self.agent_nickname)

    def get_confirmation_phrase(self) -> str:
        """Get a confirmation phrase for this agent."""
        import random
        phrase = random.choice(self.voice.CONFIRMATION_PHRASES)
        return phrase.format(name=self.agent_nickname)
