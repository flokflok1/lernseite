"""
ModuleProgressService — Mastery-Loop + Spot-Check-Schedule für Diagramm-Module.

Bindet:
- Ap2ModuleRepository / Ap2ModuleProgressRepository (Persistence)
- Ap2LearningItemRepository (Pool-Items)
- Ap2EvaluationService (KI-Bewertung)

Fluss pro Modul:
1. start_module() → liefert Lehrblock + erstes Aufgabe-Item aus Pool
2. submit_answer(item_id, answer) → KI bewertet, Streak/Status aktualisiert
3. next_item() → nächstes Pool-Item (oder None wenn Mastered/Pending-Recall)

DDD Layer: Application. Keine SQL, kein Flask.
"""

import logging
import random
from typing import Optional
from uuid import UUID

from app.domain.models.ap2 import (
    Module, ModuleProgress, ModuleStatus, AttemptPhase, AttemptSource,
    ModuleAttemptLog, LearningItem, Phase,
    MASTERY_PASS_THRESHOLD,
)
from app.infrastructure.persistence.repositories.ap2 import (
    Ap2ModuleRepository, Ap2ModuleProgressRepository, Ap2LearningItemRepository,
)
from app.application.services.ap2.evaluation_service import Ap2EvaluationService

logger = logging.getLogger(__name__)


class ModuleNotAvailableError(Exception):
    """Modul ist gesperrt oder Cooldown aktiv."""


class ModulePoolEmptyError(Exception):
    """Keine Pool-Items mehr verfügbar (alle in used_item_ids)."""


