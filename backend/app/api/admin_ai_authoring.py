"""
LernsystemX Admin AI Authoring API

Universal chat-based content creation endpoints:
- POST /api/v1/admin/ai-studio/authoring/chat - Process chat message
- POST /api/v1/admin/ai-studio/authoring/preview - Generate preview
- POST /api/v1/admin/ai-studio/authoring/save - Save content
- GET /api/v1/admin/ai-studio/authoring/prompts/<context_type> - Get quick prompts
- GET /api/v1/admin/ai-studio/authoring/session/<session_id> - Get session

Actions API (DB-driven Quick-Actions):
- GET /api/v1/admin/ai-studio/actions - Get all active actions
- GET /api/v1/admin/ai-studio/actions/<category> - Get actions by category
- POST /api/v1/admin/ai-studio/actions/execute - Execute an action
- POST /api/v1/admin/ai-studio/actions - Create new action (admin only)
- PUT /api/v1/admin/ai-studio/actions/<action_id> - Update action
- DELETE /api/v1/admin/ai-studio/actions/<action_id> - Delete action

Phase D4 - Universal KI-Authoring-System
Phase DB-Zentriertes KI-Authoring (2025-12)
"""

from flask import request, jsonify, g
import logging

from app.api import api_v1
from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions

logger = logging.getLogger(__name__)


