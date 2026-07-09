import pytest
from ai_gateway.core.compressor import MessageCompressor

def test_token_estimation():
    compressor = MessageCompressor(chars_per_token=4.0)
    assert compressor._estimate_tokens("1234") == 1
    assert compressor._estimate_tokens("12345") == 2
    assert compressor._estimate_tokens("") == 0

def test_summarize_long_text():
    compressor = MessageCompressor()
    text = "A" * 1000
    summarized = compressor._summarize_long_text(text, max_chars=100)
    assert len(summarized) <= 150  # 100 chars + compression notice length
    assert summarized.startswith("A")
    assert summarized.endswith("A")
    assert "[CONTENT COMPRESSED]" in summarized

def test_compress_under_limit():
    compressor = MessageCompressor()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    # Limit is very high, no compression expected
    compressed = compressor.compress(messages, max_tokens=1000)
    assert len(compressed) == 2
    assert compressed[0]["content"] == "You are a helpful assistant."
    assert compressed[1]["content"] == "Hello!"

def test_compress_over_limit():
    compressor = MessageCompressor(chars_per_token=4.0)
    
    # Create a large log message
    huge_log = "ERROR: Something went wrong\n" * 1000  # ~28k chars -> ~7k tokens
    
    messages = [
        {"role": "system", "content": "System prompt core instructions"},
        {"role": "user", "content": "Run this task"},
        {"role": "assistant", "content": "Running..."},
        {"role": "user", "content": huge_log},
        {"role": "assistant", "content": "Failed."},
        {"role": "user", "content": "What happened?"}
    ]
    
    # We want to compress to max 100 tokens (~400 chars)
    compressed = compressor.compress(messages, max_tokens=100)
    
    # Ensure structure is maintained
    assert len(compressed) == len(messages)
    
    # System should be untouched
    assert compressed[0]["content"] == messages[0]["content"]
    
    # Last 2 non-system messages (Failed, What happened?) should be untouched
    assert compressed[-1]["content"] == "What happened?"
    assert compressed[-2]["content"] == "Failed."
    
    # The huge log should be compressed
    assert len(compressed[3]["content"]) < len(huge_log)
    assert "[CONTENT COMPRESSED]" in compressed[3]["content"]
    
    # Calculate total tokens after compression to ensure it dropped significantly
    total_tokens_after = sum(compressor._estimate_message_tokens(m) for m in compressed)
    
    # It might not be exactly 100 due to fixed size of protected messages and compression strings,
    # but it should be way less than original
    assert total_tokens_after < 250
