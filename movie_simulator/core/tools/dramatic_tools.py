"""
Dramatic Tools for Event Injection and Tension Management
Implements the dramatic event system outlined in plan.md
"""

from agents import function_tool
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import random


@dataclass
class DramaticEvent:
    """A dramatic event that can be injected into the story"""
    event_id: str
    event_type: str
    description: str
    affected_characters: List[str]
    intensity: float  # 0.0 to 1.0
    timestamp: datetime
    consequences: List[str] = field(default_factory=list)
    tension_impact: float = 0.0


class DramaticEventLibrary:
    """Library of dramatic events categorized by type and intensity"""
    
    def __init__(self):
        self.event_templates = {
            "revelation": [
                "A character reveals a hidden secret about their past",
                "Someone discovers evidence of another character's deception", 
                "A character admits to a lie they've been telling",
                "Hidden relationships between characters are exposed"
            ],
            "conflict": [
                "Two characters have a heated argument over conflicting goals",
                "A character betrays another character's trust",
                "Someone makes an accusation against another character",
                "Old grudges resurface between characters"
            ],
            "mysterious_occurrence": [
                "A strange, unexplained event happens",
                "Someone receives a cryptic message or warning",
                "An important object goes missing",
                "A threatening message is left for a character"
            ],
            "emotional_moment": [
                "A character breaks down emotionally",
                "Two characters share a deeply personal moment",
                "Someone confesses their feelings to another character",
                "A character faces their deepest fear"
            ],
            "plot_twist": [
                "A trusted character is revealed to have ulterior motives",
                "The true nature of the central mystery is revealed",
                "An ally becomes an enemy or vice versa",
                "A character thought to be uninvolved is deeply connected"
            ],
            "external_pressure": [
                "A deadline is imposed that forces urgent action",
                "Outside forces threaten the characters",
                "New information changes everything",
                "An authority figure intervenes in the situation"
            ]
        }
        
        self.intensity_modifiers = {
            "low": 0.2,
            "moderate": 0.5,
            "high": 0.8,
            "extreme": 1.0
        }
    
    def get_random_event(self, event_type: Optional[str] = None, intensity: str = "moderate") -> Dict[str, Any]:
        """Get a random dramatic event template"""
        if event_type and event_type in self.event_templates:
            available_types = [event_type]
        else:
            available_types = list(self.event_templates.keys())
        
        selected_type = random.choice(available_types)
        description = random.choice(self.event_templates[selected_type])
        intensity_value = self.intensity_modifiers.get(intensity, 0.5)
        
        return {
            "type": selected_type,
            "description": description,
            "intensity": intensity_value,
            "tension_impact": intensity_value * 0.4  # Events increase tension
        }


# Global event library and storage
EVENT_LIBRARY = DramaticEventLibrary()
ACTIVE_EVENTS: List[DramaticEvent] = []


@function_tool
def inject_dramatic_event(
    event_type: str,
    description: str,
    affected_characters: List[str],
    intensity: float
) -> Dict[str, Any]:
    """
    Inject a specific dramatic event into the story.
    
    Args:
        event_type: Type of dramatic event
        description: What happens in the event
        affected_characters: Characters involved in the event
        intensity: Dramatic intensity (0.0 to 1.0)
    
    Returns:
        Event injection results
    """
    event = DramaticEvent(
        event_id=f"event_{len(ACTIVE_EVENTS) + 1}_{datetime.now().timestamp()}",
        event_type=event_type,
        description=description,
        affected_characters=affected_characters,
        intensity=max(0.0, min(1.0, intensity)),
        timestamp=datetime.now(),
        tension_impact=intensity * 0.3
    )
    
    ACTIVE_EVENTS.append(event)
    
    return {
        "event_id": event.event_id,
        "success": True,
        "event_type": event_type,
        "description": description,
        "affected_characters": affected_characters,
        "intensity": event.intensity,
        "tension_increase": event.tension_impact,
        "timestamp": event.timestamp.isoformat(),
        "message": f"Injected {event_type} event affecting {len(affected_characters)} characters"
    }


