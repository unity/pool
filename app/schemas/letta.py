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