import os
import argparse
import json
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Usage Ledger Summary Utility")
    parser.add_argument("logfile", help="Path to usage.jsonl file", nargs="?", default="logs/usage.jsonl")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    total_requests = 0
    skipped_lines = 0
    success_count = 0
    error_count = 0
    rate_limit_count = 0
    
    total_input_tokens = 0
    total_cached_input_tokens = 0
    total_output_tokens = 0
    total_tokens_all = 0
    
    total_cost = 0.0
    total_input_cost = 0.0
    total_cached_input_cost = 0.0
    total_output_cost = 0.0
    
    total_latency = 0.0
    latency_count = 0

    cost_by_model = defaultdict(float)
    tokens_by_model = defaultdict(int)
    error_by_model = defaultdict(int)
    
    top_output_heavy = []

    try:
        with open(args.logfile, "r", encoding="utf-8-sig") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    event = json.loads(line)
                    total_requests += 1
                except json.JSONDecodeError:
                    skipped_lines += 1
                    continue
                
                status = event.get("status")
                if status == "success":
                    success_count += 1
                elif status == "error":
                    error_count += 1
                
                if event.get("error_code") == "provider_rate_limited" or event.get("error_type") == "RateLimitException":
                    rate_limit_count += 1
                
                in_tok = event.get("input_tokens") or 0
                cached_in_tok = event.get("cached_input_tokens") or 0
                out_tok = event.get("output_tokens") or 0
                tot_tok = event.get("total_tokens") or (in_tok + out_tok)
                
                cost = event.get("estimated_cost") or 0.0
                in_cost = event.get("input_cost") or 0.0
                c_in_cost = event.get("cached_input_cost") or 0.0
                out_cost = event.get("output_cost") or 0.0
                
                latency = event.get("latency_ms")

                total_input_tokens += in_tok
                total_cached_input_tokens += cached_in_tok
                total_output_tokens += out_tok
                total_tokens_all += tot_tok
                
                total_cost += cost
                total_input_cost += in_cost
                total_cached_input_cost += c_in_cost
                total_output_cost += out_cost

                if latency is not None:
                    total_latency += latency
                    latency_count += 1

                provider = event.get("provider") or "unknown"
                model = event.get("resolved_model") or event.get("model") or "unknown"
                key = f"{provider}:{model}"
                
                cost_by_model[key] += cost
                tokens_by_model[key] += tot_tok
                if status == "error":
                    error_by_model[key] += 1
                
                if out_tok > 0:
                    top_output_heavy.append({
                        "request_id": event.get("request_id"),
                        "provider_model": key,
                        "output_tokens": out_tok
                    })

    except FileNotFoundError:
        if args.json:
            print(json.dumps({"error": f"File not found: {args.logfile}"}))
        else:
            print(f"File not found: {args.logfile}")
        return

    top_output_heavy = sorted(top_output_heavy, key=lambda x: x["output_tokens"], reverse=True)[:5]
    
    cache_ratio = 0.0
    if total_input_tokens > 0:
        cache_ratio = total_cached_input_tokens / total_input_tokens

    avg_latency = total_latency / latency_count if latency_count > 0 else 0.0
    
    top_expensive = sorted(cost_by_model.items(), key=lambda x: x[1], reverse=True)[:5]
    
    warnings = []
    recommendations = []
    
    # 2. Cache economics
    if cache_ratio > 0.7:
        recommendations.append("Cache efficiency is high")
    elif cache_ratio < 0.2 and total_input_tokens > 10000:
        warnings.append("Long-context workload may benefit from cache-aware routing")
        
    # 4. Recommendations
    for k, v in cost_by_model.items():
        if total_cost > 0 and v / total_cost > 0.7:
            warnings.append(f"Model {k} accounts for >70% of total cost ({v:.6f}/{total_cost:.6f}).")
            
    if rate_limit_count > 0 and rate_limit_count / max(1, total_requests) > 0.1:
        warnings.append("Provider has high rate-limit frequency. Consider increasing cooldown or load balancing.")
        
    if total_output_tokens > total_input_tokens * 2 and total_output_tokens > 10000:
        warnings.append("Output tokens are unusually high compared to input. Check generation limits.")
        
    unknown_pricing = False
    for k, v in cost_by_model.items():
        if v == 0.0 and tokens_by_model[k] > 1000:
            unknown_pricing = True
    if unknown_pricing:
        warnings.append("Many unknown pricing records. Cost estimation may be inaccurate.")
        
    for k, c in cost_by_model.items():
        if c > 0.1 and tokens_by_model[k] < 100:
            warnings.append(f"Expensive model {k} used heavily for small requests.")

    report = {
        "total_requests": total_requests,
        "skipped_lines": skipped_lines,
        "success_count": success_count,
        "error_count": error_count,
        "rate_limit_count": rate_limit_count,
        "tokens": {
            "total_input_tokens": total_input_tokens,
            "total_cached_input_tokens": total_cached_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens_all,
            "cache_ratio": cache_ratio
        },
        "costs": {
            "total_estimated_cost": total_cost,
            "input_cost": total_input_cost,
            "cached_input_cost": total_cached_input_cost,
            "output_cost": total_output_cost,
            "partial_breakdown_unavailable": total_input_cost == 0 and total_output_cost == 0 and total_cost > 0
        },
        "average_latency_ms": avg_latency,
        "cost_by_provider_model": dict(cost_by_model),
        "tokens_by_provider_model": dict(tokens_by_model),
        "error_count_by_provider_model": dict(error_by_model),
        "top_expensive_models": [{"model": k, "cost": v} for k, v in top_expensive],
        "top_output_heavy_requests": top_output_heavy,
        "warnings": warnings,
        "recommendations": recommendations
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("--- Usage Economics Report ---")
    print(f"Total Requests: {total_requests}")
    print(f"Success/Error: {success_count}/{error_count} (Rate Limit: {rate_limit_count})")
    print(f"Average Latency: {avg_latency:.2f} ms\n")
    
    print("--- Token Economics ---")
    print(f"Total Tokens: {total_tokens_all}")
    print(f"Input Tokens: {total_input_tokens} (Cached: {total_cached_input_tokens})")
    print(f"Output Tokens: {total_output_tokens}")
    print(f"Cache Ratio: {cache_ratio*100:.2f}%\n")
    
    print("--- Cost Breakdown ---")
    print(f"Total Estimated Cost: ${total_cost:.6f}")
    if report["costs"]["partial_breakdown_unavailable"]:
        print("Note: Partial breakdown unavailable for some providers (only total cost reported).")
    else:
        print(f"  Input Cost: ${total_input_cost:.6f}")
        print(f"  Cached Input Cost: ${total_cached_input_cost:.6f}")
        print(f"  Output Cost: ${total_output_cost:.6f}")
    print()
    
    print("--- Top Expensive Provider/Model ---")
    for item in report["top_expensive_models"]:
        print(f"  {item['model']}: ${item['cost']:.6f}")
    print()
    
    print("--- Tokens by Provider/Model ---")
    for k, v in sorted(tokens_by_model.items(), key=lambda x: x[1], reverse=True):
        print(f"  {k}: {v} tokens")
    print()
    
    print("--- Errors by Provider/Model ---")
    if not error_by_model:
        print("  None")
    for k, v in sorted(error_by_model.items(), key=lambda x: x[1], reverse=True):
        print(f"  {k}: {v} errors")
    print()
    
    if top_output_heavy:
        print("--- Top Output-Heavy Requests ---")
        for req in top_output_heavy:
            print(f"  {req['request_id']} ({req['provider_model']}): {req['output_tokens']} tokens")
        print()

    if skipped_lines > 0:
        warnings.append(f"Skipped {skipped_lines} lines due to JSON parse errors.")
        print(f"[WARNING] Skipped {skipped_lines} lines due to JSON parse errors.")

    if warnings or recommendations:
        print("--- Insights & Recommendations ---")
        for rec in recommendations:
            print(f"[RECOMMENDATION] {rec}")
        for w in warnings:
            print(f"[WARNING] {w}")

if __name__ == "__main__":
    main()
