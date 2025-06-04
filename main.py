#!/usr/bin/env python3
"""
Movie Simulator - Phase 1 Foundation
Main execution script for testing the Movie Simulator with OpenAI Agents SDK.
"""

import asyncio
import os
from dotenv import load_dotenv

from movie_simulator.core.agents.director import director_main

load_dotenv()
from typing import Optional

# Test imports and basic functionality
def test_basic_functionality():
    """Test basic system functionality before running full simulation."""
    print("🧪 BASIC FUNCTIONALITY TEST")
    print("-" * 40)
    
    try:
        from movie_simulator.core.models.story_models import CharacterProfile, CharacterRole
        from movie_simulator.core.simulation import MovieSimulation
        
        # Test character creation
        test_char = CharacterProfile(
            id="test_detective",
            name="Test Detective",
            background="Experienced investigator",
            personality_traits=["analytical", "determined"],
            primary_motivation="Solve the case",
            secrets=["Has a personal connection to the case"],
            secondary_goals=[],
            fears=[],
            story_role=CharacterRole.PROTAGONIST
        )
        print(f"✅ Character Model: {test_char.name} ({test_char.story_role.value})")
        
        # Test simulation creation
        simulation = MovieSimulation()
        print(f"✅ Simulation System: Initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


async def run_full_simulation():
    """Run the complete movie simulation."""
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    print("✅ OpenAI API key configured")
    
    # Check if agents are available
    try:
        from agents import Agent
        print("✅ OpenAI Agents SDK available")
        agents_available = True
    except ImportError:
        print("⚠️  OpenAI Agents SDK not available - using basic functionality")
        agents_available = False
    
    print("")
    
    # Story seeds for testing
    story_seeds = [
        "A murder mystery in a small tech company during a product launch. The victim is the CEO, found dead in the server room.",
        "A romantic comedy about two rival coffee shop owners who discover they're both trying to save the same historic neighborhood.",
        "A thriller about a data scientist who discovers their AI model is being used for illegal surveillance.",
        "A family drama about three siblings reuniting to settle their father's estate, only to discover he had a secret family."
    ]
    
    print("📖 AVAILABLE STORY SEEDS:")
    for i, seed in enumerate(story_seeds, 1):
        preview = seed[:80] + "..." if len(seed) > 80 else seed
        print(f"   {i}. {preview}")
    
    # Use the first story seed for testing
    selected_story = story_seeds[0]
    preview = selected_story[:100] + "..." if len(selected_story) > 100 else selected_story
    print(f"\n🎯 Selected Story: {preview}")
    
    # Run simulation
    from movie_simulator.core.simulation import MovieSimulation
    
    print("\n" + "=" * 70)
    simulation = MovieSimulation()
    result = await simulation.run_simulation(selected_story)
    
    print("\n📋 FINAL SIMULATION OUTPUT:")
    print("=" * 70)
    print(result)


async def main():
    """Main execution function."""
    print("🎬 MOVIE SIMULATOR - PHASE 1 FOUNDATION")
    print("=" * 70)
    
    # Test basic functionality first
    if not test_basic_functionality():
        print("\n❌ Basic tests failed. Please check your setup.")
        return
    
    print("\n🚀 Basic tests passed! Proceeding with full simulation...\n")
    
    # Run full simulation
    await run_full_simulation()


if __name__ == "__main__":
    asyncio.run(main())