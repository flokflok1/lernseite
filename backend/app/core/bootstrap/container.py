"""
DI Container – wires concrete infrastructure repos into the domain registry.

Called once during create_app() AFTER extensions are initialised but BEFORE
blueprints are registered (so domain code can already use `repos.*`).

This is the ONLY place that bridges infrastructure → domain ports.
"""

from app.domain.ports.core.registry import repos


def wire_repositories() -> None:
    """Bind concrete repository classes to the domain port registry."""

    # -- base / shared --
    from app.infrastructure.persistence.repositories.core.base import (
        BaseRepository,
    )
    from app.infrastructure.persistence.repositories.user import UserRepository

    repos.query_runner = BaseRepository
    repos.users = UserRepository

    # -- social --
    from app.infrastructure.persistence.repositories.social_posts import (
        SocialPostsRepository,
    )
    from app.infrastructure.persistence.repositories.social_likes import (
        SocialLikesRepository,
    )
    from app.infrastructure.persistence.repositories.social_comments import (
        SocialCommentsRepository,
    )
    from app.infrastructure.persistence.repositories.social_follows import (
        SocialFollowsRepository,
    )

    repos.social_posts = SocialPostsRepository
    repos.social_likes = SocialLikesRepository
    repos.social_comments = SocialCommentsRepository
    repos.social_follows = SocialFollowsRepository

    # -- social notifications --
    from app.infrastructure.persistence.repositories.social_notifications import (
        SocialNotificationsRepository,
    )

    repos.social_notifications = SocialNotificationsRepository

    # -- ai --
    from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository
    from app.infrastructure.persistence.repositories.prompts.templates import (
        PromptTemplateRepository,
    )
    from app.infrastructure.persistence.repositories.learning_method.catalog import (
        LearningMethodCatalogRepository,
    )
    from app.infrastructure.persistence.repositories.learning_method.groups import (
        LearningMethodGroupRepository,
    )

    repos.ai_jobs = AIJobRepository
    repos.prompt_templates = PromptTemplateRepository
    repos.lm_catalog = LearningMethodCatalogRepository
    repos.lm_groups = LearningMethodGroupRepository
