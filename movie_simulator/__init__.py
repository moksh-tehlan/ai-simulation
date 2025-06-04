"""
Movie Simulator with OpenAI Agents SDK
A dynamic movie simulation system using AI agents.
"""

__version__ = "0.1.0"
__author__ = "Movie Simulator Team"

# Import with error handling for development
try:
    from .core.simulation import MovieSimulation
    from .core.models.story_models import StoryState, CharacterProfile, SceneContext
    
    __all__ = [
        "MovieSimulation",
        "StoryState", 
        "CharacterProfile",
        "SceneContext"
    ]
except ImportError as e:
    # Handle import errors during development
    print(f"Warning: Some imports failed: {e}")
    __all__ = [] 