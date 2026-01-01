# Frontend – Phase F8: Analytics UI (Admin & Organisation)

**Datum:** 2025-01-XX
**Status:** ✅ Abgeschlossen
**Abhängigkeiten:** F7 (Admin & Org Panel - Grundstruktur), Backend Analytics-System

---

## Übersicht

Phase F8 implementiert die vollständigen Analytics-Dashboards für System-Admins und Organisations-Admins mit interaktiven Charts, KPI-Cards und Zeitreihen-Visualisierungen.

### Ziele
- ✅ System-weite Analytics für System-Admins (AdminAnalyticsPage.vue)
- ✅ Organisations-spezifische Analytics für Org-Admins (OrgAnalyticsPage.vue)
- ✅ Wiederverwendbare Chart-Komponenten (chart.js + vue-chartjs)
- ✅ Zeitraum-Filter (7/30/90 Tage)
- ✅ Loading/Error/Empty States
- ✅ Responsive Layout

---

## 1. Komponenten-Architektur

### 1.1 Neue Chart-Komponenten

**Verzeichnis:** `frontend/src/components/analytics/`

#### AnalyticsKpiCard.vue
```typescript
interface Props {
  label: string           // "Gesamt Nutzer"
  value: string | number  // 1234
  description?: string    // "15 neue in 7 Tagen"
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: number     // 12 (= +12%)
  icon?: string          // "👥"
  format?: 'number' | 'percent' | 'currency' | 'none'
}
```

**Features:**
- Deutsche Zahlenformatierung (`Intl.NumberFormat('de-DE')`)
- Trend-Indikatoren (↑↓→) mit Farbcodierung
- Flexible Formatierung (Zahl, Prozent, Währung)

#### LineChart.vue
```typescript
interface Props {
  labels: string[]        // ["Jan 1", "Jan 2", ...]
  datasets: Dataset[]     // [{ label, data, color, fill }]
  height?: number         // 300
  title?: string
}
```

**Features:**
- Chart.js Integration mit vue-chartjs
- Smooth Curves (tension: 0.4)
- Area Charts (optional fill)
- Responsive mit maintainAspectRatio: false
- 6 Default-Farben für mehrere Datasets

#### BarChart.vue
```typescript
interface Props {
  labels: string[]
  datasets: Dataset[]
  height?: number
  title?: string
  horizontal?: boolean    // Horizontale vs. vertikale Balken
}
```

**Features:**
- Unterstützung für horizontale/vertikale Darstellung
- Abgerundete Balken (borderRadius: 4)
- Dynamische Farben

---

## 2. API-Erweiterungen

### 2.1 Admin Analytics API (`admin.api.ts`)

**Neue Interfaces:**
```typescript
export interface TimeSeriesPoint {
  date: string
  value: number
}

export interface AdminAnalyticsCourse {
  course_id: number
  title: string
  events_count: number
  enrollments: number
  completions: number
  avg_completion_rate?: number
}

export interface AdminAnalyticsMethod {
  method_id: number
  name: string
  calls: number
  tokens_used?: number
  avg_tokens?: number
}
```

**Neue Funktionen:**
```typescript
// GET /admin/analytics/events/time-series?days=7
adminGetEventsTimeSeries(params): Promise<TimeSeriesPoint[]>

// GET /admin/analytics/active-users/time-series?days=7
adminGetActiveUsersTimeSeries(params): Promise<TimeSeriesPoint[]>

// GET /admin/analytics/top-courses?days=7&limit=10
adminGetTopCourses(params): Promise<AdminAnalyticsCourse[]>

// GET /admin/analytics/top-methods?days=7&limit=10
adminGetTopMethods(params): Promise<AdminAnalyticsMethod[]>
```

### 2.2 Organisation Analytics API (`orgAdmin.api.ts`)

**Neue Interfaces:**
```typescript
export interface TimeSeriesPoint {
  date: string
  value: number
}

export interface OrgAnalyticsCourse {
  course_id: number
  title: string
  enrolled_count: number
  avg_progress: number
  completion_rate?: number
  events_count?: number
}

export interface OrgAnalyticsModule {
  module_id: number
  module_title: string
  course_title: string
  completions: number
  avg_time_spent?: number
}
```

**Neue Funktionen:**
```typescript
// GET /organisations/{orgId}/analytics/events/time-series?days=7
orgGetEventsTimeSeries(orgId, params): Promise<TimeSeriesPoint[]>

// GET /organisations/{orgId}/analytics/active-members/time-series?days=7
orgGetActiveMembersTimeSeries(orgId, params): Promise<TimeSeriesPoint[]>

// GET /organisations/{orgId}/analytics/top-courses?days=7&limit=10
orgGetTopCourses(orgId, params): Promise<OrgAnalyticsCourse[]>

// GET /organisations/{orgId}/analytics/top-modules?days=7&limit=10
orgGetTopModules(orgId, params): Promise<OrgAnalyticsModule[]>
```

