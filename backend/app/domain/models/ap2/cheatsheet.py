"""
AP2 Cheatsheet — vom User geschriebene Kurz-Zusammenfassung pro Thema.

Generation Effect: Eigenes Aufschreiben verankert das Wissen tiefer
als nur Lesen. Die Cheatsheets werden vor der Prüfung als PDF exportiert.

DDD Layer: Domain — NO Flask, DB, or Infrastructure imports.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Cheatsheet:
    """Markdown-Cheatsheet vom User geschrieben.

    Das word_count ist ein grober Indikator für "hat der User sich
    wirklich mit dem Thema befasst?" — zeigt im Dashboard als Badge.
    """
    user_id: UUID
    topic_id: UUID
    markdown_content: str = ''
    word_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def update_content(self, new_content: str) -> None:
        """Setzt neuen Inhalt und berechnet Wortanzahl neu."""
        self.markdown_content = new_content
        self.word_count = len(new_content.split())

    @property
    def is_empty(self) -> bool:
        return self.word_count == 0

    @property
    def is_substantial(self) -> bool:
        """Mindestens 50 Wörter = ernstgemeintes Cheatsheet."""
        return self.word_count >= 50
