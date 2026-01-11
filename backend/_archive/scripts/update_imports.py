#!/usr/bin/env python3
"""
Import Update Script für Repository Refactoring

Ersetzt alle alten *_repository Imports durch neue Unterordner-Imports
"""
import os
import re
from pathlib import Path

# Mapping: ALT → NEU
IMPORT_MAPPINGS = {
    # Authoring (11)
    'from app.repositories.authoring_changes_repository import AuthoringChangesRepository': 'from app.repositories.authoring.changes import AuthoringChangesRepository',
    'from app.repositories.authoring_finalization_repository import AuthoringFinalizationRepository': 'from app.repositories.authoring.finalization import AuthoringFinalizationRepository',
    'from app.repositories.authoring_files_repository import AuthoringFilesRepository': 'from app.repositories.authoring.files import AuthoringFilesRepository',
    'from app.repositories.authoring_analysis_repository import AuthoringAnalysisRepository': 'from app.repositories.authoring.analysis import AuthoringAnalysisRepository',
    'from app.repositories.authoring_generations_repository import AuthoringGenerationsRepository': 'from app.repositories.authoring.generations import AuthoringGenerationsRepository',
    'from app.repositories.authoring_refinements_repository import AuthoringRefinementsRepository': 'from app.repositories.authoring.refinements import AuthoringRefinementsRepository',
    'from app.repositories.authoring_user_journey_repository import AuthoringUserJourneyRepository': 'from app.repositories.authoring.user_journey import AuthoringUserJourneyRepository',
    'from app.repositories.authoring_milestones_repository import AuthoringMilestonesRepository': 'from app.repositories.authoring.milestones import AuthoringMilestonesRepository',
    'from app.repositories.authoring_dialog_messages_repository import AuthoringDialogMessagesRepository': 'from app.repositories.authoring.dialog_messages import AuthoringDialogMessagesRepository',
    'from app.repositories.authoring_plan_versions_repository import AuthoringPlanVersionsRepository': 'from app.repositories.authoring.plan_versions import AuthoringPlanVersionsRepository',
    'from app.repositories.ai_decision_explanations_repository import AIDecisionExplanationsRepository': 'from app.repositories.authoring.decision_explanations import AIDecisionExplanationsRepository',

    # AI (4)
    'from app.repositories.ai_job_repository import AIJobRepository': 'from app.repositories.ai.jobs import AIJobRepository',
    'from app.repositories.ai_model_profiles_repository import AiModelProfilesRepository': 'from app.repositories.ai.profiles import AIModelProfilesRepository',
    'from app.repositories.ai_provider_repository import AIProviderRepository': 'from app.repositories.ai.providers import AIProviderRepository',
    'from app.repositories.ai_studio_repository import AIStudioRepository': 'from app.repositories.ai.studio import AIStudioRepository',
    'from app.repositories.ai_studio_repository import PDFCacheRepository': 'from app.repositories.ai.studio import PDFCacheRepository',
    'from app.repositories.ai_studio_repository import AIStudioAnalyticsRepository': 'from app.repositories.ai.studio import AIStudioAnalyticsRepository',

    # Multi-import AI Studio
    'from app.repositories.ai_studio_repository import (': 'from app.repositories.ai.studio import (',

    # Courses (5)
    'from app.repositories.chapter_repository import ChapterRepository': 'from app.repositories.courses.chapters import ChapterRepository',
    'from app.repositories.lesson_repository import LessonRepository': 'from app.repositories.courses.lessons import LessonRepository',
    'from app.repositories.course_ai_settings_repository import CourseAiSettingsRepository': 'from app.repositories.courses.ai_settings import CourseAISettingsRepository',
    'from app.repositories.course_file_repository import CourseFileRepository': 'from app.repositories.courses.files import CourseFileRepository',
    'from app.repositories.course_repository import CourseRepository': 'from app.repositories.courses import CourseRepository',

    # Weitere (11)
    'from app.repositories.admin_repository import AdminRepository': 'from app.repositories.admin.core import AdminRepository',
    'from app.repositories.organisation_repository import OrganisationRepository': 'from app.repositories.organisations.core import OrganisationRepository',
    'from app.repositories.dashboard_repository import DashboardRepository': 'from app.repositories.dashboard.core import DashboardRepository',
    'from app.repositories.enrollment_repository import EnrollmentRepository': 'from app.repositories.enrollments.core import EnrollmentRepository',
    'from app.repositories.exam_repository import ExamRepository': 'from app.repositories.exams.core import ExamRepository',
    'from app.repositories.exam_repository import ExamQuestionRepository': 'from app.repositories.exams.core import ExamQuestionRepository',
    'from app.repositories.feedback_repository import FeedbackRepository': 'from app.repositories.feedback.core import FeedbackRepository',
    'from app.repositories.system_settings_repository import SystemSettingsRepository': 'from app.repositories.settings.system import SystemSettingsRepository',
    'from app.repositories.user_preferences_repository import UserPreferencesRepository': 'from app.repositories.settings.user_preferences import UserPreferencesRepository',
    'from app.repositories.prompt_template_repository import PromptTemplateRepository': 'from app.repositories.prompts.templates import PromptTemplateRepository',
    'from app.repositories.tts_repository import TTSRepository': 'from app.repositories.tts.core import TTSRepository',
    'from app.repositories.learning_method_instance_repository import LearningMethodInstanceRepository': 'from app.repositories.learning_method.instances import LearningMethodInstanceRepository',

    # Multi-import learning_method_instance
    'from app.repositories.learning_method_instance_repository import (': 'from app.repositories.learning_method.instances import (',

    # Bereits refactored (14) - nur Package-Import ohne .py
    'from app.repositories.user_repository import UserRepository': 'from app.repositories.user import UserRepository',
    'from app.repositories.agent_repository import AgentRepository': 'from app.repositories.agent import AgentRepository',
    'from app.repositories.token_repository import TokenRepository': 'from app.repositories.token import TokenRepository',
    'from app.repositories.subscription_repository import SubscriptionRepository': 'from app.repositories.subscription import SubscriptionRepository',
    'from app.repositories.analytics_repository import AnalyticsRepository': 'from app.repositories.analytics import AnalyticsRepository',
    'from app.repositories.knowledge_repository import KnowledgeRepository': 'from app.repositories.knowledge import KnowledgeRepository',
    'from app.repositories.learning_method_repository import LearningMethodRepository': 'from app.repositories.learning_method import LearningMethodRepository',
    'from app.repositories.ai_models_repository import AIModelsRepository': 'from app.repositories.ai_models import AIModelsRepository',
    'from app.repositories.category_repository import CategoryRepository': 'from app.repositories.category import CategoryRepository',
    'from app.repositories.course_prompt_repository import CoursePromptRepository': 'from app.repositories.course_prompt import CoursePromptRepository',
    'from app.repositories.authoring_action_repository import AuthoringActionRepository': 'from app.repositories.authoring_action import AuthoringActionRepository',
    'from app.repositories.lm_model_routing_repository import LMModelAssignmentRepository': 'from app.repositories.lm_model_routing import LMModelAssignmentRepository',
    'from app.repositories.lm_slot_repository import CapabilitySlotRepository': 'from app.repositories.lm_slot import CapabilitySlotRepository',
    'from app.repositories.lm_slot_repository import LMSlotResolverRepository': 'from app.repositories.lm_slot import LMSlotResolverRepository',

    # Multi-imports
    'from app.repositories.lm_model_routing_repository import (': 'from app.repositories.lm_model_routing import (',
    'from app.repositories.lm_slot_repository import (': 'from app.repositories.lm_slot import (',
}

def update_imports_in_file(filepath):
    """Update imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made.append(f"  {old_import} → {new_import}")

        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filepath}")
            for change in changes_made:
                print(change)
            return len(changes_made)

        return 0
    except Exception as e:
        print(f"✗ Error in {filepath}: {e}")
        return 0

def main():
    """Main update function"""
    print("=" * 80)
    print("Repository Import Update Script")
    print("=" * 80)

    backend_dir = Path(__file__).parent
    app_dir = backend_dir / 'app'

    total_files = 0
    total_changes = 0

    # Scan all Python files
    for py_file in app_dir.rglob('*.py'):
        # Skip __pycache__
        if '__pycache__' in str(py_file):
            continue

        total_files += 1
        changes = update_imports_in_file(py_file)
        total_changes += changes

    print("=" * 80)
    print(f"✓ Scanned {total_files} files")
    print(f"✓ Made {total_changes} import changes")
    print("=" * 80)

if __name__ == '__main__':
    main()
