# Feature Flags - Admin Panel Guide

**Datum:** 2026-01-10
**Status:** ✅ AKTIV - Backend läuft mit Feature Flag System
**Version:** 1.0.0

---

## 🎯 Was sind Feature Flags?

Feature Flags ermöglichen dir, **neue Features progressiv auszurollen** ohne Code-Deployments. Du kannst Features:
- ✅ Global für alle User ein-/ausschalten
- ✅ Nur für bestimmte User aktivieren (z.B. Beta Tester)
- ✅ Nur für bestimmte Organisationen aktivieren
- ✅ Prozentual ausrollen (5% → 25% → 100%)
- ✅ Für User-Segmente aktivieren (Premium, Beta, etc.)

**Dark Launch Strategy**: Alle Social Features sind **gebaut (100%)** aber **deaktiviert (0%)**. Du entscheidest, wann und für wen sie aktiviert werden.

---

## 📊 Verfügbare Social Features (30+ Flags)

### Social Features (12)
| Flag | Beschreibung | Default | Status |
|------|--------------|---------|--------|
| `user_posts` | User können Posts erstellen | ❌ Disabled | Ready |
| `user_comments` | Kommentare zu Posts | ❌ Disabled | Ready |
| `likes` | Like-System | ❌ Disabled | Ready |
| `shares` | Share-System | ❌ Disabled | Ready |
| `user_profiles` | User-Profile | ❌ Disabled | Ready |
| `following` | Follow-System | ❌ Disabled | Ready |
| `direct_messages` | Direkt-Nachrichten | ❌ Disabled | Ready |
| `group_chat` | Gruppen-Chat | ❌ Disabled | Ready |
| `hashtags` | Hashtag-System | ❌ Disabled | Ready |
| `trending` | Trending Posts | ❌ Disabled | Ready |
| `mentions` | @Mentions | ❌ Disabled | Ready |
| `bookmarks` | Lesezeichen | ❌ Disabled | Ready |

### Discovery Features (3)
| Flag | Beschreibung | Default | Status |
|------|--------------|---------|--------|
| `explore_feed` | Explore Feed | ❌ Disabled | Ready |
| `personalized_recommendations` | KI-Empfehlungen | ❌ Disabled | Ready |
| `content_search` | Volltextsuche | ❌ Disabled | Ready |

### Community Features (4)
| Flag | Beschreibung | Default | Status |
|------|--------------|---------|--------|
| `forums` | Diskussionsforen | ❌ Disabled | Ready |
| `study_groups` | Lerngruppen | ❌ Disabled | Ready |
| `live_rooms` | Live-Räume | ❌ Disabled | Ready |
| `events` | Events | ❌ Disabled | Ready |

### Safety Features (5)
| Flag | Beschreibung | Default | Status |
|------|--------------|---------|--------|
| `content_moderation` | Content Moderation | ✅ Enabled | Active |
| `ai_moderation` | KI-Moderation | ✅ Enabled | Active |
| `user_blocking` | User blockieren | ❌ Disabled | Ready |
| `content_appeals` | DSA Appeals | ❌ Disabled | Ready |
| `trust_safety_dashboard` | Moderator Dashboard | ✅ Enabled | Active |

### Analytics Features (3)
| Flag | Beschreibung | Default | Status |
|------|--------------|---------|--------|
| `user_analytics` | User-Analytics | ❌ Disabled | Ready |
| `engagement_metrics` | Engagement-Metriken | ❌ Disabled | Ready |
| `ab_testing` | A/B Testing | ✅ Enabled | Active |

### Advanced Features (3)
| Flag | Beschreibung | Default | Status |
|------|--------------|---------|--------|
| `progressive_rollout` | Progressive Rollouts | ✅ Enabled | Active |
| `beta_features` | Beta Features | ✅ Enabled | Active |
| `experimental_features` | Experimentelle Features | ❌ Disabled | Ready |

**6 Flags standardmäßig aktiviert:**
- `ai_moderation` (ALWAYS ENABLED - Safety)
- `content_moderation` (ALWAYS ENABLED - DSA/NetzDG Compliance)
- `trust_safety_dashboard` (für Moderatoren)
- `progressive_rollout` (Rollout-System selbst)
- `beta_features` (Beta-Programm)
- `ab_testing` (A/B Testing System)

---

## 🔧 Admin Panel Integration

### API Endpoints für Feature Flag Management

#### 1. **Alle Feature Flags abrufen**
```http
GET /api/v1/admin/feature-flags
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_posts": {
      "is_enabled": false,
      "created_at": "2026-01-10T20:00:00Z",
      "updated_at": "2026-01-10T20:00:00Z"
    },
    "ai_moderation": {
      "is_enabled": true,
      "created_at": "2026-01-10T20:00:00Z",
      "updated_at": "2026-01-10T20:00:00Z"
    }
    // ... 30+ weitere Flags
  }
}
```

---

#### 2. **Feature global aktivieren**
```http
POST /api/v1/admin/feature-flags/:name/enable
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "globally": true
}
```

**Beispiel - User Posts aktivieren:**
```bash
curl -X POST http://localhost:5000/api/v1/admin/feature-flags/user_posts/enable \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"globally": true}'
```

