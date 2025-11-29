# Release Copilot Agent - Engineering Fundamentals

This branch serves as a **reference implementation** for building AI agents with Microsoft Agent Framework in Python. It demonstrates best practices for project structure, development environment setup, and agent-based tooling.

## 🏗️ Project Structure

```
release-copilot-agent/
├── .devcontainer/          # Dev container configuration
│   ├── devcontainer.json   # Container settings with Azure CLI
│   └── post_create.sh      # Auto-install Azure CLI
├── src/                    # Source code
├── data/                   # Sample data files
│   ├── pipelines.json
│   └── log.json
├── pyproject.toml          # Python project & dependencies
├── Makefile                # Common commands
└── .env                    # Environment variables (not in git)
```

## 🚀 Getting Started

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

## 📦 Key Technologies

| Technology | Purpose |
|------------|---------|
| **uv** | Fast Python package manager (replaces pip) |
| **Microsoft Agent Framework** | Build AI agents with function calling |
| **Azure OpenAI** | LLM backend with DefaultAzureCredential |
| **python-dotenv** | Load environment variables from `.env` |
| **Pydantic** | Type validation for function parameters |

## 🛠️ Common Commands

```bash
# Install/sync dependencies
make install

# Run main.py
make run

# Clean up cache files
make clean
```

