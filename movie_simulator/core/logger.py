"""
Logger Service for Movie Simulator

A clean, structured logging service to replace print statements throughout the application.
Provides different log levels and formatted output for better debugging and monitoring.
"""

import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log levels for the Movie Simulator."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    PROGRESS = "PROGRESS"


class MovieSimulatorLogger:
    """
    Custom logger for the Movie Simulator with emoji-enhanced formatting.
    """
    
    def __init__(self, name: str = "MovieSimulator", level: LogLevel = LogLevel.INFO):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            level: Minimum log level to display
        """
        self.name = name
        self.level = level
        self.logger: logging.Logger  # Properly type the logger attribute
        self._setup_logger()
        
        # Emoji mappings for different log types
        self.emojis = {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.SUCCESS: "✅",
            LogLevel.PROGRESS: "🚀"
        }
        
        # Special emojis for specific contexts
        self.context_emojis = {
            "test": "🧪",
            "simulation": "🎬",
            "agent": "🤖",
            "character": "🎭",
            "story": "📖",
            "tools": "🔧",
            "event": "💥",
            "memory": "🧠",
            "scene": "🎬",
            "analysis": "📊",
            "config": "⚙️",
            "api": "🌐",
            "file": "📁",
            "director": "🎯",
            "conflict": "⚔️",
            "twist": "🌪️"
        }
    
    def _setup_logger(self):
        """Set up the internal Python logger."""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.propagate = False
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on current log level."""
        level_hierarchy = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.PROGRESS: 1,
            LogLevel.SUCCESS: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3
        }
        
        return level_hierarchy.get(level, 1) >= level_hierarchy.get(self.level, 1)
    
    def _format_message(self, message: str, level: LogLevel, context: Optional[str] = None) -> str:
        """Format message with appropriate emoji and context."""
        emoji = self.emojis.get(level, "")
        
        if context:
            context_emoji = self.context_emojis.get(context.lower(), "")
            if context_emoji:
                emoji = context_emoji
        
        return f"{emoji} {message}" if emoji else message
    
    def debug(self, message: str, context: Optional[str] = None):
        """Log debug message."""
        if self._should_log(LogLevel.DEBUG):
            formatted_msg = self._format_message(message, LogLevel.DEBUG, context)
            print(formatted_msg)
    
    def info(self, message: str, context: Optional[str] = None):
        """Log info message."""
        if self._should_log(LogLevel.INFO):
            formatted_msg = self._format_message(message, LogLevel.INFO, context)
            print(formatted_msg)
    
    def warning(self, message: str, context: Optional[str] = None):
        """Log warning message."""
        if self._should_log(LogLevel.WARNING):
            formatted_msg = self._format_message(message, LogLevel.WARNING, context)
            print(formatted_msg)
    
    def error(self, message: str, context: Optional[str] = None, error: Optional[Exception] = None):
        """Log error message."""
        if self._should_log(LogLevel.ERROR):
            full_message = message
            if error:
                full_message += f": {str(error)}"
            formatted_msg = self._format_message(full_message, LogLevel.ERROR, context)
            print(formatted_msg)
    
    def success(self, message: str, context: Optional[str] = None):
        """Log success message."""
        if self._should_log(LogLevel.SUCCESS):
            formatted_msg = self._format_message(message, LogLevel.SUCCESS, context)
            print(formatted_msg)
    
    def progress(self, message: str, context: Optional[str] = None):
        """Log progress message."""
        if self._should_log(LogLevel.PROGRESS):
            formatted_msg = self._format_message(message, LogLevel.PROGRESS, context)
            print(formatted_msg)
    
    def section_header(self, title: str, width: int = 70, char: str = "="):
        """Print a section header."""
        if self._should_log(LogLevel.INFO):
            print(f"\n{title}")
            print(char * width)
    
    def subsection_header(self, title: str, width: int = 50, char: str = "-"):
        """Print a subsection header."""
        if self._should_log(LogLevel.INFO):
            print(f"\n{title}")
            print(char * width)
    
    def separator(self, width: int = 70, char: str = "-"):
        """Print a separator line."""
        if self._should_log(LogLevel.INFO):
            print(char * width)
    
    def blank_line(self):
        """Print a blank line."""
        if self._should_log(LogLevel.INFO):
            print("")
    
    def list_item(self, message: str, indent: int = 3):
        """Print a list item with proper indentation."""
        if self._should_log(LogLevel.INFO):
            print(" " * indent + message)
    
    def phase_start(self, phase_name: str, description: str = ""):
        """Log the start of a major phase."""
        if self._should_log(LogLevel.PROGRESS):
            emoji = "🚀"
            full_message = f"{emoji} Phase: {phase_name}"
            if description:
                full_message += f" - {description}"
            print(full_message)
    
    def phase_complete(self, phase_name: str, success: bool = True):
        """Log the completion of a major phase."""
        if self._should_log(LogLevel.PROGRESS):
            emoji = "✅" if success else "❌"
            status = "completed" if success else "failed"
            print(f"{emoji} Phase {phase_name} {status}")
    
    def tool_execution(self, tool_name: str, details: Optional[str] = None):
        """Log tool execution."""
        if self._should_log(LogLevel.DEBUG):
            message = f"Executing {tool_name}"
            if details:
                message += f" - {details}"
            self.debug(message, "tools")
    
    def agent_status(self, agent_name: str, status: str, details: Optional[str] = None):
        """Log agent status updates."""
        if self._should_log(LogLevel.INFO):
            message = f"{agent_name} {status}"
            if details:
                message += f" - {details}"
            self.info(message, "agent")
    
    def story_event(self, event_type: str, description: str):
        """Log story events."""
        if self._should_log(LogLevel.INFO):
            self.info(f"{event_type}: {description}", "story")
    
    def character_action(self, character_name: str, action: str):
        """Log character actions."""
        if self._should_log(LogLevel.INFO):
            self.info(f"{character_name}: {action}", "character")
    
    def metrics(self, metrics_dict: Dict[str, Any]):
        """Log metrics and statistics."""
        if self._should_log(LogLevel.INFO):
            self.info("Metrics:", "analysis")
            for key, value in metrics_dict.items():
                self.list_item(f"{key}: {value}")
    
    def set_level(self, level: LogLevel):
        """Change the logging level."""
        self.level = level
        self.info(f"Log level set to {level.value}")


# Global logger instance
_global_logger: Optional[MovieSimulatorLogger] = None


def get_logger(name: str = "MovieSimulator", level: LogLevel = LogLevel.INFO) -> MovieSimulatorLogger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        level: Log level
        
    Returns:
        MovieSimulatorLogger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = MovieSimulatorLogger(name, level)
    
    return _global_logger


def set_global_log_level(level: LogLevel):
    """Set the global log level."""
    logger = get_logger()
    logger.set_level(level)


# Convenience functions
def debug(message: str, context: Optional[str] = None):
    """Log debug message using global logger."""
    get_logger().debug(message, context)


def info(message: str, context: Optional[str] = None):
    """Log info message using global logger."""
    get_logger().info(message, context)


def warning(message: str, context: Optional[str] = None):
    """Log warning message using global logger."""
    get_logger().warning(message, context)


def error(message: str, context: Optional[str] = None, error: Optional[Exception] = None):
    """Log error message using global logger."""
    get_logger().error(message, context, error)


def success(message: str, context: Optional[str] = None):
    """Log success message using global logger."""
    get_logger().success(message, context)


def progress(message: str, context: Optional[str] = None):
    """Log progress message using global logger."""
    get_logger().progress(message, context) 