# Quick Evaluation Guide

## TL;DR

```bash
# Run the complete evaluation
make eval

# Or run step by step
make eval-collect  # Collect agent responses
make eval-run      # Evaluate responses
```

## What Gets Evaluated?

Tool selection accuracy - whether the agent calls the right tools for each query.

## Test Cases

See `src/rc_agent/eval/ground_truth.json`:

1. ✅ Pipeline status query → `get_pipeline_status`
2. ✅ Failure investigation → `get_pipeline_status` + `get_job_logs`  
3. ✅ Direct logs request → `get_job_logs`
4. ✅ Service status check → `get_pipeline_status`
5. ✅ Combined query → `get_pipeline_status` + `get_job_logs`

## Metrics Explained

### Manual Metrics
- **Precision**: % of called tools that were expected
- **Recall**: % of expected tools that were called
- **F1 Score**: Balance of precision & recall
- **Exact Match**: Tools match exactly (100% or 0%)

### LLM Metrics (Optional)
- **Correctness**: Are tools appropriate?
- **Completeness**: All necessary tools called?
- **Efficiency**: No unnecessary tools?
- **Overall**: Combined assessment

## Example Output

```
AGGREGATE RESULTS
================================================================================

Manual Metrics (averaged over 5 test cases):
  Average Precision: 95.00%
  Average Recall: 98.00%
  Average F1 Score: 96.00%
  Exact Match Rate: 80.00% (4/5)

LLM-based Metrics (averaged over 5 test cases):
  Average Overall Score: 92.00%
```

## Files Generated

- `src/rc_agent/eval/collected_responses.json` - Agent outputs
- `src/rc_agent/eval/eval_results.json` - Detailed results

## Adding Test Cases

Edit `src/rc_agent/eval/ground_truth.json`:

```json
{
    "query": "Your question here",
    "expected_tools": ["tool_name"],
    "expected_tool_args": {
        "arg": "value"
    }
}
```

## Troubleshooting

**No tool calls detected?**
- Check `collect_responses.py` → `extract_tool_calls_from_response()`
- Print `response` object to see its structure

**LLM evaluation fails?**
- Verify `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT` in `.env`
- Run with `--no-llm`: `python -m rc_agent.eval.evaluate --no-llm`

**Agent errors during collection?**
- Check logs in console output
- Errors are captured in `collected_responses.json`

## Advanced Usage

```bash
# Collect only (reuse existing responses)
python -m rc_agent.eval.collect_responses

# Evaluate without LLM
python -m rc_agent.eval.evaluate --no-llm

# All-in-one script
python -m rc_agent.eval.eval_tool_selection
```
