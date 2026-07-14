import os
import json
import argparse
from typing import List, Dict, Any
from ai_gateway.config.settings import settings
from ai_gateway.core.usage import UsageEvent
from ai_gateway.core.provider_statistics import StatisticsUpdater, ProviderStats

def load_events_from_jsonl(file_path: str) -> List[UsageEvent]:
    events = []
    if not os.path.exists(file_path):
        return events
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                # Load with model_validate_json
                event = UsageEvent.model_validate_json(line)
                events.append(event)
            except Exception as e:
                # Fallback to simple dict load if parsing fails
                try:
                    data = json.loads(line)
                    event = UsageEvent(**data)
                    events.append(event)
                except Exception:
                    pass
    return events

def get_recommendation(stats: ProviderStats, total_count: int) -> str:
    if total_count == 0:
        return "No History"
    
    success_rate = stats.success_count / total_count
    timeout_rate = stats.timeout_count / total_count
    rate_limit_rate = stats.rate_limit_count / total_count
    
    # Critical flags for AVOID
    if success_rate < 0.85 or timeout_rate > 0.15 or rate_limit_rate > 0.15 or stats.auth_error_count > 0:
        return "Avoid temporarily"
    
    # Highly optimal flags for Preferred
    if success_rate >= 0.98 and stats.cache_hit_ratio >= 0.30 and stats.average_cost < 0.5:
        return "Preferred"
    
    if success_rate >= 0.95:
        return "GOOD"
    elif success_rate >= 0.88:
        return "OK"
    else:
        return "BAD"

def generate_report(file_path: str = "logs/usage.jsonl"):
    print("=== AI Gateway Provider Statistics Report ===")
    print(f"Reading historical events from: {file_path}")
    
    events = load_events_from_jsonl(file_path)
    print(f"Total historical events loaded: {len(events)}\n")
    
    updater = StatisticsUpdater(window_size=100) # Use a reasonably sized window for global report
    for event in events:
        updater.update(event)
        
    # Get all unique providers from events and config
    providers = {settings.env.get("AI_GATEWAY_PROVIDER_1_NAME", "cliproxy")}
    for p in settings.providers:
        providers.add(p.name)
    for event in events:
        if event.provider:
            providers.add(event.provider)
            
    sorted_providers = sorted(list(providers))
    
    # Headers
    print(f"{'Provider':<18} | {'Success %':<9} | {'Failure %':<9} | {'Avg Cost':<9} | {'Avg Latency':<12} | {'Avg Tokens':<10} | {'Cache Hit':<9} | {'Rolling Score':<13} | {'Recommendation':<18}")
    print("-" * 115)
    
    for provider in sorted_providers:
        stats = updater.get_stats(provider)
        total = stats.success_count + stats.failure_count
        
        success_pct = f"{(stats.success_count / total * 100):.1f}%" if total > 0 else "N/A"
        failure_pct = f"{(stats.failure_count / total * 100):.1f}%" if total > 0 else "N/A"
        avg_cost = f"${stats.average_cost:.5f}" if total > 0 else "N/A"
        avg_latency = f"{stats.average_latency:.1f}ms" if total > 0 else "N/A"
        avg_tokens = f"{int(stats.average_prompt_tokens + stats.average_completion_tokens)}" if total > 0 else "N/A"
        cache_hit = f"{(stats.cache_hit_ratio * 100):.1f}%" if total > 0 else "N/A"
        rolling_score = f"{stats.rolling_score:.1f}"
        recommendation = get_recommendation(stats, total)
        
        print(f"{provider:<18} | {success_pct:<9} | {failure_pct:<9} | {avg_cost:<9} | {avg_latency:<12} | {avg_tokens:<10} | {cache_hit:<9} | {rolling_score:<13} | {recommendation:<18}")
    print("-" * 115)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate provider adaptive routing statistics report.")
    parser.add_argument("file_path", nargs="?", default="logs/usage.jsonl", help="Path to usage.jsonl file.")
    args = parser.parse_args()
    
    generate_report(args.file_path)
