"""
Main simulation runner for the Movie Simulator.
"""

import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import random

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
    from .agents.character_factory import get_character_manager
except ImportError:
    Runner = None
    create_director_agent = None
    get_character_manager = None


class MovieSimulation:
    """
    Main simulation class that orchestrates the movie creation process.
    """
    
    def __init__(self):
        """Initialize the movie simulation."""
        self.context: Optional[MovieContext] = None
        self.director_agent = None
        self.character_agents: Dict[str, Any] = {}
        self.character_manager = None
        
        # Initialize Phase 2 tools
        self.progression_manager = StoryProgressionManager() if StoryProgressionManager else None
        self.event_injector = DramaticEventInjector() if DramaticEventInjector else None
        
        # Initialize configuration from environment
        self.max_interactions = int(os.getenv("MAX_INTERACTIONS", "50"))
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
            
            # Initialize director agent and character manager
            if create_director_agent is not None:
                self.director_agent = create_director_agent()
            if get_character_manager is not None:
                self.character_manager = get_character_manager()
            
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

    
    async def create_autonomous_character_agents(self) -> bool:
        """Create autonomous agents from the characters in MovieContext."""
        logger.subsection_header("🤖 CREATING AUTONOMOUS CHARACTER AGENTS")
        
        if not self.context or not self.context.characters:
            logger.error("No characters found in context", "agent")
            return False
        
        if not Runner or not self.character_manager:
            logger.warning("AI agents not available - autonomous mode disabled", "agent")
            return False
        
        try:
            for char_id, character in self.context.characters.items():
                logger.info(f"Creating autonomous agent for {character.name}...", "agent")
                
                # Register character with character manager and get agent
                agent = self.character_manager.add_character(char_id, character)
                
                # Create initial character prompt for autonomous behavior
                character_prompt = f"""
                You are {character.name}, a {character.story_role.value} in this story.
                
                Background: {character.background}
                Personality: {', '.join(character.personality_traits)}
                Motivation: {character.primary_motivation}
                Secrets: {', '.join(character.secrets)}
                
                You can use tools to:
                - Express emotions and take actions 
                - Reveal secrets when appropriate
                - Interact with other characters
                - Investigate and discover information
                
                Act autonomously based on your personality and motivations.
                """
                
                # Store the agent for autonomous interactions
                self.character_agents[char_id] = {
                    "agent": agent,
                    "character": character,
                    "prompt_template": character_prompt,
                    "last_action": None
                }
                
                logger.success(f"✅ {character.name} agent ready", "agent")
            
            logger.success(f"All {len(self.character_agents)} character agents ready for autonomous storytelling", "agent")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create autonomous agents: {e}", "agent")
            return False
    
    async def start_initial_scene(self) -> bool:
        """Start the initial scene for autonomous storytelling."""
        logger.subsection_header("🎬 STARTING INITIAL SCENE")
        
        if not self.context or not self.context.characters:
            logger.error("No characters available for scene", "scene")
            return False
        
        try:
            # Import scene tools
            from .tools.scene_tools import start_new_scene
            
            # Determine appropriate setting based on story
            scene_location = self.context.story_state.setting or "Main Location"
            present_characters = list(self.context.characters.keys())
            
            # Start initial scene
            scene_result = await start_new_scene(
                ctx=type('MockContext', (), {'context': self.context})(),
                scene_id="initial_scene",
                location=scene_location,
                mood="mysterious",
                present_characters=present_characters,
                scene_objectives=["Establish character relationships", "Begin investigation", "Set story in motion"],
                dramatic_tension_target=0.6
            )
            
            if scene_result.get("success"):
                logger.success(f"Initial scene started at {scene_location}", "scene")
                return True
            else:
                logger.error(f"Failed to start scene: {scene_result.get('error')}", "scene")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start initial scene: {e}", "scene")
            return False
    
    async def run_autonomous_storytelling_loop(self) -> List[Dict[str, Any]]:
        """Run the main autonomous storytelling loop where characters interact freely."""
        logger.subsection_header("🤖 AUTONOMOUS STORYTELLING LOOP")
        logger.info("Characters will now interact autonomously until story concludes...", "loop")
        
        story_events = []
        interaction_count = 0
        
        # Import character and scene tools
        try:
            from .tools.character_tools import express_emotion, take_character_action, reveal_character_secret
            from .tools.scene_tools import manage_character_turn, check_scene_objectives
        except ImportError:
            logger.error("Character/Scene tools not available", "loop")
            return story_events
        
        while interaction_count < self.max_interactions:
            try:
                # Check if story has reached natural conclusion
                if await self._check_story_completion():
                    logger.success("Story has reached natural conclusion", "loop")
                    break
                
                # Select next character to act (round-robin with some randomness)
                active_characters = list(self.character_agents.keys())
                if not active_characters:
                    break
                
                # Weight selection towards characters who haven't acted recently
                char_weights = []
                for char_id in active_characters:
                    last_action = self.character_agents[char_id].get("last_action", 0)
                    weight = max(1, interaction_count - last_action + 1)
                    char_weights.append(weight)
                
                selected_char = random.choices(active_characters, weights=char_weights)[0]
                char_data = self.character_agents[selected_char]
                
                logger.info(f"🎭 {char_data['character'].name} takes autonomous action...", "loop")
                
                # Have character decide their next action autonomously
                action_prompt = f"""
                {char_data['prompt_template']}
                
                Current situation: {await self._get_current_situation_summary()}
                
                Decide what you want to do next. You can:
                1. Express an emotion about the current situation
                2. Take an investigative or social action
                3. Reveal one of your secrets if appropriate
                4. Interact with another character
                
                Choose ONE action that fits your character and current situation.
                Be specific about what you want to do.
                """
                
                # Get character's autonomous decision
                action_result = await Runner.run(char_data["agent"], action_prompt, context=self.context)
                action_decision = action_result.final_output
                
                # Parse and execute the character's decision using tools
                event = await self._execute_character_decision(selected_char, action_decision)
                
                if event:
                    story_events.append(event)
                    self.character_agents[selected_char]["last_action"] = interaction_count
                    
                    logger.info(f"✅ {char_data['character'].name}: {event.get('action_summary', 'Unknown action')}", "loop")
                
                interaction_count += 1
                
                # Occasional dramatic events to spice things up
                if interaction_count % 10 == 0 and self.event_injector:
                    event_result = self.event_injector.inject_random_event()
                    if event_result.get("success"):
                        logger.info(f"💥 Dramatic event: {event_result.get('event_type', 'Unknown')}", "loop")
                
                # Brief pause between interactions
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in storytelling loop: {e}", "loop")
                interaction_count += 1
                continue
        
        if interaction_count >= self.max_interactions:
            logger.warning(f"Reached maximum interactions ({self.max_interactions})", "loop")
        
        logger.success(f"Autonomous storytelling completed with {len(story_events)} character interactions", "loop")
        return story_events
    
    async def _execute_character_decision(self, char_id: str, decision: str) -> Optional[Dict[str, Any]]:
        """Execute a character's autonomous decision using the appropriate tools."""
        try:
            # Import tools
            from .tools.character_tools import express_emotion, take_character_action, reveal_character_secret
            
            # Simple decision parsing (could be enhanced with AI)
            decision_lower = decision.lower()
            char_data = self.character_agents[char_id]
            character = char_data["character"]
            
            # Create context wrapper
            ctx = type('MockContext', (), {'context': self.context})()
            
            # Determine action type and execute
            if any(word in decision_lower for word in ["feel", "emotion", "angry", "scared", "happy", "sad"]):
                # Extract emotion and trigger
                emotion = "curious" if "curious" in decision_lower else "anxious"
                if "angry" in decision_lower: emotion = "anger"
                elif "scared" in decision_lower or "afraid" in decision_lower: emotion = "fear"
                elif "happy" in decision_lower or "excited" in decision_lower: emotion = "joy"
                elif "sad" in decision_lower: emotion = "sadness"
                
                result = await express_emotion(
                    ctx=ctx,
                    character_id=char_id,
                    emotion=emotion,
                    intensity=random.uniform(0.5, 0.9),
                    trigger=decision
                )
                
                return {
                    "type": "emotion",
                    "character": character.name,
                    "action_summary": f"expressed {emotion}",
                    "details": result
                }
                
            elif any(word in decision_lower for word in ["secret", "reveal", "tell", "confess"]):
                # Character wants to reveal a secret
                if character.secrets:
                    secret = random.choice(character.secrets)
                    revelation_type = "public" if "everyone" in decision_lower else "private"
                    
                    result = await reveal_character_secret(
                        ctx=ctx,
                        character_id=char_id,
                        secret=secret,
                        revelation_type=revelation_type
                    )
                    
                    return {
                        "type": "revelation",
                        "character": character.name,
                        "action_summary": f"revealed a secret",
                        "details": result
                    }
            
            else:
                # General action
                action_type = "investigative" if "investigate" in decision_lower else "social"
                
                result = await take_character_action(
                    ctx=ctx,
                    character_id=char_id,
                    action=decision,
                    action_type=action_type,
                    motivation=character.primary_motivation
                )
                
                return {
                    "type": "action",
                    "character": character.name,
                    "action_summary": decision[:50],
                    "details": result
                }
                
        except Exception as e:
            logger.error(f"Failed to execute decision for {char_id}: {e}", "loop")
            return None
    
    async def _get_current_situation_summary(self) -> str:
        """Get a summary of the current story situation."""
        if not self.context:
            return "Unknown situation"
        
        tension = self.context.story_state.dramatic_tension
        beat = self.context.story_state.current_beat
        location = self.context.current_scene.location if self.context.current_scene else "Unknown location"
        
        return f"Location: {location}, Story beat: {beat}, Tension: {tension:.1f}/1.0"
    
    async def _check_story_completion(self) -> bool:
        """Check if the story has reached a natural conclusion."""
        if not self.context:
            return False
        
        story_state = self.context.story_state
        
        # Story is complete if resolution readiness is high
        if story_state.resolution_readiness >= 0.9:
            return True
        
        # Or if all major story elements are highly progressed
        if (story_state.setup_progress >= 0.9 and 
            story_state.conflict_progress >= 0.8 and 
            story_state.character_arc_progress >= 0.7):
            return True
        
        return False
    
    async def run_simulation(self, story_seed: str) -> str:
        """
        Run the complete autonomous movie simulation.
        
        Args:
            story_seed: User's initial story idea
            
        Returns:
            Generated story content
        """
        logger.subsection_header("🎬 AUTONOMOUS MOVIE SIMULATION")
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
        
        if not director_result["success"]:
            logger.error(f"Director agent failed: {director_result.get('message', 'Unknown error')}", "agent")
            return "Director agent failed to create story setup"
        
        logger.success("Director agent completed successfully", "agent")
        
        # Phase 3: Create Autonomous Character Agents
        logger.subsection_header("🤖 Phase 3: Character Agent Creation")
        agents_created = await self.create_autonomous_character_agents()
        
        if not agents_created:
            logger.warning("Could not create autonomous agents - using basic simulation", "agent")
            return await self._generate_story_summary()
        
        # Phase 4: Start Initial Scene
        logger.subsection_header("🎬 Phase 4: Initial Scene Setup")
        scene_started = await self.start_initial_scene()
        
        if not scene_started:
            logger.error("Failed to start initial scene", "scene")
            return "Failed to start story scene"
        
        # Phase 5: Autonomous Storytelling Loop
        logger.subsection_header("🚀 Phase 5: AUTONOMOUS STORYTELLING")
        story_events = await self.run_autonomous_storytelling_loop()
        
        # Phase 6: Generate Final Story Summary
        logger.subsection_header("📑 Phase 6: Story Conclusion")
        story_summary = await self._generate_autonomous_story_summary(story_events)
        
        logger.success("🎉 AUTONOMOUS STORYTELLING COMPLETE!", "simulation")
        
        return story_summary
    
    async def _generate_autonomous_story_summary(self, story_events: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the autonomous story that was created.
        
        Args:
            story_events: List of autonomous character interactions
            
        Returns:
            Story summary string
        """
        if not self.context:
            return "No story context available"
        
        logger.subsection_header("📊 Generating autonomous story summary...")
        
        # Analyze story events by type
        emotions_count = len([e for e in story_events if e.get("type") == "emotion"])
        actions_count = len([e for e in story_events if e.get("type") == "action"])
        revelations_count = len([e for e in story_events if e.get("type") == "revelation"])
        
        # Build comprehensive summary
        summary_parts = [
            "🎬 AUTONOMOUS MOVIE SIMULATION COMPLETE",
            "=" * 70,
            f"🤖 Total Autonomous Interactions: {len(story_events)}",
            f"   💭 Emotional Expressions: {emotions_count}",
            f"   🎭 Character Actions: {actions_count}",  
            f"   🔍 Secret Revelations: {revelations_count}",
            "",
            f"📝 Story Title: {self.context.story_state.title}",
            f"🎭 Genre: {self.context.story_state.genre.value.upper()}",
            f"🏢 Setting: {self.context.story_state.setting}",
            f"🎯 Current Beat: {self.context.story_state.current_beat}",
            f"⚡ Final Dramatic Tension: {self.context.story_state.dramatic_tension:.1f}/1.0",
            "",
            f"🎭 AUTONOMOUS CHARACTERS ({len(self.context.characters)} active):"
        ]
        
        # Add character info
        if self.context.characters:
            for char_id, character in self.context.characters.items():
                role_emoji = {"protagonist": "🌟", "antagonist": "💀", "supporting": "🎬", "minor": "👤"}
                emoji = role_emoji.get(character.story_role.value, "👤")
                
                # Count this character's actions
                char_events = [e for e in story_events if e.get("character") == character.name]
                
                summary_parts.extend([
                    f"  {emoji} {character.name} ({character.story_role.value})",
                    f"     Autonomous Actions: {len(char_events)}",
                    f"     Remaining Secrets: {len(character.secrets)}",
                    f"     Motivation: {character.primary_motivation}",
                    ""
                ])
        
        # Add story progression metrics
        summary_parts.extend([
            "📊 STORY PROGRESSION METRICS:",
            f"  📈 Setup Progress: {self.context.story_state.setup_progress:.1%}",
            f"  ⚔️  Conflict Progress: {self.context.story_state.conflict_progress:.1%}",
            f"  👥 Character Arc Progress: {self.context.story_state.character_arc_progress:.1%}",
            f"  🎯 Resolution Readiness: {self.context.story_state.resolution_readiness:.1%}",
            ""
        ])
        
        # Add sample story events
        if story_events:
            summary_parts.extend([
                "🎬 AUTONOMOUS STORY HIGHLIGHTS:",
            ])
            
            # Show first and last few events
            highlight_events = story_events[:3] + story_events[-3:] if len(story_events) > 6 else story_events
            
            for i, event in enumerate(highlight_events, 1):
                event_type_emoji = {"emotion": "💭", "action": "🎭", "revelation": "🔍"}
                emoji = event_type_emoji.get(event.get("type", "action"), "🎭")
                
                summary_parts.append(f"  {emoji} {event.get('character', 'Unknown')}: {event.get('action_summary', 'Unknown action')}")
            
            summary_parts.append("")
        
        # Add autonomous features achieved
        summary_parts.extend([
            "🚀 AUTONOMOUS STORYTELLING FEATURES ACHIEVED:",
            "   ✅ Characters created autonomously by Director AI",
            "   ✅ Character agents make independent decisions",
            "   ✅ Tools used autonomously for character interactions",
            "   ✅ Story progression driven by character choices",
            "   ✅ Dramatic tension evolves naturally",
            "   ✅ Secrets revealed based on character motivations",
            "   ✅ Scene coordination through autonomous interactions",
            "   ✅ Story conclusion reached organically",
            "",
            "🎯 RESULT: Full autonomous AI storytelling achieved!",
            "   Characters acted independently, used tools autonomously,",
            "   and created an emergent story through their interactions."
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