---

#### 3. **Feature global deaktivieren**
```http
POST /api/v1/admin/feature-flags/:name/disable
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "globally": true
}
```

---

#### 4. **Feature für bestimmten User aktivieren**
```http
POST /api/v1/admin/feature-flags/:name/enable
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "user_id": "user-uuid-123"
}
```

**Use Case:** Beta-Tester soll neues Feature testen.

---

#### 5. **Feature für Organisation aktivieren**
```http
POST /api/v1/admin/feature-flags/:name/enable
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "organization_id": "org-uuid-456"
}
```

**Use Case:** Enterprise-Kunde soll exklusives Feature nutzen.

---

#### 6. **Percentage Rollout setzen**
```http
POST /api/v1/admin/feature-flags/:name/rollout
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "percentage": 25
}
```

**Progression:**
- Start: 0% (niemand)
- Stufe 1: 5% (Early Adopters)
- Stufe 2: 10%
- Stufe 3: 25% (Breiterer Test)
- Stufe 4: 50%
- Stufe 5: 75%
- Final: 100% (alle User)

**⚠️ WICHTIG:** Der Hash-Algorithmus ist **deterministisch** - ein User bleibt immer in der gleichen Gruppe!

---

## 🎭 Priority System

Wenn mehrere Regeln existieren, gilt diese Priorität:

```
1. User-Override    (höchste Priorität)
   ↓
2. Organisation-Override
   ↓
3. User Segment (beta, premium)
   ↓
4. Percentage Rollout
   ↓
5. Global Flag      (niedrigste Priorität)
```

**Beispiel:**
- Global: `user_posts = disabled`
- Rollout: `user_posts = 25%`
- User-Override: `user_id="123" → enabled`

→ User 123 sieht das Feature (User-Override schlägt alles andere)

---

## 💻 Backend Code-Integration

Alle Social API Endpoints sind automatisch geschützt:

```python
@posts_bp.route('/api/social/posts', methods=['POST'])
@token_required
@require_feature('user_posts')
def create_post():
    """
    Create a new post

    Feature Flag: user_posts (DISABLED by default)
    """
    # ... code ...
```

**Wenn Feature deaktiviert:**
```json
HTTP 403 Forbidden
{
  "success": false,
  "error": {
    "code": "FEATURE_DISABLED",
    "message": "This feature is not available for your account",
    "feature": "user_posts"
  }
}
```

---

## 📱 Frontend Integration

**Vue.js Composable:**
```typescript
// composables/useFeatureFlags.ts
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useFeatureFlags() {
  const authStore = useAuthStore()
  const flags = ref<Record<string, boolean>>({})

  async function loadFlags() {
    const response = await fetch('/api/v1/feature-flags/my-flags', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    flags.value = await response.json()
  }

  function isEnabled(feature: string): boolean {
    return flags.value[feature] === true
  }

  return {
    flags,
    loadFlags,
    isEnabled
  }
}
```

**Nutzung in Component:**
```vue
<script setup lang="ts">
import { useFeatureFlags } from '@/composables/useFeatureFlags'

const { isEnabled } = useFeatureFlags()
</script>

<template>
  <div>
    <button v-if="isEnabled('user_posts')" @click="createPost">
      Create Post
    </button>
    <div v-else class="feature-locked">
      🔒 This feature is coming soon!
    </div>
  </div>
</template>
```

---

## 🚀 Rollout-Strategie (Empfohlen)

### Phase 1: Beta Testing (5%)
```bash
# Aktiviere für Beta-User Segment
POST /api/v1/admin/feature-flags/user_posts/enable
{
  "segment": "beta_users"
}
```

**Dauer:** 1-2 Wochen
**Monitoring:** Fehlerrate, Performance, User Feedback

---

### Phase 2: Early Adopters (10%)
```bash
# Erhöhe auf 10% Rollout
POST /api/v1/admin/feature-flags/user_posts/rollout
{
  "percentage": 10
}
```

**Dauer:** 1 Woche
**Monitoring:** Engagement-Metriken, Server-Load

---

### Phase 3: Breiterer Test (25%)
```bash
POST /api/v1/admin/feature-flags/user_posts/rollout
{
  "percentage": 25
}
```

**Dauer:** 1 Woche
**Monitoring:** Database-Performance, Redis-Cache

---

### Phase 4: Mehrheit (50% → 75%)
```bash
# Stufe 1
POST /api/v1/admin/feature-flags/user_posts/rollout
{"percentage": 50}

# Nach 3 Tagen - Stufe 2
POST /api/v1/admin/feature-flags/user_posts/rollout
{"percentage": 75}
```

**Dauer:** 1 Woche total
**Monitoring:** Gesamt-Systemstabilität

---

### Phase 5: Full Rollout (100%)
```bash
# Option A: 100% Rollout
POST /api/v1/admin/feature-flags/user_posts/rollout
{"percentage": 100}

# Option B: Global aktivieren (sauberer)
POST /api/v1/admin/feature-flags/user_posts/enable
{"globally": true}
```

**Feature ist jetzt permanent aktiviert!**

