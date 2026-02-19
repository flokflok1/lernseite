"""
LernsystemX AI Model Sync Service - Helper Methods

Private helper methods for building model data from model IDs and pricing.
Split from sync.py for Quality Gate G01 (max 500 lines per file).

Phase KI-Architektur - Model Management
"""

from typing import Dict, Any


class AIModelSyncHelpers:
    """
    Helper methods for AI model data construction

    Contains category detection, cost level calculation,
    display name formatting, and model description generation.
    Used as base class for AIModelSyncService.
    """

    # Category mapping based on model ID patterns
    CATEGORY_PATTERNS = {
        # OpenAI patterns
        'gpt-5': 'chat',
        'gpt-4': 'chat',
        'gpt-3': 'chat',
        'o1': 'reasoning',
        'o3': 'reasoning',
        'o4': 'reasoning',
        'dall-e': 'image',
        'gpt-image': 'image',
        'whisper': 'audio',
        'tts': 'audio',
        'gpt-audio': 'audio',
        'gpt-realtime': 'realtime',
        'text-embedding': 'embedding',
        'moderation': 'moderation',
        'sora': 'video',
        'codex': 'coding',
        'search': 'search',
        'computer-use': 'agent',
        'babbage': 'legacy',
        'davinci': 'legacy',
    }

    # Cost level mapping based on input price
    COST_LEVELS = [
        (0.0, 'free'),
        (0.0005, 'low'),
        (0.003, 'medium'),
        (0.010, 'high'),
        (float('inf'), 'very_high')
    ]

    # Speed mapping based on category/model type
    SPEED_MAP = {
        'reasoning': 'slow',
        'image': 'medium',
        'video': 'slow',
        'realtime': 'very_fast',
        'embedding': 'very_fast',
        'moderation': 'very_fast',
    }

    @classmethod
    def _build_model_data(cls, model_id: str, provider: str) -> Dict[str, Any]:
        """
        Build model data from model ID and static pricing

        Args:
            model_id: Model identifier
            provider: Provider name

        Returns:
            Model data dictionary
        """
        # Get pricing from static data
        pricing = {}
        if provider == 'openai':
            pricing = cls.OPENAI_PRICES.get(model_id, {})
        elif provider == 'anthropic':
            pricing = cls.ANTHROPIC_PRICES.get(model_id, {})
        elif provider == 'google':
            pricing = cls.GOOGLE_PRICES.get(model_id, {})

        category = cls._get_category(model_id)
        input_price = pricing.get('input_price', 0)

        return {
            'display_name': cls._format_display_name(model_id),
            'model_type': category if category in ['embedding', 'audio'] else 'chat',
            'category': category,
            'description': cls._get_model_description(model_id, provider),
            'cost_level': cls._get_cost_level(input_price),
            'speed': cls._get_speed(model_id, category),
            'context_window': pricing.get('context_window'),
            'max_output_tokens': pricing.get('max_tokens'),
            'supports_vision': cls._supports_vision(model_id, category),
            'supports_functions': category in ['chat', 'reasoning'],
            'input_price_per_1k': input_price,
            'output_price_per_1k': pricing.get('output_price', 0),
            'active': True,
            'is_default': False
        }

    @classmethod
    def _get_category(cls, model_id: str) -> str:
        """Determine model category from model ID"""
        model_lower = model_id.lower()

        for pattern, category in cls.CATEGORY_PATTERNS.items():
            if pattern in model_lower:
                return category

        return 'chat'  # Default

    @classmethod
    def _get_cost_level(cls, input_price: float) -> str:
        """Determine cost level from input price"""
        for threshold, level in cls.COST_LEVELS:
            if input_price <= threshold:
                return level
        return 'very_high'

    @classmethod
    def _get_speed(cls, model_id: str, category: str) -> str:
        """Determine model speed"""
        model_lower = model_id.lower()

        # Check category-based speed
        if category in cls.SPEED_MAP:
            return cls.SPEED_MAP[category]

        # Pattern-based speed
        if 'mini' in model_lower or 'nano' in model_lower or 'haiku' in model_lower:
            return 'very_fast'
        if 'turbo' in model_lower or 'flash' in model_lower:
            return 'fast'
        if 'pro' in model_lower and 'preview' not in model_lower:
            return 'slow'

        return 'medium'

    @classmethod
    def _supports_vision(cls, model_id: str, category: str) -> bool:
        """Check if model supports vision"""
        if category in ['image', 'video', 'moderation']:
            return True

        model_lower = model_id.lower()
        # GPT-4o and GPT-4-turbo support vision
        if 'gpt-4o' in model_lower or 'gpt-4-turbo' in model_lower:
            return True
        if 'gpt-5' in model_lower:
            return True
        if 'claude-3' in model_lower:
            return True
        if 'gemini' in model_lower:
            return True

        return False

    @classmethod
    def _format_display_name(cls, model_id: str) -> str:
        """Format model ID into display name"""
        # Common replacements
        name = model_id.replace('-', ' ').replace('_', ' ')

        # Capitalize appropriately
        parts = name.split()
        formatted = []
        for part in parts:
            if part.lower() in ['gpt', 'tts', 'hd', 'ai']:
                formatted.append(part.upper())
            elif part.isdigit() or (len(part) <= 3 and part.lower() not in ['and', 'the', 'for']):
                formatted.append(part)
            else:
                formatted.append(part.capitalize())

        return ' '.join(formatted)

    @classmethod
    def _get_model_description(cls, model_id: str, provider: str) -> str:
        """Generate model description"""
        model_lower = model_id.lower()

        descriptions = {
            'gpt-5.1': 'Latest flagship GPT model with enhanced capabilities',
            'gpt-5': 'Next-generation GPT model',
            'gpt-5-mini': 'Fast and affordable GPT-5 variant',
            'gpt-4o': 'Most capable GPT-4 model with vision',
            'gpt-4o-mini': 'Fast and cost-effective GPT-4 variant',
            'o3': 'Advanced reasoning model for complex tasks',
            'o3-mini': 'Fast reasoning model',
            'o1': 'Reasoning model for complex problem solving',
            'claude-sonnet': 'Balanced Claude model for most tasks',
            'claude-haiku': 'Fast and lightweight Claude model',
            'claude-opus': 'Most capable Claude model',
            'gemini-2.0': 'Latest Gemini model',
            'gemini-pro': 'Capable Gemini model',
            'gemini-flash': 'Fast Gemini model',
            'dall-e-3': 'Advanced image generation',
            'whisper': 'Speech-to-text transcription',
            'tts': 'Text-to-speech synthesis',
            'text-embedding': 'Text embeddings for semantic search',
        }

        for pattern, desc in descriptions.items():
            if pattern in model_lower:
                return desc

        return f'{provider.capitalize()} AI model'
