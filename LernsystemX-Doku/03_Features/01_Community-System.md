# 05 – Community-System (Final)

**Version:** 1.0
**Stand:** Final

---

## Überblick

Das LSX-Community-System ist ein zentraler Bestandteil der Plattform und ermöglicht soziales Lernen, Wissensaustausch und organisches Wachstum. Es verbindet Free User, Premium User und Creator in einem Ökosystem, das durch qualitativ hochwertige Inhalte, Moderation und KI-gestützte Qualitätssicherung geprägt ist.

### 🎯 Kernziele

```plantuml
@startuml
title Community-System Ziele

package "Community Ziele" {
  [Kostenlose Kurse] as free_courses
  [Gemeinschaft fördern] as community
  [Sozialer Lernfortschritt] as social
  [Premium-Wert erhöhen] as premium_value
  [Creator-Testfeld] as creator_test
  [Qualitätssicherung] as quality
}

actor "Free User" as free #LightGray
actor "Premium User" as premium #Gold
actor "Creator" as creator #LightBlue
actor "Moderator" as mod #Orange

free --> free_courses : Zugang
premium --> community : Voller Zugang
premium --> social : Gruppen erstellen
creator --> creator_test : Inhalte testen
creator --> premium_value : Qualität liefern
mod --> quality : Content prüfen

note right of free_courses
  ✅ Basis-Methoden für alle
  ✅ Keine KI für Free
  ✅ Öffentlich durchsuchbar
end note

note right of creator_test
  ✅ Feedback sammeln
  ✅ Analytics nutzen
  ✅ Reichweite testen
end note

@enduml
```

---

## C4 Architektur

### Context Diagram

```plantuml
@startuml
!include <C4/C4_Context>

title Community-System Context Diagram

Person(free_user, "Free User", "Lernt mit Basis-Methoden")
Person(premium_user, "Premium User", "Lernt & veröffentlicht Community-Kurse")
Person(creator, "Creator", "Erstellt & monetarisiert Kurse")
Person(teacher, "Lehrer", "Importiert Community-Kurse")
Person(moderator, "Moderator", "Prüft & moderiert Inhalte")

System(community, "Community System", "Soziales Lernen, Kurse teilen, Gruppen")

System_Ext(course_system, "Kurs-System", "Kursarchitektur & Module")
System_Ext(ai_pipeline, "KI-Pipeline", "Content-Analyse & Qualitätsprüfung")
System_Ext(search, "Suchsystem", "Elasticsearch")
System_Ext(analytics, "Analytics", "Community-Metriken")

Rel(free_user, community, "Durchsucht kostenlose Kurse")
Rel(premium_user, community, "Veröffentlicht & lernt")
Rel(creator, community, "Veröffentlicht & verkauft")
Rel(teacher, community, "Importiert Kurse")
Rel(moderator, community, "Moderiert Inhalte")

Rel(community, course_system, "Verwendet Kurse")
Rel(community, ai_pipeline, "KI-Qualitätsprüfung")
Rel(community, search, "Indexiert Kurse")
Rel(community, analytics, "Speichert Metriken")

@enduml
```

### Container Diagram

```plantuml
@startuml
!include <C4/C4_Container>

title Community-System Container Diagram

Person(user, "User", "Community-Teilnehmer")
Person(moderator, "Moderator", "Content-Prüfer")

System_Boundary(community_system, "Community System") {
  Container(browser, "Kurs-Browser", "Vue.js", "Durchsuchen & Filtern von Kursen")
  Container(groups, "Gruppen-Manager", "Vue.js + WebSocket", "Private & öffentliche Gruppen")
  Container(comments, "Kommentar-System", "Vue.js", "Bewertungen & Feedback")
  Container(moderation, "Moderation-Panel", "Vue.js", "Content-Review & Sperren")

  ContainerDb(community_db, "Community DB", "PostgreSQL", "Kurse, Gruppen, Kommentare, Ratings")
  Container(ranking_engine, "Ranking-Engine", "Python/Celery", "Berechnet Kurs-Rankings")
  Container(ai_checker, "KI-Content-Checker", "Python/AI", "Plagiatsprüfung, Qualität")
  Container(notification, "Notification Service", "Python/SocketIO", "Echtzeit-Benachrichtigungen")
}

System_Ext(search_engine, "Elasticsearch", "Volltextsuche")
System_Ext(ai_pipeline, "KI-Pipeline", "AI Modules")
System_Ext(cdn, "CDN", "Media-Hosting")

Rel(user, browser, "Durchsucht Kurse", "HTTPS")
Rel(user, groups, "Erstellt/Betritt Gruppen", "HTTPS/WSS")
Rel(user, comments, "Kommentiert & bewertet", "HTTPS")
Rel(moderator, moderation, "Prüft Inhalte", "HTTPS")

Rel(browser, community_db, "Liest Kurse")
Rel(groups, community_db, "Speichert Gruppen")
Rel(comments, community_db, "Speichert Kommentare")
Rel(moderation, community_db, "Aktualisiert Status")

Rel(ranking_engine, community_db, "Liest Metriken")
Rel(ai_checker, ai_pipeline, "Nutzt AI-Module")
Rel(browser, search_engine, "Sucht Kurse")
Rel(notification, user, "Sendet Updates", "WebSocket")

@enduml
```

---

## Datenbankschema

### ER-Diagram: Community Entities

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) <color:#efefef><&media-record></color> x
!define table(x) entity x << (T, white) >>

title Community-System ER-Diagram

table(community_courses) {
  primary_key(community_course_id) : UUID
  foreign_key(course_id) : UUID
  foreign_key(created_by) : UUID
  column(title) : VARCHAR(255)
  column(description) : TEXT
  column(is_free) : BOOLEAN
  column(price) : DECIMAL(10,2)
  column(language) : VARCHAR(10)
  column(category) : VARCHAR(100)
  column(subcategory) : VARCHAR(100)
  column(tags) : JSONB
  column(visibility) : ENUM('public', 'unlisted', 'banned')
  column(quality_score) : FLOAT
  column(ai_verified) : BOOLEAN
  column(total_enrollments) : INTEGER
  column(average_rating) : FLOAT
  column(total_ratings) : INTEGER
  column(featured) : BOOLEAN
  column(trending_score) : FLOAT
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
  column(published_at) : TIMESTAMP
}

