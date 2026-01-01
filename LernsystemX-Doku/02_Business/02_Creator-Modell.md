# 07 – Creator-Modell (Final)

**Version:** 1.0
**Stand:** Final

---

## Überblick

Das LSX-Creator-Modell ist das wirtschaftliche Rückgrat der Plattform. Creator sind Kursautoren, Dozenten, Coaches und Experten, die hochwertige Bildungsinhalte erstellen, global veröffentlichen und durch 75% Revenue Share monetarisieren. Sie verfügen über Business-Funktionen, die weit über Premium-User hinausgehen.

### 🎯 Creator-Positionierung

```plantuml
@startuml
title Creator-Modell Positionierung

package "LSX Business-Ökosystem" {
  [Premium User] as premium #Gold
  [Creator] as creator #LightBlue
  [Marketplace] as marketplace #LightCoral
  [Global Publishing] as global #LightGreen
  [Analytics] as analytics #Purple
}

actor "Kursautor" as author
actor "Käufer" as buyer
actor "LSX Platform" as platform

author --> creator : **Erstellt Kurse**
creator --> marketplace : Verkauft
creator --> global : 20 Sprachen
creator --> analytics : Insights

buyer --> marketplace : Kauft Kurse
marketplace --> author : 75% Revenue
marketplace --> platform : 25% Platform Fee

note right of creator
  ✅ Alle 19 Content-LMs erstellen (A-C)
  ✅ Global Publishing
  ✅ 75% Revenue Share
  ✅ Creator-Analytics
  ✅ 20.000 Tokens/Monat
  ✅ 29,99 € / Monat
end note

note left of premium
  Premium kann KEINE
  Kurse verkaufen
end note

@enduml
```

---

## C4 Architektur

### Context Diagram

```plantuml
@startuml
!include <C4/C4_Context>

title Creator-System Context Diagram

Person(creator, "Creator", "Erstellt & verkauft Kurse")
Person(buyer, "Käufer", "Kauft Creator-Kurse")
Person(admin, "Admin", "Verifiziert Creator")

System(creator_system, "Creator System", "Monetarisierung, Publishing, Analytics")

System_Ext(course_system, "Kurs-System", "Kurserstellung")
System_Ext(ai_pipeline, "KI-Pipeline", "Content-Generierung & Übersetzung")
System_Ext(marketplace, "Marketplace", "Kursverkauf")
System_Ext(payment, "Payment System", "Stripe, Payouts")
System_Ext(analytics, "Analytics", "Creator-Metriken")
System_Ext(translation, "Übersetzungs-System", "20 Sprachen")

Rel(creator, creator_system, "Erstellt Kurse, sieht Einnahmen")
Rel(buyer, marketplace, "Kauft Kurse")
Rel(admin, creator_system, "Verifiziert Creator")

Rel(creator_system, course_system, "Nutzt Kurseditor")
Rel(creator_system, ai_pipeline, "KI-Generierung")
Rel(creator_system, marketplace, "Publiziert Kurse")
Rel(creator_system, payment, "Erhält Auszahlungen")
Rel(creator_system, analytics, "Trackt Performance")
Rel(creator_system, translation, "Global Publishing")

@enduml
```

### Container Diagram

```plantuml
@startuml
!include <C4/C4_Container>

title Creator-System Container Diagram

Person(creator, "Creator", "Kursautor")
Person(buyer, "Käufer", "Kursteilnehmer")

System_Boundary(creator_system, "Creator System") {
  Container(creator_dashboard, "Creator Dashboard", "Vue.js", "Einnahmen, Analytics, Kursverwaltung")
  Container(course_editor, "Advanced Course Editor", "Vue.js", "19 Content-LMs (A-C) + Pro-Features")
  Container(marketplace_mgmt, "Marketplace Manager", "Python/Flask", "Kursverkauf & Pricing")
  Container(payout_service, "Payout Service", "Python", "Einnahmen-Auszahlung")
  Container(global_publisher, "Global Publisher", "Python", "20-Sprachen-Publishing")
  Container(creator_analytics, "Creator Analytics", "Python/Pandas", "Performance-Metriken")

  ContainerDb(creator_db, "Creator DB", "PostgreSQL", "Profile, Sales, Payouts")
  Container(revenue_tracker, "Revenue Tracker", "Python/Celery", "Echtzeit-Einnahmen")
}

System_Ext(stripe, "Stripe API", "Zahlungen & Payouts")
System_Ext(ai_translation, "KI-Übersetzung", "DeepL/GPT")
System_Ext(ai_content, "KI-Content-Generator", "AI-Pipeline")

Rel(creator, creator_dashboard, "Verwaltet Kurse", "HTTPS")
Rel(creator, course_editor, "Erstellt Kurse", "HTTPS")
Rel(buyer, marketplace_mgmt, "Kauft Kurs", "HTTPS")

Rel(course_editor, ai_content, "KI-Generierung")
Rel(marketplace_mgmt, stripe, "Verarbeitet Zahlung")
Rel(payout_service, stripe, "Auszahlung an Creator")
Rel(global_publisher, ai_translation, "Übersetzt Kurse")

Rel(creator_dashboard, creator_db, "Liest Daten")
Rel(marketplace_mgmt, creator_db, "Speichert Sales")
Rel(revenue_tracker, creator_db, "Aktualisiert Einnahmen")
Rel(creator_analytics, creator_db, "Analysiert Performance")

@enduml
```

---

## Datenbankschema

