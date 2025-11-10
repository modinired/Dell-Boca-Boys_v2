"""
Spedines CLI - Simple command-line interface for Spedines agent
"""

import asyncio
import logging
from pathlib import Path
import sys

from .agent import create_spedines_agent, AgentError
from .llm.prompts import PromptTemplate

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SpedinesCLI:
    """Simple CLI for Spedines agent"""

    def __init__(self, env_file: str = ".env"):
        """
        Initialize CLI

        Args:
            env_file: Path to .env file
        """
        logger.info("Starting Little Jim Spedines...")

        try:
            self.agent = create_spedines_agent(env_file=env_file)
            logger.info("Spedines agent ready!")

        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    async def chat_loop(self):
        """Interactive chat loop"""

        print("\n" + "=" * 60)
        print("Little Jim Spedines - AI Assistant")
        print("=" * 60)
        print("\nCommands:")
        print("  /help     - Show help")
        print("  /health   - Check system health")
        print("  /metrics  - Show metrics")
        print("  /search <query> - Search memory")
        print("  /quit     - Exit")
        print("\n" + "=" * 60 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                    continue

                # Process query
                print("\nSpedines: ", end="", flush=True)

                response = await self.agent.query(user_input)

                print(response.response)
                print()

                # Show metrics if verbose
                if response.metadata.get("memory_results_count", 0) > 0:
                    print(f"  [Retrieved {response.metadata['memory_results_count']} memories]")

                print(f"  [LLM: {response.routing_result.strategy}, "
                      f"Latency: {response.routing_result.metrics.total_latency_ms:.0f}ms"
                      f"{f', Cost: ${response.routing_result.metrics.total_cost_usd:.6f}' if response.routing_result.metrics.total_cost_usd > 0 else ''}]")
                print()

            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break

            except AgentError as e:
                print(f"\n\nError: {e}\n")

            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                print(f"\n\nUnexpected error: {e}\n")

        print("\nGoodbye!")

    async def _handle_command(self, command: str):
        """Handle CLI commands"""

        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "/help":
            print("\nAvailable commands:")
            print("  /help               - Show this help")
            print("  /health             - Check system health")
            print("  /metrics            - Show usage metrics")
            print("  /search <query>     - Search memory")
            print("  /quit               - Exit\n")

        elif cmd == "/health":
            print("\nChecking system health...")
            health = self.agent.health_check()

            print(f"\nOverall Status: {health['status'].upper()}")
            print("\nComponents:")

            for component, status in health['components'].items():
                comp_status = status.get('status', 'unknown')
                print(f"  - {component}: {comp_status}")

                if comp_status == 'unhealthy' and 'error' in status:
                    print(f"    Error: {status['error']}")

            print()

        elif cmd == "/metrics":
            print("\nAgent Metrics:")
            metrics = self.agent.get_metrics()

            # Agent metrics
            agent_metrics = metrics['agent']
            print(f"\nQueries:")
            print(f"  Total: {agent_metrics['total_queries']}")
            print(f"  Successful: {agent_metrics['successful_queries']}")
            print(f"  Failed: {agent_metrics['failed_queries']}")
            print(f"  Success Rate: {agent_metrics['success_rate']:.1%}")

            # LLM metrics
            if 'llm' in metrics:
                llm_metrics = metrics['llm']
                print(f"\nLLM:")
                print(f"  Total Requests: {llm_metrics['total_requests']}")
                print(f"  Strategy Counts: {llm_metrics['strategy_counts']}")

            # Memory metrics
            if 'memory' in metrics:
                memory_metrics = metrics['memory']
                print(f"\nMemory:")
                print(f"  Total Memories: {memory_metrics['store']['total_memories']}")
                print(f"  Total Retrievals: {memory_metrics['retriever']['total_retrievals']}")

            print()

        elif cmd == "/search":
            if not args:
                print("\nUsage: /search <query>\n")
                return

            print(f"\nSearching memory for: {args}")

            results = self.agent.search_memory(args, top_k=5)

            if not results:
                print("No results found.\n")
                return

            print(f"\nFound {len(results)} results:\n")

            for i, result in enumerate(results, 1):
                print(f"{i}. [Similarity: {result['similarity']:.2f}]")
                print(f"   {result['content'][:200]}...")
                print(f"   Source: {result['metadata'].get('source', 'unknown')}")
                print()

        elif cmd == "/quit":
            print("\nExiting...")
            sys.exit(0)

        else:
            print(f"\nUnknown command: {cmd}")
            print("Type /help for available commands\n")

    async def single_query(self, query: str):
        """Process a single query and exit"""

        print(f"\nQuery: {query}\n")

        response = await self.agent.query(query)

        print(f"Spedines: {response.response}\n")

        # Show metadata
        print(f"Strategy: {response.routing_result.strategy}")
        print(f"Latency: {response.routing_result.metrics.total_latency_ms:.0f}ms")

        if response.routing_result.metrics.total_cost_usd > 0:
            print(f"Cost: ${response.routing_result.metrics.total_cost_usd:.6f}")

        print()


def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description="Little Jim Spedines CLI")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        "--query",
        help="Single query to process (non-interactive)"
    )

    args = parser.parse_args()

    # Check if env file exists
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: Environment file not found: {args.env_file}")
        print("\nPlease create a .env file with your configuration.")
        print("See .env.example for a template.")
        sys.exit(1)

    # Create CLI
    try:
        cli = SpedinesCLI(env_file=args.env_file)

    except Exception as e:
        print(f"Failed to initialize Spedines: {e}")
        sys.exit(1)

    # Run
    try:
        if args.query:
            # Single query mode
            asyncio.run(cli.single_query(args.query))
        else:
            # Interactive mode
            asyncio.run(cli.chat_loop())

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
