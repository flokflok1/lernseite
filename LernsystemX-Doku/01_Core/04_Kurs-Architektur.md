# 04 – Kurs-Architektur (Final)

**Version:** 1.0
**Stand:** Final

---

## Überblick

Die LSX-Kursarchitektur definiert eine **flexible, skalierbare, KI-fähige** Struktur für Lerninhalte, die von allen Rollen (Premium, Creator, Lehrer, Schulen, Unternehmen) genutzt werden kann.

### 🏗️ Kurs-Architektur (C4 Model - Container)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title LSX Kurs-Architektur - Gesamtübersicht

Person(user, "Lernender", "Konsumiert Kurse")
Person(creator, "Creator", "Erstellt & verkauft Kurse")
Person(teacher, "Lehrer", "Erstellt Unterrichtsinhalte")

Container_Boundary(course_system, "Kurssystem") {
    Container(course, "Kurs", "Core Entity", "Metadaten, Einstellungen, Sichtbarkeit")
    Container(modules, "Module", "Lerneinheiten", "Strukturiert Kursinhalte in Themen")
    Container(theory, "Theorie-Blätter", "Wissensbasis", "Zentrale Lerndokumente")
    Container(methods, "Lernmethoden", "12 Content-LMs (A-C)", "Interaktive Übungen & Tests")
    Container(exams, "Prüfungen", "Assessment", "Tests & Zertifikate")
}

Container_Boundary(ki_system, "KI-Pipeline") {
    Container(ki_gen, "KI-Generator", "Content Creation", "Generiert Module & Methoden")
    Container(ki_trans, "Übersetzung", "20 Sprachen", "Global Publishing")
}

ContainerDb(db, "PostgreSQL", "Database", "Persistiert alle Kursdaten")
ContainerDb(storage, "File Storage", "S3/Local", "PDFs, Videos, Bilder")

Rel(user, course, "Belegt", "HTTPS")
Rel(creator, course, "Erstellt & Verkauft", "HTTPS")
Rel(teacher, course, "Erstellt für Klassen", "HTTPS")

Rel(course, modules, "Enthält", "1:n")
Rel(modules, theory, "Hat", "1:1")
Rel(modules, methods, "Enthält", "1:n")
Rel(course, exams, "Kann haben", "1:n")

Rel(ki_gen, modules, "Generiert")
Rel(ki_gen, methods, "Generiert")
Rel(ki_trans, course, "Übersetzt")

Rel(course, db, "Speichert")
Rel(modules, db, "Speichert")
Rel(theory, storage, "Referenziert Medien")

note right of course
  Kursarten:
  - Private
  - Community
  - Marketplace
  - School/Company Internal
end note

note right of modules
  Jedes Modul (Kapitel):
  - 1 Theorie-Blatt (Pflicht)
  - 12 Content-Lernmethoden (siehe 02_Lernmethoden.md)
  - Optional: Quiz-Pool
  - Optional: Kapitel-Endprüfung (LM25)
end note

@enduml
```

---

## 1. Grundaufbau eines Kurses

### 📊 Kurskomponenten

Ein LSX-Kurs besteht aus folgenden Hauptkomponenten:

| Komponente | Beschreibung | Pflicht |
|------------|--------------|---------|
| **Kurs-Metadaten** | Titel, Beschreibung, Kategorie, Sprache | ✅ |
| **Module** | Thematische Lerneinheiten | ✅ (mind. 1) |
| **Theorie-Blätter** | Zentrale Wissensdokumente pro Modul | ✅ (1 pro Modul) |
| **Lernmethoden** | 12 Content-Lernmethoden (siehe [02_Lernmethoden.md](02_Lernmethoden.md)) | Optional |
| **Prüfungen** | Tests & Simulationen | Optional |
| **KI-Materialien** | Zusatzinhalte, Zusammenfassungen | Optional |
| **Ressourcen** | PDFs, Videos, Links | Optional |

### 🔄 Kurs-Hierarchie

```plantuml
@startuml
title Kurs-Hierarchie

package "Kurs" {
  [Kurs-Metadaten]

  package "Modul 1 (Kapitel)" {
    [Theorie-Blatt 1]
    [LM13: Flashcards]
    [LM22: Prüfungs-Quiz]
    [LM05: Mindmap-Generator]
  }

  package "Modul 2 (Kapitel)" {
    [Theorie-Blatt 2]
    [LM03: Diagramm/Visualisierung]
    [LM11: IT-Szenario lösen]
    [LM25: Kapitel-Endprüfung]
  }

  package "Modul N" {
    [Theorie-Blatt N]
    [Methode N.1]
    [Methode N.2]
  }

  package "Prüfungen" {
    [Übungsprüfung]
    [KI-Simulation]
    [Abschlussprüfung]
  }
}

[Kurs-Metadaten] --> "Modul 1"
[Kurs-Metadaten] --> "Modul 2"
[Kurs-Metadaten] --> "Modul N"
[Kurs-Metadaten] --> "Prüfungen"

"Modul 1 (Kapitel)" --> [Theorie-Blatt 1] : 1:1
"Modul 1 (Kapitel)" --> [LM13: Flashcards] : 1:n
"Modul 1 (Kapitel)" --> [LM22: Prüfungs-Quiz] : 1:n
"Modul 1 (Kapitel)" --> [LM05: Mindmap-Generator] : 1:n