### ER-Diagram: Creator & Monetarisierung

```plantuml
@startuml
!define primary_key(x) <b><color:#b8861b><&key></color> x</b>
!define foreign_key(x) <color:#aaaaaa><&key></color> x
!define column(x) <color:#efefef><&media-record></color> x
!define table(x) entity x << (T, white) >>

title Creator-Modell ER-Diagram

table(creator_profiles) {
  primary_key(creator_id) : UUID
  foreign_key(user_id) : UUID
  column(display_name) : VARCHAR(255)
  column(bio) : TEXT
  column(avatar_url) : TEXT
  column(website_url) : VARCHAR(255)
  column(social_links) : JSONB
  column(creator_level) : ENUM('beginner', 'verified', 'pro', 'master')
  column(total_courses) : INTEGER
  column(total_sales) : INTEGER
  column(total_revenue) : DECIMAL(12,2)
  column(average_rating) : FLOAT
  column(total_ratings) : INTEGER
  column(verified_at) : TIMESTAMP
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
}

table(marketplace_courses) {
  primary_key(marketplace_course_id) : UUID
  foreign_key(course_id) : UUID
  foreign_key(creator_id) : UUID
  column(title) : VARCHAR(255)
  column(description) : TEXT
  column(price) : DECIMAL(10,2)
  column(currency) : VARCHAR(3)
  column(is_published) : BOOLEAN
  column(is_global) : BOOLEAN
  column(available_languages) : JSONB
  column(total_sales) : INTEGER
  column(total_revenue) : DECIMAL(12,2)
  column(status) : ENUM('draft', 'review', 'published', 'suspended')
  column(quality_score) : FLOAT
  column(published_at) : TIMESTAMP
  column(created_at) : TIMESTAMP
  column(updated_at) : TIMESTAMP
}

table(course_sales) {
  primary_key(sale_id) : UUID
  foreign_key(marketplace_course_id) : UUID
  foreign_key(buyer_id) : UUID
  foreign_key(creator_id) : UUID
  column(price_paid) : DECIMAL(10,2)
  column(currency) : VARCHAR(3)
  column(platform_fee) : DECIMAL(10,2)
  column(creator_revenue) : DECIMAL(10,2)
  column(payment_method) : VARCHAR(50)
  column(stripe_payment_id) : VARCHAR(255)
  column(purchased_at) : TIMESTAMP
}

table(creator_payouts) {
  primary_key(payout_id) : UUID
  foreign_key(creator_id) : UUID
  column(amount) : DECIMAL(12,2)
  column(currency) : VARCHAR(3)
  column(period_start) : DATE
  column(period_end) : DATE
  column(status) : ENUM('pending', 'processing', 'paid', 'failed')
  column(stripe_payout_id) : VARCHAR(255)
  column(bank_account) : VARCHAR(255)
  column(paid_at) : TIMESTAMP
  column(created_at) : TIMESTAMP
}

table(creator_analytics) {
  primary_key(analytics_id) : UUID
  foreign_key(creator_id) : UUID
  foreign_key(marketplace_course_id) : UUID
  column(date) : DATE
  column(views) : INTEGER
  column(sales) : INTEGER
  column(revenue) : DECIMAL(10,2)
  column(conversion_rate) : FLOAT
  column(refunds) : INTEGER
  column(new_ratings) : INTEGER
  column(avg_completion_rate) : FLOAT
}

table(global_translations) {
  primary_key(translation_id) : UUID
  foreign_key(marketplace_course_id) : UUID
  column(language_code) : VARCHAR(10)
  column(translated_title) : VARCHAR(255)
  column(translated_description) : TEXT
  column(translation_status) : ENUM('pending', 'in_progress', 'completed', 'failed')
  column(ai_confidence) : FLOAT
  column(translated_at) : TIMESTAMP
}

table(creator_verifications) {
  primary_key(verification_id) : UUID
  foreign_key(creator_id) : UUID
  foreign_key(verified_by) : UUID
  column(verification_type) : ENUM('identity', 'quality', 'tax')
  column(status) : ENUM('pending', 'approved', 'rejected')
  column(notes) : TEXT
  column(verified_at) : TIMESTAMP
}

' Relationships
creator_profiles ||--o{ marketplace_courses : "creates"
creator_profiles ||--o{ course_sales : "earns from"
creator_profiles ||--o{ creator_payouts : "receives"
creator_profiles ||--o{ creator_analytics : "tracked by"
creator_profiles ||--o{ creator_verifications : "verified by"

marketplace_courses ||--o{ course_sales : "sold as"
marketplace_courses ||--o{ creator_analytics : "analyzed"
marketplace_courses ||--o{ global_translations : "translated to"

course_sales ||--|| creator_payouts : "included in"

@enduml
```

---

## 1. Zielgruppe des Creator-Modells

### Zielgruppen-Segmentierung

```plantuml
@startuml
title Creator Zielgruppen

package "Creator-Typen" {
  [Kursautoren] as authors #LightBlue
  [Freiberufliche Dozenten] as freelance #LightGreen
  [Coaches] as coaches #Gold
  [IT-Experten] as it_experts #LightCoral
  [BWL-Experten] as bwl #Purple
  [Sprach-Lehrer] as language #LightYellow
  [Content-Producer] as producers #Orange
}

actor "Creator" as creator #LightBlue

authors --> creator
freelance --> creator
coaches --> creator
it_experts --> creator
bwl --> creator
language --> creator
producers --> creator

note right of creator
  ✅ Expertise in Fachgebiet
  ✅ Content-Erstellung
  ✅ Business-Mindset
  ✅ Globale Reichweite
  ❌ NICHT: Schulen/Unternehmen
end note

@enduml
```

