"""Job Logs Analyzer Agent - Specialist for analyzing job execution logs."""

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from rc_agent.config.settings import settings
from rc_agent.services import LogsService


def create_job_logs_analyzer_agent() -> ChatAgent:
    """
    Create and return a Job Logs Analyzer Agent.

    This agent specializes in retrieving and analyzing job execution logs.
    It uses the LogsService to access log data and provides intelligent
    analysis of failures and errors.

    Returns:
        ChatAgent: A configured job logs analyzer specialist agent
    """
    # Create Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        endpoint=settings.endpoint,
        deployment_name=settings.deployment,
    )

    # Initialize logs service
    logs_service = LogsService()

    # Define custom function for log retrieval
    def fetch_job_logs(job_id: str) -> str:
        """
        Internal function to fetch job logs.

        Args:
            job_id: Job ID to retrieve logs for

        Returns:
            str: Formatted log information
        """
        result = logs_service.get_job_logs(job_id)

        if not result.get("found"):
            return result.get("message") or result.get("error", "Logs not found")

        # Format logs for analysis
        logs = result.get("logs", [])
        log_text = "\n".join(logs)

        return f"""Job Logs for {job_id}:
        
{log_text}

(Total: {len(logs)} log lines)"""

    # Create tool wrapper
    from agent_framework import ai_function
    from typing import Annotated
    from pydantic import Field

    @ai_function(
        name="get_job_logs",
        description="Retrieve the execution logs for a specific job to understand what happened during execution"
    )
    def get_logs(
        job_id: Annotated[str, Field(
            description="The job ID to retrieve logs for (e.g., 'job-789')")]
    ) -> str:
        return fetch_job_logs(job_id)

    # Create the specialist agent
    agent = ChatAgent(
        name="JobLogsAnalyzerAgent",
        instructions=(
            "You are a CI/CD log analysis specialist. Your expertise is in reading job execution logs "
            "and explaining what went wrong in plain, understandable language.\n\n"
            "When analyzing logs:\n"
            "1. Use the get_job_logs tool to retrieve the logs for the given job ID\n"
            "2. Carefully read through the logs to identify error patterns\n"
            "3. Common error types include:\n"
            "   - Build failures (compilation errors, missing dependencies)\n"
            "   - Test failures (failing unit tests, integration tests)\n"
            "   - Deployment issues (permission errors, resource conflicts)\n"
            "   - Configuration problems (missing env vars, invalid configs)\n"
            "4. Explain what went wrong in simple, non-technical terms\n"
            "5. If possible, suggest what might need to be fixed\n"
            "6. Be concise but thorough\n\n"
            "Your goal is to help developers quickly understand the root cause of failures "
            "without having to manually parse through logs."
        ),
        chat_client=chat_client,
        tools=[get_logs],
    )

    return agent
