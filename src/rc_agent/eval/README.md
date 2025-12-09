# Tool Selection Accuracy Evaluation

This directory contains evaluation scripts to assess how accurately the Release Copilot agent selects tools based on user queries.

## Overview

The evaluation system consists of three main components:

1. **Ground Truth Data** (`ground_truth.json`) - Test cases with expected tool selections
2. **Response Collection** (`collect_responses.py`) - Runs the agent and captures tool calls
3. **Evaluation** (`evaluate.py`) - Calculates tool selection accuracy metrics

## Files

- `ground_truth.json` - Test queries with expected tool calls
- `collect_responses.py` - Script to run agent and collect responses
- `evaluate.py` - Main evaluation script with manual and LLM-based metrics
- `eval_tool_selection.py` - All-in-one evaluation script (runs agent and evaluates)
- `collected_responses.json` - (Generated) Collected agent responses
- `eval_results.json` - (Generated) Detailed evaluation results

## Quick Start

### Method 1: Two-Step Process (Recommended)

This approach separates data collection from evaluation, allowing you to re-evaluate without re-running the agent.

```bash
# Step 1: Collect agent responses
python -m rc_agent.eval.collect_responses

# Step 2: Evaluate the responses
python -m rc_agent.eval.evaluate

# Optional: Evaluate without LLM (manual metrics only)
python -m rc_agent.eval.evaluate --no-llm
```

### Method 2: All-in-One

This runs both collection and evaluation in a single script:

```bash
python -m rc_agent.eval.eval_tool_selection
```

## Ground Truth Format

The `ground_truth.json` file contains test cases in the following format:

```json
[
    {
        "query": "What's the status of the payments service in production?",
        "expected_tools": ["get_pipeline_status"],
        "expected_tool_args": {
            "service": "payments",
            "environment": "prod"
        }
    }
]
```

- `query`: The user's question to the agent
- `expected_tools`: List of tool names that should be called
- `expected_tool_args`: (Optional) Expected arguments for the tools

## Evaluation Metrics

### Manual Metrics

- **Precision**: What percentage of selected tools were correct?
- **Recall**: What percentage of expected tools were selected?
- **F1 Score**: Harmonic mean of precision and recall
- **Exact Match**: Did the agent select exactly the right tools (no more, no less)?

### LLM-based Metrics

Uses Azure OpenAI to evaluate:

- **Correctness Score**: Are the selected tools appropriate for the query?
- **Completeness Score**: Were all necessary tools selected?
- **Efficiency Score**: Were unnecessary tools avoided?
- **Overall Score**: Combined assessment
- **Reasoning**: Natural language explanation

## Adding New Test Cases

To add new test cases, edit `ground_truth.json`:

```json
{
    "query": "Your test query here",
    "expected_tools": ["tool_name_1", "tool_name_2"],
    "expected_tool_args": {
        "param1": "value1"
    }
}
```

Available tools in this agent:
- `get_pipeline_status` - Get deployment pipeline status
- `get_job_logs` - Retrieve job execution logs

## Environment Variables

Make sure these are set in your `.env` file:

```bash
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

## Output Files

### collected_responses.json

Contains agent responses for each test case:

```json
[
    {
        "test_case_id": 1,
        "query": "...",
        "expected_tools": [...],
        "actual_tool_calls": [...],
        "response": "...",
        "timestamp": "2025-12-09T..."
    }
]
```

### eval_results.json

Contains detailed evaluation results:

```json
{
    "evaluation_timestamp": "...",
    "total_test_cases": 5,
    "successful_evaluations": 5,
    "results": [
        {
            "test_case_id": 1,
            "query": "...",
            "manual_evaluation": {
                "precision": 1.0,
                "recall": 1.0,
                "f1_score": 1.0,
                "exact_match": true
            },
            "llm_evaluation": {
                "overall_score": 0.95,
                "reasoning": "..."
            }
        }
    ]
}
```

## Troubleshooting

### Agent Framework Response Structure

If tool calls aren't being detected, you may need to adjust the `extract_tool_calls_from_response()` function in `collect_responses.py` to match the actual response structure from the agent-framework.

To debug, add print statements:

```python
print("Response type:", type(response))
print("Response attributes:", dir(response))
print("Response data:", response)
```

### LLM Evaluation Errors

If LLM evaluation fails:
- Check that `AZURE_OPENAI_DEPLOYMENT` is set correctly
- Verify your Azure credentials with `az login`
- Run with `--no-llm` flag to skip LLM evaluation

## Example Usage

```bash
# Collect responses from agent
$ python -m rc_agent.eval.collect_responses
================================================================================
Agent Response Collection for Evaluation
================================================================================

Loaded 5 test queries from ground_truth.json

Initializing agent...
Agent initialized successfully!

================================================================================
Running Test Case 1/5
Query: What's the status of the payments service in production?

✓ Agent completed successfully
Tool calls detected: 1
  - get_pipeline_status

# Evaluate the collected responses
$ python -m rc_agent.eval.evaluate
================================================================================
Tool Selection Accuracy Evaluation
================================================================================

Loaded 5 collected responses from collected_responses.json

Initializing Azure OpenAI evaluator client...
✓ LLM evaluator initialized

================================================================================
Evaluating Test Case 1
Query: What's the status of the payments service in production?
Expected Tools: ['get_pipeline_status']

Actual Tool Calls:
  - get_pipeline_status: {'service': 'payments', 'environment': 'prod'}

Manual Evaluation:
  Precision: 100.00%
  Recall: 100.00%
  F1 Score: 100.00%
  Exact Match: ✓

LLM Evaluation:
  Overall Score: 95.00%
  Reasoning: The agent correctly selected get_pipeline_status tool with appropriate arguments.

================================================================================
AGGREGATE RESULTS
================================================================================

Manual Metrics (averaged over 5 test cases):
  Average Precision: 95.00%
  Average Recall: 98.00%
  Average F1 Score: 96.00%
  Exact Match Rate: 80.00% (4/5)

LLM-based Metrics (averaged over 5 test cases):
  Average Overall Score: 92.00%
  Average Correctness: 93.00%
  Average Completeness: 95.00%
  Average Efficiency: 89.00%
```

## Customization

### Adding More Ground Truth Cases

Edit `ground_truth.json` to add more diverse test cases covering:
- Simple status queries
- Complex multi-tool workflows
- Error scenarios
- Edge cases

### Modifying Evaluation Criteria

In `evaluate.py`, you can adjust:
- Manual metric calculations in `evaluate_tool_selection_manual()`
- LLM evaluation prompt in `evaluate_with_llm()`
- Aggregate metric computations

## Best Practices

1. **Diverse Test Cases**: Include queries that require different combinations of tools
2. **Regular Evaluation**: Run evaluation after agent changes to catch regressions
3. **Manual Review**: Review failed cases to improve agent instructions or tools
4. **Iterate on Ground Truth**: Update expected tools as agent capabilities evolve
