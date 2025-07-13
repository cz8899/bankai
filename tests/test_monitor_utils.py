# tests/test_monitor_utils.py

import unittest
import tempfile
import json
import os
from chatbot.utils import monitor_utils


class TestMonitorUtils(unittest.TestCase):

    def setUp(self):
        self.sample_logs = [
            {
                "timestamp": "2025-07-12 15:00:00",
                "prompt": "How to deploy in AWS?",
                "response": "Use CDK",
                "mode": "Claude",
                "type": "qa",
                "tokens": 100,
                "cost": 0.002,
                "source": "OpenSearch"
            },
            {
                "timestamp": "2025-07-12 15:01:00",
                "prompt": "Generate architecture",
                "response": "Here's your draw.io XML",
                "mode": "Agent",
                "type": "qa",
                "tokens": 250,
                "cost": 0.01,
                "source": "BedrockKB"
            }
        ]

    def test_summarize_costs(self):
        df = monitor_utils.summarize_costs(self.sample_logs)
        self.assertEqual(df.shape[0], 2)
        self.assertIn("cost", df.columns)

    def test_summarize_usage_by_mode(self):
        df = monitor_utils.summarize_usage_by_mode(self.sample_logs)
        self.assertEqual(df.shape[0], 2)
        self.assertIn("Total Cost ($)", df.columns)

    def test_extract_recent_questions(self):
        recent = monitor_utils.extract_recent_questions(self.sample_logs, limit=1)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["mode"], "Agent")

    def test_get_timestamp_format(self):
        timestamp = monitor_utils.get_timestamp()
        self.assertTrue("UTC" in timestamp)

    def test_missing_log_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["INTERACTIONS_LOG_PATH"] = os.path.join(tmp, "no_log.jsonl")
            logs = monitor_utils.load_interaction_log()
            self.assertEqual(logs, [])

if __name__ == "__main__":
    unittest.main()
