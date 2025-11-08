#!/usr/bin/env python3
"""
Verification script for Terry Integration.

Checks that all components are properly integrated and functional.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Verify all new modules can be imported."""
    print("=" * 70)
    print("CHECKING IMPORTS")
    print("=" * 70)

    modules = [
        ('app.bridges.terry_bridge', 'TerryBridge'),
        ('app.core.llm_router', 'LLMRouter'),
        ('app.core.health_monitor', 'HealthMonitor'),
        ('app.crew.code_generator_agent', 'CodeGeneratorAgent'),
        ('app.tools.code_executor', 'execute_python_code'),
    ]

    all_passed = True

    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            obj = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")
            all_passed = False

    return all_passed


def check_terry_bridge():
    """Test basic Terry Bridge functionality."""
    print("\n" + "=" * 70)
    print("TESTING TERRY BRIDGE")
    print("=" * 70)

    try:
        from app.bridges.terry_bridge import terry_bridge

        # Test simple execution
        result = terry_bridge.execute_python_code("result = 2 + 2")
        assert result['success'], "Execution failed"
        assert result['result'] == 4, f"Expected 4, got {result['result']}"
        print("✅ Simple execution: PASS")

        # Test security validation
        try:
            terry_bridge.execute_python_code("import os")
            print("❌ Security validation: FAIL (should block dangerous imports)")
            return False
        except Exception:
            print("✅ Security validation: PASS")

        # Test syntax validation
        syntax_result = terry_bridge.validate_code_syntax("def foo(): return 42")
        assert syntax_result['valid'], "Valid code marked as invalid"
        print("✅ Syntax validation: PASS")

        # Test complexity analysis
        complexity = terry_bridge.analyze_code_complexity("x = 1\ny = 2\nresult = x + y")
        assert 'complexity_rating' in complexity, "Missing complexity rating"
        print("✅ Complexity analysis: PASS")

        return True

    except Exception as e:
        print(f"❌ Terry Bridge test failed: {e}")
        return False


def check_llm_router():
    """Test LLM Router functionality."""
    print("\n" + "=" * 70)
    print("TESTING LLM ROUTER")
    print("=" * 70)

    try:
        from app.core.llm_router import llm_router

        # Stop background threads for testing
        llm_router.stop_health_monitoring()

        # Check default provider exists
        assert 'default' in llm_router.providers, "Default provider missing"
        print("✅ Default provider registered: PASS")

        # Check provider selection
        selected = llm_router.select_provider(task_type='general')
        assert selected is not None, "No provider selected"
        print(f"✅ Provider selection: PASS (selected: {selected})")

        # Check health snapshot
        snapshot = llm_router.get_health_snapshot()
        assert 'timestamp' in snapshot, "Invalid health snapshot"
        assert 'providers' in snapshot, "Missing providers in snapshot"
        print("✅ Health snapshot: PASS")

        return True

    except Exception as e:
        print(f"❌ LLM Router test failed: {e}")
        return False


def check_health_monitor():
    """Test Health Monitor functionality."""
    print("\n" + "=" * 70)
    print("TESTING HEALTH MONITOR")
    print("=" * 70)

    try:
        from app.core.health_monitor import health_monitor

        # Stop background threads
        health_monitor.stop_monitoring()

        # Check services initialized
        assert 'postgres' in health_monitor.health, "Postgres health tracking missing"
        assert 'llm_provider' in health_monitor.health, "LLM provider tracking missing"
        print("✅ Service tracking initialized: PASS")

        # Check health snapshot
        snapshot = health_monitor.get_health_snapshot()
        assert 'timestamp' in snapshot, "Invalid health snapshot"
        assert 'services' in snapshot, "Missing services in snapshot"
        assert 'overall_status' in snapshot, "Missing overall status"
        print("✅ Health snapshot: PASS")

        return True

    except Exception as e:
        print(f"❌ Health Monitor test failed: {e}")
        return False


def check_code_generator():
    """Test Code Generator Agent functionality."""
    print("\n" + "=" * 70)
    print("TESTING CODE GENERATOR AGENT")
    print("=" * 70)

    try:
        from app.crew.code_generator_agent import code_generator_agent

        # Check agent initialized
        assert code_generator_agent.name == "Code Generator Agent", "Wrong agent name"
        print("✅ Agent initialization: PASS")

        # Check code extraction
        code = code_generator_agent._extract_code_from_response("```python\nx = 1\n```")
        assert "x = 1" in code, "Code extraction failed"
        assert "```" not in code, "Markdown markers not removed"
        print("✅ Code extraction: PASS")

        # Check node name generation
        name = code_generator_agent._generate_node_name("Transform customer data")
        assert len(name) > 0, "Empty node name"
        assert len(name) <= 30, "Node name too long"
        print("✅ Node name generation: PASS")

        return True

    except Exception as e:
        print(f"❌ Code Generator test failed: {e}")
        return False


def check_face_agent_integration():
    """Test Face Agent integration."""
    print("\n" + "=" * 70)
    print("TESTING FACE AGENT INTEGRATION")
    print("=" * 70)

    try:
        from app.agent_face_chiccki import face_agent

        # Check code generator is in crew
        assert hasattr(face_agent, 'code_generator'), "Code generator not in Face Agent"
        print("✅ Code generator in crew: PASS")

        # Check all 7 agents present
        agents = [
            'crawler', 'pattern_analyst', 'flow_planner',
            'json_compiler', 'qa_fighter', 'deploy_capo',
            'code_generator'
        ]

        for agent_name in agents:
            assert hasattr(face_agent, agent_name), f"Missing agent: {agent_name}"

        print(f"✅ All 7 agents present: PASS")

        return True

    except Exception as e:
        print(f"❌ Face Agent integration test failed: {e}")
        return False


def check_files_exist():
    """Verify all expected files exist."""
    print("\n" + "=" * 70)
    print("CHECKING FILE STRUCTURE")
    print("=" * 70)

    base_dir = Path(__file__).parent.parent

    required_files = [
        'app/bridges/__init__.py',
        'app/bridges/terry_bridge.py',
        'app/core/__init__.py',
        'app/core/llm_router.py',
        'app/core/health_monitor.py',
        'app/crew/code_generator_agent.py',
        'app/tools/code_executor.py',
        'app/tests/test_terry_bridge.py',
        'app/tests/test_code_generator_agent.py',
        'app/tests/test_llm_router.py',
        'docs/CODE_GENERATION_INTEGRATION.md',
        'INTEGRATION_SUMMARY.md',
    ]

    all_exist = True

    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False

    return all_exist


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("N8N-AGENT TERRY INTEGRATION VERIFICATION")
    print("=" * 70)
    print()

    results = {
        'File Structure': check_files_exist(),
        'Imports': check_imports(),
        'Terry Bridge': check_terry_bridge(),
        'LLM Router': check_llm_router(),
        'Health Monitor': check_health_monitor(),
        'Code Generator': check_code_generator(),
        'Face Agent Integration': check_face_agent_integration(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<50} {status}")

    print()
    print(f"Total: {passed}/{total} checks passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Integration successful.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please review errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
