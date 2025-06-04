"""
Story progression management tools.

These tools control the flow and development of the story,
managing beats, dramatic tension, and character development.
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random

from movie_simulator.core.models.story_models import MovieContext, StoryGenre, CharacterRole

class StoryBeat(Enum):
    """Standard story beats following three-act structure."""
    SETUP = "setup"
    INCITING_INCIDENT = "inciting_incident"
    FIRST_PLOT_POINT = "first_plot_point"
    RISING_ACTION = "rising_action"
    MIDPOINT = "midpoint"
    SECOND_PLOT_POINT = "second_plot_point"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


class StoryProgressionManager:
    """Manages story progression, beats, and dramatic tension."""
    
    def __init__(self):
        """Initialize the story progression manager."""
        self._context: Optional[MovieContext] = None
        
        # Define story progression templates by genre
        self.genre_progressions = {
            StoryGenre.MYSTERY: [
                StoryBeat.SETUP,
                StoryBeat.INCITING_INCIDENT,  # Crime discovered
                StoryBeat.FIRST_PLOT_POINT,   # Investigation begins
                StoryBeat.RISING_ACTION,      # Clues and red herrings
                StoryBeat.MIDPOINT,           # Major revelation
                StoryBeat.SECOND_PLOT_POINT,  # Final clue/confrontation
                StoryBeat.CLIMAX,             # Truth revealed
                StoryBeat.RESOLUTION          # Justice served
            ],
            StoryGenre.ROMANCE: [
                StoryBeat.SETUP,
                StoryBeat.INCITING_INCIDENT,  # Meet cute
                StoryBeat.FIRST_PLOT_POINT,   # Attraction/conflict
                StoryBeat.RISING_ACTION,      # Romance develops
                StoryBeat.MIDPOINT,           # Relationship test
                StoryBeat.SECOND_PLOT_POINT,  # Crisis/breakup
                StoryBeat.CLIMAX,             # Grand gesture
                StoryBeat.RESOLUTION          # Together
            ],
            StoryGenre.THRILLER: [
                StoryBeat.SETUP,
                StoryBeat.INCITING_INCIDENT,  # Threat introduced
                StoryBeat.FIRST_PLOT_POINT,   # Danger escalates
                StoryBeat.RISING_ACTION,      # Cat and mouse
                StoryBeat.MIDPOINT,           # Major setback
                StoryBeat.SECOND_PLOT_POINT,  # Final gambit
                StoryBeat.CLIMAX,             # Confrontation
                StoryBeat.RESOLUTION          # Safety restored
            ]
        }
        
        # Default progression for other genres
        self.default_progression = [
            StoryBeat.SETUP,
            StoryBeat.INCITING_INCIDENT,
            StoryBeat.FIRST_PLOT_POINT,
            StoryBeat.RISING_ACTION,
            StoryBeat.MIDPOINT,
            StoryBeat.SECOND_PLOT_POINT,
            StoryBeat.CLIMAX,
            StoryBeat.RESOLUTION
        ]
    
    def set_context(self, context: MovieContext) -> None:
        """Set the movie context for progression operations."""
        self._context = context
    
    def get_story_progression(self) -> List[str]:
        """
        Get the story progression beats for the current genre.
        
        Returns:
            List of story beats in order
        """
        if not self._context:
            return [beat.value for beat in self.default_progression]
        
        genre = self._context.story_state.genre
        progression = self.genre_progressions.get(genre, self.default_progression)
        return [beat.value for beat in progression]
    
    def advance_story_beat(self) -> bool:
        """
        Advance the story to the next beat.
        
        Returns:
            True if successful, False if already at the end
        """
        if not self._context:
            print("❌ No context available for story progression")
            return False
        
        try:
            current_beat = self._context.story_state.current_beat
            progression = self.get_story_progression()
            
            if current_beat not in progression:
                # Start at the beginning if current beat is unknown
                next_beat = progression[0]
            else:
                current_index = progression.index(current_beat)
                if current_index >= len(progression) - 1:
                    print("📚 Story has reached the final beat")
                    return False
                next_beat = progression[current_index + 1]
            
            self._context.story_state.current_beat = next_beat
            self._update_progression_metrics(next_beat)
            
            print(f"📖 Advanced story beat: {current_beat} → {next_beat}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to advance story beat: {e}")
            return False
    
    def set_story_beat(self, beat: str) -> bool:
        """
        Set the story to a specific beat.
        
        Args:
            beat: The story beat to set
            
        Returns:
            True if successful, False otherwise
        """
        if not self._context:
            print("❌ No context available for story progression")
            return False
        
        try:
            progression = self.get_story_progression()
            if beat not in progression:
                print(f"⚠️  Beat '{beat}' not valid for current genre")
                return False
            
            old_beat = self._context.story_state.current_beat
            self._context.story_state.current_beat = beat
            self._update_progression_metrics(beat)
            
            print(f"📖 Set story beat: {old_beat} → {beat}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set story beat: {e}")
            return False
    
    def adjust_dramatic_tension(self, change: float) -> bool:
        """
        Adjust the dramatic tension by a given amount.
        
        Args:
            change: Amount to change tension (-1.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._context:
            print("❌ No context available for tension adjustment")
            return False
        
        try:
            old_tension = self._context.story_state.dramatic_tension
            new_tension = max(0.0, min(1.0, old_tension + change))
            
            self._context.story_state.dramatic_tension = new_tension
            
            direction = "increased" if change > 0 else "decreased"
            print(f"⚡ Dramatic tension {direction}: {old_tension:.2f} → {new_tension:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to adjust dramatic tension: {e}")
            return False
    
    def set_dramatic_tension(self, tension: float) -> bool:
        """
        Set the dramatic tension to a specific level.
        
        Args:
            tension: Tension level (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._context:
            print("❌ No context available for tension setting")
            return False
        
        try:
            if not (0.0 <= tension <= 1.0):
                print("⚠️  Tension must be between 0.0 and 1.0")
                return False
            
            old_tension = self._context.story_state.dramatic_tension
            self._context.story_state.dramatic_tension = tension
            
            print(f"⚡ Set dramatic tension: {old_tension:.2f} → {tension:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set dramatic tension: {e}")
            return False
    
    def update_character_arc_progress(self, character_id: str, progress: float) -> bool:
        """
        Update a character's arc progression.
        
        Args:
            character_id: ID of the character
            progress: Arc progress (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._context:
            print("❌ No context available for character arc update")
            return False
        
        try:
            if character_id not in self._context.characters:
                print(f"⚠️  Character {character_id} not found")
                return False
            
            if not (0.0 <= progress <= 1.0):
                print("⚠️  Progress must be between 0.0 and 1.0")
                return False
            
            # Update overall character arc progress based on all characters
            total_progress = sum(
                progress if cid == character_id else 0.5  # Default progress for others
                for cid in self._context.characters.keys()
            )
            
            avg_progress = total_progress / len(self._context.characters)
            self._context.story_state.character_arc_progress = avg_progress
            
            character_name = self._context.characters[character_id].name
            print(f"👤 Updated {character_name}'s arc progress: {progress:.1%}")
            print(f"📊 Overall character arc progress: {avg_progress:.1%}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update character arc: {e}")
            return False
    
    def get_current_act(self) -> int:
        """
        Get the current act number based on story beat.
        
        Returns:
            Act number (1, 2, or 3)
        """
        if not self._context:
            return 1
        
        beat = self._context.story_state.current_beat
        
        # Act 1: Setup and inciting incident
        if beat in ["setup", "inciting_incident"]:
            return 1
        # Act 3: Climax and resolution
        elif beat in ["climax", "falling_action", "resolution"]:
            return 3
        # Act 2: Everything else
        else:
            return 2
    
    def get_recommended_tension_range(self) -> Tuple[float, float]:
        """
        Get the recommended dramatic tension range for current beat.
        
        Returns:
            Tuple of (min_tension, max_tension)
        """
        if not self._context:
            return (0.3, 0.7)
        
        beat = self._context.story_state.current_beat
        
        tension_ranges = {
            "setup": (0.1, 0.3),
            "inciting_incident": (0.3, 0.5),
            "first_plot_point": (0.4, 0.6),
            "rising_action": (0.5, 0.7),
            "midpoint": (0.6, 0.8),
            "second_plot_point": (0.7, 0.9),
            "climax": (0.8, 1.0),
            "falling_action": (0.4, 0.6),
            "resolution": (0.1, 0.3)
        }
        
        return tension_ranges.get(beat, (0.3, 0.7))
    
    def auto_adjust_tension_for_beat(self) -> bool:
        """
        Automatically adjust tension to appropriate level for current beat.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._context:
            return False
        
        try:
            min_tension, max_tension = self.get_recommended_tension_range()
            current_tension = self._context.story_state.dramatic_tension
            
            # If tension is outside recommended range, adjust it
            if current_tension < min_tension:
                target_tension = (min_tension + max_tension) / 2
            elif current_tension > max_tension:
                target_tension = (min_tension + max_tension) / 2
            else:
                # Already in good range
                return True
            
            return self.set_dramatic_tension(target_tension)
            
        except Exception as e:
            print(f"❌ Failed to auto-adjust tension: {e}")
            return False
    
    def get_progression_status(self) -> Dict[str, Any]:
        """
        Get a comprehensive status of story progression.
        
        Returns:
            Dictionary containing progression information
        """
        if not self._context:
            return {"error": "No context available"}
        
        progression = self.get_story_progression()
        current_beat = self._context.story_state.current_beat
        
        try:
            current_index = progression.index(current_beat)
            progress_percent = (current_index + 1) / len(progression)
        except ValueError:
            current_index = 0
            progress_percent = 0.0
        
        min_tension, max_tension = self.get_recommended_tension_range()
        current_tension = self._context.story_state.dramatic_tension
        tension_status = "optimal"
        
        if current_tension < min_tension:
            tension_status = "too_low"
        elif current_tension > max_tension:
            tension_status = "too_high"
        
        return {
            "current_beat": current_beat,
            "current_act": self.get_current_act(),
            "progress_percent": progress_percent,
            "beats_completed": current_index + 1,
            "total_beats": len(progression),
            "remaining_beats": len(progression) - current_index - 1,
            "dramatic_tension": {
                "current": current_tension,
                "recommended_range": (min_tension, max_tension),
                "status": tension_status
            },
            "story_metrics": {
                "setup_progress": self._context.story_state.setup_progress,
                "conflict_progress": self._context.story_state.conflict_progress,
                "character_arc_progress": self._context.story_state.character_arc_progress,
                "resolution_readiness": self._context.story_state.resolution_readiness
            }
        }
    
    def _update_progression_metrics(self, beat: str) -> None:
        """Update story progression metrics based on current beat."""
        if not self._context:
            return
        
        # Update metrics based on beat
        metrics_by_beat = {
            "setup": {"setup_progress": 0.8, "conflict_progress": 0.1},
            "inciting_incident": {"setup_progress": 1.0, "conflict_progress": 0.3},
            "first_plot_point": {"conflict_progress": 0.5, "character_arc_progress": 0.2},
            "rising_action": {"conflict_progress": 0.7, "character_arc_progress": 0.4},
            "midpoint": {"conflict_progress": 0.8, "character_arc_progress": 0.6},
            "second_plot_point": {"conflict_progress": 0.9, "character_arc_progress": 0.8},
            "climax": {"conflict_progress": 1.0, "character_arc_progress": 0.9, "resolution_readiness": 0.8},
            "falling_action": {"resolution_readiness": 0.9},
            "resolution": {"resolution_readiness": 1.0}
        }
        
        if beat in metrics_by_beat:
            for metric, value in metrics_by_beat[beat].items():
                setattr(self._context.story_state, metric, value) 