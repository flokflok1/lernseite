# 20 – Internationalisierung & Lokalisierung (Final)

**Version:** 1.0  
**Stand:** Final

---

## Überblick

Dieses Dokument beschreibt das vollständige **Internationalisierungs- (i18n)** und **Lokalisierungssystem (L10n)** des LSX Lernsystems.

Die Internationalisierung ist **zentral**, da LSX **global nutzbar** sein soll, inklusive **automatischer KI-Übersetzungen** für Kurse.

---

## 1. Ziele der Internationalisierung

### ✅ i18n System Ziele

| Ziel | Umsetzung |
|------|-----------|
| 🌍 **Vollständige UI-Übersetzung** | vue-i18n mit JSON-Dateien |
| 📚 **Content-Übersetzung** | KI-gestützte Übersetzungen |
| ✨ **Global Publishing** | Creator können weltweit publishen |
| 🔄 **Echtzeit-Sprachwechsel** | Ohne Page Reload |
| 🔍 **Auto-Detection** | Browser-Sprache erkennen |
| 📅 **Lokalisierung** | Datum, Zeit, Zahlen formatieren |
| 🤖 **KI-Übersetzung** | Anthropic/OpenAI Integration |
| ♿ **Barrierefreiheit** | Vereinfachte Sprachen, ADHD-Modus |

---

## 2. i18n System Architecture (C4 Model)

### 🌍 Internationalization System Context

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

Person(user_de, "Deutscher User", "Nutzer aus DE")
Person(user_pl, "Polnischer User", "Nutzer aus PL")
Person(creator, "Creator", "Erstellt mehrsprachige Kurse")

System_Boundary(i18n, "i18n System") {
    Container(ui_i18n, "UI i18n", "vue-i18n", "Statische UI-Texte")
    Container(content_i18n, "Content i18n", "PostgreSQL", "Dynamische Inhalte")
    Container(translation_engine, "Translation Engine", "KI", "Automatische Übersetzung")
    Container(locale_service, "Locale Service", "JavaScript", "Formatierung")
}

System_Ext(ki_api, "KI APIs", "Anthropic/OpenAI")

Rel(user_de, ui_i18n, "Browser: de", "HTTPS")
Rel(user_pl, ui_i18n, "Browser: pl", "HTTPS")

Rel(ui_i18n, content_i18n, "Lädt Content", "API")
Rel(creator, translation_engine, "Global Publishing", "API")
Rel(translation_engine, ki_api, "Übersetzt", "HTTPS")
Rel(translation_engine, content_i18n, "Speichert", "SQL")
Rel(ui_i18n, locale_service, "Formatiert", "JS")

note right of translation_engine
  Automatische Übersetzung:
  - Kurse
  - Module
  - Methoden
  - Prüfungen
end note

@enduml
```

---

### 🧩 i18n Components

```plantuml
@startuml
package "Frontend i18n" {
  component "vue-i18n" {
    [Language Detector]
    [Translation Loader]
    [Formatter]
  }
  
  component "Static Translations" {
    file "de.json"
    file "en.json"
    file "pl.json"
  }
}

package "Backend i18n" {
  component "Translation Service" {
    [Content Translator]
    [Cache Manager]
    [Fallback Handler]
  }
  
  database "translations" {
    [content_type]
    [content_id]
    [language]
    [translated_json]
  }
}

package "KI Translation" {
  component "Translation Engine" {
    [Chunker]
    [Glossary Manager]
    [Consistency Checker]
  }
}

[Language Detector] --> [Translation Loader]
[Translation Loader] --> "de.json"
[Translation Loader] --> "en.json"
[vue-i18n] --> [Translation Service] : "API Call"
[Translation Service] --> translations : "liest"
[Translation Engine] --> translations : "schreibt"
[Translation Engine] --> [KI APIs] : "übersetzt"

@enduml
```

---

## 3. Unterstützte Sprachen

### 🌐 Language Support Matrix

```plantuml
@startuml
card "Standard-Sprachen (Always Active)" #E8F4F8 {
  :🇩🇪 Deutsch (de);
  :🇬🇧 Englisch (en);
  :🇵🇱 Polnisch (pl);
}

