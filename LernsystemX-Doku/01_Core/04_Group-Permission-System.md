# 04 – Group-Based Permission System (GBA)

**Version:** 1.0
**Status:** ACTIVE (Replaces RBAC 2.0)
**Implementation Phase:** Phase 2-5 (Planning → Testing)

---

## 🎯 Überblick

Das **Group-Based Permission System (GBA)** ersetzt die komplexe RBAC 2.0 Architektur durch ein intuitives, flexibles Many-to-Many Modell. Ein User kann mehreren Gruppen gleichzeitig angehören und erhält damit Zugriff auf alle Permissions, die diese Gruppen haben.

### Warum ein neuer Ansatz?

| Aspekt | RBAC 2.0 (ALT) | Group-Based (NEU) |
|--------|---|---|
| **Struktur** | 1 User = 1 Role | 1 User = N Groups |
| **Flexibilität** | Limited (fixed roles) | Flexible (custom groups) |
| **Skalierbarkeit** | Schwach (custom roles too complex) | Stark (simple Many-to-Many) |
| **User-Experience** | Kompliziert | Intuitiv |
| **Verwaltung** | Zentral (hard to delegate) | Dezentral (org admins can manage) |
| **Ressourcen-Ownership** | ❌ Nicht unterstützt | ✅ Owner Groups (automatisch) |

### Group-Typen im System (4-EBENEN HIERARCHIE)

**EBENE 1: Site-Level Owner-Admin** ⭐ GLOBAL
- Nur der **Platform Founder** (eine Person)
- Hat ALLE Rechte über ALLE Organisationen
- Verwaltet: Platform Settings, Feature Flags, Compliance global
- **Super-Admin über alle Org-Level Owner-Admins**

**EBENE 2: Org-Level Owner-Admin** ⭐ PRO ORGANISATION
- Der **Gründer einer Organisation** (z.B. Schulleiter, CEO)
- Hat volle Kontrolle über EINE Organisation
- Kann: Org-Settings, Billing, Branding, Admins ernennen, Ownership transferieren
- **Kann nicht:**  Andere Orgs verwalten, Platform-Settings ändern
- Benannte Gruppe: `owner-admin` (pro Org)

**EBENE 3: Standard Admin** ⭐ PRO ORGANISATION
- Ernennt vom Owner-Admin
- Verwaltet: Users, Gruppen, Permissions, System-Settings
- **Kann nicht:** Org löschen, Ownership transferieren, Billing

**EBENE 4: Standard Gruppen** (TEMPLATE-BASIERT)
- Nicht hardcoded! Werden aus **Group Templates** erstellt
- Beispiele: Teacher, Creator, Student, Support, Moderator
- Variiert je nach Template (School, Corporate, Online, etc.)
- **Können nicht gelöscht werden** (`is_predefined = TRUE`)
- Können vom Owner-Admin angepasst werden

---

### Group Templates System (NEU) 🎯

Statt hardcoded Rollen verwenden wir **Template-basierte Gruppen**:

**3-EBENEN STRUKTUR:**

```
EBENE 1: STANDARD PERMISSIONS (HARDCODED - System-Level, Immutable)
├── Definiert im Backend-Code
├── Beispiele: courses:create, content:edit, admin:system, users:manage
├── NICHT konfigurierbar (nur durch Code-Update änderbar)
└── Global über alle Organisationen

EBENE 2: GROUP TEMPLATES (VORDEFINIERT, ABER KONFIGURIERBAR via templates_*)
├── Definiert in group_templates Tabelle (Seed-Daten)
├── Jedes Template hat predefined group_types (via template_groups)
├──
├── School Template (template_code: 'school')
│   ├── Group Types aus template_groups:
│   │   ├── 'teacher' (from template) → Permissions aus template_group_permissions
│   │   ├── 'student' (from template) → Permissions aus template_group_permissions
│   │   ├── 'creator' (from template) → Permissions aus template_group_permissions
│   │   ├── 'moderator' (from template) → Permissions aus template_group_permissions
│   │   └── 'support' (from template) → Permissions aus template_group_permissions
│   └── Owner-Admin wählt Template bei Org-Gründung → automatisch erstellt
│
├── Corporate Template (template_code: 'corporate')
│   ├── Group Types: 'manager', 'developer', 'employee', 'viewer', 'support', ...
│   └── [Analog zu School Template]
│
├── Online-Course Template (template_code: 'online')
│   ├── Group Types: 'instructor', 'creator', 'learner', 'moderator', ...
│   └── [Analog zu School Template]
│
└── Education-Provider Template (template_code: 'education-provider')
    ├── Group Types: 'school-admin', 'teacher', 'student', 'support', ...
    └── [Analog zu School Template]

⚠️ WICHTIG: Gruppe-Namen sind NICHT hardcoded im Code!
    → Sie kommen aus template_groups.group_name Spalte
    → Können via Admin-UI angepasst werden (Name, Beschreibung)
    → Aber template-group sind geschützt (is_predefined = TRUE)

EBENE 3: CUSTOM GROUPS (ORG-DEFINIERT, Vollständig Konfigurierbar)
├── Erstellt von Org-Admin direkt
├── Keine Template-Einschränkungen
├──
├── Subscription Groups (Abo-Modelle):
│   ├── auto:premium (erstellt wenn Premium-Abo-Plan erstellt wird)
│   ├── auto:starter (erstellt wenn Starter-Abo-Plan erstellt wird)
│   └── auto:pro (erstellt wenn Pro-Abo-Plan erstellt wird)
│   → User automatisch added/removed bei Abo-Kauf/Kündigung
│
├── Team Groups (Org-Abteilungen):
│   ├── team:finance, team:marketing, team:sales
│   └── Org-spezifische Teams
│
├── Cohort Groups (Lerngruppen):
│   ├── cohort-2024-fall, cohort-2024-spring
│   └── Für Lernmanagemnt
│
└── Partner Groups (Kooperationen):
    ├── partner:external-org-xyz, partner:vendor-abc
    └── Für B2B / Kooperationen
```

**Wie funktioniert es?**

```
SCHRITT 1: Neue Organisation gründen (z.B. "Gymnasium München")
   ↓
SCHRITT 2: Owner-Admin wählt Template: "School Template" (template_code: 'school')
   ↓
SCHRITT 3: Backend lädt Template-Konfiguration aus Datenbank:
   └── SELECT group_types FROM template_groups
       WHERE template_id = school_template.id

   → Teacher (group_name aus template_groups[0])
   → Student (group_name aus template_groups[1])
   → Creator (group_name aus template_groups[2])
   → Moderator (group_name aus template_groups[3])
   → Support (group_name aus template_groups[4])

   Für jede Gruppe laden die Permissions:
   └── SELECT permissions FROM template_group_permissions
       WHERE template_group_id = X

SCHRITT 4: Backend erstellt automatisch in organisation_X:
   └── 5 neue Groups mit:
       - name, description von template_groups
       - is_predefined = TRUE (können nicht gelöscht werden)
       - Alle Permissions aus template_group_permissions

   Plus:
   └── owner-admin Group (für Org-Gründer/Besitzer)

SCHRITT 5: Owner-Admin kann später:
   ✅ Custom Groups hinzufügen (z.B. "Klasse-9A", "Team Finance")
   ✅ Subscription Groups erstellen (z.B. "abo:premium")
   ✅ Permissions anpassen für alle Gruppen (template + custom)
   ⚠️ Template-Gruppen UMBENENNEN: Ja (via groups.name ändern)
   ❌ Template-Gruppen LÖSCHEN: Nein (is_predefined = TRUE verhindert das)
   ✅ Neue Gruppen löschen: Ja (bei custom groups)
```

---

**5. Owner Groups (Ressourcen-Level) ⭐**
- Automatisch erstellt für jede Ressource
- User der Ressource erstellt = automatisch Owner
- Naming: `owner:course:ABC123`, `owner:content:XYZ456`
- Können gelöscht werden wenn Ressource gelöscht wird
- Ermöglichen Delegation (Co-Owner hinzufügen)
- Beispiel: "Owners von Kurs Mathematik 101"

**6. Custom Subscription Groups (Abo-Modelle) ⭐ NEW**
- Automatisch erstellt basierend auf Subscription-Plan
- Naming: `abo:premium`, `abo:starter`, `abo:pro`
- User wird automatisch hinzugefügt wenn Subscription gekauft wird
- User wird automatisch entfernt wenn Subscription endet
- Haben spezifische Permissions (z.B. AI-Features für Premium)
- Org-weit, können gelöscht werden wenn Abo-Plan gelöscht wird

---

## 📋 System-Architektur

### C4 Context Diagram

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

title Group-Based Permission System (GBA) Architecture

Person(user, "User", "LSX User")
Person(admin, "Admin", "Admin/Org Manager")

System(gba, "Group-Based Permission System", "User Group & Permission Management")

