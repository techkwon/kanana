import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class SessionLoggingCliTests(unittest.TestCase):
    def test_explain_writes_session_file_and_redacts_secrets(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["EDUFLOW_USE_STUB_RUNTIME"] = "1"
        with tempfile.TemporaryDirectory() as temp_dir:
            env["EDUFLOW_SESSION_DIR"] = temp_dir
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "eduflow_cli.main",
                    "explain",
                    "--session-id",
                    "abc123",
                    "--input-json",
                    '{"input":{"topic":"fractions","api_key":"top-secret"},"safety":{"authorization":"Bearer secret"}}',
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            session_file = Path(temp_dir) / "abc123.json"
            self.assertTrue(session_file.exists())
            record = json.loads(session_file.read_text(encoding="utf-8"))
            self.assertEqual(record["session_id"], "abc123")
            self.assertEqual(record["request"]["input"]["api_key"], "***REDACTED***")
            self.assertEqual(record["response"]["input"]["api_key"], "***REDACTED***")
            self.assertEqual(record["request"]["safety"]["mode"], "strict")
            self.assertTrue(record["safety"]["checked_input"]["unsafe"] is False)


if __name__ == "__main__":
    unittest.main()
