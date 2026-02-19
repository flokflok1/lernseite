"""i18n persistence repositories."""

from .translation import Translation, TranslationRepository  # noqa: F401
from . import translation_part2  # noqa: F401 - Attaches comparison/analytics methods

# Service query repositories (Pattern A - static methods)
from .service_queries import (  # noqa: F401
    I18nLanguageStatsRepository,
    I18nSuggestionQueriesRepository,
    I18nKeyQueriesRepository,
)
from .service_queries_part2 import (  # noqa: F401
    I18nAIQueriesRepository,
    I18nConfigQueriesRepository,
    I18nTranslationQueriesRepository,
)

# Admin language management repository
from .admin_languages import I18nAdminLanguageRepository  # noqa: F401

# Admin translation management queries
from .admin_queries import I18nAdminQueryRepository  # noqa: F401
