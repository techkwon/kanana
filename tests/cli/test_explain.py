import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ExplainCliTests(unittest.TestCase):
    def test_explain_command_outputs_json(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["KANANA_USE_STUB_RUNTIME"] = "1"
        with tempfile.TemporaryDirectory() as temp_dir:
            env["KANANA_SESSION_DIR"] = temp_dir
            proc = subprocess.run(
                [sys.executable, "-m", "kanana_cli.main", "explain", "--topic", "fractions", "--learner-level", "elementary"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "explain")
            self.assertEqual(payload["result"]["learner_level"], "elementary")
            self.assertIn("structured", payload["result"])
            self.assertEqual(payload["result"]["structured"]["title"], "fractions")
            self.assertTrue(payload["result"]["content"].startswith("fractions\n\n개념 설명"))

    def test_stdin_learner_level_is_not_overridden_by_parser_defaults(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["KANANA_USE_STUB_RUNTIME"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", "kanana_cli.main", "explain", "--no-save"],
            cwd=ROOT,
            env=env,
            input=json.dumps({
                "input": {"topic": "photosynthesis"},
                "audience": {"learner_level": "middle"},
                "safety": {"mode": "standard", "block_on_unsafe": False},
            }),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"]["learner_level"], "middle")
        self.assertEqual(payload["result"]["safety"]["decision"], "allowed")
        self.assertFalse(payload["meta"]["session_id"])

    def test_explain_fallback_template_keeps_input_topic_when_raw_generation_is_stub_like(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["KANANA_USE_STUB_RUNTIME"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", "kanana_cli.main", "explain", "--topic", "photosynthesis", "--no-save"],
            cwd=ROOT,
            env=env,
            input=json.dumps({
                "input": {"topic": "photosynthesis"},
                "audience": {"learner_level": "middle"},
                "safety": {"mode": "standard", "block_on_unsafe": False},
            }),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"]["structured"]["title"], "photosynthesis")
        self.assertIn("photosynthesis", payload["result"]["content"])


if __name__ == "__main__":
    unittest.main()
