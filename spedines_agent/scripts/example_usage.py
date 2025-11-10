#!/usr/bin/env python3
"""
Example usage of Spedines agent
Demonstrates basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from spedines.agent import create_spedines_agent
from spedines.llm.prompts import PromptTemplate


async def basic_query_example():
    """Example: Basic query"""

    print("\n" + "="*60)
    print("Example 1: Basic Query")
    print("="*60 + "\n")

    # Create agent (reads from .env file)
    agent = create_spedines_agent()

    # Simple query
    response = await agent.query(
        "What are the key principles of good software architecture?"
    )

    print(f"Question: What are the key principles of good software architecture?")
    print(f"\nSpedines: {response.response}")
    print(f"\nMetadata:")
    print(f"  - Strategy: {response.routing_result.strategy}")
    print(f"  - Latency: {response.routing_result.metrics.total_latency_ms:.0f}ms")
    print(f"  - Memory results: {len(response.memory_context)}")


async def code_generation_example():
    """Example: Code generation"""

    print("\n" + "="*60)
    print("Example 2: Code Generation")
    print("="*60 + "\n")

    agent = create_spedines_agent()

    # Code generation request
    response = await agent.query(
        "Write a Python function to calculate the Fibonacci sequence up to n terms",
        template=PromptTemplate.CODE_GENERATION
    )

    print(f"Request: Write a Python function for Fibonacci sequence")
    print(f"\nSpedines: {response.response}")


async def memory_example():
    """Example: Using memory"""

    print("\n" + "="*60)
    print("Example 3: Memory and Knowledge")
    print("="*60 + "\n")

    agent = create_spedines_agent()

    # Add knowledge
    print("Adding knowledge to memory...")

    agent.add_knowledge(
        content="The Dell Boca Boys is a team of AI agents with distinct personalities: "
                "Face (leader), Vito (local expert), and Little Jim Spedines (hybrid agent).",
        source="manual",
        tags=["team", "agents"]
    )

    agent.add_knowledge(
        content="Little Jim Spedines uses a Draft-and-Polish approach with local Qwen "
                "drafting responses and Gemini polishing them for quality.",
        source="manual",
        tags=["spedines", "architecture"]
    )

    print("Knowledge added!\n")

    # Query using memory
    response = await agent.query(
        "Who are the Dell Boca Boys?"
    )

    print(f"Question: Who are the Dell Boca Boys?")
    print(f"\nSpedines: {response.response}")
    print(f"\nMemory context used: {len(response.memory_context)} memories")


async def search_memory_example():
    """Example: Searching memory"""

    print("\n" + "="*60)
    print("Example 4: Searching Memory")
    print("="*60 + "\n")

    agent = create_spedines_agent()

    # Search memory
    results = agent.search_memory(
        query="Draft-and-Polish",
        top_k=3
    )

    print(f"Searching memory for: 'Draft-and-Polish'")
    print(f"\nFound {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. [Similarity: {result['similarity']:.2f}]")
        print(f"   {result['content'][:150]}...")
        print()


async def health_check_example():
    """Example: Health check"""

    print("\n" + "="*60)
    print("Example 5: Health Check")
    print("="*60 + "\n")

    agent = create_spedines_agent()

    health = agent.health_check()

    print(f"Overall Status: {health['status'].upper()}\n")
    print("Components:")

    for component, status in health['components'].items():
        comp_status = status.get('status', 'unknown')
        print(f"  {component}: {comp_status}")


async def metrics_example():
    """Example: Metrics"""

    print("\n" + "="*60)
    print("Example 6: Metrics")
    print("="*60 + "\n")

    agent = create_spedines_agent()

    # Make a few queries first
    await agent.query("Hello!")
    await agent.query("What's 2+2?")

    # Get metrics
    metrics = agent.get_metrics()

    print("Agent Metrics:")
    print(f"  Total queries: {metrics['agent']['total_queries']}")
    print(f"  Success rate: {metrics['agent']['success_rate']:.1%}")

    print("\nLLM Metrics:")
    print(f"  Total requests: {metrics['llm']['total_requests']}")
    print(f"  Strategy counts: {metrics['llm']['strategy_counts']}")

    if 'memory' in metrics:
        print("\nMemory Metrics:")
        print(f"  Total memories: {metrics['memory']['store']['total_memories']}")


async def main():
    """Run all examples"""

    print("\n" + "="*60)
    print("Little Jim Spedines - Usage Examples")
    print("="*60)

    try:
        # Run examples
        await basic_query_example()
        await code_generation_example()
        await memory_example()
        await search_memory_example()
        await health_check_example()
        await metrics_example()

        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("\nError: .env file not found!")
        print("Please copy .env.example to .env and configure it.")
        sys.exit(1)

    # Run examples
    asyncio.run(main())
