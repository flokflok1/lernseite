# 02 – Lernmethoden (31 Methoden, Master-Dokument)

**Version:** 3.0
**Stand:** 2025-12-07
**Status:** Master-Dokument für alle Lernmethoden

---

## Einleitung

Das LernsystemX (LSX) arbeitet mit **31 aktiven Lernmethoden** in **6 Gruppen** (A–F). Zwei Methoden (LM05, LM07) wurden zu anderen Systemkomponenten verschoben.

### Zentrale Dokument-Referenzen

| Dokument | Inhalt |
|----------|--------|
| [04_Kurs-Architektur.md](04_Kurs-Architektur.md) | Einbindung der Lernmethoden in den Kursflow |
| [09_KI-Pipeline.md](09_KI-Pipeline.md) | Nutzung der Lernmethoden durch die KI-Generierung |
| [14_DB-Struktur.md](14_DB-Struktur.md) | Technische Verankerung in der Datenbank |
| [35_Developer-Guide-KI-Prompts.md](35_Developer-Guide-KI-Prompts.md) | KI-Prompts für jede Lernmethode |

### Gruppierung der 31 Lernmethoden

| Gruppe | Name | IDs | Anzahl | Fokus |
|--------|------|-----|--------|-------|
| **A** | Erklärend | LM00–LM03, LM06 | 5 | Verständnis aufbauen |
| **B** | Praxis | LM08, LM12–LM15, LM17 | 6 | Anwenden & Üben |
| **C** | Prüfung | LM18–LM25 | 8 | Prüfungsvorbereitung |
| **D** | Pro | LM04 | 1 | Premium-Feature |
| **E** | IT | LM09–LM11, LM16 | 4 | IT-spezifische Methoden |
| **F** | Kollaborativ | LM26–LM32 | 7 | Zusammenarbeit & Reflexion |

**Gesamt:** 5 + 6 + 8 + 1 + 4 + 7 = **31 Lernmethoden**

### Deaktivierte Methoden

| ID | Name | Ersatz |
|----|------|--------|
| LM05 | Mindmap-Generator | → CourseFeatures (kurs-weite Funktion) |
| LM07 | NPC-Tutor-Lecture | → TutorAgent (eigenständiges System) |

---

## Übersichtstabelle aller 31 Lernmethoden

| LM-ID | Name | Gruppe | Beschreibung |
|-------|------|--------|--------------|
| LM00 | Tiefgehende Erklärung | A – Erklärend | KI-generierte Erklärung mit Beispielen & Analogien |
| LM01 | Schritt-für-Schritt | A – Erklärend | Sequenzielle Anleitung in nummerierten Schritten |
| LM02 | Interaktive Theorie | A – Erklärend | Theorieblöcke mit eingebetteten Kontrollfragen |
| LM03 | Diagramm/Visualisierung | A – Erklärend | Visuelle Modelle (Netzwerk, OSI, ER, Flows) |
| LM06 | Beispiel-Szenario | A – Erklärend | Realitätsnahe Case-Erklärung eines Konzepts |
| LM08 | Whiteboard-Aufgabe | B – Praxis | Lernende zeichnen/verbinden Topologien, Skizzen |
| LM12 | Mathe-Interaktiv | B – Praxis | Rechenaufgaben mit Schritt-für-Schritt-Erklärung |
| LM13 | Flashcards | B – Praxis | Karteikarten mit Spaced-Repetition |
| LM14 | Drag & Drop | B – Praxis | Zuordnungs-/Matching-Aufgaben |
| LM15 | Lückentext | B – Praxis | Fill-in-the-blanks in Texten/Configs |
| LM17 | Hands-on Lab | B – Praxis | Virtuelle Umgebung (Terminal/IDE) mit Aufgabe |
| LM18 | Freitext-Langantwort | C – Prüfung | Lange Antworten, KI bewertet mit Rubric |
| LM19 | IHK-Stil Aufgaben | C – Prüfung | Prüfungsnahe MC/Lückentext/Szenario |
| LM20 | Multi-Step Praxisprüfung | C – Prüfung | Mehrstufige Prüfungsketten |
| LM21 | Zeitlimit-Training | C – Prüfung | Aufgaben unter Zeitdruck (Countdown) |
| LM22 | Prüfungs-Quiz | C – Prüfung | Quiz mit sofortigem Feedback |
| LM23 | Verständnis-Checks | C – Prüfung | Single-Item-Checks nach Lerneinheit |
| LM24 | Mündliche Erklärung | C – Prüfung | User erklärt mündlich, KI bewertet |
| LM25 | Kapitel-Endprüfung | C – Prüfung | Größere Prüfung am Kapitelende |
| LM04 | Sokratischer Dialog | D – Pro | KI fragt, User leitet Konzept selbst her |
| LM09 | Code/IT-Config Sandbox | E – IT | Code-/Config-Editor mit Tests & Output |
| LM10 | Netzwerk-Simulation | E – IT | Simulierte Netzumgebung (Router, Switch, Ping) |
| LM11 | IT-Szenario lösen | E – IT | Troubleshooting mit Logs/Configs |
| LM16 | Fehleranalyse | E – IT | Defekter Code/Config, Fehler finden & erklären |
| LM26 | Peer Instruction | F – Kollaborativ | Think–Pair–Share mit Erstantwort → Diskussion |
| LM27 | Team-Case / Gruppenfallarbeit | F – Kollaborativ | Teams lösen Fall mit Rollen |
| LM28 | Peer Review (strukturiert) | F – Kollaborativ | Rubric-basiertes Feedback zu Arbeiten anderer |
| LM29 | Lerntagebuch / Learning Journal | F – Kollaborativ | Regelmäßige Reflexionseinträge |
| LM30 | Projekt-Portfolio | F – Kollaborativ | Artefakte-Sammlung mit Meta-Kommentar |
| LM31 | Projektbasiertes Lernen | F – Kollaborativ | Mehrwöchiges IT-Projekt |
| LM32 | Inverted Classroom | F – Kollaborativ | Async Theorie + sync Praxis |

