"""Orchestrator using MCP-style tools instead of multi-agent architecture."""

from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from rc_agent.config.settings import settings
from typing import Annotated
from pydantic import Field
import json


def create_mcp_orchestrator() -> ChatAgent:
    """
    Create and return the orchestrator agent using MCP-style tools.

    This coordinator agent uses tools directly instead of sub-agents.
    The tools follow MCP principles: simple, focused, stateless operations.

    - Pipeline Status Tool: Provides pipeline status queries
    - Job Logs Tool: Provides log analysis capabilities

    Architecture:
        User → Orchestrator Agent → [Direct Tools] → Response

    Returns:
        ChatAgent: A configured coordinator that uses direct tools
    """

    # Create Azure OpenAI chat client for the coordinator
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        endpoint=settings.endpoint,
        deployment_name=settings.deployment,
    )

    # Define MCP-style tools (simple, focused, stateless)
    @ai_function(
        name="get_pipeline_status",
        description="Get the status of a deployment pipeline for a specific service and environment"
    )
    def get_pipeline_status(
        service: Annotated[str, Field(description="The service name (e.g., 'payments', 'checkout')")],
        environment: Annotated[str, Field(
            description="The environment (e.g., 'prod', 'staging')")]
    ) -> str:
        """Get pipeline status from data file."""
        pipelines_file = settings.data_dir / "pipelines.json"

        try:
            with open(pipelines_file, 'r') as f:
                pipelines = json.load(f)
        except FileNotFoundError:
            return json.dumps({"found": False, "error": "Pipelines data file not found"})

        # Search for matching pipeline
        for pipeline in pipelines:
            if pipeline.get("service") == service and pipeline.get("environment") == environment:
                result = {
                    "found": True,
                    "status": pipeline.get("status"),
                    "pipeline_id": pipeline.get("pipeline_id"),
                    "branch": pipeline.get("branch"),
                    "started_at": pipeline.get("started_at"),
                    "finished_at": pipeline.get("finished_at"),
                    "failed_job_id": pipeline.get("failed_job_id")
                }
                return json.dumps(result)

        return json.dumps({
            "found": False,
            "message": f"No pipeline found for service '{service}' in environment '{environment}'"
        })

    @ai_function(
        name="get_job_logs",
        description="Get the logs from a specific job to understand what happened during execution"
    )
    def get_job_logs(
        job_id: Annotated[str, Field(
            description="The job ID to retrieve logs for (e.g., 'job-789')")]
    ) -> str:
        """Get job logs from data file."""
        logs_file = settings.data_dir / "log.json"

        try:
            with open(logs_file, 'r') as f:
                all_logs = json.load(f)
        except FileNotFoundError:
            return json.dumps({"found": False, "error": "Logs data file not found"})

        # Look up the job logs
        if job_id in all_logs:
            logs = all_logs[job_id]
            result = {
                "found": True,
                "job_id": job_id,
                "logs": logs
            }
            return json.dumps(result)

        return json.dumps({
            "found": False,
            "message": f"No logs found for job '{job_id}'"
        })

    # Create the coordinator agent with direct tools
    coordinator = chat_client.create_agent(
        name="release_copilot_coordinator",
        instructions=(
            "You are a CI/CD deployment assistant. Your role is to help users "
            "understand their deployment pipelines and troubleshoot failures.\n\n"
            "You have access to two tools:\n"
            "1. **get_pipeline_status** - Get current deployment pipeline status\n"
            "   - Use when users ask about pipeline status, deployments, or 'what's the status'\n"
            "   - Requires: service name and environment\n"
            "2. **get_job_logs** - Retrieve and analyze job execution logs\n"
            "   - Use when users ask about failures, errors, logs, or 'what went wrong'\n"
            "   - Requires: job_id (usually from a failed pipeline)\n\n"
            "Workflow:\n"
            "- Listen carefully to what the user is asking\n"
            "- For status queries: Use get_pipeline_status\n"
            "- For failure analysis:\n"
            "  1. First get the pipeline status to find the failed_job_id\n"
            "  2. Then use get_job_logs with that job_id to analyze what went wrong\n"
            "  3. Explain the root cause in simple, non-technical terms\n"
            "- Be conversational and helpful\n"
            "- Always use the tools to get actual data - never guess\n\n"
            "Present responses clearly and help users understand their deployment health."
        ),
        tools=[get_pipeline_status, get_job_logs],
    )

    return coordinator
