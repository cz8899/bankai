# tests/test_monitor.py

import unittest
from unittest.mock import patch
import streamlit as st
from chatbot.utils import monitor_utils
from chatbot.monitor import logs

class TestMonitorUI(unittest.TestCase):

    @patch("chatbot.monitor.load_logs", return_value=[])
    def test_empty_logs_handling(self, mock_load_logs):
        logs = monitor_utils.load_interaction_log()
        self.assertEqual(len(logs), 0)

    def test_cost_summary_rendering(self):
        sample_logs = [
            {"mode": "Claude", "tokens": 1000, "cost": 0.008},
            {"mode": "Claude", "tokens": 500, "cost": 0.004},
            {"mode": "Agent", "tokens": 2000, "cost": 0.03},
        ]
        df = monitor_utils.summarize_costs(sample_logs)
        self.assertFalse(df.empty)
        self.assertIn("cost", df.columns)
        self.assertGreaterEqual(df["cost"].sum(), 0.01)

if __name__ == '__main__':
    unittest.main()