card "Erweiterbare Sprachen (Admin Activation)" #FFF4E1 {
  :🇫🇷 Französisch (fr);
  :🇪🇸 Spanisch (es);
  :🇮🇹 Italienisch (it);
  :🇳🇱 Niederländisch (nl);
  :🇸🇪 Schwedisch (sv);
  :🇳🇴 Norwegisch (no);
  :🇵🇹 Portugiesisch (pt);
  :🇹🇷 Türkisch (tr);
  :🇸🇦 Arabisch (ar);
  :🇯🇵 Japanisch (ja);
  :🇰🇷 Koreanisch (ko);
  :🇨🇳 Chinesisch (zh);
}

note bottom
  Alle Sprachen können
  per Admin-Panel
  aktiviert werden
end note
@enduml
```

---

### 📋 Sprachen-Übersicht

| Kategorie | Sprachen | Status |
|-----------|----------|--------|
| **Standard** | DE, EN, PL | ✅ Immer aktiv |
| **EU-West** | FR, ES, IT, NL | ⚠️ Admin-Aktivierung |
| **EU-Nord** | SV, NO | ⚠️ Admin-Aktivierung |
| **Global** | PT, TR | ⚠️ Admin-Aktivierung |
| **Asien** | JA, KO, ZH | ⚠️ Admin-Aktivierung |
| **MENA** | AR | ⚠️ Admin-Aktivierung + RTL |

---

## 4. Sprachlogik & Fallback

### 🔄 Language Detection & Fallback Flow

```plantuml
@startuml
|User Opens App|
start
:App startet;

|Language Detector|
:Prüfe Sprach-Priorität;

if (Manuell gewählt?) then (ja)
  :✅ Verwende gewählte Sprache;
  stop
endif

if (User eingeloggt?) then (ja)
  :Lade User Profile;
  if (Sprache gespeichert?) then (ja)
    :✅ Verwende Profil-Sprache;
    stop
  endif
endif

:Lese Browser-Sprache;
if (Unterstützte Sprache?) then (ja)
  :✅ Verwende Browser-Sprache;
else (nein)
  :⚠️ Fallback zu Englisch;
endif

stop

note right
  Priorität:
  1. Manuelle Wahl
  2. User Profil
  3. Browser
  4. Fallback (en)
end note
@enduml
```

---

### 🗂️ Content Fallback Strategy

```plantuml
@startuml
|Request Content|
start
:Request Course in (pl);

|Translation Service|
:Check translations table;

if (Polish translation exists?) then (ja)
  :✅ Return Polish content;
  stop
endif

:Check fallback languages;

if (English translation exists?) then (ja)
  :⚠️ Return English content;
  note right
    Zeige Hinweis:
    "Übersetzung nicht verfügbar"
  end note
  stop
endif

:Return original language;
stop
@enduml
```

---

## 5. Lokalisierung (L10n)

### 📅 Locale-specific Formatting

| Locale | Datum | Zahlen | Währung | Timezone |
|--------|-------|--------|---------|----------|
| 🇩🇪 **de** | DD.MM.YYYY | 1.234,56 | 1.234,56 € | Europe/Berlin |
| 🇬🇧 **en-GB** | DD/MM/YYYY | 1,234.56 | £1,234.56 | Europe/London |
| 🇺🇸 **en-US** | MM/DD/YYYY | 1,234.56 | $1,234.56 | America/New_York |
| 🇵🇱 **pl** | DD.MM.YYYY | 1 234,56 | 1 234,56 zł | Europe/Warsaw |
| 🇫🇷 **fr** | DD/MM/YYYY | 1 234,56 | 1 234,56 € | Europe/Paris |
| 🇯🇵 **ja** | YYYY/MM/DD | 1,234.56 | ¥1,235 | Asia/Tokyo |

---

### 💡 Locale Service Implementation

```javascript
// Locale Service
export class LocaleService {
  formatDate(date, locale) {
    const formats = {
      'de': 'DD.MM.YYYY',
      'en-US': 'MM/DD/YYYY',
      'en-GB': 'DD/MM/YYYY',
      'pl': 'DD.MM.YYYY'
    }
    return dayjs(date).locale(locale).format(formats[locale])
  }
  
  formatCurrency(amount, locale) {
    const currencies = {
      'de': { style: 'currency', currency: 'EUR' },
      'en-US': { style: 'currency', currency: 'USD' },
      'en-GB': { style: 'currency', currency: 'GBP' },
      'pl': { style: 'currency', currency: 'PLN' }
    }
    return new Intl.NumberFormat(locale, currencies[locale]).format(amount)
  }
  
  formatNumber(number, locale) {
    return new Intl.NumberFormat(locale).format(number)
  }
}
```

---

### ⏰ Timezone Management

```plantuml
@startuml
database "Database" as db
component "Backend" as backend
component "Frontend" as frontend
actor "User (Berlin)" as user

