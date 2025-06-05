"""
Character Tools for Character Actions and Interactions
Clean implementation using MovieContext as single source of truth
"""

from agents import function_tool, RunContextWrapper
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import movie context
from ..models.story_models import MovieContext

# Import memory tools
from .memory_tools import store_character_memory


@function_tool
async def reveal_character_secret(
    ctx: RunContextWrapper[MovieContext],
    character_id: str,
    secret: str,
    revelation_type: str = "public",
    target_character: Optional[str] = None
) -> Dict[str, Any]:
    """
    Have a character reveal one of their secrets.
    """
    # Validate character exists
    if character_id not in ctx.context.characters:
        return {
            "success": False,
            "error": f"Character '{character_id}' not found",
            "available_characters": list(ctx.context.characters.keys())
        }
    
    character = ctx.context.characters[character_id]
    
    # Check if character actually has this secret
    if secret not in character.secrets:
        return {
            "success": False,
            "error": f"Character '{character_id}' doesn't have secret: {secret}",
            "character_secrets": character.secrets
        }
    
    # Update dramatic tension based on revelation type
    tension_increase = 0.3 if revelation_type == "public" else 0.15
    ctx.context.story_state.dramatic_tension = min(1.0, 
        ctx.context.story_state.dramatic_tension + tension_increase)
    
    # Remove secret from character (now revealed)
    character.secrets.remove(secret)
    
    # Store in memories using present characters from current scene
    present_chars = ctx.context.current_scene.present_characters if ctx.context.current_scene else [character_id]
    
    if revelation_type == "public":
        # All present characters remember
        for char_id in present_chars:
            if char_id in ctx.context.characters:
                event_desc = f"{character_id} revealed: {secret}" if char_id != character_id else f"I revealed my secret: {secret}"
                store_character_memory(
                    character_id=char_id,
                    event_description=event_desc,
                    participants=present_chars,
                    emotional_impact=0.9 if char_id == character_id else 0.8,
                    memory_type="revelation"
                )
    elif revelation_type == "private" and target_character and target_character in ctx.context.characters:
        # Only target remembers
        store_character_memory(
            character_id=character_id,
            event_description=f"I told {target_character} my secret: {secret}",
            participants=[character_id, target_character],
            emotional_impact=0.8,
            memory_type="private_revelation"
        )
        store_character_memory(
            character_id=target_character,
            event_description=f"{character_id} revealed to me: {secret}",
            participants=[character_id, target_character],
            emotional_impact=0.9,
            memory_type="secret_learned"
        )
    
    return {
        "success": True,
        "character_id": character_id,
        "secret_revealed": secret,
        "revelation_type": revelation_type,
        "target_character": target_character,
        "new_tension": ctx.context.story_state.dramatic_tension,
        "characters_who_know": present_chars if revelation_type == "public" else [character_id, target_character],
        "message": f"{character_id} revealed secret: {secret} ({revelation_type})"
    }


@function_tool
async def express_emotion(
    ctx: RunContextWrapper[MovieContext],
    character_id: str,
    emotion: str,
    intensity: float,
    trigger: str,
    target_character: Optional[str] = None
) -> Dict[str, Any]:
    """
    Have a character express emotion, updating story tension and memories.
    """
    # Validate character exists
    if character_id not in ctx.context.characters:
        return {
            "success": False,
            "error": f"Character '{character_id}' not found",
            "available_characters": list(ctx.context.characters.keys())
        }
    
    # Validate target character if specified
    if target_character and target_character not in ctx.context.characters:
        return {
            "success": False,
            "error": f"Target character '{target_character}' not found"
        }
    
    # Clamp intensity
    intensity = max(0.0, min(1.0, intensity))
    
    # Update story tension based on emotion
    tension_change = intensity * 0.15 if emotion in ["anger", "fear", "sadness", "despair"] else intensity * 0.05
    ctx.context.story_state.dramatic_tension = min(1.0, 
        ctx.context.story_state.dramatic_tension + tension_change)
    
    # Store emotional memory
    emotion_desc = f"I felt {emotion} (intensity: {intensity:.1f}) because {trigger}"
    if target_character:
        emotion_desc += f" toward {target_character}"
    
    participants = [character_id]
    if target_character:
        participants.append(target_character)
    
    store_character_memory(
        character_id=character_id,
        event_description=emotion_desc,
        participants=participants,
        emotional_impact=intensity,
        memory_type="emotion"
    )
    
    # Target character observes the emotion if present in scene
    if target_character and ctx.context.current_scene and target_character in ctx.context.current_scene.present_characters:
        store_character_memory(
            character_id=target_character,
            event_description=f"{character_id} showed {emotion} toward me because {trigger}",
            participants=participants,
            emotional_impact=intensity * 0.7,
            memory_type="observation"
        )
    
    return {
        "success": True,
        "character_id": character_id,
        "emotion": emotion,
        "intensity": intensity,
        "trigger": trigger,
        "target_character": target_character,
        "new_tension": ctx.context.story_state.dramatic_tension,
        "message": f"{character_id} expressed {emotion} (intensity: {intensity:.1f})"
    }


