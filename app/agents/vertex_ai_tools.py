"""
Vertex AI RAG Tools for Letta Agents
Provides RAG capabilities using Google Cloud Vertex AI Search
"""

from typing import Dict, List, Optional, Any
import asyncio
import json
from app.agents.letta import get_rag_response, BeautyConcern


async def search_beauty_knowledge_base(query: str, concern_type: Optional[str] = None) -> str:
    """
    Tool function for Letta agents to search the beauty knowledge base using Vertex AI RAG.
    
    Args:
        query (str): The search query for the beauty knowledge base
        concern_type (str, optional): The specific beauty concern type to focus the search
        
    Returns:
        str: JSON string containing search results from the knowledge base
    """
    try:
        # Validate concern_type if provided
        if concern_type:
            try:
                BeautyConcern(concern_type)
            except ValueError:
                concern_type = None
        
        # Perform RAG search
        results = await get_rag_response(query, concern_type)
        
        # Format results for agent consumption
        formatted_results = {
            "search_successful": True,
            "query": query,
            "concern_focus": concern_type,
            "knowledge_items": results.get("results", []),
            "confidence": results.get("confidence", 0.0),
            "recommendations": _extract_recommendations(results.get("results", []))
        }
        
        return json.dumps(formatted_results, indent=2)
        
    except Exception as e:
        error_result = {
            "search_successful": False,
            "error": str(e),
            "query": query,
            "concern_focus": concern_type
        }
        return json.dumps(error_result, indent=2)


async def reasoning_step(thought: str, action_needed: str) -> str:
    """
    Tool function for ReAct reasoning steps in Letta agents.
    
    Args:
        thought (str): The current reasoning or observation
        action_needed (str): What action needs to be taken next
        
    Returns:
        str: Formatted reasoning step for the agent's memory
    """
    reasoning_entry = {
        "reasoning_step": True,
        "timestamp": None,  # Would be populated with actual timestamp in production
        "thought": thought,
        "action_needed": action_needed,
        "step_type": "react_reasoning"
    }
    
    return json.dumps(reasoning_entry, indent=2)


def _extract_recommendations(knowledge_items: List[str]) -> List[Dict[str, Any]]:
    """Extract product recommendations from knowledge base results"""
    recommendations = []
    
    for item in knowledge_items:
        if any(brand in item for brand in ["The Ordinary", "CeraVe", "Neutrogena", "Paula's Choice", "SkinCeuticals", "Vanicream"]):
            # Extract product information
            rec = {
                "type": "product_recommendation",
                "source_info": item,
                "extracted_brand": _extract_brand(item),
                "key_ingredients": _extract_ingredients(item)
            }
            recommendations.append(rec)
        else:
            # General knowledge item
            rec = {
                "type": "ingredient_info",
                "source_info": item,
                "key_ingredients": _extract_ingredients(item)
            }
            recommendations.append(rec)
    
    return recommendations


def _extract_brand(text: str) -> Optional[str]:
    """Extract brand name from knowledge text"""
    brands = ["The Ordinary", "CeraVe", "Neutrogena", "Paula's Choice", "SkinCeuticals", "Vanicream"]
    for brand in brands:
        if brand in text:
            return brand
    return None


def _extract_ingredients(text: str) -> List[str]:
    """Extract ingredient names from knowledge text"""
    ingredients = [
        "salicylic acid", "benzoyl peroxide", "niacinamide", "retinoids", "retinol",
        "vitamin c", "peptides", "ceramides", "hyaluronic acid", "glycerin",
        "kojic acid", "arbutin", "hydroquinone", "oat extract", "fragrance-free"
    ]
    
    found_ingredients = []
    text_lower = text.lower()
    
    for ingredient in ingredients:
        if ingredient in text_lower:
            found_ingredients.append(ingredient)
    
    return found_ingredients


# Tool definitions for Letta agent registration
VERTEX_AI_RAG_TOOLS = [
    {
        "name": "search_beauty_knowledge_base",
        "description": "Search the beauty knowledge base using Vertex AI RAG for accurate product and ingredient information",
        "function": search_beauty_knowledge_base,
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
    },
    {
        "name": "reasoning_step",
        "description": "Record a reasoning step in the ReAct process before taking action",
        "function": reasoning_step,
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
] 