table(community_groups) {
  primary_key(group_id) : UUID
  foreign_key(created_by) : UUID
  column(name) : VARCHAR(255)
  column(description) : TEXT
  column(type) : ENUM('public', 'private')
  column(category) : VARCHAR(100)
  column(member_count) : INTEGER
  column(max_members) : INTEGER
  column(visibility) : ENUM('open', 'closed', 'secret')
  column(requires_approval) : BOOLEAN
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
}

table(group_members) {
  primary_key(membership_id) : UUID
  foreign_key(group_id) : UUID
  foreign_key(user_id) : UUID
  column(role) : ENUM('owner', 'moderator', 'member')
  column(joined_at) : TIMESTAMP
  column(status) : ENUM('active', 'muted', 'banned')
}

table(course_ratings) {
  primary_key(rating_id) : UUID
  foreign_key(community_course_id) : UUID
  foreign_key(user_id) : UUID
  column(rating) : INTEGER
  column(review_text) : TEXT
  column(helpful_count) : INTEGER
  column(verified_purchase) : BOOLEAN
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
}

table(course_comments) {
  primary_key(comment_id) : UUID
  foreign_key(community_course_id) : UUID
  foreign_key(user_id) : UUID
  foreign_key(parent_comment_id) : UUID
  column(content) : TEXT
  column(likes) : INTEGER
  column(is_pinned) : BOOLEAN
  column(is_edited) : BOOLEAN
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
}

table(moderation_queue) {
  primary_key(queue_id) : UUID
  foreign_key(content_id) : UUID
  foreign_key(reported_by) : UUID
  foreign_key(assigned_to) : UUID
  column(content_type) : ENUM('course', 'comment', 'group')
  column(reason) : VARCHAR(255)
  column(status) : ENUM('pending', 'reviewing', 'resolved', 'dismissed')
  column(priority) : ENUM('low', 'medium', 'high', 'critical')
  column(ai_flagged) : BOOLEAN
  column(ai_confidence) : FLOAT
  column(resolution) : TEXT
  column(created_at) : TIMESTAMP
  column(resolved_at) : TIMESTAMP
}

table(moderation_actions) {
  primary_key(action_id) : UUID
  foreign_key(queue_id) : UUID
  foreign_key(moderator_id) : UUID
  column(action_type) : ENUM('warn', 'hide', 'ban', 'delete', 'approve')
  column(reason) : TEXT
  column(duration) : INTEGER
  column(created_at) : TIMESTAMP
}

table(community_analytics) {
  primary_key(analytics_id) : UUID
  foreign_key(community_course_id) : UUID
  column(date) : DATE
  column(views) : INTEGER
  column(enrollments) : INTEGER
  column(completions) : INTEGER
  column(avg_time_spent) : INTEGER
  column(bounce_rate) : FLOAT
  column(engagement_score) : FLOAT
}