---

## GRUPPE A – Erklärend (5 Methoden)

**IDs:** LM00–LM03, LM06
**Fokus:** Wissen vermitteln, Konzepte erklären, Verständnis aufbauen

---

### LM00 – Tiefgehende Erklärung

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM00 |
| **Name** | Tiefgehende Erklärung |
| **Gruppe** | A – Erklärend |
| **Kurzbeschreibung** | KI-generierte Erklärung mit Beispielen & Analogien. Strukturierte, mehrstufige Erläuterungen komplexer Themen. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `deep_explanation` |

---

### LM01 – Schritt-für-Schritt

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM01 |
| **Name** | Schritt-für-Schritt |
| **Gruppe** | A – Erklärend |
| **Kurzbeschreibung** | Sequenzielle Anleitung in nummerierten Schritten. Ideal für Prozesse, Workflows und Anleitungen. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `step_by_step` |

---

### LM02 – Interaktive Theorie

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM02 |
| **Name** | Interaktive Theorie |
| **Gruppe** | A – Erklärend |
| **Kurzbeschreibung** | Theorieblöcke mit eingebetteten Kontrollfragen. Aktive Einbindung des Lernenden. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `interactive_theory` |

---

### LM03 – Diagramm/Visualisierung

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM03 |
| **Name** | Diagramm/Visualisierung |
| **Gruppe** | A – Erklärend |
| **Kurzbeschreibung** | Visuelle Modelle (Netzwerk, OSI, ER, Flows). Unterstützt Verständnis durch grafische Darstellung. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `visualization` |

---

### LM06 – Beispiel-Szenario

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM06 |
| **Name** | Beispiel-Szenario |
| **Gruppe** | A – Erklärend |
| **Kurzbeschreibung** | Realitätsnahe Case-Erklärung eines Konzepts. Zeigt praktische Anwendung von Theorie. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `scenario_explanation` |

---

## GRUPPE B – Praxis (6 Methoden)

**IDs:** LM08, LM12–LM15, LM17
**Fokus:** Wissen anwenden, üben, praktische Fertigkeiten entwickeln

---

### LM08 – Whiteboard-Aufgabe

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM08 |
| **Name** | Whiteboard-Aufgabe |
| **Gruppe** | B – Praxis |
| **Kurzbeschreibung** | Lernende zeichnen/verbinden Topologien, Skizzen. KI analysiert und gibt Feedback. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `whiteboard` |

---

### LM12 – Mathe-Interaktiv

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM12 |
| **Name** | Mathe-Interaktiv |
| **Gruppe** | B – Praxis |
| **Kurzbeschreibung** | Rechenaufgaben mit Schritt-für-Schritt-Erklärung. Unterstützt BWL, Subnetting, Hex. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `math_interactive` |

---

### LM13 – Flashcards

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM13 |
| **Name** | Flashcards |
| **Gruppe** | B – Praxis |
| **Kurzbeschreibung** | Karteikarten mit Spaced-Repetition. Begriffe, Definitionen, Formeln. |
| **KI-Nutzung** | Optional |
| **Prompt-Key** | `flashcards` |

---

