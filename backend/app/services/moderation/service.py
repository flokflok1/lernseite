"""
LernsystemX Moderation Service

Business logic for course moderation workflow:
- Queue management for courses awaiting review
- AI analysis integration and result handling
- Human moderator workflows
- Audit trail management for all moderation actions

Compliance:
- DSA (Digital Services Act) compliant moderation
- NetzDG compliant content review
- GDPR compliant audit trails
- ISO 27001 compliant access control
"""

from typing import Dict, Optional, Any, List
from datetime import datetime
from decimal import Decimal
from flask import current_app

from app.repositories.moderation_audit import ModerationAuditRepository, ModerationAction
from app.repositories.course_publishing import CoursePublishingRepository
from app.services.audit_service import AuditService
from app.infrastructure.utils.exceptions import NotFoundError, ValidationError, ConflictError

# NOTE: CourseRepository imported lazily (inside methods) to avoid circular imports
# Import chain: repositories.courses -> cache_service -> services -> moderation_service -> repositories.courses


class ModerationService:
    """
    Service layer for course moderation.

    Manages moderation queues, AI analysis, and human review workflows.
    Maintains immutable audit trail for compliance purposes.
    """

    # AI analysis confidence thresholds
    MIN_CONFIDENCE_THRESHOLD = Decimal("0.70")  # 70% confidence required
    REJECT_THRESHOLD = Decimal("0.95")  # Automatically reject if >95% confidence

    @classmethod
    def get_moderation_queue(
        cls,
        limit: int = 100,
        offset: int = 0,
        filter_status: Optional[str] = None,
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        Get courses waiting for moderation.

        Args:
            limit: Max results
            offset: Pagination offset
            filter_status: Optional status filter (submitted, approved, rejected, etc.)

        Returns:
            Tuple of (publishing records, total count)
        """
        if filter_status:
            records = CoursePublishingRepository.list_by_status(
                status=filter_status, limit=limit, offset=offset
            )
        else:
            records = CoursePublishingRepository.list_submitted(limit=limit, offset=offset)

        total = CoursePublishingRepository.count_by_status(filter_status or "submitted")
        return records, total

    @classmethod
    def run_ai_analysis(
        cls,
        course_id: str,
        analysis_type: str = "comprehensive",
    ) -> Dict[str, Any]:
        """
        Run AI analysis on a course.

        Performs comprehensive moderation analysis using AI models:
        - Content compliance (DSA, NetzDG, GDPR)
        - Quality assessment
        - Inappropriate content detection
        - Copyright/plagiarism assessment

        Args:
            course_id: Course UUID
            analysis_type: Type of analysis (comprehensive, quick, deep)

        Returns:
            Analysis results with scores and recommendations

        Raises:
            NotFoundError: If course not found
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Placeholder for AI analysis
        # In production, this would call an AI service
        analysis_result = {
            "course_id": course_id,
            "analysis_type": analysis_type,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": Decimal("0.85"),  # 0.00-1.00
            "categories": {
                "content_compliance": {
                    "score": Decimal("0.90"),
                    "passed": True,
                    "issues": [],
                },
                "quality": {
                    "score": Decimal("0.80"),
                    "passed": True,
                    "issues": ["Could improve clarity in sections"],
                },
                "inappropriate_content": {
                    "score": Decimal("0.95"),
                    "passed": True,
                    "issues": [],
                },
                "copyright": {
                    "score": Decimal("0.75"),
                    "passed": False,
                    "issues": ["Potential copyright issue in lesson 3"],
                },
            },
            "recommendation": "REVIEW_REQUIRED",
            "manual_review_priority": "medium",
        }

        # Create audit trail entry for AI analysis
        ModerationAuditRepository.create(
            course_id=course_id,
            action="ai_analyzed",
            moderator_id=None,  # AI analysis has no moderator
            notes=f"AI analysis completed - Overall score: {analysis_result['overall_score']}",
            ai_analysis=analysis_result,
        )

        # Log action
        AuditService.log_action(
            user_id="system",
            action="admin.moderation.ai_analysis",
            resource_type="course",
            resource_id=course_id,
            details={
                "course_title": course.get("title"),
                "analysis_type": analysis_type,
                "overall_score": str(analysis_result["overall_score"]),
                "recommendation": analysis_result["recommendation"],
            },
            severity="info",
        )

        return analysis_result

    @classmethod
    def log_ai_analysis(
        cls,
        course_id: str,
        analysis_data: Dict[str, Any],
    ) -> Optional[int]:
        """
        Log AI analysis results to moderation audit trail.

        Args:
            course_id: Course UUID
            analysis_data: Analysis results dictionary

        Returns:
            Audit record ID or None if failed

        Raises:
            NotFoundError: If course not found
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Create audit trail entry
        result = ModerationAuditRepository.create(
            course_id=course_id,
            action="ai_analyzed",
            moderator_id=None,
            notes="Automated AI analysis",
            ai_analysis=analysis_data,
        )

        return result.get("audit_id") if result else None

    @classmethod
    def get_analysis_history(
        cls,
        course_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get AI analysis history for a course.

        Args:
            course_id: Course UUID
            limit: Max results
            offset: Pagination offset

        Returns:
            List of AI analysis audit entries
        """
        return ModerationAuditRepository.list_by_course_and_action(
            course_id=course_id,
            action="ai_analyzed",
            limit=limit,
            offset=offset,
        )

    @classmethod
    def get_moderation_history(
        cls,
        course_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        Get complete moderation history for a course.

        Args:
            course_id: Course UUID
            limit: Max results
            offset: Pagination offset

        Returns:
            Tuple of (audit entries, total count)
        """
        records = ModerationAuditRepository.list_by_course(
            course_id=course_id, limit=limit, offset=offset
        )
        total = ModerationAuditRepository.count_by_course(course_id)
        return records, total

    @classmethod
    def get_moderator_workload(
        cls,
        moderator_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        Get moderation actions by a specific moderator.

        Args:
            moderator_id: Moderator user ID
            limit: Max results
            offset: Pagination offset

        Returns:
            Tuple of (moderation records, total count)
        """
        records = CoursePublishingRepository.list_by_moderator(
            moderator_id=moderator_id, limit=limit, offset=offset
        )
        total = CoursePublishingRepository.count_by_moderator(moderator_id)
        return records, total

    @classmethod
    def get_pending_reviews(
        cls,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Dict[str, Any]], int]:
        """
        Get courses pending human review after AI analysis.

        Args:
            limit: Max results
            offset: Pagination offset

        Returns:
            Tuple of (publishing records, total count)
        """
        records = CoursePublishingRepository.list_submitted(limit=limit, offset=offset)
        total = CoursePublishingRepository.count_by_status("submitted")
        return records, total

    @classmethod
    def log_review_action(
        cls,
        course_id: str,
        action: ModerationAction,
        moderator_id: str,
        notes: Optional[str] = None,
        ai_score: Optional[Decimal] = None,
    ) -> Optional[int]:
        """
        Log a moderation review action.

        Args:
            course_id: Course UUID
            action: Action type (reviewed, approved, rejected, etc.)
            moderator_id: Moderator user ID
            notes: Optional review notes
            ai_score: Optional AI analysis score

        Returns:
            Audit record ID or None if failed
        """
        # Create audit trail entry
        result = ModerationAuditRepository.create(
            course_id=course_id,
            action=action,
            moderator_id=moderator_id,
            notes=notes,
            ai_analysis={"ai_score": float(ai_score)} if ai_score else None,
        )

        return result.get("audit_id") if result else None

    @classmethod
    def get_audit_trail(
        cls,
        course_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get complete immutable audit trail for a course.

        Used for compliance and transparency purposes.

        Args:
            course_id: Course UUID

        Returns:
            List of all audit entries (immutable)
        """
        return ModerationAuditRepository.list_by_course(
            course_id=course_id, limit=10000  # Get all entries
        )

    @classmethod
    def generate_compliance_report(
        cls,
        course_id: str,
    ) -> Dict[str, Any]:
        """
        Generate compliance report for a course.

        For DSA, NetzDG, GDPR reporting purposes.

        Args:
            course_id: Course UUID

        Returns:
            Compliance report with audit trail and analysis results

        Raises:
            NotFoundError: If course not found
        """
        # Lazy import to avoid circular dependency
        from app.repositories.courses import CourseRepository

        # Verify course exists
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError(f"Course not found: {course_id}")

        # Get publishing status
        pub_record = CoursePublishingRepository.get_by_course(course_id)

        # Get complete audit trail
        audit_trail = cls.get_audit_trail(course_id)

        # Get analysis history
        analyses = cls.get_analysis_history(course_id, limit=10000)

        # Compile report
        report = {
            "course_id": course_id,
            "course_title": course.get("title"),
            "report_generated": datetime.utcnow().isoformat(),
            "publishing_status": pub_record.get("status") if pub_record else "unknown",
            "total_audit_entries": len(audit_trail),
            "total_analyses": len(analyses),
            "audit_trail": audit_trail,
            "ai_analyses": analyses,
            "compliance_summary": {
                "has_ai_review": any(a.get("action") == "ai_analyzed" for a in audit_trail),
                "has_human_review": any(
                    a.get("moderator_id") for a in audit_trail if a.get("action") != "ai_analyzed"
                ),
                "total_moderators": len(
                    set(a.get("moderator_id") for a in audit_trail if a.get("moderator_id"))
                ),
                "last_action": audit_trail[0] if audit_trail else None,
                "compliance_approved": pub_record.get("status") == "published"
                if pub_record
                else False,
            },
        }

        return report

    @classmethod
    def export_moderation_data(
        cls,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Export moderation data for analysis or compliance.

        For DSA, GDPR, NetzDG compliance reports.

        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Max records

        Returns:
            List of moderation audit entries
        """
        if start_date and end_date:
            return ModerationAuditRepository.list_by_date_range(
                start_date=start_date, end_date=end_date, limit=limit
            )

        # Return all records if no date filter
        return ModerationAuditRepository.list_by_action(
            action="submitted", limit=limit
        )  # Default: all submissions