db -> backend : Stored in UTC
note right
  created_at: 2024-11-15T10:00:00Z
end note

backend -> frontend : Send UTC timestamp
frontend -> frontend : Detect User Timezone\n(Europe/Berlin)
frontend -> frontend : Convert to local time
frontend -> user : Display: 15.11.2024 11:00

note bottom
  - Speicherung: UTC
  - Übertragung: UTC
  - Anzeige: User Timezone
end note

@enduml
```

---

## 6. Global Publishing System

### ✨ Global Publishing Architecture

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container_Boundary(publishing, "Global Publishing System") {
    Component(creator_ui, "Creator UI", "Vue.js", "Global Publishing Button")
    Component(translation_service, "Translation Service", "Python", "Orchestriert Übersetzung")
    Component(chunker, "Chunker", "Python", "Teilt Content (2000 tokens)")
    Component(ki_translator, "KI Translator", "Anthropic/OpenAI", "Übersetzt Content")
    Component(validator, "Validator", "Python", "Prüft Übersetzung")
    Component(storage, "Translation Storage", "PostgreSQL", "Speichert Übersetzungen")
}

System_Ext(anthropic, "Anthropic API", "Claude 3.5/4.0")
System_Ext(openai, "OpenAI API", "GPT-4")

Rel(creator_ui, translation_service, "Start Translation")
Rel(translation_service, chunker, "Prepare Content")
Rel(chunker, ki_translator, "Send Chunks")
Rel(ki_translator, anthropic, "Translate")
Rel(ki_translator, openai, "Translate")
Rel(ki_translator, validator, "Validate Translation")
Rel(validator, storage, "Save Translation")

note right of ki_translator
  KI-Features:
  - Chunking (2000 tokens)
  - Glossar-Referenz
  - Markup-Preservation
  - Konsistenz-Check
end note

@enduml
```

---

### 🔄 Global Publishing Workflow

```plantuml
@startuml
|Creator|
start
:Erstellt Kurs (de);
:Klick "Global Publishing";

|UI|
:Zeige Sprach-Auswahl;

|Creator|
:Wählt Zielsprachen;
note right
  z.B. en, pl, fr, es
end note

|Translation Service|
:Erstelle Translation Job;
fork
  :Sprache 1 (en);
fork again
  :Sprache 2 (pl);
fork again
  :Sprache 3 (fr);
end fork

|Chunker|
:Teile Content;
split
  :Kursbeschreibung;
split again
  :Module;
split again
  :Lernmethoden;
split again
  :Glossar;
split again
  :Prüfungen;
end split

|KI Translator|
:Übersetze Chunks parallel;

|Validator|
:Prüfe Übersetzungen;
fork
  :Konsistenz;
fork again
  :Markup;
fork again
  :Glossar;
end fork

|Database|
:Speichere Übersetzungen;

|Creator|
:Benachrichtigung: "Fertig";
:Öffne Translation Editor;
:Review & Anpassungen;
:Veröffentliche pro Sprache;

stop
@enduml
```

---

### 💰 Token-Kosten Management

```plantuml
@startuml
card "Creator" #E8F4F8 {
  :Global Publishing;
  :✅ KOSTENLOS;
  note right
    LSX übernimmt
    Übersetzungskosten
  end note
}

card "School / Company" #FFF4E1 {
  :Global Publishing;
  :💰 Token Pool;
  note right
    Aus Organisations-
    Token-Pool
  end note
}

card "Premium User" #FFE1E1 {
  :Global Publishing;
  :❌ Nicht verfügbar;
  note right
    Nur für Creator+
  end note
}
@enduml
```

---

## 7. KI-Übersetzungslogik

### 🤖 Translation Engine Components

```plantuml
@startuml
package "KI Translation Engine" {
  component "Content Preparation" {
    [Text Extractor]
    [Chunker (2000 tokens)]
    [Metadata Extractor]
  }
  
  component "Translation Process" {
    [Glossary Loader]
    [Context Builder]
    [KI API Caller]
    [Response Parser]
  }
  
  component "Post-Processing" {
    [Markup Validator]
    [Consistency Checker]
    [Quality Scorer]
  }
}

[Text Extractor] --> [Chunker (2000 tokens)]
[Chunker (2000 tokens)] --> [Glossary Loader]
[Glossary Loader] --> [Context Builder]
[Context Builder] --> [KI API Caller]
[KI API Caller] --> [Response Parser]
[Response Parser] --> [Markup Validator]
[Markup Validator] --> [Consistency Checker]
[Consistency Checker] --> [Quality Scorer]

note right of [Glossary Loader]
  Lädt Fachbegriffe:
  - Kurs-spezifisch
  - Fach-spezifisch
  - Global
end note

@enduml
```

