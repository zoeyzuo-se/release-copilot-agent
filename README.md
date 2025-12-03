# Release Copilot Agent - CI/CD Assistant

This project demonstrates **two architectural approaches** for building AI agents with Microsoft Agent Framework in Python:

1. **Multi-Agent Architecture** - Coordinator with specialist sub-agents
2. **MCP (Model Context Protocol) Architecture** - Single agent with MCP tools

Both approaches handle CI/CD deployment queries, including pipeline status checks and log analysis.

> **📘 See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed comparison and migration instructions**

## Architecture Overview

### Approach 1: Multi-Agent Workflow (Legacy)

The multi-agent system uses a **coordinator pattern** with three specialized agents:

```
User Query
    |
    v
Coordinator Agent (Orchestrator)
    |
    |-- Routes to --> Pipeline Status Agent
    |                   |
    |                   |-- Uses --> PipelineService (data access)
    |                   |-- Tool --> get_pipeline_status()
    |
    |-- Routes to --> Job Logs Analyzer Agent
                        |
                        |-- Uses --> LogsService (data access)
                        |-- Tool --> get_job_logs()
```

### Agent Responsibilities

**1. Coordinator Agent** (`orchestrator.py`)
- Routes user queries to appropriate specialist agents
- Orchestrates multi-agent conversations
- Presents specialist responses to users
- Tools: `consult_pipeline_status_agent`, `consult_job_logs_agent`

**2. Pipeline Status Agent** (`pipeline_status_agent.py`)
- Specialist for deployment pipeline status queries
- Provides current pipeline state, branch info, timestamps
- Tool: `get_pipeline_status(service, environment)`

**3. Job Logs Analyzer Agent** (`job_logs_analyzer_agent.py`)
- Specialist for analyzing job execution logs
- Explains failures, errors, and suggests fixes
- Tool: `get_job_logs(job_id)`

### Approach 2: MCP Architecture (Recommended)

The MCP system uses a **single agent with MCP tools**:

```
User Query
    |
    v
MCP Orchestrator Agent
    |
    |-- Calls --> get_pipeline_status (MCP Tool)
    |                   |
    |                   |-- MCP Server --> PipelineService
    |
    |-- Calls --> get_job_logs (MCP Tool)
                        |
                        |-- MCP Server --> LogsService
```

**Benefits:**
- ✅ Simpler architecture (1 agent vs 3)
- ✅ Better performance (direct tool calls)
- ✅ Standard protocol (MCP)
- ✅ Easier to test and maintain

**Files:**
- `src/rc_agent/agents/mcp_orchestrator.py` - MCP-based coordinator
- `src/rc_agent/mcp/pipeline_mcp_server.py` - Pipeline MCP server
- `src/rc_agent/mcp/job_logs_mcp_server.py` - Logs MCP server
- `examples/mcp_usage_example.py` - Usage examples

> **📘 See [MCP_CONFIG.md](MCP_CONFIG.md) for MCP configuration details**

### Services Layer

**PipelineService** (`services/pipeline_service.py`)
- Data access for pipeline information
- Reads from `data/pipelines.json`
- Method: `get_pipeline_status(service, environment)`

**LogsService** (`services/logs_service.py`)
- Data access for job execution logs
- Reads from `data/log.json`
- Method: `get_job_logs(job_id)`

## Project Structure