@function_tool
async def take_character_action(
    ctx: RunContextWrapper[MovieContext],
    character_id: str,
    action: str,
    action_type: str = "social",
    target: Optional[str] = None,
    motivation: str = ""
) -> Dict[str, Any]:
    """
    Have a character take an action, updating story progression.
    """
    # Validate character exists
    if character_id not in ctx.context.characters:
        return {
            "success": False,
            "error": f"Character '{character_id}' not found",
            "available_characters": list(ctx.context.characters.keys())
        }
    
    # Validate target if it's another character
    if target and target in ctx.context.characters and target not in ctx.context.characters:
        return {
            "success": False,
            "error": f"Target character '{target}' not found"
        }
    
    # Update story progression based on action type
    if action_type == "investigative":
        ctx.context.story_state.conflict_progress = min(1.0, 
            ctx.context.story_state.conflict_progress + 0.1)
    elif action_type == "confrontational":
        ctx.context.story_state.dramatic_tension = min(1.0,
            ctx.context.story_state.dramatic_tension + 0.2)
    
    # Store action in memory
    action_desc = f"I {action}"
    if target:
        action_desc += f" (targeting {target})"
    if motivation:
        action_desc += f" because {motivation}"
    
    participants = [character_id]
    if target and target in ctx.context.characters:
        participants.append(target)
    
    store_character_memory(
        character_id=character_id,
        event_description=action_desc,
        participants=participants,
        emotional_impact=0.5,
        memory_type="action"
    )
    
    # Target remembers being acted upon
    if target and target in ctx.context.characters:
        store_character_memory(
            character_id=target,
            event_description=f"{character_id} {action} targeting me",
            participants=participants,
            emotional_impact=0.4,
            memory_type="observation"
        )
    
    return {
        "success": True,
        "character_id": character_id,
        "action": action,
        "action_type": action_type,
        "target": target,
        "motivation": motivation,
        "story_tension": ctx.context.story_state.dramatic_tension,
        "conflict_progress": ctx.context.story_state.conflict_progress,
        "message": f"{character_id} performed {action_type} action: {action}"
    }


@function_tool
async def update_character_relationship(
    ctx: RunContextWrapper[MovieContext],
    character_id: str,
    other_character_id: str,
    opinion_change: float,
    reason: str
) -> Dict[str, Any]:
    """
    Update relationship between characters based on story events.
    """
    # Validate both characters exist
    if character_id not in ctx.context.characters:
        return {"success": False, "error": f"Character '{character_id}' not found"}
    
    if other_character_id not in ctx.context.characters:
        return {"success": False, "error": f"Character '{other_character_id}' not found"}
    
    # Update relationship in memory system
    from .memory_tools import MEMORY_SYSTEM
    MEMORY_SYSTEM.update_relationship(character_id, other_character_id, opinion_change)
    
    # Store relationship change in memory
    opinion_desc = f"My opinion of {other_character_id} changed by {opinion_change:.2f} because {reason}"
    store_character_memory(
        character_id=character_id,
        event_description=opinion_desc,
        participants=[character_id, other_character_id],
        emotional_impact=abs(opinion_change),
        memory_type="relationship"
    )
    
    # Get updated relationship score
    relationships = MEMORY_SYSTEM.get_relationships(character_id)
    new_score = relationships.get(other_character_id, 0.0)
    
    return {
        "success": True,
        "character_id": character_id,
        "other_character_id": other_character_id,
        "opinion_change": opinion_change,
        "new_relationship_score": new_score,
        "reason": reason,
        "message": f"{character_id}'s opinion of {other_character_id} changed by {opinion_change:.2f}"
    }


@function_tool
async def get_character_status(
    ctx: RunContextWrapper[MovieContext],
    character_id: str
) -> Dict[str, Any]:
    """
    Get comprehensive status of a character from MovieContext.
    """
    if character_id not in ctx.context.characters:
        return {
            "success": False,
            "error": f"Character '{character_id}' not found",
            "available_characters": list(ctx.context.characters.keys())
        }
    
    character = ctx.context.characters[character_id]
    
    # Get character memories
    from .memory_tools import MEMORY_SYSTEM
    memories = MEMORY_SYSTEM.get_memories(character_id)
    relationships = MEMORY_SYSTEM.get_relationships(character_id)
    
    # Check if character is in current scene
    in_current_scene = (ctx.context.current_scene and 
                       character_id in ctx.context.current_scene.present_characters)
    
    return {
        "success": True,
        "character_id": character_id,
        "name": character.name,
        "role": character.story_role.value,
        "background": character.background,
        "motivation": character.primary_motivation,
        "personality_traits": character.personality_traits,
        "remaining_secrets": character.secrets,
        "fears": character.fears,
        "current_location": ctx.context.current_scene.location if in_current_scene else "unknown",
        "in_current_scene": in_current_scene,
        "memory_count": len(memories),
        "relationship_count": len(relationships),
        "relationships": relationships,
        "message": f"Status for {character.name}"
    }
