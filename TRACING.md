# OpenTelemetry Tracing Setup

This document describes the OpenTelemetry tracing implementation added to the Release Copilot agent.

## Overview

OpenTelemetry tracing has been integrated to provide observability for:
- Agent invocations (each `agent.run()` call)
- Tool calls (e.g., `get_pipeline_status`, `get_job_logs`)
- LLM/model calls (requests to Azure OpenAI)

All traces are output to the console using `ConsoleSpanExporter` for easy debugging during development.

## Implementation

### 1. Dependencies Added

The following OpenTelemetry packages were added to `pyproject.toml`:

```toml
"opentelemetry-api>=1.28.2",
"opentelemetry-sdk>=1.28.2",
```

### 2. New Module: `rc_agent.telemetry`

**Location:** `src/rc_agent/telemetry/`

**Files:**
- `__init__.py` - Exports the `init_tracing` function
- `otel.py` - Contains the OpenTelemetry initialization logic

**Key Function:** `init_tracing()`

This function:
- Initializes the Agent Framework observability with `setup_observability(enable_sensitive_data=True)`
- Adds a `ConsoleSpanExporter` to output traces to stdout
- Uses a `BatchSpanProcessor` for efficient span processing
- Is **idempotent** - safe to call multiple times

### 3. CLI Integration

**File:** `src/rc_agent/app/cli_chat.py`

The `main()` function now calls `init_tracing()` before creating the agent:

```python
async def main():
    """Interactive CLI chat with the Release Copilot agent."""
    # Initialize OpenTelemetry tracing
    init_tracing()
    
    print("Release Copilot - CI/CD Assistant")
    # ... rest of the code
```

## Usage

### Running the CLI with Tracing

Simply run the CLI as usual:

```bash
uv run python -m rc_agent.app.cli_chat
```

When you interact with the agent, you'll see trace spans printed to the console, showing:
- The agent invocation span
- Child spans for tool calls
- Child spans for model/LLM requests

### Example Trace Output

When running a query like "What is the status of the payments service in prod?", you'll see output similar to:

```
{
    'name': 'ChatAgent.run',
    'context': {...},
    'kind': 'SpanKind.INTERNAL',
    'parent_id': None,
    'start_time': '...',
    'end_time': '...',
    'status': {...},
    'attributes': {
        'agent.name': 'ReleaseCopilot',
        'agent.input': 'What is the status...',
        ...
    },
    'events': [...],
    'links': [],
    'resource': {
        'service.name': 'release-copilot-agent',
        ...
    }
}
```

### Testing Tracing

A test script is provided at `test_tracing.py`:

```bash
uv run python test_tracing.py
```

This will:
1. Initialize tracing
2. Create an agent
3. Run a simple query
4. Display trace output

## How It Works

### Agent Framework Integration

Microsoft Agent Framework has built-in OpenTelemetry support. When you call:

```python
setup_observability(enable_sensitive_data=True)
```

The framework automatically:
- Instruments `ChatAgent.run()` calls
- Creates spans for tool invocations
- Traces LLM requests and responses

### Console Output

The `ConsoleSpanExporter` outputs each completed span to stdout in JSON format, making it easy to:
- Debug agent behavior
- Understand the flow of execution
- Identify performance bottlenecks
- See which tools were called and in what order

## Configuration Options

### Sensitive Data

Currently set to `enable_sensitive_data=True` to capture:
- Full prompts sent to the LLM
- Complete responses from the LLM
- Tool inputs and outputs

For production, you may want to set this to `False`.

### Future: Application Insights

To send traces to Azure Application Insights instead of console:

1. Install additional packages:
   ```bash
   uv add azure-monitor-opentelemetry-exporter
   ```

2. Modify `otel.py` to use `AzureMonitorTraceExporter`:
   ```python
   from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
   
   exporter = AzureMonitorTraceExporter(
       connection_string="<your-app-insights-connection-string>"
   )
   span_processor = BatchSpanProcessor(exporter)
   ```

## Architecture

```
┌─────────────────────────────────────────┐
│  CLI (cli_chat.py)                      │
│  └── init_tracing()                     │
│      ├── Creates TracerProvider         │
│      ├── Adds ConsoleSpanExporter       │
│      └── Calls setup_observability()    │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Agent Framework                         │
│  └── Auto-instruments:                   │
│      ├── agent.run()                     │
│      ├── Tool calls                      │
│      └── LLM requests                    │
└─────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  OpenTelemetry SDK                       │
│  └── BatchSpanProcessor                  │
│      └── ConsoleSpanExporter             │
│          └── prints to stdout            │
└─────────────────────────────────────────┘
```

## Troubleshooting

### No traces appearing

1. Verify tracing is initialized:
   ```python
   from rc_agent.telemetry import init_tracing
   init_tracing()
   ```

2. Check that `agent_framework.observability` is available:
   ```bash
   uv run python -c "from agent_framework.observability import setup_observability; print('Available')"
   ```

### Traces not showing tool calls

Tool calls only appear if the agent actually invokes tools. Try a query that requires a tool, like:
- "What is the status of the payments service in prod?"
- "Why did the checkout pipeline fail in staging?"

## Files Modified/Created

### Created:
- `src/rc_agent/telemetry/__init__.py`
- `src/rc_agent/telemetry/otel.py`
- `test_tracing.py` (test script)
- `TRACING.md` (this file)

### Modified:
- `pyproject.toml` - Added OpenTelemetry dependencies
- `src/rc_agent/app/cli_chat.py` - Added `init_tracing()` call

## Next Steps

Possible enhancements:
1. Add metrics collection (request counts, latencies)
2. Integrate with Azure Application Insights
3. Add custom spans for specific operations
4. Configure sampling for production use
5. Add structured logging integration
