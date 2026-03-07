"""Domain utilities for exam topic normalization."""


def normalize_topic(topic: str) -> str:
    """Normalize topic to lowercase snake_case.

    Domain rule: valid topic keys are lowercase with underscores.
    Examples: 'IT-Sicherheit' -> 'it_sicherheit', 'SQL' -> 'sql'
    """
    return topic.lower().replace('-', '_').replace(' ', '_').strip()
