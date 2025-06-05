"""
Memory Tools for Character Memory Management
Implements the memory system outlined in plan.md
"""

from agents import function_tool
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class MemoryEntry:
    """Individual memory entry for a character"""
    character_id: str
    content: str
    participants: List[str]
    emotional_impact: float
    memory_type: str  # 'event', 'relationship', 'secret', 'emotion', 'observation'
    timestamp: datetime
    memory_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))


class MemorySystem:
    """In-memory storage system for character memories"""
    
    def __init__(self):
        self.memories: Dict[str, List[MemoryEntry]] = {}
        self.relationships: Dict[str, Dict[str, float]] = {}
    
    def add_character(self, character_id: str):
        """Initialize memory storage for a character"""
        if character_id not in self.memories:
            self.memories[character_id] = []
            self.relationships[character_id] = {}
    
    def store_memory(self, memory: MemoryEntry) -> bool:
        """Store a new memory entry"""
        try:
            if memory.character_id not in self.memories:
                self.add_character(memory.character_id)
            
            self.memories[memory.character_id].append(memory)
            return True
        except Exception:
            return False
    
    def search_memories(self, character_id: str, query: str, memory_type: str = "all") -> List[MemoryEntry]:
        """Search character memories by content and type"""
        if character_id not in self.memories:
            return []
        
        results = []
        for memory in self.memories[character_id]:
            # Simple keyword search (can be enhanced with embeddings later)
            if query.lower() in memory.content.lower():
                if memory_type == "all" or memory.memory_type == memory_type:
                    results.append(memory)
        
        # Sort by emotional impact and recency
        results.sort(key=lambda m: (m.emotional_impact, m.timestamp.timestamp()), reverse=True)
        return results[:10]  # Return top 10 most relevant
    
    def get_relationships(self, character_id: str) -> Dict[str, float]:
        """Get character's relationship scores"""
        return self.relationships.get(character_id, {})
    
    def update_relationship(self, character_id: str, target_id: str, change: float):
        """Update relationship score between characters"""
        if character_id not in self.relationships:
            self.relationships[character_id] = {}
        
        current = self.relationships[character_id].get(target_id, 0.0)
        self.relationships[character_id][target_id] = max(-1.0, min(1.0, current + change))


# Global memory system instance
MEMORY_SYSTEM = MemorySystem()


@function_tool
def search_character_memory(
    character_id: str, 
    query: str, 
    memory_type: str = "all"
) -> str:
    """
    Search character's memory for relevant experiences.
    
    Args:
        character_id: ID of the character
        query: What to search for
        memory_type: 'events', 'relationships', 'secrets', 'emotions', 'observations', or 'all'
    
    Returns:
        Formatted string of relevant memories
    """
    memories = MEMORY_SYSTEM.search_memories(character_id, query, memory_type)
    
    if not memories:
        return f"No memories found for '{query}'"
    
    formatted_results = [f"🧠 {character_id}'s relevant memories:"]
    
    for i, memory in enumerate(memories, 1):
        formatted_results.append(
            f"{i}. [{memory.memory_type.upper()}] {memory.content} "
            f"(Impact: {memory.emotional_impact:.1f}, {memory.timestamp.strftime('%H:%M')})"
        )
    
    return "\n".join(formatted_results)


@function_tool
def store_character_memory(
    character_id: str,
    event_description: str,
    participants: List[str],
    emotional_impact: float,
    memory_type: str = "event"
) -> bool:
    """
    Store new memory for character.
    
    Args:
        character_id: Character storing the memory
        event_description: What happened
        participants: Who was involved
        emotional_impact: Emotional significance (0.0 to 1.0)
        memory_type: Type of memory ('event', 'relationship', 'secret', 'emotion', 'observation')
    
    Returns:
        Success status
    """
    memory = MemoryEntry(
        character_id=character_id,
        content=event_description,
        participants=participants,
        emotional_impact=max(0.0, min(1.0, emotional_impact)),
        memory_type=memory_type,
        timestamp=datetime.now()
    )
    
    success = MEMORY_SYSTEM.store_memory(memory)
    
    # Update relationships if this involves other characters
    if success and len(participants) > 1:
        for participant in participants:
            if participant != character_id:
                # Positive memories improve relationships, negative ones worsen them
                relationship_change = 0.1 if emotional_impact > 0.5 else -0.05
                MEMORY_SYSTEM.update_relationship(character_id, participant, relationship_change)
    
    return success


@function_tool
def get_character_relationships(character_id: str) -> Dict[str, float]:
    """
    Get character's current relationship opinions.
    
    Args:
        character_id: Character whose relationships to retrieve
    
    Returns:
        Dictionary mapping character IDs to relationship scores (-1.0 to 1.0)
    """
    relationships = MEMORY_SYSTEM.get_relationships(character_id)
    
    # Format for better readability
    formatted = {}
    for char_id, score in relationships.items():
        if score > 0.6:
            status = "close friend"
        elif score > 0.3:
            status = "friendly"
        elif score > -0.3:
            status = "neutral"
        elif score > -0.6:
            status = "dislikes"
        else:
            status = "hostile"
        
        formatted[char_id] = f"{score:.2f} ({status})"
    
    return formatted


@function_tool
def recall_shared_experiences(character_id: str, other_character_id: str) -> str:
    """
    Recall shared experiences between two characters.
    
    Args:
        character_id: First character
        other_character_id: Second character
    
    Returns:
        Formatted list of shared memories
    """
    memories = MEMORY_SYSTEM.memories.get(character_id, [])
    shared_memories = [
        m for m in memories 
        if other_character_id in m.participants
    ]
    
    if not shared_memories:
        return f"{character_id} has no significant shared memories with {other_character_id}"
    
    # Sort by emotional impact and recency
    shared_memories.sort(key=lambda m: (m.emotional_impact, m.timestamp.timestamp()), reverse=True)
    
    result = [f"📝 Shared experiences between {character_id} and {other_character_id}:"]
    
    for i, memory in enumerate(shared_memories[:5], 1):  # Top 5 memories
        result.append(
            f"{i}. {memory.content} "
            f"(Impact: {memory.emotional_impact:.1f}, {memory.timestamp.strftime('%H:%M')})"
        )
    
    return "\n".join(result)


@function_tool
def get_memory_system_status() -> Dict[str, Any]:
    """
    Get overall status of the memory system.
    
    Returns:
        Dictionary with memory system statistics
    """
    total_memories = sum(len(memories) for memories in MEMORY_SYSTEM.memories.values())
    character_count = len(MEMORY_SYSTEM.memories)
    
    return {
        "total_characters": character_count,
        "total_memories": total_memories,
        "average_memories_per_character": total_memories / max(character_count, 1),
        "characters_with_memories": list(MEMORY_SYSTEM.memories.keys()),
        "relationship_count": sum(len(rels) for rels in MEMORY_SYSTEM.relationships.values())
    }
