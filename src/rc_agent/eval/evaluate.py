"""
Simplified evaluation script that uses pre-collected responses.

This script evaluates tool selection accuracy using responses collected
from the agent runner. It supports both manual metrics and LLM-based evaluation.
"""

import os
import json
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

from rc_agent.config.settings import settings

# Load environment variables
load_dotenv()


def load_collected_responses(file_path: Path) -> list[dict[str, Any]]:
    """Load pre-collected agent responses."""
    with open(file_path, 'r') as f:
        return json.load(f)


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
    actual_tools = [tc.get('name')
                    for tc in actual_tool_calls if tc.get('name')]

    # Check if all expected tools were called
    expected_set = set(expected_tools)
    actual_set = set(actual_tools)

    # Calculate metrics
    correct_tools = expected_set.intersection(actual_set)
    missing_tools = expected_set - actual_set
    extra_tools = actual_set - expected_set

    # Precision: How many of the selected tools were correct?
    precision = len(correct_tools) / len(actual_set) if actual_set else 0.0

    # Recall: How many of the expected tools were selected?
    recall = len(correct_tools) / len(expected_set) if expected_set else 0.0

    # F1 Score
    f1 = 2 * (precision * recall) / (precision +
                                     recall) if (precision + recall) > 0 else 0.0

    # Exact match: Did we select exactly the right tools?
    exact_match = expected_set == actual_set

    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'exact_match': exact_match,
        'expected_tools': sorted(list(expected_set)),
        'actual_tools': sorted(list(actual_set)),
        'correct_tools': sorted(list(correct_tools)),
        'missing_tools': sorted(list(missing_tools)),
        'extra_tools': sorted(list(extra_tools))
    }


