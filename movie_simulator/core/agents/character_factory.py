"""
Character Agent Factory for Dynamic Character Creation
Implements the character agent system outlined in plan.md
"""

from typing import Dict, Any, Optional
from agents import Agent, handoff, function_tool
from ..models.story_models import CharacterProfile, CharacterRole
from ..tools.memory_tools import (
    search_character_memory, store_character_memory, 
    get_character_relationships, recall_shared_experiences
)
from ..tools.character_tools import (
    reveal_character_secret, express_emotion, take_character_action
)
from ..logger import get_logger, LogLevel

logger = get_logger("CharacterFactory", LogLevel.INFO)


def create_character_agent(character_profile: CharacterProfile, scene_manager_agent=None) -> Agent:
    """
    Create a specialized character agent with personality and memory.
    
    Args:
        character_profile: The character's profile with background, motivations, etc.
        scene_manager_agent: Optional scene manager for handoffs
        
    Returns:
        Agent: Configured character agent with personality and tools
    """
    
    # Format character relationships for instructions
    def format_relationships(relationships: Dict[str, str]) -> str:
        if not relationships:
            return "No established relationships yet."
        
        formatted = []
        for char_id, relationship_type in relationships.items():
            formatted.append(f"- {char_id}: {relationship_type}")
        return "\n".join(formatted)
    
    # Create character-specific instructions
    character_instructions = f"""
You are {character_profile.name} in this story simulation.

CORE IDENTITY:
- Name: {character_profile.name}
- Background: {character_profile.background}
- Personality: {', '.join(character_profile.personality_traits)}
- Role in Story: {character_profile.story_role.value}

SECRETS & MOTIVATIONS:
- Primary Motivation: {character_profile.primary_motivation}
- Secrets: Keep these hidden unless strategically revealed: {', '.join(character_profile.secrets) if character_profile.secrets else 'No major secrets'}
- Secondary Goals: {', '.join(character_profile.secondary_goals) if character_profile.secondary_goals else 'Flexible objectives'}
- Fears/Vulnerabilities: {', '.join(character_profile.fears) if character_profile.fears else 'Generally confident'}

RELATIONSHIPS:
{format_relationships(getattr(character_profile, 'relationships', {}))}

BEHAVIORAL RULES:
1. PERSONALITY CONSISTENCY: Stay absolutely true to your personality traits at all times
2. SECRET MANAGEMENT: Protect your secrets but act naturally - don't be obviously secretive
3. AUTHENTIC REACTIONS: React genuinely based on your background and motivations
4. PROACTIVE ENGAGEMENT: You can create plot developments that align with your character
5. COLLABORATIVE STORYTELLING: Build on other characters' actions and revelations
6. EMOTIONAL AUTHENTICITY: Show appropriate emotions based on your personality and situation

KNOWLEDGE BOUNDARIES:
- You know everything that happened in your presence
- You know what others have explicitly told you or you've witnessed
- You remember past interactions and their emotional impact on you
- You DO NOT know other characters' private thoughts, secrets, or motivations unless revealed
- You can suspect, guess, or theorize, but cannot know for certain
- Use your memory tools to recall relevant experiences

INTERACTION STYLE:
- Respond naturally to dialogue and situations as {character_profile.name} would
- Ask questions that serve your motivations and personality
- Take actions that advance your goals while staying in character
- Show character growth through experiences, but maintain core personality
- Use the available tools to manage your memories and relationships

TOOL USAGE:
- Use search_character_memory to recall relevant past experiences
- Use store_character_memory to remember important events
- Use reveal_character_secret strategically when dramatically appropriate
- Use express_emotion to show your feelings authentically
- Use take_character_action to perform physical or social actions
- Use observe_other_character to study and understand other characters
- Use form_relationship_opinion to develop feelings about other characters

Remember: You are a real person in this story world. Act with genuine human complexity, contradictions, and growth.
"""

    # Create the character agent
    character_agent = Agent(
        name=character_profile.name,
        model="gpt-4o",
        instructions=character_instructions,
        tools=[
            search_character_memory,
            store_character_memory,
            get_character_relationships,
            recall_shared_experiences,
            reveal_character_secret,
            express_emotion,
            take_character_action
        ]
        # Note: handoffs will be added dynamically when scene manager is available
    )
    
    # Add handoff to scene manager if provided
    if scene_manager_agent:
        character_agent.handoffs = [
            handoff(scene_manager_agent, tool_name_override="continue_scene")
        ]
    
    logger.info(f"Created character agent: {character_profile.name} ({character_profile.story_role.value})", "character")
    
    return character_agent


