"""Telegram Bot Integration für AP2 Trainer Spot-Checks.

DDD Layer: Infrastructure. Wrapper um Telegram Bot API.
Nur HTTP-Calls, keine Business-Logik.
"""

from .bot_client import (
    TelegramBotClient,
    TelegramApiError,
    get_bot_client,
    inline_keyboard,
    callback_button,
    url_button,
)

__all__ = [
    'TelegramBotClient',
    'TelegramApiError',
    'get_bot_client',
    'inline_keyboard',
    'callback_button',
    'url_button',
]
