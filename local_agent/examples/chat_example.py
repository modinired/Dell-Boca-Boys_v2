"""
Example: Using Vito in chat mode programmatically
"""

from vito import VitoAgent

def main():
    # Create Vito agent
    print("Initializing Vito...")
    vito = VitoAgent()
    print("✓ Vito ready!\n")

    # Simple chat
    print("Example 1: Simple question")
    print("-" * 60)
    response = vito.chat("What are the best practices for Python error handling?")
    print(f"Vito: {response}\n")

    # Chat with streaming
    print("\nExample 2: Streaming response")
    print("-" * 60)
    print("Vito: ", end="", flush=True)
    for chunk in vito.chat(
        "Explain the differences between @staticmethod and @classmethod",
        stream=True
    ):
        print(chunk, end="", flush=True)
    print("\n")

    # Get agent stats
    print("\nAgent Statistics:")
    print("-" * 60)
    stats = vito.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