### Creator-Persona-Tabelle

| Persona | Hintergrund | Motivation | Hauptnutzen | Typischer Use-Case |
|---------|-------------|------------|-------------|---------------------|
| **IT-Experte** | Software-Entwickler, DevOps | Wissen teilen, passives Einkommen | Global Publishing, KI-Tools | "Python für Data Science", "Docker Mastery" |
| **Freiberuflicher Dozent** | Erfahrener Trainer | Skalierung ohne Zeitlimit | 75% Revenue, keine Overhead-Kosten | "Projektmanagement", "Agile Methoden" |
| **Coach** | Business/Life Coach | Digitales Produkt | Automatisierung, passive Einnahmen | "Leadership Skills", "Mindfulness" |
| **Sprachlehrer** | Native Speaker, Polyglott | Weltweite Schüler | Multi-Language-Support | "Business Englisch", "Spanisch für Anfänger" |
| **Content-Producer** | Influencer, YouTuber | Audience monetarisieren | Integration mit bestehenden Kanälen | "Video Editing", "Social Media Marketing" |

---

## 2. Creator-Funktionen (Detailliert)

### Feature-Übersicht

```plantuml
@startuml
!include <C4/C4_Component>

title Creator Feature-Set

Container_Boundary(creator_features, "Creator Features") {
  Component(course_editor, "Advanced Course Editor", "Vue.js", "19 Content-LMs (A-C) + Pro")
  Component(ai_tools, "KI-Tools", "Python/AI", "Generierung & Optimierung")
  Component(global_pub, "Global Publishing", "Python", "20 Sprachen")
  Component(monetization, "Monetarisierung", "Python", "Marketplace & Revenue")
  Component(analytics, "Creator Analytics", "Python/Pandas", "Performance-Tracking")
  Component(branding, "Branding", "Vue.js", "Profilseite & Portfolio")
}

System_Ext(ai_pipeline, "KI-Pipeline", "13 AI-Module")
System_Ext(translation_api, "Übersetzungs-API", "DeepL/GPT")
System_Ext(payment_system, "Payment System", "Stripe")

Rel(course_editor, ai_tools, "Nutzt KI")
Rel(ai_tools, ai_pipeline, "Verwendet")
Rel(global_pub, translation_api, "Übersetzt")
Rel(monetization, payment_system, "Verarbeitet Zahlungen")

@enduml
```

### 🔵 Kompletter Kurseditor

| Feature | Beschreibung | Premium | Creator |
|---------|--------------|---------|---------|
| **Gruppe A+B (LM00–LM17)** | Erklärende + Praxis-Methoden | ✅ Erstellen | ✅ Erstellen |
| **Gruppe C (LM18–LM25)** | Prüfungsorientierte Methoden | ✅ Privat | ✅ Verkaufen |
| **Gruppe D (LM26–LM31)** | Pro/Gamification (Case Studies, etc.) | ❌ | ✅ Erstellen |
| **KI-Unterstützung** | Generierung, Optimierung | ✅ | ✅ Enhanced |
| **Theorieblätter-Generator** | Automatisch generiert | ✅ | ✅ |
| **Modul-Templates** | Vordefinierte Strukturen | ❌ | ✅ |
| **Bulk-Operations** | Mehrere Module gleichzeitig | ❌ | ✅ |

### 🔵 Global Publishing (20 Sprachen)

| Sprache | ISO-Code | Marktgröße | Priorität |
|---------|----------|------------|-----------|
| Deutsch | de | 100M | Hoch |
| Englisch | en | 1.5B | Sehr Hoch |
| Spanisch | es | 500M | Hoch |
| Französisch | fr | 300M | Hoch |
| Italienisch | it | 70M | Mittel |
| Portugiesisch | pt | 260M | Hoch |
| Russisch | ru | 260M | Mittel |
| Chinesisch | zh | 1.3B | Sehr Hoch |
| Japanisch | ja | 130M | Mittel |
| Koreanisch | ko | 80M | Mittel |
| Arabisch | ar | 420M | Mittel |
| Türkisch | tr | 80M | Niedrig |
| Polnisch | pl | 40M | Niedrig |
| Niederländisch | nl | 25M | Niedrig |
| Schwedisch | sv | 10M | Niedrig |
| Norwegisch | no | 5M | Niedrig |
| Dänisch | da | 6M | Niedrig |
| Finnisch | fi | 5M | Niedrig |
| Griechisch | el | 13M | Niedrig |
| Hindi | hi | 600M | Hoch |

**Hinweis:** Übersetzung erfolgt automatisch und kostenlos für Creator.

### 🔵 Monetarisierung

