"""
LernsystemX AI Course Generator Worker

Synchronous worker for AI-powered course generation from PDF:
1. Extract text from PDF
2. Generate course title via AI
3. Suggest category via AI
4. Create course description via AI
5. Generate modules via AI
6. Generate lessons per module via AI
7. Store results in output_data

Phase B24-05 - ISO 27001:2013 compliant
Architecture: Synchronous execution, can be externalized later
"""

import logging
import json
from typing import Dict, Any, Optional

from app.services.ai_adapter import AIAdapter, AIProviderError, AITimeoutError
from app.services.ai_job_service import AIJobService
from app.infrastructure.persistence.repositories.courses import CourseRepository
from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository

# Setup logger
logger = logging.getLogger(__name__)


class AICourseGenerator:
    """
    AI-powered course generator

    Workflow:
    1. PDF text extraction
    2. AI: Extract course title
    3. AI: Suggest category
    4. AI: Generate course description
    5. AI: Generate module structure
    6. AI: Generate lessons per module
    7. Save to job.output_data
    """

    def __init__(self, job_id: str, ai_provider: str = 'openai', ai_model: str = 'gpt-4o-mini'):
        """
        Initialize generator

        Args:
            job_id: AI job UUID
            ai_provider: AI provider (openai, anthropic, etc.)
            ai_model: AI model name
        """
        self.job_id = job_id
        self.ai_provider = ai_provider
        self.ai_model = ai_model
        self.ai_adapter = None

    def run(self) -> bool:
        """
        Execute course generation workflow

        Returns:
            True if successful, False otherwise
        """
        try:
            # Mark job as processing
            AIJobService.start_processing(self.job_id)
            AIJobService.update_progress(self.job_id, 10)

            # Get job
            job = AIJobService.get_job(self.job_id)
            if not job:
                logger.error(f'Job not found: {self.job_id}')
                return False

            # Initialize AI adapter
            try:
                self.ai_adapter = AIAdapter(provider=self.ai_provider, model=self.ai_model)
            except Exception as e:
                error_msg = f'Failed to initialize AI adapter: {str(e)}'
                logger.error(error_msg)
                AIJobService.fail_job(self.job_id, error_msg)
                return False

            # Step 1: Extract PDF text
            # Get file path from storage_path (full path) or input_data (JSONB)
            file_path = job.get('storage_path')
            input_data = job.get('input_data', {})
            if isinstance(input_data, str):
                import json as json_module
                input_data = json_module.loads(input_data) if input_data else {}

            # Get prompt from input_data
            user_prompt = input_data.get('prompt')

            logger.info(f'Job data: storage_path={file_path}, input_data={input_data}')

            pdf_text = self._extract_pdf_text(file_path)
            AIJobService.update_progress(self.job_id, 20)

            # Step 2: Generate course title
            course_title = self._generate_course_title(pdf_text, user_prompt)
            AIJobService.update_progress(self.job_id, 30)

            # Step 3: Suggest category
            category = self._suggest_category(pdf_text, course_title)
            AIJobService.update_progress(self.job_id, 40)

            # Step 4: Generate course description
            description = self._generate_description(pdf_text, course_title)
            AIJobService.update_progress(self.job_id, 50)

            # Step 5: Generate module structure
            modules = self._generate_modules(pdf_text, course_title)
            AIJobService.update_progress(self.job_id, 70)

            # Step 6: Generate lessons per module
            for i, module in enumerate(modules):
                lessons = self._generate_lessons(pdf_text, module)
                module['lessons'] = lessons
                progress = 70 + int((i + 1) / len(modules) * 20)
                AIJobService.update_progress(self.job_id, progress)

            AIJobService.update_progress(self.job_id, 95)

            # Step 7: Save output data
            output_data = {
                'course': {
                    'title': course_title,
                    'description': description,
                    'category': category,
                    'level': 'beginner',  # Can be AI-determined later
                    'language': 'de'
                },
                'modules': modules
            }

            AIJobService.update_output(self.job_id, output_data)
            AIJobService.complete_job(self.job_id)

            logger.info(f'AI course generation completed: {self.job_id}')
            return True

        except (AIProviderError, AITimeoutError) as e:
            error_msg = f'AI provider error: {str(e)}'
            logger.error(error_msg)
            AIJobService.fail_job(self.job_id, error_msg)
            return False

        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logger.exception(error_msg)
            AIJobService.fail_job(self.job_id, error_msg)
            return False

    def _extract_pdf_text(self, file_path: Optional[str]) -> str:
        """
        Extract text from PDF using PyPDF2

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        if not file_path:
            logger.warning('No PDF file path provided')
            return ""

        import os
        if not os.path.exists(file_path):
            logger.warning(f'PDF file not found: {file_path}')
            return ""

        try:
            from PyPDF2 import PdfReader

            logger.info(f'Extracting text from PDF: {file_path}')
            reader = PdfReader(file_path)
            text_parts = []

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(f'Extracted {len(page_text)} chars from page {page_num + 1}')
                except Exception as e:
                    logger.warning(f'Failed to extract text from page {page_num + 1}: {str(e)}')

            full_text = '\n\n'.join(text_parts)
            logger.info(f'PDF text extraction complete: {len(full_text)} characters from {len(reader.pages)} pages')

            if not full_text.strip():
                logger.warning('PDF extraction returned empty text - PDF might be scanned/image-based')
                return ""

            return full_text

        except ImportError:
            logger.error('PyPDF2 not installed. Install with: pip install PyPDF2')
            return ""
        except Exception as e:
            logger.error(f'PDF extraction failed: {str(e)}')
            return ""

    def _generate_course_title(self, pdf_text: str, user_prompt: Optional[str]) -> str:
        """
        Generate course title via AI

        Args:
            pdf_text: Extracted PDF text
            user_prompt: Optional user guidance

        Returns:
            Generated course title
        """
        prompt = f"""Analysiere diesen Lerninhalt und erstelle einen prägnanten, beschreibenden Kurstitel (max 100 Zeichen).

