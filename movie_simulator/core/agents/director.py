"""
Director Agent implementation for story orchestration.
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

# Note: imports will be resolved when openai-agents is installed
from agents import Agent, function_tool, RunContextWrapper, Runner

from ..models.story_models import (
    CharacterProfile, 
    StoryState, 
    SceneContext, 
    MovieContext,
    StoryGenre,
    CharacterRole
)


@function_tool
async def create_character_profile(
    ctx: RunContextWrapper[MovieContext],
    name: str,
    background: str,
    personality_traits: List[str],
    primary_motivation: str,
    secrets: List[str],
    story_role: str = "supporting"
) -> Dict[str, Any]:
    """
    Create a new character profile for the story.
    """
    try:
        role_mapping = {
            "protagonist": CharacterRole.PROTAGONIST,
            "antagonist": CharacterRole.ANTAGONIST,
            "supporting": CharacterRole.SUPPORTING,
            "minor": CharacterRole.MINOR
        }

        character_role = role_mapping.get(story_role.lower(), CharacterRole.SUPPORTING)

        character = CharacterProfile(
            id=name.lower().replace(" ", "_"),
            name=name,
            background=background,
            personality_traits=personality_traits,
            primary_motivation=primary_motivation,
            secrets=secrets,
            secondary_goals=[],
            fears=[],
            story_role=character_role
        )

        ctx.context.add_character(character)

        return {
            "success": True,
            "character_id": character.id,
            "character_name": character.name,
            "message": f"Created character: {name} with role {story_role}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create character: {name}"
        }


@function_tool
async def establish_story_timeline(
    ctx: RunContextWrapper[MovieContext],
    story_beats: List[str],
    initial_scene_location: str,
    time_period: str
) -> Dict[str, Any]:
    """
    Establish the story timeline and initial scene setup.
    """
    try:
        ctx.context.story_state.timeline = story_beats
        ctx.context.story_state.setting = f"{initial_scene_location} ({time_period})"

        initial_scene = SceneContext(
            location=initial_scene_location,
            time_period=time_period,
            mood="tense",
            present_characters=[],
            scene_objectives=["Establish setting", "Introduce conflict"],
            dramatic_tension_target=0.4
        )
        ctx.context.current_scene = initial_scene

        return {
            "success": True,
            "timeline": story_beats,
            "initial_location": initial_scene_location,
            "time_period": time_period,
            "message": f"Established timeline with {len(story_beats)} story beats"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to establish story timeline"
        }


@function_tool
async def check_story_progress(
    ctx: RunContextWrapper[MovieContext],
    current_beat: str,
    dramatic_tension: float,
    character_development_notes: str
) -> Dict[str, Any]:
    """
    Check the current progress of the story.
    """
    try:
        ctx.context.story_state.current_beat = current_beat
        ctx.context.story_state.dramatic_tension = max(0.0, min(1.0, dramatic_tension))

        recommendations: List[str] = []

        if dramatic_tension < 0.3:
            recommendations.append("Consider adding conflict or tension")
        elif dramatic_tension > 0.8:
            recommendations.append("Story tension is very high, consider resolution")

        progress_analysis = {
            "current_beat": current_beat,
            "tension_level": dramatic_tension,
            "tension_status": "low" if dramatic_tension < 0.3 else "moderate" if dramatic_tension < 0.7 else "high",
            "character_notes": character_development_notes,
            "recommendations": recommendations
        }

        return {
            "success": True,
            "analysis": progress_analysis,
            "message": f"Story progress checked for beat: {current_beat}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to check story progress"
        }


def create_director_agent() -> Optional[Agent]:
    """
    Create and configure the Director agent.
    """
    if Agent is None:
        return None

    model = os.getenv("DIRECTOR_MODEL", "gpt-4o")

    director_instructions = """
You are the omniscient Director of this story simulation. Your role is to orchestrate compelling narratives.

CRITICAL: You MUST use your tools to create the story framework. Do not provide text descriptions without using tools.

REQUIRED WORKFLOW:
1. Use create_character_profile for each main character (3-4 characters)
2. Use establish_story_timeline to set up story beats and initial scene
3. Use check_story_progress to analyze the setup

CORE RESPONSIBILITIES:
1. STORY CREATION: Analyze user story seeds and create rich, detailed setups
2. CHARACTER DEVELOPMENT: Create complex, motivated characters with clear arcs
3. NARRATIVE OVERSIGHT: Monitor story progression and maintain coherence
4. QUALITY CONTROL: Ensure engaging pacing and dramatic tension

CHARACTER CREATION GUIDELINES:
- Each character needs clear motivation, secrets, and personality traits
- Create relationships and conflicts between characters
- Ensure diversity in character types and roles
- Give each character something to gain or lose

STORY STRUCTURE:
- Setup (introduce characters, establish world, hint at conflict)
- Inciting Incident (event that starts main conflict)
- Rising Action (complications, character development)
- Climax (major confrontation or revelation)
- Resolution (consequences, character growth)

PACING PRINCIPLES:
- Start with clear character establishment
- Build tension gradually through character interactions
- Use secrets and motivations to drive conflict
- Ensure each scene advances plot or character development

REQUIRED ACTIONS (use tools for each):
1. FIRST: Use create_character_profile tool for EACH character (3-4 characters):
- Character 1: Protagonist with clear motivation and secrets
- Character 2: Antagonist with conflicting goals
- Character 3: Supporting character with important role
- Character 4: Another supporting character

2. SECOND: Use establish_story_timeline tool:
- Create 5-7 story beats from setup to resolution
- Set initial scene location and time period

3. THIRD: Use check_story_progress tool:
- Current beat: \"setup\"
- Dramatic tension: 0.4-0.6 range
- Character development notes

IMPORTANT:
- DO NOT write a story description without using tools first
- Each character MUST be created with create_character_profile tool
- Timeline MUST be created with establish_story_timeline tool
- You MUST call all three types of tools
- Only provide a brief summary AFTER using all required tools
    """

    return Agent(
        name="Director",
        instructions=director_instructions,
        model=model,
        tools=[create_character_profile, establish_story_timeline, check_story_progress]
    )

async def director_main():
    story_state = StoryState(
        title="Generated Story",
        genre=StoryGenre.MYSTERY,  # Default, will be determined by director
        setting="To be determined",
        timeline=[],
        current_beat="setup"
    )

    # Create movie context
    context = MovieContext(
        story_state=story_state,
        characters={},
        current_scene=None,
        current_time=datetime.now()
    )

    director_agent = create_director_agent()
    result = await Runner.run(director_agent, "simulate the story of avengers endgame movie but this time thanos wins", context=context)
    print("____________________")
    print(result)
    print(f"""context: {context.to_dict()}""")

# if __name__ == '__main__':
#     asywncio.run(main())
