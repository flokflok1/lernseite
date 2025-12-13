# LernsystemX Frontend

Vue.js 3 + TypeScript Frontend für das LernsystemX Lernsystem.

## 🛠️ Tech Stack

- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Language:** TypeScript
- **State Management:** Pinia
- **Routing:** Vue Router
- **Styling:** TailwindCSS
- **HTTP Client:** Axios

## 📋 Voraussetzungen

- Node.js 18+
- npm oder yarn
- Backend läuft auf `http://localhost:5000`

## 🚀 Installation & Setup

### 1. Dependencies installieren

```bash
cd frontend
npm install
```

### 2. Umgebungsvariablen konfigurieren

Die `.env` Datei ist bereits konfiguriert:

```env
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

Wenn dein Backend auf einem anderen Port läuft, passe die URL entsprechend an.

### 3. Development Server starten

```bash
npm run dev
```

Die Anwendung ist nun unter `http://localhost:5173` erreichbar.

### 4. Setup Wizard durchlaufen

Beim ersten Start des Systems wird automatisch der **Setup Wizard** geöffnet (`/setup`), der dich durch die Installation führt:

1. **Systemcheck** - Überprüfung der Systemvoraussetzungen
2. **Datenbank** - Initialisierung der Datenbank-Struktur
3. **Admin-Account** - Erstellung des ersten Admin-Users
4. **Organisation** - Einrichtung der ersten Organisation
5. **KI-Konfiguration** - Optional: API-Keys für OpenAI, Anthropic, DeepL
6. **Seed-Daten** - Installation von Lernmethoden, Kategorien und Rollen
7. **Abschluss** - Verifizierung und Abschluss der Installation

Der Setup Wizard ist nur beim ersten Start sichtbar. Nach erfolgreicher Installation erfolgt automatisch ein Redirect zum Login.

## 📦 Verfügbare Scripts

```bash
# Setup überprüfen
npm run check

# Development Server starten
npm run dev

# Production Build erstellen
npm run build

# Production Build lokal testen
npm run preview
```

### Check-Script

Das `npm run check` Script überprüft die vollständige Installation:

- ✅ Package.json Dependencies
- ✅ Konfigurationsdateien (Vite, Tailwind, TypeScript)
- ✅ Quellcode-Struktur
- ✅ Alle Kern-Dateien vorhanden
- ✅ Wichtige Code-Features implementiert
- ✅ Node Modules installiert
- ✅ Dokumentation vorhanden

Führe dieses Script aus, um sicherzustellen, dass alles korrekt eingerichtet ist.

## 🏗️ Projektstruktur

```
frontend/
├── src/
│   ├── api/              # API Services & HTTP Client
│   │   ├── http.ts       # Axios Instance mit JWT-Interceptor
│   │   ├── auth.api.ts   # Auth API Endpoints
│   │   ├── setup.api.ts  # Setup API Endpoints (separater Client)
│   │   ├── profile.api.ts      # Profile API Endpoints
│   │   ├── tokens.api.ts       # Token API Endpoints
│   │   ├── subscriptions.api.ts # Subscription API Endpoints
│   │   └── courses.api.ts      # Course API Endpoints
│   ├── components/       # Wiederverwendbare UI-Komponenten
│   │   └── ui/           # Basis-UI-Komponenten
│   │       ├── Button.vue
│   │       ├── Input.vue
│   │       └── Card.vue
│   ├── layouts/          # Layout-Komponenten
│   │   ├── AuthLayout.vue      # Layout für Login/Register
│   │   ├── BaseLayout.vue      # Layout für authentifizierte Seiten
│   │   └── SetupLayout.vue     # Layout für Setup Wizard
│   ├── pages/            # Seiten-Komponenten
│   │   ├── auth/
│   │   │   ├── LoginPage.vue
│   │   │   └── RegisterPage.vue
│   │   ├── dashboard/
│   │   │   └── DashboardPage.vue
│   │   ├── setup/
│   │   │   ├── SetupWizardPage.vue
│   │   │   └── steps/
│   │   │       ├── SetupSystemCheckStep.vue
│   │   │       ├── SetupDatabaseStep.vue
│   │   │       ├── SetupAdminStep.vue
│   │   │       ├── SetupOrganisationStep.vue
│   │   │       ├── SetupAIConfigStep.vue
│   │   │       ├── SetupSeedStep.vue
│   │   │       └── SetupFinishStep.vue
│   │   ├── ProfilePage.vue
│   │   ├── CoursesPage.vue
│   │   └── NotFoundPage.vue
│   ├── router/           # Vue Router Konfiguration
│   │   └── index.ts      # Routes + Navigation Guards
│   ├── store/            # Pinia Stores
│   │   ├── auth.store.ts # Authentication State
│   │   └── app.store.ts  # Global App State (Installation Status)
│   ├── utils/            # Utility Functions
│   ├── App.vue           # Root Component
│   ├── main.ts           # Application Entry Point
│   └── style.css         # Global Styles + Tailwind
├── .env                  # Environment Variables
├── vite.config.ts        # Vite Configuration
├── tailwind.config.js    # TailwindCSS Configuration
├── tsconfig.json         # TypeScript Configuration
└── package.json          # Dependencies
```