Inhalt:
{pdf_text[:1000]}

{("Benutzeranweisung: " + user_prompt) if user_prompt else ""}

WICHTIG: Antworte NUR mit dem Kurstitel als reiner Text. Kein JSON, keine Formatierung, keine Anführungszeichen, keine Erklärungen."""

        try:
            response = self.ai_adapter.send_request(
                prompt=prompt,
                language='de',
                temperature=0.7,
                max_tokens=50
            )
            title = response['output_text'].strip()
            # Clean up any JSON formatting the AI might have added
            title = self._clean_ai_text_response(title)
            return title if title else "AI-Generated Course"
        except Exception as e:
            logger.warning(f'AI title generation failed, using fallback: {str(e)}')
            return "AI-Generated Course"

    def _suggest_category(self, pdf_text: str, course_title: str) -> str:
        """
        Suggest course category via AI

        Args:
            pdf_text: Extracted PDF text
            course_title: Course title

        Returns:
            Suggested category
        """
        prompt = f"""Based on this course title and content, suggest the most appropriate category from this list:
- programming
- business
- design
- marketing
- languages
- science
- mathematics
- health
- personal-development
- other

Course title: {course_title}
Content: {pdf_text[:500]}

Respond with ONLY the category name (lowercase, hyphenated), nothing else."""

        try:
            response = self.ai_adapter.send_request(
                prompt=prompt,
                language='en',
                temperature=0.3,
                max_tokens=20
            )
            category = response['output_text'].strip().lower()
            valid_categories = ['programming', 'business', 'design', 'marketing', 'languages', 'science', 'mathematics', 'health', 'personal-development', 'other']
            return category if category in valid_categories else 'other'
        except Exception as e:
            logger.warning(f'AI category suggestion failed, using fallback: {str(e)}')
            return 'other'

    def _generate_description(self, pdf_text: str, course_title: str) -> str:
        """
        Generate course description via AI

        Args:
            pdf_text: Extracted PDF text
            course_title: Course title

        Returns:
            Generated description
        """
        prompt = f"""Create a compelling course description (2-3 sentences, max 300 characters) for:

Title: {course_title}
Content: {pdf_text[:1000]}

The description should highlight what students will learn and the course benefits.
Respond with ONLY the description, nothing else."""

        try:
            response = self.ai_adapter.send_request(
                prompt=prompt,
                language='de',
                temperature=0.7,
                max_tokens=150
            )
            return response['output_text'].strip()
        except Exception as e:
            logger.warning(f'AI description generation failed, using fallback: {str(e)}')
            return f"Lerne alles über {course_title} in diesem umfassenden Kurs."

    def _generate_modules(self, pdf_text: str, course_title: str) -> list[Dict[str, Any]]:
        """
        Generate module structure via AI

        Args:
            pdf_text: Extracted PDF text
            course_title: Course title

        Returns:
            List of module dicts (without lessons)
        """
        prompt = f"""Analyze this course content and create a logical module structure (3-6 modules).

Course: {course_title}
Content: {pdf_text[:2000]}

Return a JSON array of modules with this format:
[
  {{"title": "Module 1: Introduction", "description": "Overview and basics", "duration_minutes": 45}},
  {{"title": "Module 2: Core Concepts", "description": "Main topics", "duration_minutes": 60}}
]

