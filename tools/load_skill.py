def load_skill_definition(skills: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Load the full instructions for one of the available skills.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "enum": list(skills),
                        "description": "Skill to load.",
                    }
                },
                "required": ["name"],
            },
        },
    }


def load_skill(runtime, name: str) -> str:
    skill = runtime.skills.get(name)
    if skill is None:  # enum should prevent this; small models ignore enums
        available = ", ".join(sorted(runtime.skills)) or "(none)"
        return f"ERROR: no skill named {name!r}. Available: {available}."
    return skill["body"]
