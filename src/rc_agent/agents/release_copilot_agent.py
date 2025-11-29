from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from rc_agent.config.settings import settings
from rc_agent.tools.pipelines_tool import get_pipeline_status
from rc_agent.tools.job_logs_tool import get_job_logs


def create_release_copilot_agent() -> ChatAgent:
    """
    Create and return a Release Copilot agent.

    The agent is configured to assist with CI/CD pipeline queries and uses
    the get_pipeline_status tool to retrieve actual pipeline information.

    Returns:
        ChatAgent: A configured agent instance ready to handle pipeline queries
    """
    # Create Azure OpenAI chat client
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        endpoint=settings.endpoint,
        deployment_name=settings.deployment,
    )

    # Create the agent with pipeline tools
    agent = ChatAgent(
        name="ReleaseCopilot",
        instructions=(
            "You are a CI/CD assistant that helps users understand their deployment pipelines. "
            "When users ask about pipeline status or deployment information, use the get_pipeline_status tool. "
            "\n\n"
            "When investigating failures or asked why something failed:\n"
            "1. First use get_pipeline_status to find the pipeline run\n"
            "2. If it failed and has a failed_job_id, call get_job_logs with that job ID\n"
            "3. Read the logs carefully and explain what went wrong in plain language\n"
            "4. Be helpful and suggest what might need to be fixed based on the error messages\n"
            "\n"
            "Always use the tools to get actual data instead of guessing. "
            "Be conversational and helpful - no need to be overly formal."
        ),
        chat_client=chat_client,
        tools=[get_pipeline_status, get_job_logs],
    )

    return agent
