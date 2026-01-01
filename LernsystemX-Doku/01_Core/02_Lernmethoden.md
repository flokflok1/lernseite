# 02 – Lernmethoden (19 Content-Methoden, dynamisch)

**Version:** 4.0  
**Stand:** 2025-12-28  
**Status:** Master-Dokument für Content-Lernmethoden (ohne System-Features)

---

## Einleitung

Das LernSystemX (LSX) nutzt **19 aktive Content-Lernmethoden** als didaktische Bausteine, die sich inhaltlich vollständig an unterschiedliche Kurse, Zielgruppen und Prüfungsformate anpassen lassen.[file:8][file:1]
Jede Lernmethode beschreibt ein **Aufgaben- bzw. Interaktionsformat** (z.B. Flashcards, Lückentext, Freitext-Prüfung), während die konkreten Inhalte pro Kurs und Modul frei definiert werden.[file:1]

---

## Didaktische Rollen der 19 Methoden

| Gruppe | Name | IDs | Phase im Lernprozess | Hauptziel |
|--------|------|-----|----------------------|-----------|
| **A** | Erklärend | LM00–LM03, LM06 | Einstieg, Erarbeiten | Verständnis aufbauen |
| **B** | Praxis | LM08, LM12–LM15, LM17 | Üben, Anwenden | Fertigkeiten aufbauen |
| **C** | Prüfung | LM18–LM25 | Prüfen, Transfer | Kompetenz nachweisen |

**Hinweis:** Ehemalige Gruppen **D, E, F** (Pro-, IT- und kollaborative Features) werden als **System-Features** separat dokumentiert und zählen nicht mehr zu den Content-Lernmethoden.[file:8][file:1]

---

## Technische Grundlage – Format vs. Inhalt

Die 19 Lernmethoden sind technisch als **Methodentypen** umgesetzt; jede konkrete Aufgabe im Kurs ist eine **Instanz eines Typs**.[file:1]

### Methodentypen in der Datenbank