```plantuml
@startuml
title Creator Monetarisierungs-Flow

actor Creator
participant "Marketplace" as marketplace
participant "Stripe" as stripe
database "Sales DB" as sales
participant "Payout Service" as payout
participant "Bank Account" as bank

Creator -> marketplace : Publiziert Kurs (49,99 €)
activate marketplace

marketplace -> marketplace : Setzt Status = 'published'

note right of marketplace
  Kurs ist jetzt kaufbar
end note

== Kauf durch User ==

actor Buyer
Buyer -> marketplace : Kauft Kurs (49,99 €)
marketplace -> stripe : Create Payment Intent
activate stripe

stripe --> Buyer : Zahlung erfolgreich
stripe -> marketplace : Webhook: payment_intent.succeeded
deactivate stripe

marketplace -> sales : INSERT INTO course_sales\n(price=49.99, platform_fee=12.50, creator_revenue=37.49)
activate sales
sales --> marketplace : sale_id
deactivate sales

marketplace --> Creator : Echtzeit-Benachrichtigung: "+37,49 €"
deactivate marketplace

== Monatliche Auszahlung ==

payout -> sales : SELECT SUM(creator_revenue)\nWHERE creator_id = ? AND payout_id IS NULL
activate sales
sales --> payout : total_revenue = 1.247,35 €
deactivate sales

payout -> stripe : Create Payout (1.247,35 €)
activate stripe
stripe -> bank : Banküberweisung
stripe --> payout : payout_id
deactivate stripe

payout -> sales : UPDATE course_sales SET payout_id = ?
activate sales
sales --> payout : OK
deactivate sales

payout --> Creator : Email: "Auszahlung 1.247,35 € erfolgt"

@enduml
```

### Revenue Share Breakdown

| Verkaufspreis | Platform Fee (25%) | Creator Revenue (75%) |
|---------------|--------------------|-----------------------|
| 9,99 € | 2,50 € | 7,49 € |
| 19,99 € | 5,00 € | 14,99 € |
| 29,99 € | 7,50 € | 22,49 € |
| 49,99 € | 12,50 € | 37,49 € |
| 99,99 € | 25,00 € | 74,99 € |
| 199,99 € | 50,00 € | 149,99 € |
| 299,99 € | 75,00 € | 224,99 € |

**Platform Fee deckt ab:**
- Hosting & Infrastruktur
- KI-Kosten (Übersetzung, Content-Generierung)
- Zahlungsabwicklung (Stripe-Gebühren)
- Marketing & SEO
- Support
- Qualitätskontrolle

---

## 3. Creator vs. Premium (Detaillierter Vergleich)

### Funktionsvergleich

| Funktion | Premium | Creator | Delta |
|----------|---------|---------|-------|
| **Abo-Preis** | 14,99 € / Monat | 29,99 € / Monat | +15 € |
| **Tokens/Monat** | 10.000 | 20.000 | +10.000 |
| **Kurse erstellen** | ✅ Privat & Community | ✅ Alle Typen | Erweitert |
| **Gruppe D-Methoden erstellen** | ❌ | ✅ | Exklusiv |
| **Kurse verkaufen** | ❌ | ✅ | Monetarisierung |
| **Revenue Share** | - | 75% | Einnahmen |
| **Global Publishing** | ❌ | ✅ 20 Sprachen | Reichweite |
| **Creator Analytics** | ❌ | ✅ | Business-Insights |
| **Creator-Profilseite** | ❌ | ✅ | Branding |
| **Pricing-Control** | - | ✅ | Preisgestaltung |
| **Bulk-Operations** | ❌ | ✅ | Effizienz |
| **Verified Badge** | ❌ | ✅ | Trust Signal |

### Upgrade-Journey

```plantuml
@startuml
title Premium to Creator Upgrade Journey

|Premium User|
start
:Erstellt Community-Kurse (kostenlos);
:Erhält positives Feedback;
:Möchte monetarisieren;

if (Bereit für Business?) then (ja)
  :Sieht "Upgrade to Creator"-Banner;
  :Klickt auf Upgrade;

  |System|
  :Zeigt Creator-Benefits;
  :Zeigt Pricing (29,99 € / Monat);
  :Zeigt ROI-Calculator;

  note right
    ROI-Calculator:
    - Verkaufe 10 Kurse/Monat à 49,99 €
    - Verdiene: 374,90 €
    - Kosten: 29,99 €
    - Netto: 344,91 €/Monat
  end note

  |Premium User|
  if (Überzeugt?) then (ja)
    :Zahlt 29,99 € / Monat;

    |System|
    :Upgraded zu Creator;
    :Schaltet Creator-Features frei;
    :Erhöht Token auf 20.000/Monat;
    :Erstellt Creator-Profil;
    :Aktiviert Marketplace-Zugang;

    |Creator|
    :Publiziert ersten Marketplace-Kurs;
    :Verdient erste Einnahmen;
    stop
  else (nein)
    :Bleibt Premium;
    stop
  endif
else (nein)
  :Bleibt Premium;
  :Veröffentlicht weiter kostenlos;
  stop
endif

@enduml
```

---

## 4. Arten von Creator-Kursen

### Kursarten-Übersicht

```plantuml
@startuml
title Creator-Kursarten

package "Creator kann erstellen" {
  [Community-Kurs (kostenlos)] as community #LightGreen
  [Marketplace-Kurs (bezahlt)] as marketplace #Gold
  [Private Creator-Kurse] as private #LightBlue
  [Beta-Kurse] as beta #Purple
}

actor "Creator" as creator #LightBlue
actor "Community" as users #LightGray
actor "Käufer" as buyer #Gold

creator --> community : Veröffentlicht kostenlos
creator --> marketplace : Verkauft (9,99 € - 299,99 €)
creator --> private : Intern/später öffentlich
creator --> beta : Frühe Version

users --> community : Nutzt kostenlos
buyer --> marketplace : Kauft
buyer --> beta : Testet & Feedback

note right of marketplace
  ✅ 75% Revenue Share
  ✅ Global Publishing
  ✅ Creator-Analytics
  ✅ Preis frei wählbar
end note

@enduml
```

