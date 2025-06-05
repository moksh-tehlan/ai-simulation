"""
Story Tools for Plot Progression and Structure Management
Implements the story management system outlined in plan.md
"""

from agents import function_tool
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import random


@dataclass 
class StoryBeat:
    """Individual story beat/plot point"""
    name: str
    description: str
    completion_percent: float = 0.0
    required_characters: Optional[List[str]] = None
    dramatic_tension_target: float = 0.5
    objectives: Optional[List[str]] = None


class StoryStructure:
    """Manages story progression and plot beats"""
    
    def __init__(self):
        self.beats: Dict[str, StoryBeat] = {}
        self.current_beat: str = "setup"
        self.beat_order: List[str] = [
            "setup", "inciting_incident", "rising_action", 
            "midpoint", "climax", "resolution"
        ]
        self.completion_thresholds = {
            "setup": 0.8,
            "inciting_incident": 0.7,
            "rising_action": 0.6,
            "midpoint": 0.8,
            "climax": 0.9,
            "resolution": 1.0
        }
    
    def add_beat(self, beat: StoryBeat):
        """Add a story beat to the structure"""
        self.beats[beat.name] = beat
    
    def advance_beat(self, beat_name: str, completion: float) -> bool:
        """Mark progress on a story beat"""
        if beat_name in self.beats:
            self.beats[beat_name].completion_percent = min(1.0, completion)
            return True
        return False
    
    def get_next_beat(self) -> Optional[str]:
        """Determine the next story beat to focus on"""
        current_index = self.beat_order.index(self.current_beat) if self.current_beat in self.beat_order else 0
        
        # Check if current beat is complete enough to advance
        threshold = self.completion_thresholds.get(self.current_beat, 0.8)
        current_completion = self.beats.get(self.current_beat, StoryBeat("", "")).completion_percent
        
        if current_completion >= threshold and current_index < len(self.beat_order) - 1:
            return self.beat_order[current_index + 1]
        
        return self.current_beat
    
    def get_story_progress(self) -> Dict[str, float]:
        """Calculate overall story progression metrics"""
        setup_beats = ["setup", "inciting_incident"]
        conflict_beats = ["rising_action", "midpoint"] 
        resolution_beats = ["climax", "resolution"]
        
        setup_progress = sum(
            self.beats.get(beat, StoryBeat("", "")).completion_percent 
            for beat in setup_beats
        ) / len(setup_beats)
        
        conflict_progress = sum(
            self.beats.get(beat, StoryBeat("", "")).completion_percent 
            for beat in conflict_beats
        ) / len(conflict_beats)
        
        resolution_progress = sum(
            self.beats.get(beat, StoryBeat("", "")).completion_percent 
            for beat in resolution_beats
        ) / len(resolution_beats)
        
        overall_progress = sum(
            beat.completion_percent for beat in self.beats.values()
        ) / max(len(self.beats), 1)
        
        return {
            "setup_progress": setup_progress,
            "conflict_progress": conflict_progress,
            "resolution_progress": resolution_progress,
            "overall_progress": overall_progress
        }


# Global story structure
STORY_STRUCTURE = StoryStructure()


@function_tool
def check_plot_progress() -> Dict[str, Any]:
    """
    Check progress on main plot objectives and story structure.
    
    Returns:
        Dictionary with progress metrics and recommendations
    """
    progress = STORY_STRUCTURE.get_story_progress()
    current_beat = STORY_STRUCTURE.current_beat
    next_beat = STORY_STRUCTURE.get_next_beat()
    
    # Generate recommendations based on progress
    recommendations = []
    
    if progress["setup_progress"] < 0.5:
        recommendations.append("Focus on character establishment and world-building")
    elif progress["conflict_progress"] < 0.3 and progress["setup_progress"] > 0.7:
        recommendations.append("Introduce main conflict and complications")
    elif progress["resolution_progress"] < 0.2 and progress["conflict_progress"] > 0.6:
        recommendations.append("Begin building toward climax and resolution")
    
    if current_beat != next_beat:
        recommendations.append(f"Ready to advance from '{current_beat}' to '{next_beat}'")
    
    return {
        "current_beat": current_beat,
        "next_beat": next_beat,
        "progress_metrics": progress,
        "recommendations": recommendations,
        "story_beats": {name: beat.completion_percent for name, beat in STORY_STRUCTURE.beats.items()}
    }


@function_tool
def advance_story_beat(beat_name: str, completion_percent: float) -> Dict[str, Any]:
    """
    Mark progress on specific story beats.
    
    Args:
        beat_name: Name of the story beat to advance
        completion_percent: How complete this beat is (0.0 to 1.0)
    
    Returns:
        Updated story status
    """
    success = STORY_STRUCTURE.advance_beat(beat_name, completion_percent)
    
    if success:
        # Update current beat if this beat is now complete enough
        next_beat = STORY_STRUCTURE.get_next_beat()
        if next_beat != STORY_STRUCTURE.current_beat:
            STORY_STRUCTURE.current_beat = next_beat
        
        return {
            "success": True,
            "beat_updated": beat_name,
            "new_completion": completion_percent,
            "current_beat": STORY_STRUCTURE.current_beat,
            "message": f"Advanced '{beat_name}' to {completion_percent:.1%} completion"
        }
    else:
        return {
            "success": False,
            "error": f"Story beat '{beat_name}' not found",
            "available_beats": list(STORY_STRUCTURE.beats.keys())
        }


