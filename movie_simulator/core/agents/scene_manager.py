"""
Scene Manager Agent for coordinating character interactions and scene flow
Implements the scene management system outlined in plan.md Phase 4
"""

from typing import Dict, List, Any, Optional
from ..models.story_models import SceneContext, CharacterProfile
from ..tools.scene_tools import (
    start_new_scene, transition_scene, manage_turn_taking,
    coordinate_character_dialogue, check_scene_objectives,
    update_scene_context, end_current_scene, get_scene_management_status
)
from ..logger import get_logger, LogLevel

logger = get_logger("SceneManager", LogLevel.INFO)


class SceneManagerAgent:
    """
    Scene Manager agent for coordinating story scenes.
    Handles scene coordination, character management, and turn taking.
    """
    
    def __init__(self):
        self.name = "Scene Manager"
        self.current_scene: Optional[SceneContext] = None
        self.scene_history: List[SceneContext] = []
        self.character_agents: Dict[str, Any] = {}
        self.turn_order: List[str] = []
        self.current_turn_index: int = 0
        
        # Available scene management tools
        self.tools = [
            start_new_scene,
            transition_scene,
            manage_turn_taking,
            coordinate_character_dialogue,
            check_scene_objectives,
            update_scene_context,
            end_current_scene,
            get_scene_management_status
        ]
        
        logger.info("Scene Manager Agent initialized with scene coordination tools", "scene_manager")
    
    def set_character_agents(self, character_agents: Dict[str, Any]):
        """Set the character agents for scene management"""
        self.character_agents = character_agents
        logger.info(f"Scene manager coordinating {len(character_agents)} characters", "agent")
    
    def start_new_scene_workflow(self, scene_context: SceneContext) -> Dict[str, Any]:
        """Start a new scene with comprehensive setup"""
        
        scene_id = f"scene_{len(self.scene_history) + 1}_{scene_context.location.lower().replace(' ', '_')}"
        
        # Start the scene using the tool
        result = start_new_scene(
            scene_id=scene_id,
            location=scene_context.location,
            mood=scene_context.mood,
            present_characters=scene_context.present_characters,
            scene_objectives=scene_context.scene_objectives,
            dramatic_tension_target=scene_context.dramatic_tension_target,
            time_period=scene_context.time_period
        )
        
        if result["success"]:
            self.current_scene = scene_context
            self.turn_order = scene_context.present_characters.copy()
            self.current_turn_index = 0
            
            logger.info(f"Started new scene: {scene_context.location}", "workflow")
            logger.info(f"Present characters: {scene_context.present_characters}", "workflow")
        
        return result
    
    def manage_character_turns(self) -> Dict[str, Any]:
        """Manage character turn taking in the current scene"""
        
        if not self.current_scene or not self.turn_order:
            return {
                "success": False,
                "error": "No active scene or character turn order"
            }
        
        # Get next character in turn order
        if self.current_turn_index >= len(self.turn_order):
            self.current_turn_index = 0  # Reset to beginning
        
        next_character = self.turn_order[self.current_turn_index]
        self.current_turn_index += 1
        
        # Use the turn management tool
        scene_id = f"scene_{len(self.scene_history) + 1}_{self.current_scene.location.lower().replace(' ', '_')}"
        
        result = manage_turn_taking(
            scene_id=scene_id,
            next_character=next_character,
            interaction_type="dialogue"
        )
        
        logger.info(f"Turn managed: {next_character} is now active", "workflow")
        
        return result
    
    def coordinate_dialogue(self, speaking_character: str, target_character: Optional[str] = None) -> Dict[str, Any]:
        """Coordinate dialogue between characters"""
        
        if not self.current_scene:
            return {
                "success": False,
                "error": "No active scene for dialogue coordination"
            }
        
        scene_id = f"scene_{len(self.scene_history) + 1}_{self.current_scene.location.lower().replace(' ', '_')}"
        
        result = coordinate_character_dialogue(
            scene_id=scene_id,
            speaking_character=speaking_character,
            target_character=target_character
        )
        
        logger.info(f"Dialogue coordinated: {speaking_character} -> {target_character or 'everyone'}", "workflow")
        
        return result
    
    def check_scene_progress(self) -> Dict[str, Any]:
        """Check progress on current scene objectives"""
        
        if not self.current_scene:
            return {
                "success": False,
                "error": "No active scene to check"
            }
        
        scene_id = f"scene_{len(self.scene_history) + 1}_{self.current_scene.location.lower().replace(' ', '_')}"
        
        result = check_scene_objectives(scene_id)
        
        logger.info(f"Scene progress: {result.get('total_progress', 0)*100:.1f}% complete", "workflow")
        
        return result
    
    def transition_to_new_scene(self, new_scene_context: SceneContext, characters_to_carry: Optional[List[str]] = None) -> Dict[str, Any]:
        """Transition from current scene to a new scene"""
        
        if not self.current_scene:
            return {
                "success": False,
                "error": "No current scene to transition from"
            }
        
        # Archive current scene
        self.scene_history.append(self.current_scene)
        
        # Create new scene
        new_scene_result = self.start_new_scene_workflow(new_scene_context)
        
        if new_scene_result["success"]:
            logger.info(f"Scene transition completed: {self.current_scene.location} -> {new_scene_context.location}", "workflow")
        
        return new_scene_result
    
    def end_current_scene_workflow(self, reason: str = "Objectives completed") -> Dict[str, Any]:
        """End the current scene"""
        
        if not self.current_scene:
            return {
                "success": False,
                "error": "No active scene to end"
            }
        
        scene_id = f"scene_{len(self.scene_history) + 1}_{self.current_scene.location.lower().replace(' ', '_')}"
        
        result = end_current_scene(
            scene_id=scene_id,
            reason=reason,
            completion_status="complete"
        )
        
        if result["success"]:
            # Archive the scene
            self.scene_history.append(self.current_scene)
            self.current_scene = None
            self.turn_order = []
            self.current_turn_index = 0
            
            logger.info(f"Scene ended: {reason}", "workflow")
        
        return result
    
    def get_scene_status(self) -> Dict[str, Any]:
        """Get comprehensive scene status"""
        
        status = get_scene_management_status()
        
        # Add agent-specific information
        status.update({
            "agent_status": {
                "current_scene_context": {
                    "location": self.current_scene.location if self.current_scene else None,
                    "mood": self.current_scene.mood if self.current_scene else None,
                    "present_characters": self.current_scene.present_characters if self.current_scene else [],
                    "objectives": self.current_scene.scene_objectives if self.current_scene else []
                },
                "turn_management": {
                    "turn_order": self.turn_order,
                    "current_turn_index": self.current_turn_index,
                    "next_character": self.turn_order[self.current_turn_index] if self.current_turn_index < len(self.turn_order) else None
                },
                "scene_history_count": len(self.scene_history),
                "coordinating_characters": len(self.character_agents)
            }
        })
        
        return status


