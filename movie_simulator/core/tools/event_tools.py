"""
Dramatic event injection tools.

These tools inject dramatic events, plot twists, and conflicts
to enhance story tension and progression.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import random

from movie_simulator.core.models.story_models import MovieContext, StoryGenre, CharacterRole
from movie_simulator.core.logger import get_logger

# Initialize logger
logger = get_logger("EventTools")

class EventType(Enum):
    """Types of dramatic events that can be injected."""
    PLOT_TWIST = "plot_twist"
    CHARACTER_REVELATION = "character_revelation"
    CONFLICT_ESCALATION = "conflict_escalation"
    BETRAYAL = "betrayal"
    ROMANTIC_COMPLICATION = "romantic_complication"
    MYSTERIOUS_OCCURRENCE = "mysterious_occurrence"
    DEADLINE_PRESSURE = "deadline_pressure"
    MORAL_DILEMMA = "moral_dilemma"
    UNEXPECTED_ALLY = "unexpected_ally"
    MAJOR_SETBACK = "major_setback"


class DramaticEventInjector:
    """Injects dramatic events and plot developments into the story."""
    
    def __init__(self):
        """Initialize the dramatic event injector."""
        self._context: Optional[MovieContext] = None
        
        # Define event templates by genre
        self.genre_events = {
            StoryGenre.MYSTERY: {
                EventType.PLOT_TWIST: [
                    "The victim is revealed to be alive",
                    "The detective discovers they are related to the suspect",
                    "A witness comes forward with contradictory evidence",
                    "The murder weapon belongs to an unexpected person"
                ],
                EventType.CHARACTER_REVELATION: [
                    "A character's past criminal record is exposed",
                    "Someone has been using a false identity",
                    "A character has been secretly investigating the case",
                    "Hidden family connections are revealed"
                ],
                EventType.MYSTERIOUS_OCCURRENCE: [
                    "A new piece of evidence mysteriously appears",
                    "Someone breaks into the detective's office",
                    "A threatening message is left for the investigator",
                    "Key evidence goes missing from the police station"
                ]
            },
            StoryGenre.ROMANCE: {
                EventType.ROMANTIC_COMPLICATION: [
                    "An ex-partner returns unexpectedly",
                    "A misunderstanding threatens the relationship",
                    "Family disapproval creates conflict",
                    "Career opportunities force a difficult choice"
                ],
                EventType.CHARACTER_REVELATION: [
                    "One character has been hiding their true profession",
                    "A character is already engaged to someone else",
                    "Past relationship trauma is revealed",
                    "A character has been lying about their background"
                ],
                EventType.MORAL_DILEMMA: [
                    "Choosing between love and family loyalty",
                    "Deciding whether to reveal a damaging secret",
                    "Picking between two equally deserving people",
                    "Weighing personal happiness against others' needs"
                ]
            },
            StoryGenre.THRILLER: {
                EventType.CONFLICT_ESCALATION: [
                    "The antagonist raises the stakes significantly",
                    "An innocent bystander becomes involved",
                    "Multiple threats emerge simultaneously",
                    "The safe haven is compromised"
                ],
                EventType.BETRAYAL: [
                    "A trusted ally is revealed as the enemy",
                    "Someone close betrays the protagonist's location",
                    "Information is leaked to the antagonist",
                    "A rescue attempt is actually a trap"
                ],
                EventType.DEADLINE_PRESSURE: [
                    "A bomb is set to explode in hours",
                    "Hostages' lives are threatened with a countdown",
                    "Evidence will be destroyed unless action is taken",
                    "The antagonist issues an ultimatum"
                ]
            }
        }
        
        # Generic events that work for any genre
        self.generic_events = {
            EventType.UNEXPECTED_ALLY: [
                "An enemy becomes an unlikely ally",
                "Help arrives from an unexpected source",
                "A minor character proves crucial to the plot",
                "Former rivals must work together"
            ],
            EventType.MAJOR_SETBACK: [
                "The protagonist's plan backfires spectacularly",
                "A key resource is lost or destroyed",
                "Trust between main characters is broken",
                "The situation becomes much worse than expected"
            ],
            EventType.MORAL_DILEMMA: [
                "The right choice has terrible consequences",
                "Helping one person means betraying another",
                "The truth would hurt someone innocent",
                "Success requires morally questionable actions"
            ]
        }
    
    def set_context(self, context: MovieContext) -> None:
        """Set the movie context for event operations."""
        self._context = context
    
    def inject_random_event(self, event_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Inject a random dramatic event appropriate for the current story.
        
        Args:
            event_type: Specific event type to inject (optional)
            
        Returns:
            Dictionary containing event information
        """
        if not self._context:
            return {"success": False, "error": "No context available"}
        
        try:
            # Determine event type
            if event_type:
                try:
                    selected_type = EventType(event_type)
                except ValueError:
                    return {"success": False, "error": f"Invalid event type: {event_type}"}
            else:
                selected_type = self._select_appropriate_event_type()
            
            # Get event description
            event_description = self._get_event_description(selected_type)
            
            # Apply event effects
            tension_change = self._calculate_tension_change(selected_type)
            if self._context:
                old_tension = self._context.story_state.dramatic_tension
                new_tension = max(0.0, min(1.0, old_tension + tension_change))
                self._context.story_state.dramatic_tension = new_tension
            
            event_info = {
                "success": True,
                "event_type": selected_type.value,
                "description": event_description,
                "tension_change": tension_change,
                "new_tension": new_tension if self._context else 0.5
            }
            
            logger.info("💥 DRAMATIC EVENT INJECTED!")
            logger.info(f"   Type: {selected_type.value.replace('_', ' ').title()}")
            logger.info(f"   Event: {event_description}")
            logger.info(f"   Tension: {old_tension:.2f} → {new_tension:.2f}")
            
            return event_info
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def inject_specific_event(self, event_type: str, description: str, tension_change: float = 0.0) -> Dict[str, Any]:
        """
        Inject a specific dramatic event with custom description.
        
        Args:
            event_type: Type of event
            description: Custom event description
            tension_change: How much to change tension (-1.0 to 1.0)
            
        Returns:
            Dictionary containing event information
        """
        if not self._context:
            return {"success": False, "error": "No context available"}
        
        try:
            # Validate event type
            try:
                event_enum = EventType(event_type)
            except ValueError:
                return {"success": False, "error": f"Invalid event type: {event_type}"}
            
            # Validate tension change
            if not (-1.0 <= tension_change <= 1.0):
                return {"success": False, "error": "Tension change must be between -1.0 and 1.0"}
            
            # Apply tension change
            old_tension = self._context.story_state.dramatic_tension
            new_tension = max(0.0, min(1.0, old_tension + tension_change))
            self._context.story_state.dramatic_tension = new_tension
            
            event_info = {
                "success": True,
                "event_type": event_type,
                "description": description,
                "tension_change": tension_change,
                "new_tension": new_tension
            }
            
            logger.info("💥 CUSTOM EVENT INJECTED!")
            logger.info(f"   Type: {event_type.replace('_', ' ').title()}")
            logger.info(f"   Event: {description}")
            logger.info(f"   Tension: {old_tension:.2f} → {new_tension:.2f}")
            
            return event_info
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_character_conflict(self, character1_id: str, character2_id: str, conflict_type: str = "general") -> Dict[str, Any]:
        """
        Create a conflict between two characters.
        
        Args:
            character1_id: First character's ID
            character2_id: Second character's ID
            conflict_type: Type of conflict (general, romantic, professional, moral)
            
        Returns:
            Dictionary containing conflict information
        """
        if not self._context:
            return {"success": False, "error": "No context available"}
        
        try:
            # Validate characters exist
            if character1_id not in self._context.characters:
                return {"success": False, "error": f"Character {character1_id} not found"}
            if character2_id not in self._context.characters:
                return {"success": False, "error": f"Character {character2_id} not found"}
            
            char1 = self._context.characters[character1_id]
            char2 = self._context.characters[character2_id]
            
            # Generate conflict description based on type
            conflict_templates = {
                "general": [
                    f"{char1.name} and {char2.name} have a heated disagreement",
                    f"{char1.name} accuses {char2.name} of betrayal",
                    f"Old grudges resurface between {char1.name} and {char2.name}",
                    f"{char1.name} and {char2.name} compete for the same goal"
                ],
                "romantic": [
                    f"{char1.name} is jealous of {char2.name}'s attention",
                    f"A love triangle forms involving {char1.name} and {char2.name}",
                    f"{char1.name} and {char2.name} both love the same person",
                    f"Past romantic history complicates {char1.name} and {char2.name}'s relationship"
                ],
                "professional": [
                    f"{char1.name} and {char2.name} clash over work methods",
                    f"Competition for promotion drives {char1.name} and {char2.name} apart",
                    f"{char1.name} questions {char2.name}'s professional competence",
                    f"Workplace politics pit {char1.name} against {char2.name}"
                ],
                "moral": [
                    f"{char1.name} and {char2.name} have opposing moral viewpoints",
                    f"{char1.name} disapproves of {char2.name}'s choices",
                    f"Ethical differences create tension between {char1.name} and {char2.name}",
                    f"{char1.name} and {char2.name} disagree on what's right"
                ]
            }
            
            templates = conflict_templates.get(conflict_type, conflict_templates["general"])
            conflict_description = random.choice(templates)
            
            # Increase tension
            tension_increase = random.uniform(0.1, 0.3)
            old_tension = self._context.story_state.dramatic_tension
            new_tension = min(1.0, old_tension + tension_increase)
            self._context.story_state.dramatic_tension = new_tension
            
            conflict_info = {
                "success": True,
                "character1": char1.name,
                "character2": char2.name,
                "conflict_type": conflict_type,
                "description": conflict_description,
                "tension_increase": tension_increase,
                "new_tension": new_tension
            }
            
            logger.info("⚔️ CHARACTER CONFLICT CREATED!")
            logger.info(f"   Characters: {char1.name} vs {char2.name}")
            logger.info(f"   Type: {conflict_type.title()}")
            logger.info(f"   Conflict: {conflict_description}")
            logger.info(f"   Tension: {old_tension:.2f} → {new_tension:.2f}")
            
            return conflict_info
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def inject_plot_twist(self, severity: str = "medium") -> Dict[str, Any]:
        """
        Inject a plot twist appropriate for the current genre and story beat.
        
        Args:
            severity: Severity of the twist (low, medium, high)
            
        Returns:
            Dictionary containing twist information
        """
        if not self._context:
            return {"success": False, "error": "No context available"}
        
        try:
            # Get genre-appropriate twist
            genre = self._context.story_state.genre
            current_beat = self._context.story_state.current_beat
            
            # Select twist based on genre
            if genre in self.genre_events and EventType.PLOT_TWIST in self.genre_events[genre]:
                twist_options = self.genre_events[genre][EventType.PLOT_TWIST]
            else:
                twist_options = [
                    "A hidden truth about a main character is revealed",
                    "The real antagonist is someone unexpected",
                    "A supposedly dead character returns",
                    "The protagonist's assumptions are completely wrong"
                ]
            
            twist_description = random.choice(twist_options)
            
            # Adjust tension based on severity and current beat
            tension_changes = {
                "low": (0.1, 0.2),
                "medium": (0.2, 0.4),
                "high": (0.3, 0.6)
            }
            
            min_change, max_change = tension_changes.get(severity, tension_changes["medium"])
            tension_change = random.uniform(min_change, max_change)
            
            # Higher tension changes near climax
            if current_beat in ["second_plot_point", "climax"]:
                tension_change *= 1.5
            
            old_tension = self._context.story_state.dramatic_tension
            new_tension = min(1.0, old_tension + tension_change)
            self._context.story_state.dramatic_tension = new_tension
            
            twist_info = {
                "success": True,
                "severity": severity,
                "description": twist_description,
                "tension_change": tension_change,
                "new_tension": new_tension,
                "story_beat": current_beat
            }
            
            logger.info("🌪️ PLOT TWIST INJECTED!")
            logger.info(f"   Severity: {severity.title()}")
            logger.info(f"   Twist: {twist_description}")
            logger.info(f"   Beat: {current_beat}")
            logger.info(f"   Tension: {old_tension:.2f} → {new_tension:.2f}")
            
            return twist_info
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_event_suggestions(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Get suggestions for dramatic events appropriate for the current story state.
        
        Args:
            count: Number of suggestions to return
            
        Returns:
            List of event suggestions
        """
        if not self._context:
            return []
        
        suggestions = []
        genre = self._context.story_state.genre
        current_beat = self._context.story_state.current_beat
        current_tension = self._context.story_state.dramatic_tension
        
        # Get appropriate event types for current context
        suitable_types = self._get_suitable_event_types(current_beat, current_tension)
        
        for i in range(min(count, len(suitable_types))):
            event_type = suitable_types[i]
            description = self._get_event_description(event_type)
            tension_change = self._calculate_tension_change(event_type)
            
            suggestions.append({
                "event_type": event_type.value,
                "description": description,
                "estimated_tension_change": tension_change,
                "appropriateness_score": self._score_event_appropriateness(event_type)
            })
        
        return suggestions
    
    def _select_appropriate_event_type(self) -> EventType:
        """Select an appropriate event type for the current story context."""
        if not self._context:
            return random.choice(list(EventType))
        
        current_beat = self._context.story_state.current_beat
        current_tension = self._context.story_state.dramatic_tension
        
        suitable_types = self._get_suitable_event_types(current_beat, current_tension)
        return random.choice(suitable_types) if suitable_types else random.choice(list(EventType))
    
    def _get_suitable_event_types(self, beat: str, tension: float) -> List[EventType]:
        """Get event types suitable for the current story state."""
        suitable = []
        
        # Early story beats - setup events
        if beat in ["setup", "inciting_incident"]:
            suitable.extend([EventType.CHARACTER_REVELATION, EventType.MYSTERIOUS_OCCURRENCE])
        
        # Mid story - escalate conflict
        elif beat in ["rising_action", "midpoint"]:
            suitable.extend([EventType.CONFLICT_ESCALATION, EventType.BETRAYAL, EventType.PLOT_TWIST])
        
        # Late story - major events
        elif beat in ["second_plot_point", "climax"]:
            suitable.extend([EventType.MAJOR_SETBACK, EventType.BETRAYAL, EventType.PLOT_TWIST])
        
        # Low tension - add excitement
        if tension < 0.4:
            suitable.extend([EventType.CONFLICT_ESCALATION, EventType.MYSTERIOUS_OCCURRENCE])
        
        # High tension - add complications
        elif tension > 0.7:
            suitable.extend([EventType.MORAL_DILEMMA, EventType.UNEXPECTED_ALLY])
        
        return suitable if suitable else list(EventType)
    
    def _get_event_description(self, event_type: EventType) -> str:
        """Get a description for the specified event type."""
        if not self._context:
            return "A dramatic event occurs"
        
        genre = self._context.story_state.genre
        
        # Try genre-specific events first
        if genre in self.genre_events and event_type in self.genre_events[genre]:
            return random.choice(self.genre_events[genre][event_type])
        
        # Fall back to generic events
        if event_type in self.generic_events:
            return random.choice(self.generic_events[event_type])
        
        # Default descriptions
        defaults = {
            EventType.PLOT_TWIST: "An unexpected revelation changes everything",
            EventType.CHARACTER_REVELATION: "A character's secret is exposed",
            EventType.CONFLICT_ESCALATION: "The conflict intensifies dramatically",
            EventType.BETRAYAL: "Someone betrays the protagonist's trust",
            EventType.ROMANTIC_COMPLICATION: "Romance becomes complicated",
            EventType.MYSTERIOUS_OCCURRENCE: "Something mysterious happens",
            EventType.DEADLINE_PRESSURE: "Time is running out",
            EventType.MORAL_DILEMMA: "A difficult moral choice must be made",
            EventType.UNEXPECTED_ALLY: "Help comes from an unexpected source",
            EventType.MAJOR_SETBACK: "Plans go seriously wrong"
        }
        
        return defaults.get(event_type, "A dramatic event occurs")
    
    def _calculate_tension_change(self, event_type: EventType) -> float:
        """Calculate how much an event type should change dramatic tension."""
        tension_impacts = {
            EventType.PLOT_TWIST: random.uniform(0.2, 0.4),
            EventType.CHARACTER_REVELATION: random.uniform(0.1, 0.3),
            EventType.CONFLICT_ESCALATION: random.uniform(0.3, 0.5),
            EventType.BETRAYAL: random.uniform(0.4, 0.6),
            EventType.ROMANTIC_COMPLICATION: random.uniform(0.1, 0.3),
            EventType.MYSTERIOUS_OCCURRENCE: random.uniform(0.2, 0.4),
            EventType.DEADLINE_PRESSURE: random.uniform(0.4, 0.6),
            EventType.MORAL_DILEMMA: random.uniform(0.1, 0.3),
            EventType.UNEXPECTED_ALLY: random.uniform(-0.2, 0.1),  # Can reduce tension
            EventType.MAJOR_SETBACK: random.uniform(0.3, 0.5)
        }
        
        return tension_impacts.get(event_type, random.uniform(0.1, 0.3))
    
    def _score_event_appropriateness(self, event_type: EventType) -> float:
        """Score how appropriate an event type is for the current context."""
        if not self._context:
            return 0.5
        
        score = 0.5  # Base score
        
        genre = self._context.story_state.genre
        beat = self._context.story_state.current_beat
        tension = self._context.story_state.dramatic_tension
        
        # Genre appropriateness
        if genre in self.genre_events and event_type in self.genre_events[genre]:
            score += 0.3
        
        # Beat appropriateness
        beat_preferences = {
            "setup": [EventType.CHARACTER_REVELATION, EventType.MYSTERIOUS_OCCURRENCE],
            "rising_action": [EventType.CONFLICT_ESCALATION, EventType.PLOT_TWIST],
            "climax": [EventType.BETRAYAL, EventType.MAJOR_SETBACK]
        }
        
        if beat in beat_preferences and event_type in beat_preferences[beat]:
            score += 0.2
        
        # Tension appropriateness
        if tension < 0.4 and event_type in [EventType.CONFLICT_ESCALATION, EventType.MYSTERIOUS_OCCURRENCE]:
            score += 0.2
        elif tension > 0.7 and event_type in [EventType.UNEXPECTED_ALLY, EventType.MORAL_DILEMMA]:
            score += 0.2
        
        return min(1.0, score) 