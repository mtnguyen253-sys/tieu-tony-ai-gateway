import sys
import json
import argparse
import os
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Usage Ledger Summary Utility")
    parser.add_argument("logfile", help="Path to usage.jsonl file", nargs="?", default="logs/usage.jsonl")
    args = parser.parse_args()
    
    total_requests = 0
    success_count = 0
    error_count = 0
    rate_limit_count = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    total_latency = 0.0
    latency_count = 0
    
    cost_by_model = defaultdict(float)
    error_by_model = defaultdict(int)
    
    try:
        with open(args.logfile, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                total_requests += 1
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                    
                status = event.get("status")
                if status == "success":
                    success_count += 1
                elif status == "error":
                    error_count += 1
                    
                if event.get("error_code") == "provider_rate_limited":
                    rate_limit_count += 1
                    
                in_tok = event.get("input_tokens") or 0
                out_tok = event.get("output_tokens") or 0
                cost = event.get("estimated_cost") or 0.0
                latency = event.get("latency_ms")
                
                total_input_tokens += in_tok
                total_output_tokens += out_tok
                total_cost += cost
                
                if latency is not None:
                    total_latency += latency
                    latency_count += 1
                    
                provider = event.get("provider") or "unknown"
                model = event.get("resolved_model") or event.get("model") or "unknown"
                key = f"{provider}:{model}"
                
                cost_by_model[key] += cost
                if status == "error":
                    error_by_model[key] += 1
    except FileNotFoundError:
        print(f"File not found: {args.logfile}")
        sys.exit(1)

    print("--- Usage Summary ---")
    print(f"Total Requests: {total_requests}")
    print(f"Success Count: {success_count}")
    print(f"Error Count: {error_count}")
    print(f"Rate Limit Count: {rate_limit_count}")
    print(f"Total Input Tokens: {total_input_tokens}")
    print(f"Total Output Tokens: {total_output_tokens}")
    print(f"Total Estimated Cost: ${total_cost:.6f}")
    if latency_count > 0:
        print(f"Average Latency: {total_latency/latency_count:.2f} ms")
    else:
        print("Average Latency: N/A")
        
    print("\n--- Cost by Provider/Model ---")
    for k, v in sorted(cost_by_model.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: ${v:.6f}")
        
    print("\n--- Error Count by Provider/Model ---")
    for k, v in sorted(error_by_model.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: {v}")
        
    print("\n--- Insights & Recommendations ---")
    
    daily_budget = float(os.getenv("AI_GATEWAY_DAILY_BUDGET_USD", "0"))
    if daily_budget > 0 and total_cost > daily_budget * 0.8:
        print(f"[WARNING] Total cost (${total_cost:.6f}) exceeds 80% of daily budget (${daily_budget:.6f}).")

    for k, v in cost_by_model.items():
        if total_cost > 0 and v / total_cost > 0.7:
            print(f"[WARNING] Provider/Model {k} accounts for >70% of total cost ({v:.6f}/{total_cost:.6f}).")

    if total_cost > 10.0:
        print("[WARNING] Total cost exceeds $10.0. Consider budget alerts.")
    if error_count > 0 and error_count / max(1, total_requests) > 0.3:
        print("[WARNING] Error rate > 30%. Check failing providers.")
    if rate_limit_count > 0 and rate_limit_count / max(1, total_requests) > 0.1:
        print("[WARNING] High rate limit frequency. Consider increasing cooldown or load balancing.")
    if total_requests > 0 and (total_input_tokens == 0 and total_output_tokens == 0):
        print("[RECOMMENDATION] Many requests have 0 tokens. Ensure adapter usage extraction is implemented.")

if __name__ == "__main__":
    main()
