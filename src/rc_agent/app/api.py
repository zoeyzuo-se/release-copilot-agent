"""FastAPI endpoint for Release Copilot chat service using MCP agent."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from rc_agent.agents.mcp_orchestrator import create_mcp_orchestrator
from rc_agent.telemetry.otel import init_tracing

# Initialize tracing
init_tracing()

# Create FastAPI app
app = FastAPI(
    title="Release Copilot API",
    description="CI/CD deployment assistant API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the agent instance (shared across requests)
agent = None


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    agent = create_mcp_orchestrator()
    print("✓ Release Copilot agent initialized")


# Request/Response models
class Message(BaseModel):
    """A chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's message/question")
    conversation_id: Optional[str] = Field(
        None, description="Optional conversation ID for context")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Agent's response")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    messages: List[Message] = Field(
        default_factory=list, description="Full conversation history")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": "Release Copilot API",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Release Copilot API",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for interacting with the Release Copilot agent.

    Send a message and receive an AI-powered response about your CI/CD pipelines.

    Args:
        request: ChatRequest containing the user's message

    Returns:
        ChatResponse with the agent's response and conversation history
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Run the agent with the user's message
        result = await agent.run(request.message)

        # Extract the assistant's response
        assistant_response = ""
        conversation_messages = []

        for msg in result.messages:
            # Build conversation history
            conversation_messages.append({
                "role": msg.role.value,
                "content": msg.text or ""
            })

            # Get the last assistant message as the response
            if msg.role.value == "assistant" and msg.text:
                assistant_response = msg.text

        return ChatResponse(
            response=assistant_response or "I'm sorry, I couldn't generate a response.",
            conversation_id=request.conversation_id,
            messages=conversation_messages
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint (placeholder for future implementation).

    For now, this redirects to the standard chat endpoint.
    Future: Implement server-sent events (SSE) for streaming responses.
    """
    return await chat(request)


# Example usage section
@app.get("/examples")
async def get_examples():
    """Get example queries that can be sent to the chat endpoint."""
    return {
        "examples": [
            {
                "query": "What's the status of the payments service in prod?",
                "description": "Check pipeline status"
            },
            {
                "query": "The checkout service failed in staging. What went wrong?",
                "description": "Analyze deployment failure"
            },
            {
                "query": "Can you check the logs for job-456?",
                "description": "Direct log analysis"
            },
            {
                "query": "Show me all failed pipelines",
                "description": "List failures"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting Release Copilot API...")
    print("Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Chat Endpoint: POST http://localhost:8000/chat")

    uvicorn.run(app, host="0.0.0.0", port=8000)
