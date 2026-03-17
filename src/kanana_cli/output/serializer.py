import json
import sys
from typing import Any, Dict


def emit_json(payload: Dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
