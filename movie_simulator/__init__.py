"""
Movie Simulator Package
Core package for the Movie Simulator application.
"""

from .core.logger import get_logger

# Initialize package logger
logger = get_logger("MovieSimulator")

__version__ = "0.1.0"
__author__ = "Movie Simulator Team"

try:
    # Import core components
    from .core.simulation import MovieSimulation
    from .core.models.story_models import (
        CharacterProfile, 
        CharacterRole, 
        StoryState, 
        StoryGenre,
        MovieContext
    )
    
    __all__ = ['MovieSimulation', 'CharacterProfile', 'CharacterRole', 'StoryState', 'StoryGenre', 'MovieContext']
    
except ImportError as e:
    logger.warning(f"Some imports failed: {e}", "import")
    __all__ = [] 