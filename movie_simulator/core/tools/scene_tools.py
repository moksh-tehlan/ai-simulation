"""
Scene Management Tools for coordinating character interactions and scene flow
Clean implementation using MovieContext as single source of truth
"""

from agents import function_tool, RunContextWrapper
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import movie context
from ..models.story_models import MovieContext, SceneContext


@function_tool
async def start_new_scene(
    ctx: RunContextWrapper[MovieContext],
    scene_id: str,
    location: str,
    mood: str,
    present_characters: List[str],
    scene_objectives: List[str],
    dramatic_tension_target: float = 0.5,
    time_period: str = "current"
) -> Dict[str, Any]:
    """
    Start a new scene with specified context using MovieContext.
    """
    # Validate that characters exist in context
    missing_characters = [char_id for char_id in present_characters if char_id not in ctx.context.characters]
    if missing_characters:
        return {
            "success": False,
            "error": f"Characters not found: {missing_characters}",
            "available_characters": list(ctx.context.characters.keys())
        }
    
    # Create scene context
    scene_context = SceneContext(
        location=location,
        time_period=time_period,
        mood=mood,
        present_characters=present_characters.copy(),
        scene_objectives=scene_objectives.copy(),
        dramatic_tension_target=dramatic_tension_target
    )
    
    # Set as current scene in movie context
    ctx.context.current_scene = scene_context
    
    # Update story state based on scene objectives
    ctx.context.story_state.dramatic_tension = dramatic_tension_target
    if any(obj in scene_objectives for obj in ["investigation", "interrogation", "search"]):
        ctx.context.story_state.conflict_progress = min(1.0, ctx.context.story_state.conflict_progress + 0.2)
    if any(obj in scene_objectives for obj in ["resolution", "confession", "reveal"]):
        ctx.context.story_state.resolution_readiness = min(1.0, ctx.context.story_state.resolution_readiness + 0.3)
    
    return {
        "success": True,
        "scene_id": scene_id,
        "location": location,
        "mood": mood,
        "present_characters": present_characters,
        "objectives": scene_objectives,
        "tension_target": dramatic_tension_target,
        "story_tension": ctx.context.story_state.dramatic_tension,
        "conflict_progress": ctx.context.story_state.conflict_progress,
        "message": f"Started scene '{scene_id}' at {location} with {len(present_characters)} characters"
    }


