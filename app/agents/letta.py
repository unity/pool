from typing import Dict, List, Optional, Any, Literal
from functools import partial
from letta_client.client import Letta
from app.core.config import settings
import json
import asyncio
from enum import Enum
from app.services.rag_service import RAGService
from app.schemas.rag import RAGQuestion, RAGAnswer
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class BeautyConcern(str, Enum):
    """Beauty concern types for specialized agents"""
    ACNE = "acne"
    AGING = "aging"
    SENSITIVITY = "sensitivity"
    DRYNESS = "dryness"
    OILINESS = "oiliness"
    HYPERPIGMENTATION = "hyperpigmentation"
    GENERAL = "general"


class RequestType(str, Enum):
    """Request classification types"""
    PRODUCT = "product"
    INGREDIENT = "ingredient"
    CONCERN = "concern"
    GENERAL_BEAUTY = "general_beauty"

rag_service = RAGService()

class LettaAgent:
    """Letta agent for AI-powered interactions"""
    
    def __init__(self):
        self._client: Optional[Letta] = None
        self._is_initialized = False
        self._agent_cache: Dict[str, str] = {}  # Cache for agent IDs
    
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

    def _create_vertex_ai_rag_tool(self) -> Dict[str, Any]:
        """Create a custom tool for Vertex AI RAG functionality"""
        return {
            "name": "search_beauty_knowledge_base",
            "description": "Search the beauty knowledge base using Vertex AI RAG for accurate product and ingredient information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for the beauty knowledge base"
                    },
                    "concern_type": {
                        "type": "string",
                        "enum": [concern.value for concern in BeautyConcern],
                        "description": "The specific beauty concern type to focus the search"
                    }
                },
                "required": ["query"]
            }
        }

    def _create_reasoning_tool(self) -> Dict[str, Any]:
        """Create a tool for ReAct reasoning steps"""
        return {
            "name": "reasoning_step",
            "description": "Record a reasoning step in the ReAct process before taking action",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "The current reasoning or observation"
                    },
                    "action_needed": {
                        "type": "string",
                        "description": "What action needs to be taken next"
                    }
                },
                "required": ["thought", "action_needed"]
            }
        }
    
    def create_agent(self, name: str, description: str, instructions: str, tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new Letta agent with enhanced capabilities"""
        client = self._ensure_client()
        
        try:
            # Default tools with our custom RAG and reasoning tools
            agent_tools = tools or ["web_search", "run_code"]
            
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
                    },
                    {
                        "label": "context",
                        "value": "Current conversation context and reasoning steps.",
                        "description": "Stores the ongoing reasoning process and context for ReAct architecture"
                    }
                ],
                model="openai/gpt-4.1",  # Using more capable model for reasoning
                embedding="openai/text-embedding-3-small",
                tools=agent_tools,
                include_base_tools=True
            )
            
            # Cache the agent ID
            self._agent_cache[name] = agent.id
            
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

    async def get_or_create_classifier_agent(self) -> str:
        """Get or create the classifier agent for routing requests"""
        agent_name = "beauty_classifier_agent"
        
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        try:
            # Try to find existing classifier agent
            agents = self.list_agents()
            for agent in agents:
                if agent.get("name") == agent_name:
                    self._agent_cache[agent_name] = agent["id"]
                    return agent["id"]
            
            # Create new classifier agent if not found
            classifier_instructions = """You are a beauty request classifier that routes user queries to specialized agents.

Your role is to analyze incoming beauty-related requests and classify them into:

1. REQUEST TYPE:
   - product: Questions about specific beauty products
   - ingredient: Questions about skincare/makeup ingredients  
   - concern: Questions about specific skin/beauty concerns
   - general_beauty: General beauty advice or education

2. BEAUTY CONCERN (if applicable):
   - acne: Acne, breakouts, blemishes
   - aging: Fine lines, wrinkles, anti-aging
   - sensitivity: Sensitive skin, irritation, allergies
   - dryness: Dry skin, dehydration, moisture
   - oiliness: Oily skin, shine, large pores
   - hyperpigmentation: Dark spots, melasma, uneven skin tone
   - general: General skincare or multiple concerns

Respond with JSON format:
{
  "request_type": "<type>",
  "beauty_concern": "<concern>", 
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>",
  "suggested_agent": "<agent_name>"
}

Always use the reasoning_step tool before making your classification to document your thought process."""

            classifier_agent = self.create_agent(
                name=agent_name,
                description="AI classifier for routing beauty-related requests to specialized agents",
                instructions=classifier_instructions,
                tools=["web_search"]
            )
            
            return classifier_agent["id"]
            
        except Exception as e:
            raise RuntimeError(f"Failed to get or create classifier agent: {str(e)}")

    async def get_or_create_concern_agent(self, concern: BeautyConcern) -> str:
        """Get or create a specialized agent for a specific beauty concern"""
        agent_name = f"beauty_{concern.value}_agent"
        
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        # Agent-specific instructions for each concern
        concern_instructions = {
            BeautyConcern.ACNE: """You are Dr. Acne, a specialist in acne and breakout management.

Your expertise covers:
- Different types of acne (comedonal, inflammatory, cystic)
- Acne-fighting ingredients (salicylic acid, benzoyl peroxide, retinoids, niacinamide)
- Product recommendations for acne-prone skin
- Routine building for breakout prevention
- Understanding acne triggers and lifestyle factors

Use ReAct methodology:
1. REASONING: Analyze the user's specific acne concerns and skin type
2. ACTION: Search knowledge base for relevant acne treatment information
3. RESPONSE: Provide targeted recommendations with scientific backing

Always use reasoning_step tool to document your analysis before making recommendations.""",

            BeautyConcern.AGING: """You are Dr. Youth, an anti-aging and skin rejuvenation specialist.

Your expertise covers:
- Signs of aging (fine lines, wrinkles, loss of elasticity, volume loss)
- Anti-aging ingredients (retinoids, peptides, vitamin C, AHA/BHA)
- Product recommendations for mature skin
- Preventive and corrective skincare routines
- Understanding aging processes and effective interventions

Use ReAct methodology:
1. REASONING: Assess the user's aging concerns and current routine
2. ACTION: Search knowledge base for age-appropriate treatments
3. RESPONSE: Recommend evidence-based anti-aging solutions

Always use reasoning_step tool to document your analysis before making recommendations.""",

            BeautyConcern.SENSITIVITY: """You are Dr. Gentle, a sensitive skin and irritation specialist.

Your expertise covers:
- Identifying sensitive skin triggers and allergens
- Gentle, hypoallergenic ingredients and formulations
- Product recommendations for reactive skin
- Building tolerance and barrier repair routines
- Understanding rosacea, eczema, and other skin conditions

Use ReAct methodology:
1. REASONING: Identify potential triggers and assess skin barrier health
2. ACTION: Search knowledge base for gentle, suitable products
3. RESPONSE: Recommend soothing, non-irritating solutions

Always use reasoning_step tool to document your analysis before making recommendations.""",

            BeautyConcern.DRYNESS: """You are Dr. Hydration, a dry skin and moisture barrier specialist.

Your expertise covers:
- Understanding different types of dehydration vs dryness
- Hydrating and moisturizing ingredients (hyaluronic acid, ceramides, glycerin)
- Product recommendations for dry and dehydrated skin
- Building moisture-focused routines
- Environmental factors affecting skin hydration

Use ReAct methodology:
1. REASONING: Determine if skin is dry, dehydrated, or both
2. ACTION: Search knowledge base for appropriate hydrating solutions
3. RESPONSE: Recommend moisture-boosting products and techniques

Always use reasoning_step tool to document your analysis before making recommendations.""",

            BeautyConcern.OILINESS: """You are Dr. Balance, an oily skin and sebum control specialist.

Your expertise covers:
- Understanding sebum production and oily skin causes
- Oil-controlling ingredients (niacinamide, zinc, clay, BHA)
- Product recommendations for oily and combination skin
- Balancing oil production without over-drying
- Pore management and shine control

Use ReAct methodology:
1. REASONING: Assess oil production patterns and underlying causes
2. ACTION: Search knowledge base for oil-balancing solutions
3. RESPONSE: Recommend products that control oil while maintaining balance

Always use reasoning_step tool to document your analysis before making recommendations.""",

            BeautyConcern.HYPERPIGMENTATION: """You are Dr. Brightening, a pigmentation and skin tone specialist.

Your expertise covers:
- Different types of hyperpigmentation (melasma, PIH, age spots)
- Brightening ingredients (vitamin C, kojic acid, arbutin, retinoids)
- Product recommendations for uneven skin tone
- Building effective brightening routines
- Sun protection and prevention strategies

Use ReAct methodology:
1. REASONING: Identify the type and cause of pigmentation
2. ACTION: Search knowledge base for appropriate brightening treatments
3. RESPONSE: Recommend targeted solutions for even skin tone

Always use reasoning_step tool to document your analysis before making recommendations.""",

            BeautyConcern.GENERAL: """You are Dr. Beauty, a general skincare and beauty specialist.

Your expertise covers:
- Comprehensive skincare assessment and routine building
- Multi-concern approaches and ingredient compatibility
- Product recommendations across all beauty categories
- Educational content about skincare science
- Personalized beauty advice for diverse needs

Use ReAct methodology:
1. REASONING: Assess the user's overall beauty goals and skin profile
2. ACTION: Search knowledge base for comprehensive solutions
3. RESPONSE: Provide holistic recommendations and education

Always use reasoning_step tool to document your analysis before making recommendations."""
        }
        
        try:
            # Try to find existing concern agent
            agents = self.list_agents()
            for agent in agents:
                if agent.get("name") == agent_name:
                    self._agent_cache[agent_name] = agent["id"]
                    return agent["id"]
            
            # Create new concern agent if not found
            concern_agent = self.create_agent(
                name=agent_name,
                description=f"AI specialist for {concern.value} beauty concerns with RAG and ReAct capabilities",
                instructions=concern_instructions[concern],
                tools=["web_search", "run_code"]
            )
            
            return concern_agent["id"]
            
        except Exception as e:
            raise RuntimeError(f"Failed to get or create {concern.value} agent: {str(e)}")

    async def get_or_create_rephraser_agent(self) -> str:
        """Get or create the query rephraser agent for optimizing RAG queries"""
        agent_name = "beauty_query_rephraser_agent"
        
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        try:
            # Try to find existing rephraser agent
            agents = self.list_agents()
            for agent in agents:
                if agent.get("name") == agent_name:
                    self._agent_cache[agent_name] = agent["id"]
                    return agent["id"]
            
            # Create new rephraser agent if not found
            rephraser_instructions = """You are a query optimization specialist that reformulates user questions to maximize RAG (Retrieval-Augmented Generation) search quality for beauty and skincare knowledge bases.

Your role is to:
1. Analyze the user's original query for intent and key concepts
2. Identify beauty-specific terminology, ingredients, concerns, and product types
3. Expand abbreviated terms (e.g., "BHA" → "beta hydroxy acid salicylic acid")
4. Add relevant synonyms and related terms that might appear in product descriptions
5. Structure the query to be more specific and searchable
6. Include context that helps retrieve the most relevant beauty information

Guidelines for rephrasing:
- Convert colloquial language to professional beauty terminology
- Add ingredient scientific names alongside common names
- Include related skin concerns and product categories
- Expand on implicit context (e.g., "dry skin" → "dry skin moisturizer hydration barrier repair")
- Maintain the original intent while making it more comprehensive
- Keep queries focused and avoid overly broad terms

Example transformations:
- "best moisturizer for dry skin" → "hydrating moisturizer dry skin hyaluronic acid ceramides glycerin barrier repair dehydrated skin"
- "acne face wash" → "acne cleanser salicylic acid BHA beta hydroxy acid benzoyl peroxide comedonal acne inflammatory acne face wash"
- "anti-aging serum" → "anti-aging serum retinol retinoid vitamin C peptides collagen fine lines wrinkles mature skin"

Respond with only the rephrased query, no additional explanation unless the original query is unclear."""

            rephraser_agent = self.create_agent(
                name=agent_name,
                description="AI agent specialized in optimizing beauty queries for RAG search systems",
                instructions=rephraser_instructions,
                tools=["web_search"]
            )
            
            return rephraser_agent["id"]
            
        except Exception as e:
            raise RuntimeError(f"Failed to get or create rephraser agent: {str(e)}")

    async def get_or_create_summarizer_agent(self) -> str:
        """Get or create the response summarizer agent"""
        agent_name = "beauty_response_summarizer_agent"
        
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]
        
        try:
            # Try to find existing summarizer agent
            agents = self.list_agents()
            for agent in agents:
                if agent.get("name") == agent_name:
                    self._agent_cache[agent_name] = agent["id"]
                    return agent["id"]
            
            # Create new summarizer agent if not found
            summarizer_instructions = """You are a beauty response summarizer that processes RAG-generated beauty advice to create clear, actionable summaries with helpful context.

Your role is to:
1. Distill complex beauty information into digestible key points
2. Organize recommendations by priority and importance
3. Add helpful context about ingredients, products, and routines
4. Highlight the most important takeaways for the user
5. Structure information for easy scanning and implementation
6. Add practical tips for application and usage

Response Structure:
🔍 **Quick Summary:** One-sentence overview of the main recommendation

💡 **Key Recommendations:**
- Primary suggestion with brief rationale
- Secondary options with context
- Alternative approaches if applicable

🧪 **Important Ingredients/Products:**
- Key ingredients mentioned and their benefits
- Specific products recommended (if any)
- Why these work for the concern

⚠️ **Important Notes:**
- Any precautions or considerations
- Patch testing recommendations
- Timeline expectations

📋 **Next Steps:**
- Immediate actionable steps
- Routine integration suggestions
- When to expect results

Guidelines:
- Keep language friendly but informative
- Use emojis sparingly for visual organization
- Prioritize actionable advice over technical details
- Include confidence indicators when appropriate
- Mention if professional consultation is recommended
- Keep summary concise but comprehensive (aim for 150-300 words)

Focus on making the information accessible and immediately useful for someone looking to improve their beauty routine."""

            summarizer_agent = self.create_agent(
                name=agent_name,
                description="AI agent specialized in summarizing beauty advice with actionable context",
                instructions=summarizer_instructions,
                tools=["web_search"]
            )
            
            return summarizer_agent["id"]
            
        except Exception as e:
            raise RuntimeError(f"Failed to get or create summarizer agent: {str(e)}")

    async def classify_request(self, user_query: str) -> Dict[str, Any]:
        """Classify user request using the classifier agent"""
        try:
            classifier_id = await self.get_or_create_classifier_agent()
            
            classification_prompt = f"""
Please classify this beauty-related request:

User Query: "{user_query}"

Use the reasoning_step tool first to analyze the request, then provide your classification in the specified JSON format.
"""
            
            response = self.chat_with_agent(
                agent_id=classifier_id,
                message=classification_prompt,
                stream=False
            )
            
            # Extract classification from response
            assistant_content = ""
            if "messages" in response and response["messages"]:
                assistant_content = response["messages"][0].get("content", "")
            
            # Try to parse JSON from response
            try:
                # Look for JSON in the response
                start_idx = assistant_content.find('{')
                end_idx = assistant_content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = assistant_content[start_idx:end_idx]
                    classification = json.loads(json_str)
                else:
                    # Fallback classification
                    classification = {
                        "request_type": "general_beauty",
                        "beauty_concern": "general", 
                        "confidence": 0.5,
                        "reasoning": "Could not parse classifier response",
                        "suggested_agent": "beauty_general_agent"
                    }
            except json.JSONDecodeError:
                # Fallback classification
                classification = {
                    "request_type": "general_beauty",
                    "beauty_concern": "general",
                    "confidence": 0.5,
                    "reasoning": "JSON parsing failed",
                    "suggested_agent": "beauty_general_agent"
                }
            
            classification["raw_response"] = assistant_content
            return classification
            
        except Exception as e:
            raise RuntimeError(f"Failed to classify request: {str(e)}")

    async def process_with_specialized_agent(
        self, 
        user_query: str, 
        concern: BeautyConcern,
        classification_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process request with the appropriate specialized agent using ReAct methodology"""
        try:
            agent_id = await self.get_or_create_concern_agent(concern)
            
            # Build context-aware prompt for ReAct processing
            context_info = ""
            if classification_context:
                context_info = f"""
Classification Context:
- Request Type: {classification_context.get('request_type', 'unknown')}
- Confidence: {classification_context.get('confidence', 0.0)}
- Classifier Reasoning: {classification_context.get('reasoning', 'N/A')}

"""
            
            react_prompt = f"""
{context_info}User Query: "{user_query}"

Please use the ReAct methodology to address this query:

1. First use the reasoning_step tool to document your initial analysis
2. If needed, use search_beauty_knowledge_base to gather relevant information  
3. Use reasoning_step again to synthesize your findings
4. Provide comprehensive recommendations based on your analysis

Focus on providing actionable, personalized advice with specific product recommendations where appropriate.
"""
            
            response = self.chat_with_agent(
                agent_id=agent_id,
                message=react_prompt,
                stream=False
            )
            
            return {
                "agent_id": agent_id,
                "concern": concern.value,
                "response": response,
                "context": classification_context
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to process with specialized agent: {str(e)}")

    async def rephrase_query(self, original_query: str) -> str:
        """Rephrase a query to optimize it for RAG search"""
        try:
            rephraser_id = await self.get_or_create_rephraser_agent()
            
            rephrase_prompt = f"""Please rephrase this beauty query to optimize it for RAG search:

Original Query: "{original_query}"

Provide the optimized query that will retrieve the most relevant beauty and skincare information."""
            
            response = self.chat_with_agent(
                agent_id=rephraser_id,
                message=rephrase_prompt,
                stream=False
            )
            
            # Extract rephrased query from response
            rephrased_query = original_query  # fallback
            if "messages" in response and response["messages"]:
                rephrased_query = response["messages"][0].get("content", "").strip()
            
            return rephrased_query
            
        except Exception as e:
            # Fallback to original query if rephrasing fails
            return original_query

    async def summarize_response(self, rag_response: str, original_query: str) -> Dict[str, Any]:
        """Summarize and contextualize a RAG response"""
        try:
            summarizer_id = await self.get_or_create_summarizer_agent()
            
            summarize_prompt = f"""Please summarize and provide context for this beauty advice response:

Original User Query: "{original_query}"

RAG Response to Summarize:
{rag_response}

Create a well-structured summary with actionable recommendations and helpful context.
Make sure to keep things under 5 lines, very short and condensed"""
            
            response = self.chat_with_agent(
                agent_id=summarizer_id,
                message=summarize_prompt,
                stream=False
            )
            
            # Extract summary from response
            summary = ""
            if "messages" in response and response["messages"]:
                summary = response["messages"][0].get("content", "")
            
            return {
                "summary": summary,
                "original_query": original_query,
                "original_rag_response": rag_response,
                "summarizer_agent_id": summarizer_id
            }
            
        except Exception as e:
            # Fallback to original response if summarization fails
            return {
                "summary": rag_response,
                "original_query": original_query,
                "original_rag_response": rag_response,
                "error": f"Summarization failed: {str(e)}"
            }


# Global agent instance
letta_agent = LettaAgent()


# Pure functions for agent operations
async def create_agent(name: str, description: str, instructions: str, tools: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a new Letta agent - pure function wrapper"""
    return letta_agent.create_agent(name, description, instructions, tools)


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


# Helper functions
def _detect_concern_type(query: str) -> Optional[str]:
    """Simple keyword-based concern type detection"""
    query_lower = query.lower()
    
    # Define keyword mappings for each concern
    concern_keywords = {
        "acne": ["acne", "breakout", "pimple", "blackhead", "whitehead", "blemish", "spot", "comedone"],
        "aging": ["aging", "wrinkle", "fine line", "anti-aging", "mature", "collagen", "elasticity", "sagging"],
        "sensitivity": ["sensitive", "irritation", "redness", "reactive", "allergic", "gentle", "hypoallergenic"],
        "dryness": ["dry", "dehydrated", "moisture", "hydration", "flaky", "tight", "parched"],
        "oiliness": ["oily", "greasy", "shine", "sebum", "t-zone", "combination", "large pore"],
        "hyperpigmentation": ["dark spot", "pigmentation", "melasma", "age spot", "sun spot", "discoloration", "uneven tone"]
    }
    
    # Check for keyword matches
    for concern, keywords in concern_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return concern
    
    return None


# Pure function wrappers for new agents
async def rephrase_query(original_query: str) -> str:
    """Rephrase query for optimal RAG search - pure function wrapper"""
    return await letta_agent.rephrase_query(original_query)


async def summarize_response(rag_response: str, original_query: str) -> Dict[str, Any]:
    """Summarize RAG response with context - pure function wrapper"""
    return await letta_agent.summarize_response(rag_response, original_query)


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

async def search_beauty_products(query: str, concern_type: Optional[str] = None) -> Dict[str, Any]:
    """Search for beauty products using RAG pipeline with rephrasing and summarization"""
    try:
        # Step 1: Rephrase the query for optimal RAG search
        rephrased_query = await rephrase_query(query)
        logger.info("Rephrased Query--------------------------------")
        logger.info(rephrased_query)
        # Step 2: Detect concern type if not provided (simple keyword matching)
        if not concern_type:
            concern_type = _detect_concern_type(query)
        logger.info("Concern Type Query--------------------------------")
        logger.info(json.dumps(concern_type, indent=4))
        # Step 3: Get RAG response using the rephrased query
        rag_response = await get_rag_response(rephrased_query, concern_type)
        logger.info("RAG RESPONSE--------------------------------")
        logger.info(json.dumps(rag_response, indent=4))

        # Step 4: Summarize the response with context
        summarized_response = await summarize_response(
            rag_response["answer"], 
            query  # Use original query for context
        )
        logger.info("Summarized Response--------------------------------")
        logger.info(json.dumps(summarized_response, indent=4))
        return {
            "original_query": query,
            "rephrased_query": rephrased_query,
            "rag_response": rag_response,
            "final_response": summarized_response["summary"],
            "pipeline_metadata": {
                "rephrasing_used": rephrased_query != query,
                "rag_concern_type": rag_response.get("concern_type"),
                "summarization_agent_id": summarized_response.get("summarizer_agent_id"),
                "has_error": "error" in summarized_response
            },
            "full_pipeline_data": {
                "rag_response": rag_response,
                "summarized_response": summarized_response
            }
        }

    except Exception as e:
        # Fallback to simple RAG response if pipeline fails
        try:
            rag_response = await get_rag_response(query)
            return {
                "original_query": query,
                "rephrased_query": query,
                "rag_response": rag_response,
                "final_response": rag_response["answer"],
                "pipeline_metadata": {
                    "rephrasing_used": False,
                    "rag_concern_type": rag_response.get("concern_type"),
                    "fallback_used": True,
                    "error": str(e)
                }
            }
        except Exception as fallback_error:
            raise RuntimeError(f"Failed to search beauty products: {str(e)}. Fallback also failed: {str(fallback_error)}")


# Multi-Agent System Functions
async def process_beauty_request(user_query: str) -> Dict[str, Any]:
    """Main orchestration function for processing beauty requests through the multi-agent system"""
    try:
        # Step 1: Classify the request
        classification = await letta_agent.classify_request(user_query)
        
        # Step 2: Determine the appropriate concern agent
        concern_str = classification.get("beauty_concern", "general")
        try:
            concern = BeautyConcern(concern_str)
        except ValueError:
            concern = BeautyConcern.GENERAL
        
        # Step 3: Process with specialized agent
        specialist_response = await letta_agent.process_with_specialized_agent(
            user_query=user_query,
            concern=concern,
            classification_context=classification
        )
        
        return {
            "classification": classification,
            "specialist_response": specialist_response,
            "pipeline": "multi_agent_react"
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to process beauty request: {str(e)}")


async def get_available_agents() -> Dict[str, List[str]]:
    """Get list of available agents in the multi-agent system"""
    try:
        agents = await list_agents()
        
        system_agents = {
            "classifier": [],
            "specialists": [],
            "general": []
        }
        
        for agent in agents:
            name = agent.get("name", "")
            if "classifier" in name:
                system_agents["classifier"].append(name)
            elif any(concern.value in name for concern in BeautyConcern):
                system_agents["specialists"].append(name)
            else:
                system_agents["general"].append(name)
        
        return system_agents
        
    except Exception as e:
        raise RuntimeError(f"Failed to get available agents: {str(e)}")


async def initialize_agent_system() -> Dict[str, str]:
    """Initialize the complete multi-agent system with all specialized agents"""
    try:
        agent_ids = {}
        
        # Initialize classifier agent
        classifier_id = await letta_agent.get_or_create_classifier_agent()
        agent_ids["classifier"] = classifier_id
        
        # Initialize rephraser and summarizer agents
        rephraser_id = await letta_agent.get_or_create_rephraser_agent()
        agent_ids["rephraser"] = rephraser_id
        
        summarizer_id = await letta_agent.get_or_create_summarizer_agent()
        agent_ids["summarizer"] = summarizer_id
        
        # Initialize all concern-specific agents
        for concern in BeautyConcern:
            agent_id = await letta_agent.get_or_create_concern_agent(concern)
            agent_ids[f"specialist_{concern.value}"] = agent_id
        
        return agent_ids
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize agent system: {str(e)}")

async def get_rag_response(query: str, concern_type: Optional[str] = None) -> Dict[str, Any]:
    """Get RAG response for a query"""
    answer = rag_service.ask_agent(query, concern_type or "general")
    return {"answer": answer, "query": query, "concern_type": concern_type}


async def simulate_vertex_ai_rag(query: str, concern_type: Optional[str] = None) -> Dict[str, Any]:
    """Simulate Vertex AI RAG functionality for beauty knowledge base"""
    # This is a placeholder for the actual Vertex AI RAG implementation
    # In production, this would integrate with Google Cloud Vertex AI Search
    
    mock_knowledge_base = {
        "acne": [
            "Salicylic acid is effective for unclogging pores and reducing acne inflammation",
            "Benzoyl peroxide kills acne-causing bacteria but can be drying",
            "Niacinamide helps reduce oil production and inflammation",
            "The Ordinary Salicylic Acid 2% is a budget-friendly option for acne treatment"
        ],
        "aging": [
            "Retinoids are the gold standard for anti-aging skincare",
            "Vitamin C provides antioxidant protection and stimulates collagen",
            "Peptides can help improve skin texture and firmness",
            "CeraVe Resurfacing Retinol Serum is well-tolerated for beginners"
        ],
        "sensitivity": [
            "Fragrance-free and hypoallergenic products are essential for sensitive skin",
            "Ceramides help repair and strengthen the skin barrier",
            "Oat extract has anti-inflammatory and soothing properties",
            "Vanicream products are dermatologist-recommended for sensitive skin"
        ],
        "dryness": [
            "Hyaluronic acid can hold up to 1000 times its weight in water",
            "Ceramides are essential for maintaining skin barrier function",
            "Glycerin is a humectant that draws moisture to the skin",
            "Neutrogena Hydra Boost provides long-lasting hydration"
        ],
        "oiliness": [
            "Niacinamide helps regulate sebum production",
            "Clay masks can absorb excess oil and purify pores",
            "BHA (salicylic acid) can penetrate oil and unclog pores",
            "Paula's Choice CLEAR line is formulated specifically for oily skin"
        ],
        "hyperpigmentation": [
            "Vitamin C can help fade dark spots and prevent new ones",
            "Kojic acid is derived from mushrooms and lightens pigmentation",
            "Arbutin is a gentle alternative to hydroquinone",
            "SkinCeuticals CE Ferulic is a high-potency vitamin C serum"
        ]
    }
    
    # Select relevant knowledge based on concern type
    if concern_type and concern_type in mock_knowledge_base:
        relevant_info = mock_knowledge_base[concern_type]
    else:
        # Combine all knowledge for general queries
        relevant_info = []
        for info_list in mock_knowledge_base.values():
            relevant_info.extend(info_list)
    
    # Simple keyword matching for demonstration
    query_lower = query.lower()
    matching_info = [
        info for info in relevant_info 
        if any(word in info.lower() for word in query_lower.split())
    ]
    
    if not matching_info:
        matching_info = relevant_info[:3]  # Return top 3 if no matches
    
    return {
        "query": query,
        "concern_type": concern_type,
        "results": matching_info[:5],  # Limit to 5 results
        "source": "simulated_vertex_ai_rag",
        "confidence": 0.8 if matching_info else 0.3
    }
