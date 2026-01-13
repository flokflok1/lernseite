# Quick Start - Feature Aktivierung

**Backend Status:** ✅ LÄUFT auf Port 5000
**Datum:** 2026-01-10

---

## 🚀 Dein erstes Feature aktivieren (5 Minuten)

### Schritt 1: Admin Token holen

```bash
# Login als Admin
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@lernsystemx.de",
    "password": "dein_admin_passwort"
  }'

# Antwort:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "...",
    "user": { ... }
  }
}
```

**→ Kopiere den `access_token` für die nächsten Schritte**

---

### Schritt 2: Alle Feature Flags anzeigen

```bash
curl -X GET http://localhost:5000/api/v1/admin/feature-flags \
  -H "Authorization: Bearer <DEIN_TOKEN>"

# Du siehst:
{
  "user_posts": {
    "is_enabled": false,  ← DISABLED
    "created_at": "2026-01-10T20:00:00Z"
  },
  "ai_moderation": {
    "is_enabled": true,   ← ENABLED
    "created_at": "2026-01-10T20:00:00Z"
  },
  ...
}
```

---

### Schritt 3A: Feature SOFORT für ALLE aktivieren (Global)

```bash
# User Posts global aktivieren
curl -X POST http://localhost:5000/api/v1/admin/feature-flags/user_posts/enable \
  -H "Authorization: Bearer <DEIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"globally": true}'

# Antwort:
{
  "success": true,
  "message": "Feature 'user_posts' enabled globally"
}
```

**✅ Fertig! Alle User können jetzt Posts erstellen.**

---

### Schritt 3B: Feature PROGRESSIV ausrollen (EMPFOHLEN)

```bash
# Stufe 1: Nur 5% der User (Beta Testing)
curl -X POST http://localhost:5000/api/v1/admin/feature-flags/user_posts/rollout \
  -H "Authorization: Bearer <DEIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"percentage": 5}'

# 1 Woche warten, Feedback sammeln...

# Stufe 2: 25% der User
curl -X POST http://localhost:5000/api/v1/admin/feature-flags/user_posts/rollout \
  -H "Authorization: Bearer <DEIN_TOKEN>" \
  -d '{"percentage": 25}'

# 2 Wochen warten, Monitoring...

# Stufe 3: 100% (oder global enable)
curl -X POST http://localhost:5000/api/v1/admin/feature-flags/user_posts/enable \
  -H "Authorization: Bearer <DEIN_TOKEN>" \
  -d '{"globally": true}'
```

---

### Schritt 4: Feature testen

```bash
# Als User einen Post erstellen
curl -X POST http://localhost:5000/api/social/posts \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Mein erster Post! 🎉",
    "content_type": "text"
  }'

# Vorher (Feature disabled):
{
  "success": false,
  "error": {
    "code": "FEATURE_DISABLED",
    "message": "This feature is not available for your account",
    "feature": "user_posts"
  }
}

# Nachher (Feature enabled):
{
  "success": true,
  "data": {
    "post_id": "abc-123",
    "content": "Mein erster Post! 🎉",
    "user_id": "user-456",
    "created_at": "2026-01-10T20:45:00Z",
    "moderation_status": "ai_approved"  ← KI hat geprüft!
  }
}
```

---

### Schritt 5 (Optional): Feature für bestimmten User aktivieren

```bash
# Nur für Beta-Tester "user-123" aktivieren
curl -X POST http://localhost:5000/api/v1/admin/feature-flags/user_posts/enable \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123"
  }'

# Jetzt hat nur dieser User Zugriff!
# Alle anderen sehen "FEATURE_DISABLED"
```

---

## 🔥 Emergency: Feature sofort deaktivieren

Wenn etwas schief geht:

```bash
curl -X POST http://localhost:5000/api/v1/admin/feature-flags/user_posts/disable \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"globally": true}'

# SOFORT deaktiviert für ALLE User!
# Kein Server-Neustart nötig
# Cache wird automatisch geleert
```

---

## 📊 Feature Flags Status prüfen