@enduml
```

---

## 2. Kursdaten – Metadatenstruktur

### 📋 Kurs-Metadaten (course)

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x

entity "courses" as course {
  primary_key(course_id) : UUID
  --
  title : VARCHAR(255)
  subtitle : VARCHAR(255)
  description : TEXT
  foreign_key(category_id) : INTEGER
  foreign_key(subcategory_id) : INTEGER
  language : VARCHAR(10)
  target_group : VARCHAR(100)
  level : ENUM
  foreign_key(created_by) : UUID
  creator_role : VARCHAR(50)
  visibility : ENUM
  tags : JSONB
  thumbnail : VARCHAR(500)
  duration_estimate : INTEGER
  learning_goals : JSONB
  requirements : JSONB
  global_published : BOOLEAN
  languages_available : JSONB
  version : INTEGER
  is_published : BOOLEAN
  draft_state : BOOLEAN
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
  last_edit_by : UUID
}

entity "course_categories" as category {
  primary_key(category_id) : INTEGER
  --
  name : VARCHAR(100)
  description : TEXT
}

entity "course_subcategories" as subcat {
  primary_key(subcategory_id) : INTEGER
  --
  foreign_key(category_id) : INTEGER
  name : VARCHAR(100)
}

entity "users" as user {
  primary_key(user_id) : UUID
  --
  email : VARCHAR(255)
  role_id : INTEGER
}

course }o--|| category
course }o--|| subcat
course }o--|| user : "created_by"

@enduml
```

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `course_id` | UUID | Eindeutiger Kurs-Identifier |
| `title` | VARCHAR(255) | Kurstitel |
| `subtitle` | VARCHAR(255) | Untertitel |
| `description` | TEXT | Ausführliche Kursbeschreibung |
| `category_id` | INTEGER | Kategorie (IT, BWL, Sprachen) |
| `subcategory_id` | INTEGER | Unterkategorie (CompTIA, Netzwerk) |
| `language` | VARCHAR(10) | Primärsprache (de, en, pl) |
| `target_group` | VARCHAR(100) | Zielgruppe (Azubis, Schüler, Anfänger) |
| `level` | ENUM | Schwierigkeitsgrad (Beginner, Intermediate, Advanced) |
| `created_by` | UUID | Ersteller (user_id) |
| `creator_role` | VARCHAR(50) | Rolle des Erstellers |
| `visibility` | ENUM | Sichtbarkeitsstufe |
| `tags` | JSONB | Schlagwörter |
| `thumbnail` | VARCHAR(500) | Vorschaubild-URL |
| `duration_estimate` | INTEGER | Geschätzte Lernzeit (Minuten) |
| `learning_goals` | JSONB | Lernziele |
| `requirements` | JSONB | Voraussetzungen |
| `global_published` | BOOLEAN | Für Global Publishing markiert |
| `languages_available` | JSONB | Verfügbare Sprachversionen |
| `version` | INTEGER | Versionnummer |
| `is_published` | BOOLEAN | Veröffentlicht |
| `draft_state` | BOOLEAN | Entwurfs-Modus |

---

## 3. Kursarten

### 🎯 Kurstypen-Übersicht

```plantuml
@startuml
title Kursarten im LSX-System

package "Kursarten" {

  rectangle "Private Kurse" #LightGray {
    (Premium User)
    (Creator)
    note right
      - Nur für eigenen Gebrauch
      - Nicht öffentlich sichtbar
      - KI-Unterstützung möglich
      - Keine Monetarisierung
    end note
  }

  rectangle "Community Kurse" #LightGreen {
    (Premium User)
    (Creator)
    note right
      - Öffentlich & kostenlos
      - Für alle sichtbar
      - Von Moderatoren geprüft
      - Keine Bezahlung
    end note
  }

  rectangle "Marketplace Kurse" #LightBlue {
    (Creator ONLY)
    note right
      - Kostenpflichtig
      - 75% Revenue Share
      - Global Publishing (20 Sprachen)
      - Zertifikate optional
    end note
  }

  rectangle "Schul-/Unternehmenskurse" #LightCoral {
    (Schule)
    (Unternehmen)
    (Lehrer)
    note right
      - Intern für Organisation
      - Klassen/Teams
      - Kein öffentlicher Verkauf
      - Vorlagen kopierbar
    end note
  }

  rectangle "LSX Academy" #Gold {
    (Admin)
    note right
      - Offiziell von LSX
      - Höchste Qualität
      - Vorlagen für Schulen
      - Kostenlos oder Premium
    end note
  }
}

@enduml
```

### Detaillierte Kursarten

#### 3.1 Private Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | Premium User, Creator, Lehrer, Schulen, Unternehmen |
| **Sichtbarkeit** | Nur für Ersteller |
| **KI-Zugriff** | ✅ Für Premium+ |
| **Monetarisierung** | ❌ Keine |
| **Global Publishing** | ❌ Nicht verfügbar |
| **Zweck** | Eigenes Lernen, Vorbereitung |