@api_v1.route('/admin/ai-studio/authoring/chat', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def authoring_chat():
    """
    Process a chat message for content creation.

    Request Body:
        {
            "course_id": "uuid",
            "context_type": "chapter|lesson|task|learning_method",
            "context_id": "uuid|null",
            "message": "User message",
            "file_context": ["file_id_1", "file_id_2"],
            "session_id": "uuid"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "response": "AI response text",
                "generated_content": {...} | null,
                "has_content": true|false,
                "tokens_used": 1234,
                "cost_eur": 0.02
            }
        }
    """
    try:
        from app.services.authoring_service import get_authoring_service, AuthoringServiceError

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        course_id = data.get('course_id')
        context_type = data.get('context_type', 'general')
        context_id = data.get('context_id')
        message = data.get('message', '')
        file_context = data.get('file_context', [])
        session_id = data.get('session_id')

        if not course_id:
            return jsonify({
                'success': False,
                'error': 'course_id is required'
            }), 400

        if not message:
            return jsonify({
                'success': False,
                'error': 'message is required'
            }), 400

        # Validate context type
        valid_types = ['chapter', 'lesson', 'task', 'learning_method', 'general']
        if context_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid context_type. Must be one of: {", ".join(valid_types)}'
            }), 400

        user_id = g.current_user['user_id']

        # Process message
        service = get_authoring_service()
        result = service.process_chat_message(
            course_id=course_id,
            context_type=context_type,
            context_id=context_id,
            message=message,
            file_context=file_context,
            session_id=session_id,
            user_id=user_id
        )

        logger.info(f"Authoring chat processed for course {course_id}, tokens: {result.get('tokens_used', 0)}")

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except AuthoringServiceError as e:
        logger.error(f"Authoring service error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Error processing authoring chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process message',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/authoring/preview', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def authoring_preview():
    """
    Generate preview of content without saving.

    Request Body:
        {
            "content_type": "chapter_theory|lesson_explanation|task|learning_method",
            "generated_content": {...},
            "format": "html|markdown"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "preview": "<html>...",
                "format": "html"
            }
        }
    """
    try:
        from app.services.authoring_service import get_authoring_service

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        content_type = data.get('content_type')
        generated_content = data.get('generated_content')
        format_type = data.get('format', 'html')

        if not content_type or not generated_content:
            return jsonify({
                'success': False,
                'error': 'content_type and generated_content are required'
            }), 400

        service = get_authoring_service()
        result = service.generate_preview(content_type, generated_content, format_type)

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate preview',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/authoring/save', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def authoring_save():
    """
    Save generated content to database.

    Request Body:
        {
            "content_type": "chapter|chapter_theory|lesson|lesson_explanation|task|learning_method",
            "content_id": "uuid|null",
            "content_data": {...}
        }

    Response 200:
        {
            "success": true,
            "data": {
                "content_type": "chapter_theory",
                "content_id": "uuid"
            }
        }
    """
    try:
        from app.services.authoring_service import get_authoring_service, AuthoringServiceError

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        content_type = data.get('content_type')
        content_id = data.get('content_id')
        content_data = data.get('content_data')

        if not content_type or not content_data:
            return jsonify({
                'success': False,
                'error': 'content_type and content_data are required'
            }), 400

        user_id = g.current_user['user_id']

        service = get_authoring_service()
        result = service.save_content(
            content_type=content_type,
            content_id=content_id,
            content_data=content_data,
            user_id=user_id
        )

        logger.info(f"Content saved: {content_type} by user {user_id}")

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except AuthoringServiceError as e:
        logger.error(f"Error saving content: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Error saving content: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to save content',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/authoring/prompts/<context_type>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_quick_prompts(context_type):
    """
    Get quick prompts for a context type.

    Path Parameters:
        context_type: chapter|lesson|task|learning_method|general

    Response 200:
        {
            "success": true,
            "data": {
                "context_type": "chapter",
                "prompts": [
                    {"label": "Theorie generieren", "prompt": "...", "icon": "..."}
                ]
            }
        }
    """
    try:
        from app.services.authoring_service import get_authoring_service

        valid_types = ['chapter', 'lesson', 'task', 'learning_method', 'general']
        if context_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid context_type. Must be one of: {", ".join(valid_types)}'
            }), 400

        service = get_authoring_service()
        prompts = service.get_quick_prompts(context_type)

        return jsonify({
            'success': True,
            'data': {
                'context_type': context_type,
                'prompts': prompts
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting quick prompts: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get prompts',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/authoring/session/<session_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_authoring_session(session_id):
    """
    Get authoring session data.

    Path Parameters:
        session_id: Session UUID

    Response 200:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "messages": [...],
                "context_type": "chapter",
                "generated_content": {...}
            }
        }
    """
    try:
        from app.services.authoring_service import AuthoringService

        session = AuthoringService.get_session(session_id)

        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        return jsonify({
            'success': True,
            'data': session
        }), 200

    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get session',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/authoring/session/<session_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def delete_authoring_session(session_id):
    """
    Delete/clear an authoring session.

    Path Parameters:
        session_id: Session UUID

    Response 200:
        {
            "success": true,
            "message": "Session deleted"
        }
    """
    try:
        from app.services.authoring_service import AuthoringService

        if session_id in AuthoringService._sessions:
            del AuthoringService._sessions[session_id]

        return jsonify({
            'success': True,
            'message': 'Session deleted'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete session',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/files/extract-context', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def extract_file_context():
    """
    Extract text context from files for AI.

    Request Body:
        {
            "file_ids": ["uuid1", "uuid2"],
            "context_type": "chapter|lesson|task|general"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "combined_text": "...",
                "files": [...],
                "total_word_count": 1234,
                "truncated": false
            }
        }
    """
    try:
        from app.services.file_context_service import FileContextService, FileContextError

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        file_ids = data.get('file_ids', [])
        context_type = data.get('context_type', 'general')

        if not file_ids:
            return jsonify({
                'success': False,
                'error': 'file_ids are required'
            }), 400

        result = FileContextService.get_file_context(file_ids)

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except FileContextError as e:
        logger.error(f"File context error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error extracting file context: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to extract context',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/analyze-material', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def analyze_material_for_course():
    """
    Analyze uploaded files and suggest course metadata.

    Request (multipart/form-data):
        files: One or more files (PDF, Word, PowerPoint, Text)
        action: "analyze_for_course"

    Response 200:
        {
            "success": true,
            "data": {
                "title": "Suggested course title",
                "description": "Suggested description",
                "category_id": 123,
                "category_name": "AP1",
                "level": "intermediate",
                "language": "de",
                "detected_topics": ["Netzwerk", "TCP/IP", ...],
                "word_count": 5000
            }
        }
    """
    try:
        from app.services.ai_adapter import AIAdapter
        from app.repositories.category_repository import CategoryRepository
        import PyPDF2
        import io

        files = request.files.getlist('files')

        if not files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400

        # Extract text from all files
        combined_text = ""
        file_names = []

        for file in files:
            file_names.append(file.filename)
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''

            try:
                if ext == 'pdf':
                    # Extract text from PDF
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                    for page in pdf_reader.pages[:20]:  # Max 20 pages
                        text = page.extract_text()
                        if text:
                            combined_text += text + "\n\n"
                elif ext in ['txt', 'md']:
                    combined_text += file.read().decode('utf-8', errors='ignore') + "\n\n"
                elif ext in ['doc', 'docx']:
                    # For Word docs, try basic extraction
                    try:
                        import docx
                        doc = docx.Document(io.BytesIO(file.read()))
                        for para in doc.paragraphs[:100]:  # Max 100 paragraphs
                            combined_text += para.text + "\n"
                    except Exception:
                        combined_text += f"[Word-Dokument: {file.filename}]\n"
                else:
                    combined_text += f"[Datei: {file.filename}]\n"
            except Exception as e:
                logger.warning(f"Could not extract text from {file.filename}: {e}")
                combined_text += f"[Datei: {file.filename}]\n"

        # Truncate if too long
        max_chars = 15000
        if len(combined_text) > max_chars:
            combined_text = combined_text[:max_chars] + "\n...[gekürzt]"

        word_count = len(combined_text.split())

        # Get available categories for the AI to choose from
        categories = CategoryRepository.get_all() or []
        category_list = ", ".join([f"{c['name']} (ID: {c['category_id']})" for c in categories[:20]])

        import json
        import re

        # Get active AI provider from database (not .env!)
        from app.repositories.ai_provider_repository import AIProviderRepository

        active_provider = AIProviderRepository.get_active_provider()
        has_ai_provider = active_provider is not None and active_provider.get('encrypted_api_key')

        # Smart fallback based on content analysis (no AI needed)
        def analyze_without_ai():
            """Analyze files without AI - extract title from filename and detect language."""
            # Clean filename for title
            raw_title = file_names[0].rsplit('.', 1)[0] if file_names else "Neuer Kurs"
            # Replace underscores and dashes with spaces, clean up
            clean_title = raw_title.replace('_', ' ').replace('-', ' ')
            clean_title = ' '.join(clean_title.split())  # Remove extra spaces

            # Detect language from content
            german_words = ['der', 'die', 'das', 'und', 'ist', 'ein', 'eine', 'für', 'mit', 'auf']
            english_words = ['the', 'and', 'is', 'a', 'an', 'for', 'with', 'on', 'to', 'of']
            text_lower = combined_text.lower()
            german_count = sum(1 for w in german_words if f' {w} ' in text_lower)
            english_count = sum(1 for w in english_words if f' {w} ' in text_lower)
            detected_lang = 'de' if german_count >= english_count else 'en'

            # Try to match category by keywords in filename/content
            matched_category = None
            for cat in categories:
                cat_name_lower = cat['name'].lower()
                if cat_name_lower in raw_title.lower() or cat_name_lower in combined_text[:2000].lower():
                    matched_category = cat
                    break

            # Generate description from first sentences
            sentences = combined_text[:500].split('.')
            description = sentences[0].strip()[:200] if sentences else f"Kurs basierend auf {len(file_names)} Datei(en)"

            return {
                'title': clean_title[:80],
                'description': description,
                'category_id': matched_category['category_id'] if matched_category else None,
                'category_name': matched_category['name'] if matched_category else None,
                'level': 'beginner',
                'language': detected_lang,
                'detected_topics': [],
                'word_count': word_count,
                'file_count': len(files),
                'ai_used': False
            }

        # If no valid AI provider configured in DB, use smart fallback
        if not has_ai_provider:
            logger.info("No AI provider configured in database, using smart fallback")
            return jsonify({
                'success': True,
                'data': analyze_without_ai()
            }), 200

        # Build AI prompt
        prompt = f"""Analysiere das folgende Kursmaterial und schlage passende Metadaten vor.

VERFÜGBARE KATEGORIEN:
{category_list}

DATEINAMEN:
{', '.join(file_names)}

MATERIAL-INHALT (Auszug):
{combined_text[:8000]}

Antworte NUR mit einem JSON-Objekt (keine Markdown-Formatierung):
{{
    "title": "Prägnanter Kurstitel (max 80 Zeichen)",
    "description": "Kursbeschreibung (2-3 Sätze, max 300 Zeichen)",
    "category_id": <ID der passendsten Kategorie oder null>,
    "level": "beginner" | "intermediate" | "advanced",
    "language": "de" | "en",
    "detected_topics": ["Thema1", "Thema2", "Thema3"]
}}"""

        try:
            # Use the active provider from database
            provider_name = active_provider.get('name', 'openai')
            provider_config = active_provider.get('config', {}) or {}

            # Determine model: use config from DB provider, or default based on provider type
            if provider_name == 'openai':
                model = provider_config.get('default_model', 'gpt-4o-mini')
            elif provider_name == 'anthropic':
                model = provider_config.get('default_model', 'claude-3-5-sonnet-20241022')
            else:
                model = provider_config.get('default_model', 'gpt-4o-mini')

            logger.info(f"Using AI provider from DB: {provider_name}, model: {model}")

            ai_response = AIAdapter.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="Du bist ein Experte für Kurserstellung. Analysiere Kursmaterialien und schlage passende Metadaten vor. Antworte immer mit validem JSON.",
                model=model,
                max_tokens=500,
                temperature=0.3,
                user_id=str(g.user_id) if hasattr(g, 'user_id') and g.user_id else None
            )

            response_text = ai_response.get('content', '{}')
            # Clean up response - remove markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text)
            response_text = re.sub(r'\s*```$', '', response_text)
            response_text = response_text.strip()

            suggestion = json.loads(response_text)

            # Add category name if category_id is set
            if suggestion.get('category_id'):
                cat = next((c for c in categories if c['category_id'] == suggestion['category_id']), None)
                if cat:
                    suggestion['category_name'] = cat['name']

            suggestion['word_count'] = word_count
            suggestion['file_count'] = len(files)
            suggestion['ai_used'] = True
            suggestion['model_used'] = model
            suggestion['provider_used'] = provider_name

            return jsonify({
                'success': True,
                'data': suggestion
            }), 200

        except Exception as ai_error:
            logger.warning(f"AI analysis failed ({ai_error}), using smart fallback")
            return jsonify({
                'success': True,
                'data': analyze_without_ai()
            }), 200

    except Exception as e:
        logger.error(f"Error analyzing material: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze material',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/files/<file_id>/preview', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_file_preview(file_id):
    """
    Get preview of a file's content.

    Path Parameters:
        file_id: File UUID

    Query Parameters:
        max_chars: Maximum characters (default 2000)

    Response 200:
        {
            "success": true,
            "data": {
                "preview": "...",
                "filename": "document.pdf",
                "file_type": "pdf",
                "word_count": 500
            }
        }
    """
    try:
        from app.services.file_context_service import FileContextService

        max_chars = request.args.get('max_chars', 2000, type=int)

        result = FileContextService.get_file_preview(file_id, max_chars)

        if 'error' in result and not result.get('preview'):
            return jsonify({
                'success': False,
                'error': result['error']
            }), 404

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        logger.error(f"Error getting file preview: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get preview',
            'message': str(e)
        }), 500


# ==============================================================================
# Authoring Actions API (DB-driven Quick-Actions)
# ==============================================================================

@api_v1.route('/admin/ai-studio/actions', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_authoring_actions():
    """
    Get all active authoring actions from database.

    Query Parameters:
        category: Optional filter by category (course_builder, chat, chapter, lesson, method, content)

    Response 200:
        {
            "success": true,
            "data": {
                "actions": [...],
                "categories": [{"category": "chat", "action_count": 4}]
            }
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository

        category = request.args.get('category')
        user_roles = g.current_user.get('roles', ['user'])

        if category:
            actions = AuthoringActionRepository.get_by_category(category, roles=user_roles)
        else:
            actions = AuthoringActionRepository.get_all_active(roles=user_roles)

        categories = AuthoringActionRepository.get_categories()

        return jsonify({
            'success': True,
            'data': {
                'actions': actions,
                'categories': categories
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting authoring actions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get actions',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/actions/<category>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_authoring_actions_by_category(category):
    """
    Get authoring actions for a specific category.

    Path Parameters:
        category: Action category (course_builder, chat, chapter, lesson, method, content)

    Response 200:
        {
            "success": true,
            "data": {
                "category": "chat",
                "actions": [...]
            }
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository

        valid_categories = ['course_builder', 'chat', 'chapter', 'lesson', 'method', 'content']
        if category not in valid_categories:
            return jsonify({
                'success': False,
                'error': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            }), 400

        user_roles = g.current_user.get('roles', ['user'])
        actions = AuthoringActionRepository.get_by_category(category, roles=user_roles)

        return jsonify({
            'success': True,
            'data': {
                'category': category,
                'actions': actions
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting actions for category {category}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get actions',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/actions/execute', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def execute_authoring_action():
    """
    Execute an authoring action.

    Request Body:
        {
            "action_id": "uuid" or "action_key": "structure_suggest",
            "course_id": "uuid",
            "context": {
                "chapter_id": "uuid",
                "lesson_id": "uuid",
                "method_id": "uuid",
                "selected_content": "text..."
            },
            "variables": {
                "topic": "...",
                "difficulty": "..."
            },
            "session_id": "uuid"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "session_id": "uuid",
                "response": "AI response",
                "generated_content": {...},
                "requires_confirmation": true,
                "tokens_used": 1234,
                "cost_eur": 0.02
            }
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository
        from app.services.authoring_service import get_authoring_service, AuthoringServiceError

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        # Get action by ID or key
        action_id = data.get('action_id')
        action_key = data.get('action_key')

        if action_id:
            action = AuthoringActionRepository.find_by_id(action_id)
        elif action_key:
            action = AuthoringActionRepository.find_by_key(action_key)
        else:
            return jsonify({
                'success': False,
                'error': 'action_id or action_key is required'
            }), 400

        if not action:
            return jsonify({
                'success': False,
                'error': 'Action not found'
            }), 404

        course_id = data.get('course_id')
        context = data.get('context', {})
        variables = data.get('variables', {})
        session_id = data.get('session_id')

        user_id = g.current_user['user_id']

        # Build prompt from template with variables
        prompt_template = action.get('prompt_template', '')
        prompt = _interpolate_prompt(prompt_template, context, variables)

        # Determine context type from action
        context_type = action.get('context_entity', 'general')
        context_id = context.get(f'{context_type}_id')

        # Process through authoring service
        service = get_authoring_service()
        result = service.process_chat_message(
            course_id=course_id,
            context_type=context_type,
            context_id=context_id,
            message=prompt,
            file_context=[],
            session_id=session_id,
            user_id=user_id
        )

        # Add action metadata to result
        result['action_id'] = action.get('action_id')
        result['action_key'] = action.get('action_key')
        result['requires_confirmation'] = action.get('requires_confirmation', False)
        result['output_entity'] = action.get('output_entity')

        # Log usage
        AuthoringActionRepository.log_usage(
            action_id=action.get('action_id'),
            user_id=user_id,
            session_id=result.get('session_id'),
            context_data=context,
            was_successful=True,
            tokens_input=result.get('tokens_input'),
            tokens_output=result.get('tokens_output'),
            cost_eur=result.get('cost_eur'),
            response_time_ms=result.get('response_time_ms')
        )

        logger.info(f"Action executed: {action.get('action_key')} by user {user_id}")

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except AuthoringServiceError as e:
        logger.error(f"Authoring service error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Error executing action: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to execute action',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/actions', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def create_authoring_action():
    """
    Create a new authoring action (admin only).

    Request Body:
        {
            "action_key": "my_custom_action",
            "category": "chat",
            "label": "My Custom Action",
            "description": "Description...",
            "icon": "emoji",
            "prompt_template": "...",
            "mode": "generate",
            ...
        }

    Response 201:
        {
            "success": true,
            "data": {...action}
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        required_fields = ['action_key', 'category', 'label', 'prompt_template']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400

        # Check if action_key already exists
        existing = AuthoringActionRepository.find_by_key(data['action_key'])
        if existing:
            return jsonify({
                'success': False,
                'error': f'Action with key "{data["action_key"]}" already exists'
            }), 409

        user_id = g.current_user['user_id']
        data['created_by'] = user_id

        action = AuthoringActionRepository.create(data)

        logger.info(f"Action created: {data['action_key']} by user {user_id}")

        return jsonify({
            'success': True,
            'data': action
        }), 201

    except Exception as e:
        logger.error(f"Error creating action: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create action',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/actions/<action_id>', methods=['PUT'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def update_authoring_action(action_id):
    """
    Update an authoring action (admin only).

    Path Parameters:
        action_id: Action UUID

    Request Body:
        {
            "label": "Updated Label",
            "prompt_template": "Updated prompt...",
            ...
        }

    Response 200:
        {
            "success": true,
            "data": {...action}
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        # Check if action exists
        existing = AuthoringActionRepository.find_by_id(action_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Action not found'
            }), 404

        user_id = g.current_user['user_id']
        data['updated_by'] = user_id

        action = AuthoringActionRepository.update(action_id, data)

        logger.info(f"Action updated: {action_id} by user {user_id}")

        return jsonify({
            'success': True,
            'data': action
        }), 200

    except Exception as e:
        logger.error(f"Error updating action: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update action',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/actions/<action_id>', methods=['DELETE'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_WRITE)
def delete_authoring_action(action_id):
    """
    Delete an authoring action (admin only, soft delete).

    System actions cannot be deleted.

    Path Parameters:
        action_id: Action UUID

    Response 200:
        {
            "success": true,
            "message": "Action deleted"
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository

        # Check if action exists
        existing = AuthoringActionRepository.find_by_id(action_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Action not found'
            }), 404

        if existing.get('is_system'):
            return jsonify({
                'success': False,
                'error': 'System actions cannot be deleted'
            }), 403

        deleted = AuthoringActionRepository.delete(action_id)

        if deleted:
            logger.info(f"Action deleted: {action_id}")
            return jsonify({
                'success': True,
                'message': 'Action deleted'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete action'
            }), 500

    except Exception as e:
        logger.error(f"Error deleting action: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete action',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/actions/entity/<entity_type>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_actions_for_entity(entity_type):
    """
    Get actions that apply to a specific entity type.

    Path Parameters:
        entity_type: Entity type (course, chapter, lesson, method)

    Response 200:
        {
            "success": true,
            "data": {
                "entity_type": "lesson",
                "actions": [...]
            }
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository

        valid_entities = ['course', 'chapter', 'lesson', 'method']
        if entity_type not in valid_entities:
            return jsonify({
                'success': False,
                'error': f'Invalid entity_type. Must be one of: {", ".join(valid_entities)}'
            }), 400

        actions = AuthoringActionRepository.get_by_context_entity(entity_type)

        return jsonify({
            'success': True,
            'data': {
                'entity_type': entity_type,
                'actions': actions
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting actions for entity {entity_type}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get actions',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/actions/stats', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_SYSTEM_READ)
def get_action_stats():
    """
    Get usage statistics for authoring actions.

    Query Parameters:
        action_id: Optional action ID to filter by
        days: Number of days to look back (default 30)

    Response 200:
        {
            "success": true,
            "data": {
                "total_uses": 1234,
                "successful_uses": 1200,
                "total_tokens": 50000,
                "total_cost": 1.50,
                "popular_actions": [...]
            }
        }
    """
    try:
        from app.repositories.authoring_action_repository import AuthoringActionRepository

        action_id = request.args.get('action_id')
        days = request.args.get('days', 30, type=int)

        stats = AuthoringActionRepository.get_usage_stats(action_id=action_id, days=days)
        popular = AuthoringActionRepository.get_popular_actions(limit=10, days=days)

        return jsonify({
            'success': True,
            'data': {
                **stats,
                'popular_actions': popular
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting action stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get stats',
            'message': str(e)
        }), 500


# =============================================================================
# LM SUGGESTIONS API - KI-gestützte Lernmethoden-Vorschläge
# =============================================================================

@api_v1.route('/admin/ai-studio/lm-suggestions', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_lm_suggestions():
    """
    Get AI-powered learning method suggestions for a lesson.

    The AI analyzes the lesson context and suggests appropriate
    learning methods from the 31 available types.

    Request Body:
        {
            "lesson_title": "Bezugskalkulation",
            "lesson_content": "Optional lesson content...",
            "chapter_title": "Kalkulation",
            "course_title": "BWL Grundlagen",
            "existing_lm_ids": [12, 19],
            "max_suggestions": 6
        }

    Response 200:
        {
            "success": true,
            "data": {
                "suggestions": [
                    {
                        "lm_id": 12,
                        "name": "Mathe-Interaktiv",
                        "group": "B",
                        "method_type": "practice",
                        "description": "...",
                        "reason": "KI-generierte Begründung",
                        "priority": 1,
                        "icon": "🧮",
                        "ki_usage": "medium"
                    },
                    ...
                ]
            }
        }
    """
    try:
        from app.services.lm_suggestion_service import LMSuggestionService

        data = request.get_json() or {}

        lesson_title = data.get('lesson_title', '')
        if not lesson_title:
            return jsonify({
                'success': False,
                'error': 'lesson_title is required'
            }), 400

        lesson_content = data.get('lesson_content', '')
        chapter_title = data.get('chapter_title', '')
        course_title = data.get('course_title', '')
        existing_lm_ids = data.get('existing_lm_ids', [])
        max_suggestions = data.get('max_suggestions', 6)

        user_id = g.current_user.get('user_id')

        # Get suggestions (sync version for now)
        suggestions = LMSuggestionService.get_suggestions_sync(
            lesson_title=lesson_title,
            lesson_content=lesson_content,
            chapter_title=chapter_title,
            course_title=course_title,
            existing_lm_ids=existing_lm_ids,
            user_id=user_id,
            max_suggestions=max_suggestions
        )

        logger.info(f"LM suggestions requested for '{lesson_title}': {len(suggestions)} suggestions")

        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'lesson_title': lesson_title,
                'existing_count': len(existing_lm_ids)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting LM suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get suggestions',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/lm-suggestions/async', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
async def get_lm_suggestions_async():
    """
    Get AI-powered learning method suggestions (async version).

    Uses the AI to analyze context and provide intelligent suggestions.
    Same request/response format as the sync version.
    """
    try:
        from app.services.lm_suggestion_service import LMSuggestionService

        data = request.get_json() or {}

        lesson_title = data.get('lesson_title', '')
        if not lesson_title:
            return jsonify({
                'success': False,
                'error': 'lesson_title is required'
            }), 400

        lesson_content = data.get('lesson_content', '')
        chapter_title = data.get('chapter_title', '')
        course_title = data.get('course_title', '')
        existing_lm_ids = data.get('existing_lm_ids', [])
        max_suggestions = data.get('max_suggestions', 6)

        user_id = g.current_user.get('user_id')

        # Get suggestions from AI
        suggestions = await LMSuggestionService.get_suggestions_from_ai(
            lesson_title=lesson_title,
            lesson_content=lesson_content,
            chapter_title=chapter_title,
            course_title=course_title,
            existing_lm_ids=existing_lm_ids,
            user_id=user_id,
            max_suggestions=max_suggestions
        )

        logger.info(f"LM suggestions (AI) for '{lesson_title}': {len(suggestions)} suggestions")

        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'lesson_title': lesson_title,
                'existing_count': len(existing_lm_ids),
                'ai_generated': True
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting LM suggestions (async): {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get AI suggestions',
            'message': str(e)
        }), 500


@api_v1.route('/admin/ai-studio/learning-methods', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_READ)
def get_all_learning_methods():
    """
    Get all 31 learning methods grouped by category.

    For manual selection when user wants to choose themselves.

    Response 200:
        {
            "success": true,
            "data": {
                "A": {
                    "name": "Erklärend",
                    "icon": "📖",
                    "methods": [...]
                },
                "B": {...},
                ...
            }
        }
    """
    try:
        from app.services.lm_suggestion_service import LMSuggestionService

        groups = LMSuggestionService.get_all_lms_grouped()

        return jsonify({
            'success': True,
            'data': groups
        }), 200

    except Exception as e:
        logger.error(f"Error getting learning methods: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning methods',
            'message': str(e)
        }), 500


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _interpolate_prompt(template: str, context: dict, variables: dict) -> str:
    """
    Interpolate variables into prompt template.

    Replaces {{variable_name}} with values from context and variables.

    Args:
        template: Prompt template with {{placeholders}}
        context: Context data (chapter_id, lesson_id, etc.)
        variables: Additional variables from request

    Returns:
        Interpolated prompt string
    """
    import re

    # Combine context and variables
    all_vars = {**context, **variables}

    def replace_var(match):
        var_name = match.group(1).strip()
        return str(all_vars.get(var_name, f'{{{{{{var_name}}}}}}'))

    # Replace {{variable}} patterns
    result = re.sub(r'\{\{([^}]+)\}\}', replace_var, template)

    return result


# ============================================================================
# Lesson Analysis Endpoint
# ============================================================================

@api_v1.route('/admin/ai-studio/analyze-lesson', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("20 per minute")
def analyze_lesson_with_files():
    """
    Analyze a lesson with selected course files to recommend learning methods.

    Request Body:
        {
            "course_id": "uuid",
            "chapter_id": "uuid",
            "chapter_title": "Chapter Title",
            "lesson_id": "uuid",
            "lesson_title": "Lesson Title",
            "file_ids": ["file_id_1", "file_id_2"],
            "request_type": "lm_recommendation"
        }

    Response 200:
        {
            "success": true,
            "data": {
                "summary": "Analysis summary",
                "recommended_lms": [
                    {"lm_id": 0, "name": "LM00 - Tiefgehende Erklärung", "reason": "..."},
                    ...
                ],
                "detected_topics": ["Topic1", "Topic2"]
            }
        }
    """
    try:
        from app.services.file_context_service import FileContextService
        from app.services.lm_suggestion_service import LMSuggestionService
        from app.repositories.ai_provider_repository import AIProviderRepository

        data = request.get_json() or {}

        course_id = data.get('course_id')
        chapter_title = data.get('chapter_title', '')
        lesson_title = data.get('lesson_title', '')
        file_ids = data.get('file_ids', [])

        if not lesson_title:
            return jsonify({
                'success': False,
                'error': 'lesson_title is required'
            }), 400

        # Get file content if files are selected
        file_context = ""
        if file_ids:
            for file_id in file_ids[:5]:  # Max 5 files
                try:
                    preview = FileContextService.get_file_preview(file_id, max_chars=3000)
                    if preview.get('preview'):
                        file_context += f"\n--- {preview.get('filename', 'Datei')} ---\n"
                        file_context += preview['preview'] + "\n"
                except Exception as e:
                    logger.warning(f"Could not get file preview for {file_id}: {e}")

        # Check if AI provider is available
        active_provider = AIProviderRepository.get_active_provider()
        has_ai = active_provider is not None and active_provider.get('encrypted_api_key')

        # Get LM suggestions using existing service methods
        suggestions = LMSuggestionService.get_suggestions_sync(
            lesson_title=lesson_title,
            lesson_content=file_context[:8000] if file_context else "",
            chapter_title=chapter_title,
            course_title="",
            existing_lm_ids=[],
            max_suggestions=6
        )

        # Build summary
        summary = f"Analyse für Lektion '{lesson_title}'"
        if chapter_title:
            summary += f" im Kapitel '{chapter_title}'"
        if file_ids:
            summary += f" mit {len(file_ids)} ausgewählten Datei(en)"

        return jsonify({
            'success': True,
            'data': {
                'summary': summary,
                'recommended_lms': suggestions,
                'file_count': len(file_ids),
                'ai_used': has_ai
            }
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing lesson: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze lesson',
            'message': str(e)
        }), 500
