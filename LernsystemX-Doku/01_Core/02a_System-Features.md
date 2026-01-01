# 02a – System-Features im Umfeld der Lernmethoden

**Version:** 1.0  
**Stand:** 2025-12-28  
**Status:** Ergänzungs-Dokument zu 02 – Lernmethoden

---

## Zweck dieses Dokuments

Dieses Dokument beschreibt **System-Features**, die eng mit den Lernmethoden verbunden sind, aber **keine Content-Lernmethoden** im Sinne der 19 Formate aus `02_Lernmethoden.md` sind.[file:8][file:1]
Sie erweitern das LernsystemX (LSX) um Tutor-Funktionen, Gamification, IT-Umgebungen und Kollaborations-Workflows.[file:1]

---

## Abgrenzung zu Content-Lernmethoden

- **Content-Lernmethoden** (Dokument `02_Lernmethoden.md`):
  - definieren **Aufgaben- und Prüfungsformate** (z.B. Flashcards, Freitext-Prüfung).[file:8]
  - sind inhaltlich komplett pro Kurs/Modul konfigurierbar.[file:1]
- **System-Features** (dieses Dokument):
  - sind **Infrastruktur, Logik oder Services** um die Lernmethoden herum (z.B. TutorAgent, XP-System, Learning Paths).[file:1]
  - haben oft eigene Module, Tabellen und APIs.

Frühere Dokus haben einige dieser Features als „Lernmethoden“ (LM04, LM05, LM07, LM26–LM31) bezeichnet; hier werden sie sauber als **System-Features** geführt.[file:8][file:1]

---

## Überblick – System-Features nach Bereich

| Bereich | Feature | Frühere LM-ID | Kurzbeschreibung |
|--------|---------|---------------|------------------|
| Tutor & Coaching | NPC-/Persona-Tutor | LM07, LM28 | KI-basierter Tutor mit Rollen/Personas |
| Visualisierung | Mindmap-Generator | LM05 | Kursweite Mindmaps aus Theorie-Inhalten |
| Gamification | Adaptive Difficulty, Quest-/XP, Daily Recall | LM26, LM30, LM31 | Motivation, Leveling, Wiederholungslogik |
| Learning Paths | Lernpfad-Autogenerator | LM27 | KI-gestützte Lernpfad-Erstellung und -Optimierung |
| Kollaboration | Peer Review, Team-Case, Learning Journal, Portfolio, Inverted Classroom | LM27–LM32 | Workflows für Gruppenarbeit und Reflexion |
| IT-Umgebungen | Code-/Config-Sandbox, Netzwerk-Umgebung | LM09–LM11, LM16 | Systemumgebungen für praktische Aufgaben |

---

## 1. Tutor- und Coach-Systeme

### 1.1 TutorAgent / NPC-Tutor (früher LM07, LM28)

**Beschreibung:**
- KI-gestützter Tutor, der als „NPC“ im Kurs oder LiveRoom agiert (Fragen stellt, erklärt, nachhakt).[file:1]
- Kann unterschiedliche **Rollen/Personas** annehmen (z.B. „strenger Prüfer“, „freundlicher Coach“).[file:1]

**Typische Einsätze:**
- Begleitung durch ein ganzes Modul (Fragen, Hinweise, Zusammenfassungen).
- Prüfungsvorbereitung: Tutor stellt IHK-nahe Fragen und analysiert Antworten.

**Technische Einordnung:**
- Kein eigenes Aufgabenformat – nutzt bestehende Lernmethoden (z.B. LM18, LM22) und verpackt sie dialogisch.[file:8]
- Implementiert als:
  - Backend-Service (z.B. `tutor_agent.py`) mit Session-Kontext.
  - Anbindung an KI-Provider (Claude, GPT) mit Persona-Prompts.[file:1]

---

## 2. Visualisierungs-Features

### 2.1 Mindmap-Generator (früher LM05)

**Beschreibung:**
- Generiert kursweite oder modulweite **Mindmaps** aus Theorie-Blättern und Strukturinformationen.[file:8][file:1]
- Dient als **Übersichts- und Navigations-Feature**, nicht als einzelne Lernaufgabe.

**Typische Einsätze:**
- Startseite eines Kurses: Mindmap aller Themen.
- Reflexion am Kapitelende: „Wo hängt welches Thema?“.

**Technische Einordnung:**
- Arbeitet auf Kurs-/Modul-Ebene, nicht auf Aufgabenebene.
- Nutzt Daten aus `moduletheory.content` (Struktur, Überschriften, Beziehungen).[file:1]
- Frontend: Darstellung in einem Mindmap-Widget, ggf. integriert ins Dashboard.[file:1]

---

## 3. Gamification-Features

### 3.1 Adaptive Difficulty (früher LM26)

**Beschreibung:**
- Passt Schwierigkeit von Aufgaben automatisch an den Leistungsstand der Lernenden an.[file:1]
- Nutzt Performance-Daten (Scores, Zeit, Versuche) aus verschiedenen Lernmethoden.

**Funktion:**
- Überwacht z.B. Ergebnisse von LM13, LM22, LM23.
- Entscheidet, ob schwierigere oder einfachere Items geliefert werden.

**Technische Einordnung:**
- Service-Schicht („AI-Optimizer“), der **Item-Auswahl und Settings** beeinflusst, aber keine eigene Aufgabe darstellt.[file:1]

### 3.2 Quest- & XP-System (früher LM31)

**Beschreibung:**
- Vergibt **Erfahrungspunkte (XP)** und **Badges** für erledigte Aktivitäten.[file:1]
- Basiert auf Regeln wie „Abschluss Kapitel-Endprüfung = 500 XP“.