#### 3.2 Community Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | Premium User, Creator |
| **Sichtbarkeit** | Öffentlich für alle LSX-User |
| **Preis** | ✅ Immer kostenlos |
| **Methoden** | Gruppe A+B+C (keine Gruppe D-Erstellung durch Premium) |
| **Moderation** | ✅ Kann geprüft/gesperrt werden |
| **Zweck** | Community-Beitrag, Teilen von Wissen |

#### 3.3 Marketplace Kurse (Creator ONLY)

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | ✅ Nur Creator |
| **Sichtbarkeit** | Öffentlich im Marketplace |
| **Preis** | Frei wählbar (Creator setzt Preis) |
| **Revenue Share** | 75% Creator / 25% Plattform |
| **Global Publishing** | ✅ Bis zu 20 Sprachen |
| **Zertifikate** | ✅ Optional |
| **Qualitätskontrolle** | Initial-Review durch Moderatoren |

#### 3.4 Schul-/Unternehmenskurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | Schulen, Unternehmen, Lehrer (zugeordnet) |
| **Sichtbarkeit** | Nur innerhalb der Organisation |
| **Vorlagen** | ✅ LSX Academy & Creator-Kurse kopierbar |
| **Anpassung** | ✅ Vollständig anpassbar |
| **Monetarisierung** | ❌ Keine öffentlichen Verkäufe |
| **Zweck** | Interne Schulungen, Klassen, Teams |

#### 3.5 LSX Academy Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | ✅ Nur LSX-Admins |
| **Qualität** | Höchster Standard |
| **Verwendung** | Vorlagen für Schulen/Unternehmen |
| **Preis** | Kostenlos oder Premium-exklusiv |
| **Zertifikate** | ✅ Offizielle LSX-Zertifikate |

---

## 4. Modul-Struktur

### 🧩 Modul-Datenmodell

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x

entity "modules" as module {
  primary_key(module_id) : UUID
  --
  foreign_key(course_id) : UUID
  title : VARCHAR(255)
  description : TEXT
  order_index : INTEGER
  estimated_time : INTEGER
  foreign_key(theory_sheet_id) : UUID
  resources : JSONB
  quiz_pool_id : UUID
  created_at : TIMESTAMP
  updated_at : TIMESTAMP
}

entity "courses" as course {
  primary_key(course_id) : UUID
  --
  title : VARCHAR(255)
}

entity "theory_sheets" as theory {
  primary_key(theory_sheet_id) : UUID
  --
  foreign_key(module_id) : UUID
  title : VARCHAR(255)
  intro_text : TEXT
  main_theory : TEXT
  examples : JSONB
  tables : JSONB
  graphics : JSONB
  glossary_terms : JSONB
  notes_section : TEXT
  references : JSONB
}

entity "learning_methods" as method {
  primary_key(method_instance_id) : UUID
  --
  foreign_key(module_id) : UUID
  method_type : INTEGER
  method_data : JSONB
  requires_ki : BOOLEAN
  foreign_key(created_by) : UUID
  visible_to : JSONB
  language_variants : JSONB
}

module }o--|| course : "belongs to"
theory ||--|| module : "1:1"
method }o--|| module : "contains"

@enduml
```

### Modul-Datenfelder

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `module_id` | UUID | Eindeutiger Modul-Identifier |
| `course_id` | UUID | Zugehöriger Kurs |
| `title` | VARCHAR(255) | Modultitel |
| `description` | TEXT | Modulbeschreibung |
| `order_index` | INTEGER | Reihenfolge im Kurs (1, 2, 3, ...) |
| `estimated_time` | INTEGER | Geschätzte Lernzeit (Minuten) |
| `theory_sheet_id` | UUID | Verweis auf Theorie-Blatt (1:1) |
| `resources` | JSONB | Liste von Dateien/Links |
| `quiz_pool_id` | UUID | Optional: Fragenpool |

### Modul-Regeln

| Regel | Beschreibung |
|-------|--------------|
| ✅ **Theorie-Pflicht** | Jedes Modul MUSS ein Theorie-Blatt haben |
| ✅ **Methoden-Flexibilität** | Jedes Modul KANN mehrere Content-Lernmethoden enthalten |
| ✅ **Reihenfolge** | Module werden über `order_index` sortiert |
| ✅ **Unabhängigkeit** | Module können einzeln konsumiert werden |

---

## 5. Theorie-Blatt (Zentrale Wissensbasis)

### 📖 Theorie-Blatt-Struktur

Das Theorie-Blatt ist das **Fundament** jedes Moduls und MUSS immer vorhanden sein.

```plantuml
@startuml
title Theorie-Blatt Aufbau

package "Theorie-Blatt" {
  rectangle "Header" {
    [Titel]
    [Lernziele]
    [Zeitangabe]
  }

  rectangle "Intro" {
    [Einführungstext]
    [Motivation]
  }

  rectangle "Haupttheorie" {
    [Konzepte]
    [Definitionen]
    [Erklärungen]
  }

  rectangle "Beispiele" {
    [Praktische Beispiele]
    [Analogien]
    [Stories (optional)]
  }

  rectangle "Visuelle Elemente" {
    [Tabellen]
    [Diagramme]
    [Grafiken]
  }

  rectangle "Glossar" {
    [Begriffe]
    [Definitionen]
  }

  rectangle "Zusammenfassung" {
    [Key Points]
    [Merksätze]
  }

  rectangle "Referenzen" {
    [Quellen]
    [Weiterführende Links]
  }
}