def evaluate_with_llm(
    client: AzureOpenAI,
    query: str,
    response: str,
    tool_calls: list[dict[str, Any]],
    expected_tools: list[str]
) -> dict[str, Any]:
    """
    Use Azure OpenAI to evaluate tool selection quality.

    Args:
        client: AzureOpenAI client instance
        query: User query
        response: Agent response
        tool_calls: List of tool calls made
        expected_tools: Expected tools that should have been called

    Returns:
        dict with LLM-based evaluation results
    """
    tool_definitions = [
        {
            "name": "get_pipeline_status",
            "description": "Get the status of a deployment pipeline for a specific service and environment"
        },
        {
            "name": "get_job_logs",
            "description": "Get the logs from a specific job to understand what happened during execution"
        }
    ]

    evaluation_prompt = f"""You are an expert evaluator for AI agent tool selection.

Evaluate whether the agent selected the appropriate tools for the given user query.

User Query: "{query}"

Available Tools:
{json.dumps(tool_definitions, indent=2)}

Expected Tools: {', '.join(expected_tools)}

Actual Tool Calls:
{json.dumps(tool_calls, indent=2)}

Agent Response:
{response}

Evaluate the tool selection on the following criteria:
1. Correctness: Did the agent select the right tools for the query? (0-1)
2. Completeness: Were all necessary tools selected? (0-1)
3. Efficiency: Were any unnecessary tools selected? (0-1)

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
            "correctness_score": 0.0,
            "completeness_score": 0.0,
            "efficiency_score": 0.0,
            "overall_score": 0.0,
            "reasoning": f"Evaluation failed: {str(e)}"
        }


def run_evaluation(use_llm: bool = True):
    """
    Main evaluation function.

    Args:
        use_llm: Whether to use LLM-based evaluation (requires Azure OpenAI)
    """
    print("=" * 80)
    print("Tool Selection Accuracy Evaluation")
    print("=" * 80)

    # Load collected responses
    eval_dir = Path(__file__).parent
    responses_file = eval_dir / "collected_responses.json"

    if not responses_file.exists():
        print(
            f"\n❌ Error: Collected responses file not found: {responses_file}")
        print("Please run collect_responses.py first to collect agent responses.")
        return

    collected_data = load_collected_responses(responses_file)
    print(
        f"\nLoaded {len(collected_data)} collected responses from {responses_file}")

    # Initialize LLM evaluator if needed
    eval_client = None
    if use_llm:
        print("\nInitializing Azure OpenAI evaluator client...")
        try:
            eval_client = AzureOpenAI(
                api_version="2024-10-21",
                azure_endpoint=settings.endpoint,
                azure_ad_token_provider=lambda: DefaultAzureCredential().get_token(
                    "https://cognitiveservices.azure.com/.default"
                ).token
            )
            print("✓ LLM evaluator initialized")
        except Exception as e:
            print(f"⚠ Warning: Could not initialize LLM evaluator: {e}")
            print("Continuing with manual evaluation only...")
            use_llm = False

    # Run evaluation
    results = []

    for data_point in collected_data:
        test_case_id = data_point['test_case_id']
        query = data_point['query']
        expected_tools = data_point['expected_tools']
        actual_tool_calls = data_point.get('actual_tool_calls', [])
        response = data_point.get('response', '')

        print(f"\n{'=' * 80}")
        print(f"Evaluating Test Case {test_case_id}")
        print(f"Query: {query}")
        print(f"Expected Tools: {expected_tools}")

        if 'error' in data_point:
            print(f"⚠ Skipping - Error in collection: {data_point['error']}")
            results.append({
                'test_case_id': test_case_id,
                'query': query,
                'error': data_point['error'],
                'skipped': True
            })
            continue

        # Manual evaluation
        manual_eval = evaluate_tool_selection_manual(
            expected_tools, actual_tool_calls)

        print("\nActual Tool Calls:")
        for tc in actual_tool_calls:
            print(f"  - {tc.get('name', 'unknown')}: {tc.get('arguments', {})}")

        print("\nManual Evaluation:")
        print(f"  Precision: {manual_eval['precision']:.2%}")
        print(f"  Recall: {manual_eval['recall']:.2%}")
        print(f"  F1 Score: {manual_eval['f1_score']:.2%}")
        print(f"  Exact Match: {'✓' if manual_eval['exact_match'] else '✗'}")

        result = {
            'test_case_id': test_case_id,
            'query': query,
            'expected_tools': expected_tools,
            'actual_tool_calls': actual_tool_calls,
            'manual_evaluation': manual_eval,
            'response': response
        }

        # LLM evaluation
        if use_llm and eval_client:
            llm_eval = evaluate_with_llm(
                eval_client,
                query,
                response,
                actual_tool_calls,
                expected_tools
            )
            result['llm_evaluation'] = llm_eval

            print("\nLLM Evaluation:")
            print(f"  Overall Score: {llm_eval.get('overall_score', 0):.2%}")
            print(f"  Reasoning: {llm_eval.get('reasoning', 'N/A')}")

        results.append(result)

    # Calculate aggregate metrics
    print(f"\n{'=' * 80}")
    print("AGGREGATE RESULTS")
    print(f"{'=' * 80}")

    successful_results = [r for r in results if not r.get('skipped', False)]

    if successful_results:
        avg_precision = sum(r['manual_evaluation']['precision']
                            for r in successful_results) / len(successful_results)
        avg_recall = sum(r['manual_evaluation']['recall']
                         for r in successful_results) / len(successful_results)
        avg_f1 = sum(r['manual_evaluation']['f1_score']
                     for r in successful_results) / len(successful_results)
        exact_match_count = sum(
            1 for r in successful_results if r['manual_evaluation']['exact_match'])
        exact_match_rate = exact_match_count / len(successful_results)

        print(
            f"\nManual Metrics (averaged over {len(successful_results)} test cases):")
        print(f"  Average Precision: {avg_precision:.2%}")
        print(f"  Average Recall: {avg_recall:.2%}")
        print(f"  Average F1 Score: {avg_f1:.2%}")
        print(
            f"  Exact Match Rate: {exact_match_rate:.2%} ({exact_match_count}/{len(successful_results)})")

        if use_llm and eval_client:
            llm_results = [
                r for r in successful_results if 'llm_evaluation' in r]
            if llm_results:
                avg_llm_score = sum(r['llm_evaluation'].get(
                    'overall_score', 0) for r in llm_results) / len(llm_results)
                avg_correctness = sum(r['llm_evaluation'].get(
                    'correctness_score', 0) for r in llm_results) / len(llm_results)
                avg_completeness = sum(r['llm_evaluation'].get(
                    'completeness_score', 0) for r in llm_results) / len(llm_results)
                avg_efficiency = sum(r['llm_evaluation'].get(
                    'efficiency_score', 0) for r in llm_results) / len(llm_results)

                print(
                    f"\nLLM-based Metrics (averaged over {len(llm_results)} test cases):")
                print(f"  Average Overall Score: {avg_llm_score:.2%}")
                print(f"  Average Correctness: {avg_correctness:.2%}")
                print(f"  Average Completeness: {avg_completeness:.2%}")
                print(f"  Average Efficiency: {avg_efficiency:.2%}")

    # Save detailed results
    results_file = eval_dir / "eval_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'evaluation_timestamp': Path(__file__).stem,
            'total_test_cases': len(results),
            'successful_evaluations': len(successful_results),
            'results': results
        }, f, indent=2)

    print(f"\n\nDetailed results saved to: {results_file}")
    print(f"{'=' * 80}\n")

    return results


if __name__ == "__main__":
    import sys
    use_llm = "--no-llm" not in sys.argv
    run_evaluation(use_llm=use_llm)