---

## 3. Store-Erweiterungen

### 3.1 Admin Store (`admin.store.ts`)

**Neue State:**
```typescript
const systemAnalytics = ref<{
  timeframe: 7 | 30 | 90
  eventsTimeSeries: TimeSeriesPoint[]
  activeUsersTimeSeries: TimeSeriesPoint[]
  topCourses: AdminAnalyticsCourse[]
  topMethods: AdminAnalyticsMethod[]
} | null>(null)

const systemAnalyticsLoading = ref(false)
const systemAnalyticsError = ref<string | null>(null)
```

**Neue Actions:**
```typescript
loadAdminAnalytics(timeframe: 7 | 30 | 90): Promise<void>
changeAnalyticsTimeframe(timeframe: 7 | 30 | 90): Promise<void>
```

**Neue Getters:**
```typescript
hasAnalytics: computed(() => !!systemAnalytics.value)
analyticsTimeframe: computed(() => systemAnalytics.value?.timeframe || 7)
```

### 3.2 OrgAdmin Store (`orgAdmin.store.ts`)

**Neue State:**
```typescript
const orgAnalytics = ref<{
  timeframe: 7 | 30 | 90
  eventsTimeSeries: TimeSeriesPoint[]
  activeMembersTimeSeries: TimeSeriesPoint[]
  topCourses: OrgAnalyticsCourse[]
  topModules: OrgAnalyticsModule[]
} | null>(null)

const orgAnalyticsLoading = ref(false)
const orgAnalyticsError = ref<string | null>(null)
```

**Neue Actions:**
```typescript
loadOrgAdvancedAnalytics(orgId: number, timeframe: 7 | 30 | 90): Promise<void>
changeOrgAnalyticsTimeframe(orgId: number, timeframe: 7 | 30 | 90): Promise<void>
```

**Neue Getters:**
```typescript
hasOrgAnalytics: computed(() => !!orgAnalytics.value)
orgAnalyticsTimeframe: computed(() => orgAnalytics.value?.timeframe || 7)
```

---

## 4. Seiten-Implementierung

### 4.1 AdminAnalyticsPage.vue

**Pfad:** `frontend/src/pages/admin/AdminAnalyticsPage.vue`
**Route:** `/admin/analytics`
**Zugriff:** `requiresSystemAdmin: true`

**Features:**
- **8 KPI-Cards:**
  - Gesamt Nutzer (mit Trend)
  - Aktive Nutzer (7d)
  - Organisationen
  - Kurse (Veröffentlicht)
  - Gesamt Einschreibungen
  - Premium Abos
  - Tokens verfügbar
  - Tokens (30d)

- **2 Zeitreihen-Charts:**
  - Events pro Tag
  - Aktive Nutzer pro Tag

- **2 Top-Listen:**
  - Top Kurse (Events, Einschreibungen, Abschlüsse)
  - Top Lernmethoden (Aufrufe, Tokens)

**Zeitraum-Filter:** 7/30/90 Tage (Buttons)

**States:**
- Loading: Spinner + "Analytics-Daten werden geladen..."
- Error: Rote Fehlermeldung mit Icon
- Empty: "Keine Analytics-Daten verfügbar"
- Content: Volle Dashboard-Ansicht

### 4.2 OrgAnalyticsPage.vue

**Pfad:** `frontend/src/pages/org/OrgAnalyticsPage.vue`
**Route:** `/org/analytics`
**Zugriff:** `requiresOrgAdmin: true`

**Features:**
- **8 KPI-Cards:**
  - Mitglieder Gesamt
  - Aktive Mitglieder (30d)
  - Zugewiesene Kurse
  - Durchschn. Abschlussrate
  - Tokens verwendet (7d)
  - Tokens verwendet (30d)
  - Token Pool
  - Token-Nutzung (%)

- **2 Zeitreihen-Charts:**
  - Events pro Tag
  - Aktive Mitglieder pro Tag

- **2 Top-Listen:**
  - Top Kurse (Teilnehmer, Fortschritt, Abschlussrate)
  - Top Module (Abschlüsse, Zeitaufwand)

- **Zusätzliche Liste (falls verfügbar):**
  - Top Lernende (aus `orgStats.top_users`)

**Zeitraum-Filter:** 7/30/90 Tage

