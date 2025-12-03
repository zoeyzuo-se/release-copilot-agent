"""Orchestrator - Simple multi-agent coordinator using ChatAgent with specialist agent tools."""

from agent_framework import ChatAgent, ai_function
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from rc_agent.config.settings import settings
from rc_agent.agents.pipeline_status_agent import create_pipeline_status_agent
from rc_agent.agents.job_logs_analyzer_agent import create_job_logs_analyzer_agent


def create_orchestrator() -> ChatAgent:
    """
    Create and return the orchestrator agent.

    This coordinator agent delegates to specialist agents by calling them as functions.
    This creates a true multi-agent workflow where:
    
    - PipelineStatusAgent: Runs as a sub-agent for pipeline status queries
    - JobLogsAnalyzerAgent: Runs as a sub-agent for log analysis
    
    Routing Pattern:
        User → Coordinator → [Calls specialist agent] → Response

    Returns:
        ChatAgent: A configured coordinator that orchestrates specialist agents
    """
    
    # Create specialist agents
    pipeline_agent = create_pipeline_status_agent()
    job_logs_agent = create_job_logs_analyzer_agent()
    
    # Wrap specialist agents as callable tools for the coordinator
    @ai_function(
        name="consult_pipeline_status_agent",
        description="Consult the pipeline status specialist agent to get current deployment pipeline status"
    )
    async def call_pipeline_agent(query: str) -> str:
        """
        Call the pipeline status specialist agent.
        
        Args:
            query: The user's question about pipeline status
            
        Returns:
            The specialist agent's response
        """
        result = await pipeline_agent.run(query)
        # Extract the last assistant message
        for msg in reversed(result.messages):
            if msg.role.value == "assistant" and msg.text:
                return msg.text
        return "No response from pipeline status agent"
    
    @ai_function(
        name="consult_job_logs_agent",
        description="Consult the job logs analyzer specialist agent to understand job failures and errors"
    )
    async def call_logs_agent(query: str) -> str:
        """
        Call the job logs analyzer specialist agent.
        
        Args:
            query: The user's question about job logs or failures
            
        Returns:
            The specialist agent's response
        """
        result = await job_logs_agent.run(query)
        # Extract the last assistant message
        for msg in reversed(result.messages):
            if msg.role.value == "assistant" and msg.text:
                return msg.text
        return "No response from logs analyzer agent"
    
    # Create Azure OpenAI chat client for the coordinator
    chat_client = AzureOpenAIChatClient(
        credential=DefaultAzureCredential(),
        endpoint=settings.endpoint,
        deployment_name=settings.deployment,
    )
    
    # Create the coordinator agent
    coordinator = chat_client.create_agent(
        name="release_copilot_coordinator",
        instructions=(
            "You are a CI/CD deployment assistant coordinator. Your role is to help users "
            "understand their deployment pipelines and troubleshoot failures.\n\n"
            "You coordinate with two specialist agents:\n"
            "1. **Pipeline Status Agent** - Expert in deployment pipeline status\n"
            "   - Use consult_pipeline_status_agent when users ask about pipeline status, "
            "current deployments, or 'what's the status'\n"
            "2. **Job Logs Analyzer Agent** - Expert in analyzing job execution logs\n"
            "   - Use consult_job_logs_agent when users ask about failures, errors, logs, "
            "or 'what went wrong'\n\n"
            "Workflow:\n"
            "- Listen carefully to what the user is asking\n"
            "- Route questions about status to the pipeline agent\n"
            "- Route questions about failures/logs to the logs agent\n"
            "- Pass the user's question directly to the specialist\n"
            "- Present the specialist's response to the user\n"
            "- If you're not sure which specialist to use, ask the user for clarification\n\n"
            "Be helpful, professional, and conversational. You are coordinating specialists, "
            "so delegate to them rather than trying to answer technical questions yourself."
        ),
        description="Coordinates specialist agents for CI/CD queries",
        tools=[call_pipeline_agent, call_logs_agent],
    )

    return coordinator
