#!/usr/bin/env python3
"""
Test script for Letta integration
Run this to verify that the beauty search agent is working correctly
"""

import asyncio
import os
from dotenv import load_dotenv
from app.agents.letta import search_beauty_products, get_or_create_beauty_search_agent

# Load environment variables
load_dotenv()

async def test_letta_integration():
    """Test the Letta beauty search integration"""
    print("🧪 Testing Letta Beauty Search Integration...")
    print("=" * 50)
    
    try:
        # Test 1: Create/get beauty search agent
        print("1. Creating/retrieving beauty search agent...")
        agent_id = await get_or_create_beauty_search_agent()
        print(f"   ✓ Agent ID: {agent_id}")
        
        # Test 2: Test search functionality
        test_queries = [
            "Products for dry sensitive skin",
            "Best anti-aging serums under $50",
            "What ingredients help with acne?"
        ]
        
        for i, query in enumerate(test_queries, 2):
            print(f"\n{i}. Testing query: '{query}'")
            try:
                result = await search_beauty_products(query)
                agent_response = result.get("agent_response", "")
                print(f"   ✓ Response length: {len(agent_response)} characters")
                print(f"   ✓ Preview: {agent_response[:100]}...")
                
            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
        
        print("\n🎉 Letta integration test completed!")
        print("\nTo use the search:")
        print("1. Start your FastAPI server: poetry run uvicorn app.main:app --reload")
        print("2. Open the frontend and try searching")
        print("3. The search will now use real Letta responses instead of mock data")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("\nPossible issues:")
        print("- Check that LETTA_BASE_URL is set correctly in .env")
        print("- Ensure Letta server is running")
        print("- Verify API keys are configured if needed")

if __name__ == "__main__":
    asyncio.run(test_letta_integration()) 