**States:** Wie AdminAnalyticsPage

---

## 5. Routing & Zugriffskontrolle

**Konfiguration in:** `frontend/src/router/index.ts`

### Admin Analytics Route
```typescript
{
  path: '/admin',
  component: () => import('@/layouts/AdminLayout.vue'),
  meta: { requiresAuth: true, requiresSystemAdmin: true },
  children: [
    {
      path: 'analytics',
      name: 'AdminAnalytics',
      component: () => import('@/pages/admin/AdminAnalyticsPage.vue'),
    },
  ],
}
```

### Org Analytics Route
```typescript
{
  path: '/org',
  component: () => import('@/layouts/AdminLayout.vue'),
  meta: { requiresAuth: true, requiresOrgAdmin: true },
  children: [
    {
      path: 'analytics',
      name: 'OrgAnalytics',
      component: () => import('@/pages/org/OrgAnalyticsPage.vue'),
    },
  ],
}
```

**Navigation Guards:**
```typescript
// System Admin Check (Zeilen 207-211)
if (to.meta.requiresSystemAdmin && !authStore.isSystemAdmin) {
  console.warn('Access denied: System Admin required')
  next({ name: 'Dashboard' })
  return
}

// Org Admin Check (Zeilen 214-218)
if (to.meta.requiresOrgAdmin && !authStore.isOrgAdmin) {
  console.warn('Access denied: Organisation Admin required')
  next({ name: 'Dashboard' })
  return
}
```

---

## 6. Dependencies

### NPM Packages
```json
{
  "chart.js": "^4.4.7",
  "vue-chartjs": "^5.3.2"
}
```

**Installation:**
```bash
npm install chart.js vue-chartjs
```

---

## 7. Technische Details

### 7.1 Chart.js Registrierung
```typescript
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
)
```

### 7.2 Datenfluss (Admin Analytics)
```
1. onMounted() → loadAnalyticsData()
2. loadAnalyticsData() → Promise.all([
     adminStore.loadAdminDashboard(),        // GET /admin/analytics/system
     adminStore.loadAdminAnalytics(7)        // 4 parallele Requests
   ])
3. adminStore.loadAdminAnalytics() → Promise.all([
     adminGetEventsTimeSeries(),
     adminGetActiveUsersTimeSeries(),
     adminGetTopCourses(),
     adminGetTopMethods()
   ])
4. Store speichert in systemAnalytics.value
5. Computed properties transformieren für Charts
6. Vue rendert KPIs + Charts
```

### 7.3 Datenfluss (Org Analytics)
```
1. onMounted() → loadAnalyticsData()
2. loadAnalyticsData() → Promise.all([
     orgAdminStore.loadOrgDashboard(orgId),         // GET /organisations/{id}
     orgAdminStore.loadOrgAdvancedAnalytics(orgId, 7)
   ])
3. orgAdminStore.loadOrgAdvancedAnalytics() → Promise.all([
     orgGetEventsTimeSeries(orgId),
     orgGetActiveMembersTimeSeries(orgId),
     orgGetTopCourses(orgId),
     orgGetTopModules(orgId)
   ])
4. Store speichert in orgAnalytics.value
5. Computed properties transformieren für Charts
6. Vue rendert KPIs + Charts
```

---

## 8. UI/UX-Features

### 8.1 Responsive Grid-Layouts
```html
<!-- KPI Cards -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  <AnalyticsKpiCard ... />
</div>

<!-- Charts -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <div>...</div>
</div>
```

### 8.2 Trend-Indikatoren
```typescript
const userTrend = computed(() => {
  if (!systemStats.value) return 'neutral'
  const newUsers = systemStats.value.new_users_7_days || 0
  return newUsers > 0 ? 'up' : 'neutral'
})
```

### 8.3 Datumsformatierung
```typescript
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    month: 'short',
    day: 'numeric'
  }).format(date)
}
// Beispiel: "17. Jan"
```

---

## 9. Backend-Erwartungen

Die Frontend-Implementierung erwartet folgende Backend-Endpoints:

### System Admin Endpoints
```
GET /admin/analytics/system
GET /admin/analytics/events/time-series?days=7|30|90
GET /admin/analytics/active-users/time-series?days=7|30|90
GET /admin/analytics/top-courses?days=7|30|90&limit=10
GET /admin/analytics/top-methods?days=7|30|90&limit=10
```