System_Ext(auth, "Auth Service", "JWT Validation")
System_Ext(db, "Database", "PostgreSQL")
System_Ext(cache, "Cache", "Redis")

Rel(user, gba, "Authenticate & Request Resources", "HTTPS")
Rel(admin, gba, "Manage Groups & Permissions", "HTTPS")

Rel(gba, auth, "Validate Tokens", "REST API")
Rel(gba, db, "Read/Write Groups & Permissions", "SQL")
Rel(gba, cache, "Cache Permission Decisions", "Redis")

@enduml
```

---

## 🗄️ Datenmodell

### 1. Groups Table

```sql
CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_predefined BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organisation_id, name),
    CHECK (name ~ '^[a-zA-Z0-9_\-]{3,50}$')
);

-- Indices für Performance
CREATE INDEX idx_groups_organisation_id ON groups(organisation_id);
CREATE INDEX idx_groups_is_predefined ON groups(is_predefined);
```

**Felder:**
- `id`: Eindeutige Gruppen-ID (UUID)
- `organisation_id`: Organisation, der die Gruppe gehört (Tenant Isolation)
- `name`: Eindeutiger Name innerhalb der Organisation (z.B. "Admin", "Teacher", "Klasse-9A")
- `description`: Optionale Beschreibung der Gruppe
- `is_predefined`: Flag für vordefinierte Gruppen (können nicht gelöscht werden)
- `created_at`, `updated_at`: Audit-Felder

**Spezialfall: Owner Groups**
- Owner Groups haben Namen wie: `owner:course:ABC123`, `owner:content:XYZ456`, `owner:group:DEF789`
- `is_predefined` = FALSE (werden dynamisch erstellt)
- Werden automatisch erstellt wenn User eine Ressource erstellt
- Können gelöscht werden wenn Ressource gelöscht wird

---

### 1a. Owner Groups Table (NEW)

```sql
CREATE TABLE owner_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type VARCHAR(50) NOT NULL,  -- 'course', 'content', 'group'
    resource_id UUID NOT NULL,           -- ID des Kurses/Content/Gruppe
    organisation_id UUID NOT NULL REFERENCES organisations(id),
    creator_user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(resource_type, resource_id),
    CHECK (resource_type IN ('course', 'content', 'group', 'project'))
);

-- Mapped to groups table via view
CREATE VIEW owner_groups_mapped AS
SELECT
    og.id as owner_group_id,
    og.resource_type,
    og.resource_id,
    og.creator_user_id,
    g.id as group_id,
    g.name as group_name,
    og.organisation_id
FROM owner_groups og
LEFT JOIN groups g ON
    g.name = CONCAT('owner:', og.resource_type, ':', og.resource_id)
    AND g.organisation_id = og.organisation_id;

-- Index für Performance
CREATE INDEX idx_owner_groups_resource ON owner_groups(resource_type, resource_id);
CREATE INDEX idx_owner_groups_creator ON owner_groups(creator_user_id);
```

**Felder:**
- `resource_type`: Typ der Ressource ('course', 'content', 'group')
- `resource_id`: ID der spezifischen Ressource
- `creator_user_id`: Der User der die Ressource erstellt hat (Owner)
- `organisation_id`: Tenant-Isolation

**Automatische Triggers:**
```sql
-- Trigger: Wenn Owner Group erstellt wird, auch Group erstellen
CREATE OR REPLACE FUNCTION create_owner_group()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO groups (
        organisation_id,
        name,
        description,
        is_predefined
    ) VALUES (
        NEW.organisation_id,
        CONCAT('owner:', NEW.resource_type, ':', NEW.resource_id),
        CONCAT('Owners of ', NEW.resource_type, ' ', NEW.resource_id),
        FALSE
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_create_owner_group
AFTER INSERT ON owner_groups
FOR EACH ROW
EXECUTE FUNCTION create_owner_group();

-- Trigger: Creator automatisch zu Owner Group hinzufügen
CREATE OR REPLACE FUNCTION add_creator_to_owner_group()
RETURNS TRIGGER AS $$
DECLARE
    owner_group_id UUID;
BEGIN
    -- Group finden
    SELECT id INTO owner_group_id
    FROM groups
    WHERE name = CONCAT('owner:', NEW.resource_type, ':', NEW.resource_id)
    AND organisation_id = NEW.organisation_id
    LIMIT 1;

    -- Creator zur Gruppe hinzufügen
    IF owner_group_id IS NOT NULL THEN
        INSERT INTO group_members (user_id, group_id, assigned_by)
        VALUES (NEW.creator_user_id, owner_group_id, NEW.creator_user_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_add_creator_to_owner_group
AFTER INSERT ON owner_groups
FOR EACH ROW
EXECUTE FUNCTION add_creator_to_owner_group();
```

---

### 2. Group Members Table (Many-to-Many)

```sql
CREATE TABLE group_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    group_id UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    UNIQUE(user_id, group_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

-- Index für schnelle Abfragen
CREATE INDEX idx_group_members_user_id ON group_members(user_id);
CREATE INDEX idx_group_members_group_id ON group_members(group_id);
```

**Felder:**
- `id`: Eindeutige Zuordnungs-ID
- `user_id`: User-ID (Many-to-Many Key)
- `group_id`: Gruppen-ID (Many-to-Many Key)
- `assigned_at`: Wann wurde der User zur Gruppe hinzugefügt
- `assigned_by`: Welcher Admin hat den User hinzugefügt (Audit Trail)

---

### 3. Group Permissions Table

```sql
CREATE TABLE group_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    permission_code VARCHAR(100) NOT NULL,
    granted_at TIMESTAMP DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    UNIQUE(group_id, permission_code),
    CHECK (permission_code ~ '^[a-z_]+\.[a-z_]+(\.[a-z_]+)?$')
);

-- Index für schnelle Abfragen
CREATE INDEX idx_group_permissions_group_id ON group_permissions(group_id);
CREATE INDEX idx_group_permissions_code ON group_permissions(permission_code);
```

**Felder:**
- `id`: Eindeutige Permissions-ID
- `group_id`: Welche Gruppe hat diese Permission
- `permission_code`: Code der Permission (z.B. "courses.create", "users.manage.all")
- `granted_at`: Wann wurde die Permission gewährt
- `granted_by`: Welcher Admin hat die Permission gewährt

---

### 4. Group Templates Tables (NEW)

```sql
-- Group Templates: Vordefinierte Template-Konfigurationen
CREATE TABLE group_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_code VARCHAR(50) NOT NULL UNIQUE,  -- 'school', 'corporate', 'online', 'education-provider'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),                       -- 'education', 'corporate', 'online'
    is_predefined BOOLEAN DEFAULT TRUE,         -- Platform-Standardtemplate
    config JSONB,                               -- Template-Konfiguration (flexible)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Template-Gruppen: Welche Gruppen gehören zu einem Template
CREATE TABLE template_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES group_templates(id) ON DELETE CASCADE,
    group_name VARCHAR(255) NOT NULL,           -- z.B. 'Teacher', 'Student', 'Manager'
    description TEXT,
    display_order INT DEFAULT 0,                -- Reihenfolge in UI
    is_required BOOLEAN DEFAULT TRUE,           -- Muss immer erstellt werden
    created_at TIMESTAMP DEFAULT NOW()
);

-- Template-Permissions: Welche Permissions gehören zu welcher Template-Gruppe
CREATE TABLE template_group_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_group_id UUID NOT NULL REFERENCES template_groups(id) ON DELETE CASCADE,
    permission_code VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT TRUE,            -- Wird standardmäßig gewährt
    can_override BOOLEAN DEFAULT TRUE,          -- Admin kann ändern
    created_at TIMESTAMP DEFAULT NOW()
);

-- Organisation-Template-Zuordnung: Welches Template nutzt welche Org
CREATE TABLE organisation_group_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES group_templates(id),
    selected_at TIMESTAMP DEFAULT NOW(),
    can_modify_template BOOLEAN DEFAULT TRUE,   -- Kann Admin das Template anpassen?
    UNIQUE(organisation_id, template_id)
);

-- Subscription Groups: Für Abo-Modelle
CREATE TABLE subscription_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organisation_id UUID NOT NULL REFERENCES organisations(id) ON DELETE CASCADE,
    subscription_plan_code VARCHAR(100) NOT NULL,  -- 'premium', 'starter', 'pro'
    group_id UUID NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organisation_id, subscription_plan_code)
);

-- Indices für Performance
CREATE INDEX idx_group_templates_code ON group_templates(template_code);
CREATE INDEX idx_template_groups_template ON template_groups(template_id);
CREATE INDEX idx_template_perms_template_group ON template_group_permissions(template_group_id);
CREATE INDEX idx_org_templates_org ON organisation_group_templates(organisation_id);
CREATE INDEX idx_subscription_groups_org ON subscription_groups(organisation_id);
```

**Seed-Daten: Vordefinierte Group Templates**

```sql
-- 1. SCHOOL TEMPLATE
INSERT INTO group_templates (template_code, name, category)
VALUES ('school', 'School/Education Organization', 'education');

