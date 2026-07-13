from typing import Optional, Dict, Any

class CostEstimator:
    def __init__(self, prices: Optional[Dict[str, Dict[str, Any]]] = None):
        self.prices = prices or {}

    def estimate_detailed(
        self,
        provider: str,
        model: str,
        input_tokens: Optional[int],
        output_tokens: Optional[int],
        cached_input_tokens: Optional[int] = 0
    ) -> float:
        if input_tokens is None and output_tokens is None:
            return {"total_cost": 0.0, "input_cost": 0.0, "cached_input_cost": 0.0, "output_cost": 0.0}
            
        key = f"{provider}:{model}"
        price_info = self.prices.get(key)
        
        if not price_info:
            return {"total_cost": 0.0, "input_cost": 0.0, "cached_input_cost": 0.0, "output_cost": 0.0}
            
        input_per_million = price_info.get("input_per_million", 0.0)
        cached_input_per_million = price_info.get("cached_input_per_million", 0.0)
        output_per_million = price_info.get("output_per_million", 0.0)
        
        input_tokens = input_tokens or 0
        output_tokens = output_tokens or 0
        cached_input_tokens = cached_input_tokens or 0
        
        non_cached_input = max(0, input_tokens - cached_input_tokens)
        
        cost = (non_cached_input / 1_000_000.0) * input_per_million
        c_input = (non_cached_input / 1_000_000.0) * input_per_million
        c_cached = (cached_input_tokens / 1_000_000.0) * cached_input_per_million
        c_output = (output_tokens / 1_000_000.0) * output_per_million
        cost = c_input + c_cached + c_output
        
        return {
            "total_cost": cost,
            "input_cost": c_input,
            "cached_input_cost": c_cached,
            "output_cost": c_output
        }

    def estimate(
        self,
        provider: str,
        model: str,
        input_tokens: Optional[int],
        output_tokens: Optional[int],
        cached_input_tokens: Optional[int] = 0
    ) -> float:
        res = self.estimate_detailed(provider, model, input_tokens, output_tokens, cached_input_tokens)
        if isinstance(res, dict):
            return res.get("total_cost", 0.0)
        return res