---

### 📋 KI-Übersetzungsstrategie

| Strategie | Beschreibung | Technologie |
|-----------|-------------|-------------|
| **Chunking** | Max. 2000 Tokens pro Chunk | Python |
| **Semantisches Matching** | Kontext-Erhaltung | KI |
| **Glossar-Referenz** | Fachbegriffe konsistent | Database |
| **Konsistenzprüfung** | Qualitätssicherung | Validator |
| **Markup-Preservation** | Listen, Tabellen, Formeln | Parser |

---

### 💡 Translation API Call

```plantuml
@startuml
participant "Translation Service" as service
participant "Chunker" as chunker
participant "KI API" as ki
participant "Validator" as validator
database "Database" as db

service -> chunker: Split content into chunks
chunker --> service: [chunk1, chunk2, chunk3, ...]

loop For each chunk
  service -> ki: Translate chunk
  activate ki
  
  ki -> ki: Load glossary
  ki -> ki: Build context
  ki -> ki: Call Anthropic/OpenAI
  
  ki --> service: Translated chunk
  deactivate ki
  
  service -> validator: Validate translation
  activate validator
  
  validator -> validator: Check markup
  validator -> validator: Check consistency
  validator -> validator: Score quality
  
  alt Quality score < 80%
    validator --> service: Re-translate
  else Quality OK
    validator --> service: Accept
  end
  deactivate validator
end

service -> db: Save all translations
db --> service: Success

@enduml
```

---

## 8. Markup & Code Preservation

### 🔒 Content Preservation Rules

```plantuml
@startuml
@startmindmap
* Content Preservation
** Tabellen
*** Struktur erhalten
*** Spalten-Alignment
*** Header-Formatierung
** Code-Blöcke
*** Syntax nicht ändern
*** Kommentare übersetzen
*** Keywords original
** Formeln
*** LaTeX unverändert
*** MathJax Syntax
*** Variablen original
** Diagramme
*** PlantUML erhalten
*** Nur Labels übersetzen
** JSON-Inhalte
*** Struktur erhalten
*** Keys original
*** Nur Values übersetzen
@endmindmap
@enduml
```

---

### 💡 Preservation Example

**Original (de):**
```markdown
## Beispiel: Python Loop

\```python
# Zähle von 1 bis 10
for i in range(1, 11):
    print(f"Zahl: {i}")
\```

| Variable | Typ | Beschreibung |
|----------|-----|--------------|
| i | int | Zählvariable |
```

**Übersetzt (en):**
```markdown
## Example: Python Loop

\```python
# Count from 1 to 10
for i in range(1, 11):
    print(f"Number: {i}")
\```

| Variable | Type | Description |
|----------|------|-------------|
| i | int | Counter variable |
```

---

## 9. API für Übersetzungen

### 🔌 Translation API Endpoints

```plantuml
@startuml
package "Translation API" {
  [GET /api/v1/translation/{type}/{id}/{lang}] as get
  [POST /api/v1/ki/translate] as post
  [PATCH /api/v1/translation/{id}] as patch
  [DELETE /api/v1/translation/{id}] as delete
}

actor "Frontend" as frontend
actor "Creator" as creator

frontend --> get : "Abrufen"
creator --> post : "Neu generieren"
creator --> patch : "Manuell korrigieren"

note right of get
  Returns:
  {
    "content_type": "module",
    "content_id": 15,
    "language": "pl",
    "data": {...}
  }
end note

@enduml
```

---

### 💡 API Examples

#### 1. Übersetzung abrufen

**Request:**
```http
GET /api/v1/translation/module/15/pl
Authorization: Bearer <token>
```

**Response:**
```json
{
  "content_type": "module",
  "content_id": 15,
  "language": "pl",
  "data": {
    "title": "Wprowadzenie do Pythona",
    "description": "Naucz się podstaw...",
    "content": "..."
  },
  "translated_at": "2024-11-15T10:00:00Z"
}
```

---

#### 2. Übersetzung erzeugen

**Request:**
```http
POST /api/v1/ki/translate
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_type": "theory",
  "content_id": 15,
  "target_language": "pl"
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": "trans-job-123",
  "estimated_time": 30,
  "message": "Translation started"
}
```