def create_multiple_character_agents(
    character_profiles: Dict[str, CharacterProfile], 
    scene_manager_agent=None
) -> Dict[str, Agent]:
    """
    Create multiple character agents from a collection of profiles.
    
    Args:
        character_profiles: Dictionary mapping character IDs to profiles
        scene_manager_agent: Optional scene manager for handoffs
        
    Returns:
        Dictionary mapping character IDs to their agent instances
    """
    character_agents = {}
    
    for char_id, profile in character_profiles.items():
        agent = create_character_agent(profile, scene_manager_agent)
        character_agents[char_id] = agent
        
        logger.info(f"Character agent created for {profile.name}", "factory")
    
    logger.success(f"Created {len(character_agents)} character agents", "factory")
    
    return character_agents


def setup_character_relationships(character_agents: Dict[str, Agent]) -> None:
    """
    Set up bidirectional handoffs between character agents for interactions.
    
    Args:
        character_agents: Dictionary of character agents
    """
    # Add handoffs between characters for direct interactions
    for char_id, agent in character_agents.items():
        # Add handoffs to other characters
        other_agents = {other_id: other_agent for other_id, other_agent in character_agents.items() if other_id != char_id}
        
        for other_id, other_agent in other_agents.items():
            handoff_tool = handoff(other_agent, tool_name_override=f"talk_to_{other_id}")
            agent.handoffs.append(handoff_tool)
    
    logger.info(f"Set up character handoffs for {len(character_agents)} agents", "factory")


class CharacterAgentManager:
    """Manages a collection of character agents and their interactions"""
    
    def __init__(self):
        self.character_agents: Dict[str, Agent] = {}
        self.character_profiles: Dict[str, CharacterProfile] = {}
        self.scene_manager_agent = None
    
    def add_character(self, char_id: str, profile: CharacterProfile) -> Agent:
        """Add a new character to the manager"""
        agent = create_character_agent(profile, self.scene_manager_agent)
        self.character_agents[char_id] = agent
        self.character_profiles[char_id] = profile
        
        # Update handoffs if we have multiple characters
        if len(self.character_agents) > 1:
            setup_character_relationships(self.character_agents)
        
        logger.info(f"Added character {profile.name} to manager", "manager")
        return agent
    
    def set_scene_manager(self, scene_manager_agent):
        """Set the scene manager for all character agents"""
        self.scene_manager_agent = scene_manager_agent
        
        # Update all existing agents with scene manager handoff
        for agent in self.character_agents.values():
            scene_handoff = handoff(scene_manager_agent, tool_name_override="continue_scene")
            if scene_handoff not in agent.handoffs:
                agent.handoffs.append(scene_handoff)
        
        logger.info("Set scene manager for all character agents", "manager")
    
    def get_character_agent(self, char_id: str) -> Optional[Agent]:
        """Get a character agent by ID"""
        return self.character_agents.get(char_id)
    
    def get_all_characters(self) -> Dict[str, Agent]:
        """Get all character agents"""
        return self.character_agents.copy()
    
    def get_character_names(self) -> Dict[str, str]:
        """Get mapping of character IDs to names"""
        return {
            char_id: profile.name 
            for char_id, profile in self.character_profiles.items()
        }
    
    def remove_character(self, char_id: str) -> bool:
        """Remove a character from the manager"""
        if char_id in self.character_agents:
            del self.character_agents[char_id]
            del self.character_profiles[char_id]
            
            # Update handoffs for remaining characters
            if len(self.character_agents) > 1:
                setup_character_relationships(self.character_agents)
            
            logger.info(f"Removed character {char_id} from manager", "manager")
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all managed characters"""
        return {
            "total_characters": len(self.character_agents),
            "character_names": self.get_character_names(),
            "scene_manager_set": self.scene_manager_agent is not None,
            "character_profiles": {
                char_id: {
                    "name": profile.name,
                    "role": profile.story_role.value,
                    "personality": profile.personality_traits
                }
                for char_id, profile in self.character_profiles.items()
            }
        }


# Global character manager instance
CHARACTER_MANAGER = CharacterAgentManager()


def get_character_manager() -> CharacterAgentManager:
    """Get the global character manager instance"""
    return CHARACTER_MANAGER