' Relationships
community_courses ||--o{ course_ratings : "has"
community_courses ||--o{ course_comments : "has"
community_courses ||--o{ moderation_queue : "reviewed in"
community_courses ||--o{ community_analytics : "tracked by"

community_groups ||--o{ group_members : "has"
community_groups ||--o{ moderation_queue : "reviewed in"

course_comments ||--o{ course_comments : "replies to"
course_comments ||--o{ moderation_queue : "reviewed in"

moderation_queue ||--o{ moderation_actions : "has"

@enduml
```

---

## 1. Rollen & Community-Berechtigungen

### Zugriffskontrolle

```plantuml
@startuml
title Community-Zugriffskontrolle

|Free User|
start
:Durchsuchen Community;
:Sehen nur **kostenlose** Kurse;
:Nur ausgewählte Methoden (Gruppe A+B teilweise);
note right
  ❌ Keine KI
  ❌ Kein Erstellen
  ❌ Keine Gruppen erstellen
end note
stop

|Premium User|
start
:Durchsuchen Community;
:Alle Kurse sehen;
:Alle 19 Content-LMs konsumieren (A-C);
:Community-Kurse veröffentlichen (kostenlos);
:Private Gruppen erstellen;
note right
  ✅ KI-Zugriff
  ✅ Erstellen (Community & Privat)
  ❌ Keine Gruppe D-Methoden erstellen
  ❌ Kein Verkauf
end note
stop

|Creator|
start
:Durchsuchen Community;
:Kurse veröffentlichen (kostenlos/bezahlt);
:Gruppe D-Methoden erstellen;
:Analytics nutzen;
:Global Publishing;
note right
  ✅ Monetarisierung
  ✅ 75% Revenue Share
  ✅ Creator Dashboard
end note
stop

|Lehrer/Schule/Unternehmen|
start
:Community durchsuchen;
:Kurse importieren/kopieren;
:Interne Gruppen erstellen;
note right
  ❌ Kein Community-Publishing
  ✅ Interner Einsatz
end note
stop

|Moderator|
start
:Inhalte prüfen;
:Kurse sperren/bannen;
:Kommentare verwalten;
note right
  ✅ Moderation-Panel
  ✅ KI-Unterstützung (Review)
end note
stop

@enduml
```

### Berechtigungsmatrix

| Funktion | Free | Premium | Creator | Lehrer | Schule | Unternehmen | Moderator | Admin |
|----------|------|---------|---------|--------|--------|-------------|-----------|-------|
| **Community durchsuchen** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Kostenlose Kurse sehen** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Alle Kurse sehen** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Community-Kurs erstellen** | ❌ | ✅ Kostenlos | ✅ Alle | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Kurs verkaufen** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Gruppe D-Methoden erstellen** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Öffentliche Gruppe erstellen** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Private Gruppe erstellen** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Gruppe beitreten** | ✅ Einladung | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Kommentieren** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Bewerten** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Content melden** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Moderieren** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Analytics sehen** | ❌ | ❌ | ✅ Eigene | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 2. Struktur der Community

### Komponenten-Übersicht

```plantuml
@startuml
!include <C4/C4_Component>

title Community-System Komponenten

Container_Boundary(community, "Community System") {
  Component(browser, "Kurs-Browser", "Vue.js Component", "Suchen & Filtern")
  Component(filter, "Filter-Engine", "JavaScript", "Kategorie, Preis, Sprache")
  Component(search, "Suchfunktion", "Elasticsearch Client", "Volltextsuche")

  Component(groups_public, "Öffentliche Gruppen", "Vue.js Component", "Community-Gruppen")
  Component(groups_private, "Private Study Groups", "Vue.js Component", "Premium-Lernräume")
  Component(group_chat, "Gruppen-Chat", "WebSocket", "Echtzeit-Kommunikation")

  Component(ratings, "Bewertungs-System", "Vue.js Component", "5-Sterne-Rating")
  Component(comments, "Kommentar-System", "Vue.js Component", "Feedback & Diskussion")
  Component(moderation_ui, "Moderation-UI", "Vue.js Component", "Content-Review")

  Component(ranking, "Ranking-Engine", "Python/Celery", "Trending, Popular, Top Rated")
  Component(ai_quality, "KI-Qualitätsprüfung", "Python/AI", "Plagiatsprüfung, Qualität")
}

Rel(browser, filter, "Nutzt")
Rel(browser, search, "Nutzt")
Rel(groups_public, group_chat, "Nutzt")
Rel(groups_private, group_chat, "Nutzt")
Rel(ratings, ranking, "Beeinflusst")
Rel(comments, moderation_ui, "Kann gemeldet werden")
Rel(ai_quality, ranking, "Beeinflusst")

@enduml
```

---

## 3. Kurs-Browser (Explore)

### Browse-Workflow

```plantuml
@startuml
title Community Kurs-Browser Workflow

actor User
participant "Browser UI" as UI
participant "Filter Engine" as Filter
participant "Search API" as Search
database "Elasticsearch" as ES
database "PostgreSQL" as DB

User -> UI : Öffnet Community
activate UI

UI -> Search : GET /api/community/courses
activate Search

Search -> ES : Volltextsuche
activate ES
ES --> Search : Ergebnisse
deactivate ES

Search -> DB : Lade Metadaten
activate DB
DB --> Search : Kursdaten
deactivate DB

Search --> UI : Kursliste
deactivate Search

UI --> User : Zeigt Kurse
deactivate UI

User -> UI : Wendet Filter an (Kategorie, Preis)
activate UI

UI -> Filter : Filtere Ergebnisse
activate Filter
Filter -> DB : WHERE category = ? AND price = ?
activate DB
DB --> Filter : Gefilterte Kurse
deactivate DB

Filter --> UI : Aktualisierte Liste
deactivate Filter

UI --> User : Zeigt gefilterte Kurse
deactivate UI

User -> UI : Klickt auf Kurs
activate UI
UI -> DB : GET /api/community/courses/:id
activate DB
DB --> UI : Kursdetails
deactivate DB
UI --> User : Kursdetailseite
deactivate UI

@enduml
```

### Filter-Optionen

| Filter | Optionen | Verfügbar für |
|--------|----------|---------------|
| **Kategorie** | IT, Sprachen, Business, Mathematik, Wissenschaft, etc. | Alle |
| **Unterkategorie** | Programmierung, Netzwerk, Cloud, etc. | Alle |
| **Preis** | Kostenlos, Bezahlt (€0-€500) | Alle |
| **Sprache** | DE, EN, FR, ES, IT, etc. (20 Sprachen) | Alle |
| **Schwierigkeit** | Anfänger, Fortgeschritten, Experte | Alle |
| **Lernmethoden** | Anzahl verfügbarer Methoden (19 Content-LMs) | Alle |
| **Bewertung** | 1-5 Sterne | Alle |
| **Erstellungsdatum** | Letzte Woche, Monat, Jahr | Alle |
| **Beliebtheit** | Trending, Most Popular, Editor's Pick | Alle |
| **Tags** | Custom Tags (JSON) | Alle |
| **Creator** | Creator-Name | Alle |
| **Verifiziert** | KI-verifiziert, Editor's Choice | Alle |

### Such-Syntax

```javascript
// Beispiel: Elasticsearch Query für Community-Browser
{
  "query": {
    "bool": {
      "must": [
        {
          "multi_match": {
            "query": "Python Programmierung",
            "fields": ["title^3", "description^2", "tags"]
          }
        },
        {
          "term": {
            "visibility": "public"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "is_free": true
          }
        },
        {
          "term": {
            "language": "de"
          }
        },
        {
          "range": {
            "average_rating": {
              "gte": 4.0
            }
          }
        }
      ]
    }
  },
  "sort": [
    {
      "trending_score": {
        "order": "desc"
      }
    },
    {
      "created_at": {
        "order": "desc"
      }
    }
  ]
}
```

---

## 4. Kursarten in der Community

### Kursarten-Übersicht

```plantuml
@startuml
title Community-Kursarten

package "Community-Kurse" {
  [Kostenlose Community-Kurse] as free_community #LightGreen
  [Premium-optimierte Kurse] as premium_community #Gold
  [LSX Academy Vorschau] as academy_preview #LightBlue
  [Creator Marketplace-Kurse] as marketplace #LightCoral
}

actor "Free User" as free #LightGray
actor "Premium User" as premium #Gold
actor "Creator" as creator #LightBlue

free --> free_community : ✅ Zugriff (Basis-Methoden)
premium --> free_community : ✅ Voller Zugriff
premium --> premium_community : ✅ Voller Zugriff
premium --> academy_preview : ✅ Vorschau
creator --> marketplace : ✅ Erstellen & Verkaufen

note right of free_community
  ✅ Kostenlos
  ✅ Öffentlich
  ✅ Basis + Premium-Methoden
  ❌ Keine Pro-Methoden
end note

note right of premium_community
  ✅ "Premium Recommended" Badge
  ✅ Alle 19 Content-LMs (A-C)
  ✅ KI-optimiert
  ✅ Hochwertige Inhalte
end note

note right of academy_preview
  ✅ Auszug (Preview)
  ✅ Bewerbung für LSX Academy
  ✅ Upgrade-Anreiz
end note

note right of marketplace
  ✅ Bezahlt
  ✅ 75% Revenue Share
  ✅ Creator Analytics
  ✅ Global Publishing
end note

@enduml
```

### Kursarten-Details

#### 4.1 Kostenlose Community-Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | Premium User, Creator |
| **Preis** | Kostenlos |
| **Sichtbarkeit** | Öffentlich |
| **Lernmethoden** | Gruppe A–C (LM00–LM25) |
| **KI** | Optional |
| **Nutzung** | Alle Rollen können lernen |
| **Import** | Lehrer/Schule/Unternehmen können kopieren |

**Beispiel-Datenstruktur:**

```json
{
  "community_course_id": "a1b2c3d4-...",
  "course_id": "e5f6g7h8-...",
  "created_by": "user_uuid",
  "title": "Python für Anfänger",
  "description": "Grundlagen der Python-Programmierung",
  "is_free": true,
  "price": 0.00,
  "language": "de",
  "category": "IT",
  "subcategory": "Programmierung",
  "tags": ["Python", "Coding", "Anfänger"],
  "visibility": "public",
  "quality_score": 4.2,
  "ai_verified": true,
  "total_enrollments": 1523,
  "average_rating": 4.5,
  "total_ratings": 342,
  "featured": false,
  "trending_score": 87.3,
  "created_at": "2024-01-15T10:30:00Z",
  "published_at": "2024-01-15T12:00:00Z"
}
```

#### 4.2 Premium-optimierte Community-Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | Creator (verifiziert) |
| **Badge** | "Premium Recommended" |
| **Lernmethoden** | Alle 19 Content-LMs (A-C) |
| **KI** | Intensiv genutzt |
| **Qualität** | KI-verifiziert, mind. 4.5 Sterne |
| **Sichtbarkeit** | Featured, Trending |

#### 4.3 LSX Academy Vorschau-Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | LSX Academy (Admin) |
| **Inhalt** | Auszug aus offiziellen Kursen |
| **Zweck** | Marketing für Premium-Kurse |
| **Badge** | "LSX Academy Preview" |
| **Upgrade-Link** | Zu Vollversion |

#### 4.4 Creator Marketplace-Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Ersteller** | Creator |
| **Preis** | €5 - €500 |
| **Revenue Share** | 75% an Creator |
| **Lernmethoden** | 19 Content-LMs (A-C) |
| **Global Publishing** | 20 Sprachen |
| **Analytics** | Vollständig |

---

## 5. Private Study Groups (Premium+)

### Gruppen-Workflow

```plantuml
@startuml
title Private Study Group Workflow

|Premium User|
start
:Erstellt Study Group;
:Definiert Gruppenname & Beschreibung;
:Wählt Sichtbarkeit (Private/Secret);
:Lädt Mitglieder ein;

|System|
:Erstellt group_id;
:Speichert in community_groups;
:Sendet Einladungen;

|Eingeladene User|
:Erhält Einladung;
if (Premium/Creator/Lehrer?) then (ja)
  :Akzeptiert Einladung;
  :Wird member;
else (nein, Free)
  :Kann nur beitreten (Einladung);
  note right
    Free User können nur eingeladen werden,
    aber nicht selbst erstellen
  end note
endif

|Gruppe|
:Mitglieder lernen gemeinsam;
:Notizen teilen;
:Whiteboard nutzen;
:Hausaufgaben teilen;
:Chat-Funktion;

stop

@enduml
```

### Gruppen-Typen

| Typ | Sichtbarkeit | Wer kann erstellen | Wer kann beitreten |
|-----|--------------|--------------------|--------------------|
| **Öffentlich** | Alle sehen | Premium+, Creator, Lehrer | Alle |
| **Privat** | Nur Mitglieder | Premium+, Creator, Lehrer | Nur Eingeladene |
| **Secret** | Unsichtbar | Premium+, Creator, Lehrer | Nur Eingeladene |

### Gruppen-Features

```plantuml
@startuml
!include <C4/C4_Component>

title Private Study Group Features

Container_Boundary(study_group, "Study Group") {
  Component(group_chat, "Gruppen-Chat", "WebSocket", "Echtzeit-Kommunikation")
  Component(shared_notes, "Geteilte Notizen", "CKEditor", "Kollaboratives Schreiben")
  Component(whiteboard, "Whiteboard", "Canvas API", "Visuelle Zusammenarbeit")
  Component(homework, "Hausaufgaben", "Vue.js", "Aufgaben teilen & lösen")
  Component(group_progress, "Gruppen-Fortschritt", "Chart.js", "Gemeinsame Metriken")
  Component(file_sharing, "Datei-Sharing", "S3", "Dokumente teilen")
}

System_Ext(liveroom, "LiveRoom", "Video-Calls")
System_Ext(course_system, "Kurs-System", "Kurse & Module")

Rel(group_chat, liveroom, "Kann starten")
Rel(shared_notes, course_system, "Verknüpft mit Kursen")
Rel(homework, course_system, "Basiert auf Modulen")

@enduml
```

---

## 6. Community-Gruppen (öffentlich)

### Öffentliche Gruppen-Features

```plantuml
@startuml
title Öffentliche Community-Gruppen

actor "Free User" as free #LightGray
actor "Premium User" as premium #Gold
actor "Creator" as creator #LightBlue

package "Öffentliche Gruppe" {
  [Diskussionen] as discussions
  [Ressourcen teilen] as resources
  [Lernmethoden teilen] as methods
  [Dateien teilen] as files
}

free --> discussions : ✅ Lesen & Kommentieren
premium --> discussions : ✅ Erstellen & Moderieren
creator --> discussions : ✅ Erstellen & Moderieren

free -[#red]-> resources : ❌ Kein Teilen
premium --> resources : ✅ Teilen
creator --> resources : ✅ Teilen

free -[#red]-> methods : ❌ Kein Teilen
premium --> methods : ✅ Teilen
creator --> methods : ✅ Teilen

free -[#red]-> files : ❌ Kein Upload
premium --> files : ✅ Upload (50MB)
creator --> files : ✅ Upload (100MB)

@enduml
```

### Gruppen-Kategorien

| Kategorie | Beschreibung | Beispiele |
|-----------|--------------|-----------|
| **Lerngruppen** | Gemeinsames Lernen | "Python Lerngruppe", "IHK Prüfungsvorbereitung" |
| **Themenforen** | Diskussionen zu Themen | "Cloud Computing", "Künstliche Intelligenz" |
| **Regional** | Lokale Gruppen | "Berlin Coding Meetup", "München IT-Community" |
| **Sprachen** | Sprachlernen | "Deutsch für Anfänger", "English Conversation" |
| **Fachbereiche** | Berufliche Themen | "IT-Security Experten", "BWL-Studenten" |

---

## 7. Kommentar- und Bewertungssystem

### Bewertungs-Workflow

```plantuml
@startuml
title Kurs-Bewertungs-Workflow

actor User
participant "Kursseite" as Course
participant "Rating API" as API
database "PostgreSQL" as DB
participant "Ranking Engine" as Ranking

User -> Course : Beendet Kurs
activate Course

Course --> User : "Bitte bewerten Sie den Kurs"

User -> Course : Gibt 5 Sterne + Review
activate API

Course -> API : POST /api/community/ratings
API -> DB : INSERT INTO course_ratings
activate DB
DB --> API : rating_id
deactivate DB

API -> Ranking : Update Kurs-Ranking
activate Ranking
Ranking -> DB : UPDATE community_courses\nSET average_rating = ...,\n    total_ratings = ...
activate DB
DB --> Ranking : OK
deactivate DB

Ranking -> Ranking : Berechne trending_score
Ranking --> API : OK
deactivate Ranking

API --> Course : Bewertung gespeichert
deactivate API

Course --> User : "Danke für Ihr Feedback!"
deactivate Course

@enduml
```

### Bewertungs-Datenstruktur

```json
{
  "rating_id": "r1a2t3i4-...",
  "community_course_id": "c5o6u7r8-...",
  "user_id": "u9s0e1r2-...",
  "rating": 5,
  "review_text": "Hervorragender Kurs! Die KI-gestützten Methoden haben mir sehr geholfen.",
  "helpful_count": 23,
  "verified_purchase": true,
  "created_at": "2024-02-10T14:30:00Z",
  "updated_at": "2024-02-10T14:30:00Z"
}
```

### Kommentar-Hierarchie

```plantuml
@startuml
title Kommentar-Thread-Struktur

object "Kurs-Kommentar #1" as c1 {
  comment_id = "c1"
  parent_comment_id = NULL
  content = "Toller Kurs!"
  likes = 15
}

object "Antwort #1.1" as c1_1 {
  comment_id = "c1_1"
  parent_comment_id = "c1"
  content = "Stimme zu!"
  likes = 3
}

object "Antwort #1.2" as c1_2 {
  comment_id = "c1_2"
  parent_comment_id = "c1"
  content = "Welches Modul fandest du am besten?"
  likes = 1
}

object "Antwort #1.2.1" as c1_2_1 {
  comment_id = "c1_2_1"
  parent_comment_id = "c1_2"
  content = "Modul 3 war super!"
  likes = 2
}

c1 --> c1_1
c1 --> c1_2
c1_2 --> c1_2_1

@enduml
```

---

## 8. Moderations-System

### Moderation-Workflow

```plantuml
@startuml
title Content-Moderation Workflow

|User|
start
:Meldet Content (Report);

|System|
:Erstellt moderation_queue Entry;
if (KI-Auto-Check?) then (ja)
  :KI analysiert Content;
  if (KI-Confidence > 90%?) then (ja, unsafe)
    :Flagged = TRUE;
    :Priority = CRITICAL;
  else (nein, safe)
    :Flagged = FALSE;
    :Priority = LOW;
  endif
else (nein)
  :Priority = MEDIUM;
endif

|Moderator|
:Erhält Benachrichtigung;
:Öffnet Moderation-Panel;
:Prüft Content;

if (Verstoß?) then (ja)
  :Wählt Aktion (Warnung/Sperren/Löschen);
  :Erstellt moderation_action;

  |System|
  :Führt Aktion aus;
  if (Aktion = Ban?) then (ja)
    :visibility = 'banned';
    :Sendet Benachrichtigung an Creator;
  else if (Aktion = Hide?) then (ja)
    :visibility = 'unlisted';
  else (Warnung)
    :Sendet Warnung an User;
  endif
else (nein)
  :Status = 'dismissed';
endif

:queue.status = 'resolved';
stop

@enduml
```

### Moderations-Aktionen

| Aktion | Beschreibung | Dauer | Auswirkung |
|--------|--------------|-------|------------|
| **Warnung** | User wird gewarnt | Permanent (Log) | Keine direkte Auswirkung |
| **Ausblenden** | Content unsichtbar | Temporär/Permanent | visibility = 'unlisted' |
| **Sperren** | Content gebannt | Permanent | visibility = 'banned' |
| **Löschen** | Content gelöscht | Permanent | Datensatz entfernt |
| **Freigeben** | Content genehmigt | - | Zurück zu 'public' |

### KI-Moderation

```plantuml
@startuml
title KI-gestützte Content-Prüfung

participant "Content" as Content
participant "AI Checker" as AI
participant "Plagiarism DB" as Plagiarism
participant "Quality Analyzer" as Quality
participant "Moderation Queue" as Queue

Content -> AI : Neuer Community-Kurs veröffentlicht
activate AI

AI -> Plagiarism : Prüfe auf Plagiate
activate Plagiarism
Plagiarism --> AI : Similarity Score
deactivate Plagiarism

AI -> Quality : Analysiere Qualität
activate Quality
Quality -> Quality : Grammatik, Struktur, Vollständigkeit
Quality --> AI : Quality Score
deactivate Quality

AI -> AI : Berechne Gesamtbewertung

alt Plagiat erkannt (Similarity > 80%)
  AI -> Queue : Erstelle Critical-Queue-Entry
  activate Queue
  Queue --> AI : queue_id
  deactivate Queue
  AI -> Content : Setze ai_verified = FALSE
else Qualität mangelhaft (Score < 3.0)
  AI -> Queue : Erstelle Medium-Queue-Entry
  AI -> Content : Setze ai_verified = FALSE
else Alles OK
  AI -> Content : Setze ai_verified = TRUE\nSetze quality_score = X
end

deactivate AI

@enduml
```

---

## 9. KI in der Community

### KI-Module für Community

| KI-Modul | Funktion | Einsatzbereich |
|----------|----------|----------------|
| **Content-Analyzer** | Qualitätsprüfung | Neue Kurse |
| **Plagiarism-Checker** | Duplikate finden | Alle Inhalte |
| **Category-Suggester** | Auto-Kategorisierung | Neue Kurse |
| **Sentiment-Analyzer** | Bewertungsanalyse | Reviews & Kommentare |
| **Recommendation-Engine** | Personalisierte Vorschläge | Kurs-Browser |
| **Spam-Detector** | Spam-Erkennung | Kommentare & Bewertungen |
| **Quality-Scorer** | Bewertung der Kursqualität | Ranking |

### KI-Qualitätsprüfung

```python
# Beispiel: KI-Qualitätsprüfung für Community-Kurse

from ai_modules.content_analyzer import analyze_course_quality
from ai_modules.plagiarism_checker import check_plagiarism
from models.community_course import CommunityCourse

def ai_verify_course(course_id):
    """
    KI-gestützte Qualitätsprüfung für Community-Kurse
    """
    course = CommunityCourse.query.get(course_id)

    # 1. Plagiatsprüfung
    plagiarism_score = check_plagiarism(
        title=course.title,
        description=course.description,
        content=course.get_full_content()
    )

    if plagiarism_score > 0.8:
        # Zu hohe Ähnlichkeit mit existierenden Kursen
        flag_for_moderation(
            course_id=course_id,
            reason="Mögliches Plagiat",
            priority="critical",
            ai_confidence=plagiarism_score
        )
        return False

    # 2. Qualitätsanalyse
    quality_metrics = analyze_course_quality(
        course_content=course.get_full_content(),
        modules=course.get_modules(),
        learning_methods=course.get_learning_methods()
    )

    course.quality_score = quality_metrics['overall_score']

    if quality_metrics['overall_score'] < 3.0:
        # Niedrige Qualität
        flag_for_moderation(
            course_id=course_id,
            reason="Qualität unter Mindeststandard",
            priority="medium",
            ai_confidence=quality_metrics['confidence']
        )
        course.ai_verified = False
    else:
        course.ai_verified = True

    # 3. Auto-Kategorisierung
    suggested_categories = quality_metrics['suggested_categories']
    if not course.category:
        course.category = suggested_categories[0]
        course.subcategory = suggested_categories[1]

    course.save()
    return course.ai_verified
```

---

## 10. Community-Ranking

### Ranking-Algorithmus

```plantuml
@startuml
title Community-Ranking-Berechnung

start

:Lade Kurs-Metriken;
note right
  - Bewertungen
  - Enrollments
  - Completions
  - Engagement
  - Qualität
end note

partition "Berechnung" {
  :quality_weight = quality_score * 0.25;
  :rating_weight = (average_rating / 5) * 0.20;
  :activity_weight = (enrollments / max_enrollments) * 0.15;
  :completion_weight = (completions / enrollments) * 0.15;
  :recency_weight = age_factor() * 0.10;
  :engagement_weight = (comments + likes) * 0.15;
}

:trending_score = SUM(all_weights);

if (trending_score > 80) then (yes)
  :Badge = "Trending";
  :featured = TRUE;
else if (average_rating >= 4.5 AND total_ratings > 50) then (yes)
  :Badge = "Top Rated";
else if (enrollments > 1000) then (yes)
  :Badge = "Popular";
else (normal)
  :Kein Badge;
endif

:Speichere in DB;

stop

@enduml
```

### Ranking-Kategorien

| Kategorie | Kriterien | Badge |
|-----------|-----------|-------|
| **Trending** | trending_score > 80 | 🔥 Trending |
| **Top Rated** | average_rating ≥ 4.5 AND total_ratings > 50 | ⭐ Top Rated |
| **Popular Today** | enrollments_today > 100 | 📈 Popular |
| **Editor's Pick** | Manuell ausgewählt von Admins | ✨ Editor's Pick |
| **Premium Recommended** | quality_score > 4.0 AND creator_verified | 💎 Premium |
| **LSX Academy** | Offizieller Kurs | 🏆 LSX Academy |

### Ranking-Gewichtung

```javascript
// Beispiel: Trending-Score-Berechnung

function calculateTrendingScore(course) {
  const weights = {
    quality: 0.25,      // KI-Qualitätsscore
    rating: 0.20,       // User-Bewertungen
    activity: 0.15,     // Enrollments
    completion: 0.15,   // Completion Rate
    recency: 0.10,      // Aktualität
    engagement: 0.15    // Comments + Likes
  };

  const metrics = {
    quality: course.quality_score / 5,
    rating: course.average_rating / 5,
    activity: Math.min(course.total_enrollments / 1000, 1),
    completion: course.completions / Math.max(course.total_enrollments, 1),
    recency: calculateRecencyFactor(course.created_at),
    engagement: Math.min((course.total_comments + course.total_likes) / 500, 1)
  };

  let score = 0;
  for (const [key, weight] of Object.entries(weights)) {
    score += metrics[key] * weight * 100;
  }

  return Math.round(score * 10) / 10; // 0-100
}

function calculateRecencyFactor(createdAt) {
  const ageInDays = (Date.now() - new Date(createdAt)) / (1000 * 60 * 60 * 24);

  if (ageInDays < 7) return 1.0;       // Letzte Woche
  if (ageInDays < 30) return 0.8;      // Letzter Monat
  if (ageInDays < 90) return 0.5;      // Letzte 3 Monate
  if (ageInDays < 365) return 0.3;     // Letztes Jahr
  return 0.1;                           // Älter als 1 Jahr
}
```

---

## 11. Community-Regeln

### Verhaltenskodex

| Nr. | Regel | Konsequenz bei Verstoß |
|-----|-------|------------------------|
| 1 | Kein Spam oder Werbung | Warnung → Ban |
| 2 | Keine Plagiate | Sofortige Sperrung |
| 3 | Keine illegalen Inhalte | Sofortige Sperrung + Meldung |
| 4 | Respektvoller Umgangston | Warnung → Temporärer Ban |
| 5 | KI-Inhalte müssen verifizierbar sein | Kurs-Review |
| 6 | Keine externen Werbelinks | Entfernung + Warnung |
| 7 | Keine falschen Informationen | Kurs-Review → Sperrung |
| 8 | Keine doppelten Kurse | Duplikat löschen |

### Content-Policy

```plantuml
@startuml
title Community Content Policy

start

:User erstellt Community-Kurs;

partition "Automatische Prüfungen" {
  if (KI-Content ohne Nachweis?) then (ja)
    :Warnung: "Bitte verifizieren";
  endif

  if (Plagiat erkannt?) then (ja)
    :Kurs gesperrt;
    stop
  endif

  if (Illegaler Content?) then (ja)
    :Sofortige Sperrung;
    :Meldung an Admin;
    stop
  endif
}

partition "Manuelle Prüfung" {
  if (Qualitätsscore < 3.0?) then (ja)
    :An Moderation;

    if (Moderator: Verstoß?) then (ja)
      :Kurs abgelehnt;
      stop
    else (nein)
      :Kurs freigegeben;
    endif
  endif
}

:Kurs veröffentlicht;

stop

@enduml
```

---

## 12. Interne Funktionen für LSX Academy & Admin

### Admin-Dashboard

```plantuml
@startuml
!include <C4/C4_Component>

title Admin Community-Dashboard

Container_Boundary(admin_dashboard, "Admin Dashboard") {
  Component(analytics, "Community-Analytics", "Python/Pandas", "Metriken & Statistiken")
  Component(promotion, "Promotion-Engine", "Python", "Kurse für Marketing auswählen")
  Component(creator_insights, "Creator-Insights", "Vue.js", "High-Potential Creators")
  Component(content_monitor, "Content-Monitor", "Python/AI", "Verdächtige Inhalte")
  Component(cluster_analysis, "Themen-Cluster", "ML", "Schwachstellen-Analyse")
  Component(engagement, "Engagement-Tracker", "Python", "Community-Aktivität")
}

Database(analytics_db, "Analytics DB", "PostgreSQL")
System_Ext(ai_pipeline, "KI-Pipeline", "ML Models")

Rel(analytics, analytics_db, "Liest Metriken")
Rel(promotion, analytics, "Nutzt Daten")
Rel(creator_insights, analytics, "Nutzt Daten")
Rel(content_monitor, ai_pipeline, "KI-Analyse")
Rel(cluster_analysis, ai_pipeline, "ML-Clustering")

@enduml
```

### Admin-Metriken

| Metrik | Beschreibung | Verwendung |
|--------|--------------|------------|
| **Kurs-Promotion-Score** | Eignung für Marketing | Auswahl für LSX Academy |
| **Creator-Potenzial** | High-Potential Creators | Direktansprache, Partnerschaften |
| **Content-Flagging** | Verdächtige Inhalte | Moderation |
| **Performance-Daten** | Top-Kurse, Top-Kategorien | Algorithmus-Optimierung |
| **Themen-Cluster** | Schwachstellen in Themen | Neue Kurse planen |
| **Engagement-Stats** | Aktivität pro Kategorie | Community-Strategie |

---

## 13. Analytics für Creator

### Creator-Dashboard

```plantuml
@startuml
title Creator Community-Analytics

actor Creator
participant "Creator Dashboard" as Dashboard
database "Analytics DB" as DB
participant "Chart Engine" as Chart

Creator -> Dashboard : Öffnet Community-Kurse
activate Dashboard

Dashboard -> DB : GET /api/creator/analytics/:course_id
activate DB

DB -> DB : Aggregiere Metriken\n(Views, Enrollments, Ratings)

DB --> Dashboard : Analytics-Daten
deactivate DB

Dashboard -> Chart : Generiere Charts
activate Chart

Chart -> Chart : Erstelle Grafiken:\n- Views/Tag\n- Enrollments/Woche\n- Rating-Verteilung\n- Completion Rate\n- Geographic Distribution

Chart --> Dashboard : Chart-Daten
deactivate Chart

Dashboard --> Creator : Zeigt Dashboard mit:\n- 📊 Views & Enrollments\n- ⭐ Bewertungen\n- 💬 Kommentare\n- 🌍 Geografische Verteilung\n- 📈 Trending Score
deactivate Dashboard

@enduml
```

### Creator-Metriken

| Metrik | Beschreibung | Visualisierung |
|--------|--------------|----------------|
| **Views** | Anzahl Kursaufrufe | Line Chart (Zeitverlauf) |
| **Enrollments** | Einschreibungen | Line Chart (Zeitverlauf) |
| **Completions** | Abschlüsse | Pie Chart (%) |
| **Average Rating** | Durchschnittsbewertung | Star Rating + Bar Chart |
| **Reviews** | Anzahl Bewertungen | Number + List |
| **Comments** | Kommentare | Number + List |
| **Trending Score** | Aktueller Trending-Score | Gauge Chart (0-100) |
| **Revenue** | Einnahmen (für bezahlte Kurse) | Line Chart + Total |
| **Geographic Distribution** | Nutzer nach Land | Map Chart |
| **Completion Rate** | Abschlussquote | Percentage + Trend |

---

## 14. API-Endpoints

### Community-API

| Endpoint | Methode | Beschreibung | Auth | Rolle |
|----------|---------|--------------|------|-------|
| `/api/community/courses` | GET | Liste aller Community-Kurse | Optional | Alle |
| `/api/community/courses/:id` | GET | Kursdetails | Optional | Alle |
| `/api/community/courses` | POST | Neuen Kurs erstellen | ✅ | Premium+, Creator |
| `/api/community/courses/:id` | PUT | Kurs aktualisieren | ✅ | Creator (eigener Kurs) |
| `/api/community/courses/:id` | DELETE | Kurs löschen | ✅ | Creator (eigener Kurs), Admin |
| `/api/community/groups` | GET | Liste aller Gruppen | Optional | Alle |
| `/api/community/groups` | POST | Gruppe erstellen | ✅ | Premium+, Creator, Lehrer |
| `/api/community/groups/:id/join` | POST | Gruppe beitreten | ✅ | Alle |
| `/api/community/groups/:id/leave` | POST | Gruppe verlassen | ✅ | Alle |
| `/api/community/ratings` | POST | Bewertung abgeben | ✅ | Alle |
| `/api/community/comments` | POST | Kommentar erstellen | ✅ | Alle |
| `/api/community/comments/:id` | DELETE | Kommentar löschen | ✅ | Ersteller, Moderator, Admin |
| `/api/community/moderation/report` | POST | Content melden | ✅ | Alle |
| `/api/community/moderation/queue` | GET | Moderation-Queue | ✅ | Moderator, Admin |
| `/api/community/moderation/action` | POST | Moderations-Aktion | ✅ | Moderator, Admin |
| `/api/community/analytics/:course_id` | GET | Kurs-Analytics | ✅ | Creator (eigener Kurs), Admin |

### Beispiel-Request: Kurs erstellen

```http
POST /api/community/courses
Authorization: Bearer <token>
Content-Type: application/json

{
  "course_id": "e5f6g7h8-...",
  "title": "Python für Anfänger",
  "description": "Grundlagen der Python-Programmierung",
  "is_free": true,
  "language": "de",
  "category": "IT",
  "subcategory": "Programmierung",
  "tags": ["Python", "Coding", "Anfänger"]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "community_course_id": "a1b2c3d4-...",
    "course_id": "e5f6g7h8-...",
    "created_by": "user_uuid",
    "title": "Python für Anfänger",
    "visibility": "public",
    "ai_verified": false,
    "quality_score": null,
    "created_at": "2024-02-15T10:00:00Z"
  },
  "message": "Kurs wird von KI geprüft und dann veröffentlicht."
}
```

---

## 15. Zukunftserweiterungen

### Geplante Features

| Feature | Beschreibung | Priorität | Status |
|---------|--------------|-----------|--------|
| **Community-Challenges** | Wettbewerbe & Challenges | Hoch | Geplant |
| **Badges & Achievements** | Gamification für Community | Mittel | Geplant |
| **Creator-Partnerschaft** | Offizielle LSX-Partner | Hoch | In Entwicklung |
| **Live-Events** | Community-weite Events | Mittel | Geplant |
| **Mentorship-Programm** | Creator helfen Lernenden | Niedrig | Idee |
| **Community-Podcasts** | Audio-Inhalte | Niedrig | Idee |

---

## 16. Zusammenfassung

### ✅ Kernfunktionen

| Bereich | Features |
|---------|----------|
| **Kurse** | Kostenlose & bezahlte Community-Kurse, Premium-optimiert, LSX Academy Vorschau |
| **Gruppen** | Öffentliche & private Study Groups, Chat, Whiteboard, Datei-Sharing |
| **Social** | Kommentare, Bewertungen, Diskussionen |
| **Moderation** | KI-gestützte Content-Prüfung, Moderation-Queue, Aktionen |
| **Ranking** | Trending, Top Rated, Popular, Editor's Pick |
| **Analytics** | Creator-Dashboard, Admin-Insights, Community-Metriken |
| **KI** | Qualitätsprüfung, Plagiatserkennung, Auto-Kategorisierung |

### 🎯 Design-Prinzipien

- **Inklusiv:** Free User haben Zugang zu Basis-Inhalten
- **Qualität:** KI-gestützte Qualitätssicherung
- **Community-Driven:** Nutzer erstellen & teilen Inhalte
- **Fair für Creator:** 75% Revenue Share, Analytics, Global Publishing
- **Moderiert:** Strenge Regeln & Moderation
- **Skalierbar:** Elasticsearch, Caching, Ranking-Engine

---

## 📌 Dokument abgeschlossen

**Version:** 1.0
**Status:** Final
**Letzte Aktualisierung:** 2024

---

> 💡 **Hinweis:** Das Community-System ist ein lebendiges Ökosystem, das durch Nutzer, Creator und KI gemeinsam wächst. Es bildet das Herzstück des sozialen Lernens bei LSX.
