"""TopicHierarchyService -- AI-powered topic clustering.

Reads all distinct topics from exam questions, sends them to AI
to organize into a hierarchy, and saves the result.
"""
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Maximum 12-15 root categories for a clean dashboard
_MAX_ROOT_CATEGORIES = 15


class TopicHierarchyService:
    """Orchestrates AI-based topic hierarchy generation."""

    @staticmethod
    def get_all_topics_with_counts() -> List[Dict[str, Any]]:
        """Get all distinct topics from exam questions with counts."""
        from app.infrastructure.persistence.repositories.exams.topic_nodes import (
            TopicNodeRepository,
        )
        return TopicNodeRepository.find_all_topics_with_counts()

    @staticmethod
    def auto_cluster() -> Dict[str, Any]:
        """Run AI to organize all topics into a hierarchy.

        Returns: {root_count, total_nodes, roots: [...]}
        """
        topics_with_counts = TopicHierarchyService.get_all_topics_with_counts()
        if not topics_with_counts:
            return {'root_count': 0, 'total_nodes': 0, 'roots': []}

        topic_list = [f"{t['topic']} ({t['cnt']})" for t in topics_with_counts]

        hierarchy = TopicHierarchyService._ask_ai_for_hierarchy(topic_list)
        if not hierarchy:
            logger.error("AI returned empty hierarchy")
            return {'root_count': 0, 'total_nodes': 0, 'roots': []}

        saved = TopicHierarchyService._save_hierarchy(hierarchy)
        return saved

    @staticmethod
    def _ask_ai_for_hierarchy(
        topic_list: List[str],
    ) -> Optional[List[Dict]]:
        """Ask AI to organize topics into a tree."""
        from app.infrastructure.ai.adapter import AIAdapter

        topics_text = '\n'.join(topic_list)

        prompt = (
            f"Du bist ein IHK-Pruefungsexperte fuer Fachinformatiker (AP1).\n"
            f"Ordne diese {len(topic_list)} Topics in eine saubere Hierarchie.\n\n"
            f"REGELN:\n"
            f"1. Erstelle 8-{_MAX_ROOT_CATEGORIES} Oberkategorien (Root-Topics)\n"
            f"2. Jedes Topic MUSS genau einer Oberkategorie zugeordnet werden\n"
            f"3. Oberkategorien orientieren sich an IHK-Pruefungsrahmen:\n"
            f"   - Netzwerktechnik, IT-Sicherheit, Datenbanken, Programmierung,\n"
            f"   - Wirtschaft/BWL, Recht, Rechnungswesen, Projektmanagement, etc.\n"
            f"4. Synonyme und Duplikate unter das gleiche Parent\n"
            f"   (z.B. ipv4+ipv6+ip_adresse -> netzwerk)\n"
            f"5. display_name in DE und EN fuer jedes Topic\n"
            f"6. Behalte die originalen topic_keys exakt bei (keine Umbenennung!)\n"
            f"7. Sortiere nach Relevanz (meiste Fragen zuerst)\n\n"
            f"TOPICS (mit Fragenanzahl):\n{topics_text}\n\n"
            "Antworte NUR als JSON-Array. Format:\n"
            "[\n"
            '  {\n'
            '    "topic_key": "netzwerk",\n'
            '    "display_name": {"de": "Netzwerktechnik", "en": "Networking"},\n'
            '    "children": [\n'
            '      {"topic_key": "ipv4", '
            '"display_name": {"de": "IPv4-Adressierung", "en": "IPv4 Addressing"}},\n'
            '      {"topic_key": "routing", '
            '"display_name": {"de": "Routing", "en": "Routing"}}\n'
            '    ]\n'
            '  },\n'
            '  ...\n'
            ']\n\n'
            f"WICHTIG: JEDES der {len(topic_list)} Topics muss in der Antwort "
            f"vorkommen -- entweder als Root oder als Child. Keines darf fehlen."
        )

        try:
            from app.infrastructure.ai.task_model_resolver import resolve_model_for_task
            provider, model = resolve_model_for_task('default')
            adapter = AIAdapter(provider=provider, model=model)
            response = adapter.send_request(
                prompt=prompt,
                language='de',
                temperature=0.2,
            )
            text = response.get('output_text', '')
            logger.info("AI response length: %d chars", len(text))
            if not text:
                logger.warning("AI returned empty output_text. Keys: %s", list(response.keys()))
                logger.debug("Full response: %s", str(response)[:500])
            result = TopicHierarchyService._parse_hierarchy_response(text)
            if result:
                logger.info("Parsed %d root categories", len(result))
            else:
                logger.warning("Parse failed. FULL response: %s", text if text else 'EMPTY')
            return result
        except Exception:
            logger.exception("AI hierarchy clustering failed")
            return None

    @staticmethod
    def _parse_hierarchy_response(text: str) -> Optional[List[Dict]]:
        """Parse AI JSON response into hierarchy list."""
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            if '[' in text:
                start = text.index('[')
                end = text.rindex(']') + 1
                return json.loads(text[start:end])
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Failed to parse AI hierarchy: %s", exc)
        return None

    @staticmethod
    def _save_hierarchy(roots: List[Dict]) -> Dict[str, Any]:
        """Save parsed hierarchy to DB via repository."""
        from app.infrastructure.persistence.repositories.exams.topic_nodes import (
            TopicNodeRepository,
        )

        nodes_to_save = []
        for root in roots:
            nodes_to_save.append({
                'topic_key': root['topic_key'],
                'parent_key': None,
                'display_name': root.get('display_name', {}),
                'source': 'ai',
            })
            for child in root.get('children', []):
                nodes_to_save.append({
                    'topic_key': child['topic_key'],
                    'parent_key': root['topic_key'],
                    'display_name': child.get('display_name', {}),
                    'source': 'ai',
                })

        count = TopicNodeRepository.upsert_batch(nodes_to_save)
        return {
            'root_count': len(roots),
            'total_nodes': count,
            'roots': [r['topic_key'] for r in roots],
        }

    @staticmethod
    def get_hierarchy() -> List[Dict[str, Any]]:
        """Get the current topic hierarchy tree."""
        from app.infrastructure.persistence.repositories.exams.topic_nodes import (
            TopicNodeRepository,
        )
        return TopicNodeRepository.find_tree()

    @staticmethod
    def get_aggregated_stats(
        user_id: str, exam_type_key: str = None
    ) -> List[Dict[str, Any]]:
        """Get topic stats aggregated by root category."""
        from app.infrastructure.persistence.repositories.exams.topic_nodes import (
            TopicNodeRepository,
        )
        return TopicNodeRepository.get_topic_stats_aggregated(
            user_id, exam_type_key=exam_type_key
        )

    @staticmethod
    def move_topic(topic_key: str, new_parent: Optional[str]) -> bool:
        """Admin: move a topic to a different parent."""
        from app.infrastructure.persistence.repositories.exams.topic_nodes import (
            TopicNodeRepository,
        )
        return TopicNodeRepository.update_parent(topic_key, new_parent)
