import sys
import unittest
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class TestSmokeScripts(unittest.TestCase):
    def test_smoke_budget_modes(self):
        env = os.environ.copy()
        env["AI_GATEWAY_BUDGET_MODE"] = "normal"
        env["PYTHONPATH"] = str(ROOT)
        result = subprocess.run([sys.executable, str(ROOT / "examples/smoke_budget_modes.py")], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Budget mode: normal", result.stdout)

    def test_smoke_budget_modes_economy(self):
        env = os.environ.copy()
        env["AI_GATEWAY_BUDGET_MODE"] = "economy"
        env["PYTHONPATH"] = str(ROOT)
        result = subprocess.run([sys.executable, str(ROOT / "examples/smoke_budget_modes.py")], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Budget mode: economy", result.stdout)
        self.assertIn("Reason: cheaper model preferred", result.stdout)

    def test_smoke_budget_modes_emergency(self):
        env = os.environ.copy()
        env["AI_GATEWAY_BUDGET_MODE"] = "emergency"
        env["PYTHONPATH"] = str(ROOT)
        result = subprocess.run([sys.executable, str(ROOT / "examples/smoke_budget_modes.py")], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Budget mode: emergency", result.stdout)
        self.assertIn("Reason: cheaper model preferred", result.stdout)
