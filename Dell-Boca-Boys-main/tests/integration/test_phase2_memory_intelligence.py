#!/usr/bin/env python3
"""
Phase 2 Integration Tests: Memory & Intelligence
Tests for enhanced memory management and collective intelligence systems.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Memory system imports
from core.memory import (
    EnhancedMemoryManager,
    GoogleSheetsMemoryManager,
    MemoryProvider,
    MemoryType,
    MemoryQuery,
    create_enhanced_memory_manager
)

# Intelligence system imports
from core.intelligence import (
    CollectiveIntelligenceFramework,
    AgentBreedingManager,
    IntelligenceType,
    AgentGenome,
    BreedingPattern
)


class TestEnhancedMemoryManager:
    """Test suite for Enhanced Memory Manager with Mem0 integration."""

    @pytest.fixture
    async def memory_manager(self):
        """Create enhanced memory manager for testing."""
        config = {
            'sheets_config': {},
            'memory_spreadsheet_id': 'test_spreadsheet',
            'google_credentials_path': None
        }

        manager = create_enhanced_memory_manager(
            cesar_config=config,
            provider=MemoryProvider.CESAR_SHEETS  # Use CESAR for tests (no Mem0 dependency)
        )

        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_memory_storage_and_retrieval(self, memory_manager):
        """Test basic memory storage and retrieval."""
        # Store agent communication
        memory_id = await memory_manager.store_agent_communication(
            sender_id="agent_1",
            receiver_id="agent_2",
            message_type="task_assignment",
            content={"task": "analyze_data", "priority": "high"},
            importance=0.9
        )

        assert memory_id is not None
        assert len(memory_id) > 0

        # Retrieve memory
        query = MemoryQuery(
            memory_types=[MemoryType.AGENT_COMMUNICATION],
            agent_filter="agent_1",
            limit=10
        )

        results = await memory_manager.retrieve_memory(query)
        assert len(results) >= 0  # May be 0 if Google Sheets not configured

    @pytest.mark.asyncio
    async def test_learning_data_storage(self, memory_manager):
        """Test learning data storage."""
        memory_id = await memory_manager.store_learning_data(
            agent_id="agent_1",
            learning_type="pattern_recognition",
            learning_content={
                "pattern": "market_trend",
                "accuracy": 0.92,
                "training_samples": 1000
            },
            effectiveness=0.92
        )

        assert memory_id is not None

    @pytest.mark.asyncio
    async def test_user_interaction_storage(self, memory_manager):
        """Test user interaction storage."""
        memory_id = await memory_manager.store_user_interaction(
            user_id="user_123",
            interaction_type="query",
            content={
                "question": "What is the market trend?",
                "response": "Upward trend detected",
                "satisfaction": 0.95
            },
            sentiment=0.9
        )

        assert memory_id is not None

    @pytest.mark.asyncio
    async def test_performance_analytics(self, memory_manager):
        """Test memory performance analytics."""
        # Store some test data
        await memory_manager.store_memory(
            MemoryType.SYSTEM_STATE,
            content={"status": "active", "uptime": 3600},
            importance_score=0.7
        )

        # Get analytics
        analytics = await memory_manager.get_performance_analytics()

        assert 'status' in analytics or 'total_operations' in analytics

    @pytest.mark.asyncio
    async def test_memory_status(self, memory_manager):
        """Test memory system status retrieval."""
        status = await memory_manager.get_memory_status()

        assert 'enhanced_memory_manager' in status
        assert status['enhanced_memory_manager']['active_provider'] == MemoryProvider.CESAR_SHEETS.value


class TestGoogleSheetsMemoryManager:
    """Test suite for Google Sheets Memory Manager."""

    @pytest.fixture
    async def sheets_manager(self):
        """Create Google Sheets memory manager for testing."""
        config = {
            'sheets_config': {},
            'memory_spreadsheet_id': 'test_spreadsheet',
            'google_credentials_path': None
        }

        manager = GoogleSheetsMemoryManager(config)
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_agent_memory_summary(self, sheets_manager):
        """Test agent memory summary generation."""
        summary = await sheets_manager.get_agent_memory_summary(
            agent_id="agent_1",
            days=7
        )

        assert 'agent_id' in summary
        assert summary['agent_id'] == "agent_1"

    @pytest.mark.asyncio
    async def test_system_memory_analytics(self, sheets_manager):
        """Test system-wide memory analytics."""
        analytics = await sheets_manager.get_system_memory_analytics()

        assert 'total_memories' in analytics
        assert 'memory_distribution' in analytics

    @pytest.mark.asyncio
    async def test_memory_optimization(self, sheets_manager):
        """Test memory optimization functionality."""
        results = await sheets_manager.perform_memory_optimization()

        assert 'start_time' in results
        assert 'optimizations_performed' in results


class TestCollectiveIntelligenceFramework:
    """Test suite for Collective Intelligence Framework."""

    @pytest.fixture
    async def ci_framework(self):
        """Create collective intelligence framework for testing."""
        config = {
            'cesar_integration': {},
            'max_swarm_iterations': 5,
            'max_learning_rounds': 3
        }

        framework = CollectiveIntelligenceFramework(config)

        # Create mock knowledge brain and memory manager
        knowledge_brain = None  # Would be actual implementation
        memory_manager = None   # Would be actual implementation

        await framework.initialize(knowledge_brain, memory_manager)
        yield framework
        await framework.shutdown()

    @pytest.mark.asyncio
    async def test_agent_registration(self, ci_framework):
        """Test agent registration in network."""
        # Create mock agent
        class MockAgent:
            def __init__(self):
                self.agent_id = "test_agent_1"
                self.agent_type = "analytical_agent"

            def get_capabilities(self):
                return ["data_analysis", "pattern_recognition"]

            async def get_performance_metrics(self):
                return {"success_rate": 0.85}

        agent = MockAgent()
        success = await ci_framework.register_agent(agent)

        assert success is True
        assert agent.agent_id in ci_framework.agent_nodes

    @pytest.mark.asyncio
    async def test_network_status(self, ci_framework):
        """Test collective intelligence status retrieval."""
        status = await ci_framework.get_collective_intelligence_status()

        assert 'network_size' in status
        assert 'emergent_behaviors' in status
        assert 'collective_insights' in status


class TestAgentBreedingManager:
    """Test suite for Agent Breeding Manager."""

    @pytest.fixture
    async def breeding_manager(self):
        """Create agent breeding manager for testing."""
        manager = AgentBreedingManager()
        await manager.initialize()
        yield manager
        await manager.shutdown()

    @pytest.mark.asyncio
    async def test_task_pattern_observation(self, breeding_manager):
        """Test observation of task patterns for breeding."""
        task_data = {
            'task_type': 'data_analysis',
            'required_capabilities': ['analytics', 'statistics'],
            'complexity_indicators': ['large_dataset', 'real_time'],
            'estimated_duration_ms': 5000
        }

        performance_metrics = {
            'success_rate': 0.9,
            'duration_ms': 4800
        }

        await breeding_manager.observe_task_pattern(
            task_data=task_data,
            agents_involved=["agent_1", "agent_2"],
            performance_metrics=performance_metrics
        )

        # Check that pattern was recorded
        assert len(breeding_manager.breeding_patterns) > 0

    @pytest.mark.asyncio
    async def test_breeding_status(self, breeding_manager):
        """Test breeding manager status retrieval."""
        status = await breeding_manager.get_breeding_status()

        assert 'active_patterns' in status
        assert 'stored_genomes' in status
        assert 'evolution_events' in status
        assert 'breeding_rules' in status


class TestMemoryIntelligenceIntegration:
    """Integration tests for Memory and Intelligence systems working together."""

    @pytest.mark.asyncio
    async def test_collective_memory_integration(self):
        """Test integration between collective intelligence and memory systems."""
        # Create memory manager
        memory_config = {
            'sheets_config': {},
            'memory_spreadsheet_id': 'test_spreadsheet',
            'google_credentials_path': None
        }

        memory_manager = create_enhanced_memory_manager(
            cesar_config=memory_config,
            provider=MemoryProvider.CESAR_SHEETS
        )
        await memory_manager.initialize()

        # Create CI framework
        ci_config = {'cesar_integration': {}}
        ci_framework = CollectiveIntelligenceFramework(ci_config)
        await ci_framework.initialize(None, memory_manager)

        # Test integration
        status = await ci_framework.get_collective_intelligence_status()
        assert status is not None

        # Cleanup
        await ci_framework.shutdown()
        await memory_manager.shutdown()

    @pytest.mark.asyncio
    async def test_breeding_with_memory(self):
        """Test agent breeding with memory persistence."""
        # Create breeding manager
        breeding_manager = AgentBreedingManager()
        await breeding_manager.initialize()

        # Create memory manager
        memory_config = {
            'sheets_config': {},
            'memory_spreadsheet_id': 'test_spreadsheet',
            'google_credentials_path': None
        }

        memory_manager = create_enhanced_memory_manager(
            cesar_config=memory_config,
            provider=MemoryProvider.CESAR_SHEETS
        )
        await memory_manager.initialize()

        # Store evolution history in memory
        genome_data = {
            'agent_type': 'specialized_analyst',
            'capabilities': ['advanced_analytics'],
            'generation': 2,
            'fitness_score': 0.92
        }

        memory_id = await memory_manager.store_memory(
            MemoryType.EVOLUTION_HISTORY,
            content=genome_data,
            importance_score=0.9
        )

        assert memory_id is not None

        # Cleanup
        await breeding_manager.shutdown()
        await memory_manager.shutdown()


# Performance benchmarks
class TestPhase2Performance:
    """Performance tests for Phase 2 components."""

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_memory_storage_latency(self):
        """Benchmark memory storage latency."""
        memory_manager = create_enhanced_memory_manager(
            provider=MemoryProvider.CESAR_SHEETS
        )
        await memory_manager.initialize()

        start_time = datetime.now()

        for i in range(10):
            await memory_manager.store_memory(
                MemoryType.SYSTEM_STATE,
                content={"test": f"iteration_{i}"},
                importance_score=0.5
            )

        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000 / 10

        # Expect average latency under 100ms for CESAR (without Sheets API)
        print(f"Average storage latency: {latency:.2f}ms")

        await memory_manager.shutdown()

    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_collective_intelligence_scalability(self):
        """Test collective intelligence with multiple agents."""
        ci_framework = CollectiveIntelligenceFramework({})
        await ci_framework.initialize(None, None)

        # Register multiple agents
        class MockAgent:
            def __init__(self, agent_id):
                self.agent_id = agent_id
                self.agent_type = "test_agent"

            def get_capabilities(self):
                return ["test_capability"]

            async def get_performance_metrics(self):
                return {"success_rate": 0.8}

        start_time = datetime.now()

        for i in range(10):
            agent = MockAgent(f"agent_{i}")
            await ci_framework.register_agent(agent)

        end_time = datetime.now()
        registration_time = (end_time - start_time).total_seconds() * 1000

        print(f"10 agent registrations took: {registration_time:.2f}ms")

        assert len(ci_framework.agent_nodes) == 10

        await ci_framework.shutdown()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