### LM14 – Drag & Drop

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM14 |
| **Name** | Drag & Drop |
| **Gruppe** | B – Praxis |
| **Kurzbeschreibung** | Zuordnungs-/Matching-Aufgaben. Elemente in richtige Kategorien ziehen. |
| **KI-Nutzung** | Optional |
| **Prompt-Key** | `drag_drop` |

---

### LM15 – Lückentext

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM15 |
| **Name** | Lückentext |
| **Gruppe** | B – Praxis |
| **Kurzbeschreibung** | Fill-in-the-blanks in Texten/Configs. Testet präzises Fachwissen. |
| **KI-Nutzung** | Optional |
| **Prompt-Key** | `fill_blanks` |

---

### LM17 – Hands-on Lab

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM17 |
| **Name** | Hands-on Lab |
| **Gruppe** | B – Praxis |
| **Kurzbeschreibung** | Virtuelle Umgebung (Terminal/IDE) mit Aufgabe. Praktische Übungen in simulierter Umgebung. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `hands_on_lab` |

---

## GRUPPE C – Prüfung (8 Methoden)

**IDs:** LM18–LM25
**Fokus:** Prüfungsvorbereitung, Wissensüberprüfung, Zertifizierungstraining

---

### LM18 – Freitext-Langantwort

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM18 |
| **Name** | Freitext-Langantwort |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | Lange Antworten, KI bewertet mit Rubric. Ausführliche schriftliche Prüfungsaufgaben. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `long_answer` |

---

### LM19 – IHK-Stil Aufgaben

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM19 |
| **Name** | IHK-Stil Aufgaben |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | Prüfungsnahe MC/Lückentext/Szenario im IHK-Format. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `ihk_style` |

---

### LM20 – Multi-Step Praxisprüfung

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM20 |
| **Name** | Multi-Step Praxisprüfung |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | Mehrstufige Prüfungsketten mit aufeinander aufbauenden Aufgaben. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `multi_step_exam` |

---

### LM21 – Zeitlimit-Training

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM21 |
| **Name** | Zeitlimit-Training |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | Aufgaben unter Zeitdruck (Countdown). Simuliert Prüfungssituation. |
| **KI-Nutzung** | Optional |
| **Prompt-Key** | `time_limit` |

---

### LM22 – Prüfungs-Quiz

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM22 |
| **Name** | Prüfungs-Quiz |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | Quiz mit sofortigem Feedback. MC, Single Choice, Matching. |
| **KI-Nutzung** | Optional |
| **Prompt-Key** | `exam_quiz` |

---

### LM23 – Verständnis-Checks

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM23 |
| **Name** | Verständnis-Checks |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | Single-Item-Checks nach Lerneinheit. Schnelle Wissensüberprüfung. |
| **KI-Nutzung** | Optional |
| **Prompt-Key** | `comprehension_check` |

---

### LM24 – Mündliche Erklärung

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM24 |
| **Name** | Mündliche Erklärung |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | User erklärt mündlich, KI bewertet. Speech-to-Text + inhaltliche Analyse. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `oral_explanation` |

---

### LM25 – Kapitel-Endprüfung

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM25 |
| **Name** | Kapitel-Endprüfung |
| **Gruppe** | C – Prüfung |
| **Kurzbeschreibung** | Größere Prüfung am Kapitelende. Kombiniert verschiedene Fragetypen. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `chapter_exam` |

---

## GRUPPE D – Pro (1 Methode)

**IDs:** LM04
**Fokus:** Premium-Feature für fortgeschrittenes Lernen

---

### LM04 – Sokratischer Dialog

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM04 |
| **Name** | Sokratischer Dialog |
| **Gruppe** | D – Pro |
| **Kurzbeschreibung** | KI fragt, User leitet Konzept selbst her. Fördert kritisches Denken durch geleitete Reflexion. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `socratic_dialog` |

---

## GRUPPE E – IT (4 Methoden)

**IDs:** LM09–LM11, LM16
**Fokus:** IT-spezifische praktische Übungen

---

### LM09 – Code/IT-Config Sandbox

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM09 |
| **Name** | Code/IT-Config Sandbox |
| **Gruppe** | E – IT |
| **Kurzbeschreibung** | Code-/Config-Editor mit Tests & Output. Unterstützt Python, JS, SQL, Bash. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `code_sandbox` |

---

### LM10 – Netzwerk-Simulation

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM10 |
| **Name** | Netzwerk-Simulation |
| **Gruppe** | E – IT |
| **Kurzbeschreibung** | Simulierte Netzumgebung (Router, Switch, Ping). Topologie-Aufbau und Konfiguration. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `network_sim` |

---

### LM11 – IT-Szenario lösen

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM11 |
| **Name** | IT-Szenario lösen |
| **Gruppe** | E – IT |
| **Kurzbeschreibung** | Troubleshooting mit Logs/Configs. Komplexe mehrstufige IT-Case-Studies. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `it_scenario` |

