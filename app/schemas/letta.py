from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentCreateRequest(BaseModel):
    """Request schema for creating a new agent"""
    name: str = Field(..., description="Name of the agent", min_length=1, max_length=100)
    description: str = Field(..., description="Description of the agent", min_length=1, max_length=500)
    instructions: str = Field(..., description="Instructions for the agent", min_length=1)


class AgentResponse(BaseModel):
    """Response schema for agent data"""
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Name of the agent")
    description: str = Field(..., description="Description of the agent")
    instructions: str = Field(..., description="Instructions for the agent")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class AgentListResponse(BaseModel):
    """Response schema for list of agents"""
    agents: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")


class ChatRequest(BaseModel):
    """Request schema for chatting with an agent"""
    message: str = Field(..., description="Message to send to the agent", min_length=1)
    stream: bool = Field(False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Response schema for chat responses"""
    agent_id: str = Field(..., description="ID of the agent")
    message: str = Field(..., description="Response message from the agent")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MessageResponse(BaseModel):
    """Response schema for individual messages"""
    id: str = Field(..., description="Message ID")
    content: str = Field(..., description="Message content")
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class MessageListResponse(BaseModel):
    """Response schema for list of messages"""
    messages: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


# New schemas for Smart Search functionality
class SearchRequest(BaseModel):
    """Request schema for smart search"""
    query: str = Field(..., description="Natural language search query", min_length=1)


class ProductRecommendation(BaseModel):
    """Schema for individual product recommendation"""
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    brand: str = Field(..., description="Product brand")
    price: float = Field(..., description="Product price")
    currency: str = Field(default="USD", description="Price currency")
    rating: float = Field(..., description="Product rating (0-5)", ge=0, le=5)
    review_count: int = Field(..., description="Number of reviews", ge=0)
    image_url: str = Field(..., description="Product image URL")
    description: str = Field(..., description="Short product description")
    why_recommended: str = Field(..., description="Explanation of why this product was recommended")
    learn_more_url: str = Field(..., description="URL to product details page")


class SearchResponse(BaseModel):
    """Response schema for smart search results"""
    query: str = Field(..., description="Original search query")
    explanation: str = Field(..., description="Natural language explanation of the search results")
    agent_response: str = Field(..., description="Full response from the Letta beauty agent")
    agent_id: str = Field(..., description="ID of the agent that provided the response")
    products: List[ProductRecommendation] = Field(default=[], description="List of recommended products (3-5 items)")
    quiz_cta: str = Field(default="Want more precise recommendations? Do the quiz!", description="Call to action for quiz")
    quiz_url: str = Field(default="/quiz", description="URL to quiz page")


# Multi-Agent System Schemas
class ClassificationRequest(BaseModel):
    """Request schema for beauty request classification"""
    query: str = Field(..., description="User query to classify", min_length=1)


class ClassificationResponse(BaseModel):
    """Response schema for beauty request classification"""
    request_type: str = Field(..., description="Type of request (product, ingredient, concern, general_beauty)")
    beauty_concern: str = Field(..., description="Identified beauty concern")
    confidence: float = Field(..., description="Classification confidence (0.0-1.0)", ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Reasoning behind the classification")
    suggested_agent: str = Field(..., description="Suggested specialist agent name")
    raw_response: Optional[str] = Field(None, description="Raw classifier response")


class MultiAgentRequest(BaseModel):
    """Request schema for multi-agent processing"""
    query: str = Field(..., description="User query to process", min_length=1)
    force_concern: Optional[str] = Field(None, description="Force specific concern routing (optional)")
    include_reasoning: bool = Field(True, description="Include ReAct reasoning steps in response")


class ReActStep(BaseModel):
    """Schema for individual ReAct reasoning steps"""
    step_type: str = Field(..., description="Type of step (reasoning, action, observation)")
    content: str = Field(..., description="Step content")
    timestamp: Optional[str] = Field(None, description="Step timestamp")
    agent_id: Optional[str] = Field(None, description="Agent that performed the step")


class SpecialistResponse(BaseModel):
    """Response schema for specialist agent processing"""
    agent_id: str = Field(..., description="ID of the specialist agent")
    concern: str = Field(..., description="Beauty concern being addressed")
    response: Dict[str, Any] = Field(..., description="Full agent response")
    reasoning_steps: List[ReActStep] = Field(default=[], description="ReAct reasoning steps")
    recommendations: List[Dict[str, Any]] = Field(default=[], description="Extracted recommendations")
    confidence: float = Field(..., description="Response confidence", ge=0.0, le=1.0)


class MultiAgentResponse(BaseModel):
    """Response schema for multi-agent system processing"""
    classification: ClassificationResponse = Field(..., description="Request classification results")
    specialist_response: SpecialistResponse = Field(..., description="Specialist agent response")
    pipeline: str = Field(default="multi_agent_react", description="Processing pipeline used")
    total_processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    agents_involved: List[str] = Field(default=[], description="List of agent IDs involved in processing")


class AgentSystemStatus(BaseModel):
    """Schema for agent system status"""
    classifier_agent: Optional[str] = Field(None, description="Classifier agent ID")
    specialist_agents: Dict[str, str] = Field(default={}, description="Mapping of concern to agent ID")
    total_agents: int = Field(0, description="Total number of agents in system")
    system_ready: bool = Field(False, description="Whether the system is fully initialized")
    last_updated: Optional[str] = Field(None, description="Last system update timestamp")


class RAGSearchRequest(BaseModel):
    """Request schema for RAG search"""
    query: str = Field(..., description="Search query", min_length=1)
    concern_type: Optional[str] = Field(None, description="Specific beauty concern to focus search")
    max_results: int = Field(5, description="Maximum number of results to return", ge=1, le=20)


class RAGSearchResponse(BaseModel):
    """Response schema for RAG search results"""
    query: str = Field(..., description="Original search query")
    concern_focus: Optional[str] = Field(None, description="Beauty concern focus")
    knowledge_items: List[str] = Field(default=[], description="Knowledge base results")
    recommendations: List[Dict[str, Any]] = Field(default=[], description="Extracted recommendations")
    confidence: float = Field(..., description="Search confidence", ge=0.0, le=1.0)
    source: str = Field(default="vertex_ai_rag", description="Source of the search results")


class AgentInitializationRequest(BaseModel):
    """Request schema for initializing the agent system"""
    force_recreate: bool = Field(False, description="Force recreation of existing agents")
    concerns_to_initialize: Optional[List[str]] = Field(None, description="Specific concerns to initialize (optional)")


class AgentInitializationResponse(BaseModel):
    """Response schema for agent system initialization"""
    initialized_agents: Dict[str, str] = Field(..., description="Mapping of agent type to agent ID")
    initialization_success: bool = Field(..., description="Whether initialization was successful")
    errors: List[str] = Field(default=[], description="Any errors during initialization")
    time_taken: float = Field(..., description="Time taken for initialization in seconds") 