-- Template-Gruppen für School
INSERT INTO template_groups (template_id, group_name, description, display_order)
SELECT id, 'Owner-Admin', 'Schulleiter/Direktor (höchste Autorität)', 0 FROM group_templates WHERE template_code = 'school'
UNION ALL
SELECT id, 'Teacher', 'Lehrer und Kursersteller', 1 FROM group_templates WHERE template_code = 'school'
UNION ALL
SELECT id, 'Creator', 'Content-Ersteller mit AI-Zugriff', 2 FROM group_templates WHERE template_code = 'school'
UNION ALL
SELECT id, 'Student', 'Schüler mit Kurszugriff', 3 FROM group_templates WHERE template_code = 'school'
UNION ALL
SELECT id, 'Moderator', 'Content-Moderator', 4 FROM group_templates WHERE template_code = 'school'
UNION ALL
SELECT id, 'Support', 'Schul-Support-Team', 5 FROM group_templates WHERE template_code = 'school';

-- 2. CORPORATE TEMPLATE
INSERT INTO group_templates (template_code, name, category)
VALUES ('corporate', 'Corporate/Enterprise Organization', 'corporate');

-- Template-Gruppen für Corporate
INSERT INTO template_groups (template_id, group_name, description, display_order)
SELECT id, 'Owner-Admin', 'CEO/Geschäftsführer (höchste Autorität)', 0 FROM group_templates WHERE template_code = 'corporate'
UNION ALL
SELECT id, 'Manager', 'Abteilungsleiter und Trainer', 1 FROM group_templates WHERE template_code = 'corporate'
UNION ALL
SELECT id, 'Developer', 'Inhalts-/Kurs-Entwickler', 2 FROM group_templates WHERE template_code = 'corporate'
UNION ALL
SELECT id, 'Employee', 'Mitarbeiter/Lerner', 3 FROM group_templates WHERE template_code = 'corporate'
UNION ALL
SELECT id, 'Viewer', 'Schreibgeschützt Zugriff', 4 FROM group_templates WHERE template_code = 'corporate'
UNION ALL
SELECT id, 'Support', 'HR/Support-Team', 5 FROM group_templates WHERE template_code = 'corporate';

-- 3. ONLINE-COURSE TEMPLATE
INSERT INTO group_templates (template_code, name, category)
VALUES ('online-course', 'Online Course Platform', 'online');

-- Template-Gruppen für Online-Course
INSERT INTO template_groups (template_id, group_name, description, display_order)
SELECT id, 'Owner-Admin', 'Plattform-Owner (höchste Autorität)', 0 FROM group_templates WHERE template_code = 'online-course'
UNION ALL
SELECT id, 'Instructor', 'Kurs-Instruktoren', 1 FROM group_templates WHERE template_code = 'online-course'
UNION ALL
SELECT id, 'Creator', 'Content-Ersteller', 2 FROM group_templates WHERE template_code = 'online-course'
UNION ALL
SELECT id, 'Learner', 'Kursteilnehmer', 3 FROM group_templates WHERE template_code = 'online-course'
UNION ALL
SELECT id, 'Moderator', 'Community-Moderator', 4 FROM group_templates WHERE template_code = 'online-course';

-- 4. EDUCATION-PROVIDER TEMPLATE
INSERT INTO group_templates (template_code, name, category)
VALUES ('education-provider', 'Education Service Provider', 'education');

-- Template-Gruppen für Education-Provider
INSERT INTO template_groups (template_id, group_name, description, display_order)
SELECT id, 'Owner-Admin', 'Organisationsleiter (höchste Autorität)', 0 FROM group_templates WHERE template_code = 'education-provider'
UNION ALL
SELECT id, 'SchoolAdmin', 'Schul-Administrator', 1 FROM group_templates WHERE template_code = 'education-provider'
UNION ALL
SELECT id, 'Teacher', 'Lehrer', 2 FROM group_templates WHERE template_code = 'education-provider'
UNION ALL
SELECT id, 'Student', 'Schüler', 3 FROM group_templates WHERE template_code = 'education-provider'
UNION ALL
SELECT id, 'Creator', 'Content-Ersteller', 4 FROM group_templates WHERE template_code = 'education-provider'
UNION ALL
SELECT id, 'SchoolSupport', 'Schul-Support', 5 FROM group_templates WHERE template_code = 'education-provider'
UNION ALL
SELECT id, 'Moderator', 'Content-Moderator', 6 FROM group_templates WHERE template_code = 'education-provider';
```

**Beispiel: Permissions für School Template, Teacher Gruppe**

```sql
-- School Template → Teacher Gruppe → Permissions
INSERT INTO template_group_permissions (template_group_id, permission_code)
SELECT tg.id, 'courses:create' FROM template_groups tg
JOIN group_templates gt ON tg.template_id = gt.id
WHERE gt.template_code = 'school' AND tg.group_name = 'Teacher'
UNION ALL
SELECT tg.id, 'courses:edit:own' FROM template_groups tg
JOIN group_templates gt ON tg.template_id = gt.id
WHERE gt.template_code = 'school' AND tg.group_name = 'Teacher'
UNION ALL
SELECT tg.id, 'courses:publish' FROM template_groups tg
JOIN group_templates gt ON tg.template_id = gt.id
WHERE gt.template_code = 'school' AND tg.group_name = 'Teacher'
... (weitere Teacher Permissions für School);
```

---

## 🔌 API Spezifikation

### Authentifizierung & Permission Check

```python
# Backend: Permission Check Logic
def has_permission(user_id: str, permission_code: str, org_id: str) -> bool:
    """
    Check if user has a specific permission.

    Algorithm:
    1. Get all groups for user in organisation
    2. Get all permissions for those groups
    3. Check if permission_code is in permissions
    4. Cache result in Redis for 1 hour
    """
    # Try cache first
    cache_key = f"perms:{user_id}:{org_id}"
    cached_perms = redis.get(cache_key)

    if cached_perms:
        return permission_code in json.loads(cached_perms)

    # Query permissions from database
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get all groups for this user in org
        cursor.execute("""
            SELECT DISTINCT gp.permission_code
            FROM group_members gm
            JOIN groups g ON gm.group_id = g.id
            JOIN group_permissions gp ON g.id = gp.group_id
            WHERE gm.user_id = %s AND g.organisation_id = %s
        """, (user_id, org_id))

        permissions = {row[0] for row in cursor.fetchall()}

        # Cache in Redis
        redis.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(list(permissions))
        )

        return permission_code in permissions