Respond with ONLY valid JSON, nothing else."""

        try:
            response = self.ai_adapter.send_request(
                prompt=prompt,
                language='de',
                temperature=0.7,
                max_tokens=500
            )

            # Parse JSON response
            modules_json = response['output_text'].strip()
            modules = json.loads(modules_json)

            # Validate and add order_index
            validated_modules = []
            for i, module in enumerate(modules[:6], start=1):  # Max 6 modules
                validated_modules.append({
                    'title': module.get('title', f'Modul {i}'),
                    'description': module.get('description', ''),
                    'duration_minutes': module.get('duration_minutes', 60),
                    'order_index': i
                })

            return validated_modules if validated_modules else self._get_fallback_modules()

        except Exception as e:
            logger.warning(f'AI module generation failed, using fallback: {str(e)}')
            return self._get_fallback_modules()

    def _generate_lessons(self, pdf_text: str, module: Dict[str, Any]) -> list[Dict[str, Any]]:
        """
        Generate lessons for a module via AI

        Args:
            pdf_text: Extracted PDF text
            module: Module dict

        Returns:
            List of lesson dicts
        """
        prompt = f"""Create 3-5 lessons for this module:

Module: {module['title']}
Description: {module.get('description', '')}
Context: {pdf_text[:1000]}

Return a JSON array of lessons with this format:
[
  {{"title": "Lesson 1: Introduction", "lesson_type": "text", "duration_minutes": 15}},
  {{"title": "Lesson 2: Practice", "lesson_type": "quiz", "duration_minutes": 20}}
]

Valid lesson_types: text, video, quiz, interactive, assignment, discussion
Respond with ONLY valid JSON, nothing else."""

        try:
            response = self.ai_adapter.send_request(
                prompt=prompt,
                language='de',
                temperature=0.7,
                max_tokens=400
            )

            # Parse JSON response
            lessons_json = response['output_text'].strip()
            lessons = json.loads(lessons_json)

            # Validate and add order_index
            validated_lessons = []
            for i, lesson in enumerate(lessons[:5], start=1):  # Max 5 lessons
                validated_lessons.append({
                    'title': lesson.get('title', f'Lektion {i}'),
                    'lesson_type': lesson.get('lesson_type', 'text'),
                    'duration_minutes': lesson.get('duration_minutes', 15),
                    'order_index': i
                })

            return validated_lessons if validated_lessons else self._get_fallback_lessons()

        except Exception as e:
            logger.warning(f'AI lesson generation failed, using fallback: {str(e)}')
            return self._get_fallback_lessons()

    @staticmethod
    def _clean_ai_text_response(text: str) -> str:
        """
        Clean up AI response that might contain JSON formatting.

        Handles cases where AI returns:
        - ```json{...}```
        - {"key": "value"}
        - "quoted text"

        Args:
            text: Raw AI response text

        Returns:
            Clean text without JSON formatting
        """
        import re

        # Remove markdown code blocks
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = re.sub(r'```\s*$', '', text)

        # Try to extract value from JSON if it looks like JSON
        if text.strip().startswith('{') and text.strip().endswith('}'):
            try:
                data = json.loads(text.strip())
                # Look for common keys that might contain the title
                for key in ['course_title', 'title', 'name', 'course_name']:
                    if key in data:
                        return str(data[key]).strip()
                # If no known key, return first string value
                for value in data.values():
                    if isinstance(value, str):
                        return value.strip()
            except json.JSONDecodeError:
                pass

        # Remove surrounding quotes
        text = text.strip().strip('"\'')

        return text.strip()

    @staticmethod
    def _get_fallback_modules() -> list[Dict[str, Any]]:
        """Get fallback module structure"""
        return [
            {'title': 'Modul 1: Einführung', 'description': 'Grundlagen und Überblick', 'duration_minutes': 45, 'order_index': 1},
            {'title': 'Modul 2: Hauptthemen', 'description': 'Kernkonzepte', 'duration_minutes': 60, 'order_index': 2},
            {'title': 'Modul 3: Praxis', 'description': 'Übungen und Anwendungen', 'duration_minutes': 60, 'order_index': 3}
        ]

    @staticmethod
    def _get_fallback_lessons() -> list[Dict[str, Any]]:
        """Get fallback lesson structure"""
        return [
            {'title': 'Lektion 1: Einführung', 'lesson_type': 'text', 'duration_minutes': 15, 'order_index': 1},
            {'title': 'Lektion 2: Konzepte', 'lesson_type': 'text', 'duration_minutes': 20, 'order_index': 2},
            {'title': 'Lektion 3: Quiz', 'lesson_type': 'quiz', 'duration_minutes': 10, 'order_index': 3}
        ]


def run_ai_course_generation(job_id: str, ai_provider: str = 'openai', ai_model: str = 'gpt-4o-mini') -> bool:
    """
    Main entry point for AI course generation

    Args:
        job_id: AI job UUID
        ai_provider: AI provider
        ai_model: AI model name (default, may be overridden by job.model)

    Returns:
        True if successful, False otherwise
    """
    from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository

    # Phase C3.4: Check if job has a model override
    job = AIJobRepository.find_by_id(job_id)
    if job and job.get('model'):
        ai_model = job['model']
        logger.info(f'Using job model override: {ai_model}')

    generator = AICourseGenerator(job_id, ai_provider, ai_model)
    return generator.run()
