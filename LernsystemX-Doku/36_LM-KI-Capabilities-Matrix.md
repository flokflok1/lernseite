# LM KI-Capabilities Matrix

## Übersicht

Dieses Dokument definiert welche KI-Capabilities jede der 33 Lernmethoden (LM00-LM32) benötigt.

## KI-Capability-Typen

| Capability | API/Technologie | Beschreibung |
|------------|-----------------|--------------|
| **TEXT** | GPT-4o, Claude | Standard Text-Generation |
| **TEXT_STREAM** | GPT-4o Stream | Streaming Text (typewriter effect) |
| **TTS** | OpenAI TTS | Text-to-Speech (Sprachausgabe) |
| **STT** | Whisper | Speech-to-Text (Spracherkennung) |
| **REALTIME** | OpenAI Realtime API | Bidirektionales Audio-Streaming (Konversation) |
| **VISION** | GPT-4o Vision | Bild-Analyse |
| **IMAGE_GEN** | DALL-E 3 | Bild-Generierung |
| **CODE_EXEC** | Sandbox/Docker | Code-Ausführung |
| **MATH** | GPT-4o + LaTeX | Mathematische Formeln |
| **DIAGRAM** | Mermaid/D3.js + KI | Diagramm-Generierung |

---

## Gruppe A – Erklärende Methoden (LM00-LM07)

| LM | Name | Capabilities | Primary Model | Fallback | Notes |
|----|------|--------------|---------------|----------|-------|
| **LM00** | Deep Explanation | TEXT_STREAM, TTS | GPT-4o / Claude Opus | GPT-4o-mini | Lange, detaillierte Erklärungen mit optionaler Vorlesung |
| **LM01** | Schritt-für-Schritt | TEXT_STREAM, DIAGRAM | GPT-4o | GPT-4o-mini | Sequenzielle Anleitungen, evtl. mit Flowcharts |
| **LM02** | Interaktive Theorie | TEXT_STREAM | GPT-4o-mini | - | Theorie mit eingebetteten Fragen |
| **LM03** | Diagramm/Visualisierung | TEXT, DIAGRAM, IMAGE_GEN | GPT-4o + DALL-E | - | Mermaid-Code oder Bild-Generierung |
| **LM04** | Glossar-Autogenerator | TEXT | GPT-4o-mini | - | Fachbegriffe extrahieren |
| **LM05** | Mindmap-Generator | TEXT, DIAGRAM | GPT-4o-mini | - | JSON für Mindmap-Rendering |
| **LM06** | Beispiel-Szenario | TEXT_STREAM | GPT-4o | GPT-4o-mini | Real-World Cases |
| **LM07** | NPC-Tutor-Lecture | TEXT_STREAM, TTS, **REALTIME** | GPT-4o + TTS | - | **Virtueller Tutor - braucht Realtime für Dialog!** |

---

## Gruppe B – Praxis/Übung (LM08-LM17)

| LM | Name | Capabilities | Primary Model | Fallback | Notes |
|----|------|--------------|---------------|----------|-------|
| **LM08** | Whiteboard-Aufgabe | TEXT, VISION, DIAGRAM | GPT-4o Vision | - | **User zeichnet, KI analysiert Zeichnung** |
| **LM09** | Code/IT-Config Sandbox | TEXT_STREAM, CODE_EXEC | GPT-4o | Claude Sonnet | Code-Generierung + Validierung |
| **LM10** | Netzwerk-Simulation | TEXT, DIAGRAM, VISION | GPT-4o | - | Topologie-Analyse |
| **LM11** | IT-Szenario lösen | TEXT_STREAM, CODE_EXEC | GPT-4o / Claude | - | Mehrstufige IT-Cases |
| **LM12** | Mathe-Interaktiv | TEXT_STREAM, MATH, VISION | GPT-4o | - | **Handschrift-Erkennung für Formeln** |
| **LM13** | Flashcards | TEXT | GPT-4o-mini | - | Einfache Karten-Generierung |
| **LM14** | Drag & Drop | TEXT | GPT-4o-mini | - | Aufgaben-Generierung |
| **LM15** | Lückentext | TEXT | GPT-4o-mini | - | Text mit Lücken generieren |
| **LM16** | Fehleranalyse | TEXT, CODE_EXEC, VISION | GPT-4o | - | Code/Config mit Fehlern analysieren |
| **LM17** | Hands-on Lab | TEXT_STREAM, CODE_EXEC | GPT-4o | Claude | **Virtuelle Umgebung + KI-Guidance** |

---

## Gruppe C – Prüfungsorientiert (LM18-LM25)

| LM | Name | Capabilities | Primary Model | Fallback | Notes |
|----|------|--------------|---------------|----------|-------|
| **LM18** | Freitext-Langantwort | TEXT_STREAM | GPT-4o | Claude | Bewertung von Langtexten |
| **LM19** | IHK-Stil Aufgaben | TEXT, IMAGE_GEN | GPT-4o | - | Authentische Prüfungsaufgaben |
| **LM20** | Multi-Step Praxisprüfung | TEXT_STREAM, CODE_EXEC | GPT-4o | Claude | Komplexe Szenarien |
| **LM21** | Zeitlimit-Training | TEXT | GPT-4o-mini | - | Zeitbasierte Aufgaben |
| **LM22** | Prüfungs-Quiz | TEXT | GPT-4o-mini | - | MC-Fragen generieren |
| **LM23** | Verständnis-Checks | TEXT | GPT-4o-mini | - | Kurze Checks |
| **LM24** | Mündliche Erklärung | **STT, TTS, REALTIME**, TEXT | GPT-4o + Whisper + TTS | - | **Braucht Realtime API für echten Dialog!** |
| **LM25** | Kapitel-Endprüfung | TEXT | GPT-4o | - | Umfassende Prüfung |