---

## 🔥 Emergency Rollback

Wenn ein Feature Probleme verursacht:

```bash
# SOFORT DEAKTIVIEREN
POST /api/v1/admin/feature-flags/user_posts/disable
{
  "globally": true
}
```

**Effekt:**
- ✅ Feature wird sofort für ALLE User deaktiviert
- ✅ Kein Code-Deployment nötig
- ✅ Kein Server-Neustart nötig
- ✅ Cache wird automatisch geleert (5min TTL)

**User sehen wieder:**
```json
HTTP 403 Forbidden
{
  "code": "FEATURE_DISABLED",
  "message": "This feature is temporarily unavailable"
}
```

---

## 📈 Monitoring & Analytics

### Wichtige Metriken überwachen:

1. **Feature Adoption Rate**
   - Wie viele User nutzen das Feature?
   - Conversion Rate: Aktiviert → Tatsächlich genutzt

2. **Engagement Metrics**
   - Likes/Comments/Shares pro User
   - Time-on-Site mit neuem Feature

3. **Performance Metrics**
   - API Response Times
   - Database Query Performance
   - Redis Cache Hit Rate

4. **Error Rates**
   - HTTP 5xx Errors
   - Feature-spezifische Fehler
   - Client-side JavaScript Errors

5. **Compliance Metrics**
   - DSA: Moderation Response Time (< 24h)
   - NetzDG: SLA Compliance (24h/7d)
   - Child Safety: Age Verification Rate

---

## 🎯 Use Cases

### Use Case 1: Neues Social Feature testen
```
1. Feature ist gebaut (user_posts)
2. Aktiviere für Beta-User (5%)
3. Sammle Feedback (1 Woche)
4. Rollout auf 25%
5. Weitere 2 Wochen Monitoring
6. Full Rollout (100%)
```

### Use Case 2: Premium-Feature für Enterprise
```
1. Feature ist gebaut (advanced_analytics)
2. Aktiviere nur für Organisation XYZ
3. Organisation zahlt Premium
4. Feature bleibt exklusiv
```

### Use Case 3: A/B Testing
```
1. Feature ist gebaut (new_ui_variant)
2. Rollout auf 50%
3. Vergleiche Metriken:
   - Gruppe A (50%): Neue UI
   - Gruppe B (50%): Alte UI
4. Nach 2 Wochen: Beste Variante gewinnt
```

### Use Case 4: Regulatory Compliance
```
1. Feature ist gebaut (eu_gdpr_feature)
2. Aktiviere nur für EU-Organisationen
3. Compliance erfüllt für EU
4. Rest der Welt bleibt disabled
```

---

## 🔐 Security & Permissions

**Nur Admins können Feature Flags ändern!**

Required Role: `admin`
Required Permissions: `feature_flags.manage`

**Audit Log:**
- Alle Feature Flag Änderungen werden geloggt
- Wer hat was wann geändert?
- Rollback ist nachvollziehbar

---

## 🛠️ Database Schema

```sql
-- Global Feature Flags
CREATE TABLE core.feature_flags (
    name VARCHAR(255) PRIMARY KEY,
    is_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User-specific Overrides
CREATE TABLE core.feature_flag_user_overrides (
    feature_name VARCHAR(255),
    user_id VARCHAR(36),
    is_enabled BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (feature_name, user_id)
);

-- Organization Overrides
CREATE TABLE core.feature_flag_org_overrides (
    feature_name VARCHAR(255),
    organization_id VARCHAR(36),
    is_enabled BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (feature_name, organization_id)
);

-- User Segments
CREATE TABLE core.feature_flag_segments (
    feature_name VARCHAR(255),
    segment VARCHAR(100), -- 'beta', 'premium', 'internal'
    is_enabled BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (feature_name, segment)
);

-- Percentage Rollout
CREATE TABLE core.feature_flag_rollouts (
    feature_name VARCHAR(255) PRIMARY KEY,
    percentage INTEGER CHECK (percentage >= 0 AND percentage <= 100)
);
```

---

## 📞 Support

Bei Fragen zum Feature Flag System:
1. Siehe diese Dokumentation
2. Check Backend Logs: `/backend/logs/`
3. Redis Status prüfen: `redis-cli ping`
4. Database Status: `psql service=devdb -c "\dt core.feature_*"`

---

## ✅ Quick Start Checklist

Als Admin möchte ich ein neues Feature ausrollen:

- [ ] Backend läuft (Port 5000)
- [ ] Admin-Token vorhanden
- [ ] Feature in DB vorhanden (see list above)
- [ ] Entscheidung: Beta (5%) oder Global (100%)?
- [ ] API Call durchführen (POST /admin/feature-flags/...)
- [ ] Frontend neu laden (Cache-Bust)
- [ ] Feature testen
- [ ] Monitoring aktivieren
- [ ] Bei Problemen: Emergency Rollback bereit

---

**Version:** 1.0.0
**Letzte Aktualisierung:** 2026-01-10
**Backend Status:** ✅ LIVE - Feature Flags aktiv auf Port 5000
**Social Platform:** ✅ READY - 30+ Feature Flags verfügbar
