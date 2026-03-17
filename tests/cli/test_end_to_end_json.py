import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class EndToEndJsonTests(unittest.TestCase):
    def test_health_explain_and_safety_are_json(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["KANANA_USE_STUB_RUNTIME"] = "1"
        commands = [
            [sys.executable, "-m", "kanana_cli.main", "health"],
            [sys.executable, "-m", "kanana_cli.main", "explain", "--topic", "fractions", "--no-save"],
            [sys.executable, "-m", "kanana_cli.main", "safety.check", "--topic", "fractions", "--no-save"],
        ]
        for command in commands:
            proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["schema_version"], "1.0")
            self.assertIn("ok", payload)
            self.assertIn("command", payload)


if __name__ == "__main__":
    unittest.main()
