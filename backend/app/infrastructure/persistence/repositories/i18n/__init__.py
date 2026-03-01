"""i18n persistence repositories."""

from .translations.translation import Translation, TranslationRepository  # noqa: F401
from .translations import translation_part2  # noqa: F401 - Attaches comparison/analytics methods

# Service query repositories (Pattern A - static methods)
from .translations.service_queries import (  # noqa: F401
    I18nLanguageStatsRepository,
    I18nSuggestionQueriesRepository,
    I18nKeyQueriesRepository,
)
from .translations.service_queries_part2 import (  # noqa: F401
    I18nAIQueriesRepository,
    I18nConfigQueriesRepository,
    I18nTranslationQueriesRepository,
)

# Admin language management repository
from .admin.admin_languages import I18nAdminLanguageRepository  # noqa: F401

# Admin translation management queries
from .admin.admin_queries import I18nAdminQueryRepository  # noqa: F401

# Bulk seed operations
from .admin.bulk_seed import I18nBulkSeedRepository  # noqa: F401
