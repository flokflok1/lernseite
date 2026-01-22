# 01 – Gruppenmodell (Group-Based Permission System)

**Status:** 🟢 Group-Based System (seit 2026-01-21)
**Typ:** Architecture Documentation
**Version:** 2.0 (Group-Based)
**Zielgruppe:** Architekten, Backend-Entwickler, Admins

> **Wichtig:** Dieses Dokument beschreibt das NEW Group-Based Permission System.
> Alte RBAC 2.0 Dokumentation siehe: `.claude/RBAC-2.0-LEGACY.md`

---

## 🏗️ Überblick: Von Rollen zu Gruppen

### **Konzeptuelle Verschiebung**

**VORHER (RBAC 2.0 - DEPRECATED):**
```
Ein User = EINE Rolle (1:1 Zuordnung)

┌──────────┐
│   User   │
└────┬─────┘
     │
     ↓
   [Admin]    ← nur EINE Rolle möglich
   [Teacher]
   [Student]
   ...
```

**NACHHER (Group-Based - AKTUELL):**
```
Ein User = MEHRERE Gruppen (Many-to-Many)

┌──────────┐
│   User   │
└────┬─────┘
     │
     ├─→ [Admin]      ← Group 1
     ├─→ [Teacher]    ← Group 2
     ├─→ [Moderator]  ← Group 3
     └─→ [Custom-Gruppe "Team Finance"]  ← Custom Group
```

**Was sich ändert:**

| Aspekt | RBAC 2.0 (Alt) | Group-Based (Neu) |
|--------|---|---|
| **User-Zuordnung** | 1:1 (`users.role`) | Many-to-Many (`group_members` Tabelle) |
| **Permission-Berechnung** | Direkter Lookup `roles.permissions` | Set Union aus ALLEN User-Gruppen |
| **Neue Gruppen** | Nur DB Schema Change | Nur DB INSERT in `core.groups` |
| **User-Verwaltung** | `UPDATE users SET role='teacher'` | `INSERT INTO group_members (user, group)` |
| **Fehlerfall** | ❌ 500 Error | ✅ 403 Forbidden (Fail-Secure) |
| **Scalability** | Limitiert auf 10-20 Rollen | Unbegrenzt (custom Groups) |

---

## 📋 6 Vordefinierte Gruppen

Diese 6 Gruppen sind in JEDEM System verfügbar und können nicht gelöscht werden:

### 1. **Admin Group**
**Beschreibung:** Systemweiter Administrator. Volles System-Management.

**Permissions:**
- `admin:system` - Gesamtes System verwalten
- `users:manage:all` - Alle Benutzer verwalten
- `groups:manage:all` - Alle Gruppen erstellen/löschen
- `permissions:assign:all` - Alle Permissions vergeben
- `audit:view:all` - Alle Audit-Logs einsehen
- `settings:system` - System-Einstellungen ändern

**Typische User:**
- Plattform-Administratoren
- DevOps-Team
- Sicherheitsbeauftragte

**Mapping von Alt-Rollen:**
- RBAC 2.0 `role='admin'` → jetzt Member der Admin-Group

---

### 2. **Teacher Group**
**Beschreibung:** Kurs-Erstellung und Verwaltung, Studierenden-Betreuung.

**Permissions:**
- `courses:create` - Neue Kurse erstellen
- `courses:edit:own` - Eigene Kurse bearbeiten
- `courses:publish` - Kurse veröffentlichen
- `chapters:manage` - Kapitel/Lektionen verwalten
- `students:view:enrolled` - Eingeschriebene Studierende sehen
- `grades:assign` - Noten vergeben
- `feedback:send` - Feedback an Studierende

**Typische User:**
- Universität-Dozenten
- Unternehmens-Trainer
- Schullehrer

**Mapping von Alt-Rollen:**
- RBAC 2.0 `role='lehrer'` / `role='teacher'` → Teacher-Group
- RBAC 2.0 `role='schule'` (Schulleiter) → Teacher-Group + Admin-Group (Org-Admin)
- RBAC 2.0 `role='unternehmen'` (Trainer) → Teacher-Group

---

### 3. **Creator Group**
**Beschreibung:** Content-Creator. Inhalte erstellen (ohne Publikations-Recht).

**Permissions:**
- `content:create` - Inhalte erstellen
- `learning-methods:use` - Lernmethoden verwenden
- `ai:content-generation` - KI Content-Generator nutzen
- `ai:auto-correction` - Auto-Correction für Aufgaben
- `files:upload` - Dateien hochladen (max 100MB pro Datei)
- `content:preview` - Eigene Inhalte preview
- `templates:use:shared` - Shared Templates nutzen