@function_tool
def inject_random_event(
    target_characters: Optional[List[str]] = None,
    event_type: Optional[str] = None,
    intensity_level: str = "moderate"
) -> Dict[str, Any]:
    """
    Inject a random dramatic event to spice up the story.
    
    Args:
        target_characters: Specific characters to involve (optional)
        event_type: Type of event to create (optional, will be random if not specified)
        intensity_level: "low", "moderate", "high", or "extreme"
    
    Returns:
        Random event injection results
    """
    if target_characters is None:
        target_characters = ["random_character"]  # Would be populated from story context
    
    event_template = EVENT_LIBRARY.get_random_event(event_type, intensity_level)
    
    # Customize the description based on target characters
    description = event_template["description"]
    if len(target_characters) == 1:
        description = description.replace("characters", target_characters[0])
        description = description.replace("A character", target_characters[0])
        description = description.replace("Someone", target_characters[0])
    
    return inject_dramatic_event(
        event_type=event_template["type"],
        description=description,
        affected_characters=target_characters,
        intensity=event_template["intensity"]
    )


@function_tool
def escalate_existing_conflict(conflict_id: str, escalation_description: str) -> Dict[str, Any]:
    """
    Escalate an existing conflict or dramatic situation.
    
    Args:
        conflict_id: ID of the conflict to escalate
        escalation_description: How the conflict escalates
    
    Returns:
        Escalation results
    """
    # Find existing conflict/event
    existing_event = None
    for event in ACTIVE_EVENTS:
        if event.event_id == conflict_id or conflict_id in event.description.lower():
            existing_event = event
            break
    
    if existing_event:
        # Create escalation event
        escalation_event = DramaticEvent(
            event_id=f"escalation_{conflict_id}_{datetime.now().timestamp()}",
            event_type="conflict_escalation",
            description=f"ESCALATION: {escalation_description}",
            affected_characters=existing_event.affected_characters,
            intensity=min(1.0, existing_event.intensity + 0.2),
            timestamp=datetime.now(),
            tension_impact=0.3
        )
        
        ACTIVE_EVENTS.append(escalation_event)
        
        return {
            "success": True,
            "original_conflict": existing_event.event_id,
            "escalation_id": escalation_event.event_id,
            "escalation_description": escalation_description,
            "new_intensity": escalation_event.intensity,
            "message": "Conflict successfully escalated"
        }
    else:
        return {
            "success": False,
            "error": f"Conflict '{conflict_id}' not found",
            "available_conflicts": [e.event_id for e in ACTIVE_EVENTS if "conflict" in e.event_type]
        }


@function_tool
def create_plot_twist(
    twist_description: str,
    revelation_target: str,
    impact_characters: List[str],
    twist_severity: str = "major"
) -> Dict[str, Any]:
    """
    Create a major plot twist that reframes the story.
    
    Args:
        twist_description: Description of the plot twist
        revelation_target: What/who the twist reveals information about
        impact_characters: Characters affected by this revelation
        twist_severity: "minor", "major", or "story_changing"
    
    Returns:
        Plot twist creation results
    """
    severity_intensities = {
        "minor": 0.4,
        "major": 0.7,
        "story_changing": 0.95
    }
    
    intensity = severity_intensities.get(twist_severity, 0.7)
    
    twist_event = DramaticEvent(
        event_id=f"twist_{datetime.now().timestamp()}",
        event_type="plot_twist",
        description=f"PLOT TWIST: {twist_description}",
        affected_characters=impact_characters,
        intensity=intensity,
        timestamp=datetime.now(),
        tension_impact=intensity * 0.5,
        consequences=[f"Reframes understanding of {revelation_target}"]
    )
    
    ACTIVE_EVENTS.append(twist_event)
    
    return {
        "success": True,
        "twist_id": twist_event.event_id,
        "description": twist_description,
        "revelation_target": revelation_target,
        "impact_characters": impact_characters,
        "severity": twist_severity,
        "intensity": intensity,
        "tension_impact": twist_event.tension_impact,
        "message": f"Created {twist_severity} plot twist affecting {len(impact_characters)} characters"
    }