### Kursarten-Details

#### 4.1 Community-Kurs (kostenlos)

| Eigenschaft | Details |
|-------------|---------|
| **Preis** | Kostenlos |
| **Sichtbarkeit** | Öffentlich |
| **Methoden** | Alle 19 Content-LMs (A-C) |
| **Global Publishing** | ✅ Optional |
| **Zweck** | Marketing, Portfolio, Community-Building |
| **Analytics** | Basic (Views, Enrollments, Ratings) |
| **Monetarisierung** | Indirekt (Lead-Generierung) |

#### 4.2 Marketplace-Kurs (kostenpflichtig)

| Eigenschaft | Details |
|-------------|---------|
| **Preis** | 9,99 € - 299,99 € (Creator wählt) |
| **Revenue Share** | 75% an Creator |
| **Sichtbarkeit** | Weltweit (20 Sprachen) |
| **Methoden** | Alle 19 Content-LMs (A-C) |
| **Global Publishing** | ✅ Empfohlen |
| **Analytics** | Advanced (Sales, Revenue, Conversion, Retention) |
| **Auszahlung** | Monatlich via Stripe |

#### 4.3 Private Creator-Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Preis** | Intern |
| **Sichtbarkeit** | Privat |
| **Zweck** | Entwürfe, Experimente, später öffentlich |
| **Methoden** | Alle 19 Content-LMs (A-C) |

#### 4.4 Beta-Kurse

| Eigenschaft | Details |
|-------------|---------|
| **Preis** | Reduziert (z.B. 50% Rabatt) |
| **Status** | "Beta" Badge |
| **Zweck** | Feedback sammeln, iterativ verbessern |
| **Vorteil für Käufer** | Günstiger Preis, Early Access |
| **Vorteil für Creator** | Qualitätsverbesserung, Marketing |

---

## 5. Global Publishing Prozess

### Publishing-Workflow

```plantuml
@startuml
title Global Publishing Workflow

actor Creator
participant "Course Editor" as editor
participant "Global Publisher" as publisher
participant "KI-Übersetzung" as ai_translation
participant "Quality Checker" as quality
database "Translation DB" as trans_db
participant "Marketplace" as marketplace

Creator -> editor : Klickt "Global Publish"
activate editor

editor -> publisher : POST /api/courses/:id/publish-global
activate publisher

publisher -> quality : Prüfe Kurs-Qualität
activate quality

quality -> quality : Check Struktur, Vollständigkeit
quality --> publisher : quality_score = 4.2 (OK)
deactivate quality

publisher -> ai_translation : Übersetze in 20 Sprachen
activate ai_translation

loop For each language (20 Sprachen)
  ai_translation -> ai_translation : Übersetze:\n- Titel\n- Beschreibung\n- Theorieblätter\n- Lernmethoden\n- Prüfungen

  ai_translation -> trans_db : INSERT INTO global_translations
  activate trans_db
  trans_db --> ai_translation : translation_id
  deactivate trans_db
end

ai_translation --> publisher : Alle Übersetzungen fertig
deactivate ai_translation

publisher -> marketplace : Publiziere in allen Sprachen
activate marketplace

marketplace -> marketplace : Kurs weltweit sichtbar

marketplace --> Creator : "Kurs in 20 Sprachen veröffentlicht!"
deactivate marketplace
deactivate publisher
deactivate editor

@enduml
```

### Übersetzungs-Qualität

| Element | KI-Übersetzung | Manuelle Review | Ergebnis |
|---------|----------------|-----------------|----------|
| **Titel** | ✅ Automatisch | Optional | 95% Qualität |
| **Beschreibung** | ✅ Automatisch | Optional | 95% Qualität |
| **Theorieblätter** | ✅ Automatisch | Empfohlen | 90% Qualität |
| **Lernmethoden** | ✅ Automatisch | Empfohlen | 90% Qualität |
| **Quiz-Fragen** | ✅ Automatisch | Empfohlen | 85% Qualität |
| **Videos (Untertitel)** | ✅ Automatisch | Empfohlen | 85% Qualität |

**Hinweis:** Creator kann jede Übersetzung manuell nachbearbeiten.

---

## 6. Monetarisierung & Einnahmen

### Pricing-Strategie

```plantuml
@startuml
title Creator Pricing-Strategie

actor Creator
participant "Pricing Tool" as pricing
participant "AI Recommender" as ai_rec
database "Market Data" as market

Creator -> pricing : Erstellt neuen Marketplace-Kurs
activate pricing

pricing -> ai_rec : Empfehle Preis
activate ai_rec

ai_rec -> market : Analysiere:\n- Kurslänge\n- Anzahl Module\n- Lernmethoden-Mix\n- Qualitätsscore\n- Kategorie\n- Wettbewerber-Preise
activate market
market --> ai_rec : Marktdaten
deactivate market

ai_rec -> ai_rec : Berechne optimalen Preis

ai_rec --> pricing : Empfohlener Preis: 49,99 €\nRange: 39,99 € - 59,99 €
deactivate ai_rec

pricing --> Creator : Zeigt Empfehlung
deactivate pricing

Creator -> pricing : Wählt Preis: 49,99 €
activate pricing
pricing --> Creator : Preis gesetzt
deactivate pricing

@enduml
```

### Revenue-Modell

