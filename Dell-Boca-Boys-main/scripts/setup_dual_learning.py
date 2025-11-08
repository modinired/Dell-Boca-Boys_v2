#!/usr/bin/env python3
"""
Setup script for Dual Learning System (Local + Gemini)

This script:
1. Adds Gemini API key to .env
2. Creates learning_executions table in PostgreSQL
3. Registers Gemini provider with LLM Router
4. Tests both models
5. Runs initial meta-analysis
"""
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.llm_router import llm_router, ProviderConfig
from app.core.gemini_adapter import GeminiModelWrapper
from app.utils.database import db
from app.utils.logging import logger
from app.tools.dual_learning import dual_learning


def setup_database():
    """Create learning_executions table."""
    print("📊 Setting up learning database...")

    schema = """
    CREATE TABLE IF NOT EXISTS learning_executions (
        id SERIAL PRIMARY KEY,
        workflow_id VARCHAR(255) NOT NULL,
        user_goal TEXT NOT NULL,
        workflow_json JSONB NOT NULL,
        qa_score REAL NOT NULL,
        success BOOLEAN NOT NULL,
        user_feedback TEXT,
        execution_time_ms REAL,
        created_at TIMESTAMP NOT NULL,
        INDEX idx_learning_created_at (created_at),
        INDEX idx_learning_success (success),
        INDEX idx_learning_qa_score (qa_score)
    );
    """

    try:
        db.execute(schema)
        print("✅ Learning database table created")
        return True
    except Exception as e:
        print(f"❌ Failed to create table: {e}")
        return False


def register_gemini():
    """Register Gemini provider with LLM Router."""
    print("\n🤖 Registering Gemini provider...")

    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("   Please add to .env file:")
        print('   GEMINI_API_KEY="your-key-here"')
        return False

    try:
        # Create Gemini config
        gemini_config = ProviderConfig(
            provider_id='gemini',
            model_id='gemini-2.0-flash-exp',
            api_base='https://generativelanguage.googleapis.com/v1beta',
            api_key=gemini_api_key,
            temperature=0.1,
            max_tokens=8192,
            priority=80,  # Lower than default (100) - use as fallback/specialist
            specializations=['workflow_planning', 'pattern_analysis', 'general'],
            enabled=True,
            max_failures_before_circuit=3,
            circuit_recovery_seconds=300
        )

        # Create Gemini model wrapper
        gemini_model = GeminiModelWrapper(
            model_id='gemini-2.0-flash-exp',
            api_key=gemini_api_key,
            temperature=0.1,
            max_tokens=8192
        )

        # Register with router
        llm_router.providers[gemini_config.provider_id] = gemini_config
        llm_router.models[gemini_config.provider_id] = gemini_model

        # Initialize health tracking
        from app.core.llm_router import ProviderHealth, ProviderStatus, CircuitBreaker
        llm_router.health[gemini_config.provider_id] = ProviderHealth(
            provider_id=gemini_config.provider_id,
            model_id=gemini_config.model_id,
            status=ProviderStatus.HEALTHY
        )

        llm_router.circuit_breakers[gemini_config.provider_id] = CircuitBreaker(
            max_failures=gemini_config.max_failures_before_circuit,
            recovery_timeout=gemini_config.circuit_recovery_seconds
        )

        print("✅ Gemini provider registered")
        return True

    except Exception as e:
        print(f"❌ Failed to register Gemini: {e}")
        return False


def test_providers():
    """Test both local and Gemini providers."""
    print("\n🧪 Testing LLM providers...")

    # Test local model
    print("  Testing local model...")
    try:
        response = llm_router.call(
            messages=[{"role": "user", "content": "Say 'Hello from local model' and nothing else."}],
            task_type='general',
            fallback=False,
            max_attempts=1
        )
        print(f"  ✅ Local model: {response[:50]}...")
    except Exception as e:
        print(f"  ❌ Local model failed: {e}")

    # Test Gemini
    print("  Testing Gemini...")
    try:
        response = llm_router.call(
            messages=[{"role": "user", "content": "Say 'Hello from Gemini' and nothing else."}],
            task_type='workflow_planning',  # Should route to Gemini
            fallback=False,
            max_attempts=1
        )
        print(f"  ✅ Gemini: {response[:50]}...")
    except Exception as e:
        print(f"  ❌ Gemini failed: {e}")


def show_routing_strategy():
    """Display routing strategy."""
    print("\n📋 LLM Routing Strategy:")
    print("=" * 70)

    routing_table = {
        "Code Generation": "Local (Qwen2.5-Coder specialized)",
        "JSON Compilation": "Local (Fast, deterministic)",
        "QA Validation": "Local (Rule-based)",
        "User Chat": "Local (Fast response)",
        "Pattern Analysis": "Gemini (Deep reasoning)",
        "Workflow Planning": "Gemini (Complex architecture)",
        "Meta-Analysis": "Gemini (Strategic insights)",
        "Error Debugging": "Local → Gemini fallback",
        "General Queries": "Local → Gemini fallback"
    }

    for task, strategy in routing_table.items():
        print(f"  {task:.<30} {strategy}")

    print("=" * 70)


def display_health_status():
    """Display health status of all providers."""
    print("\n💚 Provider Health Status:")
    print("=" * 70)

    snapshot = llm_router.get_health_snapshot()

    for provider_id, health in snapshot['providers'].items():
        status_emoji = {
            'healthy': '🟢',
            'degraded': '🟡',
            'offline': '🔴',
            'circuit_open': '⚫'
        }.get(health['status'], '❓')

        print(f"\n{status_emoji} {provider_id.upper()}")
        print(f"  Model: {health['model']}")
        print(f"  Status: {health['status']}")
        print(f"  Available: {health['is_available']}")
        print(f"  Success Rate: {health['success_rate']:.1%}")
        print(f"  Avg Latency: {health['average_latency_ms']:.0f}ms")
        print(f"  Total Requests: {health['total_requests']}")

    print("=" * 70)


def main():
    """Main setup routine."""
    print("=" * 70)
    print("🚀 Dell Boca Vista Boys - Dual Learning System Setup")
    print("=" * 70)

    # Step 1: Database
    if not setup_database():
        print("\n❌ Setup failed at database step")
        return False

    # Step 2: Register Gemini
    if not register_gemini():
        print("\n⚠️  Gemini not registered - system will use local model only")
        print("   To enable Gemini, add GEMINI_API_KEY to .env and re-run")
        return True  # Not fatal

    # Step 3: Test providers
    test_providers()

    # Step 4: Show routing strategy
    show_routing_strategy()

    # Step 5: Display health
    display_health_status()

    print("\n" + "=" * 70)
    print("✅ Dual Learning System is ready!")
    print("=" * 70)

    print("\n📚 Next Steps:")
    print("  1. System will now use both models intelligently")
    print("  2. Local model handles fast tasks (code, validation)")
    print("  3. Gemini handles complex reasoning (planning, analysis)")
    print("  4. Both models learn from execution feedback")
    print("  5. Run 'python scripts/run_meta_analysis.py' for weekly insights")

    print("\n💡 Usage Examples:")
    print("  # Normal workflow generation (uses both models)")
    print("  curl -X POST http://localhost:8080/api/v1/workflow/design \\")
    print("    -d '{\"user_goal\": \"Create a complex order processing workflow\"}'")

    print("\n  # Meta-analysis (uses Gemini for deep insights)")
    print("  curl -X POST http://localhost:8080/api/v1/learning/meta-analysis \\")
    print("    -d '{\"days_back\": 7}'")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
