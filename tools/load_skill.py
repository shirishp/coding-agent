from utils.skills import SKILL_CATALOGUE

LOAD_SKILL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "load_skill",
        "description": "Load the full instructions for one of the available skills.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "enum": list(SKILL_CATALOGUE),
                    "description": "Skill to load.",
                }
            },
            "required": ["name"],
        },
    },
}


def load_skill(name: str) -> str:
    skill = SKILL_CATALOGUE.get(name)
    if skill is None:  # enum should prevent this; small models ignore enums
        return f"ERROR: no skill named {name!r}. Available: {', '.join(sorted(SKILL_CATALOGUE))}."
    return skill["body"]