```plantuml
@startuml
title Creator Revenue-Flow

database "Course Sales" as sales
participant "Revenue Tracker" as revenue
database "Creator Earnings" as earnings
participant "Payout Service" as payout
participant "Stripe" as stripe
participant "Creator Bank" as bank

sales -> revenue : New Sale: 49,99 €
activate revenue

revenue -> revenue : Calculate:\nPlatform Fee: 12,50 € (25%)\nCreator Revenue: 37,49 € (75%)

revenue -> earnings : UPDATE creator_earnings\nSET total_revenue += 37.49
activate earnings
earnings --> revenue : OK
deactivate earnings

revenue --> sales : Revenue tracked
deactivate revenue

== Monatliche Auszahlung ==

payout -> earnings : SELECT SUM(unpaid_revenue)
activate earnings
earnings --> payout : total_unpaid = 1.247,35 €
deactivate earnings

alt Mindestbetrag erreicht (>= 50 €)
  payout -> stripe : Create Payout (1.247,35 €)
  activate stripe

  stripe -> bank : Banküberweisung
  stripe --> payout : payout_succeeded
  deactivate stripe

  payout -> earnings : Mark as paid
  activate earnings
  earnings --> payout : OK
  deactivate earnings

  payout -> Creator : Email: "Auszahlung 1.247,35 € erfolgt"
else (< 50 €)
  payout -> Creator : Email: "Auszahlung verschoben (Minimum 50 €)"
end

@enduml
```

### Einnahmen-Dashboard

| Metrik | Beschreibung | Berechnung |
|--------|--------------|------------|
| **Total Revenue** | Gesamteinnahmen (alle Zeiten) | SUM(creator_revenue) |
| **Monthly Revenue** | Einnahmen diesen Monat | SUM(creator_revenue WHERE month = current) |
| **Avg. Sale Price** | Durchschnittlicher Verkaufspreis | AVG(price_paid) |
| **Total Sales** | Anzahl Verkäufe | COUNT(sale_id) |
| **Conversion Rate** | Verkäufe / Views | (sales / views) * 100 |
| **Top Course** | Best-Seller | Course mit höchstem Revenue |
| **Pending Payout** | Noch nicht ausgezahlt | SUM(unpaid_revenue) |
| **Next Payout Date** | Nächste Auszahlung | 1. des Folgemonats |

---

## 7. Creator-Tools

### KI-Tools für Creator

```plantuml
@startuml
!include <C4/C4_Component>

title Creator KI-Tools

Container_Boundary(ai_tools, "Creator KI-Tools") {
  Component(module_gen, "KI-Modulerstellung", "Python/AI", "Automatische Modul-Generierung")
  Component(summary_gen, "KI-Kurszusammenfassung", "Python/AI", "Automatische Zusammenfassungen")
  Component(optimizer, "KI-Verbesserung", "Python/AI", "Content-Optimierung")
  Component(exam_gen, "KI-Prüfungsgenerator", "Python/AI", "Prüfungen erstellen")
  Component(lang_opt, "KI-Sprachoptimierung", "Python/AI", "Grammatik & Stil")
  Component(glossary_gen, "KI-Glossar-Generator", "Python/AI", "Fachbegriffe automatisch")
  Component(story_gen, "KI-Storytelling", "Python/AI", "Geschichten für Lerninhalte")
  Component(case_gen, "KI-Fallstudien", "Python/AI", "Realistische Case Studies")
}

System_Ext(ai_pipeline, "KI-Pipeline", "13 AI-Module")
System_Ext(token_system, "Token-System", "Verbrauchskontrolle")

Rel(module_gen, ai_pipeline, "Nutzt AI-Module")
Rel(summary_gen, ai_pipeline, "Nutzt AI-Module")
Rel(optimizer, ai_pipeline, "Nutzt AI-Module")
Rel(exam_gen, ai_pipeline, "Nutzt AI-Module")
Rel(lang_opt, ai_pipeline, "Nutzt AI-Module")
Rel(glossary_gen, ai_pipeline, "Nutzt AI-Module")
Rel(story_gen, ai_pipeline, "Nutzt AI-Module")
Rel(case_gen, ai_pipeline, "Nutzt AI-Module")

Rel(module_gen, token_system, "Verbraucht Tokens")

@enduml
```

### KI-Tool-Verbrauch (Tokens)

| KI-Tool | Token-Kosten | Typische Nutzung | Tokens/Kurs |
|---------|--------------|------------------|-------------|
| **KI-Modulerstellung** | 2.000-5.000 | 10 Module | 20.000-50.000 |
| **KI-Kurszusammenfassung** | 1.000-2.000 | 1x pro Kurs | 1.000-2.000 |
| **KI-Verbesserung** | 500-1.500 | 5 Module | 2.500-7.500 |
| **KI-Prüfungsgenerator** | 3.000-8.000 | 2 Prüfungen | 6.000-16.000 |
| **KI-Sprachoptimierung** | 300-800 | 10 Texte | 3.000-8.000 |
| **KI-Glossar-Generator** | 500-1.000 | 1x pro Kurs | 500-1.000 |
| **KI-Storytelling** | 800-2.000 | 3 Geschichten | 2.400-6.000 |
| **KI-Fallstudien** | 2.000-5.000 | 2 Case Studies | 4.000-10.000 |

**Total für einen vollständigen Kurs:** 39.400-100.500 Tokens

**Creator-Abo:** 20.000 Tokens/Monat → Zusatzkauf empfohlen für größere Kurse

---

## 8. Creator-Level-System

### Level-Progression

