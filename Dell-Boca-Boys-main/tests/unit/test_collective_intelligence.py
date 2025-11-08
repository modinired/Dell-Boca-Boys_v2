"""
Comprehensive unit tests for Collective Intelligence Framework.
Tests emergent behavior detection, swarm optimization, and collaborative learning.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import numpy as np

from core.intelligence.collective_intelligence_framework import (
    CollectiveIntelligenceFramework,
    IntelligenceType,
    EmergentBehavior,
    CollectiveInsight,
    AgentNetworkNode
)
from core.memory.google_sheets_memory_manager import MemoryType


@pytest.mark.unit
class TestCollectiveIntelligenceFramework:
    """Test suite for Collective Intelligence Framework."""

    @pytest.fixture
    def ci_config(self, collective_intelligence_config):
        """Provide CI framework configuration."""
        return collective_intelligence_config

    @pytest.fixture
    async def ci_framework(self, ci_config):
        """Create CI framework instance."""
        framework = CollectiveIntelligenceFramework(ci_config)

        # Mock knowledge brain and memory manager
        framework.knowledge_brain = Mock()
        framework.memory_manager = Mock()
        framework.memory_manager.store_memory = AsyncMock()
        framework.memory_manager.MemoryType = MemoryType

        await framework.initialize(framework.knowledge_brain, framework.memory_manager)
        return framework

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        agents = []
        for i in range(5):
            agent = Mock()
            agent.agent_id = f"agent_{i}"
            agent.agent_type = f"type_{i % 2}"  # 2 types
            agent.get_capabilities = Mock(return_value=[
                f"capability_{i}",
                "common_capability"
            ])
            agent.get_performance_metrics = AsyncMock(return_value={
                "success_rate": 0.8 + (i * 0.03),
                "avg_latency_ms": 100 + (i * 10)
            })
            agent.is_healthy = AsyncMock(return_value=True)
            agents.append(agent)
        return agents

    @pytest.mark.asyncio
    async def test_initialization(self, ci_framework):
        """Test framework initialization."""
        assert ci_framework is not None
        assert ci_framework.agent_network is not None
        assert len(ci_framework.agent_nodes) == 0
        assert len(ci_framework.emergent_behaviors) == 0
        assert ci_framework.ci_parameters['emergence_threshold'] == 0.7

    @pytest.mark.asyncio
    async def test_register_agent(self, ci_framework, mock_agents):
        """Test agent registration in the network."""
        agent = mock_agents[0]

        success = await ci_framework.register_agent(agent)

        assert success is True
        assert agent.agent_id in ci_framework.agent_nodes
        assert ci_framework.agent_network.has_node(agent.agent_id)

        # Verify agent node properties
        agent_node = ci_framework.agent_nodes[agent.agent_id]
        assert agent_node.agent_id == agent.agent_id
        assert len(agent_node.capabilities) > 0
        assert isinstance(agent_node.performance_metrics, dict)
        assert isinstance(agent_node.trust_scores, dict)

    @pytest.mark.asyncio
    async def test_register_multiple_agents(self, ci_framework, mock_agents):
        """Test registering multiple agents and trust score initialization."""
        # Register first two agents
        await ci_framework.register_agent(mock_agents[0])
        await ci_framework.register_agent(mock_agents[1])

        # Verify network structure
        assert len(ci_framework.agent_nodes) == 2
        assert ci_framework.agent_network.number_of_nodes() == 2

        # Verify trust scores are initialized between agents
        agent0_node = ci_framework.agent_nodes[mock_agents[0].agent_id]
        agent1_node = ci_framework.agent_nodes[mock_agents[1].agent_id]

        assert mock_agents[1].agent_id in agent0_node.trust_scores
        assert mock_agents[0].agent_id in agent1_node.trust_scores
        assert 0 < agent0_node.trust_scores[mock_agents[1].agent_id] <= 1.0

    @pytest.mark.asyncio
    async def test_detect_emergent_behavior(self, ci_framework, mock_agents):
        """Test emergent behavior detection from agent interactions."""
        # Register agents
        for agent in mock_agents[:3]:
            await ci_framework.register_agent(agent)

        # Create interaction data with high emergence score
        interaction_data = {
            "type": "collaborative_problem_solving",
            "actions": [
                {"agent": "agent_0", "action": "analyze"},
                {"agent": "agent_1", "action": "synthesize"},
                {"agent": "agent_2", "action": "validate"}
            ],
            "outcome": {
                "success": True,
                "solution_quality": 0.95,
                "novel_approach": True
            },
            "triggers": {
                "complexity": "high",
                "urgency": "medium"
            }
        }

        behavior = await ci_framework.detect_emergent_behavior(
            mock_agents[:3],
            interaction_data
        )

        assert behavior is not None
        assert isinstance(behavior, EmergentBehavior)
        assert len(behavior.participating_agents) == 3
        assert behavior.emergence_strength > ci_framework.ci_parameters['emergence_threshold']
        assert behavior.replication_count == 1

    @pytest.mark.asyncio
    async def test_emergent_behavior_stability_tracking(self, ci_framework, mock_agents):
        """Test stability score calculation for recurring behaviors."""
        # Register agents
        for agent in mock_agents[:3]:
            await ci_framework.register_agent(agent)

        interaction_data = {
            "type": "pattern_alpha",
            "actions": [{"agent": "agent_0", "action": "test"}],
            "outcome": {"success": True},
            "triggers": {"test": True}
        }

        # Detect same behavior multiple times
        behavior1 = await ci_framework.detect_emergent_behavior(mock_agents[:3], interaction_data)
        behavior2 = await ci_framework.detect_emergent_behavior(mock_agents[:3], interaction_data)
        behavior3 = await ci_framework.detect_emergent_behavior(mock_agents[:3], interaction_data)

        # Should be same behavior (same ID)
        assert behavior1.behavior_id == behavior2.behavior_id == behavior3.behavior_id

        # Replication count should increase
        final_behavior = ci_framework.emergent_behaviors[behavior1.behavior_id]
        assert final_behavior.replication_count >= 3

        # Stability score should be calculated
        assert final_behavior.stability_score > 0

    @pytest.mark.asyncio
    async def test_generate_collective_insight(self, ci_framework, mock_agents):
        """Test collective insight generation from distributed knowledge."""
        # Register agents
        for agent in mock_agents[:4]:
            await ci_framework.register_agent(agent)

        # Generate collective insight
        insight = await ci_framework.generate_collective_insight(
            problem_domain="workflow_optimization",
            participating_agents=mock_agents[:4]
        )

        assert insight is not None
        assert isinstance(insight, CollectiveInsight)
        assert insight.intelligence_type == IntelligenceType.DISTRIBUTED_REASONING
        assert len(insight.source_agents) == 4
        assert insight.confidence_score > ci_framework.ci_parameters['insight_confidence_threshold']
        assert len(insight.insight_content) > 0
        assert len(insight.application_areas) > 0

    @pytest.mark.asyncio
    async def test_swarm_optimization(self, ci_framework, mock_agents):
        """Test swarm intelligence optimization."""
        # Register agents
        for agent in mock_agents:
            await ci_framework.register_agent(agent)

        # Run swarm optimization
        result = await ci_framework.optimize_swarm_behavior(
            objective="performance_optimization",
            agent_pool=mock_agents
        )

        assert result is not None
        assert "objective" in result
        assert "final_configuration" in result
        assert "performance_improvement" in result
        assert len(result["optimization_steps"]) > 0

        # Verify convergence was tracked
        last_step = result["optimization_steps"][-1]
        assert "convergence_metric" in last_step
        assert "performance_score" in last_step

    @pytest.mark.asyncio
    async def test_collaborative_learning(self, ci_framework, mock_agents):
        """Test collaborative learning between agents."""
        # Register agents
        for agent in mock_agents[:4]:
            await ci_framework.register_agent(agent)

        # Facilitate collaborative learning
        learning_session = await ci_framework.facilitate_collaborative_learning(
            learning_domain="workflow_patterns",
            participants=mock_agents[:4]
        )

        assert learning_session is not None
        assert "session_id" in learning_session
        assert learning_session["domain"] == "workflow_patterns"
        assert len(learning_session["participants"]) == 4
        assert "learning_exchanges" in learning_session
        assert "knowledge_synthesis" in learning_session
        assert "learning_outcomes" in learning_session

        # Verify each participant has learning outcomes
        for agent in mock_agents[:4]:
            assert agent.agent_id in learning_session["learning_outcomes"]

    @pytest.mark.asyncio
    async def test_collective_memory_maintenance(self, ci_framework, mock_agents):
        """Test collective memory maintenance."""
        # Register agents
        for agent in mock_agents[:3]:
            await ci_framework.register_agent(agent)

        # Run memory maintenance
        result = await ci_framework.maintain_collective_memory()

        assert result is not None
        assert "memory_consolidation" in result
        assert "pattern_extraction" in result
        assert "knowledge_evolution" in result
        assert "network_updates" in result

    @pytest.mark.asyncio
    async def test_network_dynamics_analysis(self, ci_framework, mock_agents):
        """Test network dynamics analysis."""
        # Register agents and create some connections
        for agent in mock_agents[:4]:
            await ci_framework.register_agent(agent)

        # Add some edges to the network
        ci_framework.agent_network.add_edge("agent_0", "agent_1", weight=0.8)
        ci_framework.agent_network.add_edge("agent_1", "agent_2", weight=0.7)

        analysis = await ci_framework.analyze_network_dynamics()

        assert analysis is not None
        assert "network_metrics" in analysis
        assert "trust_dynamics" in analysis
        assert "collaboration_patterns" in analysis
        assert "information_flow" in analysis
        assert "emergence_potential" in analysis

    @pytest.mark.asyncio
    async def test_emergence_potential_assessment(self, ci_framework, mock_agents):
        """Test emergence potential assessment."""
        # Empty network should have low emergence potential
        potential_empty = await ci_framework._assess_emergence_potential()
        assert potential_empty < 0.2

        # Add agents with diverse capabilities
        for agent in mock_agents:
            await ci_framework.register_agent(agent)

        # Connected network with diverse agents should have higher potential
        potential_full = await ci_framework._assess_emergence_potential()
        assert potential_full > potential_empty

    @pytest.mark.asyncio
    async def test_trust_score_calculation(self, ci_framework, mock_agents):
        """Test initial trust score calculation between agents."""
        agent1 = mock_agents[0]
        agent2 = mock_agents[1]

        await ci_framework.register_agent(agent1)
        await ci_framework.register_agent(agent2)

        node1 = ci_framework.agent_nodes[agent1.agent_id]
        node2 = ci_framework.agent_nodes[agent2.agent_id]

        # Trust scores should be symmetric
        trust_1_to_2 = node1.trust_scores[agent2.agent_id]
        trust_2_to_1 = node2.trust_scores[agent1.agent_id]

        assert trust_1_to_2 == trust_2_to_1
        assert 0.1 <= trust_1_to_2 <= 1.0

    @pytest.mark.asyncio
    async def test_knowledge_synthesis(self, ci_framework):
        """Test knowledge synthesis from agent contributions."""
        agent_contributions = {
            "agent_0": {
                "capabilities": ["api_integration", "data_transform"],
                "domain_expertise": 0.8
            },
            "agent_1": {
                "capabilities": ["api_integration", "error_handling"],
                "domain_expertise": 0.7
            },
            "agent_2": {
                "capabilities": ["data_validation", "monitoring"],
                "domain_expertise": 0.9
            }
        }

        synthesis = ci_framework._synthesize_knowledge(agent_contributions)

        assert synthesis is not None
        assert "consensus_areas" in synthesis
        assert "novel_combinations" in synthesis

        # "api_integration" should be in consensus (mentioned by 2 agents)
        assert "api_integration" in synthesis["consensus_areas"]

    @pytest.mark.asyncio
    async def test_get_collective_intelligence_status(self, ci_framework, mock_agents):
        """Test retrieving collective intelligence status."""
        # Register some agents
        for agent in mock_agents[:3]:
            await ci_framework.register_agent(agent)

        # Create some emergent behaviors
        interaction_data = {
            "type": "test_behavior",
            "actions": [{"agent": "agent_0", "action": "test"}],
            "outcome": {"success": True},
            "triggers": {"test": True}
        }
        await ci_framework.detect_emergent_behavior(mock_agents[:2], interaction_data)

        status = await ci_framework.get_collective_intelligence_status()

        assert status is not None
        assert status["network_size"] == 3
        assert status["emergent_behaviors"] > 0
        assert "network_density" in status
        assert "average_trust" in status
        assert "emergence_potential" in status

    @pytest.mark.asyncio
    async def test_behavior_novelty_assessment(self, ci_framework):
        """Test novelty assessment for interaction outcomes."""
        # New outcome should have high novelty
        outcome1 = {"type": "novel_approach", "value": "unique"}
        novelty1 = ci_framework._assess_outcome_novelty(outcome1)
        assert novelty1 > 0.8

        # Add behavior to history
        ci_framework.emergent_behaviors["test_behavior"] = EmergentBehavior(
            behavior_id="test_behavior",
            behavior_type="test",
            participating_agents=["agent_0"],
            trigger_conditions={},
            observed_outcomes=[outcome1],
            emergence_strength=0.8,
            stability_score=0.5,
            discovery_timestamp=datetime.utcnow(),
            last_observed=datetime.utcnow(),
            replication_count=1
        )

        # Same outcome should have lower novelty
        novelty2 = ci_framework._assess_outcome_novelty(outcome1)
        assert novelty2 < novelty1

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, ci_framework, mock_agents):
        """Test thread safety of concurrent agent operations."""
        # Register agents concurrently
        tasks = [ci_framework.register_agent(agent) for agent in mock_agents]
        results = await asyncio.gather(*tasks)

        assert all(results)
        assert len(ci_framework.agent_nodes) == len(mock_agents)

    @pytest.mark.asyncio
    async def test_framework_shutdown(self, ci_framework, mock_agents):
        """Test graceful framework shutdown."""
        # Register some agents
        for agent in mock_agents[:2]:
            await ci_framework.register_agent(agent)

        # Shutdown should complete without errors
        await ci_framework.shutdown()

        # Framework should still have data (not cleared)
        assert len(ci_framework.agent_nodes) > 0
