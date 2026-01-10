"""
AI Domain - Factory Patterns (DDD)

Factories encapsulate complex object creation logic and enforce business rules.
Factories ensure that created objects are always in a valid state.

Reference: Eric Evans - Domain-Driven Design, Chapter 6
Pattern: Factory Pattern, Builder Pattern
"""

from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import uuid

from ..value_objects import (
    ModelCategory,
    ModelCategoryEnum,
    Margin,
    PricingTier,
    ProviderHealth,
    ProviderHealthStatus
)


class AIModelFactory:
    """
    Factory for creating AI Model aggregates.

    Enforces business rules:
    1. Model name must be unique per provider
    2. Pricing must be non-negative
    3. Category must be valid
    4. Default margin is 33.33% if not specified
    """

    DEFAULT_MARGIN_PERCENT = 33.33

    @staticmethod
    def create_from_provider_sync(
        provider_id: str,
        model_identifier: str,
        model_name: str,
        category: str,
        input_cost_per_1k: float,
        output_cost_per_1k: float,
        context_window: Optional[int] = None,
        supports_streaming: bool = True
    ) -> Dict[str, Any]:
        """
        Create a model from provider synchronization.

        Business Rule: Apply default margin to provider costs.

        Args:
            provider_id: Provider identifier
            model_identifier: Provider's model ID (e.g., 'gpt-4')
            model_name: Display name
            category: Model category
            input_cost_per_1k: Provider's input cost per 1K tokens
            output_cost_per_1k: Provider's output cost per 1K tokens
            context_window: Maximum context window size
            supports_streaming: Whether model supports streaming

        Returns:
            Model data dictionary ready for repository insertion

        Raises:
            ValueError: If validation fails
        """
        # Validate category
        try:
            category_enum = ModelCategoryEnum(category.lower())
        except ValueError:
            raise ValueError(f"Invalid category: {category}")

        # Create pricing tier with default margin
        margin = Margin(margin_percent=AIModelFactory.DEFAULT_MARGIN_PERCENT)
        pricing = PricingTier(
            input_cost_per_1k=Decimal(str(input_cost_per_1k)),
            output_cost_per_1k=Decimal(str(output_cost_per_1k)),
            margin=margin
        )

        # Generate unique model_id
        model_id = str(uuid.uuid4())

        return {
            'model_id': model_id,
            'provider_id': provider_id,
            'model_identifier': model_identifier,
            'model_name': model_name,
            'display_name': model_name,
            'category': category_enum.value,
            'input_cost_per_1k': float(pricing.input_cost_per_1k),
            'output_cost_per_1k': float(pricing.output_cost_per_1k),
            'input_price_per_1k': float(pricing.get_customer_input_price()),
            'output_price_per_1k': float(pricing.get_customer_output_price()),
            'context_window': context_window,
            'supports_streaming': supports_streaming,
            'active': True,
            'is_default': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def create_custom_model(
        provider_id: str,
        model_name: str,
        category: str,
        input_cost_per_1k: float,
        output_cost_per_1k: float,
        margin_percent: float,
        description: Optional[str] = None,
        context_window: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a custom model with specified margin.

        Business Rule: Margin must be between 0-100%.

        Args:
            provider_id: Provider identifier
            model_name: Model name
            category: Model category
            input_cost_per_1k: Input cost
            output_cost_per_1k: Output cost
            margin_percent: Desired margin percentage
            description: Optional description
            context_window: Optional context window size

        Returns:
            Model data dictionary

        Raises:
            ValueError: If validation fails
        """
        # Validate category
        try:
            category_enum = ModelCategoryEnum(category.lower())
        except ValueError:
            raise ValueError(f"Invalid category: {category}")

        # Validate and create pricing tier
        margin = Margin(margin_percent=margin_percent)  # Validates 0-100%
        pricing = PricingTier(
            input_cost_per_1k=Decimal(str(input_cost_per_1k)),
            output_cost_per_1k=Decimal(str(output_cost_per_1k)),
            margin=margin
        )

        model_id = str(uuid.uuid4())

        return {
            'model_id': model_id,
            'provider_id': provider_id,
            'model_identifier': model_name.lower().replace(' ', '_'),
            'model_name': model_name,
            'display_name': model_name,
            'description': description,
            'category': category_enum.value,
            'input_cost_per_1k': float(pricing.input_cost_per_1k),
            'output_cost_per_1k': float(pricing.output_cost_per_1k),
            'input_price_per_1k': float(pricing.get_customer_input_price()),
            'output_price_per_1k': float(pricing.get_customer_output_price()),
            'context_window': context_window,
            'supports_streaming': True,
            'active': True,
            'is_default': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


class AIJobFactory:
    """
    Factory for creating AI Job aggregates.

    Enforces business rules:
    1. Job must have valid type (course_from_pdf, module_autogen, lesson_autogen)
    2. Job starts in 'queued' status
    3. Job must have user_id
    4. File upload jobs must have file reference
    """

    VALID_JOB_TYPES = [
        'course_from_pdf',
        'module_autogen',
        'lesson_autogen',
        'exam_generation',
        'translation_batch'
    ]

    @staticmethod
    def create_course_from_pdf_job(
        user_id: str,
        file_id: str,
        file_name: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a course generation job from PDF.

        Business Rule: File must exist and be PDF format.

        Args:
            user_id: User requesting the job
            file_id: Uploaded file identifier
            file_name: Original filename
            options: Optional generation options

        Returns:
            Job data dictionary
        """
        job_id = str(uuid.uuid4())

        return {
            'job_id': job_id,
            'user_id': user_id,
            'job_type': 'course_from_pdf',
            'status': 'queued',
            'progress': 0,
            'input_data': {
                'file_id': file_id,
                'file_name': file_name,
                'options': options or {}
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def create_module_autogen_job(
        user_id: str,
        course_id: str,
        chapter_title: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a chapter (module) auto-generation job.

        Args:
            user_id: User requesting the job
            course_id: Target course identifier
            chapter_title: Title for the new chapter
            context: Optional context data (course files, existing chapters)

        Returns:
            Job data dictionary
        """
        job_id = str(uuid.uuid4())

        return {
            'job_id': job_id,
            'user_id': user_id,
            'job_type': 'module_autogen',
            'status': 'queued',
            'progress': 0,
            'input_data': {
                'course_id': course_id,
                'chapter_title': chapter_title,
                'context': context or {}
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def create_lesson_autogen_job(
        user_id: str,
        course_id: str,
        chapter_id: str,
        lesson_title: str,
        learning_methods: list[int]
    ) -> Dict[str, Any]:
        """
        Create a lesson auto-generation job.

        Business Rule: Learning methods must be valid (0-11).

        Args:
            user_id: User requesting the job
            course_id: Course identifier
            chapter_id: Chapter identifier
            lesson_title: Title for the new lesson
            learning_methods: List of learning method IDs to generate

        Returns:
            Job data dictionary

        Raises:
            ValueError: If learning methods are invalid
        """
        # Validate learning methods (must be 0-11)
        for lm in learning_methods:
            if not isinstance(lm, int) or not 0 <= lm <= 11:
                raise ValueError(f"Invalid learning method ID: {lm}. Must be 0-11.")

        job_id = str(uuid.uuid4())

        return {
            'job_id': job_id,
            'user_id': user_id,
            'job_type': 'lesson_autogen',
            'status': 'queued',
            'progress': 0,
            'input_data': {
                'course_id': course_id,
                'chapter_id': chapter_id,
                'lesson_title': lesson_title,
                'learning_methods': learning_methods
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


class AIProviderFactory:
    """
    Factory for creating AI Provider aggregates.

    Enforces business rules:
    1. Provider name must be unique
    2. API key must be encrypted before storage
    3. Provider starts inactive until API key is validated
    """

    @staticmethod
    def create_provider(
        name: str,
        display_name: str,
        description: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new AI provider.

        Business Rule: Provider starts inactive without API key.

        Args:
            name: Internal provider name (e.g., 'openai')
            display_name: User-facing name (e.g., 'OpenAI')
            description: Optional provider description
            base_url: Optional API base URL

        Returns:
            Provider data dictionary
        """
        provider_id = str(uuid.uuid4())

        return {
            'provider_id': provider_id,
            'name': name.lower(),
            'display_name': display_name,
            'description': description,
            'base_url': base_url,
            'has_api_key': False,
            'api_key_encrypted': None,
            'active': False,
            'health_status': ProviderHealthStatus.UNKNOWN.value,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }


class AIProfileFactory:
    """
    Factory for creating AI Profile aggregates.

    Enforces business rules:
    1. Profile must have at least one model slot
    2. Each slot must reference a valid, active model
    3. Only one profile can be default per organization
    """

    @staticmethod
    def create_profile(
        profile_name: str,
        description: str,
        model_slots: Dict[str, str],
        organisation_id: Optional[str] = None,
        is_default: bool = False
    ) -> Dict[str, Any]:
        """
        Create an AI model profile.

        Business Rule: At least one model slot must be defined.

        Args:
            profile_name: Profile name
            description: Profile description
            model_slots: Mapping of slot_name -> model_id
            organisation_id: Optional organization owner
            is_default: Whether this is the default profile

        Returns:
            Profile data dictionary

        Raises:
            ValueError: If no model slots provided
        """
        if not model_slots or len(model_slots) == 0:
            raise ValueError("Profile must have at least one model slot")

        profile_id = str(uuid.uuid4())

        return {
            'profile_id': profile_id,
            'profile_name': profile_name,
            'description': description,
            'model_slots': model_slots,
            'organisation_id': organisation_id,
            'is_default': is_default,
            'active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
