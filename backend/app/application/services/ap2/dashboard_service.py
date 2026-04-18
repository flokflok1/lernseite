"""
AP2 DashboardService — Liefert aggregierte Stats für Dashboard-View.

DDD Layer: Application. Keine SQL, kein Flask.
"""

from uuid import UUID

from app.infrastructure.persistence.repositories.ap2 import (
    Ap2AttemptRepository,
    Ap2TopicMasteryRepository,
    Ap2ReviewScheduleRepository,
)


# Thresholds
PASS_THRESHOLD_PCT = 50
COMFORTABLE_THRESHOLD_PCT = 65
WEAKNESS_THRESHOLD = 40.0


class Ap2DashboardService:
    """Aggregiert Dashboard-Daten aus mehreren Repositories."""

    @classmethod
    def get_user_stats(cls, user_id: UUID) -> dict:
        """Liefert vollständiges Dashboard-Payload.

        Returns:
          {
            overall: { attempts, correct, pct, pass_prediction, ... },
            bereich_stats: { PB2: {...}, PB3: {...}, WISO: {...} },
            bereich_pass: { PB2: bool|None, ... },
            topic_stats: [...],
            weaknesses: [...],
            review_queue_count: int,
          }
        """
        attempts_count = Ap2AttemptRepository.count_for_user(user_id)

        bereich_summary = Ap2TopicMasteryRepository.compute_bereich_summary(user_id)
        bereich_stats = cls._build_bereich_stats(bereich_summary)
        bereich_pass = cls._build_bereich_pass(bereich_stats)

        topic_rows = Ap2TopicMasteryRepository.find_all_for_user(user_id)
        topic_stats = [cls._serialize_topic(r) for r in topic_rows]

        weakness_rows = Ap2TopicMasteryRepository.find_weaknesses(
            user_id, WEAKNESS_THRESHOLD
        )
        weaknesses = [cls._serialize_weakness(r) for r in weakness_rows]

        regression_rows = Ap2TopicMasteryRepository.find_recent_regressions(
            user_id, limit=10
        )
        recent_regressions = [cls._serialize_regression(r) for r in regression_rows]

        overall = cls._build_overall(attempts_count, topic_rows, bereich_pass)
        review_count = Ap2ReviewScheduleRepository.count_due_for_user(user_id)

        return {
            'overall': overall,
            'bereich_stats': bereich_stats,
            'bereich_pass': bereich_pass,
            'topic_stats': topic_stats,
            'weaknesses': weaknesses,
            'recent_regressions': recent_regressions,
            'review_queue_count': review_count,
        }

    @staticmethod
    def _build_bereich_stats(summary: dict) -> dict:
        return {
            bereich: {
                'topic_count': s['topic_count'],
                'avg_mastery': s['avg_mastery'],
                'points_earned': s['points_earned'],
                'points_possible': s['points_possible'],
                'pct': round(
                    s['points_earned'] / s['points_possible'] * 100, 2
                ) if s['points_possible'] > 0 else 0,
            }
            for bereich, s in summary.items()
        }

    @staticmethod
    def _build_bereich_pass(bereich_stats: dict) -> dict:
        """Pro Bereich: True wenn >= 50% Punkte, False wenn darunter, None wenn kein Versuch."""
        out = {}
        for bereich in ('PB2', 'PB3', 'WISO'):
            s = bereich_stats.get(bereich)
            if s is None or s['points_possible'] == 0:
                out[bereich] = None
            else:
                out[bereich] = s['pct'] >= PASS_THRESHOLD_PCT
        return out

    @staticmethod
    def _build_overall(
        attempts_count: int,
        topic_rows: list[dict],
        bereich_pass: dict,
    ) -> dict:
        total_earned = sum(float(r['total_points_earned'] or 0) for r in topic_rows)
        total_possible = sum(float(r['total_points_possible'] or 0) for r in topic_rows)
        correct_count = sum(int(r['correct_count'] or 0) for r in topic_rows)
        overall_pct = round(total_earned / total_possible * 100, 2) if total_possible > 0 else 0

        # Prognose: alle bereiche >= 50% → bestanden
        pass_values = [p for p in bereich_pass.values() if p is not None]
        if not pass_values:
            prediction = 'unvollstaendig'
        elif all(pass_values) and overall_pct >= PASS_THRESHOLD_PCT:
            prediction = 'bestanden'
        else:
            prediction = 'gefaehrdet'

        return {
            'attempts': attempts_count,
            'correct': correct_count,
            'total_earned': total_earned,
            'total_possible': total_possible,
            'pct': overall_pct,
            'pass_prediction': prediction,
        }

    @staticmethod
    def _serialize_topic(r: dict) -> dict:
        return {
            'topic_slug': r['slug'],
            'topic_name': r['name_de'],
            'bereich': r['bereich'],
            'priority': r['priority'],
            'mastery_score': float(r['mastery_score']),
            'attempts_count': r['attempts_count'],
            'correct_count': r['correct_count'],
            'last_attempt_at': (
                r['last_attempt_at'].isoformat() if r['last_attempt_at'] else None
            ),
        }

    @staticmethod
    def _serialize_weakness(r: dict) -> dict:
        return {
            'topic_slug': r['slug'],
            'topic_name': r['name_de'],
            'bereich': r['bereich'],
            'priority': r['priority'],
            'mastery_score': float(r['mastery_score']),
            'attempts_count': r['attempts_count'],
            'gap': round(WEAKNESS_THRESHOLD - float(r['mastery_score']), 2),
        }

    @staticmethod
    def _serialize_regression(r: dict) -> dict:
        """Mini-Schwäche: Item heute schwächer als beim letzten Mal."""
        return {
            'item_id': str(r['item_id']),
            'topic_slug': r['topic_slug'],
            'topic_name': r['topic_name'],
            'item_type': r['item_type'],
            'item_prompt': r['item_prompt'][:120],   # gekürzt für Dashboard
            'last_pct': r['last_pct'],
            'prev_pct': r['prev_pct'],
            'regression_size': r['regression_size'],
            'last_attempt_at': (
                r['last_attempt_at'].isoformat() if r['last_attempt_at'] else None
            ),
        }
