"""
TelegramSessionService — verarbeitet Bot-Updates und führt User durch Modul-Loop.

Bindet:
- TelegramBotClient (HTTP an Telegram)
- TelegramLinkRepository (Account-Verknüpfung)
- ModuleProgressService (Mastery-Logik)
- Redis (Session-State pro chat_id: welches Item aktuell aktiv)

Update-Typen die verarbeitet werden:
- /start CODE     — Account verknüpfen
- /start          — Hilfe
- /heute          — fällige Spot-Checks
- /skip /pause /stats /hilfe
- Text-Antwort    — als Antwort auf aktive Frage werten
- Callback-Query  — Inline-Button-Klick (z.B. „Sitzt" oder „Refresh")

DDD Layer: Application.
"""

import json
import logging
from typing import Optional
from uuid import UUID

from app.domain.models.ap2 import (
    AttemptSource, ModuleStatus, MASTERY_PASS_THRESHOLD,
)
from app.infrastructure.persistence.repositories.user import (
    TelegramLinkRepository,
)
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2ModuleRepository, Ap2ModuleProgressRepository,
)
from app.infrastructure.telegram import (
    get_bot_client, inline_keyboard, callback_button, url_button,
    TelegramApiError,
)
from app.application.services.ap2.module_progress_service import (
    ModuleProgressService, ModuleNotAvailableError,
)

logger = logging.getLogger(__name__)


# Redis-Keys
SESSION_KEY = 'telegram:session:{chat_id}'           # JSON {module_id, item_id, phase}
SESSION_TTL_SEC = 3600 * 6  # 6h pro aktiver Session


