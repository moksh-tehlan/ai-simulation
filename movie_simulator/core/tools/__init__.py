"""
Core tools for movie simulation.

This package contains the tools used by agents to manipulate story state,
control story progression, and inject dramatic events.
"""

from .progression_tools import StoryProgressionManager
from .event_tools import DramaticEventInjector

__all__ = [
    'StoryProgressionManager',
    'DramaticEventInjector'
] 