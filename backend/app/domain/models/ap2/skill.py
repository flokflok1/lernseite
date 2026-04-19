"""
AP2 Trainer — User Learning Prefs + Item Skill Domain Models.

Pascal's "Stützrad"-Lernsystem:
- Pro User: global konfigurierbare Präferenzen (Basis-Ziel, Recovery-Verhalten, ...).
- Pro User pro Item: Kopf-Serie-Counter, Fails, effektives Ziel, Stützrad-Zähler.
- Recovery-Logik adaptiv: Fehler erhöhen das Ziel, bewältigtes Item = Ziel erreicht.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


# Konstanten
ABS_MIN_TARGET = 1
ABS_MAX_TARGET = 20
DEFAULT_BASE_TARGET = 3
DEFAULT_MAX_TARGET = 10
SOFT_FAIL_THRESHOLD = 2          # Ab diesem Fail-Count wird Ziel erhöht
AUTO_STUETZRAD_THRESHOLD = 3     # Ab diesem Fail-Count wird Stützrad empfohlen
PAUSE_HINT_THRESHOLD = 5         # Ab diesem Fail-Count wird Pause empfohlen


class RecoveryMode(str, Enum):
    """Wie das Ziel bei Fehlern erhöht wird."""
    PLUS_ONE = 'plus_one'          # +1 pro Fehler (sanft)
    PLUS_TWO = 'plus_two'          # +2 pro Fehler (normal)
    MULTIPLY_1_5 = 'multiply_1_5'  # × 1.5 (hart)


class StuetzradDefault(str, Enum):
    """Default-Modus fürs Stützrad beim Öffnen eines Items."""
    OFF = 'off'                    # nie auto an
    PER_ITEM = 'per_item'          # User entscheidet jedes Mal
    FIRST_TWO_ON = 'first_two_on'  # erste 2 Versuche auto AN


class MasteryStrictness(str, Enum):
    """Wie streng ist Modul-Mastery?"""
    EXPRESS = 'express'    # 80% der Items bewältigt
    STANDARD = 'standard'  # 100% Items bewältigt
    STRICT = 'strict'      # 100% + Same-Day-Recall (3 Zufalls ≥80%, Stützrad aus)


@dataclass
class UserLearningPrefs:
    """Globale Lern-Einstellungen pro User."""
    user_id: UUID
    base_target: int = DEFAULT_BASE_TARGET
    max_target: int = DEFAULT_MAX_TARGET
    recovery_mode: RecoveryMode = RecoveryMode.PLUS_TWO
    stuetzrad_default: StuetzradDefault = StuetzradDefault.PER_ITEM
    mastery_strictness: MasteryStrictness = MasteryStrictness.STANDARD
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def clamp_target(self, raw: int) -> int:
        """Sorge dass Ziel in [base_target, max_target] bleibt."""
        return max(self.base_target, min(raw, self.max_target))


@dataclass
class ItemSkill:
    """Pro User pro Item: Fortschritt im Stützrad-Mastery-Loop."""
    user_id: UUID
    item_id: UUID
    kopf_serie_count: int = 0
    fail_count: int = 0
    effective_target: int = DEFAULT_BASE_TARGET
    total_attempts: int = 0
    stuetzrad_uses: int = 0
    is_mastered: bool = False
    mastered_at: Optional[datetime] = None
    snoozed_until: Optional[datetime] = None
    last_attempt_at: Optional[datetime] = None
    last_score_pct: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ==================== Domain-Logik ====================

    @property
    def is_snoozed(self) -> bool:
        return (
            self.snoozed_until is not None
            and self.snoozed_until > datetime.utcnow()
        )

    @property
    def is_in_recovery(self) -> bool:
        return self.fail_count >= SOFT_FAIL_THRESHOLD

    @property
    def should_suggest_stuetzrad(self) -> bool:
        """Ab 3 Fails schlägt UI Stützrad vor."""
        return self.fail_count >= AUTO_STUETZRAD_THRESHOLD

    @property
    def should_suggest_pause(self) -> bool:
        """Ab 5 Fails schlägt UI Pause vor."""
        return self.fail_count >= PAUSE_HINT_THRESHOLD

    def record_stuetzrad_use(self) -> 'ItemSkill':
        """Stützrad wurde benutzt — kein Scoring, nur Zähler."""
        self.stuetzrad_uses += 1
        self.last_attempt_at = datetime.utcnow()
        return self

    def record_submission(
        self,
        passed: bool,
        score_pct: float,
        stuetzrad_used: bool,
        prefs: UserLearningPrefs,
    ) -> 'ItemSkill':
        """
        Wendet einen Versuch auf den Skill an.

        Mit Stützrad-AN: nur last_attempt_at + stuetzrad_uses erhöhen,
        keine Kopf-Serie/Fail-Änderung.

        Mit Stützrad-AUS:
        - passed (≥80%): kopf_serie_count += 1 (sanfter -1 bei einzelnem
          Ausrutscher ist hier NICHT, das ist im Service-Layer als History-Check)
        - !passed: fail_count += 1; kopf_serie_count = 0; effective_target
          wird je nach recovery_mode erhöht (aber max_target capped).
        - Ziel erreicht: is_mastered = True, mastered_at = now
        """
        self.total_attempts += 1
        self.last_attempt_at = datetime.utcnow()
        self.last_score_pct = float(score_pct)

        if stuetzrad_used:
            self.stuetzrad_uses += 1
            return self

        if passed:
            self.kopf_serie_count += 1
            if self.kopf_serie_count >= self.effective_target:
                self.is_mastered = True
                self.mastered_at = datetime.utcnow()
        else:
            self.fail_count += 1
            self.kopf_serie_count = 0
            self.effective_target = self._compute_effective_target(prefs)

        return self

    def record_soft_miss(self, prefs: UserLearningPrefs) -> 'ItemSkill':
        """Alternative bei einzelnem Fail (Service-Layer entscheidet):
        kopf_serie_count -= 1 (min 0), kein fail_count++."""
        if self.kopf_serie_count > 0:
            self.kopf_serie_count -= 1
        return self

    def _compute_effective_target(self, prefs: UserLearningPrefs) -> int:
        """Berechnet neues effective_target basierend auf fail_count."""
        if self.fail_count < SOFT_FAIL_THRESHOLD:
            return prefs.base_target
        # Recovery-Increments basierend auf Mode
        overflow = self.fail_count - SOFT_FAIL_THRESHOLD + 1
        if prefs.recovery_mode == RecoveryMode.PLUS_ONE:
            raw = prefs.base_target + overflow
        elif prefs.recovery_mode == RecoveryMode.MULTIPLY_1_5:
            raw = int(round(prefs.base_target * (1.5 ** overflow)))
        else:  # PLUS_TWO (default)
            raw = prefs.base_target + overflow * 2
        return prefs.clamp_target(raw)

    def snooze(self, hours: int = 24) -> 'ItemSkill':
        """Item wird für N Stunden aus Pool ausgeblendet."""
        from datetime import timedelta
        self.snoozed_until = datetime.utcnow() + timedelta(hours=hours)
        return self

    def extra_round(self) -> 'ItemSkill':
        """User will nach Mastered nochmal üben — +1 zum Ziel, is_mastered=False."""
        if self.is_mastered:
            self.is_mastered = False
            self.mastered_at = None
            self.effective_target += 1
        return self
