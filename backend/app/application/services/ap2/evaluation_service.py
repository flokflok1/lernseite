"""
AP2 EvaluationService — IHK-Prüfer-KI-Bewertung.

Bewertet User-Antwort auf ein LearningItem. Phase bestimmt Bewertungslogik:
- BLURT:       Vollständigkeits-Check gegen expected_answer_structure
- CUED:        Einzelfrage gegen model_answer + grading_criteria
- APPLICATION: wie CUED + Hotspot-Bewertung wenn Anlage

DDD Layer: Application. Nutzt AIAdapter (Infrastructure), nur Domain-Models
+ Repositories. Keine SQL, kein Flask. Fehler propagieren (G08) — der
API-Layer handhabt HTTP-Status.
"""

import json
import logging
import re
from typing import Optional

from app.domain.models.ap2 import (
    LearningItem, Phase, AttemptFeedback, Hotspot, Anlage,
)
from app.infrastructure.ai.adapter import AIAdapter

logger = logging.getLogger(__name__)

# Module-level regex für Numeric-Check (kein try/except nötig)
_FLOAT_RE = re.compile(r'^-?\d+([.,]\d+)?$')

IHK_PRUEFER_SYSTEM_PROMPT = """Du bist ein erfahrener IHK-Prüfer für die
Abschlussprüfung Teil 2 der Fachinformatiker Systemintegration (FA 235,
Baden-Württemberg).

AUFGABE: Bewerte die Antwort eines Prüflings. Gib Prozent (0-100) und
strukturiertes Feedback. Sei streng aber fair, wie ein echter Prüfer.

KRITERIEN:
- Fachliche Korrektheit (wichtigstes)
- Fachbegriffe korrekt verwendet
- Vollständigkeit (alle geforderten Aspekte)
- Rechenweg bei Berechnungen
- Fachsprache: nicht umgangssprachlich

ANTWORTFORMAT (STRIKT JSON, kein anderer Text):
{
  "pct": 0-100,
  "summary": "1-2 Sätze",
  "correct_aspects": ["..."],
  "missing_aspects": ["..."],
  "partial_aspects": ["..."],
  "incorrect_aspects": ["..."],
  "suggestions": ["..."]
}"""