[Header] --> [Intro]
[Intro] --> [Haupttheorie]
[Haupttheorie] --> [Beispiele]
[Beispiele] --> [Visuelle Elemente]
[Visuelle Elemente] --> [Glossar]
[Glossar] --> [Zusammenfassung]
[Zusammenfassung] --> [Referenzen]

@enduml
```

### Theorie-Blatt-Datenfelder

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `theory_sheet_id` | UUID | Eindeutiger Identifier |
| `module_id` | UUID | Zugehöriges Modul (1:1) |
| `title` | VARCHAR(255) | Titel des Theorie-Blatts |
| `intro_text` | TEXT | Einführung & Motivation |
| `main_theory` | TEXT | Haupttheoretischer Inhalt |
| `examples` | JSONB | Liste von Beispielen |
| `tables` | JSONB | Tabellenstrukturen |
| `graphics` | JSONB | Referenzen zu Bildern/Diagrammen |
| `glossary_terms` | JSONB | Begriffe & Definitionen |
| `notes_section` | TEXT | Bereich für Notizen (Lernende) |
| `references` | JSONB | Quellenangaben |

### Erstellungsmöglichkeiten

```plantuml
@startuml
title Theorie-Blatt Erstellungspfade

actor "Creator/Lehrer" as creator

rectangle "Manuelle Erstellung" #LightBlue {
  [Text-Editor]
  [WYSIWYG-Editor]
  [Markdown]
}

rectangle "KI-Gestützt" #LightYellow {
  [PDF/DOCX Upload]
  [Foliensatz Upload]
  [Text-Eingabe]
}

rectangle "KI-Pipeline" #LightGreen {
  [Parser]
  [Strukturierung]
  [Theorieblatt-Generator]
}

database "Theorie-Blatt" as theory

creator --> "Manuelle Erstellung"
creator --> "KI-Gestützt"

"Manuelle Erstellung" --> theory
"KI-Gestützt" --> "KI-Pipeline"
"KI-Pipeline" --> theory

note right of "KI-Pipeline"
  Extrahiert:
  - Überschriften
  - Absätze
  - Beispiele
  - Tabellen
  - Formeln
end note

@enduml
```

### KI-Unterstützung für Theorie-Blätter

| Funktion | Verfügbar für | Beschreibung |
|----------|---------------|--------------|
| **Zusammenfassung** | Premium, Creator, Lehrer, School, Company | KI generiert kurze Zusammenfassung |
| **Vereinfachung** | Premium, Creator, Lehrer, School, Company | "Erkläre wie für Anfänger" |
| **Beispiele generieren** | Premium, Creator, Lehrer, School, Company | Praktische Beispiele hinzufügen |
| **Analogien erstellen** | Premium, Creator, Lehrer, School, Company | Metaphern & Vergleiche |
| **Story-Modus** | Premium, Creator, Lehrer, School, Company | Thema als Geschichte erzählt |
| **Übersetzung** | Creator, School, Company | Global Publishing (20 Sprachen) |

---

## 6. Lernmethoden in Modulen

### 🎯 Methoden-Integration

Ein Modul kann **mehrere Lernmethoden** enthalten. Jede Methode ist eine Instanz eines der 12 Content-Lernmethodentypen (definiert in [02_Lernmethoden.md](02_Lernmethoden.md)).

```plantuml
@startuml
title Lernmethoden-Instanzen in Modulen

package "Modul: OSI-Modell" {
  rectangle "Theorie-Blatt" #LightBlue {
    [OSI-7-Schichten erklärt]
  }

  rectangle "Lernmethoden" #LightGreen {
    [Methode 1: Flashcards] #LightYellow
    [Methode 2: MCQ Quiz] #LightYellow
    [Methode 4: Matching] #LightYellow
    [Methode 14: Timeline] #LightCyan
    [LM08: Whiteboard-Aufgabe] #LightCoral
  }
}

[OSI-7-Schichten erklärt] --> [Methode 1: Flashcards]
[OSI-7-Schichten erklärt] --> [Methode 2: MCQ Quiz]
[OSI-7-Schichten erklärt] --> [Methode 4: Matching]
[OSI-7-Schichten erklärt] --> [Methode 14: Timeline]
[OSI-7-Schichten erklärt] --> [LM08: Whiteboard-Aufgabe]

note right of "Lernmethoden"
  - Flashcards: Schichten auswendig lernen
  - MCQ: Wissenstest
  - Matching: Schicht ↔ Funktion
  - Timeline: Datenfluss visualisieren
  - Whiteboard-KI: Netzwerk zeichnen
end note

