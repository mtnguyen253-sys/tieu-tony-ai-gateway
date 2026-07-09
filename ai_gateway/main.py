"""
Main Entry Point for AI Gateway (Dự án Tiểu Tony - Phase 0)
"""
import sys
from core.config import get_config


def main():
    """Initialize system configuration and start gateway daemon."""
    config = get_config()
    
    print(f"[{config.app_name} v{config.version}] Initializing system configuration...")
    print(f"Mode: {config.environment} | Debug: {config.debug} | Host: {config.host}:{config.port}")
    print("Gateway started")


if __name__ == "__main__":
    main()
