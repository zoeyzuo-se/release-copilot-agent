"""
Evaluation script for tool selection accuracy using AzureOpenAI evaluator.

This script evaluates how well the agent selects the correct tools based on user queries.
It uses Azure OpenAI's evaluation capabilities without requiring AI Projects SDK.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

from rc_agent.agents.mcp_orchestrator import create_mcp_orchestrator
from rc_agent.config.settings import settings

# Load environment variables
load_dotenv()


def load_ground_truth(file_path: Path) -> list[dict[str, Any]]:
    """Load ground truth test cases from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


async def run_agent_and_capture_tools(agent, query: str) -> dict[str, Any]:
    """
    Run the agent with a query and capture which tools were called.

    Args:
        agent: The ChatAgent instance
        query: User query to process

    Returns:
        dict containing the response and tool calls information
    """
    # Run the agent (async)
    response = await agent.run(query)

    # Extract tool calls from the response
    tool_calls = []

    # The response has messages with contents
    if hasattr(response, 'messages'):
        for message in response.messages:
            if hasattr(message, 'contents'):
                for content in message.contents:
                    if hasattr(content, 'to_dict'):
                        content_dict = content.to_dict()
                        if content_dict.get('type') == 'function_call':
                            tool_calls.append({
                                'id': content_dict.get('call_id'),
                                'name': content_dict.get('name'),
                                'arguments': json.loads(content_dict.get('arguments', '{}'))
                            })

    return {
        'query': query,
        'response': str(response),
        'tool_calls': tool_calls
    }