---

## Gruppe D – Pro/Gamification (LM26-LM32)

| LM | Name | Capabilities | Primary Model | Fallback | Notes |
|----|------|--------------|---------------|----------|-------|
| **LM26** | Adaptive Difficulty | TEXT, (Meta-Logic) | GPT-4o | - | Schwierigkeit anpassen basierend auf Performance |
| **LM27** | Lernpfad-Generator | TEXT | GPT-4o | Claude | Personalisierte Pfade |
| **LM28** | Persona-Tutor | TEXT_STREAM, TTS, **REALTIME** | GPT-4o + TTS | - | **Anpassbarer Tutor - Realtime für Konversation!** |
| **LM29** | Sokratischer Dialog | TEXT_STREAM, TTS, **REALTIME** | GPT-4o / Claude | - | **Sokratische Methode - braucht echten Dialog!** |
| **LM30** | Spaced Repetition | TEXT | GPT-4o-mini | - | Wiederholungs-Algorithmus |
| **LM31** | Quest/XP System | TEXT | GPT-4o-mini | - | Gamification-Texte |
| **LM32** | Vokabeltrainer | TEXT, TTS, STT | GPT-4o-mini + TTS | - | **Audio für Aussprache!** |

---

## Zusammenfassung: Welche LMs brauchen welche Capabilities?

### Realtime API (bidirektionaler Audio-Dialog)
**KRITISCH für echte Konversation:**
- LM07 (NPC-Tutor-Lecture)
- LM24 (Mündliche Erklärung)
- LM28 (Persona-Tutor)
- LM29 (Sokratischer Dialog)

### TTS (Text-to-Speech)
- LM00, LM07, LM24, LM28, LM29, LM32

### STT (Speech-to-Text / Whisper)
- LM24 (Mündliche Erklärung)
- LM32 (Vokabeltrainer - Aussprache prüfen)

### Vision (Bild-Analyse)
- LM08 (Whiteboard - Zeichnung analysieren)
- LM10 (Netzwerk - Topologie erkennen)
- LM12 (Mathe - Handschrift)
- LM16 (Fehleranalyse - Screenshots)

### Image Generation (DALL-E)
- LM03 (Visualisierungen)
- LM19 (IHK-Aufgaben mit Bildern)

### Code Execution
- LM09 (Code Sandbox)
- LM11 (IT-Szenario)
- LM16 (Fehleranalyse)
- LM17 (Hands-on Lab)
- LM20 (Praxisprüfung)

### Streaming Text
- Fast alle erklärenden Methoden (bessere UX)

---

## Architektur-Empfehlung

### 1. Multi-Model Routing (bereits implementiert)
- Admin wählt pro LM das bevorzugte Modell
- Fallback-Kette wenn Primärmodell nicht verfügbar

### 2. Capability-basierte Validierung (NEU)
```python
LM_CAPABILITIES = {
    0: ['TEXT_STREAM', 'TTS'],
    7: ['TEXT_STREAM', 'TTS', 'REALTIME'],
    24: ['STT', 'TTS', 'REALTIME', 'TEXT'],
    # ...
}

def validate_lm_model_assignment(lm_id: int, model_id: str) -> bool:
    """Prüft ob das Model alle Capabilities für die LM unterstützt"""
    required = LM_CAPABILITIES.get(lm_id, [])
    model_caps = get_model_capabilities(model_id)
    return all(cap in model_caps for cap in required)
```

### 3. Realtime API Integration (Priorität!)
Für LM07, LM24, LM28, LM29:
- WebSocket-Verbindung zum Client
- OpenAI Realtime API für Audio-Streaming
- Bidirektionale Konversation

### 4. Multi-Model pro LM (NEU)
Manche LMs brauchen mehrere Modelle gleichzeitig:
```python
LM_MODEL_REQUIREMENTS = {
    24: {  # Mündliche Erklärung
        'chat': 'gpt-4o',           # Für Textanalyse
        'stt': 'whisper-1',         # Für Transkription
        'tts': 'tts-1',             # Für Sprachausgabe
        'realtime': 'gpt-4o-realtime-preview'  # Für Live-Dialog
    },
    8: {  # Whiteboard
        'chat': 'gpt-4o',           # Für Aufgaben-Generierung
        'vision': 'gpt-4o',         # Für Zeichnung-Analyse
    }
}
```

---

## Nächste Schritte

1. **Capability-Registry im Backend erstellen**
2. **Model-Capabilities in DB speichern** (welches Model kann was)
3. **Validierung bei LM-Model-Zuweisung**
4. **OpenAI Realtime API Integration** für Dialog-LMs
5. **Multi-Model-Support pro LM** in Frontend/Backend
6. **Vision-Endpoint** für Whiteboard/Mathe
