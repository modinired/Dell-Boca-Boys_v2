"""
Example: Code generation with Vito
"""

from vito import VitoAgent

def main():
    vito = VitoAgent()

    # Example 1: Generate Python function
    print("Example 1: Generate Python function")
    print("=" * 70)

    code = vito.generate_code(
        description="""
        Create a Python function that implements a retry decorator with
        exponential backoff. It should:
        - Take max_retries and initial_delay parameters
        - Use exponential backoff (delay doubles each retry)
        - Include proper type hints
        - Handle exceptions properly
        - Log retry attempts
        """,
        language="python",
        style="modern Python with type hints"
    )

    print(code)
    print()

    # Example 2: Generate JavaScript async function
    print("\nExample 2: Generate JavaScript async function")
    print("=" * 70)

    code = vito.generate_code(
        description="""
        Create a JavaScript async function that fetches data from an API
        with rate limiting. It should:
        - Use fetch API
        - Implement rate limiting (max N requests per second)
        - Handle errors gracefully
        - Return typed results
        - Include JSDoc comments
        """,
        language="javascript",
        style="modern ES6+ with async/await"
    )

    print(code)
    print()

    # Example 3: Generate with context
    print("\nExample 3: Generate with project context")
    print("=" * 70)

    context = """
    Project uses:
    - FastAPI for REST API
    - SQLAlchemy for database
    - Pydantic for data validation
    - JWT for authentication
    """

    code = vito.generate_code(
        description="Create an endpoint for user registration",
        language="python",
        context=context,
        style="FastAPI best practices"
    )

    print(code)


if __name__ == "__main__":
    main()
