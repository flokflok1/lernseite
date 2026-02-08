"""
Domain Ports – abstract interfaces for infrastructure dependencies.

The domain layer defines WHAT it needs (ports/ABCs).
The infrastructure layer provides HOW (concrete repos).
The bootstrap container wires them together at startup.

Usage in domain code:
    from app.domain.ports.registry import repos
    user = repos.users.find_by_id(user_id)
"""

from app.domain.ports.registry import repos

__all__ = ["repos"]