**Typische User:**
- Freiberufliche Content-Creator
- Lehrbuch-Autoren
- Instructional Designer

**Mapping von Alt-Rollen:**
- RBAC 2.0 `role='creator'` → Creator-Group
- RBAC 2.0 `role='premium'` (mit Creators-Features) → Creator-Group

---

### 4. **Student Group**
**Beschreibung:** Lernende. Zugang zu Kursen und Lernmaterialien.

**Permissions:**
- `courses:enroll` - Sich in Kurse einschreiben
- `lessons:access` - Lektionen zugreifen
- `learning-methods:execute` - Lernmethoden durchführen
- `progress:track` - Eigenen Fortschritt sehen
- `quizzes:take` - Quizze absolvieren
- `certificates:earn` - Zertifikate erhalten
- `feedback:receive` - Feedback erhalten
- `social:participate` - In Diskussionen teilnehmen

**Typische User:**
- Studentinnen und Studenten
- Unternehmens-Mitarbeiter in Trainings
- Online-Lernende (Allgemein)

**Mapping von Alt-Rollen:**
- RBAC 2.0 `role='student'` → Student-Group
- RBAC 2.0 `role='free'` / `role='premium'` (Lernende) → Student-Group
- Automatisch zugewiesen bei User-Registrierung

---

### 5. **Support Group**
**Beschreibung:** Support-Team. Benutzer-Unterstützung und Ticket-Management.

**Permissions:**
- `tickets:view` - Support-Tickets sehen
- `tickets:respond` - Auf Tickets antworten
- `users:view` - Benutzer-Informationen einsehen
- `org:support` - Organisationale Support-Funktionen
- `compliance:reports` - Compliance-Reports erstellen
- `audit:view:org` - Org-Audit-Logs einsehen

**Typische User:**
- Support-Mitarbeiter
- Customer Success Manager
- Compliance Officer

**Mapping von Alt-Rollen:**
- RBAC 2.0 `role='support'` → Support-Group

---

### 6. **Moderator Group**
**Beschreibung:** Content-Moderation. DSA/NetzDG Compliance.

**Permissions:**
- `content:review` - Inhalte reviewen
- `content:moderate` - Inhalte moderieren (löschen/sperren)
- `users:suspend` - Benutzer sperren
- `violations:view` - Violations sehen
- `appeals:review` - Appeals reviewen
- `dsa:reports` - DSA-Reports erstellen

**Typische User:**
- Content-Moderatoren
- Compliance-Monitors
- DSA-Beauftrag- (Digital Services Act)

**Mapping von Alt-Rollen:**
- RBAC 2.0 `role='moderator'` → Moderator-Group

---

## 🎯 Custom Groups (Benutzerdefinierte Gruppen)

Zusätzlich zu den 6 vordefinierten Gruppen können Organisations-Admins BELIEBIG VIELE Custom-Gruppen erstellen:

### Beispiele:

**1. Team-basierte Gruppen:**
```
- Team-Finance (Finanz-Team-Zugang)
- Team-Marketing (Marketing-Spezific-Features)
- Team-HR (HR-Daten-Zugang)
```

**2. Klassen-basierte Gruppen (Schulen):**
```
- Klasse-9A (alle Schüler dieser Klasse)
- Klasse-11B (alle Schüler dieser Klasse)
```

**3. Projekt-basierte Gruppen:**
```
- ProjectX-Team (Projekt X Mitglieder)
- AI-Research-Group (KI-Forschungsteam)
```

**4. Zugangs-basierte Gruppen:**
```
- Beta-Testers (Early-Access Features)
- Enterprise-Premium (Enterprise-Features)
```

**Erstellen einer Custom-Gruppe:**
```sql
INSERT INTO core.groups (id, organisation_id, name, description, is_predefined)
VALUES (
  'grp_custom_finance',
  'org_123',
  'Team-Finance',
  'Zugang zu Finanz-Daten und Reports',
  FALSE
);

-- Dann: Permissions zu dieser Gruppe hinzufügen
INSERT INTO core.group_permissions (group_id, permission_code)
VALUES ('grp_custom_finance', 'finance:reports:view');

-- Dann: User zu Gruppe hinzufügen
INSERT INTO core.group_members (user_id, group_id)
VALUES ('user_456', 'grp_custom_finance');
```

---

## 👥 User-Szenarios: Multiple Gruppen

