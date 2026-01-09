"""
Admin AI Operations

Proxies to system_features/ai/

Struktur:
- authoring/ - Content-Authoring (Kurs-Builder, Tutor)
- management/ - AI-Management (Jobs, Models, Pricing, Prompts)
- settings/ - AI-Settings (Global Settings, Exams, Models)
- studio/ - AI-Studio (Main Studio Interface)

Alle Blueprints werden von system_features/ai/ importiert und re-exportiert.
"""

# Import from system_features/ai and re-export
from app.api.system_features.ai.authoring import authoring_bp
from app.api.system_features.ai.generation import generation_bp
from app.api.system_features.ai.jobs import jobs_bp
from app.api.system_features.ai.models import models_bp
from app.api.system_features.ai.pricing import pricing_bp
from app.api.system_features.ai.profiles import profiles_bp
from app.api.system_features.ai.studio import studio_bp
from app.api.system_features.ai.tutor import tutor_bp

__all__ = [
    'authoring_bp',
    'generation_bp',
    'jobs_bp',
    'models_bp',
    'pricing_bp',
    'profiles_bp',
    'studio_bp',
    'tutor_bp'
]