### Organisation Admin Endpoints
```
GET /organisations/{orgId}
GET /organisations/{orgId}/analytics
GET /organisations/{orgId}/analytics/events/time-series?days=7|30|90
GET /organisations/{orgId}/analytics/active-members/time-series?days=7|30|90
GET /organisations/{orgId}/analytics/top-courses?days=7|30|90&limit=10
GET /organisations/{orgId}/analytics/top-modules?days=7|30|90&limit=10
```

**Hinweis:** Diese Endpoints müssen noch im Backend implementiert werden (siehe Backend Phase B10 – Analytics-Endpoints).

---

## 10. Testing-Hinweise

### Manuelle Tests
- [ ] System-Admin kann `/admin/analytics` aufrufen
- [ ] Org-Admin kann `/org/analytics` aufrufen
- [ ] Nicht-Admins werden auf Dashboard umgeleitet
- [ ] Zeitraum-Filter (7/30/90d) funktioniert
- [ ] Charts werden korrekt gerendert
- [ ] KPI-Cards zeigen formatierte Zahlen (de-DE)
- [ ] Trend-Indikatoren sind korrekt (↑↓→)
- [ ] Loading-State wird angezeigt
- [ ] Error-State bei API-Fehler wird angezeigt
- [ ] Empty-State wenn keine Daten vorhanden
- [ ] Responsive auf Mobile/Tablet/Desktop

### E2E-Tests (zukünftig)
```typescript
describe('AdminAnalyticsPage', () => {
  it('should display analytics dashboard for system admin', () => {
    // Login as system admin
    // Navigate to /admin/analytics
    // Verify KPI cards visible
    // Verify charts visible
    // Click timeframe filter
    // Verify data reloads
  })
})
```

---

## 11. Bekannte Einschränkungen

1. **Trend-Berechnung:** Trends werden derzeit vereinfacht berechnet (Vergleich 7d vs. 30d). In Zukunft sollten historische Vergleichsdaten verwendet werden.

2. **Backend-Abhängigkeit:** Die Seiten sind vollständig implementiert, aber Endpoints müssen noch im Backend entwickelt werden.

3. **Echtzeit-Updates:** Aktuell nur manuelle Aktualisierung via Button. WebSocket-Integration für Live-Updates ist geplant (siehe 26_Analytics-System.md).

4. **Export-Funktion:** Derzeit kein CSV/PDF-Export. Feature für zukünftige Phase.

---

## 12. Nächste Schritte

**Backend (Phase B10):**
- [ ] Analytics-Endpoints implementieren
- [ ] Zeitreihen-Aggregation in PostgreSQL
- [ ] Top-Listen-Queries optimieren
- [ ] Caching-Strategie (Redis)

**Frontend (Zukünftige Phasen):**
- [ ] Export-Funktionalität (CSV, PDF)
- [ ] Erweiterte Filter (Datum-Range-Picker)
- [ ] Drill-Down in Charts (z.B. Click auf Kurs → Details)
- [ ] WebSocket-Integration für Echtzeit-Updates
- [ ] Custom Dashboard-Builder (User wählt KPIs)

---

## 13. Zusammenfassung

✅ **Erfolgreich implementiert:**
- 3 wiederverwendbare Chart-Komponenten (AnalyticsKpiCard, LineChart, BarChart)
- Admin Analytics API mit 4 neuen Endpoints
- Org Analytics API mit 4 neuen Endpoints
- Admin Store mit Analytics-State & Actions
- OrgAdmin Store mit Analytics-State & Actions
- AdminAnalyticsPage.vue (8 KPIs, 2 Charts, 2 Top-Listen)
- OrgAnalyticsPage.vue (8 KPIs, 2 Charts, 2 Top-Listen, Top Lernende)
- Zeitraum-Filter (7/30/90 Tage)
- Loading/Error/Empty States
- Routing mit Zugriffskontrolle (requiresSystemAdmin, requiresOrgAdmin)

📦 **Dateien:**
```
frontend/
├── src/
│   ├── api/
│   │   ├── admin.api.ts (erweitert)
│   │   └── orgAdmin.api.ts (erweitert)
│   ├── store/
│   │   ├── admin.store.ts (erweitert)
│   │   └── orgAdmin.store.ts (erweitert)
│   ├── components/analytics/
│   │   ├── AnalyticsKpiCard.vue (neu)
│   │   ├── LineChart.vue (neu)
│   │   └── BarChart.vue (neu)
│   └── pages/
│       ├── admin/
│       │   └── AdminAnalyticsPage.vue (vollständig)
│       └── org/
│           └── OrgAnalyticsPage.vue (vollständig)
└── docs/
    └── F8_AnalyticsUI.md (dieses Dokument)
```

**Phase F8 ist abgeschlossen und bereit für Backend-Integration (Phase B10).**
