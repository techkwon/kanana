import unittest

from kanana_cli.contracts.errors import InputValidationError
from kanana_cli.contracts.requests import build_request_envelope


class ContractTests(unittest.TestCase):
    def test_builds_valid_defaults(self):
        envelope = build_request_envelope({"input": {"topic": "fractions"}})
        self.assertEqual(envelope.audience.learner_level, "elementary")
        self.assertEqual(envelope.output.format, "json")

    def test_invalid_level_raises(self):
        with self.assertRaises(InputValidationError):
            build_request_envelope({"input": {}, "audience": {"learner_level": "college"}})


if __name__ == "__main__":
    unittest.main()
