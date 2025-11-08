#!/usr/bin/env python3
"""
Vito CLI - Command-line interface for local coding agent

Usage:
    vito chat                    # Interactive chat mode
    vito generate <description>  # Generate code
    vito review <file>           # Review code file
    vito explain <file>          # Explain code file
    vito refactor <file>         # Refactor code file
    vito debug <file>            # Debug code file
    vito analyze <file|dir>      # Analyze file or project
    vito serve                   # Start API server
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional
import argparse

# Add vito package to path
sys.path.insert(0, str(Path(__file__).parent))

from vito import VitoAgent, Config
from vito.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class VitoCLI:
    """CLI interface for Vito agent"""

    def __init__(self):
        """Initialize CLI"""
        self.config = get_config()
        self.agent = None

    def _init_agent(self):
        """Lazy initialize agent"""
        if self.agent is None:
            print("🎩 Vito: Initializing... (connecting to Qwen)")
            try:
                self.agent = VitoAgent()
                print("✓ Ready!")
            except Exception as e:
                print(f"❌ Error initializing Vito: {e}")
                print("\nMake sure Qwen 2.5 Coder is running locally!")
                print(f"Expected endpoint: {self.config.qwen_endpoint}")
                sys.exit(1)

    def chat(self):
        """Interactive chat mode"""
        self._init_agent()

        print("\n" + "="*60)
        print("🎩 Vito Italian (Diet Bocca) - Local Coding Expert")
        print("="*60)
        print("Type your coding questions or requests.")
        print("Commands: /exit, /help, /stats, /clear")
        print("="*60 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if user_input == "/exit":
                        print("👋 Vito: Take care!")
                        break
                    elif user_input == "/help":
                        self._print_help()
                        continue
                    elif user_input == "/stats":
                        self._print_stats()
                        continue
                    elif user_input == "/clear":
                        os.system('clear' if os.name != 'nt' else 'cls')
                        continue
                    else:
                        print(f"Unknown command: {user_input}")
                        continue

                # Get response from Vito
                print("\n🎩 Vito: ", end="", flush=True)

                if self.config.streaming:
                    # Stream response
                    for chunk in self.agent.chat(user_input, stream=True):
                        print(chunk, end="", flush=True)
                    print("\n")
                else:
                    # Non-streaming
                    response = self.agent.chat(user_input, stream=False)
                    print(response + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Vito: Take care!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                logger.exception("Chat error")

    def generate(self, description: str, language: str = "python"):
        """Generate code"""
        self._init_agent()

        print(f"\n🎩 Vito: Generating {language} code...\n")

        code = self.agent.generate_code(
            description=description,
            language=language
        )

        print("="*60)
        print(f"Generated {language} code:")
        print("="*60)
        print(code)
        print("="*60)

    def review(self, file_path: str):
        """Review code file"""
        self._init_agent()

        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return

        print(f"\n🎩 Vito: Reviewing {file_path}...\n")

        # Read file
        with open(path, 'r') as f:
            code = f.read()

        # Detect language
        from vito.code_tools import detect_language_from_file
        language = detect_language_from_file(file_path)

        # Review
        review = self.agent.review_code(code, language)

        print("="*60)
        print(f"Code Review: {file_path}")
        print("="*60)
        print(review)
        print("="*60)

    def explain(self, file_path: str, level: str = "detailed"):
        """Explain code file"""
        self._init_agent()

        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return

        print(f"\n🎩 Vito: Explaining {file_path}...\n")

        # Read file
        with open(path, 'r') as f:
            code = f.read()

        # Detect language
        from vito.code_tools import detect_language_from_file
        language = detect_language_from_file(file_path)

        # Explain
        explanation = self.agent.explain_code(code, language, level)

        print("="*60)
        print(f"Code Explanation: {file_path}")
        print("="*60)
        print(explanation)
        print("="*60)

    def refactor(self, file_path: str, goal: str = "improve readability and maintainability"):
        """Refactor code file"""
        self._init_agent()

        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return

        print(f"\n🎩 Vito: Refactoring {file_path}...\n")

        # Read file
        with open(path, 'r') as f:
            code = f.read()

        # Detect language
        from vito.code_tools import detect_language_from_file
        language = detect_language_from_file(file_path)

        # Refactor
        result = self.agent.refactor_code(code, language, goal)

        print("="*60)
        print(f"Refactored Code: {file_path}")
        print("="*60)
        print(result)
        print("="*60)

    def debug(self, file_path: str, error: Optional[str] = None):
        """Debug code file"""
        self._init_agent()

        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return

        print(f"\n🎩 Vito: Debugging {file_path}...\n")

        # Read file
        with open(path, 'r') as f:
            code = f.read()

        # Detect language
        from vito.code_tools import detect_language_from_file
        language = detect_language_from_file(file_path)

        # Debug
        result = self.agent.debug_code(code, language, error)

        print("="*60)
        print(f"Debug Analysis: {file_path}")
        print("="*60)
        print(result)
        print("="*60)

    def analyze(self, path: str):
        """Analyze file or project"""
        self._init_agent()

        target = Path(path)
        if not target.exists():
            print(f"❌ Path not found: {path}")
            return

        print(f"\n🎩 Vito: Analyzing {path}...\n")

        if target.is_file():
            # Analyze single file
            analysis = self.agent.analyze_file(str(target))
        else:
            # Analyze project
            analysis = self.agent.analyze_project(str(target))

        print("="*60)
        print(f"Analysis: {path}")
        print("="*60)
        import json
        print(json.dumps(analysis, indent=2))
        print("="*60)

    def serve(self, host: str = "0.0.0.0", port: int = 8080):
        """Start API server"""
        print(f"\n🎩 Vito: Starting API server on {host}:{port}...")
        print("Press Ctrl+C to stop\n")

        # Import and run API
        from api import app
        import uvicorn

        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )

    def _print_help(self):
        """Print help message"""
        print("""
Available commands:
  /help   - Show this help
  /stats  - Show agent statistics
  /clear  - Clear screen
  /exit   - Exit chat

For code questions, just type naturally:
  - "Generate a FastAPI endpoint for user authentication"
  - "Review this function for performance issues"
  - "Explain how decorators work in Python"
""")

    def _print_stats(self):
        """Print agent statistics"""
        stats = self.agent.get_stats()
        print("\n" + "="*60)
        print("Agent Statistics")
        print("="*60)
        for key, value in stats.items():
            print(f"{key}: {value}")
        print("="*60 + "\n")


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description="Vito - Local AI Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Chat command
    subparsers.add_parser("chat", help="Interactive chat mode")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate code")
    gen_parser.add_argument("description", help="What to generate")
    gen_parser.add_argument("--language", "-l", default="python", help="Programming language")

    # Review command
    review_parser = subparsers.add_parser("review", help="Review code file")
    review_parser.add_argument("file", help="File to review")

    # Explain command
    explain_parser = subparsers.add_parser("explain", help="Explain code file")
    explain_parser.add_argument("file", help="File to explain")
    explain_parser.add_argument("--level", choices=["brief", "detailed", "comprehensive"], default="detailed")

    # Refactor command
    refactor_parser = subparsers.add_parser("refactor", help="Refactor code file")
    refactor_parser.add_argument("file", help="File to refactor")
    refactor_parser.add_argument("--goal", default="improve readability and maintainability")

    # Debug command
    debug_parser = subparsers.add_parser("debug", help="Debug code file")
    debug_parser.add_argument("file", help="File to debug")
    debug_parser.add_argument("--error", help="Error message")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze file or project")
    analyze_parser.add_argument("path", help="File or directory to analyze")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8080)

    args = parser.parse_args()

    # Create CLI instance
    cli = VitoCLI()

    # Execute command
    if args.command == "chat" or args.command is None:
        cli.chat()
    elif args.command == "generate":
        cli.generate(args.description, args.language)
    elif args.command == "review":
        cli.review(args.file)
    elif args.command == "explain":
        cli.explain(args.file, args.level)
    elif args.command == "refactor":
        cli.refactor(args.file, args.goal)
    elif args.command == "debug":
        cli.debug(args.file, args.error)
    elif args.command == "analyze":
        cli.analyze(args.path)
    elif args.command == "serve":
        cli.serve(args.host, args.port)


if __name__ == "__main__":
    main()
