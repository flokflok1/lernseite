"""
Domain Ports – abstract interfaces for infrastructure dependencies.

The domain layer defines WHAT it needs (ports/ABCs).
The infrastructure layer provides HOW (concrete repos).
The bootstrap container wires them together at startup.

Usage in domain code:
    from app.domain.ports.core.registry import repos
    user = repos.users.find_by_id(user_id)
"""

# AI domain ports
from app.domain.ports.ai import (
    AIJobPort,
    PromptTemplatePort,
    LearningMethodCatalogPort,
    LearningMethodGroupPort
)

# Core domain ports
from app.domain.ports.core import (
    QueryRunnerPort,
    UserPort,
    _RepositoryRegistry
)

# Social domain ports
from app.domain.ports.social import (
    SocialPostsPort,
    SocialLikesPort,
    SocialCommentsPort,
    SocialFollowsPort
)

# Import registry for backward compatibility
from app.domain.ports.core.registry import repos

__all__ = [
    # AI
    'AIJobPort',
    'PromptTemplatePort',
    'LearningMethodCatalogPort',
    'LearningMethodGroupPort',

    # Core
    'QueryRunnerPort',
    'UserPort',
    '_RepositoryRegistry',

    # Social
    'SocialPostsPort',
    'SocialLikesPort',
    'SocialCommentsPort',
    'SocialFollowsPort',

    # Registry
    'repos'
]
