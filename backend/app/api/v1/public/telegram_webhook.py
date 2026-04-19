"""
Telegram Webhook Endpoint — empfängt Updates vom Bot.

DDD: API-Layer. Nur Auth-Validierung + Service-Aufruf.

Sicherheit: validiert X-Telegram-Bot-Api-Secret-Token Header gegen
TELEGRAM_WEBHOOK_SECRET aus ENV. Wenn nicht gesetzt, läuft Webhook
ohne Validierung (nur für Dev — in Prod immer setzen!).
"""

import logging
import os

from flask import Blueprint, request, jsonify

from app.application.services.ap2 import TelegramSessionService

logger = logging.getLogger(__name__)


telegram_webhook_bp = Blueprint(
    'telegram_webhook',
    __name__,
    url_prefix='/telegram',
)


@telegram_webhook_bp.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Empfängt Updates von Telegram, dispatcht an SessionService."""
    # Optional: Secret-Token-Validierung
    expected_secret = os.getenv('TELEGRAM_WEBHOOK_SECRET')
    if expected_secret:
        provided = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
        if provided != expected_secret:
            logger.warning('Telegram webhook: invalid secret token')
            return jsonify({'error': 'unauthorized'}), 401

    update = request.get_json(silent=True) or {}
    if not update:
        logger.warning('Telegram webhook: empty body')
        return jsonify({'ok': True}), 200

    try:
        TelegramSessionService.handle_update(update)
    except Exception:
        logger.exception('Telegram update handling failed: %s',
                         update.get('update_id', 'unknown'))
        # Wichtig: trotzdem 200 zurück, sonst retried Telegram endlos
        return jsonify({'ok': True, 'error': 'internal'}), 200

    return jsonify({'ok': True}), 200


@telegram_webhook_bp.route('/health', methods=['GET'])
def telegram_health():
    """Healthcheck: prüft ob Bot-Token gesetzt + API erreichbar."""
    from app.infrastructure.telegram import get_bot_client, TelegramApiError
    try:
        bot_info = get_bot_client().get_me()
        return jsonify({
            'ok': True,
            'bot_username': bot_info.get('username'),
            'bot_id': bot_info.get('id'),
        }), 200
    except (ValueError, TelegramApiError) as e:
        return jsonify({'ok': False, 'error': str(e)}), 503