```plantuml
@startuml
title Creator Level-Progression

state "Beginner Creator" as level1 #LightGray
state "Verified Creator" as level2 #LightGreen
state "Pro Creator" as level3 #Gold
state "LSX Master Creator" as level4 #Purple

[*] --> level1 : Registrierung

level1 --> level2 : Kriterien:\n- Min. 3 Kurse\n- Avg. Rating >= 4.5\n- Admin-Verifikation

level2 --> level3 : Kriterien:\n- Min. 10 Kurse\n- Min. 100 Sales\n- Total Revenue > 5.000 €\n- Avg. Rating >= 4.7

level3 --> level4 : Kriterien:\n- Min. 25 Kurse\n- Min. 1.000 Sales\n- Total Revenue > 50.000 €\n- Avg. Rating >= 4.8\n- LSX-Partnerschaft

note right of level1
  ✅ Grundfunktionen
  ❌ Kein Badge
  ❌ Keine Bevorzugung
end note

note right of level2
  ✅ "Verified" Badge
  ✅ Bevorzugtes Ranking
  ✅ Support-Priorität
end note

note right of level3
  ✅ "Pro Creator" Badge
  ✅ Top-Ranking
  ✅ Featured in LSX-Marketing
  ✅ Early Access zu Beta-Features
end note

note right of level4
  ✅ "LSX Master" Badge
  ✅ Co-Marketing mit LSX
  ✅ Custom Revenue Share (80%)
  ✅ Exklusive Features
end note

@enduml
```

### Level-Kriterien-Tabelle

| Level | Kurse | Sales | Revenue | Avg. Rating | Besonderheiten |
|-------|-------|-------|---------|-------------|----------------|
| **Beginner** | 0-2 | 0-49 | < 1.000 € | Beliebig | Grundfunktionen |
| **Verified** | 3+ | 50+ | 1.000-5.000 € | >= 4.5 | Admin-Verifikation, "Verified" Badge |
| **Pro** | 10+ | 100+ | 5.000-50.000 € | >= 4.7 | Top-Ranking, Featured |
| **Master** | 25+ | 1.000+ | > 50.000 € | >= 4.8 | Custom Revenue Share (80%), Co-Marketing |

---

## 9. Qualitätskontrolle

### Quality-Check-Workflow

```plantuml
@startuml
title Creator-Kurs Qualitätsprüfung

actor Creator
participant "Course Submission" as submission
participant "AI Quality Checker" as ai_quality
participant "Moderation Queue" as moderation
participant "Admin Review" as admin
database "Course DB" as db

Creator -> submission : Publiziert Marketplace-Kurs
activate submission

submission -> ai_quality : Prüfe Qualität
activate ai_quality

ai_quality -> ai_quality : Analysiere:\n- Struktur\n- Verständlichkeit\n- Vollständigkeit\n- Plagiat\n- Copyright

alt Quality Score >= 4.0
  ai_quality --> submission : quality_score = 4.2\nSTATUS: APPROVED
  deactivate ai_quality

  submission -> db : UPDATE marketplace_courses\nSET status = 'published', quality_score = 4.2
  activate db
  db --> submission : OK
  deactivate db

  submission --> Creator : "Kurs veröffentlicht!"
  deactivate submission

else Quality Score < 4.0
  ai_quality --> submission : quality_score = 2.8\nSTATUS: NEEDS_REVIEW
  deactivate ai_quality

  submission -> moderation : Add to Queue (MEDIUM Priority)
  activate moderation
  moderation --> submission : queued
  deactivate moderation

  submission -> db : UPDATE marketplace_courses\nSET status = 'review'
  activate db
  db --> submission : OK
  deactivate db

  submission --> Creator : "Kurs wird geprüft"
  deactivate submission

  == Manual Review ==

  admin -> moderation : Öffnet Queue
  activate admin

  admin -> admin : Prüft Kurs manuell

  alt Qualität OK
    admin -> db : UPDATE marketplace_courses\nSET status = 'published'
    admin --> Creator : "Kurs freigegeben"
  else Qualität mangelhaft
    admin -> db : UPDATE marketplace_courses\nSET status = 'rejected'
    admin --> Creator : "Kurs abgelehnt\nGründe: ..."
  end

  deactivate admin
end

@enduml
```

### Quality-Kriterien

| Kriterium | Gewichtung | Bewertung |
|-----------|------------|-----------|
| **Struktur** | 20% | Klare Gliederung, logischer Aufbau |
| **Verständlichkeit** | 25% | Sprache, Erklärungen, Beispiele |
| **Vollständigkeit** | 15% | Alle Themen abgedeckt |
| **Lernmethoden-Mix** | 15% | Vielfältige Methoden genutzt |
| **Theoriequalität** | 15% | Korrektheit, Tiefe |
| **Kein Plagiat** | 10% | Originalität |

**Mindest-Score für Auto-Approval:** 4.0 / 5.0

---

## 10. Creator-Analytics

### Analytics-Dashboard