```
release-copilot-agent/
├── .devcontainer/              # Dev container configuration
│   ├── devcontainer.json       # Container settings with Azure CLI
│   └── post_create.sh          # Auto-install Azure CLI
├── src/
│   └── rc_agent/
│       ├── agents/             # Agent implementations
│       │   ├── orchestrator.py          # Multi-agent coordinator (legacy)
│       │   ├── mcp_orchestrator.py      # MCP coordinator (recommended)
│       │   ├── pipeline_status_agent.py # Pipeline specialist (multi-agent)
│       │   ├── job_logs_analyzer_agent.py # Logs specialist (multi-agent)
│       │   └── release_copilot_agent.py # Single agent (simple approach)
│       ├── mcp/                # MCP servers (new)
│       │   ├── pipeline_mcp_server.py   # Pipeline status MCP server
│       │   └── job_logs_mcp_server.py   # Job logs MCP server
│       ├── services/           # Data access layer
│       │   ├── pipeline_service.py
│       │   └── logs_service.py
│       ├── telemetry/          # OpenTelemetry tracing
│       │   └── otel.py
│       ├── config/             # Settings management
│       │   └── settings.py
│       └── app/                # Application entry points
│           └── cli_chat.py     # Interactive CLI
├── data/                       # Sample data files
│   ├── pipelines.json          # Pipeline status data
│   └── log.json                # Job execution logs
├── examples/                   # Usage examples
│   └── mcp_usage_example.py    # MCP orchestrator example
├── traces/                     # OpenTelemetry trace files
├── MCP_CONFIG.md               # MCP configuration guide
├── MIGRATION_GUIDE.md          # Multi-agent to MCP migration guide
├── test_multi_agent.py         # Multi-agent workflow tests
├── test_logs_agent.py          # Logs agent test
├── view_traces.py              # Trace viewer utility
├── pyproject.toml              # Python project & dependencies
├── Makefile                    # Common commands
└── .env                        # Environment variables (not in git)
```

## OpenTelemetry Tracing

The system includes comprehensive tracing that captures:
- Agent invocations (coordinator + specialists)
- LLM calls (chat completions)
- Tool executions
- Token usage statistics

Traces are automatically written to timestamped files in `traces/trace_YYYYMMDD_HHMMSS.jsonl`

View traces with:
```bash
python view_traces.py --summary  # Summary statistics
python view_traces.py            # Full trace details
```

## Getting Started

### Prerequisites

- **Docker** or **VS Code with Dev Containers extension**
- **Azure subscription** with access to Azure OpenAI
- **Git** for version control

### Step 1: Clone the Repository

```bash
git clone https://github.com/zoeyzuo-se/release-copilot-agent.git
cd release-copilot-agent
git checkout engineering-fundamentals
```

### Step 2: Set Up Azure Authentication

**On your HOST machine** (not in dev container):

```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_NAME"
```

> **Why on host?** The dev container mounts your `~/.azure` credentials from the host to bypass device compliance policies.

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI details:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### Step 4: Open in Dev Container

1. Open the project in **VS Code**
2. Press `F1` → **Dev Containers: Reopen in Container**
3. Wait for the container to build and post-create script to run

The dev container includes:
- Python 3.13
- `uv` package manager
- Azure CLI (auto-installed)
- Node.js LTS
- VS Code extensions (Pylance, Ruff, Black, mypy)

### Step 5: Install Dependencies

Inside the dev container:

```bash
make install
```

This runs:
- `uv sync` - Syncs dependencies from `pyproject.toml`
- `uv pip install -e .` - Installs the package in editable mode

## Running the Application

### Option 1: FastAPI REST API (Recommended for Integration)

Start the API server:

```bash
make api
# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

Use the API client:

```bash
make api-client
# or
python examples/api_client_example.py
```

See [API_README.md](API_README.md) for complete API documentation.

### Option 2: MCP Orchestrator (Direct Usage)

Run the MCP-based orchestrator example:

```bash
python examples/mcp_usage_example.py
```

Or use it in your own code:

```python
from rc_agent.agents.mcp_orchestrator import create_mcp_orchestrator

agent = create_mcp_orchestrator()
result = await agent.run("What's the status of payments in prod?")
```

### Option 3: Multi-Agent Architecture (Legacy)

Start the multi-agent CLI assistant:

```bash
python src/rc_agent/app/cli_chat.py
```

Example interactions:
```
You: What is the status of the payments service in prod?
Agent: [Coordinator routes to Pipeline Status Agent]
       The payments service pipeline in production has failed...

You: Can you analyze the logs for job-789?
Agent: [Coordinator routes to Job Logs Analyzer Agent]
       The logs show that job-789 failed during the build step...
```

### Option 4: Development UI (AI Toolkit)

Launch the AI Toolkit development UI for interactive agent testing:

```bash
make devui
```

This starts the AI Toolkit UI where you can:
- Test the multi-agent workflow interactively
- View real-time agent conversations
- Inspect tool calls and LLM responses
- Debug agent behavior with visual feedback


## Key Technologies

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework for programmatic access |
| **Uvicorn** | ASGI server for the API |
| **uv** | Fast Python package manager (replaces pip) |
| **Microsoft Agent Framework** | Build AI agents with function calling |
| **MCP (Model Context Protocol)** | Standard protocol for AI tool integration |
| **Azure OpenAI** | LLM backend with DefaultAzureCredential |
| **python-dotenv** | Load environment variables from `.env` |
| **Pydantic** | Type validation for function parameters |


## Common Commands

```bash
# Install/sync dependencies
make install

