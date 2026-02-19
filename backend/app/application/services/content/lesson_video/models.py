"""
Configuration models and constants for lesson video service.

Defines Sora models, avatar styles, and default settings.
"""

from typing import Dict, Any

# Available Sora models
SORA_MODELS: Dict[str, Dict[str, Any]] = {
    'sora-2': {
        'name': 'Sora 2',
        'description': 'Flagship video generation with synced audio',
        'performance': 'higher',
        'speed': 'slow',
        'input': ['text', 'image'],
        'output': ['video', 'audio'],
        'cost_per_second': 0.10,  # Estimated
        'max_duration': 60
    },
    'sora-2-pro': {
        'name': 'Sora 2 Pro',
        'description': 'Premium quality video generation with synced audio',
        'performance': 'highest',
        'speed': 'slower',
        'input': ['text', 'image'],
        'output': ['video', 'audio'],
        'cost_per_second': 0.20,  # Estimated - higher quality
        'max_duration': 120
    }
}

# Default model
DEFAULT_MODEL = 'sora-2'

# Video generation settings
DEFAULT_RESOLUTION = '1080p'
DEFAULT_FRAMERATE = 30

# Avatar styles for Sora video prompts
AVATAR_STYLES: Dict[str, Dict[str, str]] = {
    'professional_teacher': {
        'name': 'Professioneller Lehrer',
        'description': 'A professional male teacher in his 40s with glasses, wearing a blue dress shirt and brown vest, standing in front of a classic green chalkboard in a well-lit classroom',
        'voice_style': 'warm, clear German male voice, professional but friendly tone',
        'gestures': 'uses natural hand gestures while explaining, occasionally points to the chalkboard',
        'expression': 'friendly and encouraging, maintains eye contact'
    },
    'female_instructor': {
        'name': 'Dozentin',
        'description': 'A professional female instructor in her 30s with a warm smile, wearing smart casual attire, standing in a modern classroom with a whiteboard',
        'voice_style': 'clear, confident German female voice, engaging and encouraging',
        'gestures': 'animated hand movements while explaining concepts, writes on whiteboard',
        'expression': 'enthusiastic and approachable'
    },
    'casual_tutor': {
        'name': 'Lockerer Tutor',
        'description': 'A young casual tutor in their 20s, wearing a polo shirt, in a cozy study room with bookshelves',
        'voice_style': 'relaxed, friendly German voice, conversational tone like talking to a friend',
        'gestures': 'relaxed and conversational, uses casual hand gestures',
        'expression': 'friendly peer, nodding encouragingly'
    },
    'animated_expert': {
        'name': 'Animierter Experte',
        'description': 'A Pixar-style 3D animated character, friendly expert with expressive features, in a colorful educational environment',
        'voice_style': 'energetic, clear German voice with enthusiasm',
        'gestures': 'expressive animated movements, points and gestures dynamically',
        'expression': 'highly expressive, engaging cartoon-style emotions'
    }
}

# OpenAI Sora 2 API endpoint
SORA_API_URL = 'https://api.openai.com/v1/videos/generations'
