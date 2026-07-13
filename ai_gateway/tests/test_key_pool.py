import pytest
from ai_gateway.core.key_pool import KeyPool
from ai_gateway.config.settings import ProviderKeyProfile
from ai_gateway.core.quota import InMemoryQuotaTracker
from ai_gateway.core.cooldown import ProviderCooldownManager
from unittest.mock import MagicMock

def test_key_selection_lowest_usage():
    tracker = InMemoryQuotaTracker()
    cooldown = ProviderCooldownManager()
    keys = [
        ProviderKeyProfile(name="key1", api_key="k1", enabled=True),
        ProviderKeyProfile(name="key2", api_key="k2", enabled=True),
    ]
    pool = KeyPool("p1", keys, tracker, cooldown)
    
    # key1 has 5 uses, key2 has 10 uses
    for _ in range(5): tracker.record_success("p1", "key1")
    for _ in range(10): tracker.record_success("p1", "key2")
    
    selected = pool.select_key()
    assert selected.name == "key1"

def test_key_selection_skips_disabled():
    tracker = InMemoryQuotaTracker()
    cooldown = ProviderCooldownManager()
    keys = [
        ProviderKeyProfile(name="key1", api_key="k1", enabled=False),
        ProviderKeyProfile(name="key2", api_key="k2", enabled=True),
    ]
    pool = KeyPool("p1", keys, tracker, cooldown)
    
    selected = pool.select_key()
    assert selected.name == "key2"

def test_key_selection_skips_request_limit():
    tracker = InMemoryQuotaTracker()
    cooldown = ProviderCooldownManager()
    keys = [
        ProviderKeyProfile(name="key1", api_key="k1", enabled=True, daily_request_limit=1),
    ]
    pool = KeyPool("p1", keys, tracker, cooldown)
    
    tracker.record_success("p1", "key1")
    
    selected = pool.select_key()
    assert selected is None

def test_key_selection_skips_cost_limit():
    tracker = InMemoryQuotaTracker()
    cooldown = ProviderCooldownManager()
    keys = [
        ProviderKeyProfile(name="key1", api_key="k1", enabled=True, daily_cost_limit=0.5),
    ]
    pool = KeyPool("p1", keys, tracker, cooldown)
    
    tracker.record_success("p1", "key1", cost=0.6)
    
    selected = pool.select_key()
    assert selected is None

def test_key_selection_skips_cooldown():
    tracker = InMemoryQuotaTracker()
    cooldown = ProviderCooldownManager()
    keys = [
        ProviderKeyProfile(name="key1", api_key="k1", enabled=True),
    ]
    pool = KeyPool("p1", keys, tracker, cooldown)
    
    cooldown.mark_cooldown("p1", duration=60.0)
    
    selected = pool.select_key()
    assert selected is None