def evaluate_tool_selection_manual(
    expected_tools: list[str],
    actual_tool_calls: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Manually evaluate if the correct tools were selected.

    Args:
        expected_tools: List of expected tool names
        actual_tool_calls: List of actual tool calls made by the agent

    Returns:
        dict with evaluation metrics
    """
    actual_tools = [tc['name'] for tc in actual_tool_calls if tc.get('name')]

    # Check if all expected tools were called
    expected_set = set(expected_tools)
    actual_set = set(actual_tools)

    # Calculate metrics
    correct_tools = expected_set.intersection(actual_set)
    missing_tools = expected_set - actual_set
    extra_tools = actual_set - expected_set

    # Precision: How many of the selected tools were correct?
    precision = len(correct_tools) / len(actual_set) if actual_set else 0

    # Recall: How many of the expected tools were selected?
    recall = len(correct_tools) / len(expected_set) if expected_set else 0

    # F1 Score
    f1 = 2 * (precision * recall) / (precision +
                                     recall) if (precision + recall) > 0 else 0

    # Exact match: Did we select exactly the right tools?
    exact_match = expected_set == actual_set

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'exact_match': exact_match,
        'expected_tools': list(expected_set),
        'actual_tools': list(actual_set),
        'correct_tools': list(correct_tools),
        'missing_tools': list(missing_tools),
        'extra_tools': list(extra_tools)
    }


def evaluate_tool_selection_with_llm(
    client: AzureOpenAI,
    query: str,
    response: str,
    tool_calls: list[dict[str, Any]],
    tool_definitions: list[dict[str, Any]],
    expected_tools: list[str]
) -> dict[str, Any]:
    """
    Use Azure OpenAI to evaluate tool selection quality.

    Args:
        client: AzureOpenAI client instance
        query: User query
        response: Agent response
        tool_calls: List of tool calls made
        tool_definitions: Available tool definitions
        expected_tools: Expected tools that should have been called

    Returns:
        dict with LLM-based evaluation results
    """
    evaluation_prompt = f"""You are an expert evaluator for AI agent tool selection.

Evaluate whether the agent selected the appropriate tools for the given user query.

User Query: {query}

Available Tools:
{json.dumps(tool_definitions, indent=2)}

Expected Tools: {', '.join(expected_tools)}

Actual Tool Calls:
{json.dumps(tool_calls, indent=2)}

Agent Response:
{response}

Evaluate the tool selection on the following criteria:
1. Correctness: Did the agent select the right tools for the query?
2. Completeness: Were all necessary tools selected?
3. Efficiency: Were any unnecessary tools selected?

Provide your evaluation in JSON format:
{{
    "correctness_score": <float 0-1>,
    "completeness_score": <float 0-1>,
    "efficiency_score": <float 0-1>,
    "overall_score": <float 0-1>,
    "reasoning": "<brief explanation>"
}}
"""

    try:
        eval_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are an expert AI evaluator. Respond only with valid JSON."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = json.loads(eval_response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "correctness_score": 0,
            "completeness_score": 0,
            "efficiency_score": 0,
            "overall_score": 0,
            "reasoning": f"Evaluation failed: {str(e)}"
        }


async def run_evaluation():
    """Main evaluation function."""
    print("=" * 80)
    print("Tool Selection Accuracy Evaluation")
    print("=" * 80)

    # Load ground truth
    eval_dir = Path(__file__).parent
    ground_truth_file = eval_dir / "ground_truth.json"
    ground_truth = load_ground_truth(ground_truth_file)

    print(f"\nLoaded {len(ground_truth)} test cases from {ground_truth_file}")

    # Create agent
    print("\nInitializing agent...")
    agent = create_mcp_orchestrator()

    # Create Azure OpenAI client for evaluation
    print("Initializing Azure OpenAI evaluator client...")
    eval_client = AzureOpenAI(
        api_version="2024-10-21",
        azure_endpoint=settings.endpoint,
        azure_ad_token_provider=lambda: DefaultAzureCredential().get_token(
            "https://cognitiveservices.azure.com/.default"
        ).token
    )

    # Tool definitions for the evaluator
    tool_definitions = [
        {
            "name": "get_pipeline_status",
            "description": "Get the status of a deployment pipeline for a specific service and environment",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "The service name (e.g., 'payments', 'checkout')"},
                    "environment": {"type": "string", "description": "The environment (e.g., 'prod', 'staging')"}
                },
                "required": ["service", "environment"]
            }
        },
        {
            "name": "get_job_logs",
            "description": "Get the logs from a specific job to understand what happened during execution",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "The job ID to retrieve logs for (e.g., 'job-789')"}
                },
                "required": ["job_id"]
            }
        }
    ]

    # Run evaluation
    results = []

    for idx, test_case in enumerate(ground_truth, 1):
        print(f"\n{'=' * 80}")
        print(f"Test Case {idx}/{len(ground_truth)}")
        print(f"Query: {test_case['query']}")
        print(f"Expected Tools: {test_case['expected_tools']}")

        # Run agent
        try:
            agent_result = await run_agent_and_capture_tools(agent, test_case['query'])

            print("\nActual Tool Calls:")
            for tc in agent_result['tool_calls']:
                print(f"  - {tc['name']}: {tc.get('arguments', {})}")

            # Manual evaluation
            manual_eval = evaluate_tool_selection_manual(
                test_case['expected_tools'],
                agent_result['tool_calls']
            )

            # LLM-based evaluation
            llm_eval = evaluate_tool_selection_with_llm(
                eval_client,
                test_case['query'],
                agent_result['response'],
                agent_result['tool_calls'],
                tool_definitions,
                test_case['expected_tools']
            )

            # Combine results
            result = {
                'test_case_id': idx,
                'query': test_case['query'],
                'expected_tools': test_case['expected_tools'],
                'actual_tool_calls': agent_result['tool_calls'],
                'manual_evaluation': manual_eval,
                'llm_evaluation': llm_eval,
                'response': agent_result['response']
            }

            results.append(result)

            # Print summary
            print("\nManual Evaluation:")
            print(f"  Precision: {manual_eval['precision']:.2f}")
            print(f"  Recall: {manual_eval['recall']:.2f}")
            print(f"  F1 Score: {manual_eval['f1_score']:.2f}")
            print(f"  Exact Match: {manual_eval['exact_match']}")

            print("\nLLM Evaluation:")
            print(f"  Overall Score: {llm_eval.get('overall_score', 0):.2f}")
            print(f"  Reasoning: {llm_eval.get('reasoning', 'N/A')}")

        except Exception as e:
            print(f"\n❌ Error running test case: {e}")
            results.append({
                'test_case_id': idx,
                'query': test_case['query'],
                'error': str(e)
            })

    # Calculate aggregate metrics
    print(f"\n{'=' * 80}")
    print("AGGREGATE RESULTS")
    print(f"{'=' * 80}")

    successful_results = [r for r in results if 'error' not in r]

    if successful_results:
        avg_precision = sum(r['manual_evaluation']['precision']
                            for r in successful_results) / len(successful_results)
        avg_recall = sum(r['manual_evaluation']['recall']
                         for r in successful_results) / len(successful_results)
        avg_f1 = sum(r['manual_evaluation']['f1_score']
                     for r in successful_results) / len(successful_results)
        exact_match_rate = sum(
            1 for r in successful_results if r['manual_evaluation']['exact_match']) / len(successful_results)
        avg_llm_score = sum(r['llm_evaluation'].get('overall_score', 0)
                            for r in successful_results) / len(successful_results)

        print(
            f"\nManual Metrics (averaged over {len(successful_results)} test cases):")
        print(f"  Average Precision: {avg_precision:.2%}")
        print(f"  Average Recall: {avg_recall:.2%}")
        print(f"  Average F1 Score: {avg_f1:.2%}")
        print(f"  Exact Match Rate: {exact_match_rate:.2%}")

        print("\nLLM-based Metrics:")
        print(f"  Average Overall Score: {avg_llm_score:.2%}")

    # Save detailed results
    results_file = eval_dir / "eval_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nDetailed results saved to: {results_file}")
    print(f"{'=' * 80}\n")

    return results


if __name__ == "__main__":
    asyncio.run(run_evaluation())
