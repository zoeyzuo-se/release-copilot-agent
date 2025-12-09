"""
Agent runner to collect responses from test dataset for evaluation.

This script runs the agent against test queries and captures the tool calls
and responses for later evaluation.
"""

import json
from pathlib import Path
from typing import Any
from datetime import datetime
import asyncio

from rc_agent.agents.mcp_orchestrator import create_mcp_orchestrator


def load_test_queries(file_path: Path) -> list[dict[str, Any]]:
    """Load test queries from ground truth file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def extract_tool_calls_from_response(response) -> list[dict[str, Any]]:
    """
    Extract tool calls from agent response.

    The agent-framework returns an AgentRunResponse with messages.
    Tool calls are in message.contents with type 'function_call'.
    """
    tool_calls = []

    # The response has a messages attribute containing ChatMessage objects
    if hasattr(response, 'messages'):
        for message in response.messages:
            # Each message can have a 'contents' attribute
            if hasattr(message, 'contents'):
                for content in message.contents:
                    # Check if this content is a function call
                    # We can use to_dict() to inspect it
                    if hasattr(content, 'to_dict'):
                        content_dict = content.to_dict()
                        if content_dict.get('type') == 'function_call':
                            tool_info = {
                                'id': content_dict.get('call_id'),
                                'name': content_dict.get('name'),
                                'arguments': json.loads(content_dict.get('arguments', '{}'))
                            }
                            tool_calls.append(tool_info)

    return tool_calls


async def run_agent_collection():
    """
    Run agent against test queries and collect responses with tool calls.
    """
    print("=" * 80)
    print("Agent Response Collection for Evaluation")
    print("=" * 80)

    # Load test queries
    eval_dir = Path(__file__).parent
    ground_truth_file = eval_dir / "ground_truth.json"
    test_cases = load_test_queries(ground_truth_file)

    print(f"\nLoaded {len(test_cases)} test queries from {ground_truth_file}")

    # Create agent
    print("\nInitializing agent...")
    agent = create_mcp_orchestrator()
    print("Agent initialized successfully!")

    # Collect responses
    collected_data = []

    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Running Test Case {idx}/{len(test_cases)}")
        print(f"Query: {test_case['query']}")

        try:
            # Run the agent (it's async!)
            response = await agent.run(test_case['query'])

            # Extract tool calls
            tool_calls = extract_tool_calls_from_response(response)

            # Get response text
            response_text = str(response)

            print("\n✓ Agent completed successfully")
            print(f"Tool calls detected: {len(tool_calls)}")
            for tc in tool_calls:
                print(
                    f"  - {tc.get('name', 'unknown')}: {tc.get('arguments', {})}")

            # Store collected data
            collected_data.append({
                'test_case_id': idx,
                'query': test_case['query'],
                'expected_tools': test_case['expected_tools'],
                'expected_tool_args': test_case.get('expected_tool_args', {}),
                'actual_tool_calls': tool_calls,
                'response': response_text,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            print(f"\n❌ Error running agent: {e}")
            import traceback
            traceback.print_exc()

            collected_data.append({
                'test_case_id': idx,
                'query': test_case['query'],
                'expected_tools': test_case['expected_tools'],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })

    # Save collected data
    output_file = eval_dir / "collected_responses.json"
    with open(output_file, 'w') as f:
        json.dump(collected_data, f, indent=2)

    print(f"\n{'=' * 80}")
    print("Collection complete!")
    print(f"Collected {len(collected_data)} responses")
    print(f"Saved to: {output_file}")
    print(f"{'=' * 80}\n")

    return collected_data


if __name__ == "__main__":
    asyncio.run(run_agent_collection())
