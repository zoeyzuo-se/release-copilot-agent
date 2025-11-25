from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from rc_agent.config.settings import settings
from rc_agent.tools.pipelines_tool import get_pipeline_status


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
            "When users ask about pipeline status, results, or deployment information, "
            "always use the get_pipeline_status tool to retrieve accurate, real-time data "
            "instead of guessing or making assumptions. "
            "Provide clear, helpful responses based on the actual pipeline data."
        ),
        chat_client=chat_client,
        tools=[get_pipeline_status],
    )
    
    return agent
