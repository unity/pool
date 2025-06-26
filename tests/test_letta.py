import pytest
from unittest.mock import AsyncMock, patch
from app.agents.letta import create_agent, list_agents, chat_with_agent


@pytest.mark.asyncio
async def test_create_agent():
    """Test creating a new Letta agent"""
    with patch('app.agents.letta.letta_agent._ensure_client') as mock_ensure_client:
        mock_client = AsyncMock()
        mock_ensure_client.return_value = mock_client
        
        mock_client.create_agent.return_value = {
            "id": "test-agent-123",
            "name": "Test Agent",
            "description": "A test agent",
            "instructions": "You are a helpful test agent"
        }
        
        result = await create_agent(
            name="Test Agent",
            description="A test agent",
            instructions="You are a helpful test agent"
        )
        
        assert result["id"] == "test-agent-123"
        assert result["name"] == "Test Agent"
        mock_client.create_agent.assert_called_once()


@pytest.mark.asyncio
async def test_list_agents():
    """Test listing all Letta agents"""
    with patch('app.agents.letta.letta_agent._ensure_client') as mock_ensure_client:
        mock_client = AsyncMock()
        mock_ensure_client.return_value = mock_client
        
        mock_client.list_agents.return_value = [
            {
                "id": "agent-1",
                "name": "Agent 1",
                "description": "First agent",
                "instructions": "Instructions for agent 1"
            },
            {
                "id": "agent-2", 
                "name": "Agent 2",
                "description": "Second agent",
                "instructions": "Instructions for agent 2"
            }
        ]
        
        result = await list_agents()
        
        assert len(result) == 2
        assert result[0]["name"] == "Agent 1"
        assert result[1]["name"] == "Agent 2"
        mock_client.list_agents.assert_called_once()


@pytest.mark.asyncio
async def test_chat_with_agent():
    """Test chatting with a Letta agent"""
    with patch('app.agents.letta.letta_agent._ensure_client') as mock_ensure_client:
        mock_client = AsyncMock()
        mock_ensure_client.return_value = mock_client
        
        mock_client.chat_with_agent.return_value = {
            "message": "Hello! I'm here to help you.",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        result = await chat_with_agent(
            agent_id="test-agent-123",
            message="Hello, how are you?",
            stream=False
        )
        
        assert result["message"] == "Hello! I'm here to help you."
        mock_client.chat_with_agent.assert_called_once_with(
            agent_id="test-agent-123",
            message="Hello, how are you?"
        ) 