#!/usr/bin/env python3
"""
Autonomous Storytelling Test
Test the fully autonomous flow where user provides seed and AI does everything else.
"""

import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_autonomous_storytelling():
    """Test the fully autonomous storytelling flow."""
    print("🎬 AUTONOMOUS STORYTELLING TEST")
    print("="*50)
    
    try:
        from movie_simulator.core.simulation import MovieSimulation
        
        # Create simulation
        simulation = MovieSimulation()
        
        # User provides just a story seed
        story_seed = "A tech company murder during a product launch"
        print(f"📝 Story Seed: {story_seed}")
        print("\n🤖 Starting autonomous AI storytelling...")
        print("   (Characters will be created and interact autonomously)")
        
        # Run fully autonomous simulation
        story_result = await simulation.run_simulation(story_seed)
        
        print("\n" + "="*70)
        print("🎉 AUTONOMOUS STORYTELLING COMPLETE!")
        print("="*70)
        print(story_result)
        
        return True
        
    except Exception as e:
        print(f"❌ Autonomous storytelling failed: {e}")
        logger.error(f"Error: {e}", exc_info=True)
        return False

def main():
    """Main entry point."""
    print("🚀 Testing Autonomous AI Storytelling")
    print("   User provides seed → AI does everything autonomously")
    
    try:
        success = asyncio.run(test_autonomous_storytelling())
        
        if success:
            print("\n✅ Autonomous storytelling system working!")
        else:
            print("\n❌ Autonomous storytelling needs debugging")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main() 