"""Domain utilities for exam topic normalization."""

_TOPIC_SYNONYMS = {
    'netzwerktechnik': 'netzwerk',
    'netzwerke': 'netzwerk',
    'netzwerkplanung': 'netzwerk',
    'netzwerkkonfiguration': 'netzwerk',
    'datenbank': 'datenbanken',
    'database': 'datenbanken',
    'sicherheit': 'it_sicherheit',
    'security': 'it_sicherheit',
    'datensicherheit': 'it_sicherheit',
    'programmieren': 'programmierung',
    'coding': 'programmierung',
    'recht': 'vertragsrecht',
    'vpn_tunnel': 'vpn',
    'wlan_sicherheit': 'wlan',
    'ip': 'ipv4',
    'datensicherung': 'backup',
    'webentwicklung': 'html',
    'css': 'html',
}


def normalize_topic(topic: str) -> str:
    """Normalize topic to lowercase snake_case with synonym resolution.

    Domain rule: valid topic keys are lowercase with underscores.
    Synonyms are mapped to canonical keys to reduce fragmentation.

    Examples:
        'IT-Sicherheit' -> 'it_sicherheit'
        'SQL' -> 'sql'
        'Netzwerktechnik' -> 'netzwerk'
        'database' -> 'datenbanken'
    """
    t = topic.lower().strip().replace(' ', '_').replace('-', '_')
    return _TOPIC_SYNONYMS.get(t, t)
