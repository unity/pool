"""
Tests for the multi-agent beauty system with Letta
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from app.agents.letta import (
    LettaAgent,
    BeautyConcern,
    RequestType,
    process_beauty_request,
    get_available_agents,
    initialize_agent_system,
    simulate_vertex_ai_rag
)
from app.agents.vertex_ai_tools import (
    search_beauty_knowledge_base,
    reasoning_step
)


class TestBeautyEnums:
    """Test beauty concern and request type enums"""
    
    def test_beauty_concerns(self):
        """Test that all expected beauty concerns are available"""
        expected_concerns = {
            "acne", "aging", "sensitivity", "dryness", 
            "oiliness", "hyperpigmentation", "general"
        }
        actual_concerns = {concern.value for concern in BeautyConcern}
        assert actual_concerns == expected_concerns
    
    def test_request_types(self):
        """Test that all expected request types are available"""
        expected_types = {
            "product", "ingredient", "concern", "general_beauty"
        }
        actual_types = {req_type.value for req_type in RequestType}
        assert actual_types == expected_types


class TestLettaAgent:
    """Test the enhanced LettaAgent class"""
    
    @pytest.fixture
    def mock_letta_client(self):
        """Mock Letta client for testing"""
        mock_client = Mock()
        mock_agent = Mock()
        mock_agent.id = "test-agent-123"
        mock_agent.dict.return_value = {
            "id": "test-agent-123",
            "name": "test_agent",
            "description": "Test agent"
        }
        mock_client.agents.create.return_value = mock_agent
        mock_client.agents.list.return_value = [mock_agent]
        return mock_client
    
    @patch('app.agents.letta.Letta')
    def test_agent_initialization(self, mock_letta_class, mock_letta_client):
        """Test agent initialization with caching"""
        mock_letta_class.return_value = mock_letta_client
        
        agent = LettaAgent()
        agent_data = agent.create_agent(
            name="test_agent",
            description="Test agent",
            instructions="Test instructions"
        )
        
        assert agent_data["id"] == "test-agent-123"
        assert "test_agent" in agent._agent_cache
        assert agent._agent_cache["test_agent"] == "test-agent-123"
    
    @patch('app.agents.letta.Letta')
    def test_vertex_ai_rag_tool_creation(self, mock_letta_class, mock_letta_client):
        """Test creation of Vertex AI RAG tool definition"""
        mock_letta_class.return_value = mock_letta_client
        
        agent = LettaAgent()
        rag_tool = agent._create_vertex_ai_rag_tool()
        
        assert rag_tool["name"] == "search_beauty_knowledge_base"
        assert "query" in rag_tool["parameters"]["properties"]
        assert "concern_type" in rag_tool["parameters"]["properties"]
    
    @patch('app.agents.letta.Letta')
    def test_reasoning_tool_creation(self, mock_letta_class, mock_letta_client):
        """Test creation of ReAct reasoning tool definition"""
        mock_letta_class.return_value = mock_letta_client
        
        agent = LettaAgent()
        reasoning_tool = agent._create_reasoning_tool()
        
        assert reasoning_tool["name"] == "reasoning_step"
        assert "thought" in reasoning_tool["parameters"]["properties"]
        assert "action_needed" in reasoning_tool["parameters"]["properties"]


class TestMultiAgentOrchestration:
    """Test multi-agent system orchestration"""
    
    @pytest.fixture
    def mock_agent_responses(self):
        """Mock agent responses for testing"""
        return {
            "classification": {
                "request_type": "concern",
                "beauty_concern": "acne",
                "confidence": 0.9,
                "reasoning": "User mentioned breakouts and acne",
                "suggested_agent": "beauty_acne_agent",
                "raw_response": "JSON response about acne classification"
            },
            "specialist_response": {
                "agent_id": "agent-acne-123",
                "concern": "acne",
                "response": {
                    "messages": [
                        {"content": "For acne treatment, I recommend...", "message_type": "assistant_message"}
                    ]
                },
                "context": {}
            }
        }
    
    @patch('app.agents.letta.letta_agent')
    async def test_process_beauty_request(self, mock_agent, mock_agent_responses):
        """Test the main beauty request processing pipeline"""
        mock_agent.classify_request = AsyncMock(return_value=mock_agent_responses["classification"])
        mock_agent.process_with_specialized_agent = AsyncMock(return_value=mock_agent_responses["specialist_response"])
        
        result = await process_beauty_request("I have bad acne, what should I use?")
        
        assert result["classification"]["beauty_concern"] == "acne"
        assert result["specialist_response"]["concern"] == "acne"
        assert result["pipeline"] == "multi_agent_react"
    
    @patch('app.agents.letta.letta_agent')
    async def test_get_available_agents(self, mock_agent):
        """Test retrieval of available agents"""
        mock_agents = [
            {"name": "beauty_classifier_agent"},
            {"name": "beauty_acne_agent"},
            {"name": "beauty_aging_agent"},
            {"name": "other_agent"}
        ]
        mock_agent.list_agents = AsyncMock(return_value=mock_agents)
        
        result = await get_available_agents()
        
        assert len(result["classifier"]) == 1
        assert len(result["specialists"]) == 2
        assert len(result["general"]) == 1
    
    @patch('app.agents.letta.letta_agent')
    async def test_initialize_agent_system(self, mock_agent):
        """Test agent system initialization"""
        mock_agent.get_or_create_classifier_agent = AsyncMock(return_value="classifier-123")
        mock_agent.get_or_create_concern_agent = AsyncMock(side_effect=lambda concern: f"agent-{concern.value}-123")
        
        result = await initialize_agent_system()
        
        assert "classifier" in result
        assert result["classifier"] == "classifier-123"
        assert len([k for k in result.keys() if k.startswith("specialist_")]) == len(BeautyConcern)


class TestVertexAIRAG:
    """Test Vertex AI RAG functionality"""
    
    async def test_simulate_vertex_ai_rag_acne(self):
        """Test RAG simulation for acne-related queries"""
        result = await simulate_vertex_ai_rag("best acne treatment", "acne")
        
        assert result["query"] == "best acne treatment"
        assert result["concern_type"] == "acne"
        assert len(result["results"]) > 0
        assert any("salicylic acid" in item.lower() for item in result["results"])
    
    async def test_simulate_vertex_ai_rag_general(self):
        """Test RAG simulation for general queries"""
        result = await simulate_vertex_ai_rag("skincare routine", None)
        
        assert result["query"] == "skincare routine"
        assert result["concern_type"] is None
        assert len(result["results"]) > 0
        assert result["confidence"] >= 0.0
    
    async def test_search_beauty_knowledge_base_tool(self):
        """Test the search tool function"""
        result = await search_beauty_knowledge_base("niacinamide for oily skin", "oiliness")
        
        import json
        parsed_result = json.loads(result)
        
        assert parsed_result["search_successful"] is True
        assert parsed_result["query"] == "niacinamide for oily skin"
        assert parsed_result["concern_focus"] == "oiliness"
        assert len(parsed_result["knowledge_items"]) > 0
    
    async def test_reasoning_step_tool(self):
        """Test the reasoning step tool function"""
        thought = "User has oily skin and mentions large pores"
        action = "Search for oil-controlling products with pore-minimizing ingredients"
        
        result = await reasoning_step(thought, action)
        
        import json
        parsed_result = json.loads(result)
        
        assert parsed_result["reasoning_step"] is True
        assert parsed_result["thought"] == thought
        assert parsed_result["action_needed"] == action
        assert parsed_result["step_type"] == "react_reasoning"


class TestErrorHandling:
    """Test error handling in the multi-agent system"""
    
    @patch('app.agents.letta.letta_agent')
    async def test_classification_fallback(self, mock_agent):
        """Test fallback behavior when classification fails"""
        mock_agent.classify_request = AsyncMock(side_effect=Exception("Classification failed"))
        
        with pytest.raises(RuntimeError, match="Failed to process beauty request"):
            await process_beauty_request("test query")
    
    async def test_rag_search_error_handling(self):
        """Test error handling in RAG search"""
        # Test with invalid concern type
        result = await search_beauty_knowledge_base("test query", "invalid_concern")
        
        import json
        parsed_result = json.loads(result)
        
        # Should still work but with concern_type set to None
        assert parsed_result["search_successful"] is True
        assert parsed_result["concern_focus"] is None


class TestAgentSpecialization:
    """Test specialized agent behavior"""
    
    @pytest.mark.parametrize("concern", [
        BeautyConcern.ACNE,
        BeautyConcern.AGING,
        BeautyConcern.SENSITIVITY,
        BeautyConcern.DRYNESS,
        BeautyConcern.OILINESS,
        BeautyConcern.HYPERPIGMENTATION,
        BeautyConcern.GENERAL
    ])
    @patch('app.agents.letta.letta_agent')
    async def test_concern_agent_creation(self, mock_agent, concern):
        """Test that each concern has a properly configured agent"""
        mock_agent.list_agents = AsyncMock(return_value=[])
        mock_agent.create_agent = AsyncMock(return_value={"id": f"agent-{concern.value}-123"})
        
        agent_id = await mock_agent.get_or_create_concern_agent(concern)
        
        mock_agent.create_agent.assert_called_once()
        call_args = mock_agent.create_agent.call_args
        
        assert f"beauty_{concern.value}_agent" in call_args[1]["name"]
        assert "ReAct methodology" in call_args[1]["instructions"]
        assert "reasoning_step tool" in call_args[1]["instructions"]


class TestIntegration:
    """Integration tests for the complete multi-agent system"""
    
    @pytest.mark.asyncio
    @patch('app.agents.letta.Letta')
    async def test_end_to_end_acne_query(self, mock_letta_class):
        """Test complete end-to-end processing of an acne query"""
        # Mock the entire Letta client behavior
        mock_client = Mock()
        mock_letta_class.return_value = mock_client
        
        # Mock agent creation
        classifier_agent = Mock()
        classifier_agent.id = "classifier-123"
        classifier_agent.dict.return_value = {"id": "classifier-123", "name": "beauty_classifier_agent"}
        
        acne_agent = Mock()
        acne_agent.id = "acne-123"
        acne_agent.dict.return_value = {"id": "acne-123", "name": "beauty_acne_agent"}
        
        mock_client.agents.create.side_effect = [classifier_agent, acne_agent]
        mock_client.agents.list.return_value = []
        
        # Mock chat responses
        classification_response = Mock()
        classification_response.messages = [Mock()]
        classification_response.messages[0].message_type = "assistant_message"
        classification_response.messages[0].content = '{"request_type": "concern", "beauty_concern": "acne", "confidence": 0.9, "reasoning": "User mentioned acne", "suggested_agent": "beauty_acne_agent"}'
        
        specialist_response = Mock()
        specialist_response.messages = [Mock()]
        specialist_response.messages[0].message_type = "assistant_message"
        specialist_response.messages[0].content = "For acne treatment, I recommend using salicylic acid products..."
        
        mock_client.agents.messages.create.side_effect = [
            classification_response,
            specialist_response
        ]
        
        # Test the complete pipeline
        result = await process_beauty_request("I have terrible acne, what should I do?")
        
        assert result["pipeline"] == "multi_agent_react"
        assert result["classification"]["beauty_concern"] == "acne"
        assert result["specialist_response"]["concern"] == "acne"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 