---

### LM16 – Fehleranalyse

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM16 |
| **Name** | Fehleranalyse |
| **Gruppe** | E – IT |
| **Kurzbeschreibung** | Defekter Code/Config, Fehler finden & erklären. Debugging-Skills entwickeln. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `error_analysis` |

---

## GRUPPE F – Kollaborativ (7 Methoden)

**IDs:** LM26–LM32
**Fokus:** Zusammenarbeit, Peer-Learning, Reflexion

---

### LM26 – Peer Instruction

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM26 |
| **Name** | Peer Instruction |
| **Gruppe** | F – Kollaborativ |
| **Kurzbeschreibung** | Think–Pair–Share mit Erstantwort → Diskussion. Lernende erklären sich gegenseitig. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `peer_instruction` |

---

### LM27 – Team-Case / Gruppenfallarbeit

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM27 |
| **Name** | Team-Case / Gruppenfallarbeit |
| **Gruppe** | F – Kollaborativ |
| **Kurzbeschreibung** | Teams lösen Fall mit Rollen. Komplexe Fallstudien in Gruppenarbeit. |
| **KI-Nutzung** | Intensiv |
| **Prompt-Key** | `team_case` |

---

### LM28 – Peer Review (strukturiert)

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM28 |
| **Name** | Peer Review (strukturiert) |
| **Gruppe** | F – Kollaborativ |
| **Kurzbeschreibung** | Rubric-basiertes Feedback zu Arbeiten anderer. Gegenseitige Bewertung nach Kriterien. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `peer_review` |

---

### LM29 – Lerntagebuch / Learning Journal

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM29 |
| **Name** | Lerntagebuch / Learning Journal |
| **Gruppe** | F – Kollaborativ |
| **Kurzbeschreibung** | Regelmäßige Reflexionseinträge. KI gibt Feedback auf Einträge. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `learning_journal` |

---

### LM30 – Projekt-Portfolio

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM30 |
| **Name** | Projekt-Portfolio |
| **Gruppe** | F – Kollaborativ |
| **Kurzbeschreibung** | Artefakte-Sammlung mit Meta-Kommentar. Dokumentation des Lernfortschritts. |
| **KI-Nutzung** | Optional |
| **Prompt-Key** | `portfolio` |

---

### LM31 – Projektbasiertes Lernen

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM31 |
| **Name** | Projektbasiertes Lernen |
| **Gruppe** | F – Kollaborativ |
| **Kurzbeschreibung** | Mehrwöchiges IT-Projekt. Längerfristige Projekte mit Meilensteinen und KI-Coaching. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `project_based` |

---

### LM32 – Inverted Classroom

| Eigenschaft | Details |
|-------------|---------|
| **ID** | LM32 |
| **Name** | Inverted Classroom |
| **Gruppe** | F – Kollaborativ |
| **Kurzbeschreibung** | Async Theorie + sync Praxis. Vorbereitung zu Hause, Vertiefung in der Gruppe. |
| **KI-Nutzung** | Mittel |
| **Prompt-Key** | `inverted_classroom` |

---

## Zusammenfassung

### Methodenverteilung (31 Methoden)

| Gruppe | Name | IDs | Anzahl |
|--------|------|-----|--------|
| **A** | Erklärend | LM00–LM03, LM06 | 5 |
| **B** | Praxis | LM08, LM12–LM15, LM17 | 6 |
| **C** | Prüfung | LM18–LM25 | 8 |
| **D** | Pro | LM04 | 1 |
| **E** | IT | LM09–LM11, LM16 | 4 |
| **F** | Kollaborativ | LM26–LM32 | 7 |

**Gesamt:** 5 + 6 + 8 + 1 + 4 + 7 = **31 Lernmethoden**

### Code-Referenzen

| Datei | Beschreibung |
|-------|--------------|
| `backend/app/ki/learning_method_mapping.py` | Backend-Definitionen aller LMs |
| `frontend/src/config/learningMethods.ts` | Frontend-Konfiguration |
| `backend/app/api/admin_learning_methods.py` | Admin-API-Endpoints |

---

## Dokument-Metadaten

| Eigenschaft | Wert |
|-------------|------|
| **Version** | 3.0 |
| **Status** | Master-Dokument |
| **Aktualisiert** | 2025-12-07 |
| **Autor** | LSX Development Team |

---

> Dieses Dokument definiert alle **31 aktiven Lernmethoden** des LernsystemX (LSX). Es ist das Master-Dokument für alle Referenzen auf Lernmethoden in der gesamten Dokumentation und im Code.
