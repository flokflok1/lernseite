"""
LM Slot Requirements - Capability Analysis

Quick reference constants for LMs needing specific capabilities.
"""

from typing import List

# Quick reference for LMs needing specific capabilities
LMS_NEEDING_REALTIME: List[int] = [4, 24]  # Sokratisch, Muendlich
LMS_NEEDING_VISION: List[int] = [8, 10, 12, 16]  # Whiteboard, Network, Mathe, Fehleranalyse
LMS_NEEDING_STT: List[int] = [24]  # Muendlich
LMS_NEEDING_TTS: List[int] = [0, 24]  # Deep Explanation, Muendlich
LMS_NEEDING_CODE_EXEC: List[int] = [9, 11, 16, 17, 20, 31]  # Sandbox, IT, Fehler, Lab, MultiStep, Projekt
LMS_NEEDING_REASONING: List[int] = [4, 18, 27]  # Sokratisch, Freitext, Team-Case