```bash
# Alle Flags anzeigen
curl http://localhost:5000/api/v1/admin/feature-flags \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# Einen bestimmten Flag prüfen
curl http://localhost:5000/api/v1/admin/feature-flags/user_posts \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

---

## 🎯 Verfügbare Features (Ready to activate)

### Social Features
```bash
user_posts              # Posts erstellen
user_comments           # Kommentare
likes                   # Like-System
shares                  # Share-System
following               # Follow-System
direct_messages         # DMs
group_chat              # Gruppen-Chat
hashtags                # #hashtags
trending                # Trending Posts
user_profiles           # User-Profile
mentions                # @mentions
bookmarks               # Lesezeichen
```

### Discovery
```bash
explore_feed            # Explore Feed
personalized_recommendations  # KI-Empfehlungen
content_search          # Volltextsuche
```

### Community
```bash
forums                  # Diskussionsforen
study_groups            # Lerngruppen
live_rooms              # Live-Räume
events                  # Events
```

### Safety (bereits aktiv)
```bash
content_moderation      # ✅ AKTIV
ai_moderation           # ✅ AKTIV
trust_safety_dashboard  # ✅ AKTIV
```

---

## 🛠️ Debug Commands

```bash
# Backend Status
curl http://localhost:5000/health

# Setup Status
curl http://localhost:5000/setup/status

# Prüfe ob Backend läuft
ps aux | grep "python.*run.py"

# Backend Logs live anzeigen
tail -f /tmp/backend_test_social.log

# Redis Status (Feature Flag Cache)
redis-cli -h 10.0.43.2 -p 6379 ping

# Feature Flag in DB prüfen
psql service=devdb -c "SELECT * FROM core.feature_flags WHERE name = 'user_posts';"

# Rollout Percentage prüfen
psql service=devdb -c "SELECT * FROM core.feature_flag_rollouts WHERE feature_name = 'user_posts';"
```

---

## 📱 Frontend Integration (Vue.js Beispiel)

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const canCreatePosts = ref(false)

onMounted(async () => {
  // Check if user_posts feature is enabled
  const response = await fetch('/api/v1/feature-flags/check', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ feature: 'user_posts' })
  })

  const data = await response.json()
  canCreatePosts.value = data.enabled
})

const createPost = async () => {
  if (!canCreatePosts.value) {
    alert('Feature not available!')
    return
  }

  const response = await fetch('/api/social/posts', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authStore.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      content: 'Mein Post',
      content_type: 'text'
    })
  })

  // Handle response...
}
</script>

<template>
  <div>
    <button
      v-if="canCreatePosts"
      @click="createPost"
      class="btn-primary"
    >
      Create Post
    </button>

    <div v-else class="feature-locked">
      🔒 This feature is coming soon!
    </div>
  </div>
</template>
```

---

## ✅ Checkliste: Erstes Feature aktivieren

- [ ] Backend läuft (`curl http://localhost:5000/health`)
- [ ] Admin-Token geholt (`POST /api/v1/auth/login`)
- [ ] Feature ausgewählt (z.B. `user_posts`)
- [ ] Aktivierungs-Methode gewählt:
  - [ ] Option A: Global (100%) - SOFORT
  - [ ] Option B: Progressive (5% → 100%) - EMPFOHLEN
- [ ] API Call durchgeführt (`POST /admin/feature-flags/.../enable`)
- [ ] Feature getestet (z.B. `POST /api/social/posts`)
- [ ] Monitoring aktiviert (Logs, Errors, Performance)
- [ ] Rollback-Plan bereit (`POST .../disable`)

---

## 📞 Support

Dokumentation:
- **Vollständiger Guide:** `.claude/FEATURE_FLAGS_ADMIN_GUIDE.md`
- **Backend Struktur:** `.claude/BACKEND_STRUCTURE_FINAL.md`

Logs:
- Backend: `tail -f /tmp/backend_test_social.log`
- Application: `tail -f logs/lernsystemx.log`

Database:
- `psql service=devdb`
- Schema: `core.feature_flags`, `core.feature_flag_user_overrides`, etc.

Redis:
- `redis-cli -h 10.0.43.2 -p 6379`
- Keys: `KEYS feature_flag:*`

---

**Status:** ✅ READY TO GO!
**Backend:** http://localhost:5000
**PID:** $(cat /tmp/backend_pid.txt)

🚀 **Jetzt Features aktivieren und loslegen!**
