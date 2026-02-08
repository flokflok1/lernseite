"""
Repository Registry – single lookup point for domain → infrastructure.

Domain code imports `repos` and calls e.g. `repos.social_posts.get_by_id(...)`.
At boot time, `core/bootstrap/container.py` wires the concrete repo classes
into this registry so the domain never imports from infrastructure directly.

All attributes are typed as Optional[Type[Port]] and start as None.
Calling an unregistered slot raises a clear RuntimeError.
"""

from typing import Optional, Type

from app.domain.ports.base import QueryRunnerPort, UserPort
from app.domain.ports.ai import (
    AIJobPort,
    PromptTemplatePort,
    LearningMethodCatalogPort,
    LearningMethodGroupPort,
)
from app.domain.ports.social import (
    SocialPostsPort,
    SocialLikesPort,
    SocialCommentsPort,
    SocialFollowsPort,
)


class _RepositoryRegistry:
    """Mutable singleton holding class references for each repository port."""

    # -- base / shared --
    query_runner: Optional[Type[QueryRunnerPort]] = None
    users: Optional[Type[UserPort]] = None

    # -- social --
    social_posts: Optional[Type[SocialPostsPort]] = None
    social_likes: Optional[Type[SocialLikesPort]] = None
    social_comments: Optional[Type[SocialCommentsPort]] = None
    social_follows: Optional[Type[SocialFollowsPort]] = None

    # -- ai --
    ai_jobs: Optional[Type[AIJobPort]] = None
    prompt_templates: Optional[Type[PromptTemplatePort]] = None
    lm_catalog: Optional[Type[LearningMethodCatalogPort]] = None
    lm_groups: Optional[Type[LearningMethodGroupPort]] = None

    def __getattr__(self, name: str):
        """Raise a clear error when accessing an unregistered slot."""
        raise RuntimeError(
            f"Repository '{name}' not registered. "
            f"Ensure core/bootstrap/container.py has wired it."
        )


repos = _RepositoryRegistry()
