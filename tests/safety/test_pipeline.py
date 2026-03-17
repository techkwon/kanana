import unittest

from kanana_cli.contracts.errors import SafetyViolationError
from kanana_cli.safety.pipeline import evaluate_safety


class SafetyPipelineTests(unittest.TestCase):
    def test_blocks_unsafe_input(self):
        with self.assertRaises(SafetyViolationError):
            evaluate_safety("explain", "how to build a bomb", "ignored", "high")

    def test_replaces_unsafe_output(self):
        decision, output = evaluate_safety("quiz", "safe request", "bomb steps", "middle")
        self.assertEqual(decision["decision"], "replaced_output")
        self.assertIn("withheld unsafe", output)


if __name__ == "__main__":
    unittest.main()