class SceneManagerCoordinator:
    """Manages scene flow and character interactions"""
    
    def __init__(self):
        self.scene_manager_agent = SceneManagerAgent()
        self.character_agents: Dict[str, Any] = {}
        
    def set_character_agents(self, character_agents: Dict[str, Any]):
        """Set the character agents for scene management"""
        self.character_agents = character_agents
        self.scene_manager_agent.set_character_agents(character_agents)
        
        logger.info(f"Scene coordinator managing {len(character_agents)} characters", "coordinator")
    
    def run_scene_sequence(self, scenes: List[SceneContext]) -> List[Dict[str, Any]]:
        """Run a sequence of scenes with automatic transitions"""
        
        scene_results = []
        
        for i, scene_context in enumerate(scenes):
            logger.info(f"Starting scene {i+1}/{len(scenes)}: {scene_context.location}", "sequence")
            
            # Start the scene
            scene_result = self.scene_manager_agent.start_new_scene_workflow(scene_context)
            
            if scene_result["success"]:
                # Simulate some character interactions
                for turn in range(min(3, len(scene_context.present_characters))):
                    turn_result = self.scene_manager_agent.manage_character_turns()
                    if turn_result["success"]:
                        logger.info(f"Turn {turn + 1}: {turn_result['current_speaker']}", "sequence")
                
                # Check scene progress
                progress_result = self.scene_manager_agent.check_scene_progress()
                
                # End the scene
                end_result = self.scene_manager_agent.end_current_scene_workflow(
                    reason=f"Scene {i+1} objectives completed"
                )
                
                scene_results.append({
                    "scene_number": i + 1,
                    "start_result": scene_result,
                    "progress_result": progress_result,
                    "end_result": end_result
                })
            else:
                logger.error(f"Failed to start scene {i+1}: {scene_result.get('error')}", "sequence")
                scene_results.append({
                    "scene_number": i + 1,
                    "error": scene_result.get("error")
                })
        
        logger.success(f"Scene sequence completed: {len(scene_results)} scenes processed", "sequence")
        
        return scene_results
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get comprehensive coordinator status"""
        
        return {
            "coordinator_info": {
                "total_character_agents": len(self.character_agents),
                "character_ids": list(self.character_agents.keys())
            },
            "scene_manager_status": self.scene_manager_agent.get_scene_status()
        }


# Global scene coordinator instance
SCENE_COORDINATOR = SceneManagerCoordinator()


def get_scene_coordinator() -> SceneManagerCoordinator:
    """Get the global scene coordinator instance"""
    return SCENE_COORDINATOR


def create_scene_manager_agent() -> SceneManagerAgent:
    """Create a new Scene Manager agent"""
    return SceneManagerAgent()
