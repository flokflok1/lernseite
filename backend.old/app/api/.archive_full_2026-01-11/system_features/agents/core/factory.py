"""
LernsystemX Agent API - Agent Factory (OPTIONAL)

Domain-Driven Design (DDD) Factory Pattern for creating agent instances.
Centralizes business rules and default values for agent creation.

This factory is OPTIONAL and demonstrates best practices for:
- Centralized creation logic
- Testability improvements
- Type safety
- Business rule enforcement

ISO 9001:2015 compliant - Agent Factory Layer
Created: 2026-01-08
Status: REFERENCE IMPLEMENTATION (Not yet integrated)
"""

from typing import Dict, Optional
from datetime import datetime
import uuid


class AgentFactory:
    """
    Factory for creating agent instances with sensible defaults.
    Implements DDD Factory Pattern for complex object creation.

    Usage:
        # Create default agent for basic tier
        agent = AgentFactory.create_default_agent('course-123', 'basic')

        # Create custom agent
        agent = AgentFactory.create_custom_agent(
            course_id='course-123',
            name='Math Tutor',
            persona='socratic',
            temperature=0.9
        )

        # Validate before database insertion
        AgentFactory.validate_agent_config(agent)
    """

    # Default configurations by subscription tier
    DEFAULT_CONFIGS = {
        'free': {
            'temperature': 0.7,
            'max_tokens': 500,
            'primary_provider': 'openai',
            'primary_model': 'gpt-3.5-turbo',
            'fallback_provider': 'openai',
            'fallback_model': 'gpt-3.5-turbo'
        },
        'basic': {
            'temperature': 0.7,
            'max_tokens': 1000,
            'primary_provider': 'openai',
            'primary_model': 'gpt-3.5-turbo',
            'fallback_provider': 'openai',
            'fallback_model': 'gpt-3.5-turbo'
        },
        'premium': {
            'temperature': 0.8,
            'max_tokens': 2000,
            'primary_provider': 'anthropic',
            'primary_model': 'claude-3-sonnet-20240229',
            'fallback_provider': 'openai',
            'fallback_model': 'gpt-4'
        },
        'creator': {
            'temperature': 0.8,
            'max_tokens': 3000,
            'primary_provider': 'anthropic',
            'primary_model': 'claude-3-sonnet-20240229',
            'fallback_provider': 'openai',
            'fallback_model': 'gpt-4'
        },
        'enterprise': {
            'temperature': 0.9,
            'max_tokens': 4000,
            'primary_provider': 'anthropic',
            'primary_model': 'claude-opus-4-5-20251101',
            'fallback_provider': 'anthropic',
            'fallback_model': 'claude-3-sonnet-20240229'
        }
    }

    # Valid personas (from agent.py enum)
    VALID_PERSONAS = ['friendly', 'professional', 'encouraging', 'socratic']

    # Valid providers (from agent.py validation)
    VALID_PROVIDERS = ['openai', 'anthropic', 'google', 'cohere', 'huggingface']

    # Valid languages (from agent.py validation)
    VALID_LANGUAGES = ['de', 'en', 'fr', 'es', 'it', 'pt', 'nl', 'pl', 'ru', 'zh']

    @staticmethod
    def create_default_agent(course_id: str, tier: str = 'basic') -> Dict:
        """
        Create agent instance with defaults for given subscription tier.

        Args:
            course_id: Course UUID
            tier: Subscription tier (free, basic, premium, creator, enterprise)

        Returns:
            Agent dictionary ready for database insertion

        Example:
            >>> agent = AgentFactory.create_default_agent('course-123', 'premium')
            >>> assert agent['primary_provider'] == 'anthropic'
            >>> assert agent['max_tokens'] == 2000
        """
        # Get tier config or fall back to basic
        config = AgentFactory.DEFAULT_CONFIGS.get(
            tier,
            AgentFactory.DEFAULT_CONFIGS['basic']
        )

        return {
            'agent_id': str(uuid.uuid4()),
            'course_id': course_id,
            'name': 'KI-Tutor',
            'persona': 'friendly',
            'language': 'de',
            'knowledge_status': 'pending',
            'primary_provider': config['primary_provider'],
            'primary_model': config['primary_model'],
            'fallback_provider': config['fallback_provider'],
            'fallback_model': config['fallback_model'],
            'temperature': config['temperature'],
            'max_tokens': config['max_tokens'],
            'total_queries': 0,
            'cache_hits': 0,
            'tokens_saved': 0,
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def create_custom_agent(
        course_id: str,
        name: str,
        persona: str = 'friendly',
        language: str = 'de',
        tier: str = 'basic',
        **kwargs
    ) -> Dict:
        """
        Create custom agent with explicit configuration.

        Args:
            course_id: Course UUID
            name: Agent name (e.g., "Python Tutor", "Math Assistant")
            persona: Agent persona (friendly, professional, encouraging, socratic)
            language: Response language (de, en, fr, es, it, pt, nl, pl, ru, zh)
            tier: Base tier for defaults (free, basic, premium, creator, enterprise)
            **kwargs: Additional configuration overrides (temperature, max_tokens, etc.)

        Returns:
            Agent dictionary with merged defaults and custom values

        Example:
            >>> agent = AgentFactory.create_custom_agent(
            ...     course_id='course-123',
            ...     name='Math Tutor',
            ...     persona='socratic',
            ...     temperature=0.9,
            ...     max_tokens=2500
            ... )
            >>> assert agent['name'] == 'Math Tutor'
            >>> assert agent['temperature'] == 0.9
        """
        # Start with tier defaults
        agent = AgentFactory.create_default_agent(course_id, tier)

        # Override with explicit parameters
        agent.update({
            'name': name,
            'persona': persona,
            'language': language
        })

        # Apply additional custom overrides
        for key, value in kwargs.items():
            if key in agent and value is not None:
                agent[key] = value

        return agent

    @staticmethod
    def validate_agent_config(agent: Dict) -> bool:
        """
        Validate agent configuration meets business rules.

        Args:
            agent: Agent dictionary to validate

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails with descriptive error message

        Example:
            >>> agent = AgentFactory.create_default_agent('course-123')
            >>> AgentFactory.validate_agent_config(agent)  # Returns True
            >>> agent['temperature'] = 5.0
            >>> AgentFactory.validate_agent_config(agent)  # Raises ValueError
        """
        # Required fields
        required_fields = [
            'agent_id', 'course_id', 'name', 'persona',
            'language', 'knowledge_status'
        ]
        for field in required_fields:
            if field not in agent or not agent[field]:
                raise ValueError(f"Agent missing required field: {field}")

        # Validate persona
        if agent['persona'] not in AgentFactory.VALID_PERSONAS:
            raise ValueError(
                f"Invalid persona: {agent['persona']}. "
                f"Must be one of: {', '.join(AgentFactory.VALID_PERSONAS)}"
            )

        # Validate language
        if agent['language'] not in AgentFactory.VALID_LANGUAGES:
            raise ValueError(
                f"Invalid language: {agent['language']}. "
                f"Must be one of: {', '.join(AgentFactory.VALID_LANGUAGES)}"
            )

        # Validate providers
        for provider_field in ['primary_provider', 'fallback_provider']:
            if provider_field in agent and agent[provider_field]:
                if agent[provider_field] not in AgentFactory.VALID_PROVIDERS:
                    raise ValueError(
                        f"Invalid {provider_field}: {agent[provider_field]}. "
                        f"Must be one of: {', '.join(AgentFactory.VALID_PROVIDERS)}"
                    )

        # Validate temperature range
        temperature = agent.get('temperature', 0.7)
        if not (0.0 <= temperature <= 2.0):
            raise ValueError(
                f"Temperature must be between 0.0 and 2.0, got: {temperature}"
            )

        # Validate max_tokens range
        max_tokens = agent.get('max_tokens', 1000)
        if not (100 <= max_tokens <= 8000):
            raise ValueError(
                f"Max tokens must be between 100 and 8000, got: {max_tokens}"
            )

        # Validate knowledge_status
        valid_statuses = ['pending', 'warming', 'ready', 'stale']
        if agent['knowledge_status'] not in valid_statuses:
            raise ValueError(
                f"Invalid knowledge_status: {agent['knowledge_status']}. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )

        return True

    @staticmethod
    def create_from_dict(data: Dict) -> Dict:
        """
        Create agent from dictionary (e.g., from API request).

        Useful for converting API request data to validated agent instances.

        Args:
            data: Dictionary with agent parameters

        Returns:
            Validated agent dictionary

        Example:
            >>> request_data = {
            ...     'course_id': 'course-123',
            ...     'name': 'Custom Tutor',
            ...     'persona': 'socratic'
            ... }
            >>> agent = AgentFactory.create_from_dict(request_data)
        """
        course_id = data.get('course_id')
        if not course_id:
            raise ValueError("course_id is required")

        # Extract optional parameters
        name = data.get('name', 'KI-Tutor')
        persona = data.get('persona', 'friendly')
        language = data.get('language', 'de')
        tier = data.get('tier', 'basic')

        # Extract additional overrides
        overrides = {
            k: v for k, v in data.items()
            if k not in ['course_id', 'name', 'persona', 'language', 'tier']
        }

        # Create using custom method
        agent = AgentFactory.create_custom_agent(
            course_id=course_id,
            name=name,
            persona=persona,
            language=language,
            tier=tier,
            **overrides
        )

        # Validate before returning
        AgentFactory.validate_agent_config(agent)

        return agent

    @staticmethod
    def get_tier_from_user_role(role: str) -> str:
        """
        Map user role to agent tier.

        Args:
            role: User role (free, premium, creator, etc.)

        Returns:
            Corresponding agent tier

        Example:
            >>> tier = AgentFactory.get_tier_from_user_role('premium')
            >>> assert tier == 'premium'
        """
        tier_mapping = {
            'free': 'free',
            'premium': 'premium',
            'creator': 'creator',
            'teacher': 'premium',
            'school_admin': 'enterprise',
            'company_admin': 'enterprise',
            'admin': 'enterprise',
            'superadmin': 'enterprise'
        }
        return tier_mapping.get(role, 'basic')


# Example usage (for documentation purposes)
if __name__ == '__main__':
    # Example 1: Create default agent for premium user
    agent = AgentFactory.create_default_agent('course-123', 'premium')
    print("Premium Agent:", agent)

    # Example 2: Create custom agent
    custom_agent = AgentFactory.create_custom_agent(
        course_id='course-456',
        name='Math Tutor',
        persona='socratic',
        temperature=0.9
    )
    print("Custom Agent:", custom_agent)

    # Example 3: Validate agent
    try:
        AgentFactory.validate_agent_config(custom_agent)
        print("Validation: PASSED")
    except ValueError as e:
        print(f"Validation: FAILED - {e}")

    # Example 4: Create from API request data
    request_data = {
        'course_id': 'course-789',
        'name': 'Python Assistant',
        'persona': 'professional',
        'language': 'en'
    }
    api_agent = AgentFactory.create_from_dict(request_data)
    print("API Agent:", api_agent)
