"""
Memory management tools for story simulation.

These tools provide in-memory storage and retrieval of story facts,
character memories, and scene history.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

# Import models - using absolute import for now
from movie_simulator.core.models.story_models import MovieContext, CharacterProfile

@dataclass
class StoryMemory:
    """Container for different types of story memories."""
    facts: List[str] = field(default_factory=list)
    character_memories: Dict[str, List[str]] = field(default_factory=dict)
    scene_history: List[Dict[str, Any]] = field(default_factory=list)
    plot_points: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    
    def add_fact(self, fact: str) -> None:
        """Add a story fact to memory."""
        if fact and fact not in self.facts:
            self.facts.append(fact)
    
    def add_character_memory(self, character_id: str, memory: str) -> None:
        """Add a memory for a specific character."""
        if character_id not in self.character_memories:
            self.character_memories[character_id] = []
        if memory and memory not in self.character_memories[character_id]:
            self.character_memories[character_id].append(memory)
    
    def add_scene(self, scene_data: Dict[str, Any]) -> None:
        """Add a scene to history."""
        scene_entry = {
            "timestamp": datetime.now().isoformat(),
            **scene_data
        }
        self.scene_history.append(scene_entry)
    
    def add_plot_point(self, plot_point: str) -> None:
        """Add a significant plot point."""
        if plot_point and plot_point not in self.plot_points:
            self.plot_points.append(plot_point)
    
    def add_conflict(self, conflict: str) -> None:
        """Add a story conflict."""
        if conflict and conflict not in self.conflicts:
            self.conflicts.append(conflict)
    
    def get_character_memories(self, character_id: str) -> List[str]:
        """Get all memories for a character."""
        return self.character_memories.get(character_id, [])
    
    def get_recent_scenes(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent scenes."""
        return self.scene_history[-count:] if self.scene_history else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary format."""
        return {
            "facts": self.facts,
            "character_memories": self.character_memories,
            "scene_history": self.scene_history,
            "plot_points": self.plot_points,
            "conflicts": self.conflicts,
            "total_entries": len(self.facts) + len(self.plot_points) + len(self.conflicts)
        }


class MemoryManager:
    """Manages story memory and provides tools for agents to interact with it."""
    
    def __init__(self):
        """Initialize the memory manager."""
        self.memory = StoryMemory()
        self._context: Optional[MovieContext] = None
    
    def set_context(self, context: MovieContext) -> None:
        """Set the movie context for memory operations."""
        self._context = context
    
    def record_story_fact(self, fact: str) -> bool:
        """
        Record an important story fact.
        
        Args:
            fact: The story fact to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.memory.add_fact(fact)
            print(f"📝 Recorded fact: {fact}")
            return True
        except Exception as e:
            print(f"❌ Failed to record fact: {e}")
            return False
    
    def record_character_memory(self, character_id: str, memory: str) -> bool:
        """
        Record a memory for a specific character.
        
        Args:
            character_id: ID of the character
            memory: The memory to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate character exists
            if self._context is not None and character_id not in self._context.characters:
                print(f"⚠️  Character {character_id} not found in context")
                return False
            
            self.memory.add_character_memory(character_id, memory)
            print(f"🧠 Recorded memory for {character_id}: {memory}")
            return True
        except Exception as e:
            print(f"❌ Failed to record character memory: {e}")
            return False
    
    def record_scene(self, location: str, description: str, characters: List[str]) -> bool:
        """
        Record a scene in the story.
        
        Args:
            location: Where the scene takes place
            description: Description of what happens
            characters: Characters present in the scene
            
        Returns:
            True if successful, False otherwise
        """
        try:
            scene_data = {
                "location": location,
                "description": description,
                "characters": characters,
                "dramatic_tension": self._context.story_state.dramatic_tension if self._context is not None else 0.5
            }
            
            self.memory.add_scene(scene_data)
            print(f"🎬 Recorded scene at {location}: {description}")
            return True
        except Exception as e:
            print(f"❌ Failed to record scene: {e}")
            return False
    
    def record_plot_point(self, plot_point: str) -> bool:
        """
        Record a significant plot point.
        
        Args:
            plot_point: The plot point to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.memory.add_plot_point(plot_point)
            print(f"📚 Recorded plot point: {plot_point}")
            return True
        except Exception as e:
            print(f"❌ Failed to record plot point: {e}")
            return False
    
    def record_conflict(self, conflict: str) -> bool:
        """
        Record a story conflict.
        
        Args:
            conflict: The conflict to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.memory.add_conflict(conflict)
            print(f"⚔️ Recorded conflict: {conflict}")
            return True
        except Exception as e:
            print(f"❌ Failed to record conflict: {e}")
            return False
    
    def get_story_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of stored memories.
        
        Returns:
            Dictionary containing memory summary
        """
        summary = {
            "total_facts": len(self.memory.facts),
            "total_plot_points": len(self.memory.plot_points),
            "total_conflicts": len(self.memory.conflicts),
            "total_scenes": len(self.memory.scene_history),
            "characters_with_memories": len(self.memory.character_memories),
            "recent_facts": self.memory.facts[-3:] if self.memory.facts else [],
            "recent_plot_points": self.memory.plot_points[-3:] if self.memory.plot_points else [],
            "recent_scenes": self.memory.get_recent_scenes(3)
        }
        return summary
    
    def get_character_context(self, character_id: str) -> Dict[str, Any]:
        """
        Get all context and memories for a specific character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary containing character context
        """
        scenes_appeared = []
        
        # Find scenes where character appeared
        for scene in self.memory.scene_history:
            if character_id in scene.get("characters", []):
                scenes_appeared.append({
                    "location": scene.get("location"),
                    "description": scene.get("description"),
                    "timestamp": scene.get("timestamp")
                })
        
        context = {
            "character_id": character_id,
            "memories": self.memory.get_character_memories(character_id),
            "scenes_appeared": scenes_appeared
        }
        
        return context
    
    def search_memories(self, query: str) -> Dict[str, Any]:
        """
        Search through all memories for a query string.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with matching memories by category
        """
        query_lower = query.lower()
        character_memories = {}
        
        # Search character memories
        for char_id, memories in self.memory.character_memories.items():
            matching_memories = [mem for mem in memories if query_lower in mem.lower()]
            if matching_memories:
                character_memories[char_id] = matching_memories
        
        results = {
            "facts": [fact for fact in self.memory.facts if query_lower in fact.lower()],
            "plot_points": [pp for pp in self.memory.plot_points if query_lower in pp.lower()],
            "conflicts": [conf for conf in self.memory.conflicts if query_lower in conf.lower()],
            "character_memories": character_memories
        }
        
        return results
    
    def clear_memory(self) -> bool:
        """
        Clear all stored memories (for testing/reset).
        
        Returns:
            True if successful
        """
        try:
            self.memory = StoryMemory()
            print("🗑️ Memory cleared")
            return True
        except Exception as e:
            print(f"❌ Failed to clear memory: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about memory usage."""
        return {
            "facts_count": len(self.memory.facts),
            "plot_points_count": len(self.memory.plot_points),
            "conflicts_count": len(self.memory.conflicts),
            "scenes_count": len(self.memory.scene_history),
            "characters_with_memories": len(self.memory.character_memories),
            "total_character_memories": sum(len(memories) for memories in self.memory.character_memories.values())
        } 