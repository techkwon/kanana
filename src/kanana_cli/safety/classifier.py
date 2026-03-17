from typing import Dict, Optional

from kanana_cli.domain.policy import BLOCKED_KEYWORDS


def classify_text(text: str) -> Dict[str, Optional[str]]:
    lowered = (text or "").lower()
    for category, phrases in BLOCKED_KEYWORDS.items():
        for phrase in phrases:
            if phrase in lowered:
                return {"unsafe": True, "category": category, "matched": phrase}
    return {"unsafe": False, "category": None, "matched": None}
