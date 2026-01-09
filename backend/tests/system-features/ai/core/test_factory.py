"""
Tests for AI Domain Factories

Tests factory methods for creating domain aggregates with business rules.
"""

import pytest
from datetime import datetime

from app.api.system_features.ai.core.factory import (
    AIModelFactory,
    AIJobFactory,
    AIProviderFactory,
    AIProfileFactory
)


class TestAIModelFactory:
    """Tests for AIModelFactory."""

    def test_create_from_provider_sync(self):
        """Test creating model from provider sync."""
        model = AIModelFactory.create_from_provider_sync(
            provider_id='provider-123',
            model_identifier='gpt-4',
            model_name='GPT-4',
            category='chat',
            input_cost_per_1k=0.003,
            output_cost_per_1k=0.015,
            context_window=8192
        )

        assert model['provider_id'] == 'provider-123'
        assert model['model_identifier'] == 'gpt-4'
        assert model['model_name'] == 'GPT-4'
        assert model['category'] == 'chat'
        assert model['input_cost_per_1k'] == 0.003
        assert model['output_cost_per_1k'] == 0.015
        assert model['context_window'] == 8192
        assert model['active'] is True
        assert model['is_default'] is False

        # Check margin applied (33.33%)
        assert model['input_price_per_1k'] > model['input_cost_per_1k']
        assert model['output_price_per_1k'] > model['output_cost_per_1k']

    def test_create_from_provider_sync_invalid_category(self):
        """Test that invalid category raises ValueError."""
        with pytest.raises(ValueError, match="Invalid category"):
            AIModelFactory.create_from_provider_sync(
                provider_id='provider-123',
                model_identifier='gpt-4',
                model_name='GPT-4',
                category='invalid_category',
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015
            )

    def test_create_custom_model(self):
        """Test creating custom model with specific margin."""
        model = AIModelFactory.create_custom_model(
            provider_id='provider-123',
            model_name='Custom GPT',
            category='reasoning',
            input_cost_per_1k=0.01,
            output_cost_per_1k=0.03,
            margin_percent=50.0,
            description='Custom reasoning model'
        )

        assert model['model_name'] == 'Custom GPT'
        assert model['category'] == 'reasoning'
        assert model['description'] == 'Custom reasoning model'

        # Check 50% margin applied
        expected_input_price = 0.01 * 1.5
        expected_output_price = 0.03 * 1.5
        assert abs(model['input_price_per_1k'] - expected_input_price) < 0.0001
        assert abs(model['output_price_per_1k'] - expected_output_price) < 0.0001

    def test_create_custom_model_invalid_margin(self):
        """Test that invalid margin raises ValueError."""
        with pytest.raises(ValueError, match="between 0-100"):
            AIModelFactory.create_custom_model(
                provider_id='provider-123',
                model_name='Custom Model',
                category='chat',
                input_cost_per_1k=0.01,
                output_cost_per_1k=0.03,
                margin_percent=150.0  # Invalid
            )


class TestAIJobFactory:
    """Tests for AIJobFactory."""

    def test_create_course_from_pdf_job(self):
        """Test creating course from PDF job."""
        job = AIJobFactory.create_course_from_pdf_job(
            user_id='user-123',
            file_id='file-456',
            file_name='course.pdf',
            options={'language': 'de'}
        )

        assert job['user_id'] == 'user-123'
        assert job['job_type'] == 'course_from_pdf'
        assert job['status'] == 'queued'
        assert job['progress'] == 0
        assert job['input_data']['file_id'] == 'file-456'
        assert job['input_data']['file_name'] == 'course.pdf'
        assert job['input_data']['options']['language'] == 'de'

    def test_create_module_autogen_job(self):
        """Test creating module autogeneration job."""
        job = AIJobFactory.create_module_autogen_job(
            user_id='user-123',
            course_id='course-456',
            chapter_title='Introduction to Python',
            context={'existing_chapters': []}
        )

        assert job['job_type'] == 'module_autogen'
        assert job['status'] == 'queued'
        assert job['input_data']['course_id'] == 'course-456'
        assert job['input_data']['chapter_title'] == 'Introduction to Python'

    def test_create_lesson_autogen_job(self):
        """Test creating lesson autogeneration job."""
        job = AIJobFactory.create_lesson_autogen_job(
            user_id='user-123',
            course_id='course-456',
            chapter_id='chapter-789',
            lesson_title='Variables and Data Types',
            learning_methods=[0, 1, 2]
        )

        assert job['job_type'] == 'lesson_autogen'
        assert job['input_data']['learning_methods'] == [0, 1, 2]
        assert job['input_data']['lesson_title'] == 'Variables and Data Types'

    def test_create_lesson_autogen_invalid_learning_method(self):
        """Test that invalid learning method raises ValueError."""
        with pytest.raises(ValueError, match="Invalid learning method"):
            AIJobFactory.create_lesson_autogen_job(
                user_id='user-123',
                course_id='course-456',
                chapter_id='chapter-789',
                lesson_title='Test Lesson',
                learning_methods=[0, 1, 12]  # 12 is invalid (max 11)
            )


class TestAIProviderFactory:
    """Tests for AIProviderFactory."""

    def test_create_provider(self):
        """Test creating AI provider."""
        provider = AIProviderFactory.create_provider(
            name='openai',
            display_name='OpenAI',
            description='OpenAI API provider',
            base_url='https://api.openai.com/v1'
        )

        assert provider['name'] == 'openai'
        assert provider['display_name'] == 'OpenAI'
        assert provider['description'] == 'OpenAI API provider'
        assert provider['base_url'] == 'https://api.openai.com/v1'
        assert provider['has_api_key'] is False
        assert provider['active'] is False
        assert provider['health_status'] == 'unknown'

    def test_create_provider_name_lowercase(self):
        """Test that provider name is converted to lowercase."""
        provider = AIProviderFactory.create_provider(
            name='OpenAI',  # Mixed case
            display_name='OpenAI'
        )
        assert provider['name'] == 'openai'  # Should be lowercase


class TestAIProfileFactory:
    """Tests for AIProfileFactory."""

    def test_create_profile(self):
        """Test creating AI profile."""
        profile = AIProfileFactory.create_profile(
            profile_name='Default Profile',
            description='Standard model configuration',
            model_slots={
                'chat': 'model-123',
                'reasoning': 'model-456'
            },
            is_default=True
        )

        assert profile['profile_name'] == 'Default Profile'
        assert profile['description'] == 'Standard model configuration'
        assert profile['model_slots']['chat'] == 'model-123'
        assert profile['model_slots']['reasoning'] == 'model-456'
        assert profile['is_default'] is True
        assert profile['active'] is True

    def test_create_profile_no_slots_raises(self):
        """Test that profile without slots raises ValueError."""
        with pytest.raises(ValueError, match="at least one model slot"):
            AIProfileFactory.create_profile(
                profile_name='Empty Profile',
                description='Invalid profile',
                model_slots={}  # Empty slots
            )

    def test_create_profile_with_organisation(self):
        """Test creating profile for organisation."""
        profile = AIProfileFactory.create_profile(
            profile_name='Org Profile',
            description='Organisation-specific profile',
            model_slots={'chat': 'model-123'},
            organisation_id='org-789'
        )

        assert profile['organisation_id'] == 'org-789'
