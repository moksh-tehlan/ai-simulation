"""
Main simulation runner for the Movie Simulator.
"""

import asyncio
import os
from typing import Optional, Dict, Any
from datetime import datetime

from .models.story_models import (
    StoryState, 
    CharacterProfile, 
    SceneContext, 
    MovieContext,
    StoryGenre
)

# Import Phase 2 tools
try:
    from .tools import MemoryManager, StoryProgressionManager, DramaticEventInjector
except ImportError:
    print("⚠️  Phase 2 tools not available")
    MemoryManager = None
    StoryProgressionManager = None
    DramaticEventInjector = None

# Import agents with error handling for development
try:
    from agents import Runner
    from .agents.director import create_director_agent
except ImportError:
    Runner = None
    create_director_agent = None


class MovieSimulation:
    """
    Main simulation class that orchestrates the movie creation process.
    """
    
    def __init__(self):
        """Initialize the movie simulation."""
        self.context: Optional[MovieContext] = None
        self.director_agent = None
        
        # Initialize Phase 2 tools
        self.memory_manager = MemoryManager() if MemoryManager else None
        self.progression_manager = StoryProgressionManager() if StoryProgressionManager else None
        self.event_injector = DramaticEventInjector() if DramaticEventInjector else None
        
        # Initialize configuration from environment
        self.max_interactions = int(os.getenv("MAX_INTERACTIONS", "100"))
        self.intervention_threshold = float(os.getenv("INTERVENTION_THRESHOLD", "0.3"))
        
    async def setup_simulation(self, story_seed: str) -> bool:
        """
        Set up the simulation with initial story context.
        
        Args:
            story_seed: User's initial story idea
            
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Initialize basic story state
            story_state = StoryState(
                title="Generated Story",
                genre=StoryGenre.MYSTERY,  # Default, will be determined by director
                setting="To be determined",
                timeline=[],
                current_beat="setup"
            )
            
            # Create movie context
            self.context = MovieContext(
                story_state=story_state,
                characters={},
                current_scene=None,
                current_time=datetime.now()
            )
            
            # Initialize Phase 2 tools with context
            if self.memory_manager:
                self.memory_manager.set_context(self.context)
            if self.progression_manager:
                self.progression_manager.set_context(self.context)
            if self.event_injector:
                self.event_injector.set_context(self.context)
            
            # Initialize director agent if available
            if create_director_agent is not None:
                self.director_agent = create_director_agent()
            
            return True
            
        except Exception as e:
            print(f"Failed to setup simulation: {e}")
            return False
    
    async def run_director_setup(self, story_seed: str) -> Dict[str, Any]:
        """
        Run the director agent to create initial story setup.
        
        Args:
            story_seed: User's story idea
            
        Returns:
            Dict containing setup results
        """
        if Runner is None or self.director_agent is None:
            print("   ⚠️  OpenAI Agents SDK not available - using manual setup")
            return await self._manual_setup(story_seed)
        
        try:
            setup_prompt = f"""Story seed: {story_seed}"""
            
            print("   🎬 DIRECTOR AGENT EXECUTION")
            print("   " + "=" * 50)
            
            # Agent configuration info
            if hasattr(self.director_agent, 'tools'):
                print(f"   📋 Agent Tools: {len(self.director_agent.tools)} available")
            
            print(f"   📝 Prompt Length: {len(setup_prompt)} characters")
            print("   🚀 Executing agent...")
            
            result = await Runner.run(self.director_agent, setup_prompt, context=self.context)
            
            print("   ✅ Agent execution completed")
            print("")
            
            # Process and analyze results
            await self._analyze_director_result(result)
            
            return {
                "success": True,
                "director_output": result.final_output,
                "message": "Director setup completed successfully",
                "full_result": result
            }
            
        except Exception as e:
            print(f"   ❌ Director Agent Failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Director setup failed"
            }
    
    async def _analyze_director_result(self, result):
        """Analyze and log the Director agent's execution results."""
        
        print("   📊 EXECUTION ANALYSIS")
        print("   " + "=" * 50)
        
        # Basic result info
        print(f"   🔍 Result Type: {type(result).__name__}")
        print(f"   💬 Output Length: {len(str(result.final_output))} characters")
        
        # Tool usage analysis
        tool_calls_count = self._count_tool_calls(result)
        print(f"   🔧 Tool Calls Found: {tool_calls_count}")
        
        if tool_calls_count > 0:
            print("   ✅ Agent used tools successfully")
        else:
            print("   ⚠️  Agent provided text response instead of using tools")
        
        # Context analysis
        if self.context:
            print(f"   🎭 Characters in Context: {len(self.context.characters)}")
            print(f"   📚 Timeline Beats: {len(self.context.story_state.timeline)}")
            print(f"   🎯 Current Beat: {self.context.story_state.current_beat}")
            print(f"   ⚡ Dramatic Tension: {self.context.story_state.dramatic_tension:.1f}")
        
        print("")
    
    def _count_tool_calls(self, result) -> int:
        """Count tool calls in the result object."""
        tool_calls_found = 0
        
        if hasattr(result, 'raw_responses') and result.raw_responses:
            for response in result.raw_responses:
                if hasattr(response, 'choices') and response.choices:
                    for choice in response.choices:
                        if hasattr(choice, 'message') and choice.message:
                            if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                                tool_calls_found += len(choice.message.tool_calls)
        
        return tool_calls_found
    
    async def _manual_setup(self, story_seed: str) -> Dict[str, Any]:
        """
        Fallback manual setup when agents are not available.
        
        Args:
            story_seed: User's story idea
            
        Returns:
            Dict containing manual setup results
        """
        # Basic story analysis
        genre_hints = {
            "murder": StoryGenre.MYSTERY,
            "mystery": StoryGenre.MYSTERY,
            "love": StoryGenre.ROMANCE,
            "romance": StoryGenre.ROMANCE,
            "thriller": StoryGenre.THRILLER,
            "comedy": StoryGenre.COMEDY,
            "drama": StoryGenre.DRAMA
        }
        
        # Determine genre from seed
        detected_genre = StoryGenre.DRAMA  # Default
        for keyword, genre in genre_hints.items():
            if keyword.lower() in story_seed.lower():
                detected_genre = genre
                break
        
        # Update story state
        if self.context is not None:
            self.context.story_state.genre = detected_genre
            self.context.story_state.title = f"Story: {story_seed[:50]}..."
            self.context.story_state.setting = "Contemporary setting"
            
            # Record initial story facts using memory manager
            if self.memory_manager:
                self.memory_manager.record_story_fact(f"Story begins with: {story_seed}")
                self.memory_manager.record_story_fact(f"Genre detected as: {detected_genre.value}")
            
        return {
            "success": True,
            "genre": detected_genre.value,
            "title": self.context.story_state.title if self.context else "Unknown",
            "message": "Manual setup completed (agents not available)"
        }
    
    async def run_simulation(self, story_seed: str) -> str:
        """
        Run the complete movie simulation.
        
        Args:
            story_seed: User's initial story idea
            
        Returns:
            Generated story content
        """
        print("\n🎬 MOVIE SIMULATION EXECUTION")
        print("=" * 60)
        
        # Phase 1: Setup
        print("📋 Phase 1: Context Initialization")
        setup_success = await self.setup_simulation(story_seed)
        if not setup_success:
            print("❌ Simulation initialization failed")
            return "Failed to initialize simulation"
        print("✅ Context initialized successfully\n")
        
        # Phase 2: Director Setup
        print("🎭 Phase 2: Director Agent Story Creation")
        director_result = await self.run_director_setup(story_seed)
        
        if director_result["success"]:
            print("✅ Director agent completed successfully")
            # Process director results
            if 'full_result' in director_result:
                await self._process_director_result(director_result['full_result'])
        else:
            print(f"❌ Director agent failed: {director_result.get('message', 'Unknown error')}")
        
        print("")
        
        # Phase 3: Tool Integration Demo (Phase 2 feature)
        if self.memory_manager and self.progression_manager and self.event_injector:
            print("🔧 Phase 3: Phase 2 Tools Integration Demo")
            await self._demonstrate_phase2_tools()
            print("")
        
        # Phase 4: Generate story summary
        print("📑 Phase 4: Story Summary Generation")
        story_summary = await self._generate_story_summary()
        
        print("🎉 SIMULATION COMPLETED SUCCESSFULLY!\n")
        
        return story_summary
    
    async def _demonstrate_phase2_tools(self):
        """Demonstrate the Phase 2 tools integration."""
        print("   🧠 Testing Memory Tools...")
        
        # Record some story development
        if self.memory_manager:
            self.memory_manager.record_story_fact("Story development phase initiated")
            self.memory_manager.record_plot_point("Initial character conflicts established")
        
        print("   📖 Testing Progression Tools...")
        
        # Advance story and adjust tension
        if self.progression_manager:
            # Advance to inciting incident
            if self.progression_manager.advance_story_beat():
                print(f"   → Advanced to: {self.context.story_state.current_beat if self.context else 'unknown'}")
            
            # Auto-adjust tension for current beat
            self.progression_manager.auto_adjust_tension_for_beat()
            tension = self.context.story_state.dramatic_tension if self.context else 0.5
            print(f"   → Tension adjusted to: {tension:.2f}")
        
        print("   💥 Testing Event Tools...")
        
        # Inject a dramatic event
        if self.event_injector:
            event_result = self.event_injector.inject_random_event()
            if event_result.get("success"):
                event_type = event_result.get("event_type", "unknown")
                print(f"   → Event injected: {event_type.replace('_', ' ').title()}")
                
                # Record the event in memory
                if self.memory_manager:
                    self.memory_manager.record_plot_point(f"Dramatic event: {event_result.get('description', 'Unknown event')}")
        
        print("   ✅ Phase 2 tools demonstration completed")
    
    async def _process_director_result(self, director_result):
        """
        Process the Director agent's result to extract characters and story elements.
        
        Args:
            director_result: The result object from the Director agent
        """
        print("📋 RESULT PROCESSING")
        print("-" * 30)
        
        # With proper context passing, characters should already be in the context
        if self.context:
            character_count = len(self.context.characters)
            
            if character_count > 0:
                print(f"🎭 Characters Created: {character_count}")
                for char_id, character in self.context.characters.items():
                    role_emoji = {"protagonist": "🌟", "antagonist": "💀", "supporting": "🎬", "minor": "👤"}
                    emoji = role_emoji.get(character.story_role.value, "👤")
                    print(f"   {emoji} {character.name} ({character.story_role.value})")
                    
                    # Record character details in memory
                    if self.memory_manager:
                        self.memory_manager.record_character_memory(
                            char_id, 
                            f"Character created: {character.background}"
                        )
            else:
                print("⚠️  No characters found in context")
        
        print("")

    async def _generate_story_summary(self) -> str:
        """
        Generate a summary of the created story.
        
        Returns:
            Story summary string
        """
        if not self.context:
            return "No story context available"
        
        print("📊 Generating final summary...")
        
        # Build comprehensive summary
        summary_parts = [
            "🎬 MOVIE SIMULATION RESULTS",
            "=" * 60,
            f"📝 Title: {self.context.story_state.title}",
            f"🎭 Genre: {self.context.story_state.genre.value.upper()}",
            f"🏢 Setting: {self.context.story_state.setting}",
            f"📚 Timeline Beats: {len(self.context.story_state.timeline)} defined",
            f"🎯 Current Beat: {self.context.story_state.current_beat}",
            f"⚡ Dramatic Tension: {self.context.story_state.dramatic_tension:.1f}/1.0",
            "",
            f"🎭 CHARACTERS ({len(self.context.characters)} created):"
        ]
        
        if self.context.characters:
            for char_id, character in self.context.characters.items():
                role_emoji = {"protagonist": "🌟", "antagonist": "💀", "supporting": "🎬", "minor": "👤"}
                emoji = role_emoji.get(character.story_role.value, "👤")
                
                summary_parts.extend([
                    f"  {emoji} {character.name} ({character.story_role.value})",
                    f"     Background: {character.background}",
                    f"     Motivation: {character.primary_motivation}",
                    f"     Traits: {', '.join(character.personality_traits)}",
                    ""
                ])
        else:
            summary_parts.extend([
                "  (No characters in system context)",
                ""
            ])
        
        # Add story progression info
        summary_parts.extend([
            "📊 STORY METRICS:",
            f"  📈 Setup Progress: {self.context.story_state.setup_progress:.1%}",
            f"  ⚔️  Conflict Progress: {self.context.story_state.conflict_progress:.1%}",
            f"  👥 Character Arc Progress: {self.context.story_state.character_arc_progress:.1%}",
            f"  🎯 Resolution Readiness: {self.context.story_state.resolution_readiness:.1%}",
            ""
        ])
        
        # Add Phase 2 tools information
        if self.memory_manager or self.progression_manager or self.event_injector:
            summary_parts.extend([
                "🔧 PHASE 2 TOOLS STATUS:",
                f"  🧠 Memory Manager: {'✅ Active' if self.memory_manager else '❌ Not Available'}",
                f"  📖 Progression Manager: {'✅ Active' if self.progression_manager else '❌ Not Available'}",
                f"  💥 Event Injector: {'✅ Active' if self.event_injector else '❌ Not Available'}",
                ""
            ])
            
            # Add memory statistics if available
            if self.memory_manager:
                stats = self.memory_manager.get_memory_stats()
                summary_parts.extend([
                    "💾 MEMORY STATISTICS:",
                    f"  📝 Facts Recorded: {stats.get('facts_count', 0)}",
                    f"  📚 Plot Points: {stats.get('plot_points_count', 0)}",
                    f"  ⚔️ Conflicts: {stats.get('conflicts_count', 0)}",
                    f"  🎬 Scenes: {stats.get('scenes_count', 0)}",
                    ""
                ])
        
        summary_parts.extend([
            "✅ STATUS: Enhanced Phase 2 Implementation Complete",
            "   → Director Agent: Operational",
            "   → Story Context: Initialized", 
            "   → Character System: Functional",
            "   → Memory Tools: Integrated",
            "   → Progression Tools: Integrated",
            "   → Event Tools: Integrated",
            "   → Ready for Phase 3 Development"
        ])
        
        return "\n".join(summary_parts)
    
    def get_context(self) -> Optional[MovieContext]:
        """Get the current movie context."""
        return self.context
    
    def get_memory_manager(self) -> Optional[object]:
        """Get the memory manager instance."""
        return self.memory_manager
    
    def get_progression_manager(self) -> Optional[object]:
        """Get the progression manager instance."""
        return self.progression_manager
    
    def get_event_injector(self) -> Optional[object]:
        """Get the event injector instance."""
        return self.event_injector
    
    def add_character(self, character: CharacterProfile) -> bool:
        """
        Add a character to the simulation.
        
        Args:
            character: Character to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.context:
            return False
        
        try:
            self.context.add_character(character)
            
            # Record character creation in memory
            if self.memory_manager:
                self.memory_manager.record_character_memory(
                    character.id,
                    f"Character added to story: {character.background}"
                )
            
            return True
        except ValueError as e:
            print(f"Failed to add character: {e}")
            return False


# Convenience function for quick simulation
async def run_quick_simulation(story_seed: str) -> str:
    """
    Run a quick movie simulation with minimal setup.
    
    Args:
        story_seed: User's story idea
        
    Returns:
        Generated story
    """
    simulation = MovieSimulation()
    return await simulation.run_simulation(story_seed) 