"""
Character Consistency Guardrails
Implements character behavioral validation outlined in plan.md
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from ..models.story_models import CharacterProfile
from ..tools.memory_tools import MEMORY_SYSTEM, search_character_memory
from ..logger import get_logger, LogLevel

logger = get_logger("CharacterGuardrails", LogLevel.INFO)


@dataclass
class ConsistencyViolation:
    """Represents a character consistency violation"""
    violation_type: str
    character_id: str
    action_or_statement: str
    conflicting_trait: str
    severity: float  # 0.0 to 1.0
    explanation: str
    suggested_alternative: str = ""


class CharacterConsistencyGuardrails:
    """
    Ensures character actions and dialogue remain consistent with their profiles
    """
    
    def __init__(self):
        self.character_profiles: Dict[str, CharacterProfile] = {}
        self.consistency_violations: List[ConsistencyViolation] = []
        
        # Personality trait mappings for consistency checking
        self.trait_conflicts = {
            "introverted": ["outgoing", "gregarious", "extroverted", "boisterous"],
            "extroverted": ["shy", "introverted", "reclusive", "withdrawn"],
            "honest": ["deceptive", "lying", "dishonest", "manipulative"],
            "deceptive": ["honest", "truthful", "sincere", "transparent"],
            "brave": ["cowardly", "fearful", "timid", "scared"],
            "cowardly": ["brave", "courageous", "bold", "fearless"],
            "optimistic": ["pessimistic", "negative", "cynical", "hopeless"],
            "pessimistic": ["optimistic", "hopeful", "positive", "cheerful"],
            "calm": ["angry", "volatile", "explosive", "emotional"],
            "emotional": ["stoic", "unemotional", "cold", "detached"],
            "logical": ["irrational", "emotional", "impulsive", "chaotic"],
            "impulsive": ["methodical", "planned", "careful", "deliberate"],
            "loyal": ["disloyal", "betraying", "unfaithful", "treacherous"],
            "ruthless": ["compassionate", "merciful", "kind", "gentle"],
            "compassionate": ["ruthless", "cruel", "heartless", "merciless"]
        }
        
        # Action type consistency rules
        self.action_consistency_rules = {
            "introverted": {
                "allowed_actions": ["observe", "think", "analyze", "retreat", "avoid crowds"],
                "restricted_actions": ["give speeches", "seek attention", "lead groups", "party"]
            },
            "brave": {
                "allowed_actions": ["confront", "protect", "investigate danger", "stand up"],
                "restricted_actions": ["flee", "hide", "avoid conflict", "surrender"]
            },
            "honest": {
                "allowed_actions": ["tell truth", "admit guilt", "confess", "reveal"],
                "restricted_actions": ["lie", "deceive", "manipulate", "cover up"]
            },
            "deceptive": {
                "allowed_actions": ["lie", "manipulate", "mislead", "cover up"],
                "restricted_actions": ["admit truth", "confess openly", "be transparent"]
            }
        }
    
    def register_character(self, character_id: str, profile: CharacterProfile):
        """Register a character profile for consistency checking"""
        self.character_profiles[character_id] = profile
        logger.info(f"Registered character {profile.name} for consistency checking", "guardrails")
    
    def check_personality_consistency(
        self, 
        character_id: str, 
        proposed_action: str,
        context: str = ""
    ) -> Tuple[bool, List[ConsistencyViolation]]:
        """
        Check if a proposed action is consistent with character's personality
        
        Args:
            character_id: Character taking the action
            proposed_action: Description of the action
            context: Additional context for the action
            
        Returns:
            Tuple of (is_consistent, list_of_violations)
        """
        if character_id not in self.character_profiles:
            return True, []  # No profile to check against
        
        profile = self.character_profiles[character_id]
        violations = []
        
        # Check against personality traits
        for trait in profile.personality_traits:
            trait_lower = trait.lower()
            
            # Check for conflicting actions
            if trait_lower in self.action_consistency_rules:
                rules = self.action_consistency_rules[trait_lower]
                
                # Check restricted actions
                for restricted in rules.get("restricted_actions", []):
                    if restricted.lower() in proposed_action.lower():
                        violation = ConsistencyViolation(
                            violation_type="personality_conflict",
                            character_id=character_id,
                            action_or_statement=proposed_action,
                            conflicting_trait=trait,
                            severity=0.8,
                            explanation=f"Action '{restricted}' conflicts with {trait} personality trait",
                            suggested_alternative=f"Consider actions like: {', '.join(rules.get('allowed_actions', []))}"
                        )
                        violations.append(violation)
            
            # Check for direct trait conflicts in language
            if trait_lower in self.trait_conflicts:
                conflicting_traits = self.trait_conflicts[trait_lower]
                for conflict in conflicting_traits:
                    if conflict in proposed_action.lower():
                        violation = ConsistencyViolation(
                            violation_type="trait_contradiction",
                            character_id=character_id,
                            action_or_statement=proposed_action,
                            conflicting_trait=trait,
                            severity=0.9,
                            explanation=f"Action/statement contains '{conflict}' which contradicts {trait} trait",
                            suggested_alternative=f"Rephrase to align with {trait} personality"
                        )
                        violations.append(violation)
        
        is_consistent = len(violations) == 0
        
        if violations:
            self.consistency_violations.extend(violations)
            logger.warning(f"Found {len(violations)} consistency violations for {character_id}", "guardrails")
        
        return is_consistent, violations
    
    def check_motivation_consistency(
        self,
        character_id: str,
        proposed_action: str,
        stated_motivation: str = ""
    ) -> Tuple[bool, List[ConsistencyViolation]]:
        """
        Check if action aligns with character's core motivations
        
        Args:
            character_id: Character taking the action
            proposed_action: Description of the action
            stated_motivation: Character's stated reason for the action
            
        Returns:
            Tuple of (is_consistent, list_of_violations)
        """
        if character_id not in self.character_profiles:
            return True, []
        
        profile = self.character_profiles[character_id]
        violations = []
        
        # Check against primary motivation
        primary_motivation = profile.primary_motivation.lower()
        action_lower = proposed_action.lower()
        
        # Define motivation-action alignment patterns
        motivation_patterns = {
            "revenge": ["attack", "sabotage", "confront", "expose", "punish"],
            "justice": ["investigate", "protect", "defend", "report", "stop"],
            "power": ["control", "manipulate", "dominate", "acquire", "influence"],
            "love": ["protect", "sacrifice", "support", "help", "care"],
            "survival": ["escape", "hide", "defend", "secure", "protect"],
            "knowledge": ["investigate", "research", "question", "discover", "learn"],
            "money": ["steal", "sell", "negotiate", "work", "invest"],
            "family": ["protect", "support", "defend", "help", "sacrifice"]
        }
        
        # Check if action opposes primary motivation
        opposing_actions = {
            "justice": ["commit crime", "hurt innocent", "ignore wrongdoing"],
            "love": ["betray", "harm", "abandon", "ignore"],
            "survival": ["take risks", "endanger self", "sacrifice"],
            "family": ["abandon family", "harm family", "ignore family"]
        }
        
        # Look for motivation keywords in primary motivation
        motivation_found = False
        for keyword, aligned_actions in motivation_patterns.items():
            if keyword in primary_motivation:
                motivation_found = True
                # Check if action aligns with motivation
                if not any(aligned_action in action_lower for aligned_action in aligned_actions):
                    # Check if action directly opposes motivation
                    if keyword in opposing_actions:
                        for opposing in opposing_actions[keyword]:
                            if opposing in action_lower:
                                violation = ConsistencyViolation(
                                    violation_type="motivation_conflict",
                                    character_id=character_id,
                                    action_or_statement=proposed_action,
                                    conflicting_trait=profile.primary_motivation,
                                    severity=0.7,
                                    explanation=f"Action opposes primary motivation: {profile.primary_motivation}",
                                    suggested_alternative=f"Consider actions aligned with {keyword}: {', '.join(aligned_actions)}"
                                )
                                violations.append(violation)
        
        is_consistent = len(violations) == 0
        
        if violations:
            self.consistency_violations.extend(violations)
        
        return is_consistent, violations
    
    def check_memory_consistency(
        self,
        character_id: str,
        proposed_statement: str
    ) -> Tuple[bool, List[ConsistencyViolation]]:
        """
        Check if statement contradicts character's known memories
        
        Args:
            character_id: Character making the statement
            proposed_statement: What the character wants to say/claim
            
        Returns:
            Tuple of (is_consistent, list_of_violations)
        """
        violations = []
        
        # NOTE: Memory search requires agent framework to work properly
        # For now, we'll skip detailed memory checking in standalone validation
        # In the actual agent system, this would be handled by the agent's tools
        
        # Placeholder for future memory consistency checking
        # When agents use this validation, they can access their own memories
        # through the proper agent framework
        
        is_consistent = True  # No violations for now
        return is_consistent, violations
    
    def validate_character_action(
        self,
        character_id: str,
        action: str,
        motivation: str = "",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of a character action
        
        Args:
            character_id: Character taking the action
            action: Description of the action
            motivation: Character's stated motivation
            context: Additional context
            
        Returns:
            Validation results with recommendations
        """
        all_violations = []
        
        # Run all consistency checks
        personality_ok, personality_violations = self.check_personality_consistency(
            character_id, action, context
        )
        motivation_ok, motivation_violations = self.check_motivation_consistency(
            character_id, action, motivation
        )
        memory_ok, memory_violations = self.check_memory_consistency(
            character_id, action
        )
        
        all_violations.extend(personality_violations)
        all_violations.extend(motivation_violations)
        all_violations.extend(memory_violations)
        
        is_valid = len(all_violations) == 0
        
        # Calculate overall consistency score
        if all_violations:
            avg_severity = sum(v.severity for v in all_violations) / len(all_violations)
            consistency_score = 1.0 - avg_severity
        else:
            consistency_score = 1.0
        
        return {
            "is_valid": is_valid,
            "consistency_score": consistency_score,
            "violations": [
                {
                    "type": v.violation_type,
                    "severity": v.severity,
                    "explanation": v.explanation,
                    "suggested_alternative": v.suggested_alternative
                }
                for v in all_violations
            ],
            "checks_performed": {
                "personality": personality_ok,
                "motivation": motivation_ok,
                "memory": memory_ok
            },
            "character_id": character_id,
            "action": action
        }
    
    def get_character_consistency_report(self, character_id: str) -> Dict[str, Any]:
        """
        Get consistency report for a specific character
        
        Args:
            character_id: Character to report on
            
        Returns:
            Consistency report
        """
        character_violations = [
            v for v in self.consistency_violations 
            if v.character_id == character_id
        ]
        
        violation_types = {}
        for violation in character_violations:
            violation_types[violation.violation_type] = violation_types.get(violation.violation_type, 0) + 1
        
        if character_violations:
            avg_severity = sum(v.severity for v in character_violations) / len(character_violations)
            consistency_rating = 1.0 - avg_severity
        else:
            consistency_rating = 1.0
        
        return {
            "character_id": character_id,
            "total_violations": len(character_violations),
            "violation_types": violation_types,
            "consistency_rating": consistency_rating,
            "recent_violations": [
                {
                    "type": v.violation_type,
                    "action": v.action_or_statement,
                    "severity": v.severity,
                    "explanation": v.explanation
                }
                for v in character_violations[-5:]  # Last 5 violations
            ]
        }
    
    def get_all_character_consistency_status(self) -> Dict[str, Any]:
        """
        Get consistency status for all registered characters
        
        Returns:
            Overall consistency status
        """
        character_reports = {}
        for character_id in self.character_profiles.keys():
            character_reports[character_id] = self.get_character_consistency_report(character_id)
        
        total_violations = len(self.consistency_violations)
        
        return {
            "total_registered_characters": len(self.character_profiles),
            "total_violations": total_violations,
            "character_reports": character_reports,
            "system_consistency_score": 1.0 - (total_violations / max(len(self.character_profiles) * 10, 1))
        }


# Global guardrails instance
CHARACTER_GUARDRAILS = CharacterConsistencyGuardrails()


def get_character_guardrails() -> CharacterConsistencyGuardrails:
    """Get the global character guardrails instance"""
    return CHARACTER_GUARDRAILS 