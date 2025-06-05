#!/usr/bin/env python3
"""
Test script for OpenAI Agents SDK integration with Movie Simulator
"""

import asyncio
import os
from agents import Agent, Runner, function_tool

# Set up OpenAI API key (you'll need to set this)
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

@function_tool
def create_movie_character(name: str, role: str, description: str) -> dict:
    """Create a movie character with the given details."""
    return {
        "character_name": name,
        "character_role": role,
        "character_description": description,
        "status": "created"
    }

@function_tool
def set_movie_genre(genre: str, setting: str) -> dict:
    """Set the movie genre and setting."""
    return {
        "genre": genre,
        "setting": setting,
        "status": "configured"
    }

async def test_openai_agents_sdk():
    """Test the OpenAI Agents SDK with movie creation tools."""
    
    # Create a movie director agent
    director = Agent(
        name="Movie Director",
        instructions="""You are a creative movie director. Use the provided tools to:
        1. Set the movie genre and setting using set_movie_genre
        2. Create 2-3 interesting characters using create_movie_character
        
        Make sure to actually use the tools, don't just describe what you would do.""",
        tools=[create_movie_character, set_movie_genre],
        model="gpt-4o-mini"
    )
    
    try:
        # Test with a story prompt
        story_prompt = "Create a thriller movie about a detective investigating mysterious disappearances in a remote mountain town"
        
        print("🎬 Testing OpenAI Agents SDK with Movie Director...")
        print(f"📝 Story Prompt: {story_prompt}")
        print("🤖 Running director agent...\n")
        
        result = await Runner.run(director, story_prompt)
        
        print("✅ Agent execution completed!")
        print(f"📋 Final Output:\n{result.final_output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OpenAI Agents SDK Test for Movie Simulator")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment")
        print("   Set it with: export OPENAI_API_KEY=your-key-here")
    
    # Run the test
    success = asyncio.run(test_openai_agents_sdk())
    
    if success:
        print("\n🎉 OpenAI Agents SDK is working correctly!")
        print("   Your movie simulator can now use the director agent.")
    else:
        print("\n❌ Test failed - check your OpenAI API key and connection.") 