---

#### 3. Manuelle Korrektur

**Request:**
```http
PATCH /api/v1/translation/456
Authorization: Bearer <token>
Content-Type: application/json

{
  "data": {
    "title": "Korrigierter Titel",
    "description": "Korrigierte Beschreibung"
  }
}
```

---

## 10. Frontend-Integration

### 🎨 Language Switcher Component

```vue
<!-- LanguageSwitcher.vue -->
<template>
  <div class="language-switcher">
    <Dropdown>
      <template #trigger>
        <button class="btn-language">
          <Flag :code="currentLanguage" />
          {{ languageNames[currentLanguage] }}
        </button>
      </template>
      
      <DropdownItem 
        v-for="lang in availableLanguages" 
        :key="lang"
        @click="changeLanguage(lang)"
      >
        <Flag :code="lang" />
        {{ languageNames[lang] }}
      </DropdownItem>
    </Dropdown>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/store/user'

const { locale } = useI18n()
const userStore = useUserStore()

const currentLanguage = computed(() => locale.value)

const availableLanguages = ['de', 'en', 'pl', 'fr', 'es']

const languageNames = {
  de: 'Deutsch',
  en: 'English',
  pl: 'Polski',
  fr: 'Français',
  es: 'Español'
}

const changeLanguage = async (lang) => {
  locale.value = lang
  
  // Save to user profile
  if (userStore.isAuthenticated) {
    await userStore.updateLanguage(lang)
  }
  
  // Reload dynamic content
  window.location.reload()
}
</script>
```

---

### 🔄 Dynamic Content Loading

```plantuml
@startuml
|Vue Component|
start
:Component mounted;

|i18n Service|
:Detect language;
:currentLang = 'de';

|Vue Component|
:Load dynamic content;

fork
  :Load course data;
  |API|
  :GET /translation/course/15/de;
  :Return course (de);
fork again
  :Load module data;
  |API|
  :GET /translation/module/23/de;
  :Return module (de);
end fork

|User|
:Click Language Switch;
:Select "English";

|i18n Service|
:currentLang = 'en';

|Vue Component|
:Reload content;

fork
  :Load course data;
  |API|
  :GET /translation/course/15/en;
  :Return course (en);
fork again
  :Load module data;
  |API|
  :GET /translation/module/23/en;
  :Return module (en);
end fork

:Re-render UI;
stop
@enduml
```

---

## 11. Domain-Lokalisierung (Organisationen)

### 🏢 Organization-specific Localization

```plantuml
@startuml
package "Organization Localization" {
  rectangle "schule.de" #LightBlue {
    [Erzwungene Sprache: de]
    [Custom Logo]
    [Standard-Kurssprache: de]
  }
  
  rectangle "firma.com" #LightGreen {
    [Erzwungene Sprache: en]
    [Custom Branding]
    [Standard-Kurssprache: en]
  }
  
  rectangle "LSX System" #LightYellow {
    [Domain Mapping]
    [Org Settings]
    [Language Override]
  }
}

[schule.de] --> [LSX System]
[firma.com] --> [LSX System]

note right of "schule.de"
  Deutsche Schule:
  - UI immer auf Deutsch
  - Eigenes Branding
  - Kurse primär auf Deutsch
end note

@enduml
```

---

## 12. Barrierefreiheit & Lernprofile

### ♿ Accessibility Features

```plantuml
@startuml
package "Accessibility & Learning Profiles" {
  card "Vereinfachte Sprachen" #E8F4F8 {
    :📘 Leichte Sprache (de);
    :📗 Plain Language (en);
    :Kurze Sätze;
    :Einfache Wörter;
  }
  
  card "Legasthenie-Unterstützung" #FFF4E1 {
    :🔤 OpenDyslexic Font;
    :Größerer Zeilenabstand;
    :Kontrastreiches Design;
    :Silbentrennung;
  }
  
  card "ADHD-Modus" #E1F5E1 {
    :🎯 Reduzierte UI;
    :Weniger Animationen;
    :Klare Struktur;
    :Fokus-Highlights;
  }
  
  card "Screenreader" #FFE1E1 {
    :🔊 ARIA Labels;
    :Semantisches HTML;
    :Tastatur-Navigation;
    :Alt-Texte;
  }
}

note bottom
  Alle Features kombinierbar
  und pro User konfigurierbar
end note
@enduml
```

---

## 13. Fehlende Übersetzungen

### 🔍 Missing Translation Handling

