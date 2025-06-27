from typing import List, Dict
from fastapi import APIRouter, HTTPException, status
from app.agents.letta import (
    create_agent,
    list_agents,
    get_agent,
    delete_agent,
    chat_with_agent,
    get_agent_messages,
    clear_agent_messages,
    search_beauty_products,
    process_beauty_request,
    get_available_agents,
    initialize_agent_system,
    simulate_vertex_ai_rag
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
    ProductRecommendation,
    ClassificationRequest,
    ClassificationResponse,
    MultiAgentRequest,
    MultiAgentResponse,
    AgentSystemStatus,
    RAGSearchRequest,
    RAGSearchResponse,
    AgentInitializationRequest,
    AgentInitializationResponse
)
from app.core.logging_config import get_logger

logger = get_logger(__name__)

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
        # logger.info("Search Results:")
        # logger.info(search_result)
        # Mock product recommendations for demo
        mock_products = [
            ProductRecommendation(
                id="prod-001",
                name="La Roche-Posay Toleriane Sensitive Cream",
                brand="LaRoche Posay",
                price=29.99,
                rating=4.5,
                review_count=1250,
                image_url="http://localhost:5173/images/products/cream.webp",
                description="Calm and fortify sensitive skin, for a complexion that feels balanced and deeply nourished.",
                why_recommended="Perfect for your hydration needs",
                learn_more_url="https://noli.com/products/la-roche-posay-toleriane-sensitive-cream",
            )
        ]

        return SearchResponse(
            query=request.query,
            explanation=search_result.get("summary", ""),
            agent_response=search_result.get("final_response", ""),
            agent_id=search_result.get("agent_id", ""),
            products=mock_products,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform smart search: {str(e)}"
        )


# Multi-Agent System Endpoints
@router.post(
    "/multi-agent/process",
    response_model=MultiAgentResponse,
    summary="Process request through multi-agent system",
    description="Process beauty queries using the classifier and specialized agents with ReAct methodology"
)
async def process_multi_agent_request(request: MultiAgentRequest) -> MultiAgentResponse:
    """Process a beauty request through the multi-agent system"""
    try:
        import time
        start_time = time.time()
        
        # Process through multi-agent system
        result = await process_beauty_request(request.query)
        
        processing_time = time.time() - start_time
        
        # Extract and format the response
        classification = result.get("classification", {})
        specialist_response = result.get("specialist_response", {})
        
        return MultiAgentResponse(
            classification=ClassificationResponse(
                request_type=classification.get("request_type", "general_beauty"),
                beauty_concern=classification.get("beauty_concern", "general"),
                confidence=classification.get("confidence", 0.5),
                reasoning=classification.get("reasoning", ""),
                suggested_agent=classification.get("suggested_agent", ""),
                raw_response=classification.get("raw_response", "")
            ),
            specialist_response=SpecialistResponse(
                agent_id=specialist_response.get("agent_id", ""),
                concern=specialist_response.get("concern", "general"),
                response=specialist_response.get("response", {}),
                reasoning_steps=[],  # TODO: Extract from response
                recommendations=[],  # TODO: Extract from response
                confidence=0.8  # Default confidence
            ),
            pipeline=result.get("pipeline", "multi_agent_react"),
            total_processing_time=processing_time,
            agents_involved=[
                classification.get("suggested_agent", ""),
                specialist_response.get("agent_id", "")
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process multi-agent request: {str(e)}"
        )


@router.get(
    "/multi-agent/status",
    response_model=AgentSystemStatus,
    summary="Get multi-agent system status",
    description="Retrieve the current status of the multi-agent system and available agents"
)
async def get_multi_agent_status() -> AgentSystemStatus:
    """Get the status of the multi-agent system"""
    try:
        available_agents = await get_available_agents()
        
        classifier_agents = available_agents.get("classifier", [])
        specialist_agents = available_agents.get("specialists", [])
        
        # Create mapping of concerns to agent names
        specialist_mapping = {}
        for agent_name in specialist_agents:
            if "beauty_" in agent_name and "_agent" in agent_name:
                concern = agent_name.replace("beauty_", "").replace("_agent", "")
                specialist_mapping[concern] = agent_name
        
        return AgentSystemStatus(
            classifier_agent=classifier_agents[0] if classifier_agents else None,
            specialist_agents=specialist_mapping,
            total_agents=len(classifier_agents) + len(specialist_agents),
            system_ready=len(classifier_agents) > 0 and len(specialist_agents) > 0,
            last_updated=None  # TODO: Add timestamp tracking
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )


@router.post(
    "/multi-agent/initialize",
    response_model=AgentInitializationResponse,
    summary="Initialize multi-agent system",
    description="Initialize or reinitialize the complete multi-agent system with all specialized agents"
)
async def initialize_multi_agent_system(request: AgentInitializationRequest) -> AgentInitializationResponse:
    """Initialize the multi-agent system"""
    try:
        import time
        start_time = time.time()
        
        # Initialize the agent system
        agent_ids = await initialize_agent_system()
        
        initialization_time = time.time() - start_time
        
        return AgentInitializationResponse(
            initialized_agents=agent_ids,
            initialization_success=True,
            errors=[],
            time_taken=initialization_time
        )
        
    except Exception as e:
        return AgentInitializationResponse(
            initialized_agents={},
            initialization_success=False,
            errors=[str(e)],
            time_taken=0.0
        )


@router.post(
    "/rag/search",
    response_model=RAGSearchResponse,
    summary="Search beauty knowledge base",
    description="Search the beauty knowledge base using RAG (Retrieval-Augmented Generation)"
)
async def search_knowledge_base(request: RAGSearchRequest) -> RAGSearchResponse:
    """Search the beauty knowledge base using RAG"""
    try:
        # Perform RAG search
        results = await simulate_vertex_ai_rag(
            query=request.query,
            concern_type=request.concern_type
        )
        
        return RAGSearchResponse(
            query=results.get("query", request.query),
            concern_focus=results.get("concern_type"),
            knowledge_items=results.get("results", [])[:request.max_results],
            recommendations=[],  # TODO: Extract recommendations
            confidence=results.get("confidence", 0.5),
            source=results.get("source", "vertex_ai_rag")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search knowledge base: {str(e)}"
        )


@router.get(
    "/multi-agent/concerns",
    summary="Get available beauty concerns",
    description="Get list of available beauty concerns that have specialized agents"
)
async def get_beauty_concerns() -> Dict[str, List[str]]:
    """Get available beauty concerns and request types"""
    from app.agents.letta import BeautyConcern, RequestType
    
    return {
        "beauty_concerns": [concern.value for concern in BeautyConcern],
        "request_types": [req_type.value for req_type in RequestType],
        "total_concerns": len(BeautyConcern),
        "total_request_types": len(RequestType)
    } 
