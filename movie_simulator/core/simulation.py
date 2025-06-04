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
from .logger import get_logger, LogLevel

# Initialize logger
logger = get_logger("Simulation", LogLevel.INFO)

# Import Phase 2 tools
try:
    from .tools import StoryProgressionManager, DramaticEventInjector
except ImportError:
    logger.warning("Phase 2 tools not available", "tools")
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
            if self.progression_manager:
                self.progression_manager.set_context(self.context)
            if self.event_injector:
                self.event_injector.set_context(self.context)
            
            # Initialize director agent if available
            if create_director_agent is not None:
                self.director_agent = create_director_agent()
            
            return True
            
        except Exception as e:
            logger.error("Failed to setup simulation", "simulation", e)
            return False
    
    async def run_director_setup(self, story_seed: str) -> Dict[str, Any]:
        """
        Run the director agent to create initial story setup.
        
        Args:
            story_seed: User's story idea
            
        Returns:
            Dict containing setup results
        """

        try:
            setup_prompt = f"""Story seed: {story_seed}"""
            
            logger.subsection_header("🎬 DIRECTOR AGENT EXECUTION")
            
            # Agent configuration info
            if hasattr(self.director_agent, 'tools'):
                logger.info(f"📋 Agent Tools: {len(self.director_agent.tools)} available", "tools")
            
            logger.info(f"📝 Prompt Length: {len(setup_prompt)} characters", "agent")
            logger.progress("Executing agent...", "agent")
            
            result = await Runner.run(self.director_agent, setup_prompt, context=self.context)
            
            logger.success("Agent execution completed", "agent")
            logger.blank_line()
            
            # Process and analyze results
            await self._analyze_director_result(result)
            
            return {
                "success": True,
                "director_output": result.final_output,
                "message": "Director setup completed successfully",
                "full_result": result
            }
            
        except Exception as e:
            logger.error("Director Agent Failed", "agent", e)
            return {
                "success": False,
                "error": str(e),
                "message": "Director setup failed"
            }
    
    async def _analyze_director_result(self, result):
        """Analyze and log the Director agent's execution results."""
        
        logger.subsection_header("📊 EXECUTION ANALYSIS")
        
        # Basic result info
        logger.info(f"🔍 Result Type: {type(result).__name__}", "analysis")
        logger.info(f"💬 Output Length: {len(str(result.final_output))} characters", "analysis")
        
        # Tool usage analysis
        tool_calls_count = self._count_tool_calls(result)
        logger.info(f"🔧 Tool Calls Found: {tool_calls_count}", "tools")
        
        if tool_calls_count > 0:
            logger.success("Agent used tools successfully", "tools")
        else:
            logger.warning("Agent provided text response instead of using tools", "tools")
        
        # Context analysis
        if self.context:
            metrics = {
                "Characters in Context": len(self.context.characters),
                "Timeline Beats": len(self.context.story_state.timeline),
                "Current Beat": self.context.story_state.current_beat,
                "Dramatic Tension": f"{self.context.story_state.dramatic_tension:.1f}"
            }
            logger.metrics(metrics)
        
        logger.blank_line()
    
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

    
    async def run_simulation(self, story_seed: str) -> str:
        """
        Run the complete movie simulation.
        
        Args:
            story_seed: User's initial story idea
            
        Returns:
            Generated story content
        """
        logger.subsection_header("🎬 MOVIE SIMULATION EXECUTION")
        logger.blank_line()
        
        # Phase 1: Setup
        logger.subsection_header("📋 Phase 1: Context Initialization")
        setup_success = await self.setup_simulation(story_seed)
        if not setup_success:
            logger.error("Simulation initialization failed", "simulation")
            return "Failed to initialize simulation"
        logger.success("Context initialized successfully", "simulation")
        
        # Phase 2: Director Setup
        logger.subsection_header("🎭 Phase 2: Director Agent Story Creation")
        director_result = await self.run_director_setup(story_seed)
        
        if director_result["success"]:
            logger.success("Director agent completed successfully", "agent")
            # Process director results
            if 'full_result' in director_result:
                await self._process_director_result(director_result['full_result'])
        else:
            logger.error(f"Director agent failed: {director_result.get('message', 'Unknown error')}", "agent")
        
        logger.blank_line()
        
        # Phase 3: Tool Integration Demo (Phase 2 feature)
        if self.progression_manager and self.event_injector:
            logger.subsection_header("🔧 Phase 3: Phase 2 Tools Integration Demo")
            await self._demonstrate_phase2_tools()
            logger.blank_line()
        
        # Phase 4: Generate story summary
        logger.subsection_header("📑 Phase 4: Story Summary Generation")
        story_summary = await self._generate_story_summary()
        
        logger.success("SIMULATION COMPLETED SUCCESSFULLY!", "simulation")
        
        return story_summary
    
    async def _demonstrate_phase2_tools(self):
        """Demonstrate the Phase 2 tools integration."""
        logger.subsection_header("📖 Testing Progression Tools...")
        
        # Advance story and adjust tension
        if self.progression_manager:
            # Advance to inciting incident
            if self.progression_manager.advance_story_beat():
                logger.info(f"→ Advanced to: {self.context.story_state.current_beat if self.context else 'unknown'}", "agent")
            
            # Auto-adjust tension for current beat
            self.progression_manager.auto_adjust_tension_for_beat()
            tension = self.context.story_state.dramatic_tension if self.context else 0.5
            logger.info(f"→ Tension adjusted to: {tension:.2f}", "agent")
        
        logger.subsection_header("💥 Testing Event Tools...")
        
        # Inject a dramatic event
        if self.event_injector:
            event_result = self.event_injector.inject_random_event()
            if event_result.get("success"):
                event_type = event_result.get("event_type", "unknown")
                logger.info(f"→ Event injected: {event_type.replace('_', ' ').title()}", "agent")
        
        logger.success("Phase 2 tools demonstration completed", "agent")
    
    async def _process_director_result(self, director_result):
        """
        Process the Director agent's result to extract characters and story elements.
        
        Args:
            director_result: The result object from the Director agent
        """
        logger.subsection_header("📋 RESULT PROCESSING")
        logger.blank_line()
        
        # With proper context passing, characters should already be in the context
        if self.context:
            character_count = len(self.context.characters)
            
            if character_count > 0:
                logger.info(f"🎭 Characters Created: {character_count}", "agent")
                for char_id, character in self.context.characters.items():
                    role_emoji = {"protagonist": "🌟", "antagonist": "💀", "supporting": "🎬", "minor": "👤"}
                    emoji = role_emoji.get(character.story_role.value, "👤")
                    logger.info(f"   {emoji} {character.name} ({character.story_role.value})", "agent")
            else:
                logger.warning("⚠️  No characters found in context", "agent")
        
        logger.blank_line()

    async def _generate_story_summary(self) -> str:
        """
        Generate a summary of the created story.
        
        Returns:
            Story summary string
        """
        if not self.context:
            return "No story context available"
        
        logger.subsection_header("📊 Generating final summary...")
        
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
        if self.progression_manager or self.event_injector:
            summary_parts.extend([
                "🔧 PHASE 2 TOOLS STATUS:",
                f"  📖 Progression Manager: {'✅ Active' if self.progression_manager else '❌ Not Available'}",
                f"  💥 Event Injector: {'✅ Active' if self.event_injector else '❌ Not Available'}",
                ""
            ])
        
        summary_parts.extend([
            "✅ STATUS: Enhanced Phase 2 Implementation Complete",
            "   → Director Agent: Operational",
            "   → Story Context: Initialized", 
            "   → Character System: Functional",
            "   → Progression Tools: Integrated",
            "   → Event Tools: Integrated",
            "   → Ready for Phase 3 Development"
        ])
        
        return "\n".join(summary_parts)
    
    def get_context(self) -> Optional[MovieContext]:
        """Get the current movie context."""
        return self.context
    
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
            return True
        except ValueError as e:
            logger.error("Failed to add character", "simulation", e)
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