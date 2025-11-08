"""
Example: Using Vito REST API
"""

import requests
import json

# Vito API base URL
BASE_URL = "http://localhost:8080"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    print()


def test_chat():
    """Test chat endpoint"""
    print("Testing chat endpoint...")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "What are Python list comprehensions?",
            "include_context": True
        }
    )

    result = response.json()
    print(f"Response: {result['response']}")
    print(f"Timestamp: {result['timestamp']}")
    print()


def test_generate():
    """Test code generation"""
    print("Testing code generation...")

    response = requests.post(
        f"{BASE_URL}/generate",
        json={
            "description": "Binary search implementation",
            "language": "python",
            "style": "clean and well-documented"
        }
    )

    result = response.json()
    print("Generated code:")
    print(result['code'])
    print()


def test_review():
    """Test code review"""
    print("Testing code review...")

    code = """
def calc(x,y):
    return x+y
"""

    response = requests.post(
        f"{BASE_URL}/review",
        json={
            "code": code,
            "language": "python",
            "focus": "best practices"
        }
    )

    result = response.json()
    print("Review:")
    print(result['review'])
    print()


def test_explain():
    """Test code explanation"""
    print("Testing code explanation...")

    code = """
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

    response = requests.post(
        f"{BASE_URL}/explain",
        json={
            "code": code,
            "language": "python",
            "level": "detailed"
        }
    )

    result = response.json()
    print("Explanation:")
    print(result['explanation'])
    print()


def main():
    """Run all examples"""

    print("=" * 70)
    print("Vito API Examples")
    print("=" * 70)
    print()

    print("Make sure Vito API server is running:")
    print("  ./vito serve")
    print()

    try:
        test_health()
        test_chat()
        test_generate()
        test_review()
        test_explain()

        print("=" * 70)
        print("All examples completed!")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to Vito API")
        print("Make sure the API server is running: ./vito serve")


if __name__ == "__main__":
    main()