@enduml
```

### Methoden-Datenstruktur

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `method_instance_id` | UUID | Eindeutige Instanz-ID |
| `module_id` | UUID | Zugehöriges Modul |
| `method_type` | INTEGER | Methodentyp (12 Content-LMs, siehe 02_Lernmethoden.md) |
| `method_data` | JSONB | Methodenspezifische Daten |
| `requires_ki` | BOOLEAN | KI erforderlich? |
| `created_by` | UUID | Ersteller |
| `visible_to` | JSONB | Rollenbasierte Sichtbarkeit |
| `language_variants` | JSONB | Übersetzungen |

### Methoden-Beispiel: Flashcards (Typ 1)

```json
{
  "method_instance_id": "uuid-123",
  "module_id": "module-uuid-456",
  "method_type": 1,
  "method_data": {
    "cards": [
      {
        "card_id": "card-1",
        "front": "Was ist die OSI-Schicht 7?",
        "back": "Application Layer - Anwendungsschicht",
        "tags": ["OSI", "Netzwerk"],
        "order": 1
      },
      {
        "card_id": "card-2",
        "front": "Was ist die OSI-Schicht 1?",
        "back": "Physical Layer - Bitübertragungsschicht",
        "tags": ["OSI", "Netzwerk"],
        "order": 2
      }
    ]
  },
  "requires_ki": false,
  "created_by": "creator-uuid",
  "visible_to": ["free", "premium", "creator"],
  "language_variants": {
    "de": "method_data above",
    "en": {
      "cards": [
        {
          "front": "What is OSI Layer 7?",
          "back": "Application Layer"
        }
      ]
    }
  }
}
```

---

## 7. Prüfungstypen

### 📝 Prüfungsarchitektur

```plantuml
@startuml
title Prüfungstypen im LSX-System

package "Prüfungen" {

  rectangle "Übungsprüfung" #LightGreen {
    [Quiz-Fragen Pool]
    [Zufällige Auswahl]
    [Zeitlimit optional]

    note right
      - Basis-Methode
      - Kein KI erforderlich
      - Für alle User
    end note
  }

  rectangle "KI-Prüfungssimulation" #LightYellow {
    [Theorie-Analyse]
    [Fragen-Generierung]
    [IHK/CompTIA Standard]

    note right
      - Pro-Methode #20
      - KI-generiert
      - Premium konsumiert
      - Creator/School erstellt
    end note
  }

  rectangle "Abschlussprüfung" #LightCoral {
    [Basis + KI]
    [Zertifikat]
    [Score-Tracking]

    note right
      - Kombination
      - Zertifikatsvergabe
      - Offiziell
    end note
  }
}

[Übungsprüfung] ..> [Quiz-Fragen Pool] : nutzt
[KI-Prüfungssimulation] ..> [Theorie-Analyse] : analysiert
[Abschlussprüfung] ..> [Basis + KI] : kombiniert

@enduml
```

### 7.1 Übungsprüfung (Basis)

| Eigenschaft | Details |
|-------------|---------|
| **Typ** | `practice` |
| **KI-Bedarf** | ❌ Keine |
| **Quelle** | Vorhandene Quiz-Fragen |
| **Zugriff** | Free, Premium, alle Rollen |
| **Zeitlimit** | Optional |
| **Auswertung** | Sofort |

**Datenstruktur:**

```json
{
  "exam_id": "uuid-exam-1",
  "course_id": "course-uuid",
  "type": "practice",
  "title": "OSI-Modell Übungsprüfung",
  "question_ids": ["q1", "q2", "q3", "q4", "q5"],
  "time_limit": 1800,
  "passing_score": 70
}
```

### 7.2 KI-Prüfungssimulation (Pro-Methode #20)

| Eigenschaft | Details |
|-------------|---------|
| **Typ** | `ai_simulation` |
| **KI-Bedarf** | ✅ Erforderlich |
| **Erstellen** | Creator, Lehrer, School, Company |
| **Konsumieren** | Premium+ |
| **Standards** | IHK, CompTIA, Schulcurriculum, Custom |

**Workflow:**

```plantuml
@startuml
title KI-Prüfungssimulation - Generierungsprozess

actor Creator

box "Input" #LightBlue
  participant "Theorie-Blätter" as theory
  participant "Module" as modules
  participant "Lernziele" as goals
end box

box "KI-Pipeline" #LightYellow
  participant "Content Analyzer" as analyzer
  participant "Question Generator" as generator
  participant "Difficulty Balancer" as balancer
  participant "Standard Validator" as validator
end box

box "Output" #LightGreen
  database "Prüfung" as exam
end box

Creator -> theory : Wählt Module
Creator -> modules : Definiert Umfang
Creator -> goals : Setzt Standard (z.B. IHK FISI)

theory -> analyzer : Analysiert Inhalte
modules -> analyzer : Extrahiert Themen
goals -> analyzer : Berücksichtigt Standard

analyzer -> generator : Erzeugt Fragen
generator -> balancer : Verteilt Schwierigkeit
balancer -> validator : Prüft Standard-Konformität

validator -> exam : Speichert Prüfung
exam -> Creator : Vorschau & Anpassung

note right of generator
  Generiert:
  - MCQ
  - Fallstudien
  - Rechenaufgaben
  - Freitext
end note

