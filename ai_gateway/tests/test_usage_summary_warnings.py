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
                    "request_id": f"req-{i}",
                    "status": "success",
                    "estimated_cost": 1.0 if i == 0 else 0.01,
                    "input_cost": 0.5 if i == 0 else 0.005,
                    "output_cost": 0.5 if i == 0 else 0.005,
                    "provider": "mock",
                    "model": "modelA" if i == 0 else "modelB",
                    "input_tokens": 1000 if i == 0 else 10,
                    "cached_input_tokens": 800 if i == 0 else 0,
                    "output_tokens": 10
                }) + "\n")
            
            # rate limit
            for i in range(5):
                f.write(json.dumps({
                    "request_id": f"req-err-{i}",
                    "status": "error",
                    "error_code": "provider_rate_limited",
                    "error_type": "RateLimitException",
                    "provider": "mock",
                    "model": "modelB",
                    "estimated_cost": 0.0
                }) + "\n")

            # output heavy
            f.write(json.dumps({
                "request_id": f"req-out",
                "status": "success",
                "estimated_cost": 0.1,
                "provider": "mock",
                "model": "modelB",
                "input_tokens": 10,
                "cached_input_tokens": 0,
                "output_tokens": 20000
            }) + "\n")

            tmp_path = f.name

        env = os.environ.copy()
        env["AI_GATEWAY_DAILY_BUDGET_USD"] = "1.0"
        env["PYTHONPATH"] = str(ROOT)

        # 1. Text output
        result = subprocess.run([sys.executable, str(ROOT / "ai_gateway/tools/usage_summary.py"), tmp_path], capture_output=True, text=True, env=env)
        
        # 2. JSON output
        result_json = subprocess.run([sys.executable, str(ROOT / "ai_gateway/tools/usage_summary.py"), tmp_path, "--json"], capture_output=True, text=True, env=env)

        os.remove(tmp_path)
        
        self.assertEqual(result.returncode, 0)
        
        # Check text output
        self.assertIn("Total Estimated Cost:", result.stdout)
        self.assertIn("Cache efficiency is high", result.stdout)
        self.assertIn("accounts for >70% of total cost", result.stdout)
        self.assertIn("high rate-limit frequency", result.stdout.lower())
        self.assertIn("Output tokens are unusually high", result.stdout)
        
        # Check json output
        self.assertEqual(result_json.returncode, 0)
        data = json.loads(result_json.stdout)
        self.assertEqual(data["total_requests"], 16)
        self.assertEqual(data["success_count"], 11)
        self.assertEqual(data["error_count"], 5)
        self.assertEqual(data["rate_limit_count"], 5)
        self.assertIn("cache_ratio", data["tokens"])
        self.assertGreater(data["tokens"]["cache_ratio"], 0.7)
        self.assertIn("warnings", data)
        self.assertIn("recommendations", data)

        warnings_str = " ".join(data["warnings"])
        self.assertIn(">70% of total cost", warnings_str)
        self.assertIn("rate-limit", warnings_str.lower())
        self.assertIn("Output tokens are unusually high", warnings_str)


    def test_bom_and_skip_errors(self):
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8-sig', delete=False) as f:
            f.write(json.dumps({
                "request_id": "r1",
                "status": "success",
                "estimated_cost": 0.001,
                "input_tokens": 1000,
                "cached_input_tokens": 700,
                "output_tokens": 200,
                "latency_ms": 1200
            }) + "\n")
            f.write(json.dumps({
                "request_id": "r2",
                "status": "success",
                "estimated_cost": 0.003,
                "input_tokens": 2000,
                "cached_input_tokens": 1000,
                "output_tokens": 500,
                "latency_ms": 1800
            }) + "\n")
            f.write("invalid json line\n")
            f.write(json.dumps({
                "request_id": "r3",
                "status": "error",
                "error_code": "provider_rate_limited",
                "estimated_cost": 0.0005,
                "input_tokens": 500,
                "cached_input_tokens": 0,
                "output_tokens": 100,
                "latency_ms": 900
            }) + "\n")
            tmp_path = f.name

        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)

        # 1. Text output
        result = subprocess.run([sys.executable, str(ROOT / "ai_gateway/tools/usage_summary.py"), tmp_path], capture_output=True, text=True, env=env)
        
        # 2. JSON output
        result_json = subprocess.run([sys.executable, str(ROOT / "ai_gateway/tools/usage_summary.py"), tmp_path, "--json"], capture_output=True, text=True, env=env)

        os.remove(tmp_path)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total Requests: 3", result.stdout)
        self.assertIn("Skipped 1 lines due to JSON parse errors", result.stdout)
        
        data = json.loads(result_json.stdout)
        self.assertEqual(data["total_requests"], 3)
        self.assertEqual(data["skipped_lines"], 1)
        self.assertEqual(data["success_count"], 2)
        self.assertEqual(data["error_count"], 1)
        self.assertEqual(data["tokens"]["total_input_tokens"], 3500)
        self.assertEqual(data["tokens"]["total_cached_input_tokens"], 1700)
        self.assertEqual(data["tokens"]["total_output_tokens"], 800)
        self.assertAlmostEqual(data["costs"]["total_estimated_cost"], 0.0045)