### **Szenario 1: Teacher mit Admin-Rechten (Schulleiter)**

```
User: Anna Schmidt (Schulleiter)

Gruppen:
├─ Teacher       (Kurs-Erstellung, Studierenden-Verwaltung)
├─ Moderator     (Content-Moderation)
└─ Admin         (Schul-System-Admin)

Permissions (Set Union):
  courses:create
  grades:assign
  content:moderate
  admin:system
  users:manage:all
  ...
```

**Früher (RBAC 2.0):** Anna hätte nur EINE Rolle (z.B. `role='teacher'` oder `role='admin'`). Widerspruch!

---

### **Szenario 2: Student + Content-Creator (Hybrid-Rolle)**

```
User: Bob Chen (Student & Influencer)

Gruppen:
├─ Student       (Teilnehmer in Kursen)
├─ Creator       (Eigene Inhalte erstellen)
└─ Custom: Influencer (Spezial-Features für Top-Creator)

Permissions (Set Union):
  courses:enroll
  lessons:access
  content:create
  ai:content-generation
  social:participate
  influencer:analytics
  ...
```

**Früher (RBAC 2.0):** Bob konnte nicht gleichzeitig Student UND Creator sein!

---

### **Szenario 3: Enterprise-Team mit Spezial-Zugang**

```
User: Carol Davis (Finance-Team-Lead)

Gruppen:
├─ Teacher              (darf Schulungen geben)
├─ Custom: Team-Finance (Zugang zu Finance-Tools)
└─ Support             (helfen anderen Users)

Permissions (Set Union):
  courses:create
  finance:reports:view
  finance:budgets:edit
  tickets:respond
  ...
```

---

## 🔐 Gruppentrennung (Authorization Boundaries)

### **Verbotene Gruppenkombinationen**

Manche Gruppen dürfen **NICHT zusammen** auftauchen (wegen Conflict of Interest oder Security):

| Gruppe 1 | Gruppe 2 | Grund | Lösung |
|----------|----------|-------|--------|
| **Moderator** | **Creator** (eigene Content) | Moderator könnte eigene Content bevorzugen | Moderieren nur von OTHER Content |
| **Admin** | **Creator** | Admin-Content hat automatisch Priorität | Use separate User-Accounts |
| **Support** | **User-Management** | Support sieht Tickets → könnte User-Daten missbrauchen | Role-basierte Data-Masking |

**Implementierung:**
```python
# In app/repositories/permission.py

def add_user_to_group(user_id: str, group_id: str) -> bool:
    """
    Add user to group (mit Conflict-Checking).

    Raises ValidationError wenn verbotene Kombination.
    """

    # Get user's current groups
    current_groups = self.get_user_groups(user_id)

    # Define forbidden combinations
    FORBIDDEN_PAIRS = [
        ('moderator', 'creator'),  # Moderator darf nicht Creator sein
        ('admin', 'creator'),       # Admin darf nicht Creator sein (separater Account)
    ]

    # Check if new group violates policy
    for forbidden_pair in FORBIDDEN_PAIRS:
        if (group_id in [g.id for g in current_groups] and
            forbidden_pair[0] == group_id and
            forbidden_pair[1] in current_groups):
            raise ValidationException(
                f"Cannot add user to {group_id}: conflicts with existing {forbidden_pair[1]}"
            )

    # All checks passed → add to group
    self.conn.execute(
        "INSERT INTO core.group_members (user_id, group_id) VALUES (%s, %s)",
        (user_id, group_id)
    )
```

---

## 📈 Upgrade-Pfade (Feature-Freischaltung)

### **Alte Upgrade-Pfade (RBAC 2.0):**

```
Free User → Premium User → Creator → (Lehrer) → (Schule/Unternehmen) → Admin
    ↑
   1:1 Role Progression
```

### **Neue Upgrade-Pfade (Group-Based):**

User können jetzt **non-linear** multiple Gruppen hinzubekommen:

```
Registrierung
    ↓
Auto-Zuordnung: Student-Group
    ↓
User wählt: "Ich möchte Content erstellen"
    ↓
Admin fügt hinzu: Creator-Group (ZUSÄTZLICH zu Student)
    ↓
User hat jetzt: [Student, Creator]
    ↓
Optional: Später auch Teacher-Group hinzufügen
    ↓
Result: [Student, Creator, Teacher]
```

**Feature-Freischaltung nach Gruppen:**

