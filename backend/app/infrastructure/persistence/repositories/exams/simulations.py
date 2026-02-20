"""
Exam Simulations Repository

Database access for exam simulation management:
- Simulation CRUD
- Simulation listing with filters and pagination
- Attempt management (create, list, update)
- Simulation stats updates
- User exam profile management
- Course verification
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query
)


class ExamSimulationRepository:
    """Repository for exam simulation operations."""

    # =========================================================================
    # SIMULATION CRUD
    # =========================================================================

    @staticmethod
    def create_simulation(
        simulation_id: str,
        course_id: str,
        user_id: str,
        title: str,
        context_json: str,
        config_json: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new exam simulation.

        Args:
            simulation_id: UUID for the simulation
            course_id: Course UUID
            user_id: User UUID
            title: Simulation title
            context_json: JSON string of exam context
            config_json: JSON string of simulation config

        Returns:
            Created simulation record or None
        """
        query = """
            INSERT INTO exam_simulations
            (simulation_id, course_id, user_id, title, context_json, config_json, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
            RETURNING *
        """
        return fetch_one(query, (
            simulation_id, course_id, user_id, title,
            context_json, config_json, datetime.utcnow()
        ))

    @staticmethod
    def get_simulation(simulation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation with course title.

        Args:
            simulation_id: Simulation UUID

        Returns:
            Simulation record with course_title or None
        """
        query = """
            SELECT
                es.*, c.title as course_title
            FROM exam_simulations es
            JOIN courses c ON c.course_id = es.course_id
            WHERE es.simulation_id = %s
        """
        return fetch_one(query, (simulation_id,))

    @staticmethod
    def get_simulation_owner(simulation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation user_id for ownership check.

        Args:
            simulation_id: Simulation UUID

        Returns:
            Dict with user_id or None
        """
        return fetch_one(
            "SELECT user_id FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

    @staticmethod
    def get_simulation_config(simulation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation config_json.

        Args:
            simulation_id: Simulation UUID

        Returns:
            Dict with config_json or None
        """
        return fetch_one(
            "SELECT config_json FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

    @staticmethod
    def get_simulation_full(simulation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full simulation record.

        Args:
            simulation_id: Simulation UUID

        Returns:
            Full simulation record or None
        """
        return fetch_one(
            "SELECT * FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

    @staticmethod
    def get_simulation_result(simulation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get simulation result_json.

        Args:
            simulation_id: Simulation UUID

        Returns:
            Dict with result_json or None
        """
        return fetch_one(
            "SELECT result_json FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

    @staticmethod
    def delete_simulation(simulation_id: str) -> None:
        """
        Delete a simulation.

        Args:
            simulation_id: Simulation UUID
        """
        execute_query(
            "DELETE FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

    # =========================================================================
    # SIMULATION LISTING
    # =========================================================================

    @staticmethod
    def count_simulations(
        user_id: str,
        course_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Count user's simulations with optional filters.

        Args:
            user_id: User UUID
            course_id: Optional course filter
            status: Optional status filter

        Returns:
            Total count
        """
        conditions = ["user_id = %s"]
        params: List[Any] = [user_id]

        if course_id:
            conditions.append("course_id = %s")
            params.append(course_id)
        if status:
            conditions.append("status = %s")
            params.append(status)

        where_clause = " AND ".join(conditions)
        query = f"SELECT COUNT(*) as total FROM exam_simulations WHERE {where_clause}"
        result = fetch_one(query, tuple(params))
        return result['total'] if result else 0

    @staticmethod
    def list_simulations(
        user_id: str,
        course_id: Optional[str] = None,
        status: Optional[str] = None,
        per_page: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List user's simulations with pagination and filters.

        Args:
            user_id: User UUID
            course_id: Optional course filter
            status: Optional status filter
            per_page: Items per page
            offset: Offset for pagination

        Returns:
            List of simulation records with course_title
        """
        conditions = ["user_id = %s"]
        params: List[Any] = [user_id]

        if course_id:
            conditions.append("course_id = %s")
            params.append(course_id)
        if status:
            conditions.append("status = %s")
            params.append(status)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT
                es.simulation_id, es.course_id, es.user_id, es.title,
                es.context_json, es.config_json, es.status, es.error_message,
                es.attempt_count, es.best_score, es.avg_score,
                es.created_at, es.updated_at,
                c.title as course_title
            FROM exam_simulations es
            JOIN courses c ON c.course_id = es.course_id
            WHERE {where_clause}
            ORDER BY es.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        return fetch_all(query, tuple(params))

    # =========================================================================
    # ATTEMPT MANAGEMENT
    # =========================================================================

    @staticmethod
    def create_attempt(
        attempt_id: str,
        simulation_id: str,
        user_id: str,
        max_score: int
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new exam attempt.

        Args:
            attempt_id: Attempt UUID
            simulation_id: Simulation UUID
            user_id: User UUID
            max_score: Maximum possible score

        Returns:
            Created attempt record or None
        """
        query = """
            INSERT INTO exam_simulation_attempts
            (attempt_id, simulation_id, user_id, started_at, max_score, status, created_at)
            VALUES (%s, %s, %s, %s, %s, 'in_progress', %s)
            RETURNING *
        """
        now = datetime.utcnow()
        return fetch_one(query, (
            attempt_id, simulation_id, user_id, now, max_score, now
        ))

    @staticmethod
    def get_attempt(attempt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get exam attempt by ID.

        Args:
            attempt_id: Attempt UUID

        Returns:
            Attempt record or None
        """
        return fetch_one(
            "SELECT * FROM exam_simulation_attempts WHERE attempt_id = %s",
            (attempt_id,)
        )

    @staticmethod
    def list_attempts(simulation_id: str) -> List[Dict[str, Any]]:
        """
        List all attempts for a simulation.

        Args:
            simulation_id: Simulation UUID

        Returns:
            List of attempt records ordered by created_at DESC
        """
        query = """
            SELECT
                attempt_id, simulation_id, user_id,
                started_at, completed_at, time_spent_seconds,
                score, max_score, percentage, passed,
                results_by_topic, status, created_at
            FROM exam_simulation_attempts
            WHERE simulation_id = %s
            ORDER BY created_at DESC
        """
        return fetch_all(query, (simulation_id,))

    @staticmethod
    def complete_attempt(
        attempt_id: str,
        time_spent_seconds: int,
        score: int,
        percentage: float,
        passed: bool,
        results_by_topic: Dict
    ) -> Optional[Dict[str, Any]]:
        """
        Mark attempt as completed with results.

        Args:
            attempt_id: Attempt UUID
            time_spent_seconds: Time spent
            score: Achieved score
            percentage: Score percentage
            passed: Whether passed
            results_by_topic: Results breakdown by topic

        Returns:
            Updated attempt record or None
        """
        query = """
            UPDATE exam_simulation_attempts
            SET
                completed_at = %s,
                time_spent_seconds = %s,
                score = %s,
                percentage = %s,
                passed = %s,
                results_by_topic = %s,
                status = 'completed'
            WHERE attempt_id = %s
            RETURNING *
        """
        return fetch_one(query, (
            datetime.utcnow(), time_spent_seconds, score,
            percentage, passed, json.dumps(results_by_topic), attempt_id
        ))

    @staticmethod
    def update_simulation_stats(
        simulation_id: str, score: int
    ) -> None:
        """
        Update simulation attempt stats after submission.

        Args:
            simulation_id: Simulation UUID
            score: Score from the latest attempt
        """
        query = """
            UPDATE exam_simulations
            SET
                attempt_count = attempt_count + 1,
                best_score = GREATEST(best_score, %s),
                avg_score = (SELECT AVG(score) FROM exam_simulation_attempts WHERE simulation_id = %s)
            WHERE simulation_id = %s
        """
        execute_query(query, (score, simulation_id, simulation_id))

    # =========================================================================
    # USER EXAM PROFILE
    # =========================================================================

    @staticmethod
    def get_user_exam_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's exam profile settings.

        Args:
            user_id: User UUID

        Returns:
            Profile record or None
        """
        return fetch_one(
            """
            SELECT
                profession, profession_detail, training_year,
                target_exam, exam_date, region, ihk,
                detected_profession, detected_level, detection_confidence,
                preferred_difficulty, preferred_question_types
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,)
        )

    @staticmethod
    def get_user_profile_id(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if user profile exists.

        Args:
            user_id: User UUID

        Returns:
            Dict with profile_id or None
        """
        return fetch_one(
            "SELECT profile_id FROM user_profiles WHERE user_id = %s",
            (user_id,)
        )

    @staticmethod
    def update_user_profile(
        user_id: str,
        set_parts: List[str],
        values: List[Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update existing user profile with dynamic fields.

        Args:
            user_id: User UUID
            set_parts: List of 'field = %s' strings
            values: List of values (user_id appended)

        Returns:
            Updated profile record or None
        """
        values_with_id = list(values) + [user_id]
        query = f"""
            UPDATE user_profiles
            SET {', '.join(set_parts)}
            WHERE user_id = %s
            RETURNING *
        """
        return fetch_one(query, tuple(values_with_id))

    @staticmethod
    def insert_user_profile(
        fields: List[str],
        placeholders: List[str],
        values: List[Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Insert new user profile.

        Args:
            fields: List of column names
            placeholders: List of %s placeholders
            values: List of values

        Returns:
            Created profile record or None
        """
        query = f"""
            INSERT INTO user_profiles ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        return fetch_one(query, tuple(values))
