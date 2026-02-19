"""
ExamContextDetector - Automatische Erkennung des Prüfungskontexts

Analysiert:
- User-Profil (Beruf, Region, Ziel-Prüfung)
- Kurs-Metadaten (profession_tag, exam_level, region)
- Kurs-Dateien (PDFs, TXT) -> erkennt Prüfungstyp und Themen
- Lern-Analytics (schwache/starke Themen)

Liefert einen vollständigen Kontext für die KI-Prüfungssimulation.
"""

import logging
from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime

from app.infrastructure.persistence.repositories.ai.exam_context import ExamContextRepository

logger = logging.getLogger(__name__)


class ExamContextDetector:
    """
    Erkennt automatisch den Prüfungskontext für einen User in einem Kurs.
    Kombiniert User-Profil, Kurs-Metadaten, Dateien und Lern-Analytics.
    """

    # Bekannte Berufe und ihre Varianten
    PROFESSION_MAPPINGS = {
        'fisi': ['fachinformatiker systemintegration', 'fisi', 'systemintegration', 'fi-si'],
        'fiae': ['fachinformatiker anwendungsentwicklung', 'fiae', 'anwendungsentwicklung', 'fi-ae'],
        'it_systemkaufmann': ['it-systemkaufmann', 'it systemkaufmann', 'itsk'],
        'informatikkaufmann': ['informatikkaufmann', 'ik'],
        'einzelhandel': ['einzelhandelskaufmann', 'einzelhandel', 'kaufmann im einzelhandel'],
        'industriekaufmann': ['industriekaufmann', 'industriekauffrau', 'ik'],
        'buerokaufmann': ['bürokaufmann', 'buerokaufmann', 'kaufmann für büromanagement'],
    }

    # Prüfungslevel
    EXAM_LEVELS = ['AP1', 'AP2', 'Abschlussprüfung', 'Zwischenprüfung', 'Teil 1', 'Teil 2']

    # Deutsche Bundesländer
    REGIONS = [
        'Baden-Württemberg', 'Bayern', 'Berlin', 'Brandenburg', 'Bremen',
        'Hamburg', 'Hessen', 'Mecklenburg-Vorpommern', 'Niedersachsen',
        'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland', 'Sachsen',
        'Sachsen-Anhalt', 'Schleswig-Holstein', 'Thüringen'
    ]

    # Topic Keywords für Erkennung
    TOPIC_KEYWORDS = {
        'Kalkulation': ['kalkulation', 'bezugskalkulation', 'verkaufskalkulation', 'handelskalkulation',
                       'rabatt', 'skonto', 'listenpreis', 'bezugspreis', 'selbstkosten'],
        'Netzwerk': ['netzwerk', 'tcp/ip', 'subnetting', 'routing', 'switch', 'router',
                    'firewall', 'vlan', 'dhcp', 'dns', 'ip-adresse'],
        'SQL': ['sql', 'datenbank', 'select', 'join', 'where', 'group by', 'normalisierung',
               'erm', 'entity-relationship', 'primärschlüssel', 'fremdschlüssel'],
        'Programmierung': ['programmierung', 'algorithmus', 'schleife', 'bedingung', 'variable',
                          'funktion', 'klasse', 'objekt', 'vererbung', 'pseudocode'],
        'IT-Sicherheit': ['it-sicherheit', 'verschlüsselung', 'firewall', 'backup', 'raid',
                         'datenschutz', 'dsgvo', 'authentifizierung', 'autorisierung'],
        'Projektmanagement': ['projektmanagement', 'gantt', 'netzplan', 'meilenstein',
                             'lastenheft', 'pflichtenheft', 'agil', 'scrum', 'kanban'],
        'Wirtschaft': ['wirtschaft', 'bwl', 'kosten', 'gewinn', 'umsatz', 'bilanz',
                      'buchführung', 'rechtsform', 'vertrag', 'arbeitsrecht'],
    }

    def __init__(self):
        self.confidence_threshold = 0.7

    async def detect_context(self, user_id: UUID, course_id: UUID) -> Dict[str, Any]:
        """
        Erkenne automatisch den Prüfungs-Kontext für einen User in einem Kurs.

        Returns:
            dict mit:
            - profession: Erkannter Beruf
            - exam_level: Prüfungslevel (AP1, AP2, etc.)
            - region: Bundesland
            - ihk_standard: IHK-Standard String
            - weak_topics: Liste schwacher Themen
            - strong_topics: Liste starker Themen
            - recommended_focus: Empfohlene Fokus-Verteilung
            - detected_files: Relevante Dateien
            - confidence: Konfidenz der Erkennung
        """
        logger.info(f"Detecting exam context for user {user_id} in course {course_id}")

        # 1. User-Profil laden
        user_profile = await self._get_user_profile(user_id)

        # 2. Kurs-Metadaten laden
        course_data = await self._get_course_metadata(course_id)

        # 3. Kurs-Dateien laden (prüfungsrelevante)
        course_files = await self._get_exam_relevant_files(course_id)

        # 4. Lern-Analytics laden
        analytics = await self._get_learning_analytics(user_id, course_id)

        # 5. Kontext zusammenbauen
        context = self._build_context(user_profile, course_data, course_files, analytics)

        # 6. Fokus-Verteilung berechnen
        context['recommended_focus'] = self._calculate_focus_distribution(
            analytics, context.get('detected_topics', [])
        )

        # 7. Konfidenz berechnen
        context['confidence'] = self._calculate_confidence(context)

        logger.info(f"Context detected with confidence {context['confidence']:.2f}")
        return context

    async def _get_user_profile(self, user_id: UUID) -> Optional[Dict]:
        """Lade User-Profil aus der Datenbank."""
        result = ExamContextRepository.get_user_profile(str(user_id))
        return dict(result) if result else {}

    async def _get_course_metadata(self, course_id: UUID) -> Dict:
        """Lade Kurs-Metadaten."""
        result = ExamContextRepository.get_course_metadata(str(course_id))
        return dict(result) if result else {}

    async def _get_exam_relevant_files(self, course_id: UUID) -> List[Dict]:
        """Lade prüfungsrelevante Dateien des Kurses."""
        results = ExamContextRepository.get_exam_relevant_files(str(course_id))
        return [dict(r) for r in results] if results else []

    async def _get_learning_analytics(self, user_id: UUID, course_id: UUID) -> List[Dict]:
        """Lade Lern-Analytics für den User im Kurs."""
        results = ExamContextRepository.get_learning_analytics(
            str(user_id), str(course_id)
        )
        return [dict(r) for r in results] if results else []

    def _build_context(
        self,
        user_profile: Dict,
        course_data: Dict,
        course_files: List[Dict],
        analytics: List[Dict]
    ) -> Dict[str, Any]:
        """Baue den Kontext aus allen Datenquellen zusammen."""

        # Profession bestimmen (Priorität: User-Profil > Kurs > Erkennung)
        profession = (
            user_profile.get('profession') or
            course_data.get('profession_tag') or
            self._detect_profession_from_title(course_data.get('title', ''))
        )

        # Exam Level bestimmen
        exam_level = (
            user_profile.get('target_exam') or
            course_data.get('exam_level') or
            self._detect_exam_level(course_data.get('title', ''))
        )

        # Region bestimmen
        region = (
            user_profile.get('region') or
            course_data.get('exam_region') or
            self._detect_region(course_data.get('title', ''))
        )

        # IHK Standard zusammenbauen
        ihk_standard = course_data.get('ihk_standard')
        if not ihk_standard and profession and exam_level:
            ihk_standard = f"IHK {profession.upper()} {exam_level}"

        # Schwache und starke Themen aus Analytics
        weak_topics = []
        strong_topics = []
        normal_topics = []

        for a in analytics:
            topic = a.get('topic')
            score = a.get('score_avg', 0) or 0

            if score < 70:
                weak_topics.append({'topic': topic, 'score': score})
            elif score > 85:
                strong_topics.append({'topic': topic, 'score': score})
            else:
                normal_topics.append({'topic': topic, 'score': score})

        # Themen aus Kurs-Metadaten
        detected_topics = course_data.get('detected_topics') or []
        if not detected_topics:
            # Versuche Themen aus Titel/Beschreibung zu erkennen
            detected_topics = self._detect_topics(
                course_data.get('title', '') + ' ' + (course_data.get('description') or '')
            )

        # Dateien aufbereiten
        detected_files = [
            {
                'file_id': str(f.get('file_id')),
                'filename': f.get('original_filename'),
                'type': f.get('file_type'),
                'is_exam_relevant': f.get('is_exam_relevant', False),
                'topics': f.get('exam_topics') or [],
                'summary': f.get('content_summary')
            }
            for f in course_files
        ]

        return {
            'profession': profession,
            'profession_detail': user_profile.get('profession_detail'),
            'exam_level': exam_level,
            'region': region,
            'ihk': user_profile.get('ihk'),
            'ihk_standard': ihk_standard,
            'training_year': user_profile.get('training_year'),
            'exam_date': str(user_profile.get('exam_date')) if user_profile.get('exam_date') else None,
            'weak_topics': weak_topics,
            'strong_topics': strong_topics,
            'normal_topics': normal_topics,
            'detected_topics': detected_topics,
            'detected_files': detected_files,
            'course_title': course_data.get('title'),
            'user_name': user_profile.get('display_name'),
            'preferred_difficulty': user_profile.get('preferred_difficulty', 'realistic'),
        }

    def _detect_profession_from_title(self, title: str) -> Optional[str]:
        """Erkenne Beruf aus Kurstitel."""
        title_lower = title.lower()
        for profession, keywords in self.PROFESSION_MAPPINGS.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return profession.upper()
        return None

    def _detect_exam_level(self, title: str) -> Optional[str]:
        """Erkenne Prüfungslevel aus Titel."""
        title_lower = title.lower()
        for level in self.EXAM_LEVELS:
            if level.lower() in title_lower:
                return level
        # Spezielle Patterns
        if 'teil 1' in title_lower or 'part 1' in title_lower:
            return 'AP1'
        if 'teil 2' in title_lower or 'part 2' in title_lower:
            return 'AP2'
        return None

    def _detect_region(self, title: str) -> Optional[str]:
        """Erkenne Region aus Titel."""
        title_lower = title.lower()
        for region in self.REGIONS:
            if region.lower() in title_lower:
                return region
        # Abkürzungen
        if 'bw' in title_lower or 'baden' in title_lower:
            return 'Baden-Württemberg'
        if 'by' in title_lower or 'bayern' in title_lower:
            return 'Bayern'
        if 'nrw' in title_lower:
            return 'Nordrhein-Westfalen'
        return None

    def _detect_topics(self, text: str) -> List[str]:
        """Erkenne Themen aus Text."""
        text_lower = text.lower()
        detected = []
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if topic not in detected:
                        detected.append(topic)
                    break
        return detected

    def _calculate_focus_distribution(
        self,
        analytics: List[Dict],
        detected_topics: List[str]
    ) -> Dict[str, int]:
        """
        Berechne empfohlene Fokus-Verteilung basierend auf Schwächen.

        Logik:
        - Schwache Themen (score < 70): 35% Gewicht
        - Normale Themen (70-85): 25% Gewicht
        - Starke Themen (score > 85): 15% Gewicht
        - Unbekannte Themen: 25% Gewicht

        Normalisiert auf 100%.
        """
        if not analytics and not detected_topics:
            # Default-Verteilung wenn keine Daten
            return {
                'Allgemein': 25,
                'Kalkulation': 25,
                'Netzwerk': 25,
                'Programmierung': 25
            }

        weights = {}
        total_weight = 0

        # Gewichte aus Analytics
        for a in analytics:
            topic = a.get('topic')
            score = a.get('score_avg', 75) or 75

            if score < 70:
                weight = 35  # Schwach - mehr fokussieren
            elif score > 85:
                weight = 15  # Stark - weniger fokussieren
            else:
                weight = 25  # Normal

            weights[topic] = weight
            total_weight += weight

        # Themen ohne Analytics hinzufügen
        for topic in detected_topics:
            if topic not in weights:
                weights[topic] = 25
                total_weight += 25

        # Normalisieren auf 100%
        if total_weight > 0:
            normalized = {}
            for topic, weight in weights.items():
                normalized[topic] = round((weight / total_weight) * 100)

            # Korrektur falls Summe nicht genau 100
            diff = 100 - sum(normalized.values())
            if diff != 0 and normalized:
                first_topic = list(normalized.keys())[0]
                normalized[first_topic] += diff

            return normalized

        return {'Allgemein': 100}

    def _calculate_confidence(self, context: Dict) -> float:
        """Berechne Konfidenz der Kontext-Erkennung."""
        score = 0.0
        max_score = 5.0

        # Profession erkannt?
        if context.get('profession'):
            score += 1.0

        # Exam Level erkannt?
        if context.get('exam_level'):
            score += 1.0

        # Region erkannt?
        if context.get('region'):
            score += 0.5

        # Dateien gefunden?
        if context.get('detected_files'):
            score += 1.0

        # Analytics vorhanden?
        if context.get('weak_topics') or context.get('strong_topics'):
            score += 1.0

        # Themen erkannt?
        if context.get('detected_topics'):
            score += 0.5

        return round(score / max_score, 2)


# ============================================================================
# Convenience Funktion
# ============================================================================

async def get_exam_context(user_id: UUID, course_id: UUID) -> Dict[str, Any]:
    """
    Convenience-Funktion zum Abrufen des Prüfungskontexts.

    Args:
        user_id: UUID des Users
        course_id: UUID des Kurses

    Returns:
        Vollständiger Kontext-Dict für KI-Prüfungssimulation
    """
    detector = ExamContextDetector()
    return await detector.detect_context(user_id, course_id)


# ============================================================================
# Synchrone Wrapper (für Flask-Routen ohne async)
# ============================================================================

def get_exam_context_sync(user_id: UUID, course_id: UUID) -> Dict[str, Any]:
    """Synchroner Wrapper für get_exam_context."""
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_exam_context(user_id, course_id))
    finally:
        loop.close()