```python
# In frontend/src/utils/featureAccess.ts

export function hasFeature(user, featureCode: string): boolean {
  const userGroups = user.groups.map(g => g.id)

  const FEATURE_MATRIX = {
    'courses.create': ['teacher', 'creator'],
    'ai.content-generation': ['creator', 'teacher'],
    'content.moderate': ['moderator'],
    'users.manage': ['admin'],
    'finance.reports': ['custom_team-finance'],
    'influencer.analytics': ['custom_influencer'],
  }

  const requiredGroups = FEATURE_MATRIX[featureCode] || []
  return requiredGroups.some(g => userGroups.includes(g))
}
```

---

## 📊 Zusammenfassung: Alte vs. Neue Modell

### **Vergleich-Tabelle**

| Kriterium | RBAC 2.0 (Alt) | Group-Based (Neu) |
|-----------|---|---|
| **User-Rollen-Mapping** | 1:1 (One role per user) | Many-to-Many (Multiple groups per user) |
| **Basis-Rollen** | 9 Rollen (Free, Premium, Creator, Teacher, School, Company, Support, Moderator, Admin) | 6 Predefined Groups + Custom Groups |
| **Permission-Model** | Hardcoded role → permissions | Dynamic: Set Union aus ALLEN user groups |
| **Neue Rollen hinzufügen** | DB Schema Change + Code Update | Just DB INSERT in `core.groups` |
| **User zu Rolle** | `UPDATE users SET role='teacher'` | `INSERT INTO group_members` |
| **Fehler-Handling** | ❌ Permission-Error → 500 Error | ✅ Permission-Error → 403 Forbidden (Fail-Secure) |
| **Skalierbarkeit** | Limitiert (10-20 Rollen max) | Unbegrenzt (custom groups) |
| **Hybrid-Rollen (z.B. Student + Creator)** | ❌ Impossible (1:1 mapping) | ✅ Fully supported |
| **Admin-Komplexität** | Mittel (verstehe Rollen-Hierarchie) | Niedrig (einfach User zu Gruppen hinzufügen) |
| **Audit Trail** | Per Application-Logging | Built-in: Timestamps in group_members + group_permissions |
| **Migration** | N/A (Neu) | Alter users.role → neue group_members |

---

## ✅ Migration: Von alt zu neu

**Für bestehende Installations-Daten:**

```sql
-- Step 1: Create standard groups (if not exist)
INSERT INTO core.groups (id, organisation_id, name, is_predefined)
SELECT 'grp_admin_' || org_id, org_id, 'Admin', TRUE
FROM core.organisations
ON CONFLICT DO NOTHING;

-- Step 2: Migrate old role → new group
INSERT INTO core.group_members (user_id, group_id)
SELECT
  u.id,
  CASE u.role
    WHEN 'admin' THEN 'grp_admin_' || u.organisation_id
    WHEN 'teacher' THEN 'grp_teacher_' || u.organisation_id
    WHEN 'creator' THEN 'grp_creator_' || u.organisation_id
    WHEN 'student' THEN 'grp_student_' || u.organisation_id
    WHEN 'support' THEN 'grp_support_' || u.organisation_id
    WHEN 'moderator' THEN 'grp_moderator_' || u.organisation_id
    ELSE 'grp_student_' || u.organisation_id  -- Default to Student
  END AS group_id
FROM core.users u
WHERE u.role IS NOT NULL
ON CONFLICT DO NOTHING;

-- Step 3: Deprecate old role column (keep for rollback)
ALTER TABLE core.users ADD COLUMN role_deprecated VARCHAR(50);
UPDATE core.users SET role_deprecated = role;
-- Don't delete users.role yet - keep for rollback!
```

---

## 📝 Dokument-Status

**Überarbeitungs-Historie:**

| Version | Datum | Änderung | Status |
|---------|-------|----------|--------|
| 1.0 | 2025-XX-XX | Initiiale RBAC 2.0 Dokumentation (Role-Based) | Archived |
| 2.0 | 2026-01-21 | Umstellung auf Group-Based System | ✅ CURRENT |

**Zukunfts-Änderungen:**

- Phase 2: Exakte SQL-Migrations-Schema (Tabellen: `core.groups`, `core.group_members`, `core.group_permissions`)
- Phase 3: Backend-PermissionRepository Implementierung mit Fail-Secure Design
- Phase 4: Frontend Group-Management UI (rename Role-Studio → Group-Management)
- Phase 5: Data Migration, Rollback-Verfahren, Produktions-Deployment

---

**Dokument abgeschlossen:** ✅
**Gültig ab:** 2026-01-21
**Nächste Überprüfung:** Nach Phase 2 (Datenmodell-Definition)
