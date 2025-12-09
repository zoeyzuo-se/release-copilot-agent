"""Orchestrator using FastMCP tools (can be local or will support remote via MCP client in future)."""

from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from rc_agent.config.settings import settings
from typing import Annotated
from pydantic import Field
import json


def create_mcp_orchestrator() -> ChatAgent:
    """
    Create and return the orchestrator agent using FastMCP-style tools.

    This coordinator agent uses tools that wrap FastMCP server functions.
    The tools are currently called directly in-process.

    For remote deployment, FastMCP servers can be hosted separately
    and connected via MCP client (future enhancement).

    Architecture:
        User → Orchestrator Agent → [Direct Tool Calls] → FastMCP Functions → Response

    Returns:
        ChatAgent: A configured coordinator that uses FastMCP tools
    """

    # Create Azure OpenAI chat client for the coordinator
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        endpoint=settings.endpoint,
        deployment_name=settings.deployment,
    )

    # Import FastMCP tool functions
    from rc_agent.mcp.pipeline_mcp_server import get_pipeline_status as pipeline_tool
    from rc_agent.mcp.job_logs_mcp_server import get_job_logs as logs_tool

    # Wrap FastMCP tools for agent framework
    @ai_function(
        name="get_pipeline_status",
        description="Get the status of a deployment pipeline for a specific service and environment"
    )
    def get_pipeline_status(
        service: Annotated[str, Field(description="The service name (e.g., 'payments', 'checkout')")],
        environment: Annotated[str, Field(
            description="The environment (e.g., 'prod', 'staging')")]
    ) -> str:
        """Get pipeline status using FastMCP tool."""
        result = pipeline_tool(service=service, environment=environment)
        return json.dumps(result)

    @ai_function(
        name="get_job_logs",
        description="Get the logs from a specific job to understand what happened during execution"
    )
    def get_job_logs(
        job_id: Annotated[str, Field(
            description="The job ID to retrieve logs for (e.g., 'job-789')")]
    ) -> str:
        """Get job logs using FastMCP tool."""
        result = logs_tool(job_id=job_id)
        return json.dumps(result)

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
