"""
AP2 Trainer — Module + Module Progress Domain Models.

Module = Lehreinheit (z.B. "IPv6-Konfiguration", "Organigramm lesen").
Jedes Modul hat einen Lehrblock + Pool von Aufgaben aus ap2_learning_items.

Mastery-Logik: 3× hintereinander ≥80% + Same-Day-Recall ≥80% = mastered.
Spot-Check-Schedule: Tag 1+4h, 2, 4, 7, 12, 18.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID


class ModuleStatus(str, Enum):
    """Status eines Moduls für einen User."""
    LOCKED = 'locked'                  # Voraussetzung-Module noch nicht mastered
    AVAILABLE = 'available'            # Bereit zum Starten
    LEARNING = 'learning'              # Im Mastery-Loop (3-Streak läuft)
    PENDING_RECALL = 'pending_recall'  # 3× geschafft, wartet auf Same-Day-Recall (4h)
    MASTERED = 'mastered'              # Vollständig durch + Recall bestanden
    REVIEW_FAILED = 'review_failed'    # Spot-Check < 80% — muss nachholen


class AttemptPhase(str, Enum):
    """Phase eines Modul-Versuchs."""
    MASTERY = 'mastery'        # Während 3-Streak-Aufbau
    RECALL = 'recall'          # Same-Day-Recall (4h-Marker)
    SPOTCHECK = 'spotcheck'    # Spätere Wiederholung (Tag 2/4/7/...)


class AttemptSource(str, Enum):
    """Wo der User die Aufgabe beantwortet hat."""
    WEBAPP = 'webapp'
    TELEGRAM = 'telegram'


# Mastery-Konstanten — die Regeln des Systems
MASTERY_PASS_THRESHOLD = 80.0          # Score in Prozent
MASTERY_STREAK_REQUIRED = 3            # 3× hintereinander ≥80%
SAME_DAY_RECALL_DELAY_HOURS = 4        # 4h nach 3-Streak
COOLDOWN_AFTER_FAILURES_MIN = 30       # 30 min Cooldown nach 3× Scheitern
MAX_FAILURES_BEFORE_COOLDOWN = 3       # Anzahl Failures bis Cooldown

# Spot-Check-Schedule (Stage → Tage nach Mastered)
SPOTCHECK_SCHEDULE_DAYS = [2, 4, 7, 12, 18]
# Nach Stage 4 (Tag 18) verdoppelt sich das Intervall pro weiterer erfolgreicher Stage


@dataclass
class Module:
    """Lehreinheit (Diagramm-Typ, Themenfeld)."""

    module_id: UUID
    slug: str                              # 'ipv6-konfiguration'
    name_de: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    theory_markdown: Optional[str] = None  # Lehrblock (Markdown), wird vor Aufgaben gezeigt
    estimated_min: int = 12
    difficulty: int = 3                    # 1-5
    sort_order: int = 0
    prerequisite_slugs: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ModuleProgress:
    """User-spezifischer Fortschritt zu einem Modul."""

    progress_id: UUID
    user_id: UUID
    module_id: UUID
    status: ModuleStatus = ModuleStatus.LOCKED

    # Mastery-Loop State
    streak_count: int = 0                  # Aktuelle Streak ≥80%
    total_attempts: int = 0                # Aufgaben in dieser Mastery-Session
    passed_attempts: int = 0               # Erfolgreiche seit Modul-Start
    cooldown_until: Optional[datetime] = None

    # Same-Day-Recall
    same_day_recall_due_at: Optional[datetime] = None
    same_day_recall_passed: Optional[bool] = None

    # Mastery-Erfolg
    mastered_at: Optional[datetime] = None

    # Spot-Check-Schedule
    spotcheck_stage: int = 0
    next_spotcheck_at: Optional[datetime] = None
    last_spotcheck_at: Optional[datetime] = None
    last_spotcheck_score: Optional[float] = None

    # Anti-Wiederholung: bereits genutzte Items in aktueller Session
    used_item_ids: list[UUID] = field(default_factory=list)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ==================== Domain-Logik ====================

    @property
    def is_in_cooldown(self) -> bool:
        """Cooldown nach 3× Scheitern aktiv?"""
        return self.cooldown_until is not None and datetime.utcnow() < self.cooldown_until

    @property
    def is_recall_overdue(self) -> bool:
        """Same-Day-Recall fällig (>4h vergangen)?"""
        return (
            self.status == ModuleStatus.PENDING_RECALL
            and self.same_day_recall_due_at is not None
            and datetime.utcnow() >= self.same_day_recall_due_at
        )

    @property
    def is_spotcheck_due(self) -> bool:
        """Spot-Check fällig (Mastered + next_spotcheck_at <= jetzt)?"""
        return (
            self.status == ModuleStatus.MASTERED
            and self.next_spotcheck_at is not None
            and datetime.utcnow() >= self.next_spotcheck_at
        )

    def apply_attempt(self, score_pct: float, phase: AttemptPhase) -> 'ModuleProgress':
        """
        Verarbeitet einen Versuch und aktualisiert State.

        Logik:
        - MASTERY-Phase: jedes ≥80% erhöht streak_count; <80% setzt Streak auf 0
        - 3-Streak erreicht → status PENDING_RECALL, same_day_recall_due_at = jetzt + 4h
        - RECALL-Phase: ≥80% → MASTERED + spotcheck_stage = 0; <80% → REVIEW_FAILED + Reset
        - SPOTCHECK-Phase: ≥80% → spotcheck_stage++; <80% → REVIEW_FAILED + zurück zu LEARNING
        """
        passed = score_pct >= MASTERY_PASS_THRESHOLD
        self.total_attempts += 1
        if passed:
            self.passed_attempts += 1

        if phase == AttemptPhase.MASTERY:
            if passed:
                self.streak_count += 1
                if self.streak_count >= MASTERY_STREAK_REQUIRED:
                    # 3-Streak erreicht → warte auf Same-Day-Recall
                    self.status = ModuleStatus.PENDING_RECALL
                    self.same_day_recall_due_at = (
                        datetime.utcnow() + timedelta(hours=SAME_DAY_RECALL_DELAY_HOURS)
                    )
            else:
                # Streak zurücksetzen — User muss neu 3 in Folge schaffen
                self.streak_count = 0
                # Wenn 3× scheitern: Cooldown
                failed_in_session = self.total_attempts - self.passed_attempts
                if failed_in_session >= MAX_FAILURES_BEFORE_COOLDOWN:
                    self.cooldown_until = (
                        datetime.utcnow() + timedelta(minutes=COOLDOWN_AFTER_FAILURES_MIN)
                    )

        elif phase == AttemptPhase.RECALL:
            if passed:
                self.status = ModuleStatus.MASTERED
                self.same_day_recall_passed = True
                self.mastered_at = datetime.utcnow()
                self.spotcheck_stage = 0
                self.next_spotcheck_at = self._compute_next_spotcheck()
            else:
                # Recall durchgefallen — zurück zum Mastery-Loop
                self.status = ModuleStatus.LEARNING
                self.same_day_recall_passed = False
                self.streak_count = 0
                self.same_day_recall_due_at = None

        elif phase == AttemptPhase.SPOTCHECK:
            self.last_spotcheck_at = datetime.utcnow()
            self.last_spotcheck_score = score_pct
            if passed:
                self.spotcheck_stage += 1
                self.next_spotcheck_at = self._compute_next_spotcheck()
            else:
                # Spot-Check durchgefallen — zurück zu LEARNING (Refresh nötig)
                self.status = ModuleStatus.REVIEW_FAILED
                self.streak_count = 0
                self.next_spotcheck_at = None

        return self

    def _compute_next_spotcheck(self) -> datetime:
        """Berechnet next_spotcheck_at basierend auf aktueller Stage."""
        if self.spotcheck_stage < len(SPOTCHECK_SCHEDULE_DAYS):
            days = SPOTCHECK_SCHEDULE_DAYS[self.spotcheck_stage]
        else:
            # Nach Stage 4 verdoppelt sich das Intervall (18 → 36 → 72 ...)
            base = SPOTCHECK_SCHEDULE_DAYS[-1]
            multiplier = 2 ** (self.spotcheck_stage - len(SPOTCHECK_SCHEDULE_DAYS) + 1)
            days = base * multiplier
        return datetime.utcnow() + timedelta(days=days)

    def reset_for_relearn(self) -> 'ModuleProgress':
        """Setzt Modul zurück auf LEARNING (z.B. nach REVIEW_FAILED Refresh)."""
        self.status = ModuleStatus.LEARNING
        self.streak_count = 0
        self.same_day_recall_due_at = None
        self.same_day_recall_passed = None
        return self


@dataclass
class ModuleAttemptLog:
    """Audit-Trail eines einzelnen Versuchs (Mastery/Recall/Spotcheck)."""
    attempt_log_id: UUID
    user_id: UUID
    module_id: UUID
    item_id: UUID
    attempt_phase: AttemptPhase
    source: AttemptSource
    user_answer: str
    score_pct: float
    passed: bool
    feedback: Optional[dict] = None
    created_at: Optional[datetime] = None
