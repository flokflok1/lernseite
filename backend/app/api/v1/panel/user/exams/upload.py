"""
Community Upload — Authenticated users upload exam PDFs for moderation.

Flow: User upload -> virus scan -> pending_review -> admin approve -> AI analysis
Requires: active subscription, PDF file, exam metadata.
"""

import os
import uuid
import logging
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

from app.api.middleware.auth import token_required, get_current_user_id
from app.core.bootstrap.extensions import limiter
from app.infrastructure.persistence.repositories.exams.core import (
    ExamRepository,
)
from app.infrastructure.persistence.repositories.exams.sessions import (
    ExamSessionRepository,
)
from app.infrastructure.persistence.repositories.subscription.user_subscriptions import (
    UserSubscriptionRepository,
)
from app.infrastructure.security.virus_scan import VirusScanService

logger = logging.getLogger(__name__)

upload_bp = Blueprint(
    'exam_community_upload', __name__,
    url_prefix='/user/exam-upload',
)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {'.pdf'}


def _validate_upload_file(file):
    """Validate uploaded file extension and size."""
    if not file or not file.filename:
        return None, 'No file provided'

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None, 'Only PDF files allowed'

    # Check Content-Length header (approximate)
    content_length = request.content_length
    if content_length and content_length > MAX_FILE_SIZE:
        return None, 'File too large (max 50 MB)'

    return ext, None


@upload_bp.route('/', methods=['POST'])
@token_required
@limiter.limit("10 per hour")
def upload_exam():
    """
    Community upload: user submits an exam PDF for moderation.

    Multipart form fields:
    - file: PDF (required)
    - exam_type_key: e.g. "IHK_FISI" (required)
    - year: e.g. 2024 (required)
    - season: "sommer" | "winter" (required)
    - part: "GA1" | "GA2" | "WK" (optional)
    - region: region code (optional, default "alle")
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401

    # 1. Subscription check
    sub = UserSubscriptionRepository.get_subscription(user_id)
    if not sub or sub.get('status') not in ('active', 'trial'):
        return jsonify({'error': 'Active subscription required'}), 403

    # 2. File validation
    file = request.files.get('file')
    ext, error = _validate_upload_file(file)
    if error:
        return jsonify({'error': error}), 400

    # 3. Required metadata
    exam_type_key = request.form.get('exam_type_key')
    year_str = request.form.get('year')
    season = request.form.get('season')

    if not exam_type_key or not year_str or not season:
        return jsonify({
            'error': 'exam_type_key, year, and season are required',
        }), 400

    try:
        year = int(year_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'year must be an integer'}), 400

    if season.lower() not in ('sommer', 'winter'):
        return jsonify({'error': 'season must be sommer or winter'}), 400

    part = request.form.get('part')
    region = request.form.get('region', 'alle')

    # 4. Save to temp location
    upload_base = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    temp_dir = os.path.join(upload_base, 'exams', 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    safe_name = secure_filename(file.filename)
    temp_filename = f"{uuid.uuid4().hex}_{safe_name}"
    temp_path = os.path.join(temp_dir, temp_filename)

    file.save(temp_path)

    # 5. Virus scan
    scan_result = VirusScanService.scan_file(temp_path)
    if not scan_result['clean']:
        _cleanup_file(temp_path)
        logger.warning(
            "Upload rejected (virus): user=%s file=%s threat=%s",
            user_id, safe_name, scan_result['threat'],
        )
        return jsonify({
            'error': 'File rejected',
            'threat': scan_result['threat'],
        }), 422

    # 6. Move to final location
    final_dir = os.path.join(
        upload_base, 'exams', 'community', str(user_id)
    )
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, temp_filename)
    os.rename(temp_path, final_path)

    # 7. Create exam record (pending_review)
    title_parts = []
    if part:
        title_parts.append(part)
    title_parts.append(exam_type_key.replace('_', ' '))
    season_label = 'Sommer' if season.lower() == 'sommer' else 'Winter'
    title_parts.append(f"{season_label} {year}")
    title = ' '.join(title_parts)

    exam_data = {
        'exam_type': 'real',
        'title': title,
        'description': f"Community-Upload von User {user_id}",
        'duration_minutes': 90,
        'passing_score': 50,
        'total_points': 100,
        'year': year,
        'season': season.lower(),
        'part': part,
        'region': region,
        'profession': exam_type_key.split('_')[-1] if '_' in exam_type_key else '',
        'pdf_path': final_path,
        'analysis_status': 'pending_review',
        'exam_type_key': exam_type_key,
        'uploaded_by': user_id,
        'upload_source': 'community',
    }
    exam_data = {k: v for k, v in exam_data.items() if v is not None}
    result = ExamRepository.create_exam(exam_data)

    if not result:
        _cleanup_file(final_path)
        return jsonify({'error': 'Failed to create exam record'}), 500

    exam_id = result['exam_id']

    # 8. Assign to session
    session = ExamSessionRepository.find_or_create(
        exam_type_key=exam_type_key,
        region=region,
        year=year,
        season=season.lower(),
    )
    if session:
        from app.infrastructure.persistence.database.connection import (
            execute_query,
        )
        execute_query(
            "UPDATE assessments.exams SET session_id = %s WHERE exam_id = %s",
            [session['session_id'], exam_id],
        )

    logger.info(
        "Community upload: user=%s exam_id=%s file=%s",
        user_id, exam_id, safe_name,
    )

    return jsonify({
        'exam_id': str(exam_id),
        'status': 'pending_review',
    }), 201


def _cleanup_file(path: str) -> None:
    """Remove a file, ignoring errors."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