# Start the FastAPI REST API server (recommended for integration)
make api
# or
python src/rc_agent/app/api.py

# Test the API with the client example
make api-client
# or
python examples/api_client_example.py

# Run MCP orchestrator example
python examples/mcp_usage_example.py

# Run multi-agent CLI (legacy)
python src/rc_agent/app/cli_chat.py

# Launch AI Toolkit development UI
make devui

# Run multi-agent tests
python test_multi_agent.py
python test_logs_agent.py

# Test MCP servers independently
python src/rc_agent/mcp/pipeline_mcp_server.py
python src/rc_agent/mcp/job_logs_mcp_server.py

# View traces
python view_traces.py --summary

# Clean up cache files
make clean
```

## How the Multi-Agent System Works

> **Note:** This section describes the multi-agent architecture. For MCP architecture, see [MCP_CONFIG.md](MCP_CONFIG.md)

## Choosing the Right Architecture

### Use MCP When:
✅ Tools provide simple data retrieval or transformation  
✅ You want fast, direct tool execution  
✅ Tools are stateless operations  
✅ You want standard protocol integration  
✅ Performance and simplicity are priorities  

**→ Recommended for most use cases, including this project**

### Use Multi-Agent When:
✅ Specialists need complex reasoning and decision-making  
✅ Each specialist has its own conversation context  
✅ Specialists need to maintain state across interactions  
✅ You need agents to collaborate and negotiate  
✅ Each specialist requires different model configurations  

**→ Better for complex collaborative agent scenarios**

### 1. Agent Delegation Pattern

The coordinator agent uses specialist agents as **async function tools**:

```python
@ai_function
async def call_pipeline_agent(query: str) -> str:
    result = await pipeline_agent.run(query)
    return result.text
```

This creates a true multi-agent workflow where:
- Multiple agents run independently with their own LLM calls
- Each agent has specialized instructions and capabilities
- The coordinator explicitly delegates to and waits for specialists
- Tracing shows multiple agent invocations

### 2. Query Routing

The coordinator analyzes user queries and routes them:

**Pipeline Status Queries** → Pipeline Status Agent
- "What is the status of X service?"
- "Is the deployment to production complete?"
- "Show me the pipeline for Y environment"

**Log Analysis Queries** → Job Logs Analyzer Agent
- "Why did job-789 fail?"
- "Analyze the logs for this job"
- "What went wrong with the deployment?"

### 3. Data Flow

```
User Query
    ↓
Coordinator Agent (decides which specialist)
    ↓
Specialist Agent (processes query)
    ↓
Tool Function (data access)
    ↓
Service Layer (reads JSON data)
    ↓
Returns formatted response
    ↓
Coordinator presents to user
```

## Development Notes

### Adding New Specialist Agents

1. Create agent in `src/rc_agent/agents/`
2. Implement with specialized instructions and tools
3. Add service layer if needed in `src/rc_agent/services/`
4. Wrap in `@ai_function` in orchestrator
5. Add to coordinator's tool list
6. Update coordinator instructions

### Tracing Configuration

Tracing is initialized in `src/rc_agent/telemetry/otel.py`:
- Automatic timestamped trace files
- Console metrics suppressed for clean CLI output
- Integrates with Agent Framework's observability

### Environment Variables

Required in `.env`:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

Authentication uses `DefaultAzureCredential` from Azure Identity, which supports:
- Azure CLI credentials (recommended for local dev)
- Managed Identity (for production)
- Environment variables
- Interactive browser authentication

## Best Practices Demonstrated

1. **Separation of Concerns**: Agents, services, and data access are clearly separated
2. **Multi-Agent Orchestration**: Coordinator pattern with specialist delegation
3. **Observability**: Comprehensive OpenTelemetry tracing
4. **Type Safety**: Pydantic models and type hints throughout
5. **Clean Architecture**: Services layer abstracts data access from agent logic
6. **Development Workflow**: Dev containers for consistent environments

