"""
Core data models for story simulation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class StoryGenre(Enum):
    """Supported story genres."""
    MYSTERY = "mystery"
    ROMANCE = "romance"
    THRILLER = "thriller"
    COMEDY = "comedy"
    DRAMA = "drama"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"


class CharacterRole(Enum):
    """Character roles in the story."""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    SUPPORTING = "supporting"
    MINOR = "minor"


@dataclass
class CharacterProfile:
    """Represents a character in the story."""
    id: str
    name: str
    background: str
    personality_traits: List[str]
    secrets: List[str]
    primary_motivation: str
    secondary_goals: List[str]
    fears: List[str]
    relationships: Dict[str, str] = field(default_factory=dict)
    story_role: CharacterRole = CharacterRole.SUPPORTING

    def __post_init__(self):
        """Validate character data after initialization."""
        if not self.name:
            raise ValueError("Character name cannot be empty")
        if not self.personality_traits:
            raise ValueError("Character must have at least one personality trait")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "background": self.background,
            "personality_traits": self.personality_traits,
            "secrets": self.secrets,
            "primary_motivation": self.primary_motivation,
            "secondary_goals": self.secondary_goals,
            "fears": self.fears,
            "relationships": self.relationships,
            "story_role": self.story_role.value,
        }


@dataclass
class StoryState:
    """Represents the current state of the story."""
    title: str
    genre: StoryGenre
    setting: str
    timeline: List[str]
    current_beat: str
    dramatic_tension: float = 0.5
    setup_progress: float = 0.0
    conflict_progress: float = 0.0
    character_arc_progress: float = 0.0
    resolution_readiness: float = 0.0

    def __post_init__(self):
        """Validate story state after initialization."""
        if not (0.0 <= self.dramatic_tension <= 1.0):
            raise ValueError("Dramatic tension must be between 0.0 and 1.0")
        if not self.title:
            raise ValueError("Story title cannot be empty")

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "genre": self.genre.value,
            "setting": self.setting,
            "timeline": self.timeline,
            "current_beat": self.current_beat,
            "dramatic_tension": self.dramatic_tension,
            "setup_progress": self.setup_progress,
            "conflict_progress": self.conflict_progress,
            "character_arc_progress": self.character_arc_progress,
            "resolution_readiness": self.resolution_readiness,
        }


@dataclass 
class SceneContext:
    """Represents the context of a current scene."""
    location: str
    time_period: str
    mood: str
    present_characters: List[str]
    scene_objectives: List[str]
    dramatic_tension_target: float = 0.5

    def __post_init__(self):
        """Validate scene context after initialization."""
        if not self.location:
            raise ValueError("Scene location cannot be empty")
        if not self.present_characters:
            raise ValueError("Scene must have at least one character present")

    def to_dict(self) -> dict:
        return {
            "location": self.location,
            "time_period": self.time_period,
            "mood": self.mood,
            "present_characters": self.present_characters,
            "scene_objectives": self.scene_objectives,
            "dramatic_tension_target": self.dramatic_tension_target,
        }


@dataclass
class MovieContext:
    """Central context object that holds all story state."""
    story_state: StoryState
    characters: Dict[str, CharacterProfile] = field(default_factory=dict)
    current_scene: Optional[SceneContext] = None
    current_time: datetime = field(default_factory=datetime.now)

    def add_character(self, character: CharacterProfile) -> None:
        """Add a character to the story."""
        if character.id in self.characters:
            raise ValueError(f"Character with ID {character.id} already exists")
        self.characters[character.id] = character

    def get_character(self, character_id: str) -> Optional[CharacterProfile]:
        """Get a character by ID."""
        return self.characters.get(character_id)

    def get_present_characters(self) -> List[str]:
        """Get list of characters present in current scene."""
        if self.current_scene:
            return self.current_scene.present_characters
        return []

    def update_dramatic_tension(self, new_tension: float) -> None:
        """Update the story's dramatic tension."""
        if not (0.0 <= new_tension <= 1.0):
            raise ValueError("Dramatic tension must be between 0.0 and 1.0")
        self.story_state.dramatic_tension = new_tension

    def to_dict(self) -> dict:
        return {
            "story_state": self.story_state.to_dict(),
            "characters": {cid: c.to_dict() for cid, c in self.characters.items()},
            "current_scene": self.current_scene.to_dict() if self.current_scene else None,
            "current_time": self.current_time.isoformat(),
        }
