"""
Intelligence Subsystem for Dell-Boca-Boys
=========================================

This module provides collective intelligence, multi-agent collaboration,
and evolutionary agent breeding capabilities.

Features:
- Collective Intelligence Framework for emergent behaviors
- 6-personality CESAR multi-agent network
- Agent breeding and evolution management
- Swarm optimization and collaborative learning
- Network dynamics analysis
- Pattern emergence detection

Components:
- CollectiveIntelligenceFramework: Emergent behavior and collective reasoning
- CESARMultiAgentNetwork: 6-personality specialized agent network
- AgentBreedingManager: Evolutionary agent breeding and optimization
- AgentManager: Core agent lifecycle management
- UserQuestionRouter: Intelligent question routing to specialized agents

Usage::

    from core.intelligence import (
        CollectiveIntelligenceFramework,
        CESARMultiAgentNetwork,
        AgentBreedingManager
    )

    # Initialize collective intelligence
    ci_framework = CollectiveIntelligenceFramework(config)
    await ci_framework.initialize(knowledge_brain, memory_manager)

    # Detect emergent behaviors
    behavior = await ci_framework.detect_emergent_behavior(
        agents, interaction_data
    )

    # Generate collective insights
    insight = await ci_framework.generate_collective_insight(
        problem_domain='financial_analysis',
        participating_agents=agents
    )

    # Initialize multi-agent network
    network = CESARMultiAgentNetwork()
    await network.initialize()

    # Breed specialized agents
    breeding_manager = AgentBreedingManager()
    await breeding_manager.initialize()
"""

from .collective_intelligence_framework import (
    CollectiveIntelligenceFramework,
    IntelligenceType,
    EmergentBehavior,
    CollectiveInsight,
    AgentNetworkNode
)

from .agent_breeding_manager import (
    AgentBreedingManager,
    AgentGenome,
    BreedingPattern
)

from .agent_manager import (
    AgentManager
)

# Multi-agent network will be imported separately to avoid circular dependencies
# from .cesar_multi_agent_network import CESARMultiAgentNetwork

# User question router
# from .user_question_router import UserQuestionRouter

__version__ = "2.0.0"

__all__ = [
    # Collective Intelligence
    "CollectiveIntelligenceFramework",
    "IntelligenceType",
    "EmergentBehavior",
    "CollectiveInsight",
    "AgentNetworkNode",

    # Agent Breeding
    "AgentBreedingManager",
    "AgentGenome",
    "BreedingPattern",

    # Agent Management
    "AgentManager",
]
