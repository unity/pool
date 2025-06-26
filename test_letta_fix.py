#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from agents.letta import list_agents, create_agent

async def test_letta_connection():
    """Test the Letta connection and basic operations"""
    try:
        print("Testing Letta connection...")
        
        # Test listing agents
        agents = await list_agents()
        print(f"✅ Successfully connected to Letta! Found {len(agents)} agents.")
        
        # Test creating an agent
        print("Testing agent creation...")
        test_agent = await create_agent(
            name="test_agent_connection",
            description="Test agent to verify connection",
            instructions="You are a test agent. Respond briefly to verify you're working."
        )
        print(f"✅ Successfully created test agent: {test_agent.get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Letta connection: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_letta_connection())
    if result:
        print("\n🎉 Letta integration is working correctly!")
    else:
        print("\n💥 Letta integration needs attention.") 