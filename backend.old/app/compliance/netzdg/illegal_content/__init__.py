"""
NetzDG Illegal Content Service (Germany)

Implements Netzwerkdurchsetzungsgesetz requirements:
- 24h SLA for "offensichtlich rechtswidrig" (clearly illegal)
- 7d SLA for complex cases
- StGB §§ 130-187 criminal content detection
- Transparency reporting

NetzDG Categories (German Criminal Code):
- Volksverhetzung (§130 StGB) - Incitement to hatred
- Gewaltdarstellung (§131 StGB) - Depiction of violence
- Kinderpornografie (§184b StGB) - Child pornography
- Beleidigung (§185 StGB) - Insult
- Verleumdung (§187 StGB) - Defamation
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.repositories.base_repository import BaseRepository


class NetzDGRepository(BaseRepository):
    """Repository for NetzDG compliance operations"""

    @staticmethod
    def get_reports_by_sla_status(sla_status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get reports filtered by SLA status.

        Args:
            sla_status: ok, warning, breached
            limit: Max reports

        Returns:
            List of reports matching SLA status
        """
        query = """
            SELECT *,
                   CASE
                       WHEN is_clearly_illegal AND (CURRENT_TIMESTAMP - created_at) > INTERVAL '24 hours' THEN 'breached'
                       WHEN is_clearly_illegal AND (CURRENT_TIMESTAMP - created_at) > INTERVAL '20 hours' THEN 'warning'
                       WHEN NOT is_clearly_illegal AND (CURRENT_TIMESTAMP - created_at) > INTERVAL '7 days' THEN 'breached'
                       WHEN NOT is_clearly_illegal AND (CURRENT_TIMESTAMP - created_at) > INTERVAL '6 days' THEN 'warning'
                       ELSE 'ok'
                   END as sla_status,
                   CASE
                       WHEN is_clearly_illegal THEN CURRENT_TIMESTAMP - created_at <= INTERVAL '24 hours'
                       ELSE CURRENT_TIMESTAMP - created_at <= INTERVAL '7 days'
                   END as within_sla
            FROM moderation.content_reports
            WHERE status = 'pending'
              AND jurisdiction = 'DE'
            HAVING sla_status = %s
            ORDER BY created_at ASC
            LIMIT %s
        """
        return NetzDGRepository.fetch_all(query, (sla_status, limit))

    @staticmethod
    def mark_as_clearly_illegal(report_id: str) -> Optional[Dict[str, Any]]:
        """Mark report as clearly illegal (24h SLA)."""
        query = """
            UPDATE moderation.content_reports
            SET is_clearly_illegal = TRUE,
                priority = 'critical'
            WHERE report_id = %s
            RETURNING *
        """
        return NetzDGRepository.fetch_one(query, (report_id,))

    @staticmethod
    def record_transparency_data(quarter: str, total_reports: int,
                                action_taken: int, avg_response_time: float) -> Optional[Dict[str, Any]]:
        """Record transparency report data (NetzDG §2)."""
        query = """
            INSERT INTO compliance.netzdg_transparency_reports
            (quarter, total_reports, action_taken, avg_response_time_hours)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return NetzDGRepository.fetch_one(
            query, (quarter, total_reports, action_taken, avg_response_time)
        )


class NetzDGIllegalContent:
    """Service for NetzDG-compliant illegal content handling"""

    # NetzDG Categories (German Criminal Code)
    ILLEGAL_CATEGORIES = {
        'volksverhetzung': {
            'code': '§130 StGB',
            'name': 'Volksverhetzung',
            'description': 'Incitement to hatred',
            'sla_hours': 24,
            'clearly_illegal': True
        },
        'gewaltdarstellung': {
            'code': '§131 StGB',
            'name': 'Gewaltdarstellung',
            'description': 'Depiction of violence',
            'sla_hours': 24,
            'clearly_illegal': True
        },
        'kinderpornografie': {
            'code': '§184b StGB',
            'name': 'Kinderpornografie',
            'description': 'Child pornography',
            'sla_hours': 24,
            'clearly_illegal': True
        },
        'beleidigung': {
            'code': '§185 StGB',
            'name': 'Beleidigung',
            'description': 'Insult',
            'sla_hours': 168,  # 7 days
            'clearly_illegal': False
        },
        'verleumdung': {
            'code': '§187 StGB',
            'name': 'Verleumdung',
            'description': 'Defamation',
            'sla_hours': 168,
            'clearly_illegal': False
        },
        'volksverhetzung_vorbereitung': {
            'code': '§130 StGB',
            'name': 'Vorbereitung zur Volksverhetzung',
            'description': 'Preparation of incitement to hatred',
            'sla_hours': 168,
            'clearly_illegal': False
        }
    }

    @staticmethod
    def classify_content(content: str, reason: str) -> Dict[str, Any]:
        """
        Classify content for NetzDG compliance.

        Args:
            content: Content text
            reason: Report reason

        Returns:
            Classification with SLA deadline
        """
        # Check if clearly illegal (24h SLA)
        clearly_illegal = reason in [
            'volksverhetzung',
            'gewaltdarstellung',
            'kinderpornografie'
        ]

        category_info = NetzDGIllegalContent.ILLEGAL_CATEGORIES.get(reason, {
            'code': 'UNKNOWN',
            'name': 'Unknown',
            'description': 'Not categorized',
            'sla_hours': 168,
            'clearly_illegal': False
        })

        sla_deadline = datetime.utcnow() + timedelta(hours=category_info['sla_hours'])

        return {
            'category': reason,
            'stgb_code': category_info['code'],
            'name': category_info['name'],
            'description': category_info['description'],
            'clearly_illegal': clearly_illegal,
            'sla_hours': category_info['sla_hours'],
            'sla_deadline': sla_deadline.isoformat(),
            'priority': 'critical' if clearly_illegal else 'high'
        }

    @staticmethod
    def check_sla_compliance(report_created_at: datetime,
                            is_clearly_illegal: bool) -> Dict[str, Any]:
        """
        Check SLA compliance for a report.

        Args:
            report_created_at: When report was created
            is_clearly_illegal: Whether content is clearly illegal (24h) or complex (7d)

        Returns:
            SLA status and time remaining
        """
        now = datetime.utcnow()
        time_elapsed = now - report_created_at
        sla_hours = 24 if is_clearly_illegal else 168

        sla_deadline = report_created_at + timedelta(hours=sla_hours)
        time_remaining = sla_deadline - now

        # Status
        if time_remaining.total_seconds() <= 0:
            status = 'breached'
            severity = 'critical'
        elif time_remaining.total_seconds() <= 3600 * 4:  # 4h warning
            status = 'warning'
            severity = 'high'
        else:
            status = 'ok'
            severity = 'normal'

        return {
            'status': status,
            'severity': severity,
            'sla_type': '24h' if is_clearly_illegal else '7d',
            'sla_hours': sla_hours,
            'time_elapsed_hours': time_elapsed.total_seconds() / 3600,
            'time_remaining_hours': time_remaining.total_seconds() / 3600,
            'deadline': sla_deadline.isoformat(),
            'within_sla': time_remaining.total_seconds() > 0
        }

    @staticmethod
    def get_sla_dashboard() -> Dict[str, Any]:
        """
        Get NetzDG SLA compliance dashboard.

        Returns:
            Dashboard with SLA statistics
        """
        # Get reports by SLA status
        ok_reports = NetzDGRepository.get_reports_by_sla_status('ok', limit=1000)
        warning_reports = NetzDGRepository.get_reports_by_sla_status('warning', limit=1000)
        breached_reports = NetzDGRepository.get_reports_by_sla_status('breached', limit=1000)

        total = len(ok_reports) + len(warning_reports) + len(breached_reports)
        compliance_rate = ((len(ok_reports) + len(warning_reports)) / total * 100) if total > 0 else 100

        return {
            'summary': {
                'total_pending': total,
                'ok': len(ok_reports),
                'warning': len(warning_reports),
                'breached': len(breached_reports),
                'compliance_rate': round(compliance_rate, 2)
            },
            'alerts': {
                'critical': breached_reports[:10],  # Top 10 breached
                'warning': warning_reports[:10]     # Top 10 warnings
            },
            'requires_immediate_action': len(breached_reports) > 0,
            'action_items': [
                {
                    'report_id': r['report_id'],
                    'created_at': r['created_at'],
                    'sla_type': '24h' if r.get('is_clearly_illegal') else '7d',
                    'time_since_creation': (datetime.utcnow() - r['created_at']).total_seconds() / 3600
                }
                for r in breached_reports[:5]
            ]
        }

    @staticmethod
    def generate_transparency_report(quarter: str) -> Dict[str, Any]:
        """
        Generate NetzDG transparency report (§2).

        Args:
            quarter: Quarter identifier (e.g., '2024-Q1')

        Returns:
            Transparency report data
        """
        # Query reports for quarter
        query = """
            SELECT
                COUNT(*) as total_reports,
                COUNT(CASE WHEN status = 'resolved' AND action != 'no_action' THEN 1 END) as action_taken,
                AVG(EXTRACT(EPOCH FROM (resolved_at - created_at)) / 3600.0) as avg_response_time_hours,
                COUNT(CASE WHEN is_clearly_illegal THEN 1 END) as clearly_illegal_count,
                COUNT(CASE WHEN status = 'resolved'
                           AND is_clearly_illegal
                           AND (resolved_at - created_at) <= INTERVAL '24 hours' THEN 1 END) as clearly_illegal_within_sla,
                COUNT(CASE WHEN status = 'resolved'
                           AND NOT is_clearly_illegal
                           AND (resolved_at - created_at) <= INTERVAL '7 days' THEN 1 END) as complex_within_sla
            FROM moderation.content_reports
            WHERE jurisdiction = 'DE'
              AND DATE_TRUNC('quarter', created_at) = TO_DATE(%s, 'YYYY-"Q"Q')
        """

        result = NetzDGRepository.fetch_one(query, (quarter,))

        if not result:
            return {
                'success': False,
                'error': 'No data for this quarter'
            }

        # Calculate compliance rates
        clearly_illegal_rate = (
            result['clearly_illegal_within_sla'] / result['clearly_illegal_count'] * 100
        ) if result['clearly_illegal_count'] > 0 else 100

        total_complex = result['total_reports'] - result['clearly_illegal_count']
        complex_rate = (
            result['complex_within_sla'] / total_complex * 100
        ) if total_complex > 0 else 100

        # Record transparency data
        NetzDGRepository.record_transparency_data(
            quarter,
            result['total_reports'],
            result['action_taken'],
            result['avg_response_time_hours']
        )

        return {
            'quarter': quarter,
            'total_reports': result['total_reports'],
            'action_taken': result['action_taken'],
            'action_rate': round(result['action_taken'] / result['total_reports'] * 100, 2) if result['total_reports'] > 0 else 0,
            'avg_response_time_hours': round(result['avg_response_time_hours'], 2) if result['avg_response_time_hours'] else 0,
            'sla_compliance': {
                'clearly_illegal_24h': {
                    'total': result['clearly_illegal_count'],
                    'within_sla': result['clearly_illegal_within_sla'],
                    'compliance_rate': round(clearly_illegal_rate, 2)
                },
                'complex_7d': {
                    'total': total_complex,
                    'within_sla': result['complex_within_sla'],
                    'compliance_rate': round(complex_rate, 2)
                }
            },
            'generated_at': datetime.utcnow().isoformat()
        }
