# 08 – Schulen & Unternehmen (Final)

**Version:** 1.0
**Stand:** Final

---

## Überblick

Das LSX-System bietet eine vollständige Professional/Enterprise-Lösung für Bildungseinrichtungen und Unternehmen. Diese Ebene ermöglicht die Verwaltung großer Gruppen, professionelle Unterrichtswerkzeuge, kontrollierte Lernpfade, KI-gestützte Prüfungen und LiveRoom-Unterricht mit umfassendem Branding und Analytics.

### 🎯 Zielgruppen

```plantuml
@startuml
title Schulen & Unternehmen - Zielgruppen

package "Educational Institutions" {
  [Schulen (allgemeinbildend)] as schools #LightBlue
  [Berufsschulen] as vocational #LightGreen
  [Universitäten & Hochschulen] as universities #Gold
  [Private Akademien] as academies #LightCoral
}

package "Corporate Organizations" {
  [Ausbildungsbetriebe] as training_companies #LightBlue
  [Unternehmen (Weiterbildung)] as companies #LightGreen
  [Corporate Training Depts] as corporate_training #Gold
  [Beratungsfirmen] as consulting #LightCoral
}

actor "LSX Enterprise" as lsx #Purple

schools --> lsx
vocational --> lsx
universities --> lsx
academies --> lsx

training_companies --> lsx
companies --> lsx
corporate_training --> lsx
consulting --> lsx

note right of lsx
  ✅ Zentrale Verwaltung
  ✅ LiveRoom Pro
  ✅ Domain-Branding
  ✅ Token-Pool
  ✅ DSGVO-konform
end note

@enduml
```

---

## C4 Architektur

### Context Diagram

```plantuml
@startuml
!include <C4/C4_Context>

title Schulen & Unternehmen Context Diagram

Person(admin, "Schul-/Unternehmens-Admin", "Verwaltet Organisation")
Person(teacher, "Lehrer/Ausbilder", "Unterrichtet & erstellt Kurse")
Person(student, "Schüler/Mitarbeiter", "Lernt zugewiesene Kurse")

System(org_system, "Organisation System", "Verwaltung, Kurse, Analytics")

System_Ext(liveroom, "LiveRoom Pro", "Unterricht & Meetings")
System_Ext(ai_pipeline, "KI-Pipeline", "Prüfungen, Content-Generierung")
System_Ext(course_system, "Kurs-System", "Interne & importierte Kurse")
System_Ext(analytics, "Analytics", "Reporting & Insights")
System_Ext(branding, "Branding System", "Domain, Logo, Theme")

Rel(admin, org_system, "Verwaltet Organisation, Nutzer, Kurse")
Rel(teacher, org_system, "Erstellt Kurse, verwaltet Klassen")
Rel(student, org_system, "Lernt zugewiesene Inhalte")

Rel(org_system, liveroom, "Nutzt LiveRoom Pro")
Rel(org_system, ai_pipeline, "KI-Prüfungen, Content")
Rel(org_system, course_system, "Interne Kurse")
Rel(org_system, analytics, "Reporting")
Rel(org_system, branding, "Custom Domain & Theme")

@enduml
```

### Container Diagram

```plantuml
@startuml
!include <C4/C4_Container>

title Organisation System Container Diagram

Person(admin, "Admin", "Organisation verwalten")
Person(teacher, "Lehrer", "Unterrichten")
Person(student, "Schüler", "Lernen")

System_Boundary(org_system, "Organisation System") {
  Container(admin_panel, "Admin-Panel", "Vue.js", "Nutzer & Kursverwaltung")
  Container(teacher_dashboard, "Lehrer-Dashboard", "Vue.js", "Klassen, Kurse, Prüfungen")
  Container(student_portal, "Schüler-Portal", "Vue.js", "Zugewiesene Kurse")
  Container(learning_paths, "Learning Paths", "Python/Flask", "Lernpfad-Management")
  Container(exam_system, "Prüfungs-System", "Python", "Prüfungen erstellen & auswerten")
  Container(analytics_engine, "Analytics-Engine", "Python/Pandas", "Reporting")
  Container(token_pool, "Token-Pool-Manager", "Python", "Zentrale Token-Verwaltung")

  ContainerDb(org_db, "Organisation DB", "PostgreSQL", "Nutzer, Klassen, Kurse, Prüfungen")
}

System_Ext(liveroom_pro, "LiveRoom Pro", "WebRTC")
System_Ext(ai_exam_gen, "KI-Prüfungsgenerator", "AI")
System_Ext(domain_service, "Domain-Service", "DNS/HTTPS")

Rel(admin, admin_panel, "Verwaltet", "HTTPS")
Rel(teacher, teacher_dashboard, "Unterrichtet", "HTTPS")
Rel(student, student_portal, "Lernt", "HTTPS")

Rel(teacher_dashboard, learning_paths, "Erstellt Lernpfade")
Rel(teacher_dashboard, exam_system, "Erstellt Prüfungen")
Rel(exam_system, ai_exam_gen, "Nutzt KI-Generierung")

Rel(admin_panel, org_db, "Verwaltet Daten")
Rel(teacher_dashboard, org_db, "Liest/Schreibt")
Rel(student_portal, org_db, "Liest")
Rel(analytics_engine, org_db, "Analysiert")

Rel(teacher_dashboard, liveroom_pro, "Startet Unterricht")
Rel(admin_panel, domain_service, "Konfiguriert Domain")

@enduml
```

---

## Datenbankschema

### ER-Diagram: Organisationen

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) <color:#efefef><&media-record></color> x
!define table(x) entity x << (T, white) >>

title Schulen & Unternehmen ER-Diagram