# Decorator for Flask endpoints
def require_permission(permission_code: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.current_user.id
            org_id = g.current_user.organisation_id

            if not has_permission(user_id, permission_code, org_id):
                return jsonify({
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': 'Missing required permission',
                        'required': permission_code
                    }
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

### Group Management Endpoints

```http
# 1. List all groups in organization
GET /api/v1/admin-panel/groups
Authorization: Bearer {jwt_token}
X-Organization-ID: {org_id}

Response 200:
{
  "data": [
    {
      "id": "uuid",
      "name": "Admin",
      "description": "Vollständige Systemkontrolle",
      "is_predefined": true,
      "member_count": 5,
      "permission_count": 25,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 8,
  "limit": 20,
  "offset": 0
}
```

```http
# 2. Create new custom group
POST /api/v1/admin-panel/groups
Authorization: Bearer {jwt_token}
Content-Type: application/json
X-Organization-ID: {org_id}

Request:
{
  "name": "Klasse-9A",
  "description": "Schüler der 9. Klasse A"
}

Response 201:
{
  "data": {
    "id": "uuid",
    "name": "Klasse-9A",
    "description": "Schüler der 9. Klasse A",
    "is_predefined": false,
    "created_at": "2024-11-14T10:30:00Z"
  }
}
```

```http
# 3. Get group details with members
GET /api/v1/admin-panel/groups/{group_id}
Authorization: Bearer {jwt_token}
X-Organization-ID: {org_id}

Response 200:
{
  "data": {
    "id": "uuid",
    "name": "Admin",
    "description": "Vollständige Systemkontrolle",
    "is_predefined": true,
    "members": [
      {
        "user_id": "uuid",
        "username": "anna_schmidt",
        "email": "anna@school.de",
        "assigned_at": "2024-01-01T00:00:00Z"
      }
    ],
    "permissions": [
      "admin:system",
      "users:manage:all",
      "groups:manage:all"
    ]
  }
}
```

```http
# 4. Add user to group
POST /api/v1/admin-panel/groups/{group_id}/members
Authorization: Bearer {jwt_token}
Content-Type: application/json
X-Organization-ID: {org_id}

Request:
{
  "user_id": "uuid"
}

Response 201:
{
  "status": "success",
  "message": "User added to group"
}
```

```http
# 5. Remove user from group
DELETE /api/v1/admin-panel/groups/{group_id}/members/{user_id}
Authorization: Bearer {jwt_token}
X-Organization-ID: {org_id}

Response 204:
(No content)
```

```http
# 6. Grant permission to group
POST /api/v1/admin-panel/groups/{group_id}/permissions
Authorization: Bearer {jwt_token}
Content-Type: application/json
X-Organization-ID: {org_id}

Request:
{
  "permission_code": "courses:create"
}

Response 201:
{
  "status": "success",
  "message": "Permission granted to group"
}
```

```http
# 7. Revoke permission from group
DELETE /api/v1/admin-panel/groups/{group_id}/permissions/{permission_code}
Authorization: Bearer {jwt_token}
X-Organization-ID: {org_id}

Response 204:
(No content)
```

---

## 📊 Permission Codes (HARDCODED - System-Level)

⚠️ **WICHTIG:** Dies sind die **einzigen hardcodierten Elemente** des Systems!
- Diese Permission-Codes sind im Backend definiert
- Sie werden NICHT in der Datenbank geändert
- Jede neue Permission MUSS im Backend-Code hinzugefügt werden
- Die Group-Namen (Teacher, Student, etc.) sind NICHT hardcoded (kommen aus template_groups Tabelle)

**Hierarchie:**
1. **site_admin.\*** - Platform-Level (nur Site-Owner)
2. **owner_admin.\*** - Org-Level (Org-Gründer)
3. **admin.\*** - Org-Manager (ernennt vom Owner-Admin)
4. **owner:\*** - Ressourcen-Level (Ersteller von Ressourcen)
5. **courses:\***, **users:\***, **groups:\*** - Feature-Level
6. **abo:\*** - Subscription-Level (für abo:premium, abo:starter, etc.)

---

### Kategorie: Site-Admin (`site_admin.*`) ⭐ GLOBAL

Die **Site-Admin** Rolle ist die höchste Autorität **über alle Organisationen**. Nur der Platform Founder hat diese Rolle. Hat Zugriff auf Platform-Settings und kann alle Organisationen verwalten.

```
site_admin:all                     # Alles auf Platform-Level
site_admin:organisations:manage    # Alle Organisationen verwalten
site_admin:organisations:create    # Neue Organisationen erstellen
site_admin:organisations:delete    # Organisationen löschen
site_admin:users:manage            # Alle Users auf Platform-Level
site_admin:feature-flags           # Platform Feature-Flags
site_admin:system:config           # Platform-Konfiguration
site_admin:billing:global          # Globale Billing-Settings
site_admin:audit                   # Audit-Logs über alle Orgs
site_admin:compliance              # GDPR, DSA, NetzDG global
```

**Spezifikationen:**
- Nur EIN User auf Platform-Ebene
- Hat implizit ALLE anderen Permissions (site_admin:all)
- Kann nicht gelöscht werden (außer durch Datenbank-Zugriff)
- Kann Ownership auf andere User transferieren

---

### Kategorie: Owner-Admin (`owner_admin.*`) ⭐ ORG-LEVEL

Die **Owner-Admin Rolle** ist die höchste Autorität **in einer Organisation**. Nur der Gründer einer Organisation gehört dieser Gruppe an. Hat Zugriff auf ALLE Systemfunktionen in seiner Organisation und kann die Organisation verwalten.

```
owner_admin:organisation:manage    # Organisation konfigurieren
owner_admin:organisation:billing   # Billing & Subscriptions
owner_admin:organisation:branding  # Branding & Design
owner_admin:organisation:delete    # Organisation löschen/schließen
owner_admin:organisation:transfer  # Ownership auf andere User transferieren

owner_admin:all                    # Alles (Super-Admin über Admins)
owner_admin:audit                  # Audit-Logs ansehen
owner_admin:security               # Security Settings (2FA, IP-Whitelist)
owner_admin:integrations           # Externe Integrationen verwalten
owner_admin:api                    # API-Keys & Developer Settings
owner_admin:backups                # Backups verwalten
owner_admin:support:escalate       # Support-Tickets eskalieren
```

**Spezifikationen:**
- Nur EIN User pro Organisation (oder mehrere mit owner_admin:organisation:transfer)
- Hat implizit ALLE anderen Permissions
- Kann andere User zu Admin machen
- Kann Admins demotivieren
- Hat Zugriff auf Billing & Zahlungen
- Kann Organisation übertragen/löschen
- Kann nicht entfernt werden (es sei denn Ownership wird transferiert)

---

### Kategorie: Admin (`admin.*`)

Die **Admin** Gruppe wird vom Owner-Admin ernannt und verwaltet die täglichen Operationen einer Organisation (Users, Gruppen, System-Settings), aber nicht Billing oder Ownership.

```
admin:system              # Alle Systemkonfigurationen
admin:feature-flags       # Feature-Flag Management
admin:logs                # System-Logs einsehen
admin:backups             # Backup-Verwaltung
admin:api-keys            # API-Keys rotieren
admin:users:invite        # User einladen
admin:groups:manage       # Gruppen verwalten
admin:templates:manage    # Group Templates verwalten (anpassen, aber nicht löschen)
```

**Spezifikationen:**
- Ernennt vom Owner-Admin
- Hat NICHT: Billing-Zugriff, Org-Transfer, Org-Löschung
- Hat: Users, Groups, Settings Verwaltung

### Kategorie: Users (`users.*`)

```
users:manage:all          # Alle User-Operationen
users:manage:org          # User in der Organisation
users:view:profile        # User-Profil anschauen
users:edit:profile        # User-Profil bearbeiten
users:suspend:temp        # Temporär sperren
users:suspend:perm        # Dauerhaft sperren
users:tokens:add          # Tokens hinzufügen
```

### Kategorie: Courses (`courses.*`)

```
courses:create            # Neue Kurse erstellen
courses:edit:own          # Eigene Kurse bearbeiten
courses:edit:all          # Alle Kurse bearbeiten
courses:publish           # Kurse veröffentlichen
courses:delete:own        # Eigene Kurse löschen
courses:delete:all        # Alle Kurse löschen
courses:view:analytics    # Kurs-Analytics einsehen
```

### Kategorie: Groups (`groups.*`)

```
groups:manage:all         # Alle Gruppen verwalten
groups:create             # Gruppen erstellen
groups:edit               # Gruppen bearbeiten
groups:delete             # Gruppen löschen
groups:assign             # User zu Gruppen zuweisen
permissions:assign:all    # Beliebige Permissions gewähren
```

### Kategorie: Owner (`owner.*`) ⭐ NEW

Die **Owner-Gruppe** ist ein ressourcen-spezifisches Konzept. Wenn ein User eine Ressource erstellt (Kurs, Inhalt, Gruppe), wird er automatisch zur "Owner"-Gruppe für diese Ressource hinzugefügt.

```
owner:course:manage       # Eigene Kurse verwalten
owner:course:edit         # Eigene Kurse bearbeiten
owner:course:delete       # Eigene Kurse löschen
owner:course:publish      # Eigene Kurse veröffentlichen
owner:course:analytics    # Analytics für eigene Kurse einsehen
owner:course:invite       # User zu eigenen Kursen einladen

owner:content:manage      # Eigenen Content verwalten
owner:content:edit        # Eigenen Content bearbeiten
owner:content:delete      # Eigenen Content löschen
owner:content:review      # Eigenen Content zur Review freigeben

owner:group:manage        # Eigene Gruppen verwalten
owner:group:edit          # Eigene Gruppen bearbeiten
owner:group:delete        # Eigene Gruppen löschen
owner:group:members       # Members in eigenen Gruppen verwalten

owner:analytics           # Analytics für alle eigenen Ressourcen
owner:share:invite        # Alle eigenen Ressourcen einladen
```

**How it works:**
- **Automatic Assignment**: Wenn User X einen Kurs erstellt, wird automatically eine Group `owner:course:{course_id}` erstellt
- **User wird hinzugefügt**: User X wird automatisch zur `owner:course:{course_id}` Gruppe hinzugefügt
- **Permissions erben**: User X erbt alle Permissions dieser Owner-Gruppe für DIESEN Kurs
- **Delegation möglich**: Owner kann andere User zur Owner-Gruppe hinzufügen (z.B. Co-Kurseiter)

---

### Kategorie: Subscriptions/Abo (`abo.*`) ⭐ NEW

Die **Subscription Gruppen** sind automatisch generierte Gruppen basierend auf den Abo-Plänen. User werden automatisch hinzugefügt/entfernt je nach aktiver Subscription.

```
abo:premium               # Premium Subscription aktiv
abo:starter               # Starter Subscription aktiv
abo:pro                   # Pro Subscription aktiv
abo:enterprise            # Enterprise Subscription aktiv

# Feature-spezifische Permissions (konfigurierbar per Plan)
ai:tokens:unlimited       # Unbegrenzte AI-Tokens (Premium+)
ai:advanced:features      # Erweiterte KI-Features (Pro+)
content:publish:unlimited # Unbegrenzte Content-Publishing (Premium+)
analytics:advanced        # Erweiterte Analytics (Pro+)
api:access                # API Access (Pro+)
integrations:custom       # Benutzerdefinierte Integrationen (Enterprise)
```

**How it works:**
1. **Abo-Plan erstellt**: Admin erstellt Abo-Plan "Premium" mit `abo:premium` Group und zugehörigen Permissions
2. **User kauft Abo**: User wird zur `abo:premium` Group hinzugefügt
3. **Permissions erben**: User erbt alle Permissions aus `abo:premium` Group
4. **Abo erneuert/nicht erneuert**: Automatischer Job (Celery/Cron) entfernt User aus Gruppe wenn Abo endet
5. **Permissions gehen verloren**: User verliert sofort alle `abo:premium` Permissions

---

### Kategorie: Content Access (`content.*`)

```
content:create            # Content erstellen
content:edit:own          # Eigene Content bearbeiten
content:edit:all          # Alle Content bearbeiten
content:publish           # Content veröffentlichen
content:delete:own        # Eigene Content löschen
content:delete:all        # Alle Content löschen
content:view:draft        # Draft-Content anschauen
content:view:published    # Veröffentlichter Content
```

---

### Kategorie: Learning Methods (`learning.*`)

```
learning:methods:create   # Neue Lernmethoden erstellen
learning:methods:edit     # Lernmethoden bearbeiten
learning:methods:execute  # Lernmethoden ausführen/spielen
learning:methods:delete   # Lernmethoden löschen
learning:results:view     # Lerner-Ergebnisse anschauen
```

---

### Kategorie: Analytics & Reporting (`analytics.*`)

```
analytics:view:own        # Eigene Analytics anschauen
analytics:view:org        # Organisation-Analytics
analytics:export:data     # Daten exportieren
analytics:advanced        # Erweiterte Analytics (Premium)
```

---

### Permission Hierarchie (Vererbung)

```
Wenn ein User in MEHREREN Gruppen ist, erbt er die UNION aller Permissions:

USER in Admin + Premium-Subscription:
├── admin:system           (von Admin Gruppe)
├── admin:users:invite     (von Admin Gruppe)
├── abo:premium            (von Subscription Gruppe)
├── ai:tokens:unlimited    (von Subscription Gruppe)
└── content:publish:unlimited (von Subscription Gruppe)
    = UNION aller Permissions
```
- **Skaliert**: Jede Ressource hat ihre eigene Owner-Gruppe mit Permissions

**Beispiel-Szenario:**
```
Teacher Alice erstellt Kurs "Mathematik 101"
↓
Automatisch erstellt:
  - Group: "owner:course:math-101"
  - Owner-Permissions: course:edit, course:delete, course:analytics
  - Alice → wird hinzugefügt zu "owner:course:math-101"
↓
Alice kann jetzt:
  - Diesen Kurs bearbeiten
  - Diesen Kurs löschen
  - Analytics für diesen Kurs sehen
  - Andere User als Co-Owner hinzufügen
↓
Alice kann NICHT:
  - Den Kurs eines anderen Teachers löschen
  - Den Kurs eines anderen Teachers bearbeiten
  - (Wenn sie keine "courses:edit:all" global hat)
```

### Kategorie: Content (`content.*`)

```
content:create            # Content erstellen
content:edit:own          # Eigenes Content bearbeiten
content:edit:all          # Alle Content bearbeiten
content:review            # Content reviewen
content:moderate          # Content moderieren
content:publish           # Content veröffentlichen
```

### Kategorie: AI (`ai.*`)

```
ai:content-generation     # KI-Content Generator nutzen
ai:auto-correction        # KI-Auto-Correction
ai:image-generation       # KI-Bilder generieren
ai:translate              # KI-Übersetzungen
ai:high-priority          # Priorität in KI-Queue
```

---

## 🔧 Implementation Examples

### Backend: Kurs erstellen mit Owner Group

**Szenario:** Teacher Alice erstellt einen neuen Kurs "Mathematik 101"

```python
# backend/app/blueprints/courses/routes.py

from app.database import get_db_connection
from app.repositories.course import CourseRepository
from app.repositories.owner_group import OwnerGroupRepository
from app.repositories.group import GroupRepository
from app.repositories.group_permission import GroupPermissionRepository

@bp.route('', methods=['POST'])
@require_auth
def create_course():
    """Kurs erstellen mit automatischer Owner Group"""

    data = request.get_json()

    with get_db_connection() as conn:
        # 1. Kurs erstellen
        course_repo = CourseRepository(conn)
        course = course_repo.create({
            'name': data['name'],
            'creator_id': g.current_user.id,
            'organisation_id': g.current_user.organisation_id
        })

        # 2. Owner Group automatisch erstellen
        owner_group_repo = OwnerGroupRepository(conn)
        owner_group = owner_group_repo.create({
            'resource_type': 'course',
            'resource_id': course.id,
            'organisation_id': g.current_user.organisation_id,
            'creator_user_id': g.current_user.id
        })
        # Trigger erstellt automatisch: groups.name = "owner:course:{course_id}"

        # 3. Owner-Permissions zur Owner Group hinzufügen
        group_repo = GroupRepository(conn)
        owner_group_db = group_repo.find_by_name(
            f"owner:course:{course.id}",
            g.current_user.organisation_id
        )

        group_perm_repo = GroupPermissionRepository(conn)
        owner_permissions = [
            'owner:course:manage',
            'owner:course:edit',
            'owner:course:delete',
            'owner:course:publish',
            'owner:course:analytics',
            'owner:course:invite'
        ]

        for perm in owner_permissions:
            group_perm_repo.create({
                'group_id': owner_group_db.id,
                'permission_code': perm
            })

        # Trigger fügt Alice automatisch zur Owner Group hinzu
        # (g.current_user wird automatisch zu group_members hinzugefügt)

    return jsonify({
        'status': 'success',
        'course': course.to_dict(),
        'owner_group': f"owner:course:{course.id}"
    }), 201
```

**Was passiert automatisch:**
```
1. Teacher Alice POSTs /api/courses {name: "Mathematik 101"}
2. Backend erstellt Kurs mit Alice als creator_id
3. Trigger: owner_groups INSERT → groups INSERT
   - Neue Group: "owner:course:ABC123"
4. Trigger: owner_groups INSERT → group_members INSERT
   - Alice wird zu group_members hinzugefügt
5. Backend fügt owner:course:* Permissions hinzu
6. Alice hat jetzt volle Kontrolle über diesen Kurs!
```

### Permission Check: Kann Alice diesen Kurs bearbeiten?

```python
# app/utils/permissions.py

def has_permission(user_id: str, permission_code: str, resource_id: str = None) -> bool:
    """
    Check if user has permission.

    Prüft:
    1. Vordefinierte Rollen-Permissions
    2. Owner Group Permissions (falls resource_id angegeben)
    3. Custom Group Permissions
    """

    with get_db_connection() as conn:
        # Alle Gruppen des Users finden
        group_repo = GroupRepository(conn)
        user_groups = group_repo.find_user_groups(user_id)

        # Alle Permissions dieser Gruppen sammeln
        all_permissions = set()
        for group in user_groups:
            group_perms = group_repo.get_group_permissions(group.id)
            all_permissions.update(group_perms)

        return permission_code in all_permissions

# Beispiel-Verwendung:
if has_permission(alice.id, 'courses:edit:own'):
    # ✅ Alice darf Kurse bearbeiten
    return True

if has_permission(alice.id, 'owner:course:edit', course_id='math-101'):
    # ✅ Alice ist Owner von diesem Kurs
    return True

if has_permission(alice.id, 'courses:edit:all'):
    # ✅ Alice darf ALLE Kurse bearbeiten (Admin/Moderator)
    return True
```

### Founder bekommt Owner-Admin Rolle (beim Sign-Up)

**Szenario:** Maria gründet eine neue Organisation "MathAcademy" und wählt das "School" Template

```python
# backend/app/blueprints/organisations/routes.py

from app.repositories.organisation import OrganisationRepository
from app.repositories.group import GroupRepository
from app.repositories.group_template import GroupTemplateRepository
from app.repositories.group_permission import GroupPermissionRepository

@bp.route('', methods=['POST'])
def create_organisation():
    """
    Organisation erstellen mit Template-basierter Gruppenerstellung

    Request Body:
        - name: Organisation Name
        - template_code: Gewähltes Template ('school', 'corporate', 'online', 'education-provider')
    """
    data = request.get_json()

    # ⚠️ WICHTIG: template_code muss vom Frontend übergeben werden (User wählt Template)
    if not data.get('template_code'):
        return jsonify({'error': 'template_code erforderlich'}), 400

    with get_db_connection() as conn:
        org_repo = OrganisationRepository(conn)
        group_repo = GroupRepository(conn)
        template_repo = GroupTemplateRepository(conn)
        group_perm_repo = GroupPermissionRepository(conn)

        # 1. Organisation erstellen
        org = org_repo.create({
            'name': data['name'],
            'founder_id': g.current_user.id,
            'template_code': data['template_code']  # Speichern welches Template verwendet wurde
        })

        # 2. Template aus Datenbank laden (NICHT HARDCODED!)
        # Das ist der Schlüsselunterschied zur alten Implementierung
        template = template_repo.find_by_code(data['template_code'])
        if not template:
            return jsonify({'error': f"Template '{data['template_code']}' nicht gefunden"}), 400

        # 3. Gruppen aus Template erstellen
        # Alle Group-Namen, Beschreibungen etc. kommen aus der Datenbank!
        org_groups = {}
        for template_group in template.template_groups:  # SELECT * FROM template_groups WHERE template_id = X

            # Gruppe erstellen mit Namen aus template_groups Tabelle
            group = group_repo.create({
                'organisation_id': org.id,
                'name': template_group.group_name,      # ← AUS DATABASE (nicht hardcoded!)
                'description': template_group.description,
                'is_predefined': True,
                'template_group_id': template_group.id   # Link zu Template für Auditing
            })
            org_groups[template_group.id] = group.id

            # 4. Permissions aus Template laden und hinzufügen
            # SELECT * FROM template_group_permissions WHERE template_group_id = X
            for perm in template_group.permissions:
                group_perm_repo.create({
                    'group_id': group.id,
                    'permission_code': perm.permission_code
                })

        # 5. Founder automatisch zu owner-admin Gruppe hinzufügen
        owner_admin_group = group_repo.find_by_name('owner-admin', org.id)
        if not owner_admin_group:
            # Fallback: Finde erste Gruppe mit admin-ähnlichen Permissions
            owner_admin_group = group_repo.find_by(
                {'organisation_id': org.id, 'is_predefined': True},
                order_by='created_at ASC'
            )[0]

        group_repo.add_member(owner_admin_group.id, g.current_user.id)

        return jsonify({
            'status': 'success',
            'organisation': org.to_dict(),
            'template_used': template.template_code,
            'groups_created': len(org_groups),
            'message': f'Maria ist jetzt Owner-Admin von {org.name} (Template: {template.template_name})'
        }), 201
```

**Was passiert (mit Template-basierter Architektur):**
```
1. Maria klickt "Organisation erstellen" und wählt Template: "School"
   └── Frontend sendet: {'name': 'MathAcademy', 'template_code': 'school'}

2. Backend lädt Template aus Datenbank:
   └── SELECT * FROM group_templates WHERE template_code = 'school'
   └── Ergebnis: Template mit Namen "School Template"

3. Backend lädt alle Template-Gruppen:
   └── SELECT * FROM template_groups WHERE template_id = X
   └── Ergebnis: [teacher, student, creator, moderator, support]

4. Für jede Template-Gruppe laden die Permissions:
   └── SELECT * FROM template_group_permissions WHERE template_group_id = X

5. Backend erstellt Organisationen-Gruppen mit EXAKTEN Daten aus Database:
   ├── Gruppe "teacher" mit allen teacher-Permissions (aus Template)
   ├── Gruppe "student" mit allen student-Permissions (aus Template)
   ├── Gruppe "creator" mit allen creator-Permissions (aus Template)
   ├── Gruppe "moderator" mit allen moderator-Permissions (aus Template)
   └── Gruppe "support" mit allen support-Permissions (aus Template)

6. Maria wird automatisch zu "owner-admin" Gruppe hinzugefügt

7. Maria hat jetzt volle Kontrolle über die Organisation!
   ✅ Kann Admins ernennen
   ✅ Kann Billing verwalten
   ✅ Kann Organisation konfigurieren
   ✅ Kann Ownership transferieren
   ⚠️ Template-Gruppen können nicht gelöscht werden (is_predefined = TRUE)
   ✅ Aber: Neue Custom Groups können jederzeit hinzugefügt werden
```

**Warum ist das besser als Hardcoding?**

| Aspekt | Alte Methode (Hardcoded) | Neue Methode (Template-basiert) |
|--------|--------------------------|--------------------------------|
| **Flexibilität** | ❌ Neue Template? Code-Change + Deploy erforderlich | ✅ Neue Template? Nur DB-Update (Zero Downtime) |
| **Konfigurierbarkeit** | ❌ Namen/Permissions im Code fixiert | ✅ Admin kann Names/Permissions ändern |
| **Multi-Tenancy** | ❌ Alle Orgs nutzen GLEICHE Gruppen | ✅ Jedes Template kann unterschiedliche Gruppen/Permissions haben |
| **Wartbarkeit** | ❌ Schwer zu ändern ohne Code-Review | ✅ Einfach zu ändern via Admin-UI |
| **Skalierbarkeit** | ❌ Jede neue Org-Type benötigt neuen Code | ✅ Einfach neue Template erstellen und deployen |
| **Automatisierung** | ❌ Migration bei neuer Org-Type schwer | ✅ Neue Templates können per API erstellt werden |

### Owner-Admin vs Admin vs Teacher (Vergleich)

| Permission | Owner-Admin | Admin | Teacher |
|-----------|-----------|-------|---------|
| `owner_admin:organisation:manage` | ✅ | ❌ | ❌ |
| `owner_admin:organisation:billing` | ✅ | ❌ | ❌ |
| `admin:system` | ✅ (implizit) | ✅ | ❌ |
| `admin:users:manage:all` | ✅ (implizit) | ✅ | ❌ |
| `courses:create` | ✅ (implizit) | ✅ | ✅ |
| `courses:publish` | ✅ (implizit) | ✅ | ❌ |

---

### Custom Subscription Group erstellen (Abo-Modelle)

**Szenario:** Owner-Admin "Ravi" erstellt einen neuen Subscription-Plan "Premium" und will dass Nutzer mit "Premium" Auto-Permissions bekommen

```python
# backend/app/blueprints/subscriptions/routes.py

from app.repositories.subscription import SubscriptionRepository
from app.repositories.group import GroupRepository
from app.repositories.group_permission import GroupPermissionRepository

@bp.route('/subscription-plans', methods=['POST'])
@require_auth
@require_permission('owner_admin:organisation:billing')
def create_subscription_plan():
    """
    Neuen Subscription-Plan erstellen mit automatischer Group-Erstellung

    Request Body:
        - name: Plan Name ("Premium", "Starter", etc.)
        - code: Plan Code ("premium", "starter") - muss eindeutig sein
        - permissions: Liste von Permissions die dieser Plan gewährt
            Beispiel: ["ai:tokens:unlimited", "content:publish:unlimited", "analytics:advanced"]
    """
    data = request.get_json()

    with get_db_connection() as conn:
        subscription_repo = SubscriptionRepository(conn)
        group_repo = GroupRepository(conn)
        group_perm_repo = GroupPermissionRepository(conn)

        # 1. Subscription-Plan erstellen
        subscription_plan = subscription_repo.create({
            'organisation_id': g.current_org.id,
            'name': data['name'],
            'code': data['code'],
            'price': data.get('price', 0),
            'billing_cycle': data.get('billing_cycle', 'monthly')
        })

        # 2. Automatisch eine Group für diesen Plan erstellen
        # Format: abo:<plan_code>
        group = group_repo.create({
            'organisation_id': g.current_org.id,
            'name': f'abo:{data["code"]}',
            'description': f'Automatische Gruppe für {data["name"]} Subscriber',
            'is_predefined': False,  # Custom Group, kann gelöscht werden wenn Plan gelöscht wird
            'subscription_plan_id': subscription_plan.id  # Link zu Subscription Plan
        })

        # 3. Permissions für diese Subscription-Group hinzufügen
        for permission_code in data.get('permissions', []):
            group_perm_repo.create({
                'group_id': group.id,
                'permission_code': permission_code
            })

        return jsonify({
            'status': 'success',
            'subscription_plan': subscription_plan.to_dict(),
            'group': group.to_dict(),
            'message': f'Subscription Plan "{data["name"]}" erstellt. Group "{group.name}" automatisch erstellt.'
        }), 201


# Celery Task: User zu Subscription-Group hinzufügen (beim Kauf)
@app.task(bind=True)
def add_user_to_subscription_group(self, user_id: str, subscription_plan_id: str):
    """
    Automatischer Task: Wenn User Subscription kauft, zur entsprechenden Group hinzufügen

    Aufgerufen von: /api/subscriptions/purchase Endpoint
    """
    with get_db_connection() as conn:
        group_repo = GroupRepository(conn)
        subscription_repo = SubscriptionRepository(conn)

        # 1. Subscription Plan laden
        subscription_plan = subscription_repo.find_by_id(subscription_plan_id)
        if not subscription_plan:
            return {'status': 'error', 'message': 'Plan not found'}

        # 2. Finde die entsprechende Group: abo:<plan_code>
        group = group_repo.find_by_name(f'abo:{subscription_plan.code}', subscription_plan.organisation_id)
        if not group:
            return {'status': 'error', 'message': f'Group abo:{subscription_plan.code} not found'}

        # 3. User zur Group hinzufügen
        group_repo.add_member(group.id, user_id)

        return {
            'status': 'success',
            'message': f'User {user_id} added to group {group.name}',
            'permissions_granted': [p.permission_code for p in group.permissions]
        }


# Celery Task: User aus Subscription-Group entfernen (bei Kündigung/Ablauf)
@app.task(bind=True)
def remove_user_from_subscription_group(self, user_id: str, subscription_plan_id: str):
    """
    Automatischer Task: Wenn User Subscription beendet (Kündigung oder Ablauf), aus Group entfernen

    Aufgerufen von:
    1. /api/subscriptions/{id}/cancel Endpoint (User kündigt manuell)
    2. Celery Beat Task: check_expired_subscriptions (jeden Tag laufen)
    """
    with get_db_connection() as conn:
        group_repo = GroupRepository(conn)
        subscription_repo = SubscriptionRepository(conn)

        # 1. Subscription Plan laden
        subscription_plan = subscription_repo.find_by_id(subscription_plan_id)
        if not subscription_plan:
            return {'status': 'error', 'message': 'Plan not found'}

        # 2. Finde die entsprechende Group: abo:<plan_code>
        group = group_repo.find_by_name(f'abo:{subscription_plan.code}', subscription_plan.organisation_id)
        if not group:
            return {'status': 'success', 'message': f'Group abo:{subscription_plan.code} already deleted'}

        # 3. User aus der Group entfernen
        group_repo.remove_member(group.id, user_id)

        return {
            'status': 'success',
            'message': f'User {user_id} removed from group {group.name}',
            'permissions_revoked': [p.permission_code for p in group.permissions]
        }


# Celery Beat Task: Regelmäßig abgelaufene Subscriptions verarbeiten
from celery.schedules import crontab

@app.task
def check_expired_subscriptions():
    """
    Laufe jeden Tag um 00:00 UTC
    - Finde alle Subscriptions die heute ablaufen
    - Entferne User automatisch aus entsprechenden Groups
    - Leere den Token Wallet wenn nötig
    """
    with get_db_connection() as conn:
        subscription_repo = SubscriptionRepository(conn)

        # Finde alle Subscriptions die heute oder gestern ablaufen
        expired_subs = subscription_repo.find_expired()

        results = []
        for sub in expired_subs:
            # Aufgerufen remove_user_from_subscription_group für jeden User
            result = remove_user_from_subscription_group.apply_async(
                args=[sub.user_id, sub.subscription_plan_id],
                countdown=5  # Verzögerung um Datenconsistenz zu gewährleisten
            )
            results.append({
                'subscription_id': sub.id,
                'user_id': sub.user_id,
                'task_id': result.id
            })

        return {'processed': len(results), 'details': results}
```

**Was passiert:**

```
SCHRITT 1: Ravi erstellt Plan "Premium" mit Permissions
├── Admin-Panel → Subscriptions → "Create New Plan"
├── Input: name="Premium", code="premium", permissions=["ai:tokens:unlimited", "analytics:advanced"]
└── Sendet POST /api/subscriptions/subscription-plans

SCHRITT 2: Backend erstellt automatisch:
├── 1. Subscription Plan in subscription_plans Table
├── 2. Group "abo:premium" in groups Table (mit subscription_plan_id Link)
└── 3. Alle Permissions in group_permissions Table

SCHRITT 3: User "Lisa" kauft Premium Subscription
├── Klickt "Buy Premium" → Paypal/Stripe Zahlung
├── Backend erstellt Subscription-Record (subscription_id, user_id, plan_id, expires_at)
└── Celery Task: add_user_to_subscription_group(lisa_id, premium_plan_id)
    └── Lisa wird zu "abo:premium" Group hinzugefügt
    └── Lisa erbt SOFORT alle Permissions: ai:tokens:unlimited, analytics:advanced

SCHRITT 4: Lisa hat jetzt:
✅ ai:tokens:unlimited      (aus abo:premium Group)
✅ analytics:advanced       (aus abo:premium Group)
✅ ai:tokens:daily:50       (von ihrer teacher Group falls sie auch Teacher ist)
   = UNION aller Permissions aus allen ihrer Groups!

SCHRITT 5: Lisas Subscription endet (Kündigung oder Ablauf)
├── Option A: Lisa klickt "Cancel Subscription" → Cancel API aufgerufen
├── Option B: Celery Beat Task: check_expired_subscriptions läuft jeden Tag
│   └── Findet alle abgelaufenen Subscriptions
│   └── Ruft remove_user_from_subscription_group auf
└── Celery Task: remove_user_from_subscription_group(lisa_id, premium_plan_id)
    └── Lisa wird aus "abo:premium" Group entfernt
    └── ai:tokens:unlimited Permission geht SOFORT verloren
    └── analytics:advanced Permission geht SOFORT verloren
    └── Aber: Lisa behält ihre anderen Permissions (z.B. von teacher Group)

SCHRITT 6: Admin kann Plan später aktualisieren/löschen
├── Wenn Plan gelöscht wird:
│   ├── Alle User aus "abo:premium" Group werden entfernt
│   ├── Group "abo:premium" wird gelöscht (ist custom group, nicht predefined)
│   └── Subscription Plan wird gelöscht/archiviert
```

**Automatisierung:**

| Event | Trigger | Aktion |
|-------|---------|--------|
| **User kauft Subscription** | POST /api/subscriptions/purchase | Celery Task: add_user_to_subscription_group |
| **User kündigt manuell** | POST /api/subscriptions/{id}/cancel | Celery Task: remove_user_from_subscription_group |
| **Subscription läuft ab** | Celery Beat: check_expired_subscriptions (täglich) | Celery Task: remove_user_from_subscription_group |
| **Admin ändert Plan Permissions** | PUT /api/subscriptions/subscription-plans/{id} | UPDATE group_permissions WHERE group_id = abo:X |
| **Admin löscht Plan** | DELETE /api/subscriptions/subscription-plans/{id} | DELETE group_members, DELETE group_permissions, DELETE groups |

---

### Frontend: Alice sieht nur ihre eigenen Kurse

```vue
<!-- frontend/src/components/courses/CourseList.vue -->

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useCourseStore } from '@/stores/courses'

const authStore = useAuthStore()
const courseStore = useCourseStore()

const filteredCourses = computed(() => {
  // Nur Kurse filtern die Alice gehören
  return courseStore.courses.filter(course => {
    // Check: Ist Alice owner von diesem Kurs?
    return course.creator_id === authStore.currentUser.id
      // OR: Hat Alice globale courses:edit:all Permission?
      || authStore.currentUser.hasPermission('courses:edit:all')
  })
})

const canEditCourse = (courseId) => {
  return authStore.currentUser.hasPermission('owner:course:edit', {
    resource_id: courseId
  })
}
</script>

<template>
  <div>
    <h2>Meine Kurse</h2>
    <div v-for="course in filteredCourses" :key="course.id" class="course-card">
      <h3>{{ course.name }}</h3>

      <!-- Edit-Button nur wenn Alice owner ist -->
      <button
        v-if="canEditCourse(course.id)"
        @click="editCourse(course.id)"
      >
        Bearbeiten
      </button>

      <!-- Delete-Button nur wenn Alice owner ist -->
      <button
        v-if="authStore.currentUser.hasPermission('owner:course:delete', {
          resource_id: course.id
        })"
        @click="deleteCourse(course.id)"
      >
        Löschen
      </button>
    </div>
  </div>
</template>
```

---

## 🔄 Migration Path (RBAC 2.0 → Group-Based)

### Phase 1: Datenbank-Migration (Template-Based)

⚠️ **WICHTIG:** Die Gruppenerstellung lädt Templates aus der Datenbank, NICHT aus hardcodierten Listen!

```sql
-- Step 1: Create new Group tables (done - see above)

-- Step 2: Create group templates (if not exists from seed)
INSERT INTO group_templates (template_code, template_name, description) VALUES
('school', 'School Template', 'Für Schulen und Bildungseinrichtungen'),
('corporate', 'Corporate Template', 'Für Unternehmensstrukturen'),
('online', 'Online-Course Template', 'Für Online-Kurse und MOOCs'),
('education-provider', 'Education Provider', 'Für Bildungsanbieter')
ON CONFLICT (template_code) DO NOTHING;

-- Step 3: Create template groups (aus template_groups Tabelle laden)
-- Diese Gruppen werden AUS DATABASE geladen, nicht hardcoded!
--
-- Beispiel School Template:
--  SELECT group_name, description FROM template_groups WHERE template_id = school_template.id
--  → 'teacher', 'student', 'creator', 'moderator', 'support' (aus DB)

-- Step 4: Für jede existierende Organisation: Template auswählen & Gruppen erstellen
-- Dieser Prozess:
--   1. Für jede Org ein Template auswählen (z.B. 'school')
--   2. Template-Gruppen aus template_groups laden
--   3. Für jede template-gruppe eine neue Gruppe in der Org erstellen
--
-- Pseudocode (in Python, nicht SQL):
-- for org in organisations:
--     template = templates.find_by_code(org.default_template_code)  # z.B. 'school'
--     for template_group in template.template_groups:  # aus DB laden
--         group = groups.create({
--             organisation_id: org.id,
--             name: template_group.group_name,  # ← AUS DB (nicht hardcoded)
--             description: template_group.description,
--             is_predefined: True,
--             template_group_id: template_group.id
--         })
--         # Permissions aus template_group_permissions laden
--         for perm in template_group.permissions:
--             group_permissions.create({
--                 group_id: group.id,
--                 permission_code: perm.permission_code
--             })

-- Step 5: Migrate users from old role field to new group structure
-- Mapping old roles to template groups based on selected template:
--
-- Schema: old_role → template_group_name (depends on template)
-- - 'admin' → (je nach Template: 'teacher', 'manager', 'instructor', 'admin')
-- - 'teacher' → (je nach Template: 'teacher')
-- - 'student' → (je nach Template: 'student', 'learner', 'employee')
-- etc.

-- Step 6: Keep old role column for rollback (mark as deprecated)
ALTER TABLE users ADD COLUMN IF NOT EXISTS role_deprecated VARCHAR(50);
UPDATE users SET role_deprecated = role WHERE role_deprecated IS NULL;

-- Step 7: Verify migration
SELECT
  COUNT(*) as user_count,
  COUNT(DISTINCT gm.group_id) as group_count,
  COUNT(DISTINCT gp.permission_code) as permission_count,
  COUNT(DISTINCT g.organisation_id) as org_count
FROM users u
LEFT JOIN group_members gm ON u.id = gm.user_id
LEFT JOIN groups g ON gm.group_id = g.id
LEFT JOIN group_permissions gp ON g.id = gp.group_id;
```

### Phase 2: Fallback Strategy

```python
# During transition period, support both old and new system:

def get_user_permissions(user_id: str, org_id: str) -> Set[str]:
    """Get user permissions from new Group-Based system, fallback to old RBAC if needed."""

    # Try new Group-Based system first
    permissions = _get_permissions_from_groups(user_id, org_id)

    if permissions:
        return permissions  # Successfully got permissions from groups

    # Fallback to old RBAC 2.0 system
    logger.warning(f"Fallback to RBAC for user {user_id}")
    return _get_permissions_from_role(user_id, org_id)

def _get_permissions_from_groups(user_id: str, org_id: str) -> Set[str]:
    """Get permissions from Group-Based system."""
    # (implementation as shown above)
    pass

def _get_permissions_from_role(user_id: str, org_id: str) -> Set[str]:
    """Get permissions from old RBAC 2.0 system (deprecated)."""
    # (old implementation)
    pass
```

### Phase 3: Deprecation & Cleanup

```
Timeline:
- Week 1: Notification to admins about Group-Based system launch
- Week 2-4: Support both systems (automatic fallback)
- Week 5-8: Group-Based as primary, old system as fallback
- Week 9-12: Old system removed, Group-Based is the only system
- After: role column can be dropped from users table
```

---

## ✅ Rollback Plan

Falls etwas schiefgeht, können wir schnell zurück zu RBAC 2.0:

```sql
-- Step 1: Restore old role column from backup
ALTER TABLE users DROP COLUMN role;
ALTER TABLE users RENAME COLUMN role_deprecated TO role;

-- Step 2: Deactivate Group-Based system
UPDATE system_config SET enabled = false WHERE system = 'group_based_permissions';

-- Step 3: Restart application to load old auth system
-- (redeploy with rollback flag)

-- Step 4: New Group data can stay as-is (won't be used)
-- After system stabilizes, we can drop groups/group_members/group_permissions tables
```

---

## 📊 Feature-Matrix

### Permission Features

| Feature | Status | Beschreibung |
|---------|--------|-------------|
| **Vordefinierte Gruppen** | ✅ | 6 Standard-Gruppen pro Org |
| **Custom Gruppen** | ✅ | Orgs können beliebige Gruppen erstellen |
| **Many-to-Many Membership** | ✅ | 1 User → N Groups |
| **Permission Aggregation** | ✅ | User-Perms = Union aller Group-Perms |
| **Audit Trail** | ✅ | Wer hat was wann geändert |
| **Permission Caching** | ✅ | Redis Cache für Performance |
| **Fallback System** | ✅ | Automatic fallback zu RBAC |
| **Admin UI** | ⏳ | Group Management Panel (Phase 4) |
| **API Endpoints** | ⏳ | Full CRUD endpoints (Phase 3) |
| **Migrations** | ⏳ | Data migration scripts (Phase 5) |

---

## 🚀 Implementierungs-Roadmap

### Phase 1: Dokumentation & Planning (DONE)
- ✅ Dokumentation aufräumen & erneuern
- ✅ Datenmodell definieren
- ✅ API Spezifikation schreiben
- ✅ Migration Path planen

### Phase 2: Backend-Datenbank (TODO)
- ⏳ Group-Tables erstellen (migrations)
- ⏳ Predefined groups seeden
- ⏳ Permission codes definieren

### Phase 3: Backend-API & Services (TODO)
- ⏳ GroupRepository implementieren
- ⏳ GroupMemberRepository implementieren
- ⏳ GroupPermissionRepository implementieren
- ⏳ Permission-Check Service
- ⏳ API endpoints

### Phase 4: Frontend-UI (TODO)
- ⏳ Group Management Panel
- ⏳ User Group Assignment
- ⏳ Permission Assignment UI

### Phase 5: Migration & Rollout (TODO)
- ⏳ Migration-Script testen
- ⏳ Rollback-Plan testen
- ⏳ Data migration durchführen
- ⏳ Old system deaktivieren

---

## 💡 Best Practices

### 1. Permission Naming Convention

```
{resource}.{action}.{scope}

Beispiele:
- courses.create            (resource.action)
- courses.edit.own          (resource.action.scope)
- users.manage.all          (resource.action.scope)
- admin:system              (special: admin permissions)
```

### 2. Group Naming Convention

```
Vordefinierte Gruppen: lowercase (admin, teacher, student)
Custom Gruppen: PascalCase oder descriptive (Klasse-9A, Team-Finance)
```

### 3. Caching Strategy

```python
# Cache invalidation triggers:
- User added to group → invalidate user's cache
- User removed from group → invalidate user's cache
- Permission granted to group → invalidate all group members' cache
- Permission revoked from group → invalidate all group members' cache

# Cache TTL: 1 hour (3600 seconds)
# Fallback: Always check DB if cache miss
```

### 4. Security Considerations

```
- Keine Secrets in Permission Codes speichern
- Permissions sind case-sensitive (use lowercase)
- Always validate permission codes on backend
- Log all permission changes (audit trail)
- Rate-limit permission assignment endpoints
```

---

## 📚 Referenzen

**Related Documents:**
- `01_Gruppenmodell.md` - User-facing Group Model
- `05_Backend-Struktur.md` - Backend Architecture & Services
- `04_Frontend-Struktur.md` - Frontend Components & UI
- `01_Security-Architecture.md` - Authorization Implementation

**External References:**
- [OWASP Authorization](https://owasp.org/www-community/Authorization)
- [RBAC vs ABAC](https://en.wikipedia.org/wiki/Access_control#Role-based_access_control)
- [PostgreSQL Row-Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

---

**Version:** 2.0
**Status:** ACTIVE (Phase 1 Complete - Ready for Backend Implementation)
**Last Updated:** 2026-01-22
**Maintainer:** Development Team

> 💡 **Hinweis:** Dieses Dokument ist die technische Spezifikation des Group-Based Permission Systems.
>
> **Phase 1 (Dokumentation & Planung):** ✅ ABGESCHLOSSEN
> - Template-basierte Gruppenerstellung dokumentiert (NICHT hardcoded)
> - 4-Ebenen Organisationshierarchie definiert
> - Permission Codes Hierarchie (6-Level) spezifiziert
> - Custom Subscription Groups (Abo-Modelle) mit Celery-Automation dokumentiert
> - Migration Path von RBAC 2.0 aktualisiert
>
> **Phase 2 (Backend-Implementierung):** TODO - Ready to start
> **Phase 3 (Dokumentation 05_Multi-Tenancy-Architecture.md):** TODO - Scheduled next
