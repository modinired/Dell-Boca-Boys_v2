"""
Utility Functions for Dell Boca Boys Agents

Common utilities used across the agent system.
"""

import json
import re
from typing import Dict, Any, Optional, List


def format_log_message(emoji: str, nickname: str, message: str) -> str:
    """
    Format a log message in the Dell Boca Boys style

    Args:
        emoji: Agent's emoji
        nickname: Agent's nickname
        message: Message to log

    Returns:
        Formatted log message
    """
    return f"{emoji} {nickname}: {message}"


def validate_workflow_json(workflow_json: Any) -> Dict[str, Any]:
    """
    Validate n8n workflow JSON

    Args:
        workflow_json: The workflow JSON to validate (string or dict)

    Returns:
        Dict with validation results
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": []
    }

    # Check if it's valid JSON
    try:
        if isinstance(workflow_json, str):
            parsed = json.loads(workflow_json)
        else:
            parsed = workflow_json
            # Ensure it can be serialized
            json.dumps(parsed)

        # Basic n8n workflow structure validation
        if not isinstance(parsed, dict):
            result["errors"].append("Workflow must be a JSON object")
            return result

        # Check for required fields
        if "nodes" not in parsed:
            result["errors"].append("Missing required field: nodes")

        if "connections" not in parsed:
            result["errors"].append("Missing required field: connections")

        if not isinstance(parsed.get("nodes"), list):
            result["errors"].append("nodes must be an array")

        if not isinstance(parsed.get("connections"), dict):
            result["warnings"].append("connections should be an object")

        # If no errors, it's valid
        if not result["errors"]:
            result["valid"] = True

    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON syntax: {str(e)}")

    except Exception as e:
        result["errors"].append(f"Validation error: {str(e)}")

    return result


def extract_code_from_response(response: str, language: str = "python") -> str:
    """
    Extract code from an LLM response that might contain markdown code blocks

    Args:
        response: The LLM response
        language: Expected language (python, javascript, etc.)

    Returns:
        Extracted code
    """
    # Try to find code blocks with language specifier
    pattern = f"```{language}\\s*\\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)

    if matches:
        return matches[0].strip()

    # Try generic code blocks
    pattern = r"```\s*\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)

    if matches:
        return matches[0].strip()

    # If no code blocks found, return the whole response
    return response.strip()


def sanitize_input(input_str: str, max_length: int = 10000) -> str:
    """
    Sanitize user input for security

    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    # Truncate to max length
    sanitized = input_str[:max_length]

    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")

    return sanitized


def parse_specialist_request(message: str) -> Dict[str, Any]:
    """
    Parse a user message to determine which specialist might be needed

    Args:
        message: User's message

    Returns:
        Dict with parsing results
    """
    message_lower = message.lower()

    result = {
        "keywords": [],
        "suggested_specialists": [],
        "task_type": "general"
    }

    # Keyword detection
    keyword_map = {
        "pattern_analyst": ["pattern", "best practice", "anti-pattern", "architecture", "review"],
        "crawler": ["template", "search", "find", "example", "documentation"],
        "qa_fighter": ["validate", "test", "check", "verify", "qa", "quality"],
        "flow_planner": ["design", "plan", "architect", "structure", "flow"],
        "deploy_capo": ["deploy", "production", "staging", "credentials", "security"],
        "json_compiler": ["json", "compile", "generate workflow", "create workflow"],
        "code_generator": ["code", "python", "javascript", "function", "script"]
    }

    for specialist, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in message_lower:
                if keyword not in result["keywords"]:
                    result["keywords"].append(keyword)
                if specialist not in result["suggested_specialists"]:
                    result["suggested_specialists"].append(specialist)

    # Determine task type
    if any(word in message_lower for word in ["create workflow", "build workflow", "new workflow"]):
        result["task_type"] = "workflow_creation"
    elif any(word in message_lower for word in ["code", "function", "script"]):
        result["task_type"] = "code_generation"
    elif any(word in message_lower for word in ["search", "find", "template"]):
        result["task_type"] = "template_search"
    elif any(word in message_lower for word in ["validate", "test", "check"]):
        result["task_type"] = "validation"
    elif any(word in message_lower for word in ["deploy", "production"]):
        result["task_type"] = "deployment"

    return result


def estimate_complexity(requirements: str) -> str:
    """
    Estimate complexity of a request

    Args:
        requirements: The requirements/request

    Returns:
        Complexity level: "simple", "moderate", "complex"
    """
    word_count = len(requirements.split())
    req_lower = requirements.lower()

    # Simple indicators
    if word_count < 20 and any(word in req_lower for word in ["simple", "basic", "quick"]):
        return "simple"

    # Complex indicators
    complex_keywords = [
        "multiple", "complex", "advanced", "integrate", "comprehensive",
        "error handling", "scalable", "production", "enterprise"
    ]

    if word_count > 50 or any(keyword in req_lower for keyword in complex_keywords):
        return "complex"

    return "moderate"


def generate_task_id() -> str:
    """
    Generate a unique task ID

    Returns:
        Unique task ID string
    """
    from datetime import datetime
    import random
    import string

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    return f"TASK-{timestamp}-{random_suffix}"