table(organizations) {
  primary_key(org_id) : UUID
  column(name) : VARCHAR(255)
  column(type) : ENUM('school', 'company')
  column(logo_url) : TEXT
  column(domain) : VARCHAR(255)
  column(theme_config) : JSONB
  column(token_pool_balance) : INTEGER
  column(monthly_token_grant) : INTEGER
  column(active_users_count) : INTEGER
  column(billing_email) : VARCHAR(255)
  column(dsgvo_school_mode) : BOOLEAN
  column(corporate_security_mode) : BOOLEAN
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
}

table(org_members) {
  primary_key(member_id) : UUID
  foreign_key(org_id) : UUID
  foreign_key(user_id) : UUID
  column(role) : ENUM('admin', 'teacher', 'student')
  column(display_name) : VARCHAR(255)
  column(status) : ENUM('active', 'inactive', 'suspended')
  column(joined_at) : TIMESTAMP
}

table(classes_teams) {
  primary_key(class_id) : UUID
  foreign_key(org_id) : UUID
  foreign_key(teacher_id) : UUID
  column(name) : VARCHAR(255)
  column(description) : TEXT
  column(type) : ENUM('class', 'team')
  column(member_count) : INTEGER
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
}

table(class_members) {
  primary_key(enrollment_id) : UUID
  foreign_key(class_id) : UUID
  foreign_key(student_id) : UUID
  column(enrolled_at) : TIMESTAMP
  column(status) : ENUM('active', 'completed', 'dropped')
}

table(org_courses) {
  primary_key(org_course_id) : UUID
  foreign_key(org_id) : UUID
  foreign_key(course_id) : UUID
  foreign_key(created_by) : UUID
  column(title) : VARCHAR(255)
  column(visibility) : ENUM('internal', 'class_specific')
  column(is_mandatory) : BOOLEAN
  column(created_at) : TIMESTAMP
}

table(learning_paths) {
  primary_key(path_id) : UUID
  foreign_key(org_id) : UUID
  foreign_key(created_by) : UUID
  column(name) : VARCHAR(255)
  column(description) : TEXT
  column(sequence) : JSONB
  column(estimated_duration_hours) : INTEGER
  column(created_at) : TIMESTAMP
}

table(path_assignments) {
  primary_key(assignment_id) : UUID
  foreign_key(path_id) : UUID
  foreign_key(student_id) : UUID
  foreign_key(class_id) : UUID
  column(deadline) : TIMESTAMP
  column(progress) : FLOAT
  column(status) : ENUM('not_started', 'in_progress', 'completed')
  column(assigned_at) : TIMESTAMP
}

table(org_exams) {
  primary_key(exam_id) : UUID
  foreign_key(org_id) : UUID
  foreign_key(created_by) : UUID
  foreign_key(course_id) : UUID
  column(title) : VARCHAR(255)
  column(duration_minutes) : INTEGER
  column(passing_score) : FLOAT
  column(questions) : JSONB
  column(created_at) : TIMESTAMP
}

table(exam_attempts) {
  primary_key(attempt_id) : UUID
  foreign_key(exam_id) : UUID
  foreign_key(student_id) : UUID
  column(score) : FLOAT
  column(passed) : BOOLEAN
  column(answers) : JSONB
  column(started_at) : TIMESTAMP
  column(submitted_at) : TIMESTAMP
}

table(org_token_transactions) {
  primary_key(transaction_id) : UUID
  foreign_key(org_id) : UUID
  foreign_key(user_id) : UUID
  column(amount) : INTEGER
  column(type) : ENUM('grant', 'consumption', 'refund')
  column(description) : TEXT
  column(balance_after) : INTEGER
  column(created_at) : TIMESTAMP
}

