def safe_fallback(command: str, learner_level: str) -> str:
    return (
        f"Kanana withheld unsafe {command} content for a {learner_level} learner. "
        "Provide a safer educational goal or ask for age-appropriate guidance instead."
    )
