import os
import unittest

from kanana_cli.runtime.healthcheck import run_healthcheck
from kanana_cli.runtime.ollama_client import OllamaClient


class OllamaRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.previous = os.environ.get("KANANA_USE_STUB_RUNTIME")
        os.environ["KANANA_USE_STUB_RUNTIME"] = "1"

    def tearDown(self):
        if self.previous is None:
            os.environ.pop("KANANA_USE_STUB_RUNTIME", None)
        else:
            os.environ["KANANA_USE_STUB_RUNTIME"] = self.previous

    def test_stub_generate(self):
        client = OllamaClient()
        self.assertIn("fractions", client.generate("teach fractions", "kanana-nano"))

    def test_healthcheck_ready_with_stub(self):
        result = run_healthcheck()
        self.assertTrue(result["ready"])

    def test_healthcheck_treats_latest_suffix_as_present(self):
        previous = os.environ.get("KANANA_MODEL")
        os.environ["KANANA_MODEL"] = "neoali/kanana-1.5-2.1b-instruct-2505"
        try:
            result = run_healthcheck()
        finally:
            if previous is None:
                os.environ.pop("KANANA_MODEL", None)
            else:
                os.environ["KANANA_MODEL"] = previous
        self.assertTrue(result["model_present"])


if __name__ == "__main__":
    unittest.main()