class TelegramSessionService:
    """Verarbeitet eingehende Telegram-Updates."""

    # ============================================================
    # Public API: Update-Dispatcher
    # ============================================================

    @classmethod
    def handle_update(cls, update: dict) -> None:
        """Hauptdispatcher für eingehende Telegram-Updates.

        update: das vom Webhook empfangene Dict.
        """
        if 'callback_query' in update:
            cls._handle_callback(update['callback_query'])
        elif 'message' in update:
            cls._handle_message(update['message'])
        else:
            logger.debug('Telegram update ohne handler-fall: keys=%s',
                         list(update.keys()))

    # ============================================================
    # Message Handler
    # ============================================================

    @classmethod
    def _handle_message(cls, message: dict) -> None:
        chat = message.get('chat', {})
        chat_id = chat.get('id')
        text = (message.get('text') or '').strip()

        if not chat_id:
            logger.warning('Telegram message ohne chat.id: %s', message)
            return

        # /start ohne Parameter → Hilfe
        if text == '/start' or text == '/start ':
            cls._send_welcome(chat_id, linked=cls._is_linked(chat_id))
            return

        # /start CODE → Verknüpfung
        if text.startswith('/start '):
            code = text.split(' ', 1)[1].strip().upper()
            cls._handle_link_code(chat_id, code, message.get('from', {}))
            return

        # Andere Befehle
        if text.startswith('/'):
            cls._handle_command(chat_id, text)
            return

        # Sonst: als Antwort auf aktive Frage werten
        cls._handle_text_answer(chat_id, text)

    # ============================================================
    # Callback Query Handler (Inline-Button-Klicks)
    # ============================================================

    @classmethod
    def _handle_callback(cls, callback_query: dict) -> None:
        cb_id = callback_query.get('id')
        chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
        message_id = callback_query.get('message', {}).get('message_id')
        data = callback_query.get('data', '')

        bot = get_bot_client()
        # Loading-Spinner sofort entfernen
        try:
            bot.answer_callback_query(cb_id)
        except TelegramApiError:
            logger.exception('answer_callback_query fehlgeschlagen')

        if not chat_id:
            return

        # Callback-Format: 'action:detail:more_detail'
        parts = data.split(':')
        action = parts[0] if parts else ''

        if action == 'spotcheck':
            # 'spotcheck:start:<module_id>'
            if len(parts) >= 3 and parts[1] == 'start':
                cls._start_spotcheck_in_telegram(chat_id, parts[2])
        elif action == 'snooze':
            # 'snooze:30m' / 'snooze:tomorrow'
            cls._handle_snooze(chat_id, parts[1] if len(parts) > 1 else '30m')
        elif action == 'help':
            cls._send_help(chat_id)
        else:
            logger.debug('Unbekannte callback-action: %s', action)

    # ============================================================
    # Befehle
    # ============================================================

    @classmethod
    def _handle_command(cls, chat_id: int, text: str) -> None:
        cmd = text.split()[0].lower()
        bot = get_bot_client()

        if cmd in ('/heute', '/today'):
            cls._send_today(chat_id)
        elif cmd in ('/stats', '/status'):
            cls._send_stats(chat_id)
        elif cmd == '/hilfe' or cmd == '/help':
            cls._send_help(chat_id)
        elif cmd == '/skip':
            bot.send_message(
                chat_id,
                '_Skip-Funktion wird in der nächsten Version erweitert. Heutige '
                'Spot-Checks bleiben fällig — du kannst sie morgen machen ohne '
                'Strafe._',
            )
        elif cmd == '/pause':
            bot.send_message(
                chat_id,
                '_Pause-Funktion wird in der nächsten Version erweitert._',
            )
        else:
            bot.send_message(
                chat_id,
                f'Unbekannter Befehl: {cmd}. Tippe /hilfe für die Liste.',
            )

    # ============================================================
    # Account-Verknüpfung
    # ============================================================

    @classmethod
    def _handle_link_code(cls, chat_id: int, code: str,
                          from_user: dict) -> None:
        bot = get_bot_client()
        user_record = TelegramLinkRepository.find_user_by_link_code(code)

        if not user_record:
            bot.send_message(
                chat_id,
                f'❌ Code `{code}` ist ungültig oder abgelaufen.\n\n'
                'Generiere einen neuen Code in der Webapp '
                '(_Profil → Telegram verbinden_) und schicke ihn dann hier '
                'als `/start NEUERCODE`.',
            )
            return

        # Existing chat_id für diesen User vorhanden? → überschreiben
        TelegramLinkRepository.link_chat(user_record['user_id'], chat_id)

        first_name = from_user.get('first_name', 'da')
        bot.send_message(
            chat_id,
            f'✅ *Verknüpft, {first_name}!*\n\n'
            f'Account: `{user_record.get("username") or user_record.get("email")}`\n\n'
            f'Ab jetzt sende ich dir morgens um 9:00 die fälligen Spot-Checks.\n\n'
            f'*Befehle:*\n'
            f'/heute — was heute fällig ist\n'
            f'/stats — dein Fortschritt\n'
            f'/hilfe — alle Befehle\n\n'
            f'_Tipp: schicke mir jederzeit `/heute` um zu üben._',
        )

    @classmethod
    def _is_linked(cls, chat_id: int) -> bool:
        return TelegramLinkRepository.find_user_by_chat_id(chat_id) is not None

    @classmethod
    def _send_welcome(cls, chat_id: int, linked: bool) -> None:
        bot = get_bot_client()
        if linked:
            bot.send_message(
                chat_id,
                '👋 Willkommen zurück!\n\n'
                'Tippe /heute für die fälligen Spot-Checks.\n'
                '/hilfe für alle Befehle.',
            )
        else:
            bot.send_message(
                chat_id,
                '👋 *Hallo, ich bin dein AP2-Trainer!*\n\n'
                'Ich helfe dir bei den Spot-Checks zu deinen Diagramm-Modulen.\n\n'
                '*Erste Schritte:*\n'
                '1. Geh in die Webapp → _Profil_\n'
                '2. Klick auf _Telegram verbinden_\n'
                '3. Kopiere den 6-stelligen Code\n'
                '4. Schicke ihn hier: `/start DEINCODE`\n\n'
                'Dann pinge ich dich automatisch wenn was zum Üben ansteht.',
            )

    # ============================================================
    # /heute
    # ============================================================

    @classmethod
    def _send_today(cls, chat_id: int) -> None:
        bot = get_bot_client()
        user = TelegramLinkRepository.find_user_by_chat_id(chat_id)
        if not user:
            cls._send_welcome(chat_id, linked=False)
            return

        user_id = user['user_id']

        # Fällige Recalls (4h-Marker)
        # Nur die für DIESEN User
        all_progress = Ap2ModuleProgressRepository.find_all_for_user(user_id)
        due_recalls = [p for p in all_progress if p.is_recall_overdue]
        due_spotchecks = Ap2ModuleProgressRepository.find_due_spotchecks(user_id)

        if not due_recalls and not due_spotchecks:
            bot.send_message(
                chat_id,
                '✨ *Heute nichts fällig.*\n\n'
                'Du kannst aber jederzeit ein neues Modul in der Webapp starten.\n'
                '/stats zeigt deinen aktuellen Fortschritt.',
            )
            return

        # Liste bauen
        lines = ['*Heute fällig:*\n']
        rows = []
        for p in due_recalls:
            module = Ap2ModuleRepository.find_by_id(p.module_id)
            if not module:
                continue
            lines.append(f'🔄 *{module.name_de}* — Same-Day-Recall (1 min)')
            rows.append([callback_button(
                f'▶ Recall: {module.name_de[:24]}',
                f'spotcheck:start:{p.module_id}',
            )])
        for p in due_spotchecks:
            module = Ap2ModuleRepository.find_by_id(p.module_id)
            if not module:
                continue
            lines.append(f'🔄 *{module.name_de}* — Spot-Check (1 min)')
            rows.append([callback_button(
                f'▶ Check: {module.name_de[:24]}',
                f'spotcheck:start:{p.module_id}',
            )])

        rows.append([callback_button('⏰ In 30 min', 'snooze:30m'),
                     callback_button('🛌 Heute nicht', 'snooze:tomorrow')])

        bot.send_message(
            chat_id,
            '\n'.join(lines),
            reply_markup=inline_keyboard(rows),
        )

    @classmethod
    def _start_spotcheck_in_telegram(cls, chat_id: int, module_id_str: str) -> None:
        bot = get_bot_client()
        user = TelegramLinkRepository.find_user_by_chat_id(chat_id)
        if not user:
            cls._send_welcome(chat_id, linked=False)
            return

        try:
            module_id = UUID(module_id_str)
        except ValueError:
            bot.send_message(chat_id, '❌ Ungültige Modul-ID.')
            return

        user_id = user['user_id']
        progress = Ap2ModuleProgressRepository.find_by_user_module(user_id, module_id)
        if not progress:
            bot.send_message(chat_id, '❌ Kein aktiver Fortschritt für dieses Modul.')
            return

        # Item ziehen je nach Status
        if progress.status == ModuleStatus.PENDING_RECALL:
            item = ModuleProgressService.get_recall_item(user_id, module_id)
            phase_label = 'Same-Day-Recall'
        elif progress.status == ModuleStatus.MASTERED:
            item = ModuleProgressService.get_spotcheck_item(user_id, module_id)
            phase_label = 'Spot-Check'
        else:
            bot.send_message(
                chat_id,
                'Dieses Modul ist nicht im Spot-Check-Status. Öffne es in der Webapp.',
            )
            return

        if not item:
            bot.send_message(chat_id, '❌ Kein Pool-Item verfügbar.')
            return

        # Session in Redis ablegen damit nächste Text-Nachricht als Antwort gewertet wird
        cls._set_session(chat_id, {
            'module_id': str(module_id),
            'item_id': str(item.item_id),
            'phase_label': phase_label,
        })

        module = Ap2ModuleRepository.find_by_id(module_id)
        bot.send_message(
            chat_id,
            f'🔄 *{phase_label}: {module.name_de if module else ""}*\n\n'
            f'_Frage:_\n{item.prompt[:1500]}\n\n'
            f'_Tippe deine Antwort als Nachricht._',
        )

    # ============================================================
    # Text-Antwort verarbeiten
    # ============================================================

    @classmethod
    def _handle_text_answer(cls, chat_id: int, text: str) -> None:
        bot = get_bot_client()
        session = cls._get_session(chat_id)

        if not session:
            bot.send_message(
                chat_id,
                '_Keine aktive Frage. Tippe /heute für fällige Spot-Checks._',
            )
            return

        user = TelegramLinkRepository.find_user_by_chat_id(chat_id)
        if not user:
            return

        try:
            module_id = UUID(session['module_id'])
            item_id = UUID(session['item_id'])
        except (KeyError, ValueError):
            cls._clear_session(chat_id)
            bot.send_message(chat_id, '_Session abgelaufen — bitte /heute erneut._')
            return

        # Session löschen sobald wir loslegen — verhindert doppelte Verarbeitung
        cls._clear_session(chat_id)

        bot.send_message(chat_id, '⏳ _Bewerte deine Antwort..._')

        try:
            result = ModuleProgressService.submit_answer(
                user_id=user['user_id'],
                module_id=module_id,
                item_id=item_id,
                user_answer=text,
                source=AttemptSource.TELEGRAM,
            )
        except ModuleNotAvailableError as e:
            bot.send_message(chat_id, f'❌ {e}')
            return
        except Exception:
            logger.exception('submit_answer fehlgeschlagen')
            bot.send_message(chat_id,
                '❌ Bewertung fehlgeschlagen — bitte später nochmal probieren.')
            return

        cls._send_evaluation_result(chat_id, result)

    @classmethod
    def _send_evaluation_result(cls, chat_id: int, result: dict) -> None:
        bot = get_bot_client()
        pct = result['pct']
        passed = result['passed']
        feedback = result['feedback']
        progress = result['progress']

        emoji = '✅' if passed else '❌'
        score_line = f'{emoji} *{pct} %* {"— bestanden" if passed else "— nicht bestanden"}'

        parts = [score_line]
        if feedback.summary:
            parts.append(f'\n_{feedback.summary[:300]}_')

        if feedback.missing_aspects:
            parts.append('\n*Was gefehlt hat:*')
            for m in feedback.missing_aspects[:4]:
                parts.append(f'• {m[:120]}')
        if feedback.suggestions:
            parts.append('\n*Tipp:*')
            for s in feedback.suggestions[:2]:
                parts.append(f'• {s[:200]}')

        # Status-Update
        status_line = ''
        if progress.status == ModuleStatus.MASTERED:
            status_line = '\n\n🎉 *Modul mastered!* Spot-Check kommt automatisch in 2 Tagen.'
        elif progress.status == ModuleStatus.PENDING_RECALL:
            status_line = (
                f'\n\n🟡 *3-Streak geschafft!* Same-Day-Recall in 4h.'
            )
        elif progress.status == ModuleStatus.LEARNING:
            status_line = (
                f'\n\n📚 _Streak: {progress.streak_count}/3._ '
            )
            if result.get('next_item'):
                status_line += 'Nächste Aufgabe sende ich dir gleich.'
        elif progress.status == ModuleStatus.REVIEW_FAILED:
            status_line = '\n\n🔄 _Spot-Check nicht bestanden — kurzer Refresh nötig._'

        parts.append(status_line)

        bot.send_message(chat_id, '\n'.join(parts))

        # Nächste Aufgabe direkt schicken bei LEARNING
        next_item = result.get('next_item')
        if next_item and progress.status == ModuleStatus.LEARNING:
            module = Ap2ModuleRepository.find_by_id(progress.module_id)
            cls._set_session(chat_id, {
                'module_id': str(progress.module_id),
                'item_id': str(next_item.item_id),
                'phase_label': 'Mastery',
            })
            bot.send_message(
                chat_id,
                f'➡️ *Nächste Aufgabe ({progress.streak_count}/3):*\n\n'
                f'{next_item.prompt[:1500]}',
            )

    # ============================================================
    # /stats
    # ============================================================

    @classmethod
    def _send_stats(cls, chat_id: int) -> None:
        bot = get_bot_client()
        user = TelegramLinkRepository.find_user_by_chat_id(chat_id)
        if not user:
            cls._send_welcome(chat_id, linked=False)
            return

        all_progress = Ap2ModuleProgressRepository.find_all_for_user(user['user_id'])
        n_mastered = sum(1 for p in all_progress if p.status == ModuleStatus.MASTERED)
        n_learning = sum(1 for p in all_progress if p.status == ModuleStatus.LEARNING)
        n_pending_recall = sum(1 for p in all_progress
                               if p.status == ModuleStatus.PENDING_RECALL)
        n_total = len(Ap2ModuleRepository.find_all_active())

        bot.send_message(
            chat_id,
            f'*Dein Fortschritt:*\n\n'
            f'✅ Mastered:        {n_mastered} / {n_total}\n'
            f'📚 In Arbeit:       {n_learning}\n'
            f'🟡 Same-Day-Recall: {n_pending_recall}\n\n'
            f'_/heute zeigt was du jetzt machen kannst._',
        )

    # ============================================================
    # /hilfe
    # ============================================================

    @classmethod
    def _send_help(cls, chat_id: int) -> None:
        bot = get_bot_client()
        bot.send_message(
            chat_id,
            '*Befehle:*\n\n'
            '/heute — was heute fällig ist\n'
            '/stats — dein Fortschritt\n'
            '/skip  — heutigen Spot-Check verschieben\n'
            '/pause — kurze Pause (1-3 Tage)\n'
            '/hilfe — diese Liste\n\n'
            '*Spielregeln:*\n'
            '• Mastery = 3× hintereinander ≥80% + Same-Day-Recall ≥80%\n'
            '• Spot-Checks danach: Tag 2, 4, 7, 12, 18\n'
            '• Komplexe Aufgaben (Builder/Diagramme) → Webapp-Link',
        )

    # ============================================================
    # Snooze
    # ============================================================

    @classmethod
    def _handle_snooze(cls, chat_id: int, mode: str) -> None:
        bot = get_bot_client()
        if mode == 'tomorrow':
            bot.send_message(chat_id, '🛌 _Okay, heute Pause. Bis morgen!_')
        else:
            bot.send_message(chat_id, '⏰ _Erinnere dich in 30 Minuten erneut._')

    # ============================================================
    # Session-State (Redis)
    # ============================================================

    @classmethod
    def _redis(cls):
        from app.core.bootstrap.extensions import redis_client
        return redis_client

    @classmethod
    def _set_session(cls, chat_id: int, data: dict) -> None:
        try:
            cls._redis().setex(
                SESSION_KEY.format(chat_id=chat_id),
                SESSION_TTL_SEC,
                json.dumps(data),
            )
        except Exception:
            logger.exception('Redis set_session fehlgeschlagen')

    @classmethod
    def _get_session(cls, chat_id: int) -> Optional[dict]:
        try:
            raw = cls._redis().get(SESSION_KEY.format(chat_id=chat_id))
            if raw:
                return json.loads(raw)
        except Exception:
            logger.exception('Redis get_session fehlgeschlagen')
        return None

    @classmethod
    def _clear_session(cls, chat_id: int) -> None:
        try:
            cls._redis().delete(SESSION_KEY.format(chat_id=chat_id))
        except Exception:
            logger.exception('Redis clear_session fehlgeschlagen')
