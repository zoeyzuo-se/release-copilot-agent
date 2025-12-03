"""Example client for the Release Copilot API."""

import requests


class ReleaseCopilotClient:
    """Client for interacting with the Release Copilot API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> dict:
        """Check if the API is healthy."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def chat(self, message: str, conversation_id: str = None) -> dict:
        """
        Send a message to the chat endpoint.

        Args:
            message: The user's message/question
            conversation_id: Optional conversation ID for context

        Returns:
            Response dictionary with agent's reply
        """
        payload = {"message": message}
        if conversation_id:
            payload["conversation_id"] = conversation_id

        response = requests.post(
            f"{self.base_url}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    def get_examples(self) -> dict:
        """Get example queries."""
        response = requests.get(f"{self.base_url}/examples")
        response.raise_for_status()
        return response.json()


def main():
    """Run example interactions with the API."""

    # Create client
    client = ReleaseCopilotClient()

    # Check health
    print("Checking API health...")
    health = client.health_check()
    print(f"✓ API Status: {health['status']}")
    print()

    # Example 1: Check pipeline status
    print("=" * 60)
    print("Example 1: Checking pipeline status")
    print("=" * 60)

    response = client.chat(
        "What's the status of the payments service in prod?")
    print("\nUser: What's the status of the payments service in prod?")
    print(f"\nAssistant: {response['response']}")
    print()

    # Example 2: Analyze a failure
    print("=" * 60)
    print("Example 2: Analyzing a failed deployment")
    print("=" * 60)

    response = client.chat(
        "The checkout service failed in staging. What went wrong?")
    print("\nUser: The checkout service failed in staging. What went wrong?")
    print(f"\nAssistant: {response['response']}")
    print()

    # Example 3: Direct log analysis
    print("=" * 60)
    print("Example 3: Direct log analysis")
    print("=" * 60)

    response = client.chat("Can you check the logs for job-456?")
    print("\nUser: Can you check the logs for job-456?")
    print(f"\nAssistant: {response['response']}")
    print()

    # Get available examples
    print("=" * 60)
    print("Available Example Queries")
    print("=" * 60)

    examples = client.get_examples()
    for i, example in enumerate(examples['examples'], 1):
        print(f"\n{i}. {example['description']}")
        print(f"   Query: {example['query']}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("   Make sure the server is running: python src/rc_agent/app/api.py")
    except Exception as e:
        print(f"❌ Error: {e}")
