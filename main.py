#!/usr/bin/env python3
"""
Movie Simulator - Phase 1 Foundation
Main execution script for testing the Movie Simulator with OpenAI Agents SDK.
"""

import asyncio
import os
from dotenv import load_dotenv

from movie_simulator.core.logger import get_logger, LogLevel

load_dotenv()
from typing import Optional

# Initialize logger
logger = get_logger("Main", LogLevel.INFO)

# Test imports and basic functionality
def test_basic_functionality():
    """Test basic system functionality before running full simulation."""
    logger.section_header("🧪 BASIC FUNCTIONALITY TEST", width=40)
    
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
        logger.success(f"Character Model: {test_char.name} ({test_char.story_role.value})", "test")
        
        # Test simulation creation
        simulation = MovieSimulation()
        logger.success("Simulation System: Initialized", "test")
        
        return True
        
    except Exception as e:
        logger.error("Basic functionality test failed", "test", e)
        return False


async def run_full_simulation():
    """Run the complete movie simulation."""
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set", "config")
        return
    
    logger.success("OpenAI API key configured", "config")
    
    # Check if agents are available
    try:
        from agents import Agent
        logger.success("OpenAI Agents SDK available", "api")
        agents_available = True
    except ImportError:
        logger.warning("OpenAI Agents SDK not available - using basic functionality", "api")
        agents_available = False
    
    logger.blank_line()
    
    # Story seeds for testing
    story_seeds = [
        "A murder mystery in a small tech company during a product launch. The victim is the CEO, found dead in the server room.",
        "A romantic comedy about two rival coffee shop owners who discover they're both trying to save the same historic neighborhood.",
        "A thriller about a data scientist who discovers their AI model is being used for illegal surveillance.",
        "A family drama about three siblings reuniting to settle their father's estate, only to discover he had a secret family."
    ]
    
    logger.info("📖 AVAILABLE STORY SEEDS:", "story")
    for i, seed in enumerate(story_seeds, 1):
        preview = seed[:80] + "..." if len(seed) > 80 else seed
        logger.list_item(f"{i}. {preview}")
    
    # Use the first story seed for testing
    selected_story = story_seeds[0]
    preview = selected_story[:100] + "..." if len(selected_story) > 100 else selected_story
    logger.info(f"🎯 Selected Story: {preview}", "story")
    
    # Run simulation
    from movie_simulator.core.simulation import MovieSimulation
    
    logger.section_header("SIMULATION EXECUTION")
    simulation = MovieSimulation()
    result = await simulation.run_simulation(selected_story)
    
    logger.section_header("📋 FINAL SIMULATION OUTPUT")
    logger.info(result)


async def main():
    """Main execution function."""
    logger.section_header("🎬 MOVIE SIMULATOR - PHASE 1 FOUNDATION")
    
    # Test basic functionality first
    if not test_basic_functionality():
        logger.blank_line()
        logger.error("Basic tests failed. Please check your setup.", "test")
        return
    
    logger.blank_line()
    logger.success("Basic tests passed! Proceeding with full simulation...", "test")
    logger.blank_line()
    
    # Run full simulation
    await run_full_simulation()


if __name__ == "__main__":
    asyncio.run(main())