class ModuleProgressService:
    """Verwaltet Modul-Fortschritt mit strenger Mastery-Logik."""

    # ============================================================
    # Public API
    # ============================================================

    @classmethod
    def get_or_init_progress(
        cls, user_id: UUID, module_id: UUID
    ) -> ModuleProgress:
        """Holt bestehenden Fortschritt oder erzeugt neuen.

        Neue Module starten in AVAILABLE wenn keine Voraussetzungen,
        sonst LOCKED.
        """
        existing = Ap2ModuleProgressRepository.find_by_user_module(
            user_id, module_id
        )
        if existing:
            return existing

        # Neu anlegen
        module = Ap2ModuleRepository.find_by_id(module_id)
        if not module:
            raise ValueError(f'Module not found: {module_id}')

        status = cls._compute_initial_status(user_id, module)
        new_progress = ModuleProgress(
            progress_id=UUID(int=0),  # Wird durch DB gesetzt
            user_id=user_id,
            module_id=module_id,
            status=status,
        )
        return Ap2ModuleProgressRepository.upsert(new_progress)

    @classmethod
    def start_module(
        cls, user_id: UUID, module_id: UUID
    ) -> tuple[ModuleProgress, Optional[LearningItem]]:
        """Startet ein Modul → setzt status auf LEARNING, liefert erstes Item.

        Returns: (progress, first_item) — first_item None wenn Pool leer.
        Raises: ModuleNotAvailableError wenn LOCKED oder Cooldown.
        """
        progress = cls.get_or_init_progress(user_id, module_id)

        if progress.status == ModuleStatus.LOCKED:
            raise ModuleNotAvailableError(
                f'Modul gesperrt — Voraussetzungen nicht erfüllt'
            )
        if progress.is_in_cooldown:
            raise ModuleNotAvailableError(
                f'Cooldown aktiv bis {progress.cooldown_until}'
            )

        # Bei AVAILABLE: zu LEARNING wechseln + Reset
        if progress.status == ModuleStatus.AVAILABLE:
            progress.status = ModuleStatus.LEARNING
            progress.streak_count = 0
            progress.total_attempts = 0
            progress.passed_attempts = 0
            progress.used_item_ids = []
            progress = Ap2ModuleProgressRepository.upsert(progress)

        # Bei REVIEW_FAILED: Refresh-Modus → LEARNING
        if progress.status == ModuleStatus.REVIEW_FAILED:
            progress.reset_for_relearn()
            progress = Ap2ModuleProgressRepository.upsert(progress)

        first_item = cls._pick_next_item(progress, use_in='mastery')
        return progress, first_item

    @classmethod
    def submit_answer(
        cls,
        user_id: UUID,
        module_id: UUID,
        item_id: UUID,
        user_answer: str,
        source: AttemptSource = AttemptSource.WEBAPP,
        stuetzrad_used: bool = False,
    ) -> dict:
        """Verarbeitet eine User-Antwort.

        Wenn ``stuetzrad_used=True``:
        - KI wird trotzdem aufgerufen (User hat geschrieben, soll Feedback bekommen)
        - Aber: kein Streak-Update, kein Fail-Zähler, nur Zähler für Stützrad-Nutzung
        - Item wird NICHT zu 'used' markiert (bleibt im Pool)

        Sonst (Stützrad aus):
        - Streng: ≥80% → kopf_serie_count++, Fail → count=0 + fail++, effective_target+
        - Module-Progress (Streak für Modul-Mastery) wird ebenfalls aktualisiert
        """
        progress = Ap2ModuleProgressRepository.find_by_user_module(
            user_id, module_id
        )
        if not progress:
            raise ModuleNotAvailableError('Kein aktiver Modul-Fortschritt')

        item = Ap2LearningItemRepository.find_by_id(item_id)
        if not item:
            raise ValueError(f'Item not found: {item_id}')

        # Phase aus Modul-Status ableiten
        phase = cls._derive_attempt_phase(progress)

        # KI-Bewertung (immer — auch bei Stützrad, damit User Feedback bekommt)
        try:
            pct, points_earned, feedback, model_used = Ap2EvaluationService.evaluate(
                item=item,
                phase=cls._map_to_evaluation_phase(item),
                answer_text=user_answer,
            )
        except Exception:
            logger.exception(
                'KI-Bewertung gescheitert für user=%s module=%s item=%s',
                user_id, module_id, item_id,
            )
            raise

        passed = pct >= MASTERY_PASS_THRESHOLD

        # Audit-Log (immer — auch bei Stützrad)
        Ap2ModuleProgressRepository.log_attempt(ModuleAttemptLog(
            attempt_log_id=UUID(int=0),
            user_id=user_id,
            module_id=module_id,
            item_id=item_id,
            attempt_phase=phase,
            source=source,
            user_answer=user_answer,
            score_pct=float(pct),
            passed=passed,
            feedback={
                'summary': feedback.summary,
                'correct': feedback.correct_aspects,
                'missing': feedback.missing_aspects,
                'partial': feedback.partial_aspects,
                'incorrect': feedback.incorrect_aspects,
                'suggestions': feedback.suggestions,
                'model': model_used,
                'stuetzrad_used': stuetzrad_used,
            },
        ))

        # Item-Skill (Stützrad-System) aktualisieren — ruhig auch bei Stützrad
        from app.infrastructure.persistence.repositories.ap2 import (
            Ap2UserPrefsRepository, Ap2ItemSkillRepository,
        )
        prefs = Ap2UserPrefsRepository.get_or_create(user_id)
        skill = Ap2ItemSkillRepository.get_or_init(
            user_id, item_id, initial_target=prefs.base_target,
        )
        skill.record_submission(
            passed=passed, score_pct=float(pct),
            stuetzrad_used=stuetzrad_used, prefs=prefs,
        )
        skill = Ap2ItemSkillRepository.upsert(skill)

        # Module-Level Streak NUR bei Stützrad-aus aktualisieren
        if not stuetzrad_used:
            progress.apply_attempt(float(pct), phase)
            if item_id not in progress.used_item_ids:
                progress.used_item_ids.append(item_id)
            progress = Ap2ModuleProgressRepository.upsert(progress)

            if progress.status == ModuleStatus.MASTERED:
                cls._unlock_dependent_modules(user_id, module_id)

        # Nächstes Item ermitteln (bei Stützrad das GLEICHE Item nochmal, sonst neues)
        next_item = None
        if stuetzrad_used:
            # User will das Item ggf. direkt nochmal ohne Stützrad — System bietet
            # standardmäßig ein anderes Pool-Item an, UI kann aber "Nochmal" zeigen
            next_item = cls._pick_next_item(progress, use_in='mastery')
        elif progress.status == ModuleStatus.LEARNING:
            next_item = cls._pick_next_item(progress, use_in='mastery')

        return {
            'pct': pct,
            'passed': passed,
            'points_earned': points_earned,
            'feedback': feedback,
            'progress': progress,
            'next_item': next_item,
            'model_used': model_used,
            'skill': skill,
            'stuetzrad_used': stuetzrad_used,
            'model_answer': item.model_answer if stuetzrad_used or not passed else None,
        }

    @classmethod
    def get_recall_item(
        cls, user_id: UUID, module_id: UUID
    ) -> Optional[LearningItem]:
        """Liefert ein Item für den Same-Day-Recall (anderes als bisher genutzt)."""
        progress = Ap2ModuleProgressRepository.find_by_user_module(
            user_id, module_id
        )
        if not progress or progress.status != ModuleStatus.PENDING_RECALL:
            return None
        return cls._pick_next_item(progress, use_in='mastery')

    @classmethod
    def get_spotcheck_item(
        cls, user_id: UUID, module_id: UUID
    ) -> Optional[LearningItem]:
        """Liefert ein Item für späteren Spot-Check (Tag 2/4/7/12/18)."""
        progress = Ap2ModuleProgressRepository.find_by_user_module(
            user_id, module_id
        )
        if not progress or progress.status not in (
            ModuleStatus.MASTERED, ModuleStatus.REVIEW_FAILED
        ):
            return None
        # Spot-Check zieht aus 'spotcheck' oder 'both'
        return cls._pick_next_item(progress, use_in='spotcheck')

    # ============================================================
    # Internal helpers
    # ============================================================

    @classmethod
    def _compute_initial_status(
        cls, user_id: UUID, module: Module
    ) -> ModuleStatus:
        """Wenn Voraussetzungen mastered → AVAILABLE, sonst LOCKED."""
        if not module.prerequisite_slugs:
            return ModuleStatus.AVAILABLE

        all_progress = Ap2ModuleProgressRepository.find_all_for_user(user_id)
        mastered_module_ids = {
            p.module_id for p in all_progress
            if p.status == ModuleStatus.MASTERED
        }

        for slug in module.prerequisite_slugs:
            req_module = Ap2ModuleRepository.find_by_slug(slug)
            if not req_module or req_module.module_id not in mastered_module_ids:
                return ModuleStatus.LOCKED
        return ModuleStatus.AVAILABLE

    @classmethod
    def _unlock_dependent_modules(
        cls, user_id: UUID, mastered_module_id: UUID
    ) -> None:
        """Module die diesen Modul-Slug als Voraussetzung haben → AVAILABLE."""
        mastered = Ap2ModuleRepository.find_by_id(mastered_module_id)
        if not mastered:
            return

        all_modules = Ap2ModuleRepository.find_all_active()
        all_progress = Ap2ModuleProgressRepository.find_all_for_user(user_id)
        all_mastered_ids = {
            p.module_id for p in all_progress
            if p.status == ModuleStatus.MASTERED
        }
        all_mastered_slugs = {
            m.slug for m in all_modules if m.module_id in all_mastered_ids
        }

        for module in all_modules:
            if mastered.slug not in module.prerequisite_slugs:
                continue
            # Prüfen ob ALLE Voraussetzungen jetzt erfüllt sind
            all_done = all(
                req in all_mastered_slugs for req in module.prerequisite_slugs
            )
            if not all_done:
                continue
            # Progress holen oder neu anlegen
            existing = Ap2ModuleProgressRepository.find_by_user_module(
                user_id, module.module_id
            )
            if existing and existing.status == ModuleStatus.LOCKED:
                existing.status = ModuleStatus.AVAILABLE
                Ap2ModuleProgressRepository.upsert(existing)
            elif not existing:
                Ap2ModuleProgressRepository.upsert(ModuleProgress(
                    progress_id=UUID(int=0),
                    user_id=user_id,
                    module_id=module.module_id,
                    status=ModuleStatus.AVAILABLE,
                ))

    @classmethod
    def _pick_next_item(
        cls, progress: ModuleProgress, use_in: str = 'mastery'
    ) -> Optional[LearningItem]:
        """Wählt nächstes Pool-Item — bevorzugt nicht-verwendete."""
        pool_ids = Ap2ModuleRepository.get_pool_item_ids(
            progress.module_id, use_in=use_in
        )
        if not pool_ids:
            return None

        used_set = set(progress.used_item_ids)
        unused = [iid for iid in pool_ids if iid not in used_set]

        if unused:
            chosen_id = random.choice(unused)
        else:
            # Pool erschöpft — wir cycle-en (used_items wird bei Mastery resettet)
            chosen_id = random.choice(pool_ids)

        return Ap2LearningItemRepository.find_by_id(chosen_id)

    @staticmethod
    def _derive_attempt_phase(progress: ModuleProgress) -> AttemptPhase:
        """Welche AttemptPhase gehört zu welchem Status?"""
        if progress.status == ModuleStatus.PENDING_RECALL:
            return AttemptPhase.RECALL
        if progress.status == ModuleStatus.MASTERED:
            return AttemptPhase.SPOTCHECK
        return AttemptPhase.MASTERY

    @staticmethod
    def _map_to_evaluation_phase(item: LearningItem) -> Phase:
        """Mappt ItemType → Phase für Ap2EvaluationService."""
        from app.domain.models.ap2 import ItemType
        if item.item_type == ItemType.BLURT:
            return Phase.BLURT
        if item.item_type == ItemType.CUED:
            return Phase.CUED
        return Phase.APPLICATION