@function_tool
async def manage_character_turn(
    ctx: RunContextWrapper[MovieContext],
    character_id: str,
    interaction_type: str = "dialogue",
    target_character: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage character turns and interactions in the current scene.
    """
    # Validate current scene exists
    if not ctx.context.current_scene:
        return {
            "success": False,
            "error": "No active scene",
            "suggestion": "Start a new scene first"
        }
    
    # Validate character exists and is in scene
    if character_id not in ctx.context.characters:
        return {
            "success": False,
            "error": f"Character '{character_id}' not found",
            "available_characters": list(ctx.context.characters.keys())
        }
    
    if character_id not in ctx.context.current_scene.present_characters:
        return {
            "success": False,
            "error": f"Character '{character_id}' not in current scene",
            "present_characters": ctx.context.current_scene.present_characters
        }
    
    # Validate target character if specified
    if target_character:
        if target_character not in ctx.context.characters:
            return {"success": False, "error": f"Target character '{target_character}' not found"}
        if target_character not in ctx.context.current_scene.present_characters:
            return {"success": False, "error": f"Target character '{target_character}' not in scene"}
    
    # Update story tension based on interaction type
    tension_updates = {
        "revelation": 0.25,
        "confrontation": 0.3,
        "accusation": 0.35,
        "confession": 0.4,
        "dialogue": 0.05,
        "investigation": 0.1
    }
    
    tension_increase = tension_updates.get(interaction_type, 0.05)
    ctx.context.story_state.dramatic_tension = min(1.0, 
        ctx.context.story_state.dramatic_tension + tension_increase)
    
    # Update character arc progress for meaningful interactions
    if interaction_type in ["revelation", "confrontation", "confession"]:
        ctx.context.story_state.character_arc_progress = min(1.0,
            ctx.context.story_state.character_arc_progress + 0.15)
    
    return {
        "success": True,
        "current_speaker": character_id,
        "target_character": target_character,
        "interaction_type": interaction_type,
        "scene_location": ctx.context.current_scene.location,
        "scene_mood": ctx.context.current_scene.mood,
        "present_characters": ctx.context.current_scene.present_characters,
        "story_tension": ctx.context.story_state.dramatic_tension,
        "character_arc_progress": ctx.context.story_state.character_arc_progress,
        "message": f"{character_id} takes turn for {interaction_type}" + (f" with {target_character}" if target_character else "")
    }


@function_tool
async def update_scene_context(
    ctx: RunContextWrapper[MovieContext],
    location: Optional[str] = None,
    mood: Optional[str] = None,
    add_characters: Optional[List[str]] = None,
    remove_characters: Optional[List[str]] = None,
    add_objectives: Optional[List[str]] = None,
    dramatic_tension_target: Optional[float] = None
) -> Dict[str, Any]:
    """
    Update the current scene context dynamically.
    """
    if not ctx.context.current_scene:
        return {
            "success": False,
            "error": "No active scene to update",
            "suggestion": "Start a new scene first"
        }
    
    scene = ctx.context.current_scene
    changes = []
    
    # Update location
    if location and location != scene.location:
        old_location = scene.location
        scene.location = location
        changes.append(f"Location: {old_location} → {location}")
    
    # Update mood
    if mood and mood != scene.mood:
        old_mood = scene.mood
        scene.mood = mood
        changes.append(f"Mood: {old_mood} → {mood}")
        
        # Adjust tension based on mood
        mood_tension = {
            "tense": 0.8, "dramatic": 0.9, "suspenseful": 0.85,
            "calm": 0.3, "peaceful": 0.2, "neutral": 0.5,
            "confrontational": 0.95, "mysterious": 0.7
        }
        if mood in mood_tension:
            ctx.context.story_state.dramatic_tension = mood_tension[mood]
    
    # Add characters
    if add_characters:
        for char_id in add_characters:
            if char_id in ctx.context.characters and char_id not in scene.present_characters:
                scene.present_characters.append(char_id)
                changes.append(f"Added character: {char_id}")
    
    # Remove characters
    if remove_characters:
        for char_id in remove_characters:
            if char_id in scene.present_characters:
                scene.present_characters.remove(char_id)
                changes.append(f"Removed character: {char_id}")
    
    # Add objectives
    if add_objectives:
        for objective in add_objectives:
            if objective not in scene.scene_objectives:
                scene.scene_objectives.append(objective)
                changes.append(f"Added objective: {objective}")
    
    # Update tension target
    if dramatic_tension_target is not None:
        old_target = scene.dramatic_tension_target
        scene.dramatic_tension_target = dramatic_tension_target
        ctx.context.story_state.dramatic_tension = dramatic_tension_target
        changes.append(f"Tension target: {old_target:.2f} → {dramatic_tension_target:.2f}")
    
    return {
        "success": True,
        "changes_made": changes,
        "scene_state": {
            "location": scene.location,
            "mood": scene.mood,
            "present_characters": scene.present_characters,
            "objectives": scene.scene_objectives,
            "tension_target": scene.dramatic_tension_target
        },
        "story_tension": ctx.context.story_state.dramatic_tension,
        "message": f"Updated scene with {len(changes)} changes"
    }


@function_tool
async def check_scene_objectives(
    ctx: RunContextWrapper[MovieContext]
) -> Dict[str, Any]:
    """
    Check progress on current scene objectives using story state.
    """
    if not ctx.context.current_scene:
        return {
            "success": False,
            "error": "No active scene",
            "suggestion": "Start a new scene first"
        }
    
    scene = ctx.context.current_scene
    story_state = ctx.context.story_state
    
    # Analyze objective completion based on story progression
    objectives_status = []
    for objective in scene.scene_objectives:
        progress = 0.0
        status = "not_started"
        
        # Determine progress based on objective type and story state
        if "investigation" in objective.lower():
            progress = story_state.conflict_progress
            status = "completed" if progress >= 0.8 else "in_progress" if progress > 0.2 else "not_started"
        elif "interrogation" in objective.lower() or "question" in objective.lower():
            progress = story_state.character_arc_progress
            status = "completed" if progress >= 0.7 else "in_progress" if progress > 0.1 else "not_started"
        elif "resolution" in objective.lower() or "reveal" in objective.lower():
            progress = story_state.resolution_readiness
            status = "completed" if progress >= 0.8 else "in_progress" if progress > 0.3 else "not_started"
        else:
            # General objectives based on overall story progress
            avg_progress = (story_state.setup_progress + story_state.conflict_progress + 
                          story_state.character_arc_progress) / 3
            progress = avg_progress
            status = "completed" if progress >= 0.8 else "in_progress" if progress > 0.3 else "not_started"
        
        objectives_status.append({
            "objective": objective,
            "status": status,
            "progress": progress
        })
    
    # Calculate overall scene completion
    total_progress = sum(obj["progress"] for obj in objectives_status) / len(objectives_status) if objectives_status else 0.0
    
    return {
        "success": True,
        "scene_location": scene.location,
        "objectives": objectives_status,
        "total_progress": total_progress,
        "completion_estimate": total_progress >= 0.8,
        "story_metrics": {
            "dramatic_tension": story_state.dramatic_tension,
            "conflict_progress": story_state.conflict_progress,
            "character_arc_progress": story_state.character_arc_progress,
            "resolution_readiness": story_state.resolution_readiness
        },
        "message": f"Scene is {total_progress * 100:.1f}% complete"
    }


@function_tool
async def end_current_scene(
    ctx: RunContextWrapper[MovieContext],
    reason: str,
    completion_status: str = "complete"
) -> Dict[str, Any]:
    """
    End the current scene and update story progression.
    """
    if not ctx.context.current_scene:
        return {
            "success": False,
            "error": "No active scene to end"
        }
    
    scene = ctx.context.current_scene
    
    # Get final scene metrics
    objectives_check = await check_scene_objectives(ctx)
    
    # Update story progression based on completion
    if completion_status == "complete":
        ctx.context.story_state.setup_progress = min(1.0, ctx.context.story_state.setup_progress + 0.3)
        if scene.dramatic_tension_target >= 0.7:
            ctx.context.story_state.resolution_readiness = min(1.0, ctx.context.story_state.resolution_readiness + 0.2)
    
    scene_summary = {
        "location": scene.location,
        "mood": scene.mood,
        "characters_involved": scene.present_characters,
        "objectives": scene.scene_objectives,
        "objectives_progress": objectives_check.get("total_progress", 0.0),
        "completion_status": completion_status,
        "end_reason": reason,
        "final_tension": ctx.context.story_state.dramatic_tension
    }
    
    # Clear current scene
    ctx.context.current_scene = None
    
    return {
        "success": True,
        "scene_ended": True,
        "completion_status": completion_status,
        "scene_summary": scene_summary,
        "final_story_state": {
            "dramatic_tension": ctx.context.story_state.dramatic_tension,
            "setup_progress": ctx.context.story_state.setup_progress,
            "conflict_progress": ctx.context.story_state.conflict_progress,
            "character_arc_progress": ctx.context.story_state.character_arc_progress,
            "resolution_readiness": ctx.context.story_state.resolution_readiness
        },
        "message": f"Scene ended: {reason} ({completion_status})"
    }


@function_tool
async def get_scene_status(
    ctx: RunContextWrapper[MovieContext]
) -> Dict[str, Any]:
    """
    Get comprehensive status of current scene and story from MovieContext.
    """
    if not ctx.context.current_scene:
        return {
            "success": True,
            "has_active_scene": False,
            "story_state": {
                "dramatic_tension": ctx.context.story_state.dramatic_tension,
                "setup_progress": ctx.context.story_state.setup_progress,
                "conflict_progress": ctx.context.story_state.conflict_progress,
                "character_arc_progress": ctx.context.story_state.character_arc_progress,
                "resolution_readiness": ctx.context.story_state.resolution_readiness
            },
            "total_characters": len(ctx.context.characters),
            "message": "No active scene"
        }
    
    scene = ctx.context.current_scene
    
    # Get character details for present characters
    present_character_details = {}
    for char_id in scene.present_characters:
        if char_id in ctx.context.characters:
            char = ctx.context.characters[char_id]
            present_character_details[char_id] = {
                "name": char.name,
                "role": char.story_role.value,
                "secrets_remaining": len(char.secrets)
            }
    
    return {
        "success": True,
        "has_active_scene": True,
        "scene_details": {
            "location": scene.location,
            "mood": scene.mood,
            "present_characters": scene.present_characters,
            "character_details": present_character_details,
            "objectives": scene.scene_objectives,
            "tension_target": scene.dramatic_tension_target
        },
        "story_state": {
            "dramatic_tension": ctx.context.story_state.dramatic_tension,
            "setup_progress": ctx.context.story_state.setup_progress,
            "conflict_progress": ctx.context.story_state.conflict_progress,
            "character_arc_progress": ctx.context.story_state.character_arc_progress,
            "resolution_readiness": ctx.context.story_state.resolution_readiness
        },
        "total_characters": len(ctx.context.characters),
        "message": f"Active scene at {scene.location} with {len(scene.present_characters)} characters"
    } 