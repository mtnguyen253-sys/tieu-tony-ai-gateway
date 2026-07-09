"""
Core Configuration Module for AI Gateway (Dự án Tiểu Tony)
"""
import os
from dataclasses import dataclass


@dataclass
class GatewayConfig:
    """System configuration settings for the AI Gateway."""
    app_name: str = "Tiểu Tony AI Gateway"
    version: str = "0.1.0-phase0"
    environment: str = os.getenv("GATEWAY_ENV", "development")
    host: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    port: int = int(os.getenv("GATEWAY_PORT", "8000"))
    debug: bool = True


def get_config() -> GatewayConfig:
    """Load and return system configuration."""
    return GatewayConfig()
