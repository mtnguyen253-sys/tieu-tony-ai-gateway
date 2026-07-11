import sys
import unittest
import os
import subprocess
import tempfile
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class TestUsageSummary(unittest.TestCase):
    def test_usage_summary_warnings(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for i in range(10):
                f.write(json.dumps({
                    "status": "success",
                    "estimated_cost": 1.0 if i == 0 else 0.01,
                    "provider": "mock",
                    "model": "modelA" if i == 0 else "modelB",
                    "input_tokens": 10,
                    "output_tokens": 10
                }) + "\n")
            
            # rate limit
            for i in range(5):
                f.write(json.dumps({
                    "status": "error",
                    "error_code": "provider_rate_limited",
                    "provider": "mock",
                    "model": "modelB",
                    "estimated_cost": 0.0
                }) + "\n")
            tmp_path = f.name

        env = os.environ.copy()
        env["AI_GATEWAY_DAILY_BUDGET_USD"] = "1.0"
        env["PYTHONPATH"] = str(ROOT)
        result = subprocess.run([sys.executable, str(ROOT / "ai_gateway/tools/usage_summary.py"), tmp_path], capture_output=True, text=True, env=env)
        
        os.remove(tmp_path)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total cost", result.stdout)
        self.assertIn("exceeds 80% of daily budget", result.stdout)
        self.assertIn("accounts for >70% of total cost", result.stdout)
        self.assertIn("High rate limit frequency", result.stdout)