' Relationships
organizations ||--o{ org_members : "has"
organizations ||--o{ classes_teams : "has"
organizations ||--o{ org_courses : "owns"
organizations ||--o{ learning_paths : "defines"
organizations ||--o{ org_exams : "creates"
organizations ||--o{ org_token_transactions : "tracks"

org_members ||--o{ classes_teams : "teaches (if teacher)"
classes_teams ||--o{ class_members : "has"
org_members ||--o{ class_members : "enrolled as (if student)"

learning_paths ||--o{ path_assignments : "assigned to"
org_members ||--o{ path_assignments : "assigned to student"

org_exams ||--o{ exam_attempts : "taken by"
org_members ||--o{ exam_attempts : "takes (if student)"

@enduml
```

---

## 1. Ziel des Schul- & Unternehmensmodells

### Anforderungen

```plantuml
@startuml
title Organisationsanforderungen

package "Kernfunktionen" {
  [Nutzerverwaltung] as users #LightBlue
  [Kursverwaltung] as courses #LightGreen
  [Prüfungssystem] as exams #Gold
  [LiveRoom Pro] as liveroom #LightCoral
  [Analytics] as analytics #Purple
  [Branding] as branding #Orange
}

actor "Organisation" as org

org --> users : Verwaltet 100+ Nutzer
org --> courses : Interne & importierte Kurse
org --> exams : KI-gestützte Prüfungen
org --> liveroom : Professioneller Unterricht
org --> analytics : Detailliertes Reporting
org --> branding : Custom Domain & Theme

note right of users
  ✅ Lehrer hinzufügen
  ✅ Schüler hinzufügen
  ✅ Klassen/Teams erstellen
  ✅ Rollen verwalten
end note

note right of exams
  ✅ IHK-Prüfungen
  ✅ CompTIA-Tests
  ✅ Custom Exams
  ✅ Auto-Bewertung
end note

@enduml
```

---

## 2. Rollen innerhalb von Organisationen

### Rollen-Hierarchie

```plantuml
@startuml
title Organisations-Rollen-Hierarchie

class "Organisation" as org {
  +org_id : UUID
  +name : String
  +type : Enum
  +domain : String
}

class "Admin" as admin {
  +Alle Rechte
  +Nutzer verwalten
  +Billing verwalten
  +Domain konfigurieren
}

class "Lehrer/Ausbilder" as teacher {
  +Kurse erstellen
  +Klassen verwalten
  +Prüfungen erstellen
  +LiveRoom starten
  +Analytics sehen (eigene Klassen)
}

class "Schüler/Mitarbeiter" as student {
  +Zugewiesene Kurse lernen
  +Prüfungen ablegen
  +LiveRoom beitreten
  +Eigenen Fortschritt sehen
}

org "1" --> "*" admin
org "1" --> "*" teacher
org "1" --> "*" student

teacher "1" --> "*" student : verwaltet

@enduml
```

### Berechtigungsmatrix

| Funktion | Admin | Lehrer | Schüler |
|----------|-------|--------|---------|
| **Nutzer hinzufügen** | ✅ | ❌ | ❌ |
| **Nutzer löschen** | ✅ | ❌ | ❌ |
| **Klassen erstellen** | ✅ | ✅ (eigene) | ❌ |
| **Kurse erstellen** | ✅ | ✅ | ❌ |
| **Prüfungen erstellen** | ✅ | ✅ | ❌ |
| **LiveRoom starten** | ✅ | ✅ | ❌ |
| **LiveRoom beitreten** | ✅ | ✅ | ✅ (eingeladen) |
| **Analytics (alle)** | ✅ | ❌ | ❌ |
| **Analytics (eigene Klassen)** | ✅ | ✅ | ❌ |
| **Analytics (eigener Fortschritt)** | ✅ | ✅ | ✅ |
| **Domain konfigurieren** | ✅ | ❌ | ❌ |
| **Billing** | ✅ | ❌ | ❌ |
| **Token-Pool verwalten** | ✅ | ❌ | ❌ |

---

## 3. Organisations-Struktur

### Organisations-Aufbau

```plantuml
@startuml
!include <C4/C4_Component>

title Organisations-Struktur

package "Organisation" {
  component "Admin-Ebene" as admin {
    [Org-Admins] as admins
    [Billing] as billing
    [Token-Pool] as tokens
  }

  component "Lehr-Ebene" as teaching {
    [Lehrer] as teachers
    [Klassen/Teams] as classes
    [Kurse] as courses
  }

  component "Lern-Ebene" as learning {
    [Schüler/Mitarbeiter] as students
    [Zugewiesene Kurse] as assigned
    [Prüfungen] as exams
  }

  component "Infrastruktur" as infra {
    [Domain] as domain
    [Branding] as branding
    [Analytics] as analytics
  }
}

admins --> teachers : verwaltet
teachers --> classes : erstellt
classes --> students : enthält
courses --> assigned : zugewiesen an
assigned --> exams : enthält

admins --> tokens : verwaltet
admins --> domain : konfiguriert
admins --> analytics : sieht alle

@enduml
```

---

## 4. Domain-Branding

### Branding-Workflow

```plantuml
@startuml
title Domain-Branding Setup

actor Admin
participant "Admin-Panel" as panel
participant "Domain-Service" as domain_svc
participant "DNS Provider" as dns
participant "SSL Service" as ssl
database "Org Config" as config

Admin -> panel : Konfiguriert Custom Domain\n"lernportal.meineschule.de"
activate panel

panel -> config : Speichert Domain-Config
activate config
config --> panel : OK
deactivate config

panel --> Admin : Zeigt DNS-Einträge:\nCNAME lernportal -> lsx.com\nTXT _verification=abc123
deactivate panel

Admin -> dns : Konfiguriert DNS-Einträge
activate dns
dns --> Admin : DNS propagiert
deactivate dns

dns -> domain_svc : DNS-Lookup erfolgt
activate domain_svc

domain_svc -> domain_svc : Verifiziert Domain-Ownership

domain_svc -> ssl : Erstellt SSL-Zertifikat
activate ssl
ssl --> domain_svc : Cert issued
deactivate ssl

domain_svc -> config : Aktiviert Domain
activate config
config --> domain_svc : OK
deactivate config

domain_svc --> Admin : Domain aktiv!\n"https://lernportal.meineschule.de"
deactivate domain_svc

@enduml
```

### Branding-Optionen

| Element | Anpassbar | Format | Beispiel |
|---------|-----------|--------|----------|
| **Domain** | ✅ | FQDN | lernportal.meineschule.de |
| **Logo** | ✅ | PNG, SVG (max 2MB) | logo.svg |
| **Farbschema** | ✅ | Hex Colors | Primary: #1E40AF |
| **Hintergrundbild** | ✅ | JPG, PNG (max 5MB) | background.jpg |
| **Favicon** | ✅ | ICO, PNG | favicon.ico |
| **Theme** | ✅ | Light/Dark/Custom | Custom |
| **Font** | ✅ | Google Fonts | Inter, Roboto |

**Theme-Konfiguration (JSON):**

```json
{
  "branding": {
    "domain": "lernportal.meineschule.de",
    "logo_url": "https://cdn.lsx.com/orgs/org_123/logo.svg",
    "colors": {
      "primary": "#1E40AF",
      "secondary": "#10B981",
      "accent": "#F59E0B",
      "background": "#F3F4F6",
      "text": "#111827"
    },
    "fonts": {
      "heading": "Inter",
      "body": "Roboto"
    },
    "theme_mode": "custom"
  }
}
```

---

## 5. Kursverwaltung

### Kurs-Typen

```plantuml
@startuml
title Kurs-Typen für Organisationen

package "Verfügbare Kursquellen" {
  [Interne Kurse] as internal #LightBlue
  [Creator-Kurse (gekauft)] as creator #Gold
  [Community-Kurse (importiert)] as community #LightGreen
  [LSX Academy] as academy #Purple
}

actor "Organisation" as org

org --> internal : Erstellt eigene Kurse
org --> creator : Kauft & kopiert
org --> community : Importiert & anpasst
org --> academy : Abonniert

note right of internal
  ✅ Volle Kontrolle
  ✅ Alle 12 Content-LMs (A-C)
  ✅ KI-Unterstützung
  ✅ Versionierung
end note

note right of creator
  ✅ Einmalige Zahlung
  ✅ Unbegrenzte Nutzung
  ✅ Anpassbar für interne Zwecke
  ❌ Nicht weiterverkaufbar
end note

@enduml
```

### Kurs-Erstellungs-Workflow

```plantuml
@startuml
title Kurs-Erstellung durch Lehrer

actor Lehrer
participant "Course Editor" as editor
participant "AI Generator" as ai
participant "Token Manager" as tokens
database "Org Courses" as courses
participant "Class Manager" as classes

Lehrer -> editor : Erstellt neuen Kurs
activate editor

editor --> Lehrer : Kurseditor öffnet

Lehrer -> editor : Nutzt KI-Modul-Generierung
editor -> tokens : Prüfe Org Token-Pool
activate tokens
tokens --> editor : Pool: 45.000 Tokens verfügbar
deactivate tokens

editor -> ai : Generiere 10 Module (20.000 Tokens)
activate ai
ai --> editor : Module generiert
deactivate ai

editor -> tokens : Dedukt 20.000 Tokens
activate tokens
tokens --> editor : Neuer Pool: 25.000 Tokens
deactivate tokens

Lehrer -> editor : Finalisiert Kurs

editor -> courses : Speichert Kurs (internal)
activate courses
courses --> editor : org_course_id
deactivate courses

Lehrer -> classes : Weist Kurs Klasse zu
activate classes
classes -> courses : Verknüpft Kurs mit Klasse
courses --> classes : OK
classes --> Lehrer : Kurs zugewiesen
deactivate classes

deactivate editor

@enduml
```

---

## 6. LiveRoom Pro

### LiveRoom-Architektur

```plantuml
@startuml
!include <C4/C4_Container>

title LiveRoom Pro Architecture

Person(teacher, "Lehrer", "Unterrichtet")
Person(student, "Schüler", "Teilnehmer")

System_Boundary(liveroom_pro, "LiveRoom Pro") {
  Container(video_conf, "Video-Konferenz", "WebRTC", "Real-time Video/Audio")
  Container(whiteboard, "Interactive Whiteboard", "Canvas + AI", "Kollaboratives Zeichnen")
  Container(screen_share, "Screen Sharing", "WebRTC", "Desktop-Übertragung")
  Container(chat, "Chat", "WebSocket", "Text & Datei-Upload")
  Container(breakout, "Breakout Rooms", "WebRTC", "Gruppenräume")
  Container(recording, "Recording Service", "FFmpeg", "Aufzeichnung")
  Container(ai_assistant, "AI-Assistent", "Python/AI", "Whiteboard-Analyse, Transkription")

  ContainerDb(session_db, "Session DB", "Redis", "Aktive Sessions")
}

System_Ext(storage, "Cloud Storage", "S3")

Rel(teacher, video_conf, "Startet Unterricht")
Rel(student, video_conf, "Tritt bei")

Rel(teacher, whiteboard, "Zeichnet, Erklärt")
Rel(student, whiteboard, "Zeichnet mit (Permission)")

Rel(teacher, screen_share, "Teilt Bildschirm")
Rel(teacher, breakout, "Erstellt Gruppenräume")
Rel(teacher, recording, "Startet Aufzeichnung")

Rel(recording, storage, "Speichert Video")
Rel(ai_assistant, whiteboard, "Analysiert Zeichnungen")

@enduml
```

### Feature-Vergleich

| Feature | Free | Premium | Lehrer | Schule/Unternehmen |
|---------|------|---------|--------|---------------------|
| **Max. Teilnehmer** | ❌ | 4 | 20 | Unbegrenzt |
| **Whiteboard** | ❌ | Basic | Pro | Pro + AI |
| **Bildschirmfreigabe** | ❌ | ✅ | ✅ | ✅ |
| **Chat** | ❌ | ✅ | ✅ | ✅ |
| **Datei-Upload** | ❌ | ✅ (10MB) | ✅ (50MB) | ✅ (100MB) |
| **Breakout Rooms** | ❌ | ❌ | ✅ | ✅ |
| **Aufzeichnung** | ❌ | ❌ | ✅ | ✅ |
| **Transkription** | ❌ | ❌ | ❌ | ✅ (AI) |
| **Whiteboard-AI** | ❌ | ❌ | ❌ | ✅ |
| **Dauer (max)** | - | 2h | 4h | Unbegrenzt |

---

## 7. Prüfungswesen

### Prüfungs-Workflow

```plantuml
@startuml
title Prüfungs-Erstellung und Durchführung

actor Lehrer
participant "Exam Creator" as creator
participant "AI Exam Generator" as ai_gen
participant "Exam System" as exam_sys
database "Exam DB" as db
participant "Student Portal" as student

Lehrer -> creator : Erstellt neue Prüfung
activate creator

creator --> Lehrer : Optionen:\n1. Manuell erstellen\n2. KI-Generierung

Lehrer -> creator : Wählt "KI-Generierung (IHK FIAE)"
creator -> ai_gen : POST /api/ai/generate-exam
activate ai_gen

ai_gen -> ai_gen : Analysiert:\n- Kursinhalt\n- Theorieblätter\n- IHK-Standards\n- Schwierigkeitsgrad

ai_gen --> creator : Prüfung mit 40 Fragen generiert\n(Multiple-Choice, Fallstudien, Code)
deactivate ai_gen

Lehrer -> creator : Reviewt Fragen, passt an
Lehrer -> creator : Setzt Parameter:\n- Dauer: 90 Min\n- Passing Score: 70%\n- Wiederholungen: 2

creator -> db : Speichert Prüfung
activate db
db --> creator : exam_id
deactivate db

creator --> Lehrer : Prüfung erstellt
deactivate creator

Lehrer -> exam_sys : Weist Prüfung Klasse zu
activate exam_sys

exam_sys -> student : Benachrichtigung: "Neue Prüfung verfügbar"
deactivate exam_sys

== Prüfung ablegen ==

student -> exam_sys : Startet Prüfung
activate exam_sys

exam_sys -> db : INSERT INTO exam_attempts
activate db
db --> exam_sys : attempt_id, started_at
deactivate db

exam_sys --> student : Prüfung läuft (90 Min)

student -> exam_sys : Beantwortet Fragen
student -> exam_sys : Reicht Prüfung ein (nach 75 Min)

exam_sys -> exam_sys : Bewertet automatisch\n(MC: sofort, Code: AI-Bewertung)

exam_sys -> db : UPDATE exam_attempts\nSET score=85%, passed=TRUE
activate db
db --> exam_sys : OK
deactivate db

exam_sys --> student : Ergebnis: 85% - Bestanden ✅
deactivate exam_sys

exam_sys -> Lehrer : Benachrichtigung: Schüler hat bestanden

@enduml
```

### KI-Prüfungsgenerator

**Unterstützte Prüfungstypen:**

| Typ | Beschreibung | KI-Unterstützung | Beispiele |
|-----|--------------|------------------|-----------|
| **IHK-Prüfungen** | Offizielle IHK-Standards | ✅ Vollständig | FIAE, FISI, Kaufmann |
| **CompTIA** | IT-Zertifizierungen | ✅ Vollständig | A+, Network+, Security+ |
| **Custom** | Eigene Prüfungen | ✅ Basis | Firmen-spezifisch |
| **Quiz** | Kurze Tests | ✅ Vollständig | Wissensabfragen |

---

## 8. Lernpfade (Learning Paths)

### Lernpfad-Struktur

```plantuml
@startuml
title Lernpfad-Struktur

state "Lernpfad: FISI 1. Lehrjahr" as path {
  state "1. Grundlagen IT" as module1
  state "2. Netzwerk Basics" as module2
  state "3. Netzwerk Advanced" as module3
  state "4. Subnetting" as module4
  state "5. Prüfungssimulation" as exam

  [*] --> module1
  module1 --> module2 : Abgeschlossen
  module2 --> module3 : Abgeschlossen
  module3 --> module4 : Abgeschlossen
  module4 --> exam : Abgeschlossen
  exam --> [*] : Bestanden
}

note right of module1
  ✅ Pflicht
  ⏱️ Deadline: 30.09.2024
  📊 Fortschritt: 100%
end note

note right of exam
  ✅ Pflicht
  ⏱️ Deadline: 15.10.2024
  📊 Passing Score: 70%
  🔄 Max. Versuche: 3
end note

@enduml
```

### Lernpfad-Features

```plantuml
@startuml
!include <C4/C4_Component>

title Learning Path System

Container_Boundary(lp_system, "Learning Path System") {
  Component(path_creator, "Path Creator", "Vue.js", "Lernpfade definieren")
  Component(path_engine, "Path Engine", "Python", "Fortschritt tracken")
  Component(deadline_mgr, "Deadline Manager", "Python/Celery", "Erinnerungen senden")
  Component(ai_optimizer, "AI-Optimizer", "Python/AI", "Adaptive Pfad-Anpassung")
}

Database(paths_db, "Paths DB", "PostgreSQL")
System_Ext(notification, "Notification Service", "Email/Push")

Rel(path_creator, paths_db, "Erstellt Pfade")
Rel(path_engine, paths_db, "Trackt Fortschritt")
Rel(deadline_mgr, notification, "Sendet Erinnerungen")
Rel(ai_optimizer, path_engine, "Passt Pfad an")

@enduml
```

**Lernpfad-Beispiel (JSON):**

```json
{
  "path_id": "path_fisi_year1",
  "name": "FISI 1. Lehrjahr",
  "description": "Kompletter Lernpfad für das erste Ausbildungsjahr",
  "estimated_duration_hours": 180,
  "sequence": [
    {
      "step": 1,
      "course_id": "course_grundlagen_it",
      "mandatory": true,
      "deadline": "2024-09-30",
      "estimated_hours": 40
    },
    {
      "step": 2,
      "course_id": "course_netzwerk_basics",
      "mandatory": true,
      "deadline": "2024-10-15",
      "estimated_hours": 30
    },
    {
      "step": 3,
      "course_id": "course_netzwerk_advanced",
      "mandatory": true,
      "deadline": "2024-11-01",
      "estimated_hours": 40
    },
    {
      "step": 4,
      "course_id": "course_subnetting",
      "mandatory": true,
      "deadline": "2024-11-20",
      "estimated_hours": 30
    },
    {
      "step": 5,
      "exam_id": "exam_ap1_sim",
      "mandatory": true,
      "deadline": "2024-12-15",
      "passing_score": 70,
      "max_attempts": 3
    }
  ]
}
```

---

## 9. Schüler-/Mitarbeiterverwaltung

### Verwaltungs-Workflow

```plantuml
@startuml
title Nutzer-Verwaltungs-Workflow

actor Admin
participant "Admin-Panel" as panel
database "Org Members" as members
participant "Email Service" as email
participant "Student Portal" as student_portal

Admin -> panel : Fügt neuen Schüler hinzu
activate panel

panel --> Admin : Formular:\n- Name: Max Mustermann\n- Email: max@schule.de\n- Klasse: 10A\n- Rolle: Student

Admin -> panel : Speichert

panel -> members : INSERT INTO org_members
activate members
members --> panel : member_id
deactivate members

panel -> email : Sendet Willkommens-Email mit Login-Daten
activate email
email --> panel : Sent
deactivate email

panel --> Admin : Schüler hinzugefügt
deactivate panel

== Schüler loggt ein ==

student "Max" -> student_portal : Login mit Credentials
activate student_portal

student_portal -> members : Authentifizierung
activate members
members --> student_portal : OK, Rolle: Student
deactivate members

student_portal --> student : Zugewiesene Kurse:\n- Mathematik Kl. 10\n- Physik Kl. 10\n- Englisch Kl. 10
deactivate student_portal

@enduml
```

### Verwaltungs-Aktionen

| Aktion | Beschreibung | Durchführbar von | API-Endpoint |
|--------|--------------|------------------|--------------|
| **Hinzufügen** | Neuen User anlegen | Admin | POST /api/orgs/:id/members |
| **Entfernen** | User deaktivieren | Admin | DELETE /api/orgs/:id/members/:member_id |
| **Bearbeiten** | Details anpassen | Admin, Lehrer (begrenzt) | PUT /api/orgs/:id/members/:member_id |
| **Klasse zuweisen** | User zu Klasse hinzufügen | Admin, Lehrer | POST /api/orgs/:id/classes/:class_id/members |
| **Fortschritt sehen** | Lernfortschritt tracken | Admin, Lehrer, Self | GET /api/orgs/:id/analytics/member/:member_id |
| **Prüfungen einsehen** | Prüfungsergebnisse | Admin, Lehrer, Self | GET /api/orgs/:id/exams/results/:member_id |
| **Lernzeit** | Zeiterfassung | Admin, Lehrer | GET /api/orgs/:id/analytics/time/:member_id |

### DSGVO-Schulmodus

```plantuml
@startuml
title DSGVO-Schulmodus

state "DSGVO-Schulmodus" as dsgvo {
  state "Datenschutz-Settings" as settings
  state "Reduzierte Datenerfassung" as reduced
  state "Eltern-Benachrichtigung" as parents
  state "Kein externes Tracking" as no_tracking
  state "Zeitliche Beschränkung" as time_limit

  [*] --> settings
  settings --> reduced : Aktiviert
  reduced --> parents : Benachrichtigt
  parents --> no_tracking : Konfiguriert
  no_tracking --> time_limit : Setzt
  time_limit --> [*]
}

note right of reduced
  ✅ Keine Tracking-Cookies
  ✅ Minimale Datenspeicherung
  ✅ Pseudonymisierung
  ✅ Recht auf Löschung
end note

note right of time_limit
  ✅ Nur Unterrichtszeiten
  ✅ Kein Zugriff außerhalb Schule (optional)
  ✅ Elternkontrolle
end note

@enduml
```

**DSGVO-Features:**

- ✅ Minimale Datenerfassung (nur notwendige Daten)
- ✅ Pseudonymisierung von Schülerdaten
- ✅ Kein externes Tracking (Google Analytics, etc.)
- ✅ Zugriffsbeschränkung auf Unterrichtszeiten
- ✅ Eltern-Dashboard (optional)
- ✅ Recht auf Löschung (automatisch nach Abschluss)
- ✅ Einwilligungsverwaltung

---

## 10. Analytics & Reporting

### Analytics-Dashboard

```plantuml
@startuml
!include <C4/C4_Component>

title Organisation Analytics Dashboard

Container_Boundary(analytics, "Analytics System") {
  Component(overview, "Übersichts-Dashboard", "Vue.js + Chart.js", "Org-wide Metriken")
  Component(class_analytics, "Klassen-Analytics", "Vue.js", "Pro-Klasse Insights")
  Component(student_progress, "Schüler-Fortschritt", "Python/Pandas", "Individuelles Tracking")
  Component(exam_analysis, "Prüfungs-Analyse", "Python", "Fehler-Cluster, Schwachstellen")
  Component(ai_insights, "AI-Insights", "Python/AI", "Verbesserungsvorschläge")
  Component(export_engine, "Export-Engine", "Python", "CSV, PDF, API")
}

Database(analytics_db, "Analytics DB", "PostgreSQL")
System_Ext(reporting_service, "Reporting Service", "Metabase")

Rel(overview, analytics_db, "Liest Metriken")
Rel(class_analytics, analytics_db, "Liest Klassen-Daten")
Rel(student_progress, analytics_db, "Trackt Fortschritt")
Rel(exam_analysis, analytics_db, "Analysiert Prüfungen")
Rel(ai_insights, exam_analysis, "Generiert Insights")

Rel(export_engine, reporting_service, "Exportiert Berichte")

@enduml
```

### Key Metriken

| Kategorie | Metrik | Beschreibung | Visualisierung |
|-----------|--------|--------------|----------------|
| **Übersicht** | Aktive Nutzer | Anzahl aktiver Schüler/Mitarbeiter | Number + Trend |
| **Übersicht** | Kurs-Completion-Rate | Abschlussquote aller Kurse | Percentage + Bar Chart |
| **Übersicht** | Durchschnittliche Lernzeit | Zeit pro User pro Woche | Number + Line Chart |
| **Klassen** | Fortschritt pro Klasse | Durchschnittlicher Fortschritt | Progress Bars |
| **Klassen** | Engagement-Rate | Aktivität der Klasse | Heatmap |
| **Schüler** | Individueller Fortschritt | Kurs-Completion pro Schüler | Timeline |
| **Schüler** | Lernzeit | Wöchentliche/Monatliche Zeit | Bar Chart |
| **Prüfungen** | Durchfallquote | Prozent nicht bestanden | Percentage |
| **Prüfungen** | Fehler-Cluster | Häufigste falsche Antworten | Word Cloud |
| **Prüfungen** | Durchschnittsscore | Avg. Prüfungsergebnis | Number + Distribution |

**Beispiel-Export (CSV):**

```csv
Schüler,Klasse,Kurs,Fortschritt,Lernzeit (h),Prüfungsergebnis
Max Mustermann,10A,Mathematik,85%,12.5,88%
Anna Schmidt,10A,Mathematik,92%,15.2,95%
Tom Müller,10A,Mathematik,45%,6.1,62% (nicht bestanden)
```

---

## 11. KI für Organisationen

### Token-Pool-System

```plantuml
@startuml
title Organisation Token-Pool

database "Org Token Pool" as pool {
  Balance: 50.000 Tokens
  Monthly Grant: 50.000
  Last Grant: 01.02.2024
}

participant "Lehrer 1" as t1
participant "Lehrer 2" as t2
participant "Lehrer 3" as t3
participant "Token Manager" as mgr

t1 -> mgr : Nutzt KI-Prüfungsgenerator (8.000 Tokens)
activate mgr
mgr -> pool : Deduct 8.000
pool --> mgr : New Balance: 42.000
mgr --> t1 : Prüfung generiert
deactivate mgr

t2 -> mgr : Nutzt KI-Modul-Generierung (5.000 Tokens)
activate mgr
mgr -> pool : Deduct 5.000
pool --> mgr : New Balance: 37.000
mgr --> t2 : Module generiert
deactivate mgr

t3 -> mgr : Nutzt Whiteboard-AI (2.000 Tokens)
activate mgr
mgr -> pool : Deduct 2.000
pool --> mgr : New Balance: 35.000
mgr --> t3 : Analyse fertig
deactivate mgr

note right of pool
  ✅ Zentrale Verwaltung
  ✅ Faire Verteilung
  ✅ Transparente Abrechnung
  ⚠️ Bei < 10% → Admin-Warnung
end note

@enduml
```

### KI-Features für Organisationen

| KI-Feature | Token-Kosten | Nutzer | Zweck |
|------------|--------------|--------|-------|
| **Foliensatz-Analyse** | 1.000-3.000 | Lehrer | PDF-Import, Content-Extraktion |
| **Theorie-Generierung** | 1.500-4.000 | Lehrer | Automatische Theorieblätter |
| **Quiz-Erstellung** | 500-2.000 | Lehrer | Fragenpool aufbauen |
| **Prüfungs-Generierung** | 5.000-12.000 | Lehrer | Vollständige IHK/CompTIA-Tests |
| **Lernpfad-Optimierung** | 2.000-5.000 | Admin | Adaptive Anpassung |
| **Fehleranalyse** | 1.000-3.000 | Lehrer | Schülerdaten auswerten |
| **Whiteboard-Analyse** | 500-1.500 | Lehrer | Handschrifterkennung |
| **Zusammenfassungen** | 300-800 | Schüler (mit Permission) | Content-Kondensierung |

---

## 12. Preismodell

### Pricing-Struktur

```plantuml
@startuml
title Organisation Pricing

package "Standard Tier" {
  [14,99 € / User / Monat] as standard #LightBlue
}

package "Enterprise Tier" {
  [9,99 € / User / Monat] as enterprise #LightGreen
}

package "Custom Tier" {
  [Verhandelbar] as custom #Gold
}

actor "Kleine Schule (< 100 User)" as small
actor "Mittelgroße Org (100-299 User)" as medium
actor "Große Org (300+ User)" as large

small --> standard
medium --> enterprise
large --> custom

note right of standard
  ✅ Bis 99 Nutzer
  ✅ 50.000 Tokens/Monat (Org-Pool)
  ✅ LiveRoom Pro
  ✅ Domain-Branding
  ✅ Standard-Support
end note

note right of enterprise
  ✅ 100-299 Nutzer
  ✅ 100.000 Tokens/Monat
  ✅ Alle Standard-Features
  ✅ Priority Support
end note

note right of custom
  ✅ 300+ Nutzer
  ✅ Custom Token-Pool
  ✅ SLA
  ✅ Dedicated Support
  ✅ Custom Integration
end note

@enduml
```

**Preis-Beispiele:**

| Organisation | Nutzer | Tier | Preis/Monat | Tokens/Monat |
|--------------|--------|------|-------------|--------------|
| Kleine Schule | 50 | Standard | 50 × 14,99 € = 749,50 € | 50.000 |
| Mittelgroße Firma | 150 | Enterprise | 150 × 9,99 € = 1.498,50 € | 100.000 |
| Große Universität | 500 | Custom | ~4.000 € (negotiated) | 250.000 |

**Zusatzkosten:**

- 🤖 **Zusätzliche Tokens:** 10.000 Tokens = 25 € (on-demand)
- 🎬 **Recording-Speicher:** 100 GB = 10 € / Monat (über Inklusiv hinaus)
- 📊 **Premium-Analytics:** 50 € / Monat (erweiterte Dashboards)

---

## 13. Unterschiede Schule vs. Unternehmen

### Feature-Mapping

```plantuml
@startuml
title Schule vs. Unternehmen Feature-Mapping

package "Schule" {
  [Klassen] as classes_school #LightBlue
  [Schüler] as students #LightBlue
  [Lehrer] as teachers #LightBlue
  [DSGVO-Schulmodus] as dsgvo_school #LightBlue
  [Lehrplan-Integration] as curriculum #LightBlue
}

package "Unternehmen" {
  [Teams] as teams_company #LightGreen
  [Mitarbeiter] as employees #LightGreen
  [Teamleiter/Ausbilder] as trainers #LightGreen
  [Corporate Security] as corp_sec #LightGreen
  [Skills-Gap-Analyse] as skills #LightGreen
}

package "Gemeinsame Features" {
  [LiveRoom Pro] as liveroom #Gold
  [KI-Prüfungen] as ai_exams #Gold
  [Analytics] as analytics #Gold
  [Domain-Branding] as branding #Gold
  [Token-Pool] as tokens #Gold
}

classes_school -[hidden]-> teams_company
students -[hidden]-> employees
teachers -[hidden]-> trainers

classes_school --> liveroom
teams_company --> liveroom

students --> analytics
employees --> analytics

teachers --> ai_exams
trainers --> ai_exams

@enduml
```

### Vergleichstabelle

| Aspekt | Schule | Unternehmen |
|--------|--------|-------------|
| **Primäres Ziel** | Bildung & Ausbildung | Weiterbildung & Compliance |
| **Gruppierung** | Klassen | Teams |
| **Teilnehmer** | Schüler | Mitarbeiter |
| **Lehrende** | Lehrer | Ausbilder, Teamleiter |
| **Datenschutz** | DSGVO-Schulmodus (Minderjährige) | Corporate Security (Firmengeheimnisse) |
| **Prüfungen** | IHK, Schulprüfungen | CompTIA, Firmenzertifikate |
| **Zeitplan** | Schuljahr, Stundenplan | Flexibel, On-Demand |
| **Eltern-Integration** | Ja (optional) | Nein |
| **Reporting** | Schulleitung, Eltern | Management, HR |
| **Compliance** | Lehrplan-konform | ISO, Branchen-spezifisch |

---

## 14. API-Endpoints

### Organisation-API

| Endpoint | Methode | Beschreibung | Auth | Rolle |
|----------|---------|--------------|------|-------|
| `/api/orgs/:id` | GET | Organisation abrufen | ✅ | Admin |
| `/api/orgs/:id` | PUT | Organisation aktualisieren | ✅ | Admin |
| `/api/orgs/:id/members` | GET | Alle Mitglieder | ✅ | Admin, Lehrer |
| `/api/orgs/:id/members` | POST | Neues Mitglied hinzufügen | ✅ | Admin |
| `/api/orgs/:id/members/:member_id` | DELETE | Mitglied entfernen | ✅ | Admin |
| `/api/orgs/:id/classes` | GET | Alle Klassen/Teams | ✅ | Admin, Lehrer |
| `/api/orgs/:id/classes` | POST | Neue Klasse erstellen | ✅ | Admin, Lehrer |
| `/api/orgs/:id/classes/:class_id/members` | POST | Mitglied zu Klasse hinzufügen | ✅ | Admin, Lehrer |
| `/api/orgs/:id/courses` | GET | Org-Kurse | ✅ | Admin, Lehrer |
| `/api/orgs/:id/courses` | POST | Neuer Kurs | ✅ | Admin, Lehrer |
| `/api/orgs/:id/exams` | POST | Prüfung erstellen | ✅ | Admin, Lehrer |
| `/api/orgs/:id/learning-paths` | GET | Lernpfade | ✅ | Admin, Lehrer |
| `/api/orgs/:id/learning-paths` | POST | Lernpfad erstellen | ✅ | Admin, Lehrer |
| `/api/orgs/:id/analytics` | GET | Organisation-Analytics | ✅ | Admin |
| `/api/orgs/:id/analytics/class/:class_id` | GET | Klassen-Analytics | ✅ | Admin, Lehrer (eigene) |
| `/api/orgs/:id/token-pool` | GET | Token-Pool Status | ✅ | Admin |

### Beispiel-Request: Member hinzufügen

```http
POST /api/orgs/org_abc123/members
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "max.mustermann@schule.de",
  "display_name": "Max Mustermann",
  "role": "student",
  "classes": ["class_10a", "class_mathematik"]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "member_id": "mem_xyz789",
    "user_id": "user_123",
    "org_id": "org_abc123",
    "email": "max.mustermann@schule.de",
    "display_name": "Max Mustermann",
    "role": "student",
    "status": "active",
    "joined_at": "2024-02-15T10:00:00Z"
  },
  "message": "Mitglied hinzugefügt. Willkommens-Email wurde versendet."
}
```

---

## 15. Zusammenfassung

### ✅ Kernfunktionen

| Feature | Status | Details |
|---------|--------|---------|
| **Nutzerverwaltung** | ✅ | Unbegrenzte Nutzer, Rollen, Klassen |
| **Kursverwaltung** | ✅ | Interne Kurse, Importe, 12 Content-LMs (A-C) |
| **LiveRoom Pro** | ✅ | Unbegrenzte Teilnehmer, Aufzeichnung, Breakout Rooms |
| **Prüfungssystem** | ✅ | KI-Generierung (IHK, CompTIA), Auto-Bewertung |
| **Lernpfade** | ✅ | Strukturierte Pfade, Deadlines, AI-Optimierung |
| **Domain-Branding** | ✅ | Custom Domain, Logo, Theme |
| **Token-Pool** | ✅ | Zentrale Verwaltung, transparente Abrechnung |
| **Analytics** | ✅ | Umfassendes Reporting, Export (CSV, PDF, API) |
| **DSGVO-Modus** | ✅ | Schulkonformer Datenschutz |
| **Corporate Security** | ✅ | Enterprise-Grade Security |

### 🎯 Alleinstellungsmerkmale

**Was LSX für Organisationen besonders macht:**

1. **🤖 KI-First:** Vollständig integrierte KI (Prüfungen, Content, Analytics)
2. **🎥 LiveRoom Pro:** Professionelles Online-Teaching mit Aufzeichnung
3. **📊 Datengetriebene Optimierung:** AI-Insights zur Lernverbesserung
4. **🌐 White-Label:** Custom Domain & Branding
5. **💰 Faire Preise:** Transparente, nutzungsbasierte Abrechnung
6. **🔒 Datenschutz:** DSGVO-konform (Schulen) + Corporate Security

---

## 📌 Dokument abgeschlossen

**Version:** 1.0
**Status:** Final
**Letzte Aktualisierung:** 2024

---

> 💡 **Hinweis:** Dieses Dokument definiert die Professional/Enterprise-Ebene des LSX-Systems für Bildungseinrichtungen und Unternehmen mit vollständiger Verwaltung, professionellen Tools und umfassenden Analytics.