## 🔐 Authentifizierung

### Login Flow

1. User besucht `/login`
2. Gibt E-Mail + Passwort ein
3. Bei erfolgreichem Login:
   - JWT Access Token wird im Auth Store gespeichert
   - Token wird in `localStorage` persistiert
   - Automatischer Redirect zu `/dashboard`
4. Bei aktiviertem 2FA:
   - Zusätzliches Eingabefeld für TOTP-Code erscheint

### Token Management

- **Access Token:** 1 Stunde Gültigkeit
- **Refresh Token:** 30 Tage Gültigkeit
- Tokens werden in `localStorage` gespeichert
- Bei 401-Response: Automatischer Logout + Redirect zu `/login`

## 🗺️ Routen

| Route | Komponente | Auth Required | Beschreibung |
|-------|-----------|---------------|-------------|
| `/` | - | - | Redirect zu `/dashboard` |
| `/setup` | SetupWizardPage | Nein | Setup Wizard (nur bei uninstalliertem System) |
| `/login` | LoginPage | Nein | Login-Seite |
| `/register` | RegisterPage | Nein | Registrierungs-Seite |
| `/dashboard` | DashboardPage | Ja | Haupt-Dashboard mit Profil, Tokens, Abo & Kursen |
| `/profile` | ProfilePage | Ja | User-Profil mit Bearbeitung & Passwortänderung |
| `/courses` | CoursesPage | Ja | Kurs-Übersicht (Placeholder) |
| `*` | NotFoundPage | Nein | 404-Fehlerseite |

### Navigation Guards

Der Router implementiert folgende Logik:

1. **Installation Check:** Bei jedem Seitenaufruf wird geprüft, ob das System installiert ist
   - Falls nicht installiert → Redirect zu `/setup` (außer du bist bereits dort)
   - Falls installiert → Normale Route-Validierung

2. **Auth Check:** Geschützte Routen erfordern Login
   - Nicht eingeloggt → Redirect zu `/login`
   - Eingeloggt → Zugriff gewährt

3. **Guest Check:** Login/Register-Seiten nur für nicht eingeloggte User
   - Bereits eingeloggt → Redirect zu `/dashboard`

## 🏪 State Management (Pinia)

### Auth Store

**State:**
- `user`: User-Objekt (Basic Info)
- `profile`: Vollständiges Profil mit erweiterten Infos
- `accessToken`: JWT Access Token
- `refreshToken`: JWT Refresh Token
- `isLoading`: Loading-State
- `error`: Fehler-Message

**Getters:**
- `isAuthenticated`: Boolean, ob User eingeloggt ist
- `fullName`: Vollständiger Name des Users
- `userRole`: Rolle des Users (user, premium, creator, etc.)
- `isPremium`: Boolean, ob User Premium-Rolle hat
- `isTeacher`: Boolean, ob User Lehrer ist
- `isCreator`: Boolean, ob User Creator ist
- `isOrgAdmin`: Boolean, ob User Organisations-Admin ist

**Actions:**
- `login(credentials)`: User einloggen
- `register(data)`: User registrieren
- `logout()`: User ausloggen
- `loadProfile()`: User-Profil vom Backend laden
- `loadExtendedProfile()`: Profil + Tokens + Subscription laden
- `restoreSession()`: Session aus localStorage wiederherstellen

### App Store

**State:**
- `installed`: Boolean | null - Ob System installiert ist
- `setupRequired`: Boolean - Ob Setup durchlaufen werden muss

**Actions:**
- `checkInstallationStatus()`: Prüft via API, ob System installiert ist

Der App Store wird vom Router verwendet, um automatisch zum Setup Wizard zu redirecten, falls das System noch nicht installiert ist.

## 📊 Dashboard & Widget-System (Phase F4)

### Widget-basiertes Dashboard

Das Dashboard (`/dashboard`) nutzt ein **konfigurierbares Widget-System**, das je nach Benutzerrolle und Plan unterschiedliche Funktionen bietet:

#### Widget-System Features

**Für alle Nutzer:**
- Dynamisches Dashboard mit modularen Widgets
- Rollenbasierte Widget-Sichtbarkeit
- Automatisches Standard-Layout basierend auf Rolle
- LocalStorage-Persistenz der Konfiguration

**Für Premium-Nutzer:**
- Widget-Anpassung (Ein-/Ausblenden von Widgets)
- Personalisierbare Dashboard-Ansicht
- "Widgets anpassen"-Button im Dashboard
- Zurücksetzen auf Standardlayout

#### Verfügbare Widgets

1. **Willkommen-Widget** (`welcome`)
   - Persönliche Begrüßung
   - Schnellstatistiken (Rolle, Plan, Tokens, Kurse)
   - Für alle Nutzer sichtbar

2. **Profil-Übersicht** (`profile-summary`)
   - Kompakte Profilinformationen
   - Name, E-Mail, Rolle, Organisation
   - Link zur Profilbearbeitung

