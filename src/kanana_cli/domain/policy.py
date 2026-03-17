BLOCKED_KEYWORDS = {
    "violence": ["bomb", "weapon", "stab", "kill"],
    "self_harm": ["self-harm", "suicide", "hurt myself"],
    "sexual_minors": ["minor sex", "sexual child", "nude child"],
    "illicit": ["buy drugs", "fake id", "steal exam"],
}


def educator_safe_categories():
    return tuple(BLOCKED_KEYWORDS.keys())