```plantuml
@startuml
!include <C4/C4_Component>

title Creator Analytics Dashboard

Container_Boundary(creator_analytics, "Creator Analytics") {
  Component(revenue_charts, "Revenue-Charts", "Chart.js", "Einnahmen-Visualisierung")
  Component(sales_funnel, "Sales-Funnel", "Python", "Conversion-Tracking")
  Component(course_performance, "Course-Performance", "Python/Pandas", "Pro-Kurs-Metriken")
  Component(student_insights, "Student-Insights", "Python", "Lernenden-Verhalten")
  Component(rating_analysis, "Rating-Analyse", "Python/NLP", "Sentiment-Analyse")
  Component(comparison, "Markt-Vergleich", "Python", "Benchmarking")
}

Database(analytics_db, "Analytics DB", "PostgreSQL")
System_Ext(ai_insights, "AI-Insights", "Verbesserungsvorschläge")

Rel(revenue_charts, analytics_db, "Liest Revenue")
Rel(sales_funnel, analytics_db, "Liest Conversion")
Rel(course_performance, analytics_db, "Liest Performance")
Rel(student_insights, analytics_db, "Liest User-Daten")
Rel(rating_analysis, analytics_db, "Liest Reviews")
Rel(comparison, analytics_db, "Liest Marktdaten")

Rel(rating_analysis, ai_insights, "Nutzt AI für Sentiment")

@enduml
```

### Key Metriken

| Metrik | Beschreibung | Visualisierung |
|--------|--------------|----------------|
| **Total Revenue** | Gesamteinnahmen | Number + Trend |
| **Monthly Revenue** | Monatliche Einnahmen | Line Chart |
| **Sales Funnel** | Views → Enrollments → Purchases | Funnel Chart |
| **Conversion Rate** | (Sales / Views) * 100 | Percentage + Trend |
| **Avg. Rating** | Durchschnittsbewertung | Star Rating + Distribution |
| **Completion Rate** | Abschlussquote pro Kurs | Percentage + Bar Chart |
| **Student Retention** | Wiederkehrende Käufer | Percentage |
| **Top Courses** | Best-Seller | Table |
| **Revenue by Language** | Einnahmen pro Sprache | Pie Chart |
| **Growth Rate** | MoM Revenue-Wachstum | Percentage |

---

## 11. API-Endpoints

### Creator-API

| Endpoint | Methode | Beschreibung | Auth | Rolle |
|----------|---------|--------------|------|-------|
| `/api/creator/profile` | GET | Creator-Profil abrufen | ✅ | Creator |
| `/api/creator/profile` | PUT | Profil aktualisieren | ✅ | Creator |
| `/api/creator/courses` | GET | Alle Creator-Kurse | ✅ | Creator |
| `/api/creator/courses/:id/publish` | POST | Kurs publizieren | ✅ | Creator |
| `/api/creator/courses/:id/publish-global` | POST | Global Publishing | ✅ | Creator |
| `/api/creator/analytics/:course_id` | GET | Kurs-Analytics | ✅ | Creator |
| `/api/creator/revenue` | GET | Einnahmen-Übersicht | ✅ | Creator |
| `/api/creator/payouts` | GET | Auszahlungshistorie | ✅ | Creator |
| `/api/creator/pricing/recommend` | POST | KI-Preisempfehlung | ✅ | Creator |
| `/api/creator/translations/:course_id` | GET | Übersetzungsstatus | ✅ | Creator |
| `/api/creator/verify` | POST | Verifikation beantragen | ✅ | Creator |

### Beispiel-Request: Global Publishing

```http
POST /api/creator/courses/c1a2b3c4/publish-global
Authorization: Bearer <creator_token>
Content-Type: application/json

{
  "target_languages": ["en", "es", "fr", "it", "pt", "zh"],
  "auto_translate": true,
  "manual_review_required": false
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "course_id": "c1a2b3c4",
    "publishing_job_id": "job_9x8y7z",
    "target_languages": ["en", "es", "fr", "it", "pt", "zh"],
    "estimated_completion": "2024-03-15T14:30:00Z",
    "translations": [
      {
        "language": "en",
        "status": "in_progress",
        "progress": 0
      },
      {
        "language": "es",
        "status": "pending",
        "progress": 0
      }
    ]
  },
  "message": "Global Publishing gestartet. Du erhältst eine Benachrichtigung, sobald alle Übersetzungen fertig sind."
}
```

---

## 12. Zusammenfassung

### ✅ Creator-Kernwerte

| Aspekt | Details |
|--------|---------|
| **Abo-Preis** | 29,99 € / Monat |
| **Tokens/Monat** | 20.000 |
| **Revenue Share** | 75% an Creator |
| **Auszahlung** | Monatlich via Stripe (Minimum 50 €) |
| **Global Publishing** | 20 Sprachen kostenlos |
| **Lernmethoden** | Alle 19 Content-LMs (A-C) |
| **Kurstypen** | Community, Marketplace, Privat, Beta |
| **Analytics** | Vollständig (Revenue, Sales, Conversion, Retention) |
| **Branding** | Creator-Profilseite, Verified Badge |
| **Support** | Priority (für Verified+) |

### 🎯 Design-Prinzipien

- **Fair für Creator:** 75% Revenue Share ist marktführend
- **Global Reach:** 20 Sprachen ohne Zusatzkosten
- **KI-First:** Alle Tools KI-gestützt
- **Quality über Quantity:** Level-System belohnt Qualität
- **Transparent:** Echtzeit-Einnahmen, klare Metriken
- **Skalierbar:** Business-Tools für professionelle Creator
- **Community-Driven:** Creator können auch kostenlos publizieren

---

## 📌 Dokument abgeschlossen

**Version:** 1.0
**Status:** Final
**Letzte Aktualisierung:** 2024

---

> 💡 **Hinweis:** Das Creator-Modell ist das wirtschaftliche Herzstück von LSX und ermöglicht es Experten weltweit, Wissen zu monetarisieren und gleichzeitig Lernenden Zugang zu hochwertigen Inhalten zu bieten.
