"""
LernsystemX AI Adapter - Configuration

Provider configurations and model definitions for all supported AI providers.
"""

from typing import Dict, Any

# Provider configurations with API endpoints and model pricing
PROVIDERS: Dict[str, Dict[str, Any]] = {
    'openai': {
        'api_url': 'https://api.openai.com/v1/chat/completions',
        'api_key_env': 'OPENAI_API_KEY',
        'display_name': 'OpenAI',
        'models': {
            # GPT-5 Series (2025) - Latest flagship models
            'gpt-5.1': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},
            'gpt-5': {'input_price': 0.004, 'output_price': 0.016, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},
            'gpt-5-mini': {'input_price': 0.001, 'output_price': 0.004, 'max_tokens': 32768, 'context_window': 128000, 'category': 'chat'},
            'gpt-5-nano': {'input_price': 0.0002, 'output_price': 0.0008, 'max_tokens': 16384, 'context_window': 64000, 'category': 'chat'},
            'gpt-5-pro': {'input_price': 0.010, 'output_price': 0.040, 'max_tokens': 128000, 'context_window': 512000, 'category': 'chat'},
            'gpt-5.1-chat-latest': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},
            'gpt-5-chat-latest': {'input_price': 0.004, 'output_price': 0.016, 'max_tokens': 64000, 'context_window': 256000, 'category': 'chat'},

            # GPT-5 Codex Series (2025) - Code generation specialists
            'gpt-5.1-codex': {'input_price': 0.006, 'output_price': 0.024, 'max_tokens': 64000, 'context_window': 256000, 'category': 'coding'},
            'gpt-5-codex': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 64000, 'context_window': 256000, 'category': 'coding'},
            'gpt-5.1-codex-mini': {'input_price': 0.002, 'output_price': 0.008, 'max_tokens': 32768, 'context_window': 128000, 'category': 'coding'},

            # O-Series Reasoning Models (2025) - Deep reasoning capabilities
            'o3': {'input_price': 0.010, 'output_price': 0.040, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
            'o3-pro': {'input_price': 0.020, 'output_price': 0.080, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
            'o3-mini': {'input_price': 0.0011, 'output_price': 0.0044, 'max_tokens': 65536, 'context_window': 200000, 'category': 'reasoning'},
            'o3-deep-research': {'input_price': 0.030, 'output_price': 0.120, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
            'o4-mini': {'input_price': 0.0011, 'output_price': 0.0044, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
            'o4-mini-deep-research': {'input_price': 0.010, 'output_price': 0.040, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
            'o1': {'input_price': 0.015, 'output_price': 0.060, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
            'o1-pro': {'input_price': 0.150, 'output_price': 0.600, 'max_tokens': 100000, 'context_window': 200000, 'category': 'reasoning'},
            'o1-mini': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 65536, 'context_window': 128000, 'category': 'reasoning'},
            'o1-preview': {'input_price': 0.015, 'output_price': 0.060, 'max_tokens': 32768, 'context_window': 128000, 'category': 'reasoning'},

            # GPT-4.1 Series (2025) - Smartest non-reasoning models
            'gpt-4.1': {'input_price': 0.002, 'output_price': 0.008, 'max_tokens': 32768, 'context_window': 1000000, 'category': 'chat'},
            'gpt-4.1-mini': {'input_price': 0.0004, 'output_price': 0.0016, 'max_tokens': 32768, 'context_window': 1000000, 'category': 'chat'},
            'gpt-4.1-nano': {'input_price': 0.0001, 'output_price': 0.0004, 'max_tokens': 32768, 'context_window': 1000000, 'category': 'chat'},

            # GPT-4o Series (Multimodal - Text, Vision, Audio)
            'gpt-4o': {'input_price': 0.0025, 'output_price': 0.010, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},
            'gpt-4o-mini': {'input_price': 0.00015, 'output_price': 0.0006, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},
            'chatgpt-4o-latest': {'input_price': 0.005, 'output_price': 0.015, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},

            # Search Preview Models (2025) - Web search integration
            'gpt-4o-search-preview': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 16384, 'context_window': 128000, 'category': 'search'},
            'gpt-4o-mini-search-preview': {'input_price': 0.0003, 'output_price': 0.0012, 'max_tokens': 16384, 'context_window': 128000, 'category': 'search'},

            # Computer Use Models (2025) - Agentic automation
            'computer-use-preview': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 16384, 'context_window': 128000, 'category': 'agent'},

            # Realtime API Models (Voice/Audio in real-time)
            'gpt-realtime': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},
            'gpt-realtime-mini': {'input_price': 0.001, 'output_price': 0.004, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},
            'gpt-4o-realtime-preview': {'input_price': 0.005, 'output_price': 0.020, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},
            'gpt-4o-mini-realtime-preview': {'input_price': 0.0006, 'output_price': 0.0024, 'max_tokens': 4096, 'context_window': 128000, 'category': 'realtime'},

            # Audio Models (Transcription, TTS & Speech)
            'gpt-audio': {'input_price': 0.008, 'output_price': 0.032, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
            'gpt-audio-mini': {'input_price': 0.002, 'output_price': 0.008, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
            'gpt-4o-audio-preview': {'input_price': 0.0025, 'output_price': 0.010, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
            'gpt-4o-mini-audio-preview': {'input_price': 0.00015, 'output_price': 0.0006, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
            'gpt-4o-transcribe': {'input_price': 0.006, 'output_price': 0.006, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
            'gpt-4o-mini-transcribe': {'input_price': 0.003, 'output_price': 0.003, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
            'gpt-4o-transcribe-diarize': {'input_price': 0.010, 'output_price': 0.010, 'max_tokens': 16384, 'context_window': 128000, 'category': 'audio'},
            'gpt-4o-mini-tts': {'input_price': 0.006, 'output_price': 0.006, 'max_tokens': 0, 'context_window': 4096, 'category': 'audio'},
            'whisper-1': {'input_price': 0.006, 'output_price': 0.006, 'max_tokens': 0, 'context_window': 0, 'category': 'audio'},
            'tts-1': {'input_price': 0.015, 'output_price': 0.015, 'max_tokens': 0, 'context_window': 4096, 'category': 'audio'},
            'tts-1-hd': {'input_price': 0.030, 'output_price': 0.030, 'max_tokens': 0, 'context_window': 4096, 'category': 'audio'},

            # Video Models (Sora 2 Series)
            'sora-2': {'input_price': 0.0, 'output_price': 0.100, 'max_tokens': 0, 'context_window': 0, 'category': 'video'},
            'sora-2-pro': {'input_price': 0.0, 'output_price': 0.200, 'max_tokens': 0, 'context_window': 0, 'category': 'video'},

            # Image Generation (GPT-Image & DALL-E)
            'gpt-image-1': {'input_price': 0.0, 'output_price': 0.040, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},
            'gpt-image-1-mini': {'input_price': 0.0, 'output_price': 0.020, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},
            'dall-e-3': {'input_price': 0.0, 'output_price': 0.040, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},
            'dall-e-2': {'input_price': 0.0, 'output_price': 0.020, 'max_tokens': 0, 'context_window': 0, 'category': 'image'},

            # GPT-4 Turbo & Legacy GPT-4
            'gpt-4-turbo': {'input_price': 0.010, 'output_price': 0.030, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
            'gpt-4-turbo-preview': {'input_price': 0.010, 'output_price': 0.030, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
            'gpt-4': {'input_price': 0.030, 'output_price': 0.060, 'max_tokens': 8192, 'context_window': 8192, 'category': 'chat'},
            'gpt-4.5-preview': {'input_price': 0.010, 'output_price': 0.030, 'max_tokens': 16384, 'context_window': 128000, 'category': 'chat'},

            # GPT-3.5 Turbo (Legacy, cost-effective)
            'gpt-3.5-turbo': {'input_price': 0.0005, 'output_price': 0.0015, 'max_tokens': 4096, 'context_window': 16385, 'category': 'chat'},

            # Embeddings Models
            'text-embedding-3-large': {'input_price': 0.00013, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 8191, 'category': 'embedding'},
            'text-embedding-3-small': {'input_price': 0.00002, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 8191, 'category': 'embedding'},
            'text-embedding-ada-002': {'input_price': 0.0001, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 8191, 'category': 'embedding'},

            # Moderation Models (Free)
            'omni-moderation-latest': {'input_price': 0.0, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 0, 'category': 'moderation'},
            'text-moderation-latest': {'input_price': 0.0, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 0, 'category': 'moderation'},
            'text-moderation-stable': {'input_price': 0.0, 'output_price': 0.0, 'max_tokens': 0, 'context_window': 0, 'category': 'moderation'},

            # Open-Source / Open-Weight Models (GPT-OSS)
            'gpt-oss-120b': {'input_price': 0.003, 'output_price': 0.012, 'max_tokens': 32768, 'context_window': 128000, 'category': 'open-source'},
            'gpt-oss-20b': {'input_price': 0.0005, 'output_price': 0.002, 'max_tokens': 32768, 'context_window': 128000, 'category': 'open-source'},

            # Legacy/Deprecated Models
            'babbage-002': {'input_price': 0.0004, 'output_price': 0.0004, 'max_tokens': 16384, 'context_window': 16384, 'category': 'legacy'},
            'davinci-002': {'input_price': 0.002, 'output_price': 0.002, 'max_tokens': 16384, 'context_window': 16384, 'category': 'legacy'}
        }
    },
    'anthropic': {
        'api_url': 'https://api.anthropic.com/v1/messages',
        'api_key_env': 'ANTHROPIC_API_KEY',
        'display_name': 'Anthropic',
        'models': {
            'claude-sonnet-4-20250514': {'input_price': 0.003, 'output_price': 0.015, 'max_tokens': 64000, 'context_window': 200000, 'category': 'chat'},
            'claude-3-5-sonnet-20241022': {'input_price': 0.003, 'output_price': 0.015, 'max_tokens': 8192, 'context_window': 200000, 'category': 'chat'},
            'claude-3-5-haiku-20241022': {'input_price': 0.001, 'output_price': 0.005, 'max_tokens': 8192, 'context_window': 200000, 'category': 'chat'},
            'claude-3-opus-20240229': {'input_price': 0.015, 'output_price': 0.075, 'max_tokens': 4096, 'context_window': 200000, 'category': 'chat'},
            'claude-3-haiku-20240307': {'input_price': 0.00025, 'output_price': 0.00125, 'max_tokens': 4096, 'context_window': 200000, 'category': 'chat'}
        }
    },
    'google': {
        'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        'api_key_env': 'GOOGLE_API_KEY',
        'display_name': 'Google',
        'models': {
            'gemini-2.0-flash': {'input_price': 0.0001, 'output_price': 0.0004, 'max_tokens': 8192, 'context_window': 1000000, 'category': 'chat'},
            'gemini-2.0-pro': {'input_price': 0.00125, 'output_price': 0.005, 'max_tokens': 8192, 'context_window': 1000000, 'category': 'chat'},
            'gemini-1.5-pro': {'input_price': 0.00125, 'output_price': 0.005, 'max_tokens': 8192, 'context_window': 2000000, 'category': 'chat'},
            'gemini-1.5-flash': {'input_price': 0.000075, 'output_price': 0.0003, 'max_tokens': 8192, 'context_window': 1000000, 'category': 'chat'},
            'gemini-pro': {'input_price': 0.0005, 'output_price': 0.0015, 'max_tokens': 8192, 'context_window': 32000, 'category': 'chat'}
        }
    },
    'cohere': {
        'api_url': 'https://api.cohere.ai/v1/chat',
        'api_key_env': 'COHERE_API_KEY',
        'display_name': 'Cohere',
        'models': {
            'command-r-plus': {'input_price': 0.003, 'output_price': 0.015, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
            'command-r': {'input_price': 0.0005, 'output_price': 0.0015, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
            'command': {'input_price': 0.0015, 'output_price': 0.002, 'max_tokens': 4096, 'context_window': 4096, 'category': 'chat'},
            'command-light': {'input_price': 0.0003, 'output_price': 0.0006, 'max_tokens': 4096, 'context_window': 4096, 'category': 'chat'}
        }
    },
    'huggingface': {
        'api_url': 'https://api-inference.huggingface.co/models/{model}',
        'api_key_env': 'HUGGINGFACE_API_KEY',
        'display_name': 'HuggingFace',
        'models': {
            'meta-llama/Llama-3.2-3B-Instruct': {'input_price': 0.0001, 'output_price': 0.0002, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
            'meta-llama/Llama-3.1-70B-Instruct': {'input_price': 0.0009, 'output_price': 0.0009, 'max_tokens': 4096, 'context_window': 128000, 'category': 'chat'},
            'mistralai/Mistral-7B-Instruct-v0.3': {'input_price': 0.0001, 'output_price': 0.0002, 'max_tokens': 4096, 'context_window': 32000, 'category': 'chat'},
            'mistralai/Mixtral-8x7B-Instruct-v0.1': {'input_price': 0.0007, 'output_price': 0.0007, 'max_tokens': 4096, 'context_window': 32000, 'category': 'chat'}
        }
    }
}

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
