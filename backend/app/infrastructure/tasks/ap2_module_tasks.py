"""
Celery-Tasks für AP2-Modul-Trainer + Telegram-Pings.

Tasks:
- send_due_spotchecks    — alle 30 min: User mit fälligen Spot-Checks pingen
- send_due_recalls       — alle 5 min:  User mit fälligen Same-Day-Recalls pingen
- daily_morning_summary  — täglich 09:00: Tagesübersicht (was heute ansteht)

Celery Beat-Schedule wird in extensions.py registriert.

DDD: Infrastructure. Nutzt Application-Services + Domain-Repositories.
"""

import logging

from celery import shared_task

from app.core.bootstrap.extensions import celery as celery_app
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2ModuleRepository, Ap2ModuleProgressRepository,
)
from app.infrastructure.persistence.repositories.user import (
    TelegramLinkRepository,
)
from app.infrastructure.telegram import (
    get_bot_client, inline_keyboard, callback_button, TelegramApiError,
)
from app.domain.models.ap2 import ModuleStatus

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='ap2.send_due_spotchecks',
                 max_retries=2, default_retry_delay=60)
def send_due_spotchecks(self):
    """Findet alle User mit fälligen Spot-Checks und pingt sie via Telegram."""
    try:
        due = Ap2ModuleProgressRepository.find_due_spotchecks()
    except Exception:
        logger.exception('find_due_spotchecks fehlgeschlagen')
        raise self.retry(countdown=60)

    # Gruppiere nach user_id
    by_user: dict = {}
    for p in due:
        by_user.setdefault(p.user_id, []).append(p)

    sent = 0
    for user_id, progresses in by_user.items():
        chat_id = TelegramLinkRepository.get_chat_id(user_id)
        if not chat_id:
            continue
        if _send_spotcheck_summary(chat_id, progresses):
            sent += 1

    logger.info('send_due_spotchecks: %d users pinged', sent)
    return {'pinged_users': sent, 'total_due': len(due)}


@celery_app.task(bind=True, name='ap2.send_due_recalls',
                 max_retries=2, default_retry_delay=30)
def send_due_recalls(self):
    """Findet alle User mit fälligen Same-Day-Recalls (4h-Marker)."""
    try:
        due = Ap2ModuleProgressRepository.find_due_recalls()
    except Exception:
        logger.exception('find_due_recalls fehlgeschlagen')
        raise self.retry(countdown=30)

    sent = 0
    for p in due:
        chat_id = TelegramLinkRepository.get_chat_id(p.user_id)
        if not chat_id:
            continue
        module = Ap2ModuleRepository.find_by_id(p.module_id)
        if not module:
            continue
        try:
            _send_recall_invitation(chat_id, p, module)
            sent += 1
        except TelegramApiError:
            logger.exception('Telegram-Send fehlgeschlagen user=%s module=%s',
                             p.user_id, p.module_id)

    logger.info('send_due_recalls: %d recalls sent', sent)
    return {'sent': sent, 'total_due': len(due)}


@celery_app.task(bind=True, name='ap2.daily_morning_summary')
def daily_morning_summary(self):
    """09:00 morgens: Tagesübersicht an alle aktiven User."""
    linked = TelegramLinkRepository.list_all_linked_users()
    sent = 0
    for u in linked:
        try:
            chat_id = int(u['telegram_chat_id'])
            user_id = u['user_id']
            recalls = [p for p in
                       Ap2ModuleProgressRepository.find_all_for_user(user_id)
                       if p.is_recall_overdue]
            spotchecks = Ap2ModuleProgressRepository.find_due_spotchecks(user_id)
            if not recalls and not spotchecks:
                continue
            _send_morning_summary(chat_id, recalls + spotchecks)
            sent += 1
        except Exception:
            logger.exception('daily_morning_summary fehlgeschlagen user=%s',
                             u.get('user_id'))

    logger.info('daily_morning_summary: %d users notified', sent)
    return {'notified': sent}


# ============================================================
# Helpers
# ============================================================

def _send_spotcheck_summary(chat_id: int, progresses: list) -> bool:
    bot = get_bot_client()
    lines = [f'🔄 *{len(progresses)} Spot-Check{"s" if len(progresses) > 1 else ""} fällig*\n']
    rows = []
    for p in progresses:
        module = Ap2ModuleRepository.find_by_id(p.module_id)
        if not module:
            continue
        lines.append(f'• {module.name_de}')
        rows.append([callback_button(
            f'▶ {module.name_de[:30]}',
            f'spotcheck:start:{p.module_id}',
        )])
    if not rows:
        return False
    rows.append([
        callback_button('⏰ In 30 min', 'snooze:30m'),
        callback_button('🛌 Heute nicht', 'snooze:tomorrow'),
    ])
    try:
        bot.send_message(chat_id, '\n'.join(lines),
                         reply_markup=inline_keyboard(rows))
        return True
    except TelegramApiError:
        logger.exception('spotcheck-summary an chat=%s fehlgeschlagen', chat_id)
        return False


def _send_recall_invitation(chat_id: int, progress, module) -> None:
    bot = get_bot_client()
    bot.send_message(
        chat_id,
        f'🟡 *Same-Day-Recall: {module.name_de}*\n\n'
        f'Vor 4h hast du das Modul abgeschlossen. Jetzt prüfen wir kurz '
        f'ob es wirklich sitzt — eine Aufgabe, ca. 1 Min.\n\n'
        f'_Bei ≥80% wird das Modul mastered und du kommst zum nächsten._',
        reply_markup=inline_keyboard([[
            callback_button(f'▶ Recall jetzt', f'spotcheck:start:{module.module_id}'),
            callback_button('⏰ In 30 min', 'snooze:30m'),
        ]]),
    )


def _send_morning_summary(chat_id: int, all_due: list) -> None:
    bot = get_bot_client()
    n = len(all_due)
    bot.send_message(
        chat_id,
        f'☀️ *Guten Morgen!*\n\n'
        f'Heute fällig: *{n} Spot-Check{"s" if n > 1 else ""}* '
        f'(~{n} Min Aufwand).\n\n'
        f'Tippe /heute für die Liste oder klick:',
        reply_markup=inline_keyboard([
            [callback_button('▶ Jetzt starten', 'help')],
            [callback_button('⏰ Mittag', 'snooze:30m'),
             callback_button('🛌 Heute nicht', 'snooze:tomorrow')],
        ]),
    )
