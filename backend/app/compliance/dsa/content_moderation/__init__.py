"""
DSA Content Moderation Service

Implements Digital Services Act (EU) Art. 14-16 requirements:
- Art. 14: Notice & Action mechanisms
- Art. 15: Statement of Reasons
- Art. 16: Internal complaint-handling system

Integrates with AI moderation, human review, and appeals process.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.repositories.base_repository import BaseRepository


class ContentModerationRepository(BaseRepository):
    """Repository for content moderation operations"""

    @staticmethod
    def create_report(reporter_id: str, content_type: str, content_id: str,
                     reason: str, description: Optional[str] = None,
                     evidence_urls: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a content report (DSA Art. 14).

        Args:
            reporter_id: User ID who reports
            content_type: post, comment, user
            content_id: ID of reported content
            reason: Report reason (hate_speech, harassment, spam, etc.)
            description: Optional detailed description
            evidence_urls: Optional evidence (screenshots, etc.)

        Returns:
            Created report record
        """
        query = """
            INSERT INTO moderation.content_reports
            (reporter_id, content_type, content_id, reason, description, evidence_urls)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        return ContentModerationRepository.fetch_one(
            query, (reporter_id, content_type, content_id, reason, description, evidence_urls)
        )

    @staticmethod
    def get_report(report_id: str) -> Optional[Dict[str, Any]]:
        """Get a content report by ID."""
        query = """
            SELECT * FROM moderation.content_reports
            WHERE report_id = %s
        """
        return ContentModerationRepository.fetch_one(query, (report_id,))

    @staticmethod
    def get_pending_reports(limit: int = 50, offset: int = 0,
                           priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pending reports for moderation queue.

        Args:
            limit: Max reports
            offset: Pagination offset
            priority: Filter by priority (critical, high, medium, low)

        Returns:
            List of pending reports
        """
        if priority:
            query = """
                SELECT * FROM moderation.content_reports
                WHERE status = 'pending'
                  AND priority = %s
                ORDER BY created_at ASC
                LIMIT %s OFFSET %s
            """
            return ContentModerationRepository.fetch_all(query, (priority, limit, offset))
        else:
            query = """
                SELECT * FROM moderation.content_reports
                WHERE status = 'pending'
                ORDER BY
                    CASE priority
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END,
                    created_at ASC
                LIMIT %s OFFSET %s
            """
            return ContentModerationRepository.fetch_all(query, (limit, offset))

    @staticmethod
    def take_action(report_id: str, moderator_id: str, action: str,
                   reason: str, internal_notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Take moderation action (DSA Art. 15 - Statement of Reasons).

        Args:
            report_id: Report ID
            moderator_id: Moderator user ID
            action: no_action, warn, remove_content, suspend_user, ban_user
            reason: Reason for action (DSA required)
            internal_notes: Optional internal notes

        Returns:
            Created action record
        """
        query = """
            INSERT INTO moderation.moderation_actions
            (report_id, moderator_id, action, reason, internal_notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        return ContentModerationRepository.fetch_one(
            query, (report_id, moderator_id, action, reason, internal_notes)
        )

    @staticmethod
    def update_report_status(report_id: str, status: str,
                            resolution_notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update report status after moderation."""
        query = """
            UPDATE moderation.content_reports
            SET status = %s,
                resolution_notes = %s,
                resolved_at = CASE WHEN %s IN ('resolved', 'rejected')
                              THEN CURRENT_TIMESTAMP ELSE resolved_at END
            WHERE report_id = %s
            RETURNING *
        """
        return ContentModerationRepository.fetch_one(
            query, (status, resolution_notes, status, report_id)
        )

    @staticmethod
    def create_appeal(user_id: str, action_id: str,
                     appeal_reason: str) -> Optional[Dict[str, Any]]:
        """
        Create an appeal for moderation action (DSA Art. 16).

        Args:
            user_id: User ID who appeals
            action_id: Moderation action ID
            appeal_reason: Reason for appeal

        Returns:
            Created appeal record
        """
        query = """
            INSERT INTO moderation.moderation_appeals
            (user_id, action_id, appeal_reason)
            VALUES (%s, %s, %s)
            RETURNING *
        """
        return ContentModerationRepository.fetch_one(query, (user_id, action_id, appeal_reason))

    @staticmethod
    def get_user_violations(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get violation history for a user."""
        query = """
            SELECT * FROM moderation.user_violations
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return ContentModerationRepository.fetch_all(query, (user_id, limit))

    @staticmethod
    def record_violation(user_id: str, violation_type: str,
                        severity: str, content_id: Optional[str] = None,
                        description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Record a user violation (3-strike system).

        Args:
            user_id: User ID
            violation_type: Type of violation
            severity: low, medium, high, critical
            content_id: Optional content ID
            description: Optional description

        Returns:
            Created violation record
        """
        query = """
            INSERT INTO moderation.user_violations
            (user_id, violation_type, severity, content_id, description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        return ContentModerationRepository.fetch_one(
            query, (user_id, violation_type, severity, content_id, description)
        )

    @staticmethod
    def get_violation_count(user_id: str, days: int = 30) -> int:
        """Get active violation count for user (last N days)."""
        query = """
            SELECT COUNT(*) as count
            FROM moderation.user_violations
            WHERE user_id = %s
              AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
              AND is_active = TRUE
        """
        result = ContentModerationRepository.fetch_one(query, (user_id, days))
        return result['count'] if result else 0


class DSAContentModeration:
    """Service for DSA-compliant content moderation"""

    # DSA-compliant report reasons
    REPORT_REASONS = {
        'illegal_content': 'Illegal content (see NetzDG)',
        'hate_speech': 'Hate speech or discrimination',
        'harassment': 'Harassment or bullying',
        'violence': 'Violence or threats',
        'sexual_content': 'Sexual or explicit content',
        'child_safety': 'Child safety concerns',
        'spam': 'Spam or scam',
        'misinformation': 'Misinformation or fake news',
        'ip_infringement': 'Intellectual property infringement',
        'privacy_violation': 'Privacy violation',
        'self_harm': 'Self-harm or suicide',
        'other': 'Other (specify in description)'
    }

    # Moderation actions
    ACTIONS = {
        'no_action': 'No action taken',
        'warn': 'Warning issued to user',
        'remove_content': 'Content removed',
        'suspend_user': 'User suspended temporarily',
        'ban_user': 'User permanently banned'
    }

    @staticmethod
    def submit_report(reporter_id: str, content_type: str, content_id: str,
                     reason: str, description: Optional[str] = None,
                     evidence_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Submit a content report (DSA Art. 14).

        Returns:
            Report confirmation with reference number
        """
        # Validate reason
        if reason not in DSAContentModeration.REPORT_REASONS:
            return {
                'success': False,
                'error': f'Invalid reason. Must be one of: {", ".join(DSAContentModeration.REPORT_REASONS.keys())}'
            }

        # Create report
        report = ContentModerationRepository.create_report(
            reporter_id, content_type, content_id, reason, description, evidence_urls
        )

        if not report:
            return {
                'success': False,
                'error': 'Failed to create report'
            }

        return {
            'success': True,
            'data': report,
            'message': 'Report submitted successfully. You will be notified of the outcome.',
            'reference_number': report['report_id']
        }

    @staticmethod
    def moderate_report(report_id: str, moderator_id: str, action: str,
                       reason: str, internal_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Moderate a report (DSA Art. 15 - Statement of Reasons).

        Args:
            report_id: Report ID
            moderator_id: Moderator user ID
            action: Moderation action
            reason: Public reason (required by DSA)
            internal_notes: Internal notes (not shown to user)

        Returns:
            Moderation result with statement of reasons
        """
        # Validate action
        if action not in DSAContentModeration.ACTIONS:
            return {
                'success': False,
                'error': f'Invalid action. Must be one of: {", ".join(DSAContentModeration.ACTIONS.keys())}'
            }

        # Get report
        report = ContentModerationRepository.get_report(report_id)
        if not report:
            return {
                'success': False,
                'error': 'Report not found'
            }

        # Take action
        moderation_action = ContentModerationRepository.take_action(
            report_id, moderator_id, action, reason, internal_notes
        )

        if not moderation_action:
            return {
                'success': False,
                'error': 'Failed to create moderation action'
            }

        # Update report status
        new_status = 'resolved' if action != 'no_action' else 'rejected'
        updated_report = ContentModerationRepository.update_report_status(
            report_id, new_status, reason
        )

        # Handle different actions
        if action in ['suspend_user', 'ban_user', 'warn']:
            # Record violation
            severity = 'critical' if action == 'ban_user' else 'high' if action == 'suspend_user' else 'medium'
            ContentModerationRepository.record_violation(
                report['reported_user_id'],
                report['reason'],
                severity,
                report['content_id'],
                reason
            )

        return {
            'success': True,
            'data': moderation_action,
            'report': updated_report,
            'statement_of_reasons': {
                'action': action,
                'reason': reason,
                'article': 'DSA Art. 15',
                'appeal_info': 'You can appeal this decision within 14 days.'
            }
        }

    @staticmethod
    def submit_appeal(user_id: str, action_id: str, appeal_reason: str) -> Dict[str, Any]:
        """
        Submit an appeal (DSA Art. 16).

        Returns:
            Appeal confirmation
        """
        appeal = ContentModerationRepository.create_appeal(user_id, action_id, appeal_reason)

        if appeal:
            return {
                'success': True,
                'data': appeal,
                'message': 'Appeal submitted. It will be reviewed within 14 days.',
                'appeal_id': appeal['appeal_id']
            }
        else:
            return {
                'success': False,
                'error': 'Failed to create appeal'
            }

    @staticmethod
    def get_moderation_queue(limit: int = 50, offset: int = 0,
                            priority: Optional[str] = None) -> Dict[str, Any]:
        """
        Get moderation queue with priority sorting.

        Returns:
            Pending reports sorted by priority
        """
        reports = ContentModerationRepository.get_pending_reports(limit, offset, priority)

        return {
            'reports': reports,
            'meta': {
                'total': len(reports),
                'limit': limit,
                'offset': offset,
                'priority_filter': priority
            }
        }

    @staticmethod
    def check_user_violations(user_id: str) -> Dict[str, Any]:
        """
        Check user violation history (3-strike system).

        Returns:
            Violation status and history
        """
        violations = ContentModerationRepository.get_user_violations(user_id, limit=10)
        count_30d = ContentModerationRepository.get_violation_count(user_id, days=30)

        status = 'clear'
        if count_30d >= 3:
            status = 'banned'
        elif count_30d == 2:
            status = 'warning'
        elif count_30d == 1:
            status = 'caution'

        return {
            'user_id': user_id,
            'status': status,
            'violations_30d': count_30d,
            'total_violations': len(violations),
            'recent_violations': violations[:5],
            'action_required': status in ['warning', 'banned']
        }
