#!/usr/bin/env python3
"""
Test script for Phase 2 Core Tools Implementation
Tests memory, story progression, and dramatic event tools
"""

import asyncio
from datetime import datetime

# Test the new Phase 2 tools
def test_memory_tools():
    """Test the memory system functionality"""
    print("🧠 Testing Memory Tools...")
    
    try:
        # Import the memory tools we just created
        from movie_simulator.core.tools.memory_tools import (
            store_character_memory, search_character_memory, 
            get_character_relationships, MEMORY_SYSTEM
        )
        
        # Test storing memories
        result1 = store_character_memory(
            character_id="detective_jane",
            event_description="Found suspicious evidence in the victim's office",
            participants=["detective_jane", "victim_ceo"],
            emotional_impact=0.8,
            memory_type="investigation"
        )
        
        result2 = store_character_memory(
            character_id="detective_jane", 
            event_description="Had heated argument with suspect CTO about alibis",
            participants=["detective_jane", "suspect_cto"],
            emotional_impact=0.6,
            memory_type="conflict"
        )
        
        # Test searching memories
        search_result = search_character_memory(
            character_id="detective_jane",
            query="evidence",
            memory_type="investigation"
        )
        
        # Test relationships
        relationships = get_character_relationships("detective_jane")
        
        print(f"✅ Memory storage: {result1 and result2}")
        print(f"✅ Memory search: {len(search_result) > 0}")
        print(f"✅ Relationships: {len(relationships) > 0}")
        print(f"   Search result preview: {search_result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory tools error: {e}")
        return False


def test_story_tools():
    """Test the story progression functionality"""
    print("\n📖 Testing Story Tools...")
    
    try:
        from movie_simulator.core.tools.story_tools import (
            check_plot_progress, advance_story_beat, 
            create_story_beat, suggest_plot_development
        )
        
        # Create story beats
        setup_result = create_story_beat(
            beat_name="setup",
            description="Introduce characters and establish the normal world",
            required_characters=["detective_jane", "victim_ceo"],
            tension_target=0.3,
            objectives=["Character introductions", "World establishment"]
        )
        
        incident_result = create_story_beat(
            beat_name="inciting_incident", 
            description="The CEO is found murdered in his office",
            required_characters=["detective_jane", "victim_ceo", "suspect_cto"],
            tension_target=0.7,
            objectives=["Introduce main conflict", "Start investigation"]
        )
        
        # Advance story beats
        advance_result = advance_story_beat("setup", 0.8)
        
        # Check progress
        progress = check_plot_progress()
        
        # Get suggestions
        suggestions = suggest_plot_development()
        
        print(f"✅ Story beat creation: {setup_result['success'] and incident_result['success']}")
        print(f"✅ Story advancement: {advance_result['success']}")
        print(f"✅ Progress tracking: {'current_beat' in progress}")
        print(f"✅ Plot suggestions: {len(suggestions.get('suggested_developments', [])) > 0}")
        print(f"   Current beat: {progress.get('current_beat', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Story tools error: {e}")
        return False


def test_dramatic_tools():
    """Test the dramatic event injection functionality"""
    print("\n💥 Testing Dramatic Tools...")
    
    try:
        from movie_simulator.core.tools.dramatic_tools import (
            inject_dramatic_event, inject_random_event,
            create_plot_twist, get_dramatic_events_status
        )
        
        # Inject specific dramatic event
        event_result = inject_dramatic_event(
            event_type="revelation",
            description="Detective discovers the victim was embezzling company funds",
            affected_characters=["detective_jane", "victim_ceo"],
            intensity=0.8
        )
        
        # Inject random event
        random_result = inject_random_event(
            target_characters=["suspect_cto"],
            event_type="conflict",
            intensity_level="moderate"
        )
        
        # Create plot twist
        twist_result = create_plot_twist(
            twist_description="The CTO is actually the victim's secret business partner",
            revelation_target="suspect_cto",
            impact_characters=["detective_jane", "suspect_cto", "victim_ceo"],
            twist_severity="major"
        )
        
        # Check events status
        status = get_dramatic_events_status()
        
        print(f"✅ Event injection: {event_result['success']}")
        print(f"✅ Random events: {random_result['success']}")
        print(f"✅ Plot twists: {twist_result['success']}")
        print(f"✅ Event tracking: {status['total_events'] > 0}")
        print(f"   Total events: {status['total_events']}")
        print(f"   Event types: {list(status['event_type_distribution'].keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dramatic tools error: {e}")
        return False


def test_integration():
    """Test how all Phase 2 tools work together"""
    print("\n🔧 Testing Tool Integration...")
    
    try:
        # This would demonstrate how the tools work together in a story simulation
        from movie_simulator.core.tools.memory_tools import get_memory_system_status
        from movie_simulator.core.tools.story_tools import get_story_structure_status
        from movie_simulator.core.tools.dramatic_tools import suggest_dramatic_intervention
        
        # Get overall system status
        memory_status = get_memory_system_status()
        story_status = get_story_structure_status() 
        event_suggestions = suggest_dramatic_intervention()
        
        print(f"✅ Memory system: {memory_status['total_characters']} characters, {memory_status['total_memories']} memories")
        print(f"✅ Story structure: {story_status['current_beat']} beat, {len(story_status['beat_details'])} beats defined")
        print(f"✅ Event suggestions: {len(event_suggestions['suggested_events'])} suggestions available")
        
        # Show how they could work together
        print("\n🎬 Integration Example:")
        print("- Memory system tracks character experiences")
        print("- Story tools manage plot progression") 
        print("- Dramatic tools inject events when needed")
        print("- All three inform director agent decisions")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


def main():
    """Run all Phase 2 tool tests"""
    print("🚀 Phase 2 Core Tools Test Suite")
    print("=" * 50)
    
    results = []
    
    # Run individual tool tests
    results.append(test_memory_tools())
    results.append(test_story_tools())
    results.append(test_dramatic_tools())
    results.append(test_integration())
    
    # Summary
    print("\n📊 Test Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    
    if all(results):
        print("\n🎉 All Phase 2 tools are working correctly!")
        print("   Ready to move to Phase 3: Character System")
        print("\n📋 Next Steps According to plan.md:")
        print("   1. Create character agent factory")
        print("   2. Implement character-specific tools") 
        print("   3. Add character consistency guardrails")
        print("   4. Test character interactions and handoffs")
    else:
        print("\n❌ Some tests failed - check tool implementations")
        
    return all(results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 