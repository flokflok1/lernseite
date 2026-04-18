"""
AP2 Trainer — Enumerations.

Technische Keys (Englisch) — Labels laufen über i18n im Frontend.
DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from enum import Enum


class Bereich(str, Enum):
    """AP2-Prüfungsbereich."""
    PB2 = 'PB2'        # Konzeption und Administration von IT-Systemen
    PB3 = 'PB3'        # Analyse und Entwicklung von Netzwerken
    WISO = 'WISO'      # Wirtschafts- und Sozialkunde (separater Prüfungstag)
    BOTH = 'both'      # Topic erscheint in mehreren Bereichen


class Priority(str, Enum):
    """Prognose-Priorität basierend auf Häufigkeit in Prüfungen."""
    SEHR_HOCH = 'sehr-hoch'
    HOCH = 'hoch'
    MITTEL = 'mittel'
    NIEDRIG = 'niedrig'


class ItemType(str, Enum):
    """Typ eines LearningItems im Active-Recall-Flow."""
    BLURT = 'blurt'              # Freies Abrufen ohne Frage
    CUED = 'cued'                # Karteikarten-Frage
    APPLICATION = 'application'  # Originale Prüfungsaufgabe


class Phase(str, Enum):
    """Active-Recall-Phase die gerade absolviert wird."""
    BLURT = 'blurt'
    CUED = 'cued'
    APPLICATION = 'application'
    REVIEW = 'review'            # Spaced-Repetition-Wiederholung


class AnlageType(str, Enum):
    """Typ einer Prüfungs-Anlage (bestimmt Rendering-Strategie)."""
    NETWORK_TOPOLOGY = 'network-topology'
    DATASHEET = 'datasheet'
    TABLE = 'table'
    ER_DIAGRAM = 'er-diagram'
    RACK_LAYOUT = 'rack-layout'
    PROCESS_DIAGRAM = 'process-diagram'
    EPK_DIAGRAM = 'epk-diagram'
    STATE_DIAGRAM = 'state-diagram'
    SEQUENCE_DIAGRAM = 'sequence-diagram'
    IMAGE = 'image'


class HotspotType(str, Enum):
    """Eingabe-Typ eines Hotspots in einer Anlage."""
    TEXT = 'text'
    NUMBER = 'number'
    IP_ADDRESS = 'ip-address'
    SUBNET_MASK = 'subnet-mask'
    IPV6_ADDRESS = 'ipv6-address'
    DROPDOWN = 'dropdown'
    DRAGGABLE_LABEL = 'draggable-label'


class SessionType(str, Enum):
    """Typ einer Study-Session (aggregiert mehrere Attempts)."""
    TOPIC_STUDY = 'topic_study'          # 3-Phasen-Flow
    REVIEW_QUEUE = 'review_queue'        # SM-2 fällige Items
    EXAM_SIMULATION = 'exam_simulation'  # 90-Min Prüfung
    MIXED_PRACTICE = 'mixed_practice'    # Interleaving mehrerer Themen
