"""Pipeline Status Agent - Specialist for pipeline status queries."""

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from rc_agent.config.settings import settings
from rc_agent.services import PipelineService


def create_pipeline_status_agent() -> ChatAgent:
    """
    Create and return a Pipeline Status Agent.

    This agent specializes in querying and reporting pipeline status information.
    It uses the PipelineService to access pipeline data and provides formatted
    status responses.

    Returns:
        ChatAgent: A configured pipeline status specialist agent
    """
    # Create Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        endpoint=settings.endpoint,
        deployment_name=settings.deployment,
    )

    # Initialize pipeline service
    pipeline_service = PipelineService()

    # Define custom function for pipeline status
    def check_pipeline_status(service: str, environment: str) -> str:
        """
        Internal function to check pipeline status.

        Args:
            service: Service name (e.g., 'payments', 'checkout')
            environment: Environment name (e.g., 'prod', 'staging')

        Returns:
            str: Formatted status information
        """
        result = pipeline_service.get_pipeline_status(service, environment)

        if not result.get("found"):
            return result.get("message") or result.get("error", "Pipeline not found")

        # Format successful response
        status = result.get("status", "unknown")
        pipeline_id = result.get("pipeline_id", "N/A")
        branch = result.get("branch", "N/A")
        started_at = result.get("started_at", "N/A")
        finished_at = result.get("finished_at", "N/A")

        response = f"""Pipeline Status for {service} in {environment}:
- Status: {status}
- Pipeline ID: {pipeline_id}
- Branch: {branch}
- Started: {started_at}
- Finished: {finished_at}"""

        # Add failed job info if applicable
        if result.get("failed_job_id"):
            response += f"\n- Failed Job ID: {result['failed_job_id']}"
            response += "\n\n⚠️ This pipeline has failed. The logs can be analyzed for more details."

        return response

    # Store the service on the agent for access in model context
    # We'll make it available through a simple wrapper
    from agent_framework import ai_function
    from typing import Annotated
    from pydantic import Field

    @ai_function(
        name="get_pipeline_status",
        description="Get the current status of a deployment pipeline for a specific service and environment"
    )
    def get_status(
        service: Annotated[str, Field(
            description="The service name (e.g., 'payments', 'checkout')")],
        environment: Annotated[str, Field(
            description="The environment (e.g., 'prod', 'staging')")]
    ) -> str:
        return check_pipeline_status(service, environment)

    # Create the specialist agent
    agent = ChatAgent(
        name="PipelineStatusAgent",
        instructions=(
            "You are a pipeline status specialist. Your job is to provide accurate, "
            "up-to-date information about deployment pipeline statuses.\n\n"
            "When asked about a pipeline:\n"
            "1. Extract the service name and environment from the user's question\n"
            "2. Use the get_pipeline_status tool to fetch the current status\n"
            "3. Present the information clearly and concisely\n"
            "4. If the pipeline has failed, mention the failed job ID so it can be investigated\n"
            "5. Be helpful and conversational\n\n"
            "Always use the tool to get actual data - never guess or make up status information."
        ),
        chat_client=chat_client,
        tools=[get_status],
    )

    return agent
