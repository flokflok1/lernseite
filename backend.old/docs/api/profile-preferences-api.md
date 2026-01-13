# Profile Preferences API

User preferences management endpoints for storing UI settings like window sizes.

## Overview

Diese Endpoints ermöglichen es Benutzern, ihre UI-Einstellungen zu speichern und abzurufen. Die Einstellungen werden pro Benutzer in der Datenbank gespeichert (Tabelle `user_preferences`).

**Features:**
- Window-Größen pro Window-Typ speichern
- UI-Einstellungen (z.B. Sidebar-Status)
- Allgemeine Präferenzen

## Base URL

```
/api/v1/profile/preferences
```

## Authentication

Alle Endpoints erfordern JWT-Authentifizierung:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### GET /api/v1/profile/preferences

Get all user preferences.

**Response:**
```json
{
  "success": true,
  "preferences": {
    "window_sizes": {
      "admin-model-selector": {"width": 800, "height": 600},
      "admin-course-editor": {"width": 1200, "height": 800}
    },
    "ui_settings": {},
    "general_settings": {}
  }
}
```

---

### GET /api/v1/profile/preferences/window-sizes

Get window size preferences only.

**Response:**
```json
{
  "success": true,
  "window_sizes": {
    "admin-model-selector": {"width": 800, "height": 600},
    "admin-course-editor": {"width": 1200, "height": 800}
  }
}
```

---

### PUT /api/v1/profile/preferences/window-sizes

Update window size for a specific window type.

**Request Body:**
```json
{
  "window_type": "admin-model-selector",
  "width": 900,
  "height": 700
}
```

**Response:**
```json
{
  "success": true,
  "message": "Window size for admin-model-selector updated",
  "window_sizes": {
    "admin-model-selector": {"width": 900, "height": 700}
  }
}
```

**Validation:**
- `window_type` is required
- `width` and `height` must be integers
- Minimum size: 400x300

---

### DELETE /api/v1/profile/preferences/window-sizes/{window_type}

Delete a specific window size preference.

**URL Parameters:**
- `window_type`: The window type to delete (e.g., `admin-model-selector`)

**Response:**
```json
{
  "success": true,
  "message": "Window size for admin-model-selector deleted",
  "window_sizes": {}
}
```

---

### POST /api/v1/profile/preferences/reset

Reset all user preferences to defaults.

**Response:**
```json
{
  "success": true,
  "message": "Preferences reset to defaults",
  "preferences": {
    "window_sizes": {},
    "ui_settings": {},
    "general_settings": {}
  }
}
```

---

## Database Schema

**Table: `user_preferences`**

| Column | Type | Description |
|--------|------|-------------|
| preference_id | SERIAL | Primary key |
| user_id | UUID | Foreign key to users (UNIQUE) |
| window_sizes | JSONB | Window sizes by type |
| ui_settings | JSONB | UI settings |
| general_settings | JSONB | General preferences |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update timestamp |

**Example `window_sizes` JSONB:**
```json
{
  "admin-model-selector": {"width": 800, "height": 600},
  "admin-course-editor": {"width": 1200, "height": 800},
  "admin-kapitel-editor": {"width": 1000, "height": 700}
}
```

---

## Frontend Integration

The frontend (`window.store.ts`) automatically:
1. Loads window sizes from server when admin layout mounts
2. Saves sizes to server with 500ms debounce when resizing
3. Falls back to localStorage if API is unavailable

```typescript
// Load sizes from server
await windowStore.loadWindowSizesFromServer()

// Update size (automatically syncs to server)
windowStore.updateWindowSize(windowId, { width: 800, height: 600 })
```

---

## Migration

**File:** `migrations/058_user_preferences.sql`

Run with:
```bash
psql -U lernsystem -d lernsystemx_dev -h localhost -f migrations/058_user_preferences.sql
```
