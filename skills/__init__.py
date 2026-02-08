"""
OpenCngsm v3.0 - Skills Package
Native Python implementations of MCP functionality
"""
from typing import Dict, Type, Any

# Skill registry
SKILLS: Dict[str, Type] = {}


def register_skill(name: str, skill_class: Type, description: str):
    """Register a skill in the global registry"""
    SKILLS[name] = {
        'class': skill_class,
        'description': description
    }


def get_skill(name: str) -> Type:
    """Get skill class by name"""
    if name not in SKILLS:
        raise ValueError(f"Skill '{name}' not found")
    return SKILLS[name]['class']


def list_skills() -> Dict[str, str]:
    """List all available skills"""
    return {name: info['description'] for name, info in SKILLS.items()}
