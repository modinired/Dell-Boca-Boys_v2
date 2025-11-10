#!/usr/bin/env python3
"""
Spedines Agent - Setup Script
Helps you configure and deploy Spedines for the first time
"""

import os
import sys
from pathlib import Path
import subprocess


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False

    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✅ .env file found")
        return True

    print("⚠️  .env file not found")

    if not env_example.exists():
        print("❌ .env.example not found - cannot create template")
        return False

    print("\nWould you like to create a minimal .env file for testing?")
    print("(You can configure it properly later)")

    response = input("Create .env? (y/n): ").strip().lower()

    if response == 'y':
        create_minimal_env()
        return True

    return False


def create_minimal_env():
    """Create minimal .env file for testing"""
    print("\nCreating minimal .env configuration...")

    # Minimal config for local-only mode
    env_content = """# Spedines Agent Configuration - Minimal Setup
# This is a minimal configuration for testing. See .env.example for full options.

# === REQUIRED: LLM Configuration ===
# Local Qwen (via Ollama/vLLM) - Required
QWEN_ENDPOINT=http://localhost:11434/v1
QWEN_MODEL=qwen2.5-coder:32b

# Gemini (optional - leave empty for local-only mode)
GEMINI_API_KEY=

# Routing strategy: draft_polish, local_only, gemini_only, complexity_based
ROUTING_STRATEGY=local_only

# === Memory System ===
ENABLE_MEMORY=true
CHROMA_DB_PATH=./data/chromadb

# === Google Cloud (Optional) ===
ENABLE_SHEETS_LOGGING=false
ENABLE_DRIVE_INGESTION=false

# === Logging ===
LOG_LEVEL=INFO
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("✅ Created .env file with minimal configuration")
    print("\n⚠️  Note: This is configured for LOCAL-ONLY mode")
    print("   - Requires Ollama with qwen2.5-coder:32b")
    print("   - No Gemini API key needed")
    print("   - Google features disabled")


def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running")

            # Check for qwen model
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]

            if any("qwen2.5-coder" in m for m in models):
                print("✅ Qwen 2.5 Coder model found")
            else:
                print("⚠️  Qwen 2.5 Coder model not found")
                print("   Run: ollama pull qwen2.5-coder:32b")

            return True
    except Exception as e:
        print("⚠️  Ollama not detected (optional for local mode)")
        print("   Install: https://ollama.ai")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True
        )
        print("✅ Dependencies installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\nTry manually:")
        print(f"  {sys.executable} -m pip install -r requirements.txt")
        return False


def test_import():
    """Test if spedines can be imported"""
    try:
        import spedines
        print("✅ Spedines package can be imported")
        return True
    except ImportError as e:
        print(f"⚠️  Cannot import spedines: {e}")
        return False


def main():
    """Main setup routine"""
    print_header("Little Jim Spedines - Setup & Deployment")

    # Change to spedines_agent directory
    script_dir = Path(__file__).parent
    spedines_dir = script_dir.parent
    os.chdir(spedines_dir)

    print(f"Working directory: {spedines_dir}")

    # Step 1: Check Python version
    print_header("Step 1: Checking Python Version")
    if not check_python_version():
        sys.exit(1)

    # Step 2: Check/create .env file
    print_header("Step 2: Configuration File")
    if not check_env_file():
        print("\n❌ Setup cannot continue without .env file")
        print("\nPlease either:")
        print("  1. Run this script again and choose 'y' to create .env")
        print("  2. Manually copy .env.example to .env and configure it")
        sys.exit(1)

    # Step 3: Check Ollama (optional)
    print_header("Step 3: Checking Local LLM (Optional)")
    check_ollama()

    # Step 4: Install dependencies
    print_header("Step 4: Installing Dependencies")

    print("Would you like to install Python dependencies now?")
    response = input("Install dependencies? (y/n): ").strip().lower()

    if response == 'y':
        if not install_dependencies():
            print("\n⚠️  Continuing anyway...")
    else:
        print("\n⚠️  Skipping dependency installation")
        print("   You'll need to install manually later:")
        print(f"   {sys.executable} -m pip install -r requirements.txt")

    # Step 5: Test import
    print_header("Step 5: Testing Installation")
    test_import()

    # Final instructions
    print_header("Setup Complete!")

    print("✅ Spedines is ready to use!\n")

    print("Next steps:\n")
    print("1. Start Ollama (if using local mode):")
    print("   ollama serve")
    print("   ollama pull qwen2.5-coder:32b")
    print()
    print("2. Run Spedines CLI:")
    print("   python -m spedines.cli")
    print()
    print("3. Or run examples:")
    print("   python scripts/example_usage.py")
    print()
    print("4. Configure .env for production:")
    print("   - Add Gemini API key for cloud features")
    print("   - Add Google Cloud credentials for Sheets/Drive")
    print("   - See .env.example for all options")
    print()
    print("📚 Documentation: See README.md for full usage guide")
    print()


if __name__ == "__main__":
    main()
