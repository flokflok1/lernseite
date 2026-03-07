"""
LernsystemX AI Adapter - Configuration

Provider API configurations. Model lists and pricing are managed
exclusively in the database (ai_pipeline.ai_models table).
Sync discovers new models via provider APIs; prices are set in Admin Panel.
"""

from typing import Dict, Any

# Provider configurations — API endpoints and key env vars only.
# Model data lives in the DB (Single Source of Truth).
PROVIDERS: Dict[str, Dict[str, Any]] = {
    'openai': {
        'api_url': 'https://api.openai.com/v1/chat/completions',
        'api_key_env': 'OPENAI_API_KEY',
        'display_name': 'OpenAI',
    },
    'anthropic': {
        'api_url': 'https://api.anthropic.com/v1/messages',
        'api_key_env': 'ANTHROPIC_API_KEY',
        'display_name': 'Anthropic',
    },
    'google': {
        'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        'api_key_env': 'GOOGLE_API_KEY',
        'display_name': 'Google',
    },
    'cohere': {
        'api_url': 'https://api.cohere.ai/v1/chat',
        'api_key_env': 'COHERE_API_KEY',
        'display_name': 'Cohere',
    },
    'huggingface': {
        'api_url': 'https://api-inference.huggingface.co/models/{model}',
        'api_key_env': 'HUGGINGFACE_API_KEY',
        'display_name': 'HuggingFace',
    },
}

# Default models for specialized APIs (not chat — no DB tracking needed)
DEFAULT_TTS_MODEL = 'tts-1'
DEFAULT_WHISPER_MODEL = 'whisper-1'

# Models that require max_completion_tokens instead of max_tokens
# (GPT-5 series, O-series reasoning models, O4 series)
MODELS_USING_COMPLETION_TOKENS = [
    'gpt-5', 'gpt-5.1', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro',
    'gpt-5.1-chat-latest', 'gpt-5-chat-latest',
    'gpt-5.1-codex', 'gpt-5-codex', 'gpt-5.1-codex-mini',
    'o1', 'o1-pro', 'o1-mini', 'o1-preview',
    'o3', 'o3-pro', 'o3-mini', 'o3-deep-research',
    'o4-mini', 'o4-mini-deep-research'
]