**Technische Einordnung:**
- Eigene Tabellen (z.B. `user_xp`, `quests_completed`).
- Hooks in Kurs-/Methodenlogik (z.B. nach erfolgreichem Abschluss von LM25).[file:1]

### 3.3 Daily Recall / Spaced Repetition (früher LM30)

**Beschreibung:**
- Tägliche Wiederholungsaufgaben basierend auf Vergessenskurve (Spaced Repetition).[file:1]
- Nutzt bevorzugt Flashcards (LM13) und Quiz-Formate (LM22).

**Technische Einordnung:**
- Scheduling-Logik + Algorithmus (z.B. SM-2-Variante) zur Auswahl der nächsten Karten.[file:1]

---

## 4. Learning-Path-System

### 4.1 Lernpfad-Autogenerator (früher LM27)

**Beschreibung:**
- Erzeugt und optimiert **Lernpfade** über mehrere Kurse/Module hinweg.[file:1]
- Berücksichtigt Ziele (z.B. „IHK FISI AP1 bestehen“), Zeitbudget und Vorkenntnisse.

**Technische Einordnung:**
- Nutzt eigene Tabellen (z.B. `learning_paths`, `learning_path_steps`).[file:1]
- Greift auf Kurs-/Modul-Metadaten zu, nicht auf einzelne Aufgabeninstanzen.

**Beziehung zu Content-LMs:**
- Learning Path entscheidet **welche Module/Kurse** wann kommen.
- In den Modulen selbst werden dann wieder Content-Lernmethoden (LM00–LM25) eingesetzt.[file:8]

---

## 5. Kollaborative Workflows

### 5.1 Peer Review (früher LM28)

**Beschreibung:**
- Strukturierter Review-Prozess, bei dem Lernende Arbeiten gegenseitig bewerten.[file:8]
- Nutzt Rubrics, Kommentare und ggf. KI-Feedback.

**Technische Einordnung:**
- Eigene Entitäten wie `peer_review_tasks`, `peer_review_submissions`, `peer_review_ratings`.[file:1]
- Kann Ergebnisse von Content-LMs (z.B. Freitext-Antworten aus LM18) als Input nutzen.[file:8]

### 5.2 Team-Case / Gruppenfallarbeit (früher LM27 im alten Sinn)

**Beschreibung:**
- Teams bearbeiten gemeinsam komplexe Fälle über längere Zeit.[file:8]
- Integration mit LiveRoom (gemeinsame Sessions) und Kurs-Struktur.

**Technische Einordnung:**
- Team- und Rollen-Logik (`team_id`, `role_in_team`).[file:1]
- Verknüpfung mit Kursen/Modulen und ggf. eigenen Dashboards.

### 5.3 Learning Journal & Portfolio (früher LM29, LM30)

**Beschreibung:**
- Laufende Reflexions-Einträge (Journal) und Sammlung von Artefakten (Portfolio).[file:8]
- Dient eher der Dokumentation von Lernwegen als der Bearbeitung einzelner Aufgaben.

**Technische Einordnung:**
- Tabellen wie `learning_journal_entries`, `portfolio_items`.[file:1]
- Kann auf Ergebnisse aus Content-LMs verweisen (z.B. „beste Lösung aus LM17-Lab“).

### 5.4 Inverted Classroom (früher LM32)

**Beschreibung:**
- Organisations- und Ablaufmodell: Theorie asynchron, Praxis synchron (LiveRoom).[file:8]
- Steuert, **wann** welche Module/Methoden freigeschaltet und in LiveSessions genutzt werden.

**Technische Einordnung:**
- Scheduling-/Visibility-Logik pro Kurs.[file:1]
- Enge Verbindung mit LiveRoom-Planung und Kurskalender.

---

## 6. IT-Umgebungen als System-Features

### 6.1 Code-/Config-Sandbox (früher Teil von LM09, LM16)

**Beschreibung:**
- Technische Umgebung zum Ausführen oder Validieren von Code- und Konfigurationsbeispielen.[file:8][file:1]
- Die eigentliche Lernmethode ist z.B. „Fehleranalyse“ (LM16), die Sandbox ist das **Tool** dazu.

**Technische Einordnung:**
- Containerisierte Umgebung, Sicherheits-Sandbox, Logging.[file:1]
- APIs für „run code“, „diff config“, „check tests“.

### 6.2 Netzwerk-Simulation (früher LM10)

**Beschreibung:**
- Simulierte Netzumgebungen (Router, Switches, Pings).[file:8]
- Wird von Praxis- und Prüfungsaufgaben genutzt, ist aber selbst Infrastruktur.

**Technische Einordnung:**
- Separate Simulation-Engine, ggf. eigener Service.[file:1]
- Schnittstelle zu Lernmethoden, die Szenarien definieren.

---

## 7. Zusammenfassung für Architektur & Doku

- `02_Lernmethoden.md`:
  - Definiert **19 Content-Lernmethoden** als Formate.
  - Fokus: Didaktik + Konfiguration von Aufgaben.[file:8]
- `02a_System-Features.md` (dieses Dokument):
  - Beschreibt **Tutor-, Gamification-, Kollaborations- und Infrastruktur-Features**.[file:1]
  - Fokus: System-Logik, Services, Workflows.

**Regel für zukünftige Erweiterungen:**
- Neue **Aufgabenformate** → in `02_Lernmethoden.md` aufnehmen.
- Neue **Services/Workflows um Aufgaben herum** → hier als System-Feature ergänzen.

---

*Ende: 02a – System-Features im Umfeld der Lernmethoden*
