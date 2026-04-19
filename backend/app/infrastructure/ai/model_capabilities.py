"""
Lazy Auto-Discovery für Modell-Capabilities.

Statt einer hardcoded Liste, welche Modelle z.B. ``max_completion_tokens``
statt ``max_tokens`` brauchen, lernt das System diese Information beim ersten
Request:

1. Capability liegt in ``ai_pipeline.ai_models.capabilities`` (JSONB).
2. Vor jedem Request liest der Provider die Flag aus dem Repository.
3. Wenn unbekannt → probiert ``max_tokens``. Bei provider-seitigem 400-Fehler
   mit Hinweis auf ``max_completion_tokens`` markiert der Provider das Modell
   in der DB als ``requires_completion_tokens=True`` und retried.
4. Nächster Request des selben Modells nutzt direkt die korrekte Variante.

Vorteile gegenüber hardcoded Listen:
* Funktioniert ohne Code-Change für jedes neue Modell + jeden Provider.
* Sync-Service bleibt einfach (nur Modell-IDs, keine Capability-Pflege).
* DB ist einzige Wahrheitsquelle.

DDD: Infrastructure. SQL liegt in ``AIModelsCRUDRepository``.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.infrastructure.persistence.repositories.ai_models.crud import (
    AIModelsCRUDRepository,
)

logger = logging.getLogger(__name__)


REQUIRES_COMPLETION_TOKENS = 'requires_completion_tokens'


# Prozess-Cache (kleiner Geschwindigkeits-Boost — wird beim Setzen invalidiert)
_cache: dict[tuple[str, Optional[str]], Optional[bool]] = {}


def requires_completion_tokens(
    model_name: str,
    provider_name: Optional[str] = None,
) -> Optional[bool]:
    """
    True/False wenn die Capability bekannt ist, sonst None.

    None → der Provider sollte heuristisch probieren und das Ergebnis via
    ``mark_requires_completion_tokens`` persistieren.
    """
    key = (model_name, provider_name)
    if key in _cache:
        return _cache[key]

    raw = AIModelsCRUDRepository.get_capability(
        model_name=model_name,
        capability_key=REQUIRES_COMPLETION_TOKENS,
        provider_name=provider_name,
    )
    val: Optional[bool]
    if raw is None:
        val = None
    else:
        val = bool(raw)
    _cache[key] = val
    return val


def mark_requires_completion_tokens(
    model_name: str,
    requires: bool,
    provider_name: Optional[str] = None,
) -> None:
    """Persistiert Flag in der DB. Cache wird invalidiert."""
    try:
        AIModelsCRUDRepository.set_capability(
            model_name=model_name,
            capability_key=REQUIRES_COMPLETION_TOKENS,
            value=bool(requires),
            provider_name=provider_name,
        )
        logger.info(
            'Capability gelernt: %s/%s requires_completion_tokens=%s',
            provider_name or '?', model_name, requires,
        )
    except Exception:
        logger.exception(
            'Capability konnte nicht persistiert werden: %s/%s',
            provider_name, model_name,
        )
    finally:
        _cache.pop((model_name, provider_name), None)


def clear_cache() -> None:
    """Invalidiert den Prozess-Cache (z.B. nach Sync)."""
    _cache.clear()