@function_tool
def manage_story_pacing(pacing_adjustment: str, reason: str) -> Dict[str, Any]:
    """
    Adjust story pacing by recommending specific types of events.
    
    Args:
        pacing_adjustment: "speed_up", "slow_down", or "maintain"
        reason: Explanation for the pacing change
    
    Returns:
        Pacing management recommendations
    """
    recommendations = []
    
    if pacing_adjustment == "speed_up":
        recommendations = [
            "Inject a sudden conflict or confrontation",
            "Reveal important information quickly",
            "Force characters to make urgent decisions",
            "Introduce external pressure or deadline",
            "Skip less essential character moments"
        ]
    elif pacing_adjustment == "slow_down":
        recommendations = [
            "Focus on character development and emotions",
            "Explore relationships between characters",
            "Add introspective or contemplative moments", 
            "Develop atmosphere and setting details",
            "Allow characters to process recent events"
        ]
    else:  # maintain
        recommendations = [
            "Continue current story rhythm",
            "Balance action with character moments",
            "Maintain tension without overwhelming",
            "Develop plot steadily without rushing"
        ]
    
    return {
        "pacing_adjustment": pacing_adjustment,
        "reason": reason,
        "recommendations": recommendations,
        "suggested_event_types": get_pacing_event_types(pacing_adjustment),
        "message": f"Pacing adjustment: {pacing_adjustment}"
    }


def get_pacing_event_types(pacing: str) -> List[str]:
    """Get event types that support the desired pacing"""
    if pacing == "speed_up":
        return ["conflict", "revelation", "plot_twist", "external_pressure"]
    elif pacing == "slow_down":
        return ["emotional_moment", "character_development", "atmosphere"]
    else:
        return ["moderate_conflict", "gentle_revelation", "relationship_development"]


@function_tool
def get_dramatic_events_status() -> Dict[str, Any]:
    """
    Get status of all dramatic events in the story.
    
    Returns:
        Complete status of dramatic events
    """
    recent_events = sorted(ACTIVE_EVENTS, key=lambda e: e.timestamp, reverse=True)[:10]
    
    event_summary = []
    for event in recent_events:
        event_summary.append({
            "id": event.event_id,
            "type": event.event_type,
            "description": event.description,
            "intensity": event.intensity,
            "affected_characters": event.affected_characters,
            "timestamp": event.timestamp.strftime("%H:%M:%S"),
            "tension_impact": event.tension_impact
        })
    
    # Calculate overall dramatic metrics
    total_intensity = sum(e.intensity for e in recent_events)
    average_intensity = total_intensity / max(len(recent_events), 1)
    
    event_types = {}
    for event in ACTIVE_EVENTS:
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
    
    return {
        "total_events": len(ACTIVE_EVENTS),
        "recent_events": event_summary,
        "average_intensity": average_intensity,
        "event_type_distribution": event_types,
        "cumulative_tension_impact": sum(e.tension_impact for e in ACTIVE_EVENTS),
        "available_event_types": list(EVENT_LIBRARY.event_templates.keys())
    }


@function_tool
def suggest_dramatic_intervention() -> Dict[str, Any]:
    """
    Suggest dramatic interventions based on current story state.
    
    Returns:
        Suggestions for dramatic events to inject
    """
    # Analyze recent events to avoid repetition
    recent_types = [e.event_type for e in ACTIVE_EVENTS[-5:]]
    
    # Suggest varied event types
    all_types = list(EVENT_LIBRARY.event_templates.keys())
    underused_types = [t for t in all_types if recent_types.count(t) < 2]
    
    if not underused_types:
        underused_types = all_types
    
    suggestions = []
    for event_type in underused_types[:3]:
        template = EVENT_LIBRARY.get_random_event(event_type, "moderate")
        suggestions.append({
            "event_type": event_type,
            "description": template["description"],
            "intensity": template["intensity"],
            "reason": f"Underused event type, would add variety"
        })
    
    return {
        "suggested_events": suggestions,
        "recent_event_types": recent_types,
        "underused_types": underused_types,
        "message": f"Suggested {len(suggestions)} dramatic interventions for variety"
    }
