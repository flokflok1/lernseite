"""
Telegram Bot Client — Wrapper um Telegram Bot API.

Nur HTTP-Calls, keine Business-Logik. Token aus ENV.
DDD Layer: Infrastructure.

Verwendet requests (synchron) statt asyncio — passt zu Flask + Celery.
"""

import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

TELEGRAM_API_BASE = 'https://api.telegram.org'
DEFAULT_TIMEOUT_SEC = 10


class TelegramApiError(Exception):
    """Telegram API hat einen Fehler zurückgegeben."""

    def __init__(self, message: str, response_data: Optional[dict] = None):
        super().__init__(message)
        self.response_data = response_data or {}


class TelegramBotClient:
    """Synchroner Wrapper um die Telegram Bot HTTP API."""

    def __init__(self, token: Optional[str] = None):
        self._token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not self._token:
            raise ValueError('TELEGRAM_BOT_TOKEN nicht gesetzt')
        self._base_url = f'{TELEGRAM_API_BASE}/bot{self._token}'

    # ============================================================
    # Core HTTP-Layer
    # ============================================================

    def _post(self, method: str, payload: dict,
              timeout: int = DEFAULT_TIMEOUT_SEC) -> dict:
        """POST gegen die Telegram Bot API."""
        url = f'{self._base_url}/{method}'
        try:
            response = requests.post(url, json=payload, timeout=timeout)
        except requests.RequestException:
            logger.exception('Telegram API HTTP-Fehler bei %s', method)
            raise

        try:
            data = response.json()
        except ValueError:
            logger.error(
                'Telegram API Non-JSON-Response (status=%s): %s',
                response.status_code, response.text[:200]
            )
            raise TelegramApiError(
                f'Non-JSON response (status={response.status_code})'
            )

        if not data.get('ok'):
            description = data.get('description', 'Unknown')
            logger.error('Telegram API Fehler bei %s: %s', method, description)
            raise TelegramApiError(description, response_data=data)

        return data.get('result', {})

    # ============================================================
    # Bot Info
    # ============================================================

    def get_me(self) -> dict:
        """Liefert Bot-Info (für Connectivity-Test)."""
        return self._post('getMe', {})

    # ============================================================
    # Messages
    # ============================================================

    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = 'Markdown',
        reply_markup: Optional[dict] = None,
        disable_notification: bool = False,
    ) -> dict:
        """Sendet eine Text-Nachricht.

        parse_mode: 'Markdown' | 'MarkdownV2' | 'HTML' | None
        reply_markup: Inline-Keyboard / Reply-Keyboard / Force-Reply
        """
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True,
            'disable_notification': disable_notification,
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        return self._post('sendMessage', payload)

    def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = 'Markdown',
        reply_markup: Optional[dict] = None,
    ) -> dict:
        """Bearbeitet eine bestehende Nachricht (z.B. nach Button-Klick)."""
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True,
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
        return self._post('editMessageText', payload)

    def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False,
    ) -> dict:
        """Bestätigt einen Inline-Button-Klick (entfernt Loading-Spinner)."""
        payload = {'callback_query_id': callback_query_id}
        if text:
            payload['text'] = text
            payload['show_alert'] = show_alert
        return self._post('answerCallbackQuery', payload)

    def send_photo(
        self,
        chat_id: int,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: str = 'Markdown',
        reply_markup: Optional[dict] = None,
    ) -> dict:
        """Sendet ein Bild via URL (z.B. Diagramm aus Webapp)."""
        payload = {
            'chat_id': chat_id,
            'photo': photo_url,
            'parse_mode': parse_mode,
        }
        if caption:
            payload['caption'] = caption
        if reply_markup:
            payload['reply_markup'] = reply_markup
        return self._post('sendPhoto', payload)

    # ============================================================
    # Webhook Management
    # ============================================================

    def set_webhook(
        self,
        webhook_url: str,
        secret_token: Optional[str] = None,
        allowed_updates: Optional[list[str]] = None,
    ) -> dict:
        """Registriert einen Webhook bei Telegram.

        secret_token: empfohlen — wird im Header X-Telegram-Bot-Api-Secret-Token
                      mitgesendet, kann im Webhook-Endpoint validiert werden
        """
        payload: dict = {'url': webhook_url}
        if secret_token:
            payload['secret_token'] = secret_token
        if allowed_updates is not None:
            payload['allowed_updates'] = allowed_updates
        else:
            payload['allowed_updates'] = ['message', 'callback_query']
        return self._post('setWebhook', payload, timeout=15)

    def delete_webhook(self, drop_pending: bool = False) -> dict:
        """Entfernt registrierten Webhook."""
        return self._post('deleteWebhook', {'drop_pending_updates': drop_pending})

    def get_webhook_info(self) -> dict:
        """Liefert aktuelle Webhook-Konfiguration."""
        return self._post('getWebhookInfo', {})


# ============================================================
# Singleton-Helper
# ============================================================

_bot_client_singleton: Optional[TelegramBotClient] = None


def get_bot_client() -> TelegramBotClient:
    """Liefert den Bot-Client (Lazy-Init Singleton)."""
    global _bot_client_singleton
    if _bot_client_singleton is None:
        _bot_client_singleton = TelegramBotClient()
    return _bot_client_singleton


# ============================================================
# Helpers für Inline-Keyboards
# ============================================================

def inline_keyboard(rows: list[list[dict]]) -> dict:
    """Baut ein Inline-Keyboard.

    rows: Liste von Reihen, jede Reihe = Liste von Button-Dicts.
    Button: {'text': '...', 'callback_data': '...'} oder {'text': '...', 'url': '...'}

    Beispiel:
        kb = inline_keyboard([
            [{'text': '✓ Sitzt', 'callback_data': 'recall:ok:abc'}],
            [{'text': '🔄 Refresh', 'callback_data': 'recall:refresh:abc'}],
        ])
    """
    return {'inline_keyboard': rows}


def callback_button(text: str, data: str) -> dict:
    """Shortcut für einen einzelnen Callback-Button."""
    return {'text': text, 'callback_data': data}


def url_button(text: str, url: str) -> dict:
    """Shortcut für einen URL-Button (öffnet im Browser)."""
    return {'text': text, 'url': url}