```sql
-- Tabelle für Instanzen von Lernmethoden in Modulen
CREATE TABLE learningmethods (
    methodid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moduleid UUID REFERENCES modules(moduleid) ON DELETE CASCADE,
    methodtype INTEGER CHECK (methodtype BETWEEN 0 AND 31), -- 0 = LM00, 1 = LM01, ... 31 = LM31
    title VARCHAR(255) NOT NULL,
    instructions TEXT,
    data JSONB NOT NULL,          -- inhaltliche Ausgestaltung
    solution JSONB,
    tier VARCHAR(20) CHECK (tier IN ('basic','premium','pro')),
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy','medium','hard')),
    durationminutes INTEGER,
    orderindex INTEGER DEFAULT 0,
    published BOOLEAN DEFAULT FALSE,
    createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- **`methodtype`** legt nur das **Format** fest (z.B. Quiz, Flashcards, Lückentext).[file:1]
- **`data`** enthält die **individuellen Inhalte** der Aufgabe (Fragen, Textbausteine, Beispiele, Punkteverteilung usw.).[file:1]

### Konfiguration pro Kurs/Modul

Über zusätzliche Tabellen wie `course_module_methods` oder Konfigurationsfelder in `data` können:
- Schwierigkeitsgrade,
- Themenbereiche,
- Zeitlimits,
- Punkte-Schemata
pro Kurs oder Modul angepasst werden, ohne das Format selbst zu ändern.[file:1]

Typischer Ansatz im `data`-Feld einer Instanz:

```json
{
  "items": [
    { "q": "Was ist eine IP-Adresse?", "a": "Netzwerkadresse" },
    { "q": "Port für HTTPS?", "a": "443" }
  ],
  "topic": "Netzwerkgrundlagen",
  "difficulty": "medium",
  "max_score": 10
}
```

---

## Übersicht – 19 Content-Lernmethoden

| LM-ID | Name | Gruppe | Didaktisches Ziel | Typische Phase |
|-------|------|--------|-------------------|----------------|
| LM00 | Tiefgehende Erklärung | A – Erklärend | Komplexe Konzepte verstehen | Einstieg/Erarbeiten |
| LM01 | Schritt-für-Schritt | A – Erklärend | Prozeduren sicher nachvollziehen | Erarbeiten |
| LM02 | Interaktive Theorie | A – Erklärend | Theorie aktiv verarbeiten | Erarbeiten |
| LM03 | Diagramm/Visualisierung | A – Erklärend | Strukturen/Prozesse begreifen | Einstieg/Erarbeiten |
| LM06 | Beispiel-Szenario | A – Erklärend | Transfer in reale Situationen | Erarbeiten |
| LM08 | Whiteboard-Aufgabe | B – Praxis | Visualisierend anwenden | Üben/Anwenden |
| LM12 | Mathe-Interaktiv | B – Praxis | Rechnen/Logik schrittweise beherrschen | Üben |
| LM13 | Flashcards | B – Praxis | Fakten/Wissen langfristig behalten | Wiederholen |
| LM14 | Drag & Drop | B – Praxis | Begriffe/Strukturen sicher zuordnen | Üben |
| LM15 | Lückentext | B – Praxis | Fachbegriffe gezielt anwenden | Üben |
| LM17 | Hands-on Lab | B – Praxis | Praktische Skills im Umfeld trainieren | Anwenden |
| LM18 | Freitext-Langantwort | C – Prüfung | Zusammenhängend schreiben/argumentieren | Prüfung |
| LM19 | IHK-Stil Aufgaben | C – Prüfung | Prüfungsformat 1:1 simulieren | Prüfungsvorbereitung |
| LM20 | Multi-Step Praxisprüfung | C – Prüfung | Komplexe Handlungsketten meistern | Abschlussprüfung |
| LM21 | Zeitlimit-Training | C – Prüfung | Arbeiten unter Zeitdruck trainieren | Prüfungsvorbereitung |
| LM22 | Prüfungs-Quiz | C – Prüfung | Wissensstand schnell checken | Zwischentest |
| LM23 | Verständnis-Checks | C – Prüfung | Mikro-Checks nach Lerneinheiten | Laufende Diagnose |
| LM24 | Mündliche Erklärung | C – Prüfung | Mündlich erklären und begründen | Mdl. Prüfung |
| LM25 | Kapitel-Endprüfung | C – Prüfung | Lernfortschritt auf Kapitel-Ebene prüfen | Kapitelende |

---

## Gruppe A – Erklärend (LM00–LM03, LM06)

**Didaktische Rolle:** Lernende verstehen neue Inhalte, bauen ein tragfähiges mentales Modell auf und können Begriffe in eigenen Worten erklären.[file:8]

### LM00 – Tiefgehende Erklärung (Deep Explanation)

- **Didaktisches Ziel:** Komplexe Themen systematisch verständlich machen, inkl. Beispiele und Analogien.[file:8]
- **Einsatzszenarien:**
  - Einführung ins OSI-Modell.
  - Erklärung von Subnetting-Konzepten.
  - Grundlagen von Datenbanken (Normalformen).
- **Technische Anforderungen (typisch):**
  - Inputs: `theory_json`, `learning_goals`, ggf. `examples`.[file:1]
  - Settings: `difficulty`, `target_level` (z.B. „Azubi 1. Lehrjahr“), `max_tokens`.[file:1]
  - Optional: KI-Prompt-Key `deep_explanation` für KI-generierte Texte.[file:8]

### LM01 – Schritt-für-Schritt (Step-by-Step)

- **Didaktisches Ziel:** Prozedurales Wissen aufbauen; Lernende können Abläufe reproduzieren und später variieren.[file:8]
- **Einsatzszenarien:**
  - „Wie installiere ich einen Webserver?“.
  - „Wie richte ich einen Benutzer in Linux an?“.
  - „Wie löse ich eine lineare Gleichung?“.
- **Technische Anforderungen:**
  - Inputs: `procedure_steps` oder Roh-Text, aus dem Schritte extrahiert werden.[file:1]
  - Settings: `step_count`, `show_hints`, `allow_backtracking`.[file:1]
  - Prompt-Key: `step_by_step`.[file:8]

### LM02 – Interaktive Theorie (Interactive Theory)

- **Didaktisches Ziel:** Theorie nicht nur lesen, sondern direkt mit kleinen Fragen/Checks verknüpfen.[file:8]
- **Einsatzszenarien:**
  - Theorie-Text zu „TCP vs. UDP“ mit eingebetteten Verständnisfragen.
  - Grundlagen der Objektorientierung (Klasse, Objekt, Vererbung).
- **Technische Anforderungen:**
  - Inputs: `theory_sections`, `inline_questions`.[file:1]
  - Settings: `question_frequency`, `feedback_mode` (sofort/gebündelt).[file:1]
  - Prompt-Key: `interactive_theory`.[file:8]

### LM03 – Diagramm/Visualisierung (Diagram Visualization)

- **Didaktisches Ziel:** Abstrakte Strukturen durch visuelle Darstellungen greifbar machen.[file:8]
- **Einsatzszenarien:**
  - Netzwerk-Topologie zeichnen.
  - ER-Diagramm für eine kleine Datenbank.
  - Ablaufdiagramm für einen Login-Prozess.
- **Technische Anforderungen:**
  - Inputs: `structure_description` (z.B. JSON mit Knoten/Kanten).[file:1]
  - Settings: `diagram_type` (Netzwerk, ER, Flow), `render_engine`.[file:1]
  - Optional: Anbindung an Whiteboard/Diagramm-Tool.

### LM06 – Beispiel-Szenario (Example Scenario)

- **Didaktisches Ziel:** Theorie im Kontext realistischer Situationen anwenden.[file:8]
- **Einsatzszenarien:**
  - „Kunde meldet langsames Netzwerk – wie gehst du vor?“.
  - „Server fällt vor der Prüfung aus – welche Schritte?“.
- **Technische Anforderungen:**
  - Inputs: `scenario_description`, `expected_steps`, `evaluation_rubric`.[file:1]
  - Settings: `complexity`, `allow_multiple_solutions`.[file:1]
  - Prompt-Key: `scenario_explanation`.[file:8]

---

## Gruppe B – Praxis (LM08, LM12–LM15, LM17)

**Didaktische Rolle:** Wissen wird aktiv angewendet und in praktische Fertigkeiten überführt.[file:8]

### LM08 – Whiteboard-Aufgabe

- **Didaktisches Ziel:** Inhalte zeichnend/visuell rekonstruieren; fördert räumliches und vernetztes Denken.[file:8]
- **Einsatzszenarien:**
  - Netzwerk-Topologie skizzieren.
  - Schichtenmodell zeichnen.
- **Technische Anforderungen:**
  - Inputs: `task_description`, optionale Beispiel-Lösungen.[file:1]
  - Settings: `allow_ki_feedback`, `max_board_pages`.[file:1]
  - Prompt-Key: `whiteboard`.[file:8]

### LM12 – Mathe-Interaktiv

- **Didaktisches Ziel:** Rechenwege verstehen, nicht nur Ergebnisse auswendig lernen.[file:8]
- **Einsatzszenarien:**
  - Subnetting-Aufgaben.
  - Prozentrechnung in BWL.
- **Technische Anforderungen:**
  - Inputs: `equations`, `solution_steps` oder nur `equations` für KI-generierte Schritte.[file:1]
  - Settings: `step_by_step=true`, `show_hints`, `max_attempts`.[file:1]
  - Prompt-Key: `math_interactive`.[file:8]

### LM13 – Flashcards

- **Didaktisches Ziel:** Begriffe, Definitionen, Formeln langfristig im Gedächtnis verankern.[file:8]
- **Einsatzszenarien:**
  - Fachbegriffe Netzwerke.
  - Prüfungsrelevante Schlagworte.
- **Technische Anforderungen:**
  - Inputs: `cards` mit `front`, `back`, optional `tags`.[file:1]
  - Settings: `spaced_repetition_mode`, `new_cards_per_day`.[file:1]
  - Prompt-Key: `flashcards`.[file:8]

### LM14 – Drag & Drop

- **Didaktisches Ziel:** Zuordnungswissen und Strukturverständnis stärken.[file:8]
- **Einsatzszenarien:**
  - OSI-Schichten zu Protokollen zuordnen.
  - Begriffe den richtigen Kategorien zuordnen.
- **Technische Anforderungen:**
  - Inputs: `pairs` oder `categories` + `items`.[file:1]
  - Settings: `allow_partial_credit`, `shuffle_items`.[file:1]
  - Prompt-Key: `drag_drop`.[file:8]

### LM15 – Lückentext (Cloze)

- **Didaktisches Ziel:** Präzises Fachvokabular anwenden.[file:8]
- **Einsatzszenarien:**
  - Konfigurationssnippets mit fehlenden Parametern.
  - Theorietexte mit Schlüsselbegriffen.
- **Technische Anforderungen:**
  - Inputs: `base_text` + Markierung der Lücken oder bereits strukturiert als `gaps`.[file:1]
  - Settings: `case_sensitive`, `tolerance` (Rechtschreibung), `show_solutions`.[file:1]
  - Prompt-Key: `fill_blanks`.[file:8]

### LM17 – Hands-on Lab

- **Didaktisches Ziel:** Praktische Handlungsabläufe im „sicheren“ Umfeld trainieren.[file:8]
- **Einsatzszenarien:**
  - Linux-Commands im Terminal.
  - Router konfigurieren in einer Sandbox.
- **Technische Anforderungen:**
  - Inputs: `lab_description`, `environment_config`, `check_commands`.[file:1]
  - Settings: `time_budget`, `retry_policy`, `auto_grading`.[file:1]
  - Prompt-Key: `hands_on_lab`.[file:8]

---

## Gruppe C – Prüfung (LM18–LM25)

**Didaktische Rolle:** Lernfortschritt sichtbar machen, Prüfungsformate trainieren und Zertifikatsprüfungen simulieren.[file:8]

### LM18 – Freitext-Langantwort

- **Didaktisches Ziel:** Zusammenhängend schreiben, argumentieren und fachlich korrekt begründen.[file:8]
- **Einsatzszenarien:**
  - IHK-ähnliche Langfragen.
  - Projektreflexionen.
- **Technische Anforderungen:**
  - Inputs: `prompt`, optional `rubric` (Bewertungsraster).[file:1]
  - Settings: `min_words`, `max_words`, `allow_resubmission`.[file:1]
  - Prompt-Key: `long_answer`.[file:8]

### LM19 – IHK-Stil Aufgaben

- **Didaktisches Ziel:** Originalprüfungen möglichst nah simulieren.[file:8]
- **Einsatzszenarien:**
  - AP1/AP2-Simulationen.
  - Schulabschlussprüfungen.
- **Technische Anforderungen:**
  - Inputs: `items` mit unterschiedlichen Fragetypen (MC, Lückentext, Szenario).[file:1]
  - Settings: `exam_profile` (z.B. `IHK_FISI_AP1`), `points_per_item`.[file:1]
  - Prompt-Key: `ihk_style`.[file:8]

### LM20 – Multi-Step Praxisprüfung

- **Didaktisches Ziel:** Mehrschrittige, realistische Prüfungen mit aufeinander aufbauenden Aufgaben.[file:8]
- **Einsatzszenarien:**
  - Komplettes Netzwerkdesign + Implementierung.
  - Projektähnliche Fallstudien.
- **Technische Anforderungen:**
  - Inputs: `steps` mit eigenen Teilaufgaben.[file:1]
  - Settings: `must_pass_all_steps`, `partial_scoring`.[file:1]
  - Prompt-Key: `multi_step_exam`.[file:8]

### LM21 – Zeitlimit-Training

- **Didaktisches Ziel:** Zeitmanagement und Stressresistenz unter Prüfungsbedingungen trainieren.[file:8]
- **Einsatzszenarien:**
  - 90-Minuten-Simulation mit kleineren Aufgaben.
  - Kurze „Speed-Tests“ vor der Prüfung.
- **Technische Anforderungen:**
  - Inputs: Referenz auf andere Aufgaben/Methoden oder eingebettete Items.[file:1]
  - Settings: `time_limit_seconds`, `show_timer`, `allow_pause=false`.[file:1]
  - Prompt-Key: `time_limit`.[file:8]

### LM22 – Prüfungs-Quiz

- **Didaktisches Ziel:** Wissensstand schnell checken und gezielt Lücken finden.[file:8]
- **Einsatzszenarien:**
  - Test nach jedem Modul.
  - Vorbereitung auf große Tests.
- **Technische Anforderungen:**
  - Inputs: `questions` (MC, Single Choice, Matching) mit `correct`-Index.[file:1]
  - Settings: `randomize_order`, `show_explanations`, `pass_threshold`.[file:1]
  - Prompt-Key: `exam_quiz`.[file:8]

### LM23 – Verständnis-Checks

- **Didaktisches Ziel:** Mikro-Diagnosen direkt nach kleinen Theorieblöcken.[file:8]
- **Einsatzszenarien:**
  - Eine Frage nach jedem Unterkapitel.
  - Kurze Checks während eines Live-Vortrags.
- **Technische Anforderungen:**
  - Inputs: Einfache `single_item`-Fragen.[file:1]
  - Settings: `trigger_mode` (nach X Minuten/Abschnitten), `mandatory`.[file:1]
  - Prompt-Key: `comprehension_check`.[file:8]

### LM24 – Mündliche Erklärung

- **Didaktisches Ziel:** Fachliche Inhalte frei und verständlich mündlich darstellen.[file:8]
- **Einsatzszenarien:**
  - Mündliche IHK-Simulation.
  - Kurzpräsentationen.
- **Technische Anforderungen:**
  - Inputs: `prompt`, optional Beispielantworten.
  - Settings: `max_recording_time`, `auto_transcribe`, `rubric`.[file:1]
  - Prompt-Key: `oral_explanation`.[file:8]

### LM25 – Kapitel-Endprüfung

- **Didaktisches Ziel:** Abschließende Überprüfung eines Themenblocks.[file:8]
- **Einsatzszenarien:**
  - Ende eines Kurses oder eines großen Moduls.
- **Technische Anforderungen:**
  - Inputs: Mischung aus `items`, optional Verweise auf bestehende LM-Instanzen.[file:1]
  - Settings: `weight_in_course_grade`, `retake_policy`.[file:1]
  - Prompt-Key: `chapter_exam`.[file:8]

---

## Wahl der passenden Lernmethode

| Lernziel | Geeignete Gruppen | Typische LMs |
|----------|-------------------|--------------|
| Neues Thema verstehen | A | LM00, LM01, LM02, LM03, LM06 |
| Üben/Anwenden | B | LM08, LM12, LM13, LM14, LM15, LM17 |
| Prüfungsvorbereitung | C | LM18, LM19, LM21, LM22, LM23 |
| Abschlussprüfung | C | LM20, LM25 |

---

## Abgrenzung zu System-Features

Folgende ehemals als Lernmethoden geführten Elemente gelten nun als **System-Features** und werden in einer eigenen Dokumentation beschrieben:[file:8][file:1]

- Pro-/Gamification-Features (z.B. Adaptive Difficulty, Quest-/XP-System).
- TutorAgent/NPC-Tutor.
- IT-spezifische Werkzeuge (z.B. Code-Sandbox als Umgebung, nicht das Aufgabenformat selbst).
- Kollaborative Workflows (Peer Review, Team-Projekte, Inverted Classroom als Kurs-/LiveRoom-Logik).

Die 19 Content-Lernmethoden in diesem Dokument konzentrieren sich bewusst auf **Aufgaben- und Prüfungsformate**, die sich über Inhalte und Konfiguration in vielen Kontexten wiederverwenden lassen.[file:8]

---

*Ende: 02 – Lernmethoden (19 Content-Methoden, dynamisch)*
