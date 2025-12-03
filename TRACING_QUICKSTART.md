# OpenTelemetry Tracing - Quick Start

## What Was Added

✅ **New telemetry module** at `src/rc_agent/telemetry/`  
✅ **OpenTelemetry dependencies** in `pyproject.toml`  
✅ **Automatic tracing** for agent runs, tool calls, and LLM requests  
✅ **Console output** - traces print to stdout for easy debugging  

## How to Use

### Run the CLI with Tracing

```bash
uv run python -m rc_agent.app.cli_chat
```

Ask questions like:
- "What pipeline tools do you have?"
- "What is the status of payments in prod?"

You'll see **trace spans** printed to console showing:
- Agent invocation spans
- Tool call spans  
- Model/LLM request spans

### Test Tracing

```bash
uv run python test_tracing.py
```

## What Changed

### Modified Files:
1. **`pyproject.toml`** - Added `opentelemetry-api` and `opentelemetry-sdk`
2. **`src/rc_agent/app/cli_chat.py`** - Added `init_tracing()` call at start of `main()`

### New Files:
1. **`src/rc_agent/telemetry/__init__.py`** - Module exports
2. **`src/rc_agent/telemetry/otel.py`** - OpenTelemetry initialization logic
3. **`test_tracing.py`** - Test script to verify tracing
4. **`TRACING.md`** - Comprehensive documentation

## How It Works

```python
# In cli_chat.py main():
init_tracing()  # Sets up OpenTelemetry + Agent Framework observability

# Agent Framework automatically traces:
result = await agent.run(user_input)  # ← Creates trace spans
```

## Key Features

- ✅ **Idempotent** - Safe to call `init_tracing()` multiple times
- ✅ **Zero code changes needed in tools** - Framework handles it automatically
- ✅ **Sensitive data enabled** - Captures full prompts and responses (good for debugging)
- ✅ **Console output only** - No cloud services required yet

## Next Steps (Optional)

To send traces to Azure Application Insights instead of console, see `TRACING.md` for configuration details.

## Verify Installation

```bash
uv run python -c "from rc_agent.telemetry import init_tracing; init_tracing(); print('✓ Tracing ready!')"
```

Should output: `✓ Tracing ready!`
