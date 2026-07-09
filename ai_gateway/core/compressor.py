import math
from typing import List, Dict, Any

class MessageCompressor:
    """
    Compresses conversation history to fit within context limits using rule-based techniques.
    """
    
    def __init__(self, chars_per_token: float = 4.0):
        self.chars_per_token = chars_per_token

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens based on character count."""
        if not text:
            return 0
        return math.ceil(len(text) / self.chars_per_token)

    def _estimate_message_tokens(self, message: Dict[str, Any]) -> int:
        """Estimate tokens for a single message."""
        content = message.get("content", "")
        if content is None:
            return 0
        return self._estimate_tokens(str(content))

    def _summarize_long_text(self, text: str, max_chars: int) -> str:
        """Summarize long text by keeping the beginning and end."""
        if len(text) <= max_chars:
            return text
        
        half_limit = max(0, (max_chars - 50) // 2)
        if half_limit == 0:
            return "[...TRUNCATED...]"
            
        return text[:half_limit] + "\n\n...[CONTENT COMPRESSED]...\n\n" + text[-half_limit:]

    def compress(self, messages: List[Dict[str, Any]], max_tokens: int) -> List[Dict[str, Any]]:
        """
        Compresses messages to fit within max_tokens.
        Strategy:
        1. Always keep 'system' messages.
        2. Always keep the last few messages (e.g., last 2).
        3. For messages in the middle, truncate long contents (like logs or huge code blocks)
           if we are over the token limit.
        """
        if not messages:
            return []

        total_tokens = sum(self._estimate_message_tokens(m) for m in messages)
        if total_tokens <= max_tokens:
            return messages

        compressed_messages = []
        
        # Identify system messages and the most recent messages
        system_indices = [i for i, m in enumerate(messages) if m.get("role") == "system"]
        
        # Keep the last 2 messages intact if possible
        recent_count = min(2, len(messages) - len(system_indices))
        recent_indices = []
        if recent_count > 0:
             # Get the last recent_count indices that are not system messages
             non_system_indices = [i for i in range(len(messages)) if i not in system_indices]
             recent_indices = non_system_indices[-recent_count:] if non_system_indices else []

        protected_indices = set(system_indices + recent_indices)
        
        # Calculate tokens used by protected messages
        protected_tokens = sum(self._estimate_message_tokens(messages[i]) for i in protected_indices)
        
        # Calculate remaining tokens for the middle messages
        remaining_tokens = max(0, max_tokens - protected_tokens)
        
        # Middle messages are those not protected
        middle_indices = [i for i in range(len(messages)) if i not in protected_indices]
        
        # Distribute remaining tokens among middle messages evenly
        if middle_indices:
            tokens_per_middle_msg = max(5, remaining_tokens // len(middle_indices))
            max_chars_per_msg = int(tokens_per_middle_msg * self.chars_per_token)
        else:
            max_chars_per_msg = 0

        for i, msg in enumerate(messages):
            new_msg = msg.copy()
            if i in protected_indices:
                compressed_messages.append(new_msg)
            else:
                content = str(new_msg.get("content", ""))
                compressed_content = self._summarize_long_text(content, max_chars_per_msg)
                new_msg["content"] = compressed_content
                compressed_messages.append(new_msg)

        return compressed_messages
