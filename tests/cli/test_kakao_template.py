import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class KakaoTemplateCliTests(unittest.TestCase):
    def test_kakao_template_returns_template_only(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        proc = subprocess.run(
            [sys.executable, "-m", "kanana_cli.main", "kakao.template", "--topic", "science fair", "--no-save"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["result"]["delivery"]["send_supported"])


if __name__ == "__main__":
    unittest.main()
