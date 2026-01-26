"""
LernsystemX - Learning Method Instance Repository

Data access layer for learning method instances (konkrete Lernmethoden-Instanzen pro Lesson).

Diese Instanzen sind die tatsächlichen Lernmethoden-Einträge, die:
- Einer Lesson (oder einem Module) zugeordnet sind
- Einen method_type (LM00-LM11, database-driven) haben
- Spezifische Daten (data JSONB) und optionale Lösungen (solution JSONB) enthalten

Referenz: 02_Lernmethoden.md (12 Content-Lernmethoden, LM00-LM11 + Extensions)

All learning methods are database-driven from learning_method_types table.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import psycopg
from psycopg.rows import dict_row

from app.core.bootstrap.extensions import db_pool
from app.infrastructure.persistence.repositories.learning_method.catalog import LearningMethodCatalogRepository


class LearningMethodInstanceRepository:
    """
    Repository für Learning Method Instances (konkrete Lernmethoden pro Lesson/Module).

    Alle Methoden nutzen psycopg Connection Pool und geben Dictionaries zurück.
    """

    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================

    @classmethod
    def find_by_id(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """
        Findet eine Learning Method Instance nach ID.

        Args:
            method_id: UUID der Learning Method Instance

        Returns:
            Learning Method Instance als Dict oder None
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        lm.method_id,
                        lm.chapter_id,
                        lm.method_type,
                        lm.title,
                        lm.instructions,
                        lm.data,
                        lm.solution,
                        lm.tier,
                        lm.duration_minutes,
                        lm.difficulty,
                        lm.order_index,
                        lm.published,
                        lm.created_at,
                        lm.updated_at,
                        ch.title as chapter_title,
                        ch.course_id
                    FROM learning_methods lm
                    LEFT JOIN courses.chapters ch ON lm.chapter_id = ch.chapter_id
                    WHERE lm.method_id = %s
                """, (method_id,))

                return cur.fetchone()

    @classmethod
    def find_by_chapter(
        cls,
        chapter_id: str,
        published_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Findet alle Learning Method Instances für ein Kapitel.

        Args:
            chapter_id: UUID des Kapitels
            published_only: Nur veröffentlichte Methoden

        Returns:
            Liste der Learning Method Instances
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = """
                    SELECT
                        method_id,
                        chapter_id,
                        method_type,
                        title,
                        instructions,
                        data,
                        solution,
                        tier,
                        duration_minutes,
                        difficulty,
                        order_index,
                        published,
                        created_at,
                        updated_at
                    FROM learning_methods
                    WHERE chapter_id = %s
                """

                if published_only:
                    query += " AND published = TRUE"

                query += " ORDER BY order_index, created_at"

                cur.execute(query, (chapter_id,))
                return cur.fetchall()

    @classmethod
    def find_by_lesson(
        cls,
        lesson_id: str,
        published_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Findet alle Learning Method Instances für eine Lesson.

        Hinweis: Die aktuelle Tabellenstruktur hat nur chapter_id.
        Diese Methode ist für zukünftige Erweiterung vorbereitet.

        Args:
            lesson_id: UUID der Lesson
            published_only: Nur veröffentlichte Methoden

        Returns:
            Liste der Learning Method Instances
        """
        # Aktuelle Implementierung: Suche über Lesson -> Chapter -> Learning Methods
        # TODO: Wenn lesson_id Spalte zur learning_methods Tabelle hinzugefügt wird
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Hole chapter_id der Lesson
                cur.execute("""
                    SELECT chapter_id FROM courses.lessons WHERE lesson_id = %s
                """, (lesson_id,))

                lesson = cur.fetchone()
                if not lesson:
                    return []

                # Hole Learning Methods für das Kapitel
                return cls.find_by_chapter(lesson['chapter_id'], published_only)

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt eine neue Learning Method Instance.

        Args:
            data: {
                'chapter_id': UUID,
                'method_type': int (0-31),
                'title': str,
                'instructions': str (optional),
                'data': dict (JSONB),
                'solution': dict (optional, JSONB),
                'tier': str ('basic', 'premium', 'pro'),
                'duration_minutes': int (optional),
                'difficulty': str ('easy', 'medium', 'hard'),
                'order_index': int (optional),
                'published': bool (default: False)
            }

        Returns:
            Erstellte Learning Method Instance

        Raises:
            ValueError: Bei ungültiger method_type
        """
        # Validiere method_type (0-11, database-driven)
        method_type = data.get('method_type')

        # Query database to validate method_type
        method_def = LearningMethodCatalogRepository.get_by_type(method_type=method_type)
        if not method_def:
            max_type = LearningMethodCatalogRepository.get_max_active_type()
            raise ValueError(f"Ungültige method_type: {method_type}. Muss zwischen 0 und {max_type} liegen.")

        # Hole Tier aus Datenbank falls nicht angegeben
        if 'tier' not in data:
            group_code = method_def.get('group_code')
            # Gruppe A+B = basic, C = premium
            if group_code in ['A', 'B']:
                data['tier'] = 'basic'
            elif group_code == 'C':
                data['tier'] = 'premium'
            else:
                data['tier'] = 'basic'  # Default to basic for unknown groups

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO learning_methods (
                        chapter_id,
                        method_type,
                        title,
                        instructions,
                        data,
                        solution,
                        tier,
                        duration_minutes,
                        difficulty,
                        order_index,
                        published
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING *
                """, (
                    data.get('chapter_id'),
                    method_type,
                    data.get('title', ''),
                    data.get('instructions'),
                    psycopg.types.json.Jsonb(data.get('data', {})),
                    psycopg.types.json.Jsonb(data.get('solution')) if data.get('solution') else None,
                    data.get('tier', 'basic'),
                    data.get('duration_minutes'),
                    data.get('difficulty', 'medium'),
                    data.get('order_index', 0),
                    data.get('published', False)
                ))

                conn.commit()
                return cur.fetchone()

    @classmethod
    def update(cls, method_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Aktualisiert eine Learning Method Instance.

        Args:
            method_id: UUID der Learning Method Instance
            data: Zu aktualisierende Felder

        Returns:
            Aktualisierte Learning Method Instance oder None

        Raises:
            ValueError: Bei ungültiger method_type
        """
        # Validiere method_type falls vorhanden (database-driven)
        if 'method_type' in data:
            method_def = LearningMethodCatalogRepository.get_by_type(method_type=data['method_type'])
            if not method_def:
                max_type = LearningMethodCatalogRepository.get_max_active_type()
                raise ValueError(f"Ungültige method_type: {data['method_type']}. Muss zwischen 0 und {max_type} liegen.")

        # Baue dynamisches UPDATE
        update_fields = []
        params = []

        allowed_fields = [
            'method_type', 'title', 'instructions', 'tier',
            'duration_minutes', 'difficulty', 'order_index', 'published'
        ]

        for key in allowed_fields:
            if key in data:
                update_fields.append(f"{key} = %s")
                params.append(data[key])

        # JSONB-Felder separat behandeln
        if 'data' in data:
            update_fields.append("data = %s")
            params.append(psycopg.types.json.Jsonb(data['data']))

        if 'solution' in data:
            update_fields.append("solution = %s")
            params.append(psycopg.types.json.Jsonb(data['solution']) if data['solution'] else None)

        if not update_fields:
            return cls.find_by_id(method_id)

        params.append(method_id)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = f"""
                    UPDATE learning_methods
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE method_id = %s
                    RETURNING *
                """

                cur.execute(query, params)
                conn.commit()
                return cur.fetchone()

    @classmethod
    def delete(cls, method_id: str) -> bool:
        """
        Löscht eine Learning Method Instance.

        Args:
            method_id: UUID der Learning Method Instance

        Returns:
            True wenn gelöscht, False wenn nicht gefunden
        """
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM learning_methods
                    WHERE method_id = %s
                """, (method_id,))

                conn.commit()
                return cur.rowcount > 0

    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================

    @classmethod
    def bulk_create(cls, instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Erstellt mehrere Learning Method Instances auf einmal.

        Args:
            instances: Liste von Instanz-Daten

        Returns:
            Liste der erstellten Instanzen
        """
        results = []
        for instance in instances:
            try:
                result = cls.create(instance)
                results.append(result)
            except Exception as e:
                # Log error but continue with other instances
                print(f"Error creating learning method instance: {e}")

        return results

    @classmethod
    def reorder(cls, chapter_id: str, method_ids: List[str]) -> bool:
        """
        Sortiert Learning Methods in einem Kapitel neu.

        Args:
            chapter_id: UUID des Kapitels
            method_ids: Liste der method_ids in neuer Reihenfolge

        Returns:
            True wenn erfolgreich
        """
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                for index, method_id in enumerate(method_ids):
                    cur.execute("""
                        UPDATE learning_methods
                        SET order_index = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE method_id = %s AND chapter_id = %s
                    """, (index, method_id, chapter_id))

                conn.commit()
                return True

    # =========================================================================
    # STATISTICS
    # =========================================================================

    @classmethod
    def get_statistics_by_chapter(cls, chapter_id: str) -> Dict[str, Any]:
        """
        Holt Statistiken für Learning Methods eines Kapitels.

        Args:
            chapter_id: UUID des Kapitels

        Returns:
            Statistik-Dict
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) as total_methods,
                        COUNT(*) FILTER (WHERE published = TRUE) as published_count,
                        COUNT(DISTINCT method_type) as unique_types,
                        COALESCE(SUM(duration_minutes), 0) as total_duration,
                        COUNT(*) FILTER (WHERE difficulty = 'easy') as easy_count,
                        COUNT(*) FILTER (WHERE difficulty = 'medium') as medium_count,
                        COUNT(*) FILTER (WHERE difficulty = 'hard') as hard_count,
                        COUNT(*) FILTER (WHERE tier = 'basic') as basic_count,
                        COUNT(*) FILTER (WHERE tier = 'premium') as premium_count,
                        COUNT(*) FILTER (WHERE tier = 'pro') as pro_count
                    FROM learning_methods
                    WHERE chapter_id = %s
                """, (chapter_id,))

                return cur.fetchone()

    @classmethod
    def get_method_type_distribution(cls, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Holt die Verteilung der Lernmethoden-Typen.

        Args:
            course_id: Optional - Filter auf einen Kurs

        Returns:
            Liste mit method_type und count
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if course_id:
                    cur.execute("""
                        SELECT
                            lm.method_type,
                            COUNT(*) as count
                        FROM learning_methods lm
                        JOIN courses.chapters ch ON lm.chapter_id = ch.chapter_id
                        WHERE ch.course_id = %s
                        GROUP BY lm.method_type
                        ORDER BY lm.method_type
                    """, (course_id,))
                else:
                    cur.execute("""
                        SELECT
                            method_type,
                            COUNT(*) as count
                        FROM learning_methods
                        GROUP BY method_type
                        ORDER BY method_type
                    """)

                return cur.fetchall()

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    @classmethod
    def publish(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Veröffentlicht eine Learning Method Instance."""
        return cls.update(method_id, {'published': True})

    @classmethod
    def unpublish(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Zieht die Veröffentlichung einer Learning Method Instance zurück."""
        return cls.update(method_id, {'published': False})

    @classmethod
    def copy_to_chapter(cls, method_id: str, target_chapter_id: str) -> Optional[Dict[str, Any]]:
        """
        Kopiert eine Learning Method Instance in ein anderes Kapitel.

        Args:
            method_id: UUID der zu kopierenden Instance
            target_chapter_id: UUID des Ziel-Kapitels

        Returns:
            Kopierte Instance oder None
        """
        original = cls.find_by_id(method_id)
        if not original:
            return None

        # Erstelle Kopie
        copy_data = {
            'chapter_id': target_chapter_id,
            'method_type': original['method_type'],
            'title': f"{original['title']} (Kopie)",
            'instructions': original.get('instructions'),
            'data': original.get('data', {}),
            'solution': original.get('solution'),
            'tier': original['tier'],
            'duration_minutes': original.get('duration_minutes'),
            'difficulty': original.get('difficulty'),
            'order_index': 0,  # Am Anfang einfügen
            'published': False  # Kopie ist nicht veröffentlicht
        }

        return cls.create(copy_data)