@enduml
```

**Datenstruktur:**

```json
{
  "exam_id": "uuid-exam-ai-1",
  "course_id": "course-uuid",
  "type": "ai_simulation",
  "title": "IHK FISI AP1 Simulation",
  "source_modules": ["mod1", "mod2", "mod3"],
  "difficulty_level": "intermediate",
  "exam_profile": "IHK_FISI_AP1",
  "generated_by_ai": true,
  "ai_model": "claude-sonnet-4-20250514",
  "questions": [
    {
      "question_id": "ai-q1",
      "type": "mcq",
      "question": "Welche OSI-Schicht ist für Routing zuständig?",
      "options": ["Layer 2", "Layer 3", "Layer 4", "Layer 7"],
      "correct": 1,
      "explanation": "Layer 3 (Network Layer) ist für Routing zuständig."
    }
  ],
  "time_limit": 3600,
  "passing_score": 50
}
```

### 7.3 Abschlussprüfung

| Eigenschaft | Details |
|-------------|---------|
| **Typ** | `final` |
| **Kombination** | Basis-Fragen + KI-Fragen |
| **Zertifikat** | ✅ Bei Bestehen |
| **Wiederholbar** | Ja (mit Wartezeit) |

---

## 8. Kurs-Editor

### 🛠️ Editor-Funktionen nach Rolle

```plantuml
@startuml
title Kurs-Editor - Rollenbasierte Features

actor "Premium User" as premium
actor "Creator" as creator
actor "Lehrer" as teacher
actor "School/Company" as org

package "Editor-Features" {

  rectangle "Basis-Features" #LightGreen {
    [Kurs erstellen]
    [Module hinzufügen]
    [Theorie-Blätter schreiben]
    [Gruppe A+B: Erklaerend & Praxis]
  }

  rectangle "Premium-Features" #LightBlue {
    [Gruppe C: Prüfungsorientierte Methoden (LM18–LM25)]
    [KI-Unterstützung]
    [Community Publishing]
  }

  rectangle "Creator-Features" #LightYellow {
    [Alle 12 Content-Lernmethoden]
    [Marketplace Publishing]
    [Global Publishing (20 Sprachen)]
    [Revenue Analytics]
  }

  rectangle "Org-Features" #LightCoral {
    [Klassen/Teams zuweisen]
    [Vorlagen kopieren]
    [Interne Anpassungen]
    [LiveRoom Pro]
  }
}

premium --> "Basis-Features"
premium --> "Premium-Features"

creator --> "Basis-Features"
creator --> "Premium-Features"
creator --> "Creator-Features"

teacher --> "Basis-Features"
teacher --> "Premium-Features"
teacher --> "Org-Features"

org --> "Basis-Features"
org --> "Premium-Features"
org --> "Org-Features"

@enduml
```

### Editor-Workflow

```plantuml
@startuml
title Kurserstellung - Workflow

start

:Kurs-Metadaten eingeben;

:Kategorie & Sprache wählen;

fork
  :Modul 1 erstellen;
  :Theorie-Blatt schreiben;
  :Lernmethoden hinzufügen;
fork again
  :Modul 2 erstellen;
  :Theorie-Blatt schreiben;
  :Lernmethoden hinzufügen;
fork again
  :Modul N erstellen;
  :Theorie-Blatt schreiben;
  :Lernmethoden hinzufügen;
end fork

:Prüfungen hinzufügen (optional);

if (Global Publishing?) then (ja)
  :KI übersetzt in 20 Sprachen;
else (nein)
  :Nur Primärsprache;
endif

:Vorschau prüfen;

if (Veröffentlichen?) then (ja)
  if (Kursart?) then (Private)
    :Als privat speichern;
  else (Community)
    :Community-Prüfung;
    :Veröffentlichen;
  else (Marketplace)
    :Moderator-Review;
    :Freigabe;
    :Im Marketplace listen;
  endif
else (nein)
  :Als Entwurf speichern;
endif

stop

@enduml
```

---

## 9. Versionierung & Änderungsverfolgung

### 📜 Versions-Management

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x

entity "course_versions" as version {
  primary_key(version_id) : UUID
  --
  foreign_key(course_id) : UUID
  version : INTEGER
  changelog : TEXT
  created_at : TIMESTAMP
  foreign_key(created_by) : UUID
  snapshot_data : JSONB
}

entity "courses" as course {
  primary_key(course_id) : UUID
  --
  current_version : INTEGER
  is_published : BOOLEAN
  draft_state : BOOLEAN
}

version }o--|| course

note right of version
  snapshot_data enthält:
  - Komplette Kursstruktur
  - Module
  - Theorie-Blätter
  - Methoden
end note

@enduml
```

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `version` | INTEGER | Versionnummer (1, 2, 3, ...) |
| `last_edit_at` | TIMESTAMP | Letzter Bearbeitungszeitpunkt |
| `last_edit_by` | UUID | Letzter Bearbeiter |
| `changelog` | TEXT | Änderungsprotokoll |
| `is_published` | BOOLEAN | Veröffentlicht? |
| `draft_state` | BOOLEAN | Entwurfs-Modus? |

### Versionierungs-Regeln

| Regel | Beschreibung |
|-------|--------------|
| ✅ **Auto-Versionierung** | Änderungen an veröffentlichten Kursen erzeugen neue Versionen |
| ✅ **Snapshot** | Jede Version speichert vollständigen Stand |
| ✅ **Rollback** | Frühere Versionen wiederherstellbar |
| ✅ **Organisations-Versionen** | Schulen/Unternehmen können eigene Versionen führen |

---

## 10. Sichtbarkeitsstufen

### 🔐 Visibility-Matrix

