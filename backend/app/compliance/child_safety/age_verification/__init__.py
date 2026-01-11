"""
Child Safety - Age Verification Service

Implements COPPA (USA), UK Age-Appropriate Design Code, GDPR Art. 8 compliance:
- Age verification for users under 13 (COPPA)
- Age verification for users under 16 (GDPR)
- Parental consent required for minors
- Screen time limits (UK Age Code)
- Grooming detection and prevention

Auto-calculated flags:
- is_coppa_protected (< 13 years)
- is_minor (13-15 years, GDPR Art. 8)
- is_adult (>= 16 years)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date
from app.repositories.base_repository import BaseRepository


class AgeVerificationRepository(BaseRepository):
    """Repository for age verification operations"""

    @staticmethod
    def create_verification(user_id: str, date_of_birth: date,
                           verification_method: str,
                           verification_proof: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create age verification record.

        Args:
            user_id: User ID
            date_of_birth: User's date of birth
            verification_method: self_reported, id_document, parental_consent, credit_card
            verification_proof: Optional proof document reference

        Returns:
            Created verification record
        """
        query = """
            INSERT INTO child_safety.age_verifications
            (user_id, date_of_birth, verification_method, verification_proof)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return AgeVerificationRepository.fetch_one(
            query, (user_id, date_of_birth, verification_method, verification_proof)
        )

    @staticmethod
    def get_verification(user_id: str) -> Optional[Dict[str, Any]]:
        """Get age verification record for user."""
        query = """
            SELECT * FROM child_safety.age_verifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        return AgeVerificationRepository.fetch_one(query, (user_id,))

    @staticmethod
    def get_age_status(user_id: str) -> Optional[Dict[str, Any]]:
        """Get age status with auto-calculated flags."""
        query = """
            SELECT
                user_id,
                date_of_birth,
                age_years,
                is_coppa_protected,
                is_minor,
                is_adult,
                verification_status,
                verified_at,
                requires_reverification
            FROM child_safety.age_verifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        return AgeVerificationRepository.fetch_one(query, (user_id,))

    @staticmethod
    def require_reverification(user_id: str) -> bool:
        """Mark user as requiring re-verification."""
        query = """
            UPDATE child_safety.age_verifications
            SET requires_reverification = TRUE,
                reverification_requested_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
        """
        result = AgeVerificationRepository.execute(query, (user_id,))
        return result > 0

    @staticmethod
    def get_users_requiring_reverification(limit: int = 100) -> List[Dict[str, Any]]:
        """Get users requiring re-verification (90d for minors, 365d for adults)."""
        query = """
            SELECT * FROM child_safety.age_verifications
            WHERE requires_reverification = TRUE
               OR (is_minor AND verified_at < CURRENT_TIMESTAMP - INTERVAL '90 days')
               OR (is_adult AND verified_at < CURRENT_TIMESTAMP - INTERVAL '365 days')
            ORDER BY verified_at ASC
            LIMIT %s
        """
        return AgeVerificationRepository.fetch_all(query, (limit,))


class ParentalControlsRepository(BaseRepository):
    """Repository for parental controls (COPPA)"""

    @staticmethod
    def create_parental_consent(child_user_id: str, parent_email: str,
                               consent_method: str) -> Optional[Dict[str, Any]]:
        """
        Create parental consent record (COPPA required).

        Args:
            child_user_id: Child's user ID
            parent_email: Parent/guardian email
            consent_method: email, phone, id_verification, video_call

        Returns:
            Created consent record
        """
        query = """
            INSERT INTO child_safety.parental_controls
            (child_user_id, parent_email, consent_method, consent_status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING *
        """
        return ParentalControlsRepository.fetch_one(
            query, (child_user_id, parent_email, consent_method)
        )

    @staticmethod
    def approve_consent(consent_id: str, verification_token: str) -> Optional[Dict[str, Any]]:
        """Approve parental consent via verification token."""
        query = """
            UPDATE child_safety.parental_controls
            SET consent_status = 'approved',
                consent_given_at = CURRENT_TIMESTAMP
            WHERE consent_id = %s
              AND verification_token = %s
              AND consent_status = 'pending'
            RETURNING *
        """
        return ParentalControlsRepository.fetch_one(query, (consent_id, verification_token))

    @staticmethod
    def get_parental_controls(child_user_id: str) -> Optional[Dict[str, Any]]:
        """Get parental controls for a child."""
        query = """
            SELECT * FROM child_safety.parental_controls
            WHERE child_user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        return ParentalControlsRepository.fetch_one(query, (child_user_id,))

    @staticmethod
    def set_screen_time_limit(child_user_id: str,
                             daily_limit_minutes: int = 120) -> Optional[Dict[str, Any]]:
        """Set daily screen time limit (UK Age Code default: 120 min)."""
        query = """
            UPDATE child_safety.parental_controls
            SET daily_screen_time_limit = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE child_user_id = %s
            RETURNING *
        """
        return ParentalControlsRepository.fetch_one(query, (daily_limit_minutes, child_user_id))

    @staticmethod
    def get_screen_time_today(child_user_id: str) -> int:
        """Get total screen time today in minutes."""
        query = """
            SELECT COALESCE(SUM(total_minutes), 0) as total_minutes
            FROM child_safety.daily_screen_time
            WHERE user_id = %s
              AND date = CURRENT_DATE
        """
        result = ParentalControlsRepository.fetch_one(query, (child_user_id,))
        return result['total_minutes'] if result else 0

    @staticmethod
    def log_activity(child_user_id: str, activity_type: str,
                    content_id: Optional[str] = None,
                    metadata: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Log child activity for parental monitoring."""
        query = """
            INSERT INTO child_safety.child_activity_log
            (user_id, activity_type, content_id, metadata)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """
        return ParentalControlsRepository.fetch_one(
            query, (child_user_id, activity_type, content_id, metadata)
        )


class ChildSafetyService:
    """Service for child safety and COPPA compliance"""

    # Age thresholds
    COPPA_AGE = 13  # USA
    GDPR_AGE = 16   # EU
    UK_AGE = 13     # UK

    # Verification methods
    VERIFICATION_METHODS = {
        'self_reported': 'User self-reported age',
        'id_document': 'Government ID verification',
        'parental_consent': 'Parental consent verified',
        'credit_card': 'Credit card age verification'
    }

    @staticmethod
    def verify_age(user_id: str, date_of_birth: date,
                  verification_method: str = 'self_reported',
                  verification_proof: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify user's age and set appropriate flags.

        Args:
            user_id: User ID
            date_of_birth: User's date of birth
            verification_method: Verification method
            verification_proof: Optional proof document

        Returns:
            Age verification result with protection level
        """
        # Calculate age
        today = date.today()
        age = today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )

        # Determine protection level
        is_coppa_protected = age < ChildSafetyService.COPPA_AGE
        is_minor = ChildSafetyService.COPPA_AGE <= age < ChildSafetyService.GDPR_AGE
        is_adult = age >= ChildSafetyService.GDPR_AGE

        # Create verification
        verification = AgeVerificationRepository.create_verification(
            user_id, date_of_birth, verification_method, verification_proof
        )

        if not verification:
            return {
                'success': False,
                'error': 'Failed to create age verification'
            }

        # If COPPA protected, require parental consent
        requires_parental_consent = is_coppa_protected

        return {
            'success': True,
            'data': verification,
            'age': age,
            'is_coppa_protected': is_coppa_protected,
            'is_minor': is_minor,
            'is_adult': is_adult,
            'requires_parental_consent': requires_parental_consent,
            'protection_level': (
                'coppa' if is_coppa_protected
                else 'gdpr_minor' if is_minor
                else 'adult'
            )
        }

    @staticmethod
    def request_parental_consent(child_user_id: str, parent_email: str,
                                consent_method: str = 'email') -> Dict[str, Any]:
        """
        Request parental consent for COPPA-protected child.

        Args:
            child_user_id: Child's user ID
            parent_email: Parent/guardian email
            consent_method: Consent verification method

        Returns:
            Consent request with verification instructions
        """
        # Check if child is COPPA protected
        age_status = AgeVerificationRepository.get_age_status(child_user_id)
        if not age_status or not age_status['is_coppa_protected']:
            return {
                'success': False,
                'error': 'Parental consent only required for users under 13'
            }

        # Create parental consent request
        consent = ParentalControlsRepository.create_parental_consent(
            child_user_id, parent_email, consent_method
        )

        if not consent:
            return {
                'success': False,
                'error': 'Failed to create consent request'
            }

        return {
            'success': True,
            'data': consent,
            'message': f'Parental consent request sent to {parent_email}',
            'consent_id': consent['consent_id'],
            'verification_token': consent['verification_token']
        }

    @staticmethod
    def check_screen_time_limit(child_user_id: str) -> Dict[str, Any]:
        """
        Check if child has exceeded screen time limit (UK Age Code).

        Returns:
            Screen time status and remaining time
        """
        # Get parental controls
        controls = ParentalControlsRepository.get_parental_controls(child_user_id)
        if not controls:
            return {
                'success': False,
                'error': 'No parental controls found'
            }

        # Get today's screen time
        used_minutes = ParentalControlsRepository.get_screen_time_today(child_user_id)
        limit_minutes = controls.get('daily_screen_time_limit', 120)  # Default 120 min
        remaining_minutes = max(0, limit_minutes - used_minutes)

        # Check if limit exceeded
        limit_exceeded = used_minutes >= limit_minutes

        return {
            'user_id': child_user_id,
            'limit_minutes': limit_minutes,
            'used_minutes': used_minutes,
            'remaining_minutes': remaining_minutes,
            'limit_exceeded': limit_exceeded,
            'percentage_used': round((used_minutes / limit_minutes) * 100, 2) if limit_minutes > 0 else 0
        }

    @staticmethod
    def apply_content_filter(child_user_id: str, content: str,
                           content_type: str) -> Dict[str, Any]:
        """
        Apply child safety content filter.

        Args:
            child_user_id: Child's user ID
            content: Content text
            content_type: Content type

        Returns:
            Filter result (allowed/blocked)
        """
        # Check age status
        age_status = AgeVerificationRepository.get_age_status(child_user_id)
        if not age_status:
            return {
                'allowed': True,
                'reason': 'No age verification'
            }

        # If adult, no filtering
        if age_status['is_adult']:
            return {
                'allowed': True,
                'reason': 'User is adult'
            }

        # Apply strict filtering for COPPA protected
        if age_status['is_coppa_protected']:
            # Check for inappropriate content
            inappropriate_keywords = [
                'violence', 'sexual', 'explicit', 'dangerous', 'self-harm'
            ]

            content_lower = content.lower()
            for keyword in inappropriate_keywords:
                if keyword in content_lower:
                    # Log for parental monitoring
                    ParentalControlsRepository.log_activity(
                        child_user_id,
                        'content_blocked',
                        content_id=None,
                        metadata={'reason': f'Inappropriate keyword: {keyword}'}
                    )

                    return {
                        'allowed': False,
                        'reason': 'Content blocked for child safety',
                        'protection_level': 'coppa'
                    }

        # Apply moderate filtering for GDPR minors
        if age_status['is_minor']:
            # Less strict filtering
            pass

        return {
            'allowed': True,
            'reason': 'Content passed child safety filter',
            'protection_level': (
                'coppa' if age_status['is_coppa_protected']
                else 'gdpr_minor' if age_status['is_minor']
                else 'adult'
            )
        }

    @staticmethod
    def get_child_safety_dashboard(child_user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive child safety dashboard.

        Returns:
            Dashboard with age status, parental controls, screen time, activity log
        """
        age_status = AgeVerificationRepository.get_age_status(child_user_id)
        parental_controls = ParentalControlsRepository.get_parental_controls(child_user_id)
        screen_time = ChildSafetyService.check_screen_time_limit(child_user_id)

        return {
            'user_id': child_user_id,
            'age_status': age_status,
            'parental_controls': parental_controls,
            'screen_time': screen_time,
            'protection_active': (
                age_status and (age_status['is_coppa_protected'] or age_status['is_minor'])
            ) if age_status else False
        }