class Ap2EvaluationService:
    """Bewertet User-Antworten via IHK-Prüfer-KI.

    Adapter wird pro Aufruf instantiiert (Provider/Model aus DB-Config,
    kein Hardcoding G07). Fehler werden geloggt und propagiert (G08).
    """

    @classmethod
    def evaluate(
        cls,
        item: LearningItem,
        phase: Phase,
        answer_text: str,
        anlage: Optional[Anlage] = None,
        answer_hotspots: Optional[dict] = None,
    ) -> tuple[int, float, AttemptFeedback, Optional[str]]:
        """Bewertet eine Antwort.

        Returns: (pct, points_earned, feedback, ai_model_used)
        Raises: AIProviderError, json.JSONDecodeError — propagiert an
                API-Layer für HTTP-Statusbehandlung.
        """
        user_prompt = cls._build_user_prompt(item, phase, answer_text, anlage)
        # Task-spezifisches Modell aus Admin-Config holen ('grading' = Bewertung)
        from app.infrastructure.ai.task_model_resolver import resolve_model_for_task
        try:
            provider, model = resolve_model_for_task('grading')
            adapter = AIAdapter(provider=provider, model=model)
        except Exception:
            logger.warning('grading-Task nicht konfiguriert, fallback auf default')
            adapter = AIAdapter()

        try:
            response = adapter.send_messages(
                messages=[
                    {'role': 'system', 'content': IHK_PRUEFER_SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_prompt},
                ],
                temperature=0.2,
                max_tokens=2000,
            )
            content = response.get('content', '').strip()
            parsed = cls._parse_json_response(content)
        except Exception:
            logger.exception(
                'AP2 evaluation failed for item=%s phase=%s',
                item.item_id, phase.value,
            )
            raise

        pct = max(0, min(100, int(parsed.get('pct', 0))))

        feedback = AttemptFeedback(
            summary=parsed.get('summary', ''),
            correct_aspects=parsed.get('correct_aspects', []),
            missing_aspects=parsed.get('missing_aspects', []),
            partial_aspects=parsed.get('partial_aspects', []),
            incorrect_aspects=parsed.get('incorrect_aspects', []),
            suggestions=parsed.get('suggestions', []),
        )

        hotspot_bonus = 0.0
        if phase == Phase.APPLICATION and anlage and answer_hotspots:
            hotspot_bonus = cls._grade_hotspots(anlage.hotspots, answer_hotspots)

        points_earned = round(item.points * pct / 100 + hotspot_bonus, 2)
        max_points = item.points + (anlage.total_points if anlage else 0)
        points_earned = min(points_earned, max_points)

        return pct, points_earned, feedback, adapter.model

    @staticmethod
    def _build_user_prompt(
        item: LearningItem,
        phase: Phase,
        answer_text: str,
        anlage: Optional[Anlage],
    ) -> str:
        """Baut Prompt für IHK-Prüfer-KI, differenziert nach Phase."""
        parts = [
            f'PHASE: {phase.value}',
            '',
            f'FRAGE/AUFGABE ({item.points} Punkte):',
            item.prompt,
        ]

        if anlage:
            parts += ['', f'ANLAGE: {anlage.title}']
            if anlage.description:
                parts += [anlage.description]

        if item.expected_answer_structure:
            parts += [
                '',
                'ERWARTETE STRUKTUR:',
                json.dumps(item.expected_answer_structure, ensure_ascii=False, indent=2),
            ]

        if item.grading_criteria:
            parts += ['', 'BEWERTUNGSKRITERIEN:']
            for c in item.grading_criteria:
                marker = '[PFLICHT]' if c.required else ''
                parts.append(
                    f'  - {c.criterion} (Gewicht {c.weight}) {marker}: {c.description}'
                )

        parts += [
            '', 'MUSTERLÖSUNG:', item.model_answer,
            '', 'PRÜFLING-ANTWORT:', answer_text or '(leer)',
            '', 'Bewerte jetzt. NUR JSON zurück.',
        ]
        return '\n'.join(parts)

    @staticmethod
    def _parse_json_response(content: str) -> dict:
        """Extrahiert JSON aus KI-Antwort, auch wenn in Markdown-Fence.

        Raises: json.JSONDecodeError wenn Content kein gültiges JSON ist —
        der Aufrufer fängt und loggt.
        """
        if '```json' in content:
            content = content.split('```json', 1)[1]
        if '```' in content:
            content = content.split('```', 1)[0]
        return json.loads(content.strip())

    @staticmethod
    def _grade_hotspots(
        expected: list[Hotspot],
        submitted: dict,
    ) -> float:
        """Vergleicht User-Hotspot-Werte mit korrekten Antworten.

        Returns: Summe der erreichten Hotspot-Punkte.
        """
        earned = 0.0
        for hotspot in expected:
            user_val = (submitted.get(hotspot.hotspot_id) or '').strip()
            if not user_val:
                continue
            if Ap2EvaluationService._matches_any(
                user_val, hotspot.correct_answers, hotspot.tolerance
            ):
                earned += hotspot.points
        return earned

    @staticmethod
    def _matches_any(user_val: str, correct_answers: list[str], tolerance: str) -> bool:
        """Toleranter String-Vergleich."""
        if not correct_answers:
            return False
        u = user_val.strip()
        if tolerance == 'case-insensitive':
            ul = u.lower()
            return any(ul == c.strip().lower() for c in correct_answers)
        if tolerance == 'numeric':
            return Ap2EvaluationService._matches_numeric(u, correct_answers)
        if tolerance in ('ip-address', 'subnet-mask'):
            return Ap2EvaluationService._matches_ip(u, correct_answers)
        # default: exact
        return any(u == c.strip() for c in correct_answers)

    @staticmethod
    def _matches_numeric(user_val: str, correct_answers: list[str]) -> bool:
        """Numerischer Vergleich mit Komma/Punkt-Toleranz.

        Nutzt Regex-Vorprüfung statt try/except — User-Input der kein
        Numeric ist zählt einfach als "kein Match".
        """
        if not _FLOAT_RE.match(user_val.strip()):
            return False
        uf = float(user_val.strip().replace(',', '.'))
        for c in correct_answers:
            c_str = c.strip()
            if _FLOAT_RE.match(c_str):
                cf = float(c_str.replace(',', '.'))
                if abs(uf - cf) < 0.01:
                    return True
        return False

    @staticmethod
    def _matches_ip(user_val: str, correct_answers: list[str]) -> bool:
        """IP-Adress-Vergleich: führende Nullen ignorieren."""
        parts = user_val.split('.')
        if len(parts) != 4 or not all(p.isdigit() for p in parts):
            return False
        normalized = '.'.join(str(int(p)) for p in parts)
        return any(normalized == c.strip() for c in correct_answers)