```plantuml
@startuml
title Kurssichtbarkeit - Hierarchie

rectangle "private" #LightGray {
  [Nur Ersteller]
}

rectangle "group_private" #LightBlue {
  [Private Gruppe]
  [Eingeladene Mitglieder]
}

rectangle "class_internal" #LightGreen {
  [Klasse/Schülergruppe]
  [Lehrer + Schüler]
}

rectangle "company_internal" #LightYellow {
  [Firmen-intern]
  [Alle Mitarbeiter]
}

rectangle "community_public" #LightCoral {
  [Alle LSX-User]
  [Kostenlos]
}

rectangle "marketplace" #Gold {
  [Öffentlich]
  [Kaufbar]
}

rectangle "academy" #LightPink {
  [LSX Academy]
  [Offiziell]
}

[Nur Ersteller] --> [Private Gruppe]
[Private Gruppe] --> [Klasse/Schülergruppe]
[Private Gruppe] --> [Firmen-intern]
[Klasse/Schülergruppe] --> [Alle LSX-User]
[Firmen-intern] --> [Alle LSX-User]
[Alle LSX-User] --> [Öffentlich]
[Öffentlich] --> [LSX Academy]

note bottom
  Sichtbarkeit steigt von
  oben nach unten
end note

@enduml
```

### Sichtbarkeitsstufen

| Stufe | Zugriff | Ersteller | Zweck |
|-------|---------|-----------|-------|
| `private` | Nur Ersteller | Alle Rollen | Persönliches Lernen |
| `group_private` | Eingeladene Mitglieder | Premium+ | Study Groups |
| `class_internal` | Klasse + Lehrer | Lehrer, School | Unterricht |
| `company_internal` | Alle Mitarbeiter | Company | Firmen-Training |
| `community_public` | Alle LSX-User | Premium, Creator | Community-Beitrag |
| `marketplace` | Kaufbar für alle | Creator | Monetarisierung |
| `academy` | Premium oder Free | Admin | Offizielle LSX-Kurse |

---

## 11. Kursfortschritt & Tracking

### 📊 Progress-Tracking

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x

entity "user_course_progress" as progress {
  primary_key(progress_id) : UUID
  --
  foreign_key(user_id) : UUID
  foreign_key(course_id) : UUID
  enrollment_date : TIMESTAMP
  completion_percentage : INTEGER
  last_activity : TIMESTAMP
  total_learning_time : INTEGER
  status : ENUM
}

entity "module_progress" as mod_prog {
  primary_key(module_progress_id) : UUID
  --
  foreign_key(progress_id) : UUID
  foreign_key(module_id) : UUID
  completion_percentage : INTEGER
  started_at : TIMESTAMP
  completed_at : TIMESTAMP
}

entity "method_progress" as method_prog {
  primary_key(method_progress_id) : UUID
  --
  foreign_key(module_progress_id) : UUID
  foreign_key(method_instance_id) : UUID
  attempts : INTEGER
  scores : JSONB
  completed : BOOLEAN
  last_attempt : TIMESTAMP
}