3. **Plan & Tokens** (`plan-tokens`)
   - Abo-Status und Plan
   - Token-Guthaben mit Farb-Coding
   - Warnung bei niedrigem Token-Stand
   - Link zur Plan-Verwaltung

4. **Meine Kurse** (`enrolled-courses`)
   - Liste der eingeschriebenen Kurse (Top 5)
   - Fortschrittsbalken pro Kurs
   - "Weiterlernen"-Button
   - Link zu allen Kursen

5. **Lernfortschritt** (`courses-progress`)
   - Aggregierte Lernstatistiken
   - Gestartete vs. abgeschlossene Kurse
   - Durchschnittlicher Fortschritt
   - Motivationsnachrichten

6. **Organisation** (`org-overview`) - _Nur für Lehrer/Admins_
   - Organisations-Informationen
   - Placeholder für zukünftige Statistiken
   - Nur sichtbar für: teacher, school_admin, company_admin, admin

#### Widget-Konfiguration (Premium)

Premium-Nutzer können über den "Widgets anpassen"-Button:
- Widgets ein- und ausblenden
- Sichtbarkeit per Toggle-Switch steuern
- Layout auf Standard zurücksetzen
- Änderungen werden automatisch in LocalStorage gespeichert

**Technische Details:**
- Widget-Definitionen: `src/config/widgetRegistry.ts`
- Widget-Typen: `src/types/widgets.ts`
- Dashboard Store: `src/store/dashboard.store.ts`
- Widget-Komponenten: `src/components/dashboard/widgets/`

### Dashboard (Detaillierte Ansicht)

Das Dashboard zeigt eine umfassende Übersicht über den aktuellen Status des Benutzers:

#### Sektion 1: Begrüßung & Profil
- **Mein Profil Card:**
  - Name, E-Mail, Rolle
  - Organisation (falls vorhanden)
  - Link zur Profilbearbeitung

#### Sektion 2: Plan & Tokens
- **Abo & KI Card:**
  - Aktueller Plan (Free, Premium, Creator, etc.)
  - Abo-Status (Aktiv, Trial, Gekündigt, Abgelaufen)
  - Inkludierte Tokens pro Monat
- **Token-Guthaben Card:**
  - Verfügbare Tokens (farbcodiert: grün > 5000, gelb > 1000, rot < 1000)
  - Verbrauchte Tokens
  - Warnhinweis bei niedrigem Guthaben

#### Sektion 3: Meine Kurse
- Liste der eingeschriebenen Kurse (Top 5)
- Für jeden Kurs:
  - Titel, Beschreibung
  - Fortschrittsbalken (Prozent)
  - Anzahl abgeschlossener Lektionen / Gesamt
  - "Weiterlernen"-Button
- Link zu allen Kursen

#### Sektion 4: Widget-Bereich (Placeholder)
- Vorbereitet für zukünftiges Widget-System (Phase F4)

**API-Aufrufe:**
- `GET /api/v1/profile` - Profil-Daten
- `GET /api/v1/profile/tokens` - Token-Balance
- `GET /api/v1/subscriptions/me` - Subscription-Info
- `GET /api/v1/courses/enrolled` - Eingeschriebene Kurse

### Profil

Die Profilseite (`/profile`) ermöglicht dem Benutzer, seine Daten zu verwalten:

#### Sektion 1: Meine Daten
- Anzeige: Vorname, Nachname, E-Mail, Rolle, Organisation
- Bearbeiten-Funktion:
  - Inline-Edit mit Save/Cancel
  - Validierung
  - Success/Error-Feedback
- **API:** `PUT /api/v1/profile`

#### Sektion 2: Sicherheit
- Passwort ändern:
  - Aktuelles Passwort eingeben
  - Neues Passwort (min. 8 Zeichen)
  - Bestätigung
  - Client-Side + Server-Side Validierung
- **API:** `POST /api/v1/profile/change-password`

#### Sektion 3: Plan & Tokens (Read-Only)
- **Abo-Informationen:**
  - Plan, Status, Quelle (User/Organisation/Default)
  - Ablaufdatum
  - Auto-Renewal Status
- **Token-Guthaben:**
  - Verfügbar, Gesamt erhalten, Verbraucht
  - Monatliche Token-Zuteilung

**Datenfluss:**
```
User → ProfilePage.vue
         ↓
    loadProfileData()
         ↓
    [parallel API calls]
         ↓
    ├─→ profileApi.getProfile()
    ├─→ tokensApi.getMyTokens()
    └─→ subscriptionsApi.getMySubscription()
         ↓
    [render with data]
```

## 🐛 Troubleshooting

### Backend nicht erreichbar

Stelle sicher, dass das Backend läuft:

```bash
cd backend
python run.py
```

Backend sollte unter `http://localhost:5000` erreichbar sein.

### CORS-Fehler

Falls CORS-Fehler auftreten, prüfe die Backend-Konfiguration in `backend/app/config.py`:

```python
CORS_ORIGINS = ['http://localhost:5173']
```
