import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Settings:
    def __init__(self):
        self.host = os.getenv("AI_GATEWAY_HOST", "127.0.0.1")
        self.port = int(os.getenv("AI_GATEWAY_PORT", "8000"))
        self.log_level = os.getenv("AI_GATEWAY_LOG_LEVEL", "info")
        self.budget_mode = os.getenv("AI_GATEWAY_BUDGET_MODE", "normal")
        
        # Provider config
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "qwen/qwen3.6-plus")

settings = Settings()