progress ||--|{ mod_prog
mod_prog ||--|{ method_prog

@enduml
```

### Progress-Datenfelder

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `progress_id` | UUID | Eindeutiger Progress-Identifier |
| `user_id` | UUID | Lernender |
| `course_id` | UUID | Kurs |
| `module_id` | UUID | Aktuelles Modul |
| `method_instance_id` | UUID | Aktuelle Methode |
| `completion_state` | INTEGER | Fortschritt 0-100% |
| `last_activity` | TIMESTAMP | Letzte Aktivität |
| `total_learning_time` | INTEGER | Gesamte Lernzeit (Minuten) |
| `attempts` | INTEGER | Anzahl Versuche |
| `scores` | JSONB | Punkte nach Methode |

### Analytics für Rollen

| Rolle | Analytics |
|-------|-----------|
| **Premium User** | Eigener Fortschritt, Schwachstellen |
| **Creator** | Kurs-Performance, User-Statistiken |
| **Lehrer** | Klassen-Fortschritt, individuelle Schüler |
| **School/Company** | Gesamt-Statistiken, Abteilungen, Teams |
| **Admin** | System-weite Metriken |

---

## 12. Import, Copy & Vorlagen

### 📥 Vorlagen-System

```plantuml
@startuml
title Kurs-Kopier- & Vorlagensystem

actor "School/Company" as org

database "LSX Academy" as academy
database "Creator Marketplace" as market
database "Community" as community

package "Organisation" {
  [Vorlage kopieren]
  [Anpassen]
  [Interne Version]
}

academy --> [Vorlage kopieren] : Lizenziert
market --> [Vorlage kopieren] : Gekauft
community --> [Vorlage kopieren] : Kostenlos

[Vorlage kopieren] --> [Anpassen]
[Anpassen] --> [Interne Version]

[Interne Version] --> org

note right of [Anpassen]
  Anpassungen:
  - Theorie-Blätter
  - Beispiele
  - Prüfungen
  - Reihenfolge
  - Branding
end note

@enduml
```

### Kopierfunktionen

| Rolle | Kopieren | Anpassen | Zweck |
|-------|----------|----------|-------|
| **Free** | ❌ | ❌ | Nur Konsum |
| **Premium** | ❌ | ❌ | Nur Konsum |
| **Creator** | ✅ Eigene | ✅ | Vorlagen für Marketplace |
| **Lehrer** | ✅ Academy, gekaufte | ✅ | Klassenanpassung |
| **School/Company** | ✅ Academy, gekaufte, Community | ✅ | Interne Schulungen |

---

## 13. Global Publishing

### 🌍 Übersetzungspipeline

```plantuml
@startuml
title Global Publishing - Übersetzungsworkflow

actor Creator

box "Kursinhalt" #LightBlue
  participant "Kurs-Metadaten" as meta
  participant "Module" as modules
  participant "Theorie-Blätter" as theory
  participant "Lernmethoden" as methods
  participant "Prüfungen" as exams
end box

box "KI-Translation Engine" #LightYellow
  participant "Language Detector" as detector
  participant "Translator" as translator
  participant "Quality Checker" as checker
end box

database "Translations DB" as translations

Creator -> meta : Markiert für Global Publishing
meta -> detector : Erkennt Primärsprache (z.B. de)

detector -> translator : Übersetzt in 19 weitere Sprachen

translator -> modules : Titel, Beschreibungen
translator -> theory : Vollständiger Inhalt
translator -> methods : Methodendaten
translator -> exams : Fragen & Antworten

translator -> checker : Qualitätsprüfung
checker -> translations : Speichert alle Übersetzungen

translations -> Creator : Vorschau in allen Sprachen

note right of translations
  Gespeichert für:
  - de, en, es, fr, it
  - pl, ru, pt, nl, sv
  - da, fi, no, tr, ar
  - zh, ja, ko, vi, th
  (20 Sprachen total)

  Einmalig übersetzt,
  keine Folgekosten!
end note

@enduml
```

### Global Publishing-Prozess

| Schritt | Aktion |
|---------|--------|
| 1 | Creator markiert Kurs für Global Publishing |
| 2 | System erkennt Primärsprache |
| 3 | KI übersetzt in 19 weitere Sprachen |
| 4 | Übersetzungen werden gespeichert (JSONB) |
| 5 | Kurs in allen Sprachen verfügbar |
| 6 | Keine erneuten KI-Kosten bei Abruf |

### Unterstützte Sprachen

| Region | Sprachen |
|--------|----------|
| **Europa** | Deutsch (de), Englisch (en), Spanisch (es), Französisch (fr), Italienisch (it), Polnisch (pl), Niederländisch (nl), Schwedisch (sv), Dänisch (da), Finnisch (fi), Norwegisch (no), Türkisch (tr) |
| **Asien** | Chinesisch (zh), Japanisch (ja), Koreanisch (ko), Vietnamesisch (vi), Thailändisch (th), Arabisch (ar) |
| **Amerika** | Portugiesisch (pt), Russisch (ru) |

---

## 14. Zusammenfassung

### ✅ Kurs-Architektur-Highlights

| Aspekt | Details |
|--------|---------|
| **Modularität** | Kurse → Module → Theorie-Blätter → Methoden |
| **Flexibilität** | 12 Content-Lernmethoden pro Modul |
| **KI-Integration** | Content-Generierung, Übersetzung, Prüfungen |
| **Rollenbasiert** | Strikte Trennung: Premium/Creator/Teacher/School/Company |
| **International** | Global Publishing in 20 Sprachen |
| **Versionierung** | Vollständiges Versions-Management |
| **Tracking** | Detailliertes Progress-Tracking |
| **Vorlagen** | Kopierfunktionen für Organisationen |

### 🎯 Architektur-Prinzipien

```
┌─────────────────────────────────────────┐
│  📚 Kurs-Architektur                    │
│                                         │
│  Kurs                                   │
│    ├── Metadaten (Titel, Kategorie)    │
│    ├── Module (1-n)                     │
│    │    ├── Theorie-Blatt (1:1)        │
│    │    └── Lernmethoden (12 Content-LMs)   │
│    ├── Prüfungen (optional)            │
│    └── Versionen                        │
│                                         │
│  Eigenschaften:                         │
│  ✅ Modular                             │
│  ✅ Rollenbasiert                       │
│  ✅ KI-fähig                            │
│  ✅ International                       │
│  ✅ Versioniert                         │
└─────────────────────────────────────────┘
```

---

## 15. Datenbank-Schema (Zusammenfassung)

### 🗃️ Haupt-Tabellen

| Tabelle | Beschreibung | Kardinalität |
|---------|--------------|--------------|
| `courses` | Kurs-Metadaten | - |
| `modules` | Lernmodule | n:1 zu courses |
| `theory_sheets` | Theorie-Blätter | 1:1 zu modules |
| `learning_methods` | Methodeninstanzen | n:1 zu modules |
| `exams` | Prüfungen | n:1 zu courses |
| `exam_questions` | Fragen | n:1 zu exams |
| `user_course_progress` | Fortschritt | n:1 zu users & courses |
| `module_progress` | Modul-Fortschritt | n:1 zu user_course_progress |
| `method_progress` | Methoden-Fortschritt | n:1 zu module_progress |
| `course_versions` | Versionen | n:1 zu courses |
| `translations` | Übersetzungen | Poly zu content |

---

## 📌 Dokument abgeschlossen

**Version:** 1.0
**Status:** Final
**Letzte Aktualisierung:** 2024

---

> 💡 **Hinweis:** Diese Kurs-Architektur bildet das Rückgrat des gesamten LSX-Lernsystems und ist optimiert für Skalierbarkeit, KI-Integration und internationale Nutzung.
