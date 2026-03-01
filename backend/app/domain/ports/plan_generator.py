"""
Port interface for AI-powered course plan generation.

Defines the contract for a phased plan generation workflow:
  Phase 1: Generate course definition (title, description, target audience)
  Phase 2: Generate chapter structure from course metadata
  Phase 3: Generate detailed content plan with learning methods per lesson
  Plan Chat: Refine any phase via conversational interaction

Infrastructure implementations (e.g. LLM adapters) fulfill this contract.
Domain and application code depend only on this ABC.
"""

from abc import ABC, abstractmethod


class PlanGeneratorPort(ABC):
    """Port for phased course plan generation via AI."""

    @abstractmethod
    def generate_course_definition(
        self,
        topic: str,
        file_text: str | None = None,
        quality_level: str = 'standard',
        language: str = 'de',
    ) -> dict:
        """Phase 1: Generate a course definition from a topic description.

        Args:
            topic: Free-text topic description provided by the editor.
            file_text: Optional extracted text from an uploaded reference file
                       (PDF, DOCX, etc.) to give the AI additional context.

        Returns:
            dict with keys:
                title (str): Suggested course title.
                subtitle (str): One-line subtitle.
                description (str): Multi-sentence course description.
                target_audience (str): Who the course is designed for.
                prerequisites (list[str]): Recommended prior knowledge.
                estimated_duration_hours (int): Estimated total hours.
                difficulty_level (str): One of 'beginner', 'intermediate', 'advanced'.
                tags (list[str]): Suggested category tags.
        """
        ...

    @abstractmethod
    def generate_chapter_structure(
        self,
        course_meta: dict,
        file_text: str | None = None,
        quality_level: str = 'standard',
    ) -> dict:
        """Phase 2: Generate chapter structure from course metadata.

        Args:
            course_meta: The course definition dict produced by Phase 1
                         (or edited by the user afterwards).
            file_text: Optional reference file text for additional context.

        Returns:
            dict with keys:
                chapters (list[dict]): Ordered list of chapters, each with:
                    title (str): Chapter title.
                    description (str): Brief chapter summary.
                    order (int): 1-based position.
                    estimated_lessons (int): Expected number of lessons.
                    learning_goals (list[str]): What the learner achieves.
        """
        ...

    @abstractmethod
    def generate_content_plan(
        self,
        course_meta: dict,
        chapters: list[dict],
        skill_catalog_section: str = '',
        quality_level: str = 'standard',
    ) -> dict:
        """Phase 3: Generate a detailed content plan with lessons and methods.

        Args:
            course_meta: The course definition dict from Phase 1.
            chapters: The chapter list from Phase 2.
            skill_catalog_section: Pre-built skill catalog text listing
                available skill codes and didactic guidelines. Built by
                the application layer from domain skill definitions.

        Returns:
            dict with keys:
                chapters (list[dict]): Enriched chapter list, each containing:
                    title (str): Chapter title.
                    lessons (list[dict]): Ordered lessons, each with:
                        title (str): Lesson title.
                        description (str): What the lesson covers.
                        order (int): 1-based position within the chapter.
                        learning_methods (list[dict]): Suggested methods, each:
                            method_key (str): Technical key (e.g. 'flashcards').
                            rationale (str): Why this method fits.
                        system_features (list[str]): Suggested SF codes.
                        theory_summary (str): Brief theory outline.
        """
        ...

    @abstractmethod
    def chat_about_plan(
        self,
        plan_data: dict,
        message: str,
        current_phase: int,
        file_text: str | None = None,
        quality_level: str = 'standard',
        chat_history: list[dict] | None = None,
    ) -> dict:
        """Refine any plan phase via conversational interaction.

        Args:
            plan_data: The full plan state so far (course_meta, chapters,
                       content_plan -- whatever has been generated up to
                       the current phase).
            message: The user's natural-language refinement request
                     (e.g. "Add a chapter on security" or "Make it shorter").
            current_phase: Which phase the user is currently viewing (1, 2, or 3).
            file_text: Optional reference file text for additional context.
            quality_level: Quality profile key (e.g. 'standard', 'premium').
            chat_history: Previous chat messages as list of
                          {'role': 'user'|'assistant', 'content': str} dicts.
                          Used for multi-turn conversation context.

        Returns:
            dict with keys:
                response (str): The AI's conversational reply.
                updated_data (dict | None): If the AI modified the plan, the
                    updated section matching the current phase structure.
                    None if no structural change was made.
                phase (int): The phase that was affected (same as current_phase
                    unless the AI decides a different phase needs updating).
        """
        ...

    @abstractmethod
    def generate_flat_plan(
        self,
        course_title: str,
        scope: str,
        chapters: list[dict],
        language: str = 'de',
        skill_catalog_section: str = '',
    ) -> dict:
        """Generate a flat content plan in a single AI call (legacy flow).

        Args:
            course_title: Title of the course.
            scope: Plan scope ('course', 'chapter', 'lesson').
            chapters: Existing chapter list.
            language: Target language code for generated content.
            skill_catalog_section: Pre-built skill catalog text.

        Returns:
            dict with 'phases' key containing the generated plan.
        """
        ...

    @abstractmethod
    def generate_plan_from_text(
        self,
        extracted_text: str,
        language: str = 'de',
        skill_catalog_section: str = '',
    ) -> dict:
        """Generate a content plan from uploaded file text.

        Args:
            extracted_text: Full text extracted from uploaded file(s).
            language: Target language code for generated content.
            skill_catalog_section: Pre-built skill catalog text.

        Returns:
            dict with 'phases' key containing the generated plan.
        """
        ...