```plantuml
@startuml
|User|
start
:Request Course in (pl);

|Translation Service|
:Check translation;

if (Translation exists?) then (ja)
  :Return translation;
  stop
else (nein)
  :Return original (de);
  
  |UI|
  :Zeige Banner;
  note right
    ⚠️ "Diese Seite ist nicht
    auf Polnisch verfügbar"
    
    [🤖 KI-Übersetzung jetzt erstellen]
  end note
  
  |User|
  if (Click "Erstellen"?) then (ja)
    |Translation Service|
    :Queue Translation Job;
    :Background: KI-Übersetzung;
    :Notify when ready;
  endif
  
  |Logging|
  :Log missing translation;
  
  |Admin Dashboard|
  if (Alert enabled?) then (ja)
    :Send notification;
  endif
endif

stop
@enduml
```

---

## 14. Sicherheitsaspekte

### 🔒 Translation Security

```plantuml
@startuml
|Translation Input|
start
:Receive translation;

|Security Layer|
:1. XSS Protection;
note right
  - HTML Sanitization
  - Script removal
  - Style filtering
end note

if (Contains <script>?) then (yes)
  :🚫 Block & Alert;
  stop
endif

:2. Link Validation;
if (External links?) then (yes)
  :Validate whitelist;
  if (Allowed?) then (no)
    :Remove link;
  endif
endif

:3. HTML Limits;
note right
  Allowed:
  - <b>, <i>, <u>
  - <h1>-<h6>
  - <p>, <ul>, <ol>
  
  Blocked:
  - <script>
  - <iframe>
end note

:4. Content Validation;
if (Prüfung?) then (yes)
  :❌ Auto-Publish disabled;
  :Requires manual review;
endif

:✅ Accept translation;
stop
@enduml
```

---

## 15. Zusammenfassung

### ✅ LSX Internationalisierung ist:

| Feature | Status |
|---------|--------|
| 🌍 **Global** | ✅ 15+ Sprachen |
| 🤖 **KI-gestützt** | ✅ Automatische Übersetzung |
| 🔄 **Automatisiert** | ✅ Global Publishing |
| 🎯 **Präzise** | ✅ Glossar & Konsistenz |
| 📈 **Skalierbar** | ✅ Unbegrenzte Sprachen |
| 🔒 **Sicher** | ✅ XSS-Schutz, Validation |
| ♿ **Barrierefrei** | ✅ Accessibility Features |
| 🏢 **Flexibel** | ✅ Org-spezifisch |

---

### 🌍 i18n Architecture Overview

```
┌─────────────────────────────────────┐
│  🌍 Multi-Language Support           │
│  ─────────────────────────────────   │
│  ✅ UI i18n (vue-i18n)                │
│  ✅ Content i18n (KI-gestützt)        │
│  ✅ Lokalisierung (Datum, Zahlen)     │
│  ✅ Echtzeit-Sprachwechsel            │
│  ✅ Automatische Erkennung            │
│  ✅ Fallback-System                   │
│  ✅ Creator Global Publishing         │
│  ✅ Barrierefreiheit                  │
└─────────────────────────────────────┘
```

---

### 💡 Translation Flow Summary

```plantuml
@startuml
skinparam backgroundColor transparent

rectangle "Creator" #E8F4F8
rectangle "Global Publishing" #FFF4E1
rectangle "KI Translation" #E1F5E1
rectangle "Database Storage" #FFE1E1
rectangle "User Access" #E1E8F8

"Creator" -right-> "Global Publishing" : "Initiiert"
"Global Publishing" -right-> "KI Translation" : "Übersetzt"
"KI Translation" -right-> "Database Storage" : "Speichert"
"Database Storage" -right-> "User Access" : "Liefert"

note bottom
  Workflow:
  1. Creator erstellt Content (de)
  2. Klick "Global Publishing"
  3. KI übersetzt (en, pl, fr, ...)
  4. Speicherung in DB
  5. User wählt Sprache
  6. Content wird geladen
end note
@enduml
```

> **LSX kann weltweit angeboten werden, ohne inhaltliche Barrieren.**

---

## 📌 Dokument abgeschlossen

**Version:** 1.0  
**Status:** Final  
**Letzte Aktualisierung:** November 2024

---

> 💡 **Hinweis:** Dieses Dokument ist Teil der LSX-Systemdokumentation und beschreibt das vollständige Internationalisierungs- und Lokalisierungssystem mit KI-gestützten Übersetzungen, Multi-Language-Support und Barrierefreiheit.