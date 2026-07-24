from unittest.mock import patch

from ai_gateway.config.settings import load_settings_from_dotenv


def test_dotenv_loading_is_explicit():
    with patch("dotenv.load_dotenv") as load_dotenv:
        load_settings_from_dotenv()

    load_dotenv.assert_called_once_with()