@function_tool
def adjust_dramatic_tension(adjustment: float, reason: str) -> Dict[str, Any]:
    """
    Adjust overall dramatic tension in the story.
    
    Args:
        adjustment: Amount to change tension (-1.0 to 1.0)
        reason: Explanation for the tension change
    
    Returns:
        Tension adjustment results
    """
    # This would interact with the story state in your MovieContext
    # For now, implementing as a recommendation system
    
    current_beat = STORY_STRUCTURE.current_beat
    target_tensions = {
        "setup": 0.3,
        "inciting_incident": 0.6,
        "rising_action": 0.7,
        "midpoint": 0.8,
        "climax": 0.95,
        "resolution": 0.2
    }
    
    recommended_tension = target_tensions.get(current_beat, 0.5)
    new_tension = max(0.0, min(1.0, recommended_tension + adjustment))
    
    return {
        "tension_adjustment": adjustment,
        "reason": reason,
        "current_beat": current_beat,
        "recommended_tension": recommended_tension,
        "adjusted_tension": new_tension,
        "tension_status": "high" if new_tension > 0.7 else "moderate" if new_tension > 0.4 else "low"
    }


@function_tool
def create_story_beat(
    beat_name: str,
    description: str,
    required_characters: List[str],
    tension_target: float = 0.5,
    objectives: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new story beat with specific objectives.
    
    Args:
        beat_name: Unique name for the story beat
        description: What happens in this beat
        required_characters: Characters that must be involved
        tension_target: Target dramatic tension level
        objectives: List of objectives to accomplish
    
    Returns:
        Story beat creation results
    """
    if objectives is None:
        objectives = []
    
    beat = StoryBeat(
        name=beat_name,
        description=description,
        required_characters=required_characters,
        dramatic_tension_target=tension_target,
        objectives=objectives
    )
    
    STORY_STRUCTURE.add_beat(beat)
    
    return {
        "success": True,
        "beat_created": beat_name,
        "description": description,
        "required_characters": required_characters,
        "tension_target": tension_target,
        "objectives": objectives,
        "message": f"Created story beat: {beat_name}"
    }


@function_tool
def get_story_structure_status() -> Dict[str, Any]:
    """
    Get comprehensive status of the story structure.
    
    Returns:
        Complete story structure information
    """
    progress = STORY_STRUCTURE.get_story_progress()
    
    beat_details = {}
    for name, beat in STORY_STRUCTURE.beats.items():
        beat_details[name] = {
            "description": beat.description,
            "completion": beat.completion_percent,
            "tension_target": beat.dramatic_tension_target,
            "required_characters": beat.required_characters or [],
            "objectives": beat.objectives or []
        }
    
    return {
        "current_beat": STORY_STRUCTURE.current_beat,
        "next_beat": STORY_STRUCTURE.get_next_beat(),
        "beat_order": STORY_STRUCTURE.beat_order,
        "progress_summary": progress,
        "beat_details": beat_details,
        "completion_thresholds": STORY_STRUCTURE.completion_thresholds
    }


@function_tool 
def suggest_plot_development() -> Dict[str, Any]:
    """
    Suggest next plot developments based on current story state.
    
    Returns:
        Suggestions for advancing the plot
    """
    current_beat = STORY_STRUCTURE.current_beat
    progress = STORY_STRUCTURE.get_story_progress()
    
    suggestions = []
    
    beat_suggestions = {
        "setup": [
            "Establish character relationships and conflicts",
            "Introduce the story world and rules",
            "Plant seeds for future plot developments",
            "Show characters in their normal lives before disruption"
        ],
        "inciting_incident": [
            "Create the event that kicks off the main conflict",
            "Disrupt the characters' normal world",
            "Introduce the central mystery or problem",
            "Force characters to make important decisions"
        ],
        "rising_action": [
            "Escalate conflicts between characters",
            "Reveal character secrets and hidden motives", 
            "Introduce complications and obstacles",
            "Deepen character relationships and rivalries"
        ],
        "midpoint": [
            "Major revelation or plot twist",
            "Character alliances shift dramatically",
            "Stakes are raised significantly",
            "False victory or devastating setback"
        ],
        "climax": [
            "Final confrontation between opposing forces",
            "Character's most important choice",
            "Resolution of the central conflict",
            "Maximum dramatic tension and stakes"
        ],
        "resolution": [
            "Show consequences of the climax",
            "Resolve remaining character arcs",
            "Provide emotional closure",
            "Hint at character's future paths"
        ]
    }
    
    suggestions = beat_suggestions.get(current_beat, ["Continue developing the current storyline"])
    
    return {
        "current_beat": current_beat,
        "suggested_developments": suggestions,
        "progress_analysis": progress,
        "priority_focus": f"Focus on {current_beat} elements",
        "next_milestone": STORY_STRUCTURE.get_next_beat()
    }
