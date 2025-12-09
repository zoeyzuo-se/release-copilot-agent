.PHONY: install run devui api mcp-servers clean help eval-collect eval-run eval

help:
	@echo "Available commands:"
	@echo "  make install     - Sync dependencies from pyproject.toml"
	@echo "  make add PKG=<package>  - Add a new package (e.g., make add PKG=fastapi)"
	@echo "  make run         - Run the application"
	@echo "  make devui       - Start the Release Copilot DevUI (web interface)"
	@echo "  make api         - Start the Release Copilot API server (port 8000)"
	@echo "  make mcp-servers - Start both FastMCP servers (ports 8001, 8002)"
	@echo "  make eval-collect - Collect agent responses for evaluation"
	@echo "  make eval-run    - Run evaluation on collected responses"
	@echo "  make eval        - Run full evaluation (collect + evaluate)"
	@echo "  make clean       - Clean up cache and temporary files"

install:
	uv sync
	uv pip install -e .

add:
	@test -n "$(PKG)" || (echo "Usage: make add PKG=package-name" && exit 1)
	uv add $(PKG)

run:
	uv run python main.py

devui:
	uv run python -m rc_agent.app.devui_entry

api:
	@echo "Starting Release Copilot API server..."
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Health Check: http://localhost:8000/health"
	uv run python src/rc_agent/app/api.py

mcp-servers:
	@echo "Starting FastMCP servers with HTTP/SSE transport..."
	uv run python run_mcp_servers.py

eval-collect:
	@echo "Collecting agent responses for evaluation..."
	uv run python -m rc_agent.eval.collect_responses

eval-run:
	@echo "Running evaluation on collected responses..."
	uv run python -m rc_agent.eval.evaluate

eval:
	@echo "Running full evaluation (collect + evaluate)..."
	@$(MAKE) eval-collect
	@$(MAKE) eval-run

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
