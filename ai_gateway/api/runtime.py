"""Explicit production runtime entrypoint that loads .env configuration."""

from ai_gateway.api.app import create_app
from ai_gateway.config.settings import load_settings_from_dotenv


app = create_app(app_settings=load_settings_from_dotenv())
