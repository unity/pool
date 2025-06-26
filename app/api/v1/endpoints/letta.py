from typing import List
from fastapi import APIRouter, HTTPException, status
from app.agents.letta import (
    create_agent,
    list_agents,
    get_agent,
    delete_agent,
    chat_with_agent,
    get_agent_messages,
    clear_agent_messages,
    search_beauty_products
)
from app.schemas.letta import (
    AgentCreateRequest,
    AgentResponse,
    AgentListResponse,
    ChatRequest,
    ChatResponse,
    MessageListResponse,
    ErrorResponse,
    SearchRequest,
    SearchResponse,
    ProductRecommendation
)

router = APIRouter()


@router.post(
    "/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Letta agent",
    description="Create a new AI agent with specified name, description, and instructions"
)
async def create_letta_agent(request: AgentCreateRequest) -> AgentResponse:
    """Create a new Letta agent"""
    try:
        agent_data = await create_agent(
            name=request.name,
            description=request.description,
            instructions=request.instructions
        )
        return AgentResponse(**agent_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get(
    "/agents",
    response_model=AgentListResponse,
    summary="List all Letta agents",
    description="Retrieve a list of all available AI agents"
)
async def get_letta_agents() -> AgentListResponse:
    """List all Letta agents"""
    try:
        agents_data = await list_agents()
        agents = [AgentResponse(**agent) for agent in agents_data]
        return AgentListResponse(agents=agents, total=len(agents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get(
    "/agents/{agent_id}",
    response_model=AgentResponse,
    summary="Get a specific Letta agent",
    description="Retrieve details of a specific AI agent by ID"
)
async def get_letta_agent(agent_id: str) -> AgentResponse:
    """Get a specific Letta agent by ID"""
    try:
        agent_data = await get_agent(agent_id)
        return AgentResponse(**agent_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent not found: {str(e)}"
        )


@router.delete(
    "/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Letta agent",
    description="Delete a specific AI agent by ID"
)
async def delete_letta_agent(agent_id: str) -> None:
    """Delete a Letta agent by ID"""
    try:
        success = await delete_agent(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.post(
    "/agents/{agent_id}/chat",
    response_model=ChatResponse,
    summary="Chat with a Letta agent",
    description="Send a message to a specific AI agent and get a response"
)
async def chat_with_letta_agent(agent_id: str, request: ChatRequest) -> ChatResponse:
    """Chat with a Letta agent"""
    try:
        response_data = await chat_with_agent(
            agent_id=agent_id,
            message=request.message,
            stream=request.stream
        )
        return ChatResponse(
            agent_id=agent_id,
            message=response_data.get("message", ""),
            timestamp=response_data.get("timestamp"),
            metadata=response_data.get("metadata")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to chat with agent: {str(e)}"
        )


@router.get(
    "/agents/{agent_id}/messages",
    response_model=MessageListResponse,
    summary="Get agent message history",
    description="Retrieve the conversation history for a specific AI agent"
)
async def get_letta_agent_messages(agent_id: str) -> MessageListResponse:
    """Get message history for a Letta agent"""
    try:
        messages_data = await get_agent_messages(agent_id)
        messages = [
            {
                "id": msg.get("id", ""),
                "content": msg.get("content", ""),
                "role": msg.get("role", "user"),
                "timestamp": msg.get("timestamp")
            }
            for msg in messages_data
        ]
        return MessageListResponse(messages=messages, total=len(messages))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent messages: {str(e)}"
        )


@router.delete(
    "/agents/{agent_id}/messages",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear agent message history",
    description="Clear the conversation history for a specific AI agent"
)
async def clear_letta_agent_messages(agent_id: str) -> None:
    """Clear message history for a Letta agent"""
    try:
        success = await clear_agent_messages(agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear agent messages: {str(e)}"
        )


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Smart search for beauty products",
    description="Natural language search for beauty products with AI-powered recommendations"
)
async def smart_search(request: SearchRequest) -> SearchResponse:
    """Smart search for beauty products with natural language processing"""
    try:
        # Use real Letta agent for beauty product search
        search_result = await search_beauty_products(request.query)
        
        # Extract agent response details
        agent_response = search_result.get("agent_response", "")
        agent_id = search_result.get("agent_id", "")
        
        # Generate a brief explanation for the UI (first paragraph of agent response)
        explanation_lines = agent_response.split('\n')
        explanation = explanation_lines[0] if explanation_lines else "Based on your query, here are personalized recommendations from our AI beauty consultant."
        
        return SearchResponse(
            query=request.query,
            explanation=explanation,
            agent_response=agent_response,
            agent_id=agent_id,
            products=[],  # For now, we'll rely on the agent's text response
            quiz_cta="Want more precise recommendations? Do the quiz!",
            quiz_url="/quiz"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {str(e)}"
        )


# Note: generate_search_explanation function removed - now using real Letta agent responses 