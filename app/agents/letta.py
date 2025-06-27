from typing import Dict, List, Optional, Any
from functools import partial
from letta_client.client import Letta
from app.core.config import settings


class LettaAgent:
    """Letta agent for AI-powered interactions"""
    
    def __init__(self):
        self._client: Optional[Letta] = None
        self._is_initialized = False
    
    def _initialize_client(self) -> None:
        """Initialize the Letta client with proper configuration"""
        if self._is_initialized:
            return
            
        try:
            # Configure client for self-hosted Letta instance (no credentials needed for local Docker)
            self._client = Letta(
                base_url=settings.letta_base_url
            )
            self._is_initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Letta client: {str(e)}")
    
    def _ensure_client(self) -> Letta:
        """Ensure client is initialized and return it"""
        self._initialize_client()
        if not self._client:
            raise RuntimeError("Letta client not available")
        return self._client
    
    def create_agent(self, name: str, description: str, instructions: str) -> Dict[str, Any]:
        """Create a new Letta agent"""
        client = self._ensure_client()
        
        try:
            # Create agent with proper memory blocks and configuration
            agent = client.agents.create(
                name=name,
                description=description,
                memory_blocks=[
                    {
                        "label": "human",
                        "value": "User information will be stored here as we learn about them."
                    },
                    {
                        "label": "persona", 
                        "value": instructions
                    }
                ],
                model="openai/gpt-4o-mini",
                embedding="openai/text-embedding-3-small",
                include_base_tools=True
            )
            # Convert AgentState to dict for consistent return type
            return agent.dict() if hasattr(agent, 'dict') else dict(agent)
        except Exception as e:
            raise RuntimeError(f"Failed to create agent: {str(e)}")
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        client = self._ensure_client()
        
        try:
            agents = client.agents.list()
            # API returns List[AgentState] directly, convert to dict for consistency
            return [agent.dict() if hasattr(agent, 'dict') else dict(agent) for agent in agents]
        except Exception as e:
            raise RuntimeError(f"Failed to list agents: {str(e)}")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get a specific agent by ID"""
        client = self._ensure_client()
        
        try:
            agent = client.agents.retrieve(agent_id)
            # Convert AgentState to dict for consistent return type
            return agent.dict() if hasattr(agent, 'dict') else dict(agent)
        except Exception as e:
            raise RuntimeError(f"Failed to get agent {agent_id}: {str(e)}")
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent by ID"""
        client = self._ensure_client()
        
        try:
            client.agents.delete(agent_id)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete agent {agent_id}: {str(e)}")
    
    def chat_with_agent(
        self, 
        agent_id: str, 
        message: str, 
        stream: bool = False
    ) -> Dict[str, Any]:
        """Chat with a specific agent"""
        client = self._ensure_client()
        
        try:
            if stream:
                response = client.agents.messages.create_stream(
                    agent_id=agent_id,
                    messages=[{"role": "user", "content": message}]
                )
            else:
                response = client.agents.messages.create(
                    agent_id=agent_id,
                    messages=[{"role": "user", "content": message}]
                )
            
            # Handle response properly - extract assistant messages
            if hasattr(response, 'messages'):
                assistant_messages = []
                for msg in response.messages:
                    if hasattr(msg, 'message_type') and msg.message_type == "assistant_message":
                        assistant_messages.append({
                            "content": msg.content,
                            "timestamp": getattr(msg, 'created_at', None),
                            "message_type": msg.message_type
                        })
                
                return {
                    "messages": assistant_messages,
                    "full_response": response.dict() if hasattr(response, 'dict') else dict(response)
                }
            
            return response.dict() if hasattr(response, 'dict') else dict(response)
        except Exception as e:
            raise RuntimeError(f"Failed to chat with agent {agent_id}: {str(e)}")
    
    def get_agent_messages(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get message history for an agent"""
        client = self._ensure_client()
        
        try:
            messages = client.agents.messages.list(agent_id)
            # Convert message objects to dicts if needed
            if hasattr(messages, '__iter__'):
                return [msg.dict() if hasattr(msg, 'dict') else dict(msg) for msg in messages]
            return messages
        except Exception as e:
            raise RuntimeError(f"Failed to get messages for agent {agent_id}: {str(e)}")
    
    def clear_agent_messages(self, agent_id: str) -> bool:
        """Clear message history for an agent"""
        client = self._ensure_client()
        
        try:
            client.agents.messages.reset(agent_id)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to clear messages for agent {agent_id}: {str(e)}")


# Global agent instance
letta_agent = LettaAgent()


# Pure functions for agent operations
async def create_agent(name: str, description: str, instructions: str) -> Dict[str, Any]:
    """Create a new Letta agent - pure function wrapper"""
    return letta_agent.create_agent(name, description, instructions)


async def list_agents() -> List[Dict[str, Any]]:
    """List all agents - pure function wrapper"""
    return letta_agent.list_agents()


async def get_agent(agent_id: str) -> Dict[str, Any]:
    """Get agent by ID - pure function wrapper"""
    return letta_agent.get_agent(agent_id)


async def delete_agent(agent_id: str) -> bool:
    """Delete agent by ID - pure function wrapper"""
    return letta_agent.delete_agent(agent_id)


async def chat_with_agent(
    agent_id: str, 
    message: str, 
    stream: bool = False
) -> Dict[str, Any]:
    """Chat with agent - pure function wrapper"""
    return letta_agent.chat_with_agent(agent_id, message, stream)


async def get_agent_messages(agent_id: str) -> List[Dict[str, Any]]:
    """Get agent messages - pure function wrapper"""
    return letta_agent.get_agent_messages(agent_id)


async def clear_agent_messages(agent_id: str) -> bool:
    """Clear agent messages - pure function wrapper"""
    return letta_agent.clear_agent_messages(agent_id)


# Beauty search specific functions
async def get_or_create_beauty_search_agent() -> str:
    """Get or create a dedicated beauty search agent for product recommendations"""
    beauty_agent_name = "beauty_search_agent"
    
    try:
        # Try to find existing beauty search agent
        agents = await list_agents()
        for agent in agents:
            if agent.get("name") == beauty_agent_name:
                return agent["id"]
        
        # Create new beauty search agent if not found
        beauty_agent = await create_agent(
            name=beauty_agent_name,
            description="AI beauty consultant specializing in personalized product recommendations",
            instructions="""You are Liz, an expert AI beauty consultant for Noli.com, specializing in personalized skincare and beauty product recommendations.

Your expertise includes:
- Analyzing skin types, concerns, and conditions
- Recommending products based on ingredients and formulations
- Understanding beauty brands, product lines, and price points
- Providing educational information about skincare ingredients
- Suggesting complete beauty routines

When users ask questions, you should:
1. Understand their specific skin concerns or beauty needs
2. Provide thoughtful, personalized recommendations
3. Explain WHY you recommend specific products or ingredients
4. Consider their budget constraints when mentioned
5. Suggest 3-4 specific products when appropriate
6. Include educational context about ingredients or routines

Response format:
- Start with a brief explanation addressing their concern
- Recommend 3-4 specific products with:
  - Product name and brand
  - Why it's recommended for their concern
  - Key ingredients that help
  - Approximate price range
- End with any additional tips or routine suggestions

Be conversational, helpful, and educational. Focus on evidence-based recommendations."""
        )
        return beauty_agent["id"]
        
    except Exception as e:
        raise RuntimeError(f"Failed to get or create beauty search agent: {str(e)}")


async def search_beauty_products(query: str) -> Dict[str, Any]:
    """Search for beauty products using the dedicated Letta agent"""
    try:
        agent_id = await get_or_create_beauty_search_agent()
        
        response = await chat_with_agent(
            agent_id=agent_id,
            message=f"User query: {query}\n\nPlease provide personalized beauty product recommendations based on this query. Format your response with clear explanations and specific product suggestions.",
            stream=False
        )
        
        # Extract the assistant's response content
        assistant_content = ""
        if "messages" in response and response["messages"]:
            assistant_content = response["messages"][0].get("content", "")
        
        return {
            "agent_response": assistant_content,
            "agent_id": agent_id,
            "timestamp": response.get("messages", [{}])[0].get("timestamp") if response.get("messages") else None,
            "full_response": response
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to search beauty products: {str(e)}")
