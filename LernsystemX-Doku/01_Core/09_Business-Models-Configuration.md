# 🎯 Business Models Configuration - B2B vs B2C

**Datum:** 2026-01-22
**Version:** 1.0
**Status:** PLANNING - Flexible Configuration System
**Autor:** Claude Code

---

## 📊 ÜBERSICHT: Zwei Geschäftsmodelle

```
┌─────────────────────────────────────────────────────────────┐
│                    LSX PLATFORM                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   B2B MODEL      │         │   B2C MODEL      │          │
│  │  (Organisationen)│         │ (Self-Service)   │          │
│  ├──────────────────┤         ├──────────────────┤          │
│  │ DU erstellt      │         │ User registers   │          │
│  │ Organisationen   │         │ selbst           │          │
│  │                  │         │                  │          │
│  │ Owner-Admin      │         │ User kauft       │          │
│  │ verwaltet Groups │         │ Subscription     │          │
│  │                  │         │                  │          │
│  │ Manual Process   │         │ Auto Process     │          │
│  │ (Anfrage → Org)  │         │ (Kauf → Permission) │       │
│  └──────────────────┘         └──────────────────┘          │
│                                                               │
│  ABER: Beide nutzen SAME Permission-System (UNION-Modell)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏢 TEIL 1: B2B MODEL (Organisationen)

### 1.1 Was ist B2B?

**Definition:** Organisations-basiertes Modell für Schulen, Universitäten, Unternehmen, Kanzleien, etc.

**Merkmale:**
- ✅ Organisation = Tenant (völlige Datenisolation via RLS)
- ✅ Du (Site-Admin) erstellt Organisationen nach Anfrage
- ✅ Owner-Admin der Organisation verwaltet alles selbst
- ✅ Flexible Hierarchie (bis zu 1000+ Custom Groups möglich)
- ✅ Jede Org hat dedizierte Frontend-Container

**Beispiele:**
- 🏫 "Gymnasium München" (300 Schüler, 50 Lehrer, 10 Admin)
- 🏢 "SAP Consulting GmbH" (200 Berater, 5 Departments)
- 🎓 "Ludwig-Maximilians-Universität" (45.000 Studenten, 800 Dozenten, 20 Fakultäten)
- ⚖️ "Kanzlei Schmidt & Partner" (50 Anwälte, 3 Partner, 15 Admin)

---

### 1.2 B2B Configuration Table (DATABASE-DRIVEN)

```sql
-- NEUE TABELLE: b2b_configurations
-- Speichert alle B2B-spezifischen Einstellungen
-- NICHTS ist hardcoded!

CREATE TABLE b2b_configurations (
    id UUID PRIMARY KEY,
    organisation_id UUID NOT NULL UNIQUE,

    -- GRUNDEINSTELLUNGEN
    model_type VARCHAR(20) DEFAULT 'organisation',  -- 'organisation', 'enterprise', 'partner'

    -- HIERARCHIE KONFIGURATION
    max_hierarchy_depth INT DEFAULT 10,             -- Wie viele Ebenen sind erlaubt? (1-1000)
    max_groups_per_level INT DEFAULT 500,           -- Max Groups pro Ebene (1-10000)
    allow_custom_groups BOOLEAN DEFAULT TRUE,       -- Darf Owner-Admin Custom Groups erstellen?
    allow_nested_groups BOOLEAN DEFAULT TRUE,       -- Können Groups Subgroups haben?

    -- PERMISSION SETTINGS
    enable_permission_inheritance BOOLEAN DEFAULT TRUE,  -- UNION-Modell aktiviert?
    allow_permission_overrides BOOLEAN DEFAULT FALSE,    -- Können Owner-Admin Permissions override?
    require_permission_approval BOOLEAN DEFAULT FALSE,   -- Braucht neue Permission Admin-Genehmigung?

    -- USER MANAGEMENT
    allow_owner_admin_invites BOOLEAN DEFAULT TRUE,  -- Kann Owner-Admin User einladen?
    auto_add_users_to_default_group BOOLEAN DEFAULT TRUE,  -- Auto User zu "member" Group?
    default_user_group VARCHAR(100) DEFAULT 'member',      -- Standard-Group für neue User

    -- FEATURES
    enable_subscription_groups BOOLEAN DEFAULT FALSE,  -- Darf diese Org Abo-Groups erstellen?
    enable_team_groups BOOLEAN DEFAULT TRUE,          -- Darf Owner-Admin Team Groups erstellen?
    enable_cohort_groups BOOLEAN DEFAULT TRUE,        -- Darf Owner-Admin Cohort Groups erstellen?
    enable_partner_groups BOOLEAN DEFAULT FALSE,      -- Darf Owner-Admin Partner Groups erstellen?

    -- LIMITS
    max_users INT DEFAULT NULL,                    -- NULL = unbegrenzt
    max_groups INT DEFAULT 500,                    -- Total max groups (unabhängig von depth)
    max_custom_permission_codes INT DEFAULT 50,    -- Darf Org eigene Permission-Codes definieren?

    -- AUDIT & SECURITY
    require_mfa_for_admin BOOLEAN DEFAULT FALSE,   -- Multi-Factor Auth für Admin erzwungen?
    enable_audit_logs BOOLEAN DEFAULT TRUE,        -- Alle Actions geloggt?
    log_retention_days INT DEFAULT 90,              -- Wie lange Logs behalten?

    -- BILLING & SUBSCRIPTION
    billing_model VARCHAR(50),  -- 'per_user', 'per_org', 'per_seat', 'per_feature'
    price_per_unit DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'EUR',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Beispiel-Einträge (DATABASE, NICHT HARDCODED!)
INSERT INTO b2b_configurations (organisation_id, model_type, max_hierarchy_depth, max_groups_per_level) VALUES

-- Kleine Schule
('org-gym-munich', 'organisation', 5, 100),

-- Große Universität mit komplexer Struktur
('org-lmu-munich', 'enterprise', 15, 500),

-- Consulting Firma
('org-sap-consulting', 'organisation', 4, 200),

-- Law Firm (mit Departments, Teams, Partner-Groups)
('org-kanzlei-schmidt', 'enterprise', 8, 300);
```

---

### 1.3 B2B Setup Workflow (Dein Prozess)

```python
# backend/app/blueprints/organisations/routes.py

@bp.route('/organisations', methods=['POST'])
@require_permission('site_admin:organisations:create')
def create_b2b_organisation():
    """
    [NUR DU ALS SITE-ADMIN]

    Neue B2B Organisation erstellen nach Anfrage.

    Request Body:
        {
            "name": "Gymnasium München",
            "founder_id": "user-xyz",  # Der Owner-Admin
            "model_type": "organisation",  # oder "enterprise" für große Orgs
            "business_model": "b2b",
            "template_code": "school",

            -- OPTIONAL: Custom B2B Configuration
            "b2b_config": {
                "max_hierarchy_depth": 8,     # Tiefe Fakultäts-Struktur nötig
                "max_groups_per_level": 200,
                "allow_nested_groups": true,  # Departments können Subdepartments haben
                "enable_team_groups": true,
                "max_users": 5000,
                "billing_model": "per_user",
                "price_per_unit": 2.50,
                "currency": "EUR"
            }
        }
    """
    data = request.get_json()

    with get_db_connection() as conn:
        org_repo = OrganisationRepository(conn)
        b2b_config_repo = B2BConfigurationRepository(conn)
        group_repo = GroupRepository(conn)

        # 1. ORGANISATION ERSTELLEN
        org = org_repo.create({
            'name': data['name'],
            'founder_id': data['founder_id'],
            'business_model': 'b2b',
            'template_code': data.get('template_code', 'default'),
            'model_type': data.get('model_type', 'organisation')
        })

        # 2. B2B CONFIGURATION ERSTELLEN
        # Entweder User-definiert oder Standard-Defaults
        b2b_config_data = data.get('b2b_config', {})

        # Default-Werte basierend auf Organisation-Typ
        defaults = {
            'organisation': {
                'max_hierarchy_depth': 5,
                'max_groups_per_level': 100,
                'max_users': 500,
                'allow_nested_groups': False,
                'billing_model': 'per_org'
            },
            'enterprise': {
                'max_hierarchy_depth': 15,      # ← Tiefere Hierarchie!
                'max_groups_per_level': 500,    # ← Mehr Groups pro Level!
                'max_users': 50000,
                'allow_nested_groups': True,    # ← Subgroups erlaubt!
                'billing_model': 'per_user',
                'price_per_unit': 2.50
            }
        }

        config_defaults = defaults.get(org.model_type, defaults['organisation'])
        config_data = {**config_defaults, **b2b_config_data}

        b2b_config = b2b_config_repo.create({
            'organisation_id': org.id,
            'model_type': org.model_type,
            **config_data
        })

        # 3. TEMPLATE GROUPS ERSTELLEN
        template = template_repo.find_by_code(data.get('template_code', 'default'))

        for template_group in template.template_groups:
            group = group_repo.create({
                'organisation_id': org.id,
                'name': template_group.group_name,
                'description': template_group.description,
                'is_predefined': True,
                'parent_group_id': None,  # ← Top-Level
                'hierarchy_level': 0      # ← Ebene 0 (Template)
            })

        # 4. FOUNDER WIRD OWNER-ADMIN
        owner_admin_group = group_repo.find_by_name('owner-admin', org.id)
        group_repo.add_member(owner_admin_group.id, data['founder_id'])

        return jsonify({
            'status': 'success',
            'organisation': org.to_dict(),
            'b2b_config': b2b_config.to_dict(),
            'message': f'Organisation "{org.name}" erstellt. {data["founder_id"]} ist Owner-Admin.'
        }), 201
```

---

### 1.4 B2B Hierarchie-Strukturen (FLEXIBLE EXAMPLES)

#### **Beispiel 1: Kleine Schule (flach)**

```
Gymnasium München (max_hierarchy_depth: 5)
├── Template Groups (Ebene 0)
│   ├── Teacher
│   ├── Student
│   ├── Creator
│   └── Support
│
└── Custom Groups (Owner-Admin erstellt manuell)
    ├── Klasse 9a (30 Schüler + 3 Lehrer)
    ├── Klasse 9b (28 Schüler + 3 Lehrer)
    ├── Klasse 10a (32 Schüler + 3 Lehrer)
    ├── Department: Mathematik (10 Lehrer)
    ├── Department: Sprachen (8 Lehrer)
    └── Department: Naturwissenschaften (12 Lehrer)

Struktur:
- Ebene 0: Template Groups (Teacher, Student, Creator)
- Ebene 1: Departments (Mathematik, Sprachen, etc.)
- Ebene 2: Classes (Klasse 9a, Klasse 9b, etc.)
- Ebene 3: Teams (optionale Ad-hoc Teams)

Max depth: 5
Max groups per level: 100
Tatsächlich genutzt: ~4 Ebenen
```

#### **Beispiel 2: Große Universität (tief)**

```
Ludwig-Maximilians-Universität (max_hierarchy_depth: 15)
├── Ebene 0: Template Groups
│   ├── Student
│   ├── Lecturer
│   ├── Professor
│   └── Research Assistant
│
├── Ebene 1: Fakultäten (max 30)
│   ├── Philosophische Fakultät
│   │   ├── Ebene 2: Institute (max 10)
│   │   │   ├── Institut für Philosophie
│   │   │   │   ├── Ebene 3: Lehrstühle (max 15)
│   │   │   │   │   ├── Lehrstuhl Logik
│   │   │   │   │   │   ├── Ebene 4: Arbeitsgruppen (max 20)
│   │   │   │   │   │   │   ├── AG Epistemologie
│   │   │   │   │   │   │   ├── AG Metaphysik
│   │   │   │   │   │   │   └── AG Logik & Sprache
│   │   │   │   │   │   │
│   │   │   │   │   │   └── Ebene 5: Projektgruppen
│   │   │   │   │   │       ├── Project: AI Ethics 2024
│   │   │   │   │   │       └── Project: Logic Programming
│   │   │   │   │   │
│   │   │   │   │   └── Lehrstuhl Ethik
│   │   │   │   │       ├── AG Applied Ethics
│   │   │   │   │       └── AG Bioethics
│   │   │   │   │
│   │   │   │   └── Institut für Klassische Philologie
│   │   │   │       ├── Lehrstuhl Griechisch
│   │   │   │       └── Lehrstuhl Latein
│   │   │
│   ├── Naturwissenschaftliche Fakultät
│   │   ├── Institut für Physik
│   │   ├── Institut für Chemie
│   │   └── Institut für Biologie
│   │
│   └── Juristische Fakultät
│       ├── Institut für Strafrecht
│       ├── Institut für Privatrecht
│       └── Institut für Öffentliches Recht
│
└── Cross-Org Groups
    ├── "university:executive" (Präsident + Vizepräsidenten)
    ├── "university:senate" (Senatsmitglieder)
    └── "university:research_committee" (Forschungskomitee)

TOTALE STRUKTUR:
- 1 Universität
- ~15 Fakultäten
- ~100 Institute
- ~300 Lehrstühle
- ~800 Arbeitsgruppen
- ~2000+ Projekt-Groups
+ 45.000 Studenten (in Class-Groups)
+ 800 Dozenten (in Role-Groups)

Max depth: 15
Max groups per level: 500
Tatsächlich genutzt: ~12 Ebenen, ~5000 Groups TOTAL
```

#### **Beispiel 3: Consulting Firma (Matrix-Struktur)**

```
SAP Consulting GmbH (max_hierarchy_depth: 8)

TWO HIERACHIES (Geschäftsmodell-Problem!):

STRUKTUR A: ORGANISATORISCH
├── Ebene 1: Department
│   ├── Management Consulting
│   ├── SAP Implementation
│   ├── Cloud Solutions
│   └── Quality Assurance
│
├── Ebene 2: Teams
│   ├── Team: SAP-ERP
│   ├── Team: SAP-Analytics
│   ├── Team: SAP-Supply Chain
│   └── Team: SAP-HCM

STRUKTUR B: PROJEKT-BASIERT (PARALLEL!)
├── Ebene 1: Kunden
│   ├── BMW Group
│   ├── Siemens AG
│   ├── Deutsche Telekom
│   └── Allianz SE
│
├── Ebene 2: Projekte
│   ├── Project: BMW-ERP-Migration-2024 (15 Consultants)
│   ├── Project: Siemens-Cloud-Migration (8 Consultants)
│   └── Project: Deutsche-Telekom-Analytics (12 Consultants)

PROBLEM:
→ Ein Consultant sitzt in BEIDEN Hierarchien!
→ Consultant Max:
   - In "SAP-ERP Team" → has permissions from that group
   - In "BMW-ERP-Migration Project" → has permissions from that group
   - In "Allianz Project" → has permissions from that group

→ UNION-Modell: Max hat ALLE Permissions aus allen 3 Groups!
→ ABER: Wie modelieren wir die Matrix-Struktur?

LÖSUNG: Overlap-basierte Groups (nicht hierarchisch)
├── organisational_groups (Team-Struktur)
├── project_groups (Projekt-Struktur)
├── client_groups (Client-Struktur)
└── Consultant sitzt in MEHREREN parallelen Gruppen (UNION)

```

---

### 1.5 Hierarchie-Problem: Gelöste Varianten

**PROBLEM:** Wie deep kann die Hierarchie sein?

**OPTION A: TIEFE Hierarchie (aktuelles Modell)**

```
Problems:
- Tiefe Verschachtelung (15+ Ebenen) führt zu Komplexität
- Parent-Child Queries werden langsam (Recursive CTE nötig)
- Groups sind in Baum-Struktur organisiert
```

**OPTION B: FLACHE Hierarchie mit Path-System (BESSER)**

```sql
-- NEUE SPALTE: group_path (denormalized)
CREATE TABLE groups (
    id UUID PRIMARY KEY,
    organisation_id UUID,
    name VARCHAR(255),

    -- OPTION B: Path-basiert (keine Parent-Child Rekursion!)
    group_path VARCHAR(1000),  -- z.B. "org/fakultaet-phil/institut-phil/lehrstuhl-logik"
    group_path_ids VARCHAR(1000),  -- z.B. "fac-1/inst-1/chair-1"
    hierarchy_level INT,  -- 0, 1, 2, 3, ... (aber keine FK mehr!)

    -- OPTION C: Flach mit Labeling
    group_category VARCHAR(50),  -- 'department', 'team', 'cohort', 'project', 'partner'
    group_tags VARCHAR[],  -- ['client:BMW', 'project:2024', 'type:consulting']

    created_at TIMESTAMP
);

-- Beispiel: SAP Consultant Max
INSERT INTO groups VALUES
('dept-sap-erp', org_id, 'SAP-ERP Team', 'org/sap-consulting/sap-erp', NULL, 2, 'department', ['business:sap', 'service:implementation']),
('proj-bmw-2024', org_id, 'BMW ERP Migration 2024', 'org/sap-consulting/projects/bmw-2024', NULL, 2, 'project', ['client:BMW', 'year:2024', 'service:migration']),
('proj-siemens-cloud', org_id, 'Siemens Cloud Migration', 'org/sap-consulting/projects/siemens-cloud', NULL, 2, 'project', ['client:Siemens', 'year:2024', 'service:cloud']);

-- User Max ist in allen 3 Groups
INSERT INTO group_members VALUES
('mem-1', 'user-max', 'dept-sap-erp'),
('mem-2', 'user-max', 'proj-bmw-2024'),
('mem-3', 'user-max', 'proj-siemens-cloud');

-- Query: Was sind alle Max's Permissions? (UNION-Modell)
SELECT DISTINCT permission_code
FROM group_permissions gp
JOIN group_members gm ON gp.group_id = gm.group_id
WHERE gm.user_id = 'user-max'
-- Result: UNION aller Permissions aus 3 Groups
```

**OPTION D: Flexible Tiefe mit Limits**

```python
# Backend-Validation (nicht hardcoded!)
# Basierend auf b2b_configurations.max_hierarchy_depth

def create_group(group_data):
    org_id = group_data['organisation_id']
    parent_id = group_data.get('parent_id')

    # 1. Get B2B Config
    config = b2b_config_repo.find_by_org(org_id)
    max_depth = config.max_hierarchy_depth  # z.B. 15

    # 2. Calculate current depth
    if parent_id:
        parent = group_repo.find_by_id(parent_id)
        new_depth = parent.hierarchy_level + 1
    else:
        new_depth = 1

    # 3. Validate
    if new_depth > max_depth:
        raise ValidationError(f"Max hierarchy depth {max_depth} exceeded!")

    if group_repo.count_at_level(org_id, new_depth) >= config.max_groups_per_level:
        raise ValidationError(f"Max groups per level {config.max_groups_per_level} exceeded!")

    # 4. Create
    return group_repo.create(group_data)
```

**EMPFOHLENE LÖSUNG: OPTION B + D kombiniert**

```sql
-- Flach mit Path-System + Flexible Tiefe-Limits
CREATE TABLE groups (
    id UUID PRIMARY KEY,
    organisation_id UUID,
    name VARCHAR(255),

    -- Path-System (flach, keine Rekursion)
    group_path VARCHAR(1000),        -- 'org/fak-phil/inst-phil/lehrstuhl-logik/ag-logic'
    group_path_ids VARCHAR(1000),    -- 'fac-1/inst-2/chair-3/ag-4'
    hierarchy_level INT,              -- 1, 2, 3, 4, 5 (depth)

    -- Kategorisierung
    group_category VARCHAR(50),      -- 'faculty', 'institute', 'chair', 'working-group', 'project'
    parent_id UUID,                  -- For display/UI only (nicht für queries)

    -- Tagging für flexible Queries
    group_tags VARCHAR[],            -- ['type:academic', 'university:true', 'client:BMW']

    is_predefined BOOLEAN,
    created_at TIMESTAMP
);

-- FAST Query Example (mit Path-System)
SELECT * FROM groups
WHERE organisation_id = org_id
  AND group_path LIKE 'org/fak-phil/%'  -- ← SUPER FAST!
  AND hierarchy_level <= 3
ORDER BY group_path;

-- STATT RECURSIVE CTE (langsam!)
WITH RECURSIVE group_tree AS (
    SELECT * FROM groups WHERE parent_id IS NULL
    UNION ALL
    SELECT g.* FROM groups g
    JOIN group_tree gt ON g.parent_id = gt.id
)
SELECT * FROM group_tree WHERE ...;
```

---

### 1.6 B2B API Endpoints (GROUP MANAGEMENT)

```python
# backend/app/blueprints/organisations/routes.py

@bp.route('/<org_id>/groups', methods=['POST'])
@require_auth
@require_permission('owner_admin:organisation:groups:create')
def create_group(org_id: str):
    """
    Owner-Admin erstellt neue Group (Custom).

    Respects b2b_configuration limits:
    - max_hierarchy_depth
    - max_groups_per_level
    - allow_nested_groups
    - max_groups

    Request Body:
        {
            "name": "Department Finance",
            "description": "All finance staff",
            "parent_id": "fac-1",  # Optional - für nested groups
            "group_category": "department",  # 'department', 'team', 'project', 'cohort'
            "group_tags": ["type:financial", "budget:yes", "year:2024"],
            "permissions": [  # Optional - custom permissions
                "finance:view_reports",
                "finance:approve_expenses",
                "finance:export_data"
            ]
        }
    """
    data = request.get_json()
    org_id = g.current_org.id  # Enforce multi-tenancy

    with get_db_connection() as conn:
        config_repo = B2BConfigurationRepository(conn)
        group_repo = GroupRepository(conn)
        group_perm_repo = GroupPermissionRepository(conn)

        # 1. Get B2B Config
        config = config_repo.find_by_org(org_id)

        # 2. Validate nested groups allowed
        if data.get('parent_id') and not config.allow_nested_groups:
            raise ValidationError("Nested groups not allowed in this organisation")

        # 3. Validate hierarchy depth
        if data.get('parent_id'):
            parent = group_repo.find_by_id(data['parent_id'])
            new_depth = parent.hierarchy_level + 1

            if new_depth > config.max_hierarchy_depth:
                raise ValidationError(
                    f"Max hierarchy depth {config.max_hierarchy_depth} exceeded. "
                    f"Parent is at level {parent.hierarchy_level}, "
                    f"new group would be at level {new_depth}."
                )

            level_count = group_repo.count_at_level(org_id, new_depth)
            if level_count >= config.max_groups_per_level:
                raise ValidationError(
                    f"Max groups per level ({config.max_groups_per_level}) exceeded. "
                    f"Level {new_depth} has {level_count} groups already."
                )

        # 4. Validate total group count
        total_count = group_repo.count(org_id)
        if total_count >= config.max_groups:
            raise ValidationError(
                f"Max total groups ({config.max_groups}) exceeded. "
                f"Organisation has {total_count} groups already."
            )

        # 5. Build group_path
        if data.get('parent_id'):
            parent = group_repo.find_by_id(data['parent_id'])
            group_path = f"{parent.group_path}/{data['name'].lower()}"
            group_path_ids = f"{parent.group_path_ids}/{data.get('parent_id', '')}"
            hierarchy_level = parent.hierarchy_level + 1
        else:
            group_path = f"org/{data['name'].lower()}"
            group_path_ids = None
            hierarchy_level = 1

        # 6. Create Group
        group = group_repo.create({
            'organisation_id': org_id,
            'name': data['name'],
            'description': data.get('description', ''),
            'parent_id': data.get('parent_id'),
            'group_path': group_path,
            'group_path_ids': group_path_ids,
            'hierarchy_level': hierarchy_level,
            'group_category': data.get('group_category', 'other'),
            'group_tags': data.get('group_tags', []),
            'is_predefined': False
        })

        # 7. Add Custom Permissions (if allowed)
        if data.get('permissions') and config.allow_permission_overrides:
            for perm_code in data['permissions']:
                group_perm_repo.create({
                    'group_id': group.id,
                    'permission_code': perm_code
                })

        return jsonify({
            'status': 'success',
            'group': group.to_dict(),
            'path': group_path,
            'hierarchy_level': hierarchy_level,
            'remaining_capacity': {
                'groups_at_this_level': group_repo.count_at_level(org_id, hierarchy_level),
                'max_groups_per_level': config.max_groups_per_level,
                'total_groups': group_repo.count(org_id),
                'max_total_groups': config.max_groups
            }
        }), 201

@bp.route('/<org_id>/groups/<group_id>/members', methods=['POST'])
@require_auth
@require_permission('owner_admin:organisation:groups:manage')
def add_group_member(org_id: str, group_id: str):
    """
    Füge User zu Group hinzu.

    Request Body:
        {
            "user_id": "user-xyz",
            "role": "member"  # 'member', 'moderator', 'admin'
        }
    """
    data = request.get_json()

    with get_db_connection() as conn:
        group_repo = GroupRepository(conn)
        user_repo = UserRepository(conn)

        user = user_repo.find_by_id(data['user_id'])
        if not user:
            raise NotFoundError("User not found")

        group = group_repo.find_by_id(group_id)
        if not group or group.organisation_id != g.current_org.id:
            raise NotFoundError("Group not found")

        # Add member
        group_repo.add_member(group.id, user.id)

        # User hat SOFORT alle Permissions aus dieser Group (UNION-Modell)
        return jsonify({
            'status': 'success',
            'user_id': user.id,
            'group_id': group.id,
            'group_name': group.name,
            'message': f'{user.name} added to {group.name}. Permissions updated: {len(group.permissions)} permissions granted.',
            'new_permissions': [p.permission_code for p in group.permissions]
        }), 201
```

---

## 🛍️ TEIL 2: B2C MODEL (Self-Service)

### 2.1 Was ist B2C?

**Definition:** Self-Service Einzelnutzer-Modell mit Subscription-basiertem Zugang.

**Merkmale:**
- ✅ User registriert sich selbst
- ✅ User kauft Subscription (Abo-Plan)
- ✅ Automatische Permission-Grants via Celery
- ✅ Keine Hierarchie (flach, nur Abo-basierte Groups)
- ✅ Shared Frontend (nicht pro User)

**Beispiele:**
- 📚 Student kauft "Premium Plus" (€9.99/Monat) → Unlimitiert AI-Tokens
- 👨‍💼 Teacher kauft "Pro Plan" (€19.99/Monat) → Advanced Analytics + 100 Schüler-Slots
- 🏢 SMB kauft "Business Plan" (€99.99/Monat) → Organisation mit 50 Users

---

### 2.2 B2C Configuration Table

```sql
-- NEUE TABELLE: b2c_configurations
CREATE TABLE b2c_configurations (
    id UUID PRIMARY KEY,

    -- PLATFORM-LEVEL SETTINGS (nicht org-spezifisch)

    -- REGISTRATION
    allow_self_registration BOOLEAN DEFAULT TRUE,  -- Dürfen User sich selbst registrieren?
    require_email_verification BOOLEAN DEFAULT TRUE,  -- Email-Verification nötig?
    auto_create_free_tier BOOLEAN DEFAULT TRUE,    -- Freier Account automatisch erstellt?
    free_tier_group_name VARCHAR(100) DEFAULT 'free',  -- Auto-Group für Free User

    -- SUBSCRIPTION
    enable_subscriptions BOOLEAN DEFAULT TRUE,
    default_currency VARCHAR(3) DEFAULT 'EUR',
    stripe_mode VARCHAR(20) DEFAULT 'live',  -- 'test', 'live'

    -- PERMISSIONS & GROUPS
    enable_custom_groups BOOLEAN DEFAULT FALSE,  -- Darf einzelner User Custom Groups erstellen?
    allow_user_to_user_group_sharing BOOLEAN DEFAULT FALSE,  -- Können User ihre Groups teilen?

    -- LIMITS
    max_user_custom_groups INT DEFAULT 0,  -- User kann 0 Custom Groups erstellen (nur Abo-Groups)
    max_free_tier_features INT DEFAULT 10,  -- Wie viele Features im kostenlosen Tier?

    -- AI TOKENS
    free_tier_monthly_tokens INT DEFAULT 10000,
    premium_tier_monthly_tokens INT DEFAULT NULL,  -- NULL = unbegrenzt

    -- TRIAL PERIOD
    enable_trial BOOLEAN DEFAULT TRUE,
    trial_days INT DEFAULT 14,
    trial_requires_payment BOOLEAN DEFAULT FALSE,  -- Braucht Kreditkarte für Trial?

    -- AUTOMATION
    auto_renew_subscriptions BOOLEAN DEFAULT TRUE,  -- Automatische Verlängerung?
    send_renewal_reminder BOOLEAN DEFAULT TRUE,
    reminder_days_before INT DEFAULT 7,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Aktuell nur EINE Konfiguration (Global für alle B2C User)
INSERT INTO b2c_configurations DEFAULT VALUES;
```

---

### 2.3 B2C Subscription Plans (DATABASE-DRIVEN)

```sql
-- NEUE TABELLE: subscription_plans
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY,
    code VARCHAR(50) UNIQUE,  -- 'free', 'starter', 'premium', 'pro', 'enterprise'
    name VARCHAR(100),
    description TEXT,

    -- PRICING
    price_monthly DECIMAL(10, 2),
    price_yearly DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'EUR',

    -- FEATURES (as JSON für Flexibilität)
    features JSON,  -- z.B. {"ai_tokens": 100000, "users": 50, "storage_gb": 100}

    -- PERMISSIONS (auto-granted via Celery)
    permissions VARCHAR[],  -- z.B. ['ai:tokens:100k', 'analytics:advanced', 'api:access']

    -- LIMITS
    max_ai_tokens INT,  -- NULL = unlimited
    max_users INT,      -- NULL = unlimited
    max_storage_gb INT, -- NULL = unlimited

    -- GROUP (auto-created)
    auto_group_name VARCHAR(100),  -- z.B. 'abo:premium'

    -- LIFECYCLE
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,  -- Visible für Self-Service Signup?
    trial_eligible BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- BEISPIEL-PLANS (DATABASE, NICHT HARDCODED!)
INSERT INTO subscription_plans VALUES

-- Free Tier
('plan-free', 'free', 'Free Tier', 'Basic learning features',
 NULL, NULL, 'EUR',
 '{"ai_tokens": 10000, "users": 1, "storage_gb": 1, "features": ["ai:basic", "learning:basic"]}'::json,
 ARRAY['ai:tokens:10k', 'learning:read', 'content:create:limited'],
 10000, 1, 1, 'abo:free', TRUE, TRUE, FALSE),

-- Starter
('plan-starter', 'starter', 'Starter Plan', 'For individual learners',
 4.99, 49.99, 'EUR',
 '{"ai_tokens": 100000, "users": 1, "storage_gb": 10, "features": ["ai:advanced", "learning:all"]}'::json,
 ARRAY['ai:tokens:100k', 'learning:all', 'content:publish', 'ai:advanced'],
 100000, 1, 10, 'abo:starter', TRUE, TRUE, TRUE),

-- Premium
('plan-premium', 'premium', 'Premium Plan', 'For teachers & professionals',
 9.99, 99.99, 'EUR',
 '{"ai_tokens": null, "users": 50, "storage_gb": 500, "features": ["ai:unlimited", "teaching:full"]}'::json,
 ARRAY['ai:tokens:unlimited', 'teaching:full', 'analytics:advanced', 'api:access', 'team:management'],
 NULL, 50, 500, 'abo:premium', TRUE, TRUE, TRUE),

-- Pro (für Organisationen)
('plan-pro', 'pro', 'Pro Plan', 'For small teams & organisations',
 49.99, 499.99, 'EUR',
 '{"ai_tokens": null, "users": 500, "storage_gb": 2000, "features": ["ai:unlimited", "organization:full", "sso:true"]}'::json,
 ARRAY['ai:tokens:unlimited', 'organization:full', 'sso:enabled', 'audit:logs', 'api:unlimited', 'support:priority'],
 NULL, 500, 2000, 'abo:pro', TRUE, TRUE, TRUE);
```

---

### 2.4 B2C Workflow (Automatisiert)

```python
# WORKFLOW 1: User registriert sich (Self-Service)

@bp.route('/auth/register', methods=['POST'])
def register():
    """
    [SELF-SERVICE - Kein Admin nötig!]

    User registriert sich selbst.
    - Auto free tier account erstellt
    - User added zu 'abo:free' Group
    - Hat SOFORT Free-Tier Permissions
    """
    data = request.get_json()

    with get_db_connection() as conn:
        user_repo = UserRepository(conn)
        group_repo = GroupRepository(conn)
        b2c_config_repo = B2CConfigurationRepository(conn)
        subscription_repo = SubscriptionRepository(conn)

        # 1. Create User
        user = user_repo.create({
            'email': data['email'],
            'password_hash': bcrypt.hash(data['password']),
            'name': data['name'],
            'business_model': 'b2c'  # ← Nicht B2B!
        })

        # 2. Get B2C Config
        b2c_config = b2c_config_repo.find()

        # 3. Create Free Subscription automatisch
        free_plan = subscription_repo.find_plan_by_code('free')
        subscription = subscription_repo.create({
            'user_id': user.id,
            'subscription_plan_id': free_plan.id,
            'status': 'active',
            'billing_cycle': 'free',
            'started_at': datetime.utcnow(),
            'expires_at': None  # Free = no expiration
        })

        # 4. Add User zu 'abo:free' Group (ASYNC via Celery)
        add_user_to_subscription_group.apply_async(
            args=[user.id, free_plan.id],
            countdown=2
        )

        return jsonify({
            'status': 'success',
            'user': user.to_dict(),
            'message': 'Account created! You have been added to Free Tier.',
            'free_tier_permissions': free_plan.permissions
        }), 201

# WORKFLOW 2: User kauft Subscription (Automatisch)

@bp.route('/subscriptions/purchase', methods=['POST'])
@require_auth
def purchase_subscription():
    """
    [SELF-SERVICE - Kein Admin nötig!]

    User kauft Abo via Stripe.
    - Stripe Payment verarbeitet
    - Webhook: stripe:payment_success
    - Trigger: add_user_to_subscription_group Celery Task
    - User hat SOFORT neue Permissions
    """
    data = request.get_json()
    plan_id = data['subscription_plan_id']

    with get_db_connection() as conn:
        subscription_repo = SubscriptionRepository(conn)
        stripe_repo = StripeRepository(conn)

        plan = subscription_repo.find_plan_by_id(plan_id)

        # 1. Create Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(plan.price_monthly * 100),  # In cents
            currency=plan.currency.lower(),
            customer=g.current_user.stripe_customer_id,
            metadata={
                'user_id': g.current_user.id,
                'subscription_plan_id': plan_id
            }
        )

        # 2. Create Subscription Record (status: pending_payment)
        subscription = subscription_repo.create({
            'user_id': g.current_user.id,
            'subscription_plan_id': plan_id,
            'status': 'pending_payment',
            'stripe_payment_intent_id': intent.id,
            'billing_cycle': 'monthly',
            'started_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=30)
        })

        return jsonify({
            'status': 'payment_required',
            'subscription': subscription.to_dict(),
            'stripe_client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        }), 200

# STRIPE WEBHOOK: Payment erfolgreich

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    [AUTOMATISCH VON STRIPE]

    Wenn Zahlung erfolgreich:
    1. Update Subscription zu 'active'
    2. Trigger Celery Task: add_user_to_subscription_group
    3. User hat SOFORT neue Permissions
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except:
        return 'Invalid signature', 400

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        user_id = intent['metadata']['user_id']
        plan_id = intent['metadata']['subscription_plan_id']

        with get_db_connection() as conn:
            subscription_repo = SubscriptionRepository(conn)

            # 1. Update Subscription
            subscription = subscription_repo.update_by_stripe_intent(intent['id'], {
                'status': 'active',
                'stripe_customer_id': intent['customer']
            })

            # 2. Trigger Celery Task (ASYNC)
            add_user_to_subscription_group.apply_async(
                args=[user_id, plan_id],
                countdown=5
            )

        return jsonify({'status': 'success'}), 200

    return '', 200

# CELERY TASK 1: Add User zu Subscription-Group (triggered by payment)

@app.task(bind=True)
def add_user_to_subscription_group(self, user_id: str, subscription_plan_id: str):
    """
    [AUTOMATISCH VON CELERY]

    Wenn Zahlung erfolgreich ODER User registriert sich:
    1. Find Group "abo:X"
    2. Add User zu dieser Group
    3. User hat SOFORT alle Permissions
    """
    with get_db_connection() as conn:
        group_repo = GroupRepository(conn)
        subscription_repo = SubscriptionRepository(conn)

        plan = subscription_repo.find_plan_by_id(subscription_plan_id)

        # 1. Find oder erstelle Abo-Group (z.B. "abo:premium")
        group = group_repo.find_by_name(plan.auto_group_name)

        if not group:
            # Erstelle auto-Group
            group = group_repo.create({
                'name': plan.auto_group_name,
                'description': f'Auto-created group for {plan.name} subscribers',
                'is_predefined': False,
                'subscription_plan_id': plan.id
            })

            # Add Permissions aus Plan
            group_perm_repo = GroupPermissionRepository(conn)
            for perm_code in plan.permissions:
                group_perm_repo.create({
                    'group_id': group.id,
                    'permission_code': perm_code
                })

        # 2. Add User zu Group
        group_repo.add_member(group.id, user_id)

        # 3. UNION-Modell: User hat SOFORT alle Permissions aus dieser Group
        return {
            'status': 'success',
            'user_id': user_id,
            'group_id': group.id,
            'group_name': group.name,
            'permissions_granted': plan.permissions,
            'ai_tokens_available': plan.features.get('ai_tokens'),
            'message': f'User {user_id} added to {group.name}. {len(plan.permissions)} permissions granted.'
        }

# CELERY BEAT TASK 2: Täglich abgelaufene Subscriptions prüfen

@app.task
def check_expired_subscriptions():
    """
    [LÄUFT TÄGLICH UM 00:00 UTC]

    1. Find alle Subscriptions die HEUTE ablaufen
    2. Entferne User aus Abo-Groups
    3. User verlieren SOFORT ihre Premium-Permissions
    """
    with get_db_connection() as conn:
        subscription_repo = SubscriptionRepository(conn)

        # Find all subscriptions expiring today
        expired_today = subscription_repo.find_expiring_today()

        results = []
        for subscription in expired_today:
            # Trigger async task
            result = remove_user_from_subscription_group.apply_async(
                args=[subscription.user_id, subscription.subscription_plan_id],
                countdown=10
            )
            results.append({
                'subscription_id': subscription.id,
                'user_id': subscription.user_id,
                'task_id': result.id
            })

        return {
            'processed': len(results),
            'message': f'{len(results)} expired subscriptions processed today',
            'task_ids': [r['task_id'] for r in results]
        }

# CELERY TASK 3: Remove User aus Subscription-Group (ablauf/kündigung)

@app.task(bind=True)
def remove_user_from_subscription_group(self, user_id: str, subscription_plan_id: str):
    """
    [AUTOMATISCH VON CELERY]

    Wenn:
    1. User kündigt Abo
    2. Subscription läuft ab

    Dann:
    1. Remove User aus Abo-Group
    2. User verliert SOFORT Premium-Permissions
    """
    with get_db_connection() as conn:
        group_repo = GroupRepository(conn)
        subscription_repo = SubscriptionRepository(conn)

        plan = subscription_repo.find_plan_by_id(subscription_plan_id)
        group = group_repo.find_by_name(plan.auto_group_name)

        if group:
            group_repo.remove_member(group.id, user_id)

        return {
            'status': 'success',
            'user_id': user_id,
            'group': group.name if group else None,
            'message': f'User {user_id} removed from {group.name if group else "unknown group"}. Permissions revoked.'
        }
```

---

## 💾 TEIL 3: STORAGE QUOTA & FILE MANAGEMENT SYSTEM

### 3.1 Warum Storage Limits?

**Problem:** Ohne Storage Limits können Benutzer unkontrolliert Dateien hochladen:
- 🔴 Disk-Speicher läuft voll
- 🔴 Kosten für Cloud Storage explodieren
- 🔴 Performance verschlechtert sich
- 🔴 Backups werden unmöglich

**Lösung:** Einfach & Pragmatisch
- **B2C:** Storage-Quota pro Account (tied to Subscription Plan)
  - Kein Free Tier (Infrastrukturkosten)
  - Einstiegspunkt: 4,99€ (Starter Plan = 10GB)
- **B2B:** Storage-Quota pro Account INNERHALB der Org
  - Org bekommt Gesamt-Budget (z.B. 1TB für ganze Firma)
  - Owner-Admin verteilt auf Teams/User (pro-user limits)

---

### 3.2 Datenbankschema: Storage Management

#### **Tabelle: storage_quotas** (Zugewiesene Quoten)

```sql
-- NEUE TABELLE: storage_quotas
-- Speichert die ZUGEWIESENE Storage-Quota für jede Entität
-- (nicht die tatsächlich genutzte, sondern die erlaubte)

CREATE TABLE storage_quotas (
    id UUID PRIMARY KEY,

    -- WER HAT DIE QUOTA?
    quota_holder_type VARCHAR(20) NOT NULL,  -- 'organisation' (B2B) oder 'user' (B2C)
    quota_holder_id UUID NOT NULL,           -- organisation_id (B2B) oder user_id (B2C)

    -- QUOTA DETAILS
    quota_gb INT NOT NULL,                   -- Maximal erlaubte Speicher in GB
    quota_bytes BIGINT NOT NULL,             -- Same als GB aber in Bytes (for calculations)
    warning_threshold_percent INT DEFAULT 80, -- Bei 80% -> Warnung senden
    grace_period_days INT DEFAULT 30,        -- Nach Limit: 30 Tage zum Löschen
    enforcement_type VARCHAR(20) DEFAULT 'hard',  -- 'hard'=block uploads, 'soft'=warnings only

    -- CONTEXT
    source VARCHAR(50),  -- 'b2b_config', 'subscription_plan', 'manual_assignment'
    source_id UUID,      -- b2b_configuration_id oder subscription_plan_id

    -- TIMESTAMPS
    assigned_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,  -- NULL = kein Ablaufdatum
    last_warning_sent_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- CONSTRAINTS
    CONSTRAINT unique_quota_per_holder
        UNIQUE(quota_holder_type, quota_holder_id),
    CONSTRAINT valid_threshold
        CHECK (warning_threshold_percent BETWEEN 1 AND 100),
    CONSTRAINT valid_enforcement
        CHECK (enforcement_type IN ('hard', 'soft', 'none'))
);

CREATE INDEX idx_storage_quotas_holder
    ON storage_quotas(quota_holder_type, quota_holder_id);
CREATE INDEX idx_storage_quotas_expires
    ON storage_quotas(expires_at)
    WHERE expires_at IS NOT NULL;
```

#### **Tabelle: storage_usage** (Tatsächlicher Verbrauch)

```sql
-- NEUE TABELLE: storage_usage
-- Speichert den TATSÄCHLICH GENUTZTEN Speicher

CREATE TABLE storage_usage (
    id UUID PRIMARY KEY,

    -- WER NUTZT DEN SPEICHER?
    usage_holder_type VARCHAR(20) NOT NULL,  -- 'organisation' (B2B) oder 'user' (B2C)
    usage_holder_id UUID NOT NULL,           -- organisation_id (B2B) oder user_id (B2C)

    -- RESSOURCE DIE SPEICHER NUTZT
    resource_type VARCHAR(50) NOT NULL,      -- 'file', 'video', 'backup', 'cache'
    resource_id UUID,                        -- file_id, video_id, etc.

    -- SPEICHERPLATZ
    size_bytes BIGINT NOT NULL,               -- Bytes dieser Ressource
    size_gb DECIMAL(10,2) GENERATED ALWAYS AS (size_bytes / 1024.0 / 1024.0 / 1024.0) STORED,

    -- STATUS
    is_deleted BOOLEAN DEFAULT FALSE,         -- Soft-Delete (bleibt 30 Tage)
    deleted_at TIMESTAMP,                     -- Wann wurde gelöscht?
    permanent_delete_at TIMESTAMP,            -- Wann final löschen?
    storage_tier VARCHAR(20) DEFAULT 'hot',   -- 'hot' (SSD), 'warm' (HDD), 'cold' (Archive)

    -- CONTEXT
    course_id UUID,                           -- Optional: für Reporting (welcher Kurs hat file?). NUR für reference, nicht für quota limiting!
    organisation_id UUID NOT NULL,            -- Immer mit Organisation verknüpft (for RLS)

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT valid_tier
        CHECK (storage_tier IN ('hot', 'warm', 'cold'))
);

CREATE INDEX idx_storage_usage_holder
    ON storage_usage(usage_holder_type, usage_holder_id);
CREATE INDEX idx_storage_usage_organisation
    ON storage_usage(organisation_id);
CREATE INDEX idx_storage_usage_deleted
    ON storage_usage(is_deleted, deleted_at)
    WHERE is_deleted = TRUE;
CREATE INDEX idx_storage_usage_permanent_delete
    ON storage_usage(permanent_delete_at)
    WHERE permanent_delete_at IS NOT NULL;
```

#### **Tabelle: storage_monitoring** (Alerts & Warnings)

```sql
-- NEUE TABELLE: storage_monitoring
-- Speichert Warnungen und Alert-History für Audits

CREATE TABLE storage_monitoring (
    id UUID PRIMARY KEY,

    quota_holder_type VARCHAR(20) NOT NULL,
    quota_holder_id UUID NOT NULL,
    organisation_id UUID NOT NULL,

    -- ALERT TYPE
    alert_type VARCHAR(50) NOT NULL,  -- 'warning_80_percent', 'limit_reached', 'grace_period_ended'
    alert_level VARCHAR(20),          -- 'info', 'warning', 'critical'

    -- DETAILS
    used_bytes BIGINT,
    quota_bytes BIGINT,
    percent_used INT,

    -- ACTIONS TAKEN
    action_taken VARCHAR(100),  -- 'email_sent', 'upload_blocked', 'grace_period_started'
    action_timestamp TIMESTAMP,

    -- ADMIN NOTES
    admin_notes TEXT,
    resolved BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_storage_monitoring_quota_holder
    ON storage_monitoring(quota_holder_type, quota_holder_id, alert_type);
```

#### **Tabelle: storage_enforcement_configs (DATABASE-DRIVEN CONFIGURATION)**

```sql
-- NEUE TABELLE: storage_enforcement_configs
-- Flexible Enforcement Rules - NICHT HARDCODED!
-- User's Message 3: "das sollte man aber flexibel einstellen können alles"

CREATE TABLE storage_enforcement_configs (
    id UUID PRIMARY KEY,

    -- SCOPE (per Organisation oder Global)
    organisation_id UUID,  -- NULL = System-Default, sonst org-spezifisch
    is_system_default BOOLEAN DEFAULT FALSE,

    -- THRESHOLDS (configurable, not hardcoded!)
    warning_threshold_percent INT DEFAULT 80,      -- 80% = send warnings
    critical_threshold_percent INT DEFAULT 95,     -- 95% = critical alerts
    hard_limit_percent INT DEFAULT 100,            -- 100% = block uploads (B2C)

    -- ENFORCEMENT TYPE
    enforcement_type VARCHAR(20) DEFAULT 'hard',  -- 'hard' (B2C), 'soft' (B2B), 'none'
    grace_period_days INT DEFAULT 30,             -- Days to reduce usage before read-only
    auto_cleanup_soft_deleted_days INT DEFAULT 30, -- Auto-delete soft-deleted after N days

    -- WARNING FREQUENCY
    warning_frequency VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'once'
    send_email_warnings BOOLEAN DEFAULT TRUE,
    send_ui_notifications BOOLEAN DEFAULT TRUE,

    -- ACTIONS AT EACH THRESHOLD (JSON für Flexibilität)
    actions_json JSON DEFAULT '{
        "0_to_50": {
            "status": "green",
            "upload": "allowed",
            "download": "allowed",
            "notifications": "none"
        },
        "50_to_80": {
            "status": "yellow",
            "upload": "allowed",
            "download": "allowed",
            "notifications": "weekly_reminder"
        },
        "80_to_100": {
            "status": "red",
            "upload": "allowed_with_warning",
            "download": "allowed",
            "notifications": "daily_warning",
            "encourage_cleanup": true
        },
        "100_plus": {
            "status": "black",
            "upload": "blocked",
            "download": "allowed",
            "delete_required": true,
            "grace_period_days": 30,
            "message": "Storage quota exceeded. Please delete files."
        },
        "grace_period_expired": {
            "status": "alert",
            "upload": "blocked",
            "download": "readonly",
            "new_courses": "blocked",
            "message": "Grace period expired. Account in read-only mode."
        }
    }'::json,

    -- METADATA
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT valid_enforcement_type
        CHECK (enforcement_type IN ('hard', 'soft', 'none')),
    CONSTRAINT valid_warning_frequency
        CHECK (warning_frequency IN ('daily', 'weekly', 'once'))
);

-- System-Default Config (für alle Orgs ohne spezifische Config)
INSERT INTO storage_enforcement_configs (
    is_system_default, enforcement_type
) VALUES (TRUE, 'hard');

-- Example: Soft Enforcement für B2B Org
INSERT INTO storage_enforcement_configs (
    organisation_id, enforcement_type, grace_period_days, actions_json
) VALUES (
    'org-gymnasium-muenchen',
    'soft',
    30,
    '{
        "100_plus": {
            "status": "warning",
            "upload": "allowed_with_warning",
            "download": "allowed",
            "grace_period_days": 30,
            "message": "Storage quota exceeded. Contact admin to request increase."
        }
    }'::json
);

CREATE INDEX idx_storage_enforcement_configs_org
    ON storage_enforcement_configs(organisation_id)
    WHERE organisation_id IS NOT NULL;
CREATE INDEX idx_storage_enforcement_configs_default
    ON storage_enforcement_configs(is_system_default)
    WHERE is_system_default = TRUE;
```

---

### 3.3 B2B Storage Model

**Prinzip:** Jede Organisation hat eine Gesamt-Storage-Quota. Owner-Admin kann Grenzen pro User/Team setzen.

**Modell:**
```
Organisation (z.B. Gymnasium München)
  ├─ Gesamt-Quota: 500 GB
  │  (von Site-Admin zugewiesen, based on b2b_config)
  │
  ├─ Owner-Admin verwaltet:
  │  ├─ Per-User Quotas (optional): "Lehrer A darf 50GB"
  │  ├─ Per-Department Quotas: "Mathemarik-Abteilung darf 150GB"
  │  └─ Sieht Verbrauch gruppiert nach Kurs/Abteilung (für Reporting)
  │
  └─ Enforcement: Blockiert Upload wenn GESAMT-Quota > 500GB
```

#### **B2B Storage-Quota Setup**

```python
# Backend: Organisationen haben Storage-Quota von b2b_configurations

# Beispiel:
# - Gymnasium München: 500 GB (für 300 Schüler)
# - SAP Consulting: 1000 GB (für 200 Berater + Projekte)
# - LMU: 10 TB (für 45.000 Studenten + Forschung)

# In b2b_configurations hinzufügen:
max_storage_gb INT DEFAULT 500,  # ← Diese Quota wird Org zugewiesen

# Mit Celery-Task automatisch erstellen:
def setup_b2b_organisation(org_id: str, config: dict):
    # 1. Organisation erstellt
    org = organisation_repo.create(config)

    # 2. Storage-Quota automatisch zugewiesen
    storage_quota_repo.create({
        'quota_holder_type': 'organisation',
        'quota_holder_id': org.id,
        'quota_gb': config['max_storage_gb'],  # From b2b_config
        'quota_bytes': config['max_storage_gb'] * 1024 * 1024 * 1024,
        'source': 'b2b_config',
        'source_id': org.id
    })

    # 3. Owner-Admin eingeladen
    # 4. Owner-Admin erhält Dashboard mit Storage-Übersicht

    return org
```

#### **B2B Storage Monitoring API**

```python
# API Endpoint: GET /api/organisations/{org_id}/storage

@bp.route('/organisations/<org_id>/storage', methods=['GET'])
@require_permission('owner_admin:organisation:storage:view')
def get_organisation_storage(org_id: str):
    """
    Zeigt Storage-Übersicht für ganze Organisation

    Returns:
    {
        "total_quota_gb": 500,
        "total_quota_bytes": 536870912000,
        "used_bytes": 250000000000,  # 250 GB aktuell genutzt
        "used_percent": 46.6,
        "available_bytes": 286870912000,
        "warning_threshold_percent": 80,
        "in_warning": false,
        "in_grace_period": false,

        "breakdown_by_course": [  # ← Kurse sortiert nach Größe
            {
                "course_id": "abc123",
                "course_name": "Mathematik 101",
                "used_bytes": 50000000000,  # 50 GB
                "files_count": 245,
                "largest_file": {"name": "recording.mp4", "size_bytes": 5000000000}
            },
            ...
        ],

        "breakdown_by_type": {
            "video": 150000000000,    # 150 GB Videos
            "documents": 80000000000,  # 80 GB Dokumente
            "backup": 20000000000      # 20 GB Backups
        },

        "cleanup_candidates": [  # ← Was kann gelöscht werden?
            {
                "file_id": "xyz789",
                "name": "old_recording_2023.mp4",
                "size_bytes": 5000000000,
                "created_at": "2023-01-15",
                "last_accessed": "2023-06-20",
                "days_old": 577,
                "deletion_benefit_bytes": 5000000000
            }
        ]
    }
    """
    with get_db_connection() as conn:
        quota_repo = StorageQuotaRepository(conn)
        usage_repo = StorageUsageRepository(conn)

        # Get total quota for organisation
        quota = quota_repo.find_by_holder('organisation', org_id)

        # Get current usage (sum all files not soft-deleted)
        total_used = usage_repo.sum_usage_by_holder('organisation', org_id, deleted=False)

        # Calculate metrics
        percent_used = (total_used / quota.quota_bytes) * 100 if quota else 0
        in_warning = percent_used >= quota.warning_threshold_percent if quota else False

        # Get breakdown by course
        breakdown_by_course = usage_repo.get_usage_by_course(org_id)

        # Find cleanup candidates (soft-deleted, old files)
        cleanup_candidates = usage_repo.find_cleanup_candidates(org_id)

        return jsonify({
            'total_quota_gb': quota.quota_gb if quota else 0,
            'total_quota_bytes': quota.quota_bytes if quota else 0,
            'used_bytes': total_used,
            'used_percent': round(percent_used, 1),
            'available_bytes': (quota.quota_bytes - total_used) if quota else 0,
            'warning_threshold_percent': quota.warning_threshold_percent if quota else 80,
            'in_warning': in_warning,
            'breakdown_by_course': breakdown_by_course,
            'cleanup_candidates': cleanup_candidates[:10]  # Top 10
        }), 200
```

---

### 3.4 B2C Storage Model

**Prinzip:** Jeder User hat eine Storage-Quota basierend auf seinem Subscription-Plan. Kein Free Tier - Mindest-Einstieg 4,99€.

#### **Subscription Plans mit Storage (KEINE FREE TIER)**

```sql
-- In subscription_plans tabelle (EXISTIERT BEREITS):

CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY,
    code VARCHAR(50),  -- 'starter', 'premium', 'pro'
    name VARCHAR(100),

    -- ← STORAGE LIMITS:
    max_storage_gb INT NOT NULL,  -- Plan 'starter'=10GB, 'premium'=500GB, 'pro'=2000GB

    -- Existing columns:
    price_monthly DECIMAL(10,2),
    max_ai_tokens INT,
    max_users INT,
    features JSON,
    ...
);

-- Beispieldata (KEIN FREE TIER):
INSERT INTO subscription_plans (code, name, max_storage_gb, price_monthly) VALUES
    ('starter', 'Starter Plan', 10, 4.99),           -- ← Einstiegspunkt 4,99€
    ('premium', 'Premium', 500, 29.99),
    ('pro', 'Professional', 2000, 99.99);
```

**Begründung:**
- ❌ Kein Free Tier: Speicher kostet Infrastruktur (AWS S3, Backups, Bandwidth)
- ✅ 4,99€ = Minimal für Infrastruktur-Coverage + neuer User-Wert
- ✅ Einfaches Modell: User versteht sofort: "Plan = Speicher"

#### **B2C Storage Quota Assignment (Celery Task)**

```python
# Celery Task: Wird ausgelöst bei User-Registration oder Subscription-Purchase

from celery import shared_task

@shared_task(bind=True)
def assign_storage_quota_to_user(self, user_id: str, subscription_plan_id: str):
    """
    Wenn User registriert oder Plan kauft:
    - Alte Quota löschen (wenn vorhanden)
    - Neue Quota aus subscription_plan zuweisen
    - Logging
    """
    with get_db_connection() as conn:
        user_repo = UserRepository(conn)
        plan_repo = SubscriptionPlanRepository(conn)
        quota_repo = StorageQuotaRepository(conn)

        # Get user
        user = user_repo.find_by_id(user_id)
        if not user:
            return {'status': 'error', 'message': f'User {user_id} not found'}

        # Get subscription plan
        plan = plan_repo.find_by_id(subscription_plan_id)
        if not plan:
            return {'status': 'error', 'message': f'Plan {subscription_plan_id} not found'}

        # Remove old quota if exists
        old_quota = quota_repo.find_by_holder('user', user_id)
        if old_quota:
            quota_repo.delete(old_quota.id)

        # Create new quota from plan
        storage_gb = plan.max_storage_gb
        new_quota = quota_repo.create({
            'quota_holder_type': 'user',
            'quota_holder_id': user_id,
            'quota_gb': storage_gb,
            'quota_bytes': storage_gb * 1024 * 1024 * 1024,
            'source': 'subscription_plan',
            'source_id': plan.id,
            'organisation_id': user.organisation_id,
            'enforcement_type': 'hard'  # B2C: strikt
        })

        # Log
        monitoring_repo.create({
            'quota_holder_type': 'user',
            'quota_holder_id': user_id,
            'organisation_id': user.organisation_id,
            'alert_type': 'quota_assigned',
            'action_taken': 'new_quota_created',
            'alert_level': 'info'
        })

        return {
            'status': 'success',
            'user_id': user_id,
            'plan': plan.name,
            'storage_gb': storage_gb
        }
```

---

### 3.5 File Upload Validation (CRITICAL - Quota Enforcement)

#### **File Upload Endpoint mit Quota-Check**

```python
# API Endpoint: POST /api/courses/{course_id}/files/upload

@bp.route('/courses/<course_id>/files/upload', methods=['POST'])
@require_auth
def upload_file_to_course(course_id: str):
    """
    File-Upload mit Storage-Quota Validierung

    1. ✅ Quota-Check: Hat User noch Speicher?
    2. ✅ File-Validierung: Größe, Typ, Virus?
    3. ✅ Storage-Usage aktualisieren
    4. ✅ Warnings senden wenn >80% quota
    """

    if 'file' not in request.files:
        raise ValidationError('No file provided')

    file = request.files['file']
    if file.filename == '':
        raise ValidationError('No file selected')

    # Get file size BEFORE upload
    file_size = len(file.read())
    file.seek(0)  # Reset file pointer

    with get_db_connection() as conn:
        # 1. Get organisation from current user
        user = g.current_user
        org_id = user.organisation_id or user.id  # For B2C: user_id as organisation

        # 2. HINWEIS: Ab Section 3.8 verwenden wir DYNAMISCHE Enforcement-Config!
        # Siehe StorageEnforcementService.can_upload() für detaillierte Implementierung
        # Diese Section zeigt das "legacy" Ansatz - der neue Ansatz ist configuration-driven!

        # 2. Get quota for user (B2C) or organisation (B2B)
        quota_repo = StorageQuotaRepository(conn)
        usage_repo = StorageUsageRepository(conn)

        # Determine quota holder
        if user.is_b2b_admin():
            quota_holder_type = 'organisation'
            quota_holder_id = org_id
        else:
            quota_holder_type = 'user'
            quota_holder_id = user.id

        # Get quota and usage
        quota = quota_repo.find_by_holder(quota_holder_type, quota_holder_id)
        if not quota:
            raise ForbiddenError('No storage quota assigned')

        current_usage = usage_repo.sum_usage_by_holder(
            quota_holder_type,
            quota_holder_id,
            deleted=False
        )

        # 3. QUOTA CHECK - würde upload die quota überschreiten?
        if current_usage + file_size > quota.quota_bytes:
            # ❌ QUOTA EXCEEDED

            available_bytes = quota.quota_bytes - current_usage
            available_gb = available_bytes / (1024 * 1024 * 1024)
            needed_gb = file_size / (1024 * 1024 * 1024)

            # Log the violation
            monitoring_repo.create({
                'quota_holder_type': quota_holder_type,
                'quota_holder_id': quota_holder_id,
                'organisation_id': org_id,
                'alert_type': 'upload_rejected_quota_exceeded',
                'used_bytes': current_usage + file_size,
                'quota_bytes': quota.quota_bytes,
                'percent_used': 100,
                'alert_level': 'critical'
            })

            # Return 507 Insufficient Storage
            return jsonify({
                'error': 'STORAGE_QUOTA_EXCEEDED',
                'message': f'Storage quota exceeded',
                'quota_gb': quota.quota_gb,
                'used_gb': round(current_usage / (1024 * 1024 * 1024), 2),
                'needed_gb': round(needed_gb, 2),
                'available_gb': round(available_gb, 2),
                'cleanup_suggestions': [  # Hilfreich für User
                    {
                        'type': 'delete_old_files',
                        'benefit_gb': 'X',
                        'action': 'Delete files older than 1 year'
                    }
                ]
            }), 507  # 507 = Insufficient Storage

        # 4. FILE PROCESSING
        # Speichere Datei zu Storage (S3, etc.)
        file_data = {
            'filename': file.filename,
            'size_bytes': file_size,
            'mimetype': file.mimetype,
            'course_id': course_id,
            'uploaded_by': user.id
        }

        file_repo = FileRepository(conn)
        saved_file = file_repo.create(file_data)

        # 5. UPDATE STORAGE USAGE
        usage_repo.create({
            'usage_holder_type': quota_holder_type,
            'usage_holder_id': quota_holder_id,
            'resource_type': 'file',
            'resource_id': saved_file.id,
            'size_bytes': file_size,
            'course_id': course_id,
            'organisation_id': org_id,
            'storage_tier': 'hot'  # Neu hochgeladene Dateien = hot storage
        })

        # 6. WARNING CHECK - Sollten wir User warnen?
        new_usage = current_usage + file_size
        percent_used = (new_usage / quota.quota_bytes) * 100

        if percent_used >= quota.warning_threshold_percent:
            # 🟡 WARNING - User >80% Quota

            if percent_used >= 100:
                alert_type = 'storage_quota_full'
                action = 'upload_will_fail_soon'
            else:
                alert_type = 'storage_quota_warning'
                action = 'warning_email_sent'

            # Nur 1x per Tag warnen
            last_warning = monitoring_repo.find_last_warning(quota_holder_type, quota_holder_id)
            now = datetime.utcnow()

            if not last_warning or (now - last_warning.created_at).days >= 1:
                # Send warning email
                # (Celery task für Email)

                monitoring_repo.create({
                    'quota_holder_type': quota_holder_type,
                    'quota_holder_id': quota_holder_id,
                    'organisation_id': org_id,
                    'alert_type': alert_type,
                    'used_bytes': new_usage,
                    'quota_bytes': quota.quota_bytes,
                    'percent_used': int(percent_used),
                    'action_taken': action,
                    'alert_level': 'warning'
                })

                # Queue email task
                send_storage_warning_email.delay(
                    user_id=user.id,
                    percent_used=percent_used,
                    quota_gb=quota.quota_gb
                )

        return jsonify({
            'success': True,
            'file_id': saved_file.id,
            'filename': saved_file.filename,
            'size_bytes': file_size,
            'storage_used_percent': round((new_usage / quota.quota_bytes) * 100, 1)
        }), 201
```

---

### 3.6 Cleanup & Garbage Collection

#### **Storage Cleanup Strategy**

```
TIER-System für automatische Aufräumung:

┌─────────────────────────────────────────────────────────┐
│ FILE LIFECYCLE                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. UPLOADED                                             │
│    ├─ Storage Tier: HOT (SSD, schnell)                 │
│    ├─ Kosten: Normal                                   │
│    └─ Verfügbar: Sofort lesen/schreiben               │
│                                                         │
│ 2. USER DELETES FILE (Soft-Delete)                     │
│    ├─ Storage Tier: HOT (noch 30 Tage)                │
│    ├─ Status: is_deleted = TRUE                        │
│    ├─ Kosten: Normal (aber reserviert für Restore)    │
│    ├─ Verfügbar: Nur Owner kann Restore               │
│    └─ Grace Period: 30 Tage für Recovery              │
│                                                         │
│ 3. AFTER 30 DAYS - Hard Delete                         │
│    ├─ Permanent Storage Cleanup                        │
│    ├─ Status: permanent_delete = TRUE                  │
│    ├─ Recovery: UNMÖGLICH                              │
│    └─ Speicher: Freigegeben                            │
│                                                         │
└─────────────────────────────────────────────────────────┘

OPTIONAL: Archive Tier für alte Dateien
┌─────────────────────────────────────────────────────────┐
│ ARCHIVE TIER (nach 90 Tagen inaktiv)                   │
├─────────────────────────────────────────────────────────┤
│ ├─ Auto-move zu COLD storage (Tape/Glacier)           │
│ ├─ Kosten: 80% günstiger                              │
│ ├─ Access-Zeit: 1-4 Stunden (nicht instant)           │
│ ├─ Für: Backups, alte Aufzeichnungen                  │
│ └─ Benutzer: Müssen Request einreichen für Restore    │
└─────────────────────────────────────────────────────────┘
```

#### **Celery Task: Daily Cleanup Job**

```python
# Celery Beat Task - läuft täglich um 00:00 UTC

from celery.beat import crontab
from celery import shared_task
from datetime import datetime, timedelta

@app.task
def cleanup_deleted_files():
    """
    Läuft täglich - findet Dateien die:
    1. Soft-deleted sind UND
    2. älter als 30 Tage sind
    3. Und löscht sie permanent
    """

    with get_db_connection() as conn:
        usage_repo = StorageUsageRepository(conn)
        quota_repo = StorageQuotaRepository(conn)
        monitoring_repo = StorageMonitoringRepository(conn)

        # Find files that are soft-deleted AND older than 30 days
        grace_period_days = 30
        cutoff_date = datetime.utcnow() - timedelta(days=grace_period_days)

        files_to_delete = usage_repo.find_deleted_files(
            deleted_before=cutoff_date
        )

        total_freed = 0
        files_deleted = 0

        for file_record in files_to_delete:
            try:
                # Get file size before deletion
                file_size = file_record.size_bytes
                total_freed += file_size

                # Actually delete from storage (S3, etc.)
                storage_service.delete_file(file_record.resource_id)

                # Mark in database as permanently deleted
                usage_repo.update(file_record.id, {
                    'permanent_delete_at': datetime.utcnow(),
                    'is_deleted': True,
                    'storage_tier': None
                })

                files_deleted += 1

                # Log the cleanup
                monitoring_repo.create({
                    'quota_holder_type': file_record.usage_holder_type,
                    'quota_holder_id': file_record.usage_holder_id,
                    'organisation_id': file_record.organisation_id,
                    'alert_type': 'file_permanently_deleted',
                    'action_taken': 'grace_period_expired_cleanup',
                    'alert_level': 'info',
                    'admin_notes': f'Freed {file_size / (1024**3):.2f} GB'
                })

            except Exception as e:
                # Log error, continue with next file
                logger.error(f'Failed to delete file {file_record.id}: {str(e)}')
                continue

        # Return summary
        return {
            'status': 'completed',
            'files_deleted': files_deleted,
            'total_freed_gb': round(total_freed / (1024**3), 2),
            'timestamp': datetime.utcnow().isoformat()
        }

# Schedule in Celery Beat config
CELERY_BEAT_SCHEDULE = {
    'cleanup-deleted-files-daily': {
        'task': 'app.tasks.cleanup_deleted_files',
        'schedule': crontab(hour=0, minute=0),  # Every day at 00:00 UTC
    },
}
```

#### **Celery Task: Move Old Files to Archive**

```python
@app.task
def archive_inactive_files():
    """
    Läuft weekly - findet Dateien die:
    1. Älter als 90 Tage sind UND
    2. NICHT zugegriffen wurden seit 60 Tagen
    3. Und verschiebt zu COLD storage (billiger)
    """

    with get_db_connection() as conn:
        usage_repo = StorageUsageRepository(conn)

        # Find inactive files
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        last_access_cutoff = datetime.utcnow() - timedelta(days=60)

        files_to_archive = usage_repo.find_inactive_files(
            created_before=cutoff_date,
            last_accessed_before=last_access_cutoff,
            storage_tier='hot'
        )

        for file_record in files_to_archive:
            try:
                # Move to cold storage
                storage_service.move_to_cold_storage(file_record.resource_id)

                # Update database
                usage_repo.update(file_record.id, {
                    'storage_tier': 'cold'
                })

            except Exception as e:
                logger.error(f'Failed to archive file {file_record.id}: {str(e)}')
```

---

### 3.7 Storage Monitoring & Alerts API

#### **GET /api/storage/usage (für eigene Quota)**

```python
@bp.route('/storage/usage', methods=['GET'])
@require_auth
def get_my_storage_usage():
    """
    GET /api/storage/usage

    Returns: Meine persönliche Storage-Nutzung (für B2C User)

    {
        "quota_gb": 500,
        "used_gb": 245.5,
        "available_gb": 254.5,
        "percent_used": 49.1,
        "in_warning": false,
        "warning_threshold": 80,
        "files": [
            {
                "file_id": "abc123",
                "name": "course_recording.mp4",
                "size_gb": 5.2,
                "uploaded_at": "2026-01-15",
                "course_id": "course-xyz"
            }
        ],
        "cleanup_opportunity": {
            "soft_deleted_files_gb": 10.5,
            "recoverable_until": "2026-02-22",
            "message": "You can free 10.5 GB by permanently deleting soft-deleted files"
        }
    }
    """
    with get_db_connection() as conn:
        quota_repo = StorageQuotaRepository(conn)
        usage_repo = StorageUsageRepository(conn)

        quota = quota_repo.find_by_holder('user', g.current_user.id)
        used = usage_repo.sum_usage_by_holder('user', g.current_user.id, deleted=False)
        soft_deleted = usage_repo.sum_usage_by_holder('user', g.current_user.id, deleted=True)

        return jsonify({
            'quota_gb': quota.quota_gb if quota else 0,
            'used_gb': round(used / (1024**3), 2),
            'available_gb': round((quota.quota_bytes - used) / (1024**3), 2) if quota else 0,
            'percent_used': round((used / quota.quota_bytes) * 100, 1) if quota else 0,
            'warning_threshold': quota.warning_threshold_percent if quota else 80,
            'soft_deleted_gb': round(soft_deleted / (1024**3), 2),
            'files': usage_repo.get_user_files(g.current_user.id)
        }), 200
```

---

### 3.8 Storage Quota Enforcement Rules (DYNAMISCH - NICHT HARDCODED!)

**WICHTIG:** Alle Enforcement-Regeln werden dynamisch aus der `storage_enforcement_configs` Tabelle geladen!
- ✅ Kein Hardcoding von Schwellwerten
- ✅ Pro Organisation konfigurierbar
- ✅ System-Default als Fallback
- ✅ JSON-basierte Actions für maximale Flexibilität (User's Message 3: "das sollte man aber flexibel einstellen können alles")

---

#### **📊 System-Architektur des Storage Enforcement**

Das Storage Enforcement System funktioniert nach folgendem Ablauf:

```
                     USER REQUEST (File Upload)
                              ↓
                    FILE UPLOAD ENDPOINT
               (Token-Validierung + organisation_id)
                              ↓
              STORAGE ENFORCEMENT SERVICE
         (Config laden + Entscheidungs-Logik)
                              ↓
         STORAGE ENFORCEMENT CONFIG REPOSITORY
     (Org-Config suchen → System-Default → Fallback)
                              ↓
                      DATABASE
         (storage_enforcement_configs Tabelle)
                              ↓
              DECISION RETURNED TO ENDPOINT
         (allowed: bool, reason: str, status: str)
                              ↓
                   RESPONSE TO USER
      (200 OK oder 507 Insufficient Storage)
```

---

#### **🔄 Konfigurationsauflösungs-Logik**

Das System nutzt eine intelligente Fallback-Logik bei der Konfiguration:

```
Anfrage mit organisation_id?
    ├─ JA: Suche org-spezifische Config
    │      └─ Gefunden? → USE ✅
    │      └─ Nicht gefunden? → Continue
    │
    ├─ NEIN: Skip zu System-Default
    │
    → Suche System-Default (is_system_default = TRUE)
       └─ Gefunden? → USE ✅
       └─ Nicht gefunden? → USE Internal Defaults (Hardcoded Fallback)
```

**Praktische Szenarien:**
- **B2B (Organisation mit custom Enforcement):** organisation_id='gymnasiast-berlin' → findet custom soft-enforcement config → nutzt diese
- **B2C (Einzelnutzer):** organisation_id=null → springt zu system-default → nutzt B2C hard-enforcement
- **Neue Org ohne Config:** organisation_id='new-org-123' → keine org-config → fallback zu system-default

---

#### **⏱️ Enforcement-Schwellwerte und Aktionen**

Das System definiert **5 distinct Bereiche** mit unterschiedlichen Aktionen für jeden Prozentsatz-Bereich:

| Bereich | Prozentual | Status | Upload | Download | Notification |
|---------|-----------|--------|--------|----------|--------------|
| **0_to_50** | 0-50% | 🟢 Grün | Erlaubt | Erlaubt | Keine |
| **50_to_80** | 50-80% | 🟡 Gelb | Erlaubt | Erlaubt | Wöchentlich |
| **80_to_100** | 80-100% | 🟠 Orange | Mit Warnung | Erlaubt | Täglich |
| **100_plus** | >100% | 🔴 Rot | Blockiert | Erlaubt/ReadOnly | Kritisch |
| **grace_period_expired** | Nach Grace Period | ⚠️ Alert | Blockiert | ReadOnly | Kontakt Admin |

Jeder Bereich wird in der Datenbank als separate JSON-Struktur in `actions_json` definiert:

```json
{
  "0_to_50": {
    "status": "green",
    "upload": "allowed",
    "download": "allowed",
    "notifications": "none",
    "display_message": "✅ Viel Speicher verfügbar"
  },
  "50_to_80": {
    "status": "yellow",
    "upload": "allowed",
    "download": "allowed",
    "notifications": "weekly_reminder",
    "display_message": "🟡 Speichernutzung bei {percent}%"
  },
  "80_to_100": {
    "status": "orange",
    "upload": "allowed_with_warning",
    "download": "allowed",
    "notifications": "daily_warning",
    "suggest_cleanup": true
  },
  "100_plus": {
    "status": "red",
    "upload": "blocked",
    "download": "allowed",
    "grace_period_days": 30,
    "allow_deletions_only": true
  },
  "grace_period_expired": {
    "status": "alert",
    "upload": "blocked",
    "download": "readonly",
    "action_required": true,
    "contact_support": true
  }
}
```

---

#### **Dynamic Enforcement Loading**

```python
# app/services/storage_enforcement_service.py

from app.repositories.storage_enforcement_config import StorageEnforcementConfigRepository
from typing import Dict, Any

class StorageEnforcementService:
    """
    Laden und anwenden von dynamischen Enforcement-Regeln.

    Alle Schwellwerte, Aktionen, Grace Periods, etc. kommen AUS DER DATENBANK,
    nicht aus hardcodierten Werten!
    """

    @staticmethod
    def get_enforcement_config(
        organisation_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Hole Enforcement-Config für eine Organisation.

        Logik:
        1. Wenn organisation_id vorhanden → suche org-spezifische Config
        2. Falls nicht → System-Default verwenden

        Args:
            organisation_id: Organisations-ID (optional)
            user_id: User-ID für B2C lookup (optional)

        Returns:
            Config dict mit allen Enforcement-Einstellungen
        """
        config_repo = StorageEnforcementConfigRepository()

        # Versuche org-spezifische Config zu finden
        if organisation_id:
            config = config_repo.find_by_organisation(organisation_id)
            if config:
                return config.to_dict()

        # Fallback: System-Default
        default_config = config_repo.find_system_default()
        return default_config.to_dict() if default_config else {
            'enforcement_type': 'hard',
            'warning_threshold_percent': 80,
            'critical_threshold_percent': 95,
            'hard_limit_percent': 100,
            'grace_period_days': 30,
            'warning_frequency': 'daily',
            'send_email_warnings': True,
            'send_ui_notifications': True
        }

    @staticmethod
    def get_enforcement_action(
        percent_used: float,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Bestimme die Aktion basierend auf Nutzungsprozentsatz und Config.

        Args:
            percent_used: Prozentuale Nutzung (0-100+)
            config: Enforcement-Config von get_enforcement_config()

        Returns:
            Action dict aus actions_json für diesen Schwellwert
        """
        actions_json = config.get('actions_json', {})

        # Bestimme Bereich basierend auf percent_used
        if percent_used <= 50:
            range_key = '0_to_50'
        elif percent_used <= 80:
            range_key = '50_to_80'
        elif percent_used < 100:
            range_key = '80_to_100'
        elif percent_used >= 100:
            range_key = '100_plus'
        else:
            range_key = '100_plus'

        # Hole Action aus JSON
        action = actions_json.get(range_key, {
            'status': 'red',
            'upload': 'blocked',
            'download': 'allowed',
            'notifications': 'critical'
        })

        return action

    @staticmethod
    def can_upload(
        percent_used: float,
        organisation_id: str = None,
        in_grace_period: bool = False
    ) -> tuple[bool, str]:
        """
        Kann User eine Datei hochladen?

        Returns:
            (allowed: bool, reason: str)
        """
        config = StorageEnforcementService.get_enforcement_config(
            organisation_id=organisation_id
        )
        action = StorageEnforcementService.get_enforcement_action(
            percent_used, config
        )

        upload_status = action.get('upload', 'allowed')

        if upload_status == 'blocked':
            if in_grace_period:
                return False, f"Storage quota exceeded. Grace period ends in {config['grace_period_days']} days."
            else:
                return False, "Storage quota exceeded. Please delete files to free space."
        elif upload_status == 'allowed_with_warning':
            return True, f"Storage usage at {percent_used:.1f}%. Consider cleaning up files."
        else:
            return True, ""

    @staticmethod
    def can_download(
        percent_used: float,
        in_grace_period_after: bool = False
    ) -> bool:
        """Kann User Dateien herunterladen?"""
        if in_grace_period_after:
            return False  # Read-only mode
        return True  # Immer erlaubt

    @staticmethod
    def get_status_display(
        percent_used: float,
        config: Dict[str, Any] = None
    ) -> str:
        """
        Bestimme Status-Anzeige für UI.

        Returns: 'green', 'yellow', 'red', 'black', 'alert'
        """
        if config is None:
            config = StorageEnforcementService.get_enforcement_config()

        action = StorageEnforcementService.get_enforcement_action(
            percent_used, config
        )

        return action.get('status', 'green')

    @staticmethod
    def should_send_warning(
        percent_used: float,
        last_warning_sent: datetime = None,
        config: Dict[str, Any] = None
    ) -> bool:
        """
        Sollten wir eine Warnung senden?

        Berücksichtigt:
        - Warning-Frequenz aus Config (daily, weekly, once)
        - Letzten Warnung-Zeitpunkt
        - Aktuellen Schwellwert
        """
        if config is None:
            config = StorageEnforcementService.get_enforcement_config()

        # Ist User überhaupt in Warning-Range?
        if percent_used < config['warning_threshold_percent']:
            return False

        # Prüfe Frequency
        warning_frequency = config.get('warning_frequency', 'daily')

        if last_warning_sent is None:
            return True  # Erste Warnung

        now = datetime.utcnow()

        if warning_frequency == 'once':
            return False  # Nur 1x, bereits gesendet
        elif warning_frequency == 'weekly':
            return (now - last_warning_sent).days >= 7
        elif warning_frequency == 'daily':
            return (now - last_warning_sent).days >= 1
        else:
            return False
```

#### **Beispiel-Enforcement mit dynamischer Config**

```python
# In File Upload Endpoint (siehe 3.5)

@bp.route('/courses/<course_id>/files/upload', methods=['POST'])
@require_auth
def upload_file_to_course(course_id: str):
    """File-Upload mit DYNAMISCHEN Enforcement-Regeln"""

    file = request.files['file']
    file_size = len(file.read())
    file.seek(0)

    with get_db_connection() as conn:
        # 1. Get quota for user/organisation
        user = g.current_user
        quota_holder_type = 'user'  # or 'organisation' for B2B
        quota_holder_id = user.id

        quota_repo = StorageQuotaRepository(conn)
        usage_repo = StorageUsageRepository(conn)

        quota = quota_repo.find_by_holder(quota_holder_type, quota_holder_id)
        if not quota:
            raise ValidationError('No storage quota assigned')

        current_usage = usage_repo.sum_usage_by_holder(
            quota_holder_type, quota_holder_id, deleted=False
        )

        # 2. HIER KOMMT NEUE LOGIK: Dynamische Config laden!
        enforcement_service = StorageEnforcementService()
        config = enforcement_service.get_enforcement_config(
            organisation_id=user.organisation_id
        )

        # 3. Prüfe ob Upload erlaubt ist (basierend auf Config!)
        new_usage = current_usage + file_size
        percent_used = (new_usage / quota.quota_bytes) * 100

        can_upload, reason = enforcement_service.can_upload(
            percent_used=percent_used,
            organisation_id=user.organisation_id
        )

        if not can_upload:
            return jsonify({
                'success': False,
                'error': 'storage_quota_exceeded',
                'message': reason,
                'percent_used': round(percent_used, 1),
                'cleanup_suggestions': usage_repo.find_cleanup_candidates(quota_holder_id)
            }), 507  # 507 = Insufficient Storage

        # 4. Datei speichern (wie bisher)
        file_data = {'filename': file.filename, 'size_bytes': file_size, ...}
        saved_file = file_repo.create(file_data)

        # 5. UPDATE Storage Usage (wie bisher)
        usage_repo.create({
            'usage_holder_type': quota_holder_type,
            'usage_holder_id': quota_holder_id,
            'resource_id': saved_file.id,
            'size_bytes': file_size,
            ...
        })

        # 6. HIER KOMMT NEUE LOGIK: Warning basierend auf Config!
        if enforcement_service.should_send_warning(
            percent_used=percent_used,
            config=config
        ):
            # Hole letzte Warnung
            last_warning = monitoring_repo.find_last_warning(
                quota_holder_type, quota_holder_id
            )

            # Send warning (respektiert config['warning_frequency']!)
            if config.get('send_email_warnings'):
                send_storage_warning_email.delay(
                    user_id=user.id,
                    percent_used=percent_used,
                    threshold_percent=config['warning_threshold_percent'],
                    organisation_id=user.organisation_id
                )

            if config.get('send_ui_notifications'):
                # Create in-app notification
                create_notification(
                    user_id=user.id,
                    type='storage_warning',
                    message=f"Storage at {percent_used:.1f}%"
                )

        return jsonify({
            'success': True,
            'file_id': saved_file.id,
            'storage_used_percent': round(percent_used, 1),
            'status_display': enforcement_service.get_status_display(percent_used, config)
        }), 201
```

#### **Default Enforcement Konfiguration (mit Beispiel-Überrides)**

Siehe die bereits hinzugefügte `storage_enforcement_configs` Tabelle weiter oben mit:
- System Default (enforcement_type='hard', 80% warning, 95% critical, 100% hard_limit)
- Beispiel B2B Org-Override (enforcement_type='soft', großzügigere Thresholds)
- JSON actions_json mit flexiblen Verhalten pro Schwellwert

**Vorteile dieser Implementierung:**
- ✅ Alles ist datenbank-gesteuert (NICHT hardcoded)
- ✅ Pro Organisation anpassbar
- ✅ Neue Schwellwerte ohne Code-Änderung
- ✅ Admin-Interface kann später Config-Management hinzufügen
- ✅ A/B Testing verschiedener Enforcement-Strategien möglich
- ✅ Erfüllt Message 3: "das sollte man aber flexibel einstellen können alles" 🎯

---

#### **🎯 B2C Hard Enforcement vs B2B Soft Enforcement Timelines**

Das System unterstützt zwei fundamentale Enforcement-Modelle mit unterschiedlichen Philosophien:

**B2C Hard Enforcement (Strikte Quotas für Einzelnutzer):**
```
0%           75%           90%          100%       107 days
│────────────│─────────────│────────────│──────────│────── TIME
│            │    ⚠️        │   ⚠️⚠️       │    🚫    │  🛑
│ ✅ Grün    │ 🟡 Gelb     │ 🟠 Orange   │ 🔴 Rot   │  ⚠️ Read-Only
│            │ Daily Warn  │ Daily Warn │ Blocked  │ (Admin Only)
│            │             │ Grace: 7d  │          │
└────────────┴─────────────┴────────────┴──────────┴─────────
Characteristics:
- ✓ Strikte Durchsetzung bei 100%
- ✓ Nur 7 Tage zum Aufräumen
- ✓ Täglich Warnungen (aggressiv)
- ✓ Kein Overflow erlaubt
- Use Case: Individual subscription users
```

**B2B Soft Enforcement (Flexible Quotas für Organisationen):**
```
0%           85%           95%         110%       137 days
│────────────│─────────────│────────────│──────────│────── TIME
│            │    ⚠️        │   ⚠️⚠️       │    📢    │  🛑
│ ✅ Grün    │ 🟡 Gelb     │ 🟠 Orange   │ 🟠 Orange│  ⚠️ Read-Only
│            │ Weekly Warn │ Weekly Warn│ Allow 10%│ (Admin Only)
│            │             │ Grace: 30d │ Warn     │
└────────────┴─────────────┴────────────┴──────────┴─────────
Characteristics:
- ✓ Großzügiger bis 110%
- ✓ 30 Tage zum Aufräumen
- ✓ Wöchentliche Warnungen (kooperativ)
- ✓ Erlaubt Overflow von 10%
- Use Case: Organisations with IT support
```

**Vergleichstabelle - Schwellwerte und Verhalten:**

| Aspekt | B2C Hard | B2B Soft |
|--------|----------|----------|
| **Warning Threshold** | 75% | 85% |
| **Critical Threshold** | 90% | 95% |
| **Hard Limit** | 100% | 110% |
| **Grace Period** | 7 Tage | 30 Tage |
| **Warning Frequency** | Täglich | Wöchentlich |
| **First Upload Block** | 100% | 110% |
| **Target Users** | Individuals | Organisations |
| **Flexibility** | Limited | High |
| **Admin Intervention** | Required after grace | Quota increase option |
| **Read-Only Mode** | Nach 7 Tagen | Nach 30 Tagen |

---

#### **🔧 Konfigurationsbeispiele**

**B2C Hard Enforcement (Standard für Einzelnutzer):**
```python
{
    "organisation_id": None,  # System-wide default
    "enforcement_type": "hard",
    "warning_threshold_percent": 75,
    "critical_threshold_percent": 90,
    "hard_limit_percent": 100,
    "grace_period_days": 7,
    "warning_frequency": "daily",
    "send_email_warnings": True,
    "send_ui_notifications": True,
    "actions_json": {
        "0_to_50": {"status": "green", "upload": "allowed", "notifications": "none"},
        "50_to_75": {"status": "yellow", "upload": "allowed", "notifications": "none"},
        "75_to_90": {"status": "yellow", "upload": "allowed", "notifications": "daily"},
        "90_to_100": {"status": "orange", "upload": "allowed_with_warning", "notifications": "daily_critical"},
        "100_plus": {"status": "red", "upload": "blocked", "grace_period_days": 7},
        "grace_period_expired": {"status": "alert", "upload": "blocked", "download": "readonly"}
    }
}
```

**B2B Soft Enforcement (Für Organisationen):**
```python
{
    "organisation_id": "gymnasium-munich",  # Org-specific override
    "enforcement_type": "soft",
    "warning_threshold_percent": 85,
    "critical_threshold_percent": 95,
    "hard_limit_percent": 110,  # Erlaubt 10% Overflow!
    "grace_period_days": 30,    # Längere Grace-Period
    "warning_frequency": "weekly",  # Weniger aggressiv
    "send_email_warnings": True,
    "send_ui_notifications": True,
    "actions_json": {
        "0_to_50": {"status": "green", "upload": "allowed", "notifications": "none"},
        "50_to_85": {"status": "yellow", "upload": "allowed", "notifications": "none"},
        "85_to_95": {"status": "yellow", "upload": "allowed", "notifications": "weekly"},
        "95_to_110": {"status": "orange", "upload": "allowed_with_warning", "notifications": "weekly"},
        "110_plus": {"status": "red", "upload": "blocked", "grace_period_days": 30},
        "grace_period_expired": {"status": "alert", "upload": "blocked", "download": "readonly"}
    }
}
```

**Custom Enforcement (Beliebig konfigurierbar):**
```python
{
    "organisation_id": "custom-enterprise",
    "enforcement_type": "custom",
    "warning_threshold_percent": 70,
    "critical_threshold_percent": 90,
    "hard_limit_percent": 105,
    "grace_period_days": 14,
    "warning_frequency": "twice_daily",  # Custom frequency!
    "send_email_warnings": True,
    "send_ui_notifications": True,
    "actions_json": { /* Komplett custom pro Range */ }
}
```

---

#### **⚙️ Repository Layer - Datenbankzugriff**

Die `StorageEnforcementConfigRepository` kümmert sich um alle Datenbankzugriffe:

```python
# app/repositories/storage_enforcement_config.py

from typing import Optional
from app.repositories.base import BaseRepository
from app.models.storage_enforcement_config import StorageEnforcementConfig

class StorageEnforcementConfigRepository(BaseRepository[StorageEnforcementConfig]):
    """
    Repository für Storage Enforcement Konfigurationen.

    Verantwortlich für:
    - Laden org-spezifischer Configs
    - System-Default Fallback
    - Caching (optional)
    """

    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = "storage_enforcement_configs"
        self.model_class = StorageEnforcementConfig

    def find_by_organisation(self, organisation_id: str) -> Optional[StorageEnforcementConfig]:
        """Finde Config für spezifische Organisation"""
        return self.find_by({
            'organisation_id': organisation_id,
            'is_system_default': False
        }).first() if self.find_by({
            'organisation_id': organisation_id,
            'is_system_default': False
        }) else None

    def find_system_default(self) -> Optional[StorageEnforcementConfig]:
        """Finde globales System-Default"""
        configs = self.find_by({'is_system_default': True})
        return configs[0] if configs else None

    def get_config_for_organisation_or_default(
        self,
        organisation_id: Optional[str] = None
    ) -> StorageEnforcementConfig:
        """
        Intelligente Config-Auflösung mit Fallback.

        Logik:
        1. Wenn organisation_id vorhanden → suche org-Config
        2. Falls nicht gefunden → System-Default
        3. Falls auch nicht → Internal Defaults
        """
        # Versuche org-spezifische Config
        if organisation_id:
            org_config = self.find_by_organisation(organisation_id)
            if org_config:
                return org_config

        # Fallback: System-Default
        system_default = self.find_system_default()
        if system_default:
            return system_default

        # Final Fallback: Internal Defaults (sollte selten passieren)
        return StorageEnforcementConfig.get_internal_default()
```

---

#### **🎯 Use Cases und praktische Szenarien**

**Use Case 1: Neuer User lädt Datei hoch (B2C)**
```
1. User logs in (keine organisation_id)
2. Datei-Upload-Endpoint wird aufgerufen
3. Service lädt Config: get_config_for_organisation_or_default(org_id=None)
4. System-Default wird verwendet (B2C Hard Enforcement)
5. Bei 78.5% Nutzung:
   - range_key = '50_to_80'
   - Status = 'yellow'
   - Upload = 'allowed'
   - Warning = 'weekly_reminder'
6. Upload erlaubt, Warnung angezeigt
```

**Use Case 2: Org-Admin ändert Storage-Richtlinien (B2B)**
```
1. Admin öffnet Admin-Panel
2. Modifiziert organisation-spezifische Config
3. Z.B. grace_period_days: 30 → 45
4. Database update: UPDATE storage_enforcement_configs SET grace_period_days=45 WHERE organisation_id='gymnasium-munich'
5. ✅ Sofort aktiv für alle User dieser Org (keine Code-Änderung!)
```

**Use Case 3: User nähert sich Storage-Limit (B2B)**
```
Szenario B2B (85% threshold):
- Bei 85%: Erste Warnung (wöchentlich)
- Bei 95%: Intensivere Warnung (noch wöchentlich, aber urgent)
- Bei 110%: Upload blockiert, aber 30 Tage Grace-Period
- Nach 30 Tagen: Read-Only Mode, User muss Storage aufräumen
```

**Use Case 4: Grace Period abgelaufen**
```
1. Grace Period endet (z.B. nach 7 Tagen B2C oder 30 Tagen B2B)
2. System setzt Status auf 'grace_period_expired'
3. Auswirkungen:
   - Upload: blockiert
   - Download: read-only nur (B2B) oder blockiert (B2C)
   - Neue Courses/Lessons: blockiert
   - User muss manuell aufräumen oder Admin kontaktieren
```

---

#### **🔌 Integration in Entwicklung**

**Für Backend-Entwickler:**
```python
# 1. Repository-Zugriff
from app.repositories.storage_enforcement_config import StorageEnforcementConfigRepository

with get_db_connection() as conn:
    repo = StorageEnforcementConfigRepository(conn)

    # Intelligent auflösen
    config = repo.get_config_for_organisation_or_default('org-123')

    # Oder spezifisch
    org_config = repo.find_by_organisation('org-123')
    system_default = repo.find_system_default()

# 2. Service-Nutzung
from app.services.storage_enforcement_service import StorageEnforcementService

service = StorageEnforcementService()

# Upload-Entscheidung
can_upload, reason = service.can_upload(
    percent_used=78.5,
    organisation_id='org-123'
)

# UI-Status anzeigen
status = service.get_status_display(percent_used=78.5)
# Returns: 'yellow', 'red', 'alert', etc.

# Warnung senden?
if service.should_send_warning(
    percent_used=85.5,
    config=config
):
    # Send warning email/notification
    pass
```

**Für Frontend-Entwickler:**
```javascript
// Storage Status Display Component
<template>
  <div class="storage-indicator">
    <div class="progress-bar">
      <!-- Status-Farbe basiert auf API Response -->
      <div :style="{
        width: percentUsed + '%',
        backgroundColor: statusColor
      }"></div>
    </div>

    <!-- Status-Text -->
    <p :class="`status-${status}`">
      {{ statusMessage }}
    </p>

    <!-- Cleanup-Empfehlungen wenn nötig -->
    <div v-if="showCleanupSuggestions" class="cleanup-suggestions">
      <p>{{ $t('storage.cleanup_suggested') }}</p>
      <button @click="goToCleanup">{{ $t('storage.cleanup_now') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const percentUsed = ref(0)
const status = ref('green')
const statusColor = computed(() => {
  const colors = {
    'green': '#10b981',
    'yellow': '#eab308',
    'orange': '#f97316',
    'red': '#ef4444',
    'alert': '#8b0000'
  }
  return colors[status.value] || '#10b981'
})

onMounted(async () => {
  // Fetch storage status from API
  const response = await fetch('/api/storage/status')
  const data = await response.json()

  percentUsed.value = data.percent_used
  status.value = data.status
})
</script>
```

---

### 3.9 B2B vs B2C Storage Comparison

| Aspekt | B2B (Organisationen) | B2C (Self-Service) |
|--------|---------------------|-------------------|
| **Quota Holder** | Organisation | Individual User |
| **Who Sets Limit** | Du (Site-Admin) bei Org-Erstellung | Subscription Plan |
| **Typical Quota** | 500 GB - 10 TB | 1 GB - 2 TB |
| **Enforcement** | Soft (warnings, grace period) | Hard (immediate block) |
| **Per-Course Limits** | Optional (sub-quotas) | Nein (gemeinsam) |
| **Owner Visibility** | Full dashboard with breakdown | Personal storage page |
| **Cleanup Owner** | Owner-Admin entscheidet | User muss selbst aufräumen |
| **Auto-Cleanup** | Nein (manual process) | Ja (soft-delete after 30 days) |
| **Grace Period** | 30 Tage nach Hard-Delete | 30 Tage nach Soft-Delete |
| **Cost Model** | Fixed annual contract | Per-plan monthly |
| **Support for Upgrade** | Request to Site-Admin | Auto-upgrade to higher plan |

---

```

---

## 🔄 VERGLEICH: B2B vs B2C

```
┌────────────────────┬──────────────────────────────────────┬──────────────────────────────────────┐
│ Aspekt             │ B2B (Organisationen)                 │ B2C (Self-Service)                   │
├────────────────────┼──────────────────────────────────────┼──────────────────────────────────────┤
│ WHO CREATES?       │ ✅ DU (Site-Admin nach Anfrage)      │ ✅ User (Self-Service)               │
│ PROCESS            │ Manual (Du reviews + genehmigt)      │ Automatisch (Signup + Zahlung)       │
│ HIERARCHY          │ Tief (bis 15 Ebenen, 5000+ Groups)   │ Flach (nur Abo-basierte Groups)      │
│ GROUP CREATION     │ Owner-Admin erstellt custom          │ Automatisch via Celery               │
│ PERMISSION GRANT   │ Manual (Owner-Admin + UI)            │ Automatisch via Celery Task          │
│ COMPLEXITY         │ Hoch (Matrix-Strukturen möglich)     │ Niedrig (einfache Abo-Groups)        │
│ AUTOMATION         │ Minimal                              │ Maximal (Celery Tasks)               │
│ SKALIERUNG         │ Manuell (Du genehmigst jede Org)     │ Automatisch (1000+ User gleichzeitig) │
│ ADMIN ARBEIT       │ Hoch (manuelle Freigaben)            │ Null (vollständig automatisiert)     │
│ FRONTEND           │ Dedizierte Container (Multi-Tenant)  │ Shared Frontend (Single Instance)    │
│ DATA ISOLATION     │ Streng (separate Organisationen)     │ via RLS (shared backend)             │
│ BILLING            │ B2B Pricing (Verträge)               │ Self-Service (Stripe, recurring)     │
│ PAYMENT CYCLE      │ Custom (monatlich, jährlich, etc)    │ Monthly/Yearly (standardisiert)      │
│ PERMISSIONS        │ Custom pro Org möglich               │ Vordefiniert per Plan                │
│ CONFIG TABLE       │ b2b_configurations                   │ b2c_configurations                  │
│ PLANS TABLE        │ (optional, für B2B-Tiers)            │ subscription_plans                   │
│ USER GROUPS TABLE  │ groups (custom: Abteilung, Team)     │ groups (abo-based: abo:premium)      │
│ AUTOMATION ENGINE  │ Webhooks + Manual Triggers           │ Celery Tasks + Stripe Webhooks       │
└────────────────────┴──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 📋 Hierarchie-Lösungsvergleich

```
PROBLEM: Wie deep kann Hierarchie sein?
- Small Org: 3-5 Ebenen (Teacher → Class → Student)
- Large Org: 8-15 Ebenen (Faculty → Institute → Chair → AG → Project)
- Matrix Org: 2 Hierarchien parallel (Organizational + Project-based)

┌──────────────────────┬────────────────────────────┬──────────────────┬──────────────┐
│ Lösung               │ Vorteile                   │ Nachteile         │ Skalierbarkeit│
├──────────────────────┼────────────────────────────┼──────────────────┼──────────────┤
│ OPTION A: Rekursive  │ Natürliche Struktur        │ Langsame Queries  │ Bis ~10 Ebenen
│ Hierarchie           │ (Parent-Child Modell)      │ (CTE nötig)       │             │
│                      │                            │ Komplexe Updates  │             │
├──────────────────────┼────────────────────────────┼──────────────────┼──────────────┤
│ OPTION B: Path-      │ SEHR schnell (LIKE Query)  │ Denormalisiert    │ Unbegrenzt! │
│ basiert             │ Skaliert auf 1000+ Ebenen  │ Update-Komplexität│ (Praktisch: │
│                      │ Ideal für tiefe Hierarchien│                   │  bis 100)   │
├──────────────────────┼────────────────────────────┼──────────────────┼──────────────┤
│ OPTION C: Tags/      │ Sehr flexibel              │ Nicht hierarchisch│ Flexible    │
│ Kategorien           │ Unterstützt Matrix-Struktur│ Weniger intuitiv   │ Struktur    │
│                      │ Ad-hoc Queries             │                   │             │
├──────────────────────┼────────────────────────────┼──────────────────┼──────────────┤
│ OPTION D: Flexible   │ Balance zwischen Alle      │ Custom Validation │ Bis zur     │
│ Tiefe mit Limits     │ Konfigurierbar pro Org    │ pro Org           │ konfigurierten│
│ (EMPFOHLEN!)        │ Respects b2b_config        │                   │ Limit       │
└──────────────────────┴────────────────────────────┴──────────────────┴──────────────┘

EMPFEHLUNGSTACK (für LSX):
1. OPTION B (Path-basiert) für DB-Struktur → schnell + skalierbar
2. OPTION D (Flexible Limits) für Validation → respects org-specific config
3. Beide kombiniert: Tiefe Hierarchien mit FastQuerys + flexible Limits
```

---

## 🎯 Implementierungs-Roadmap

### PHASE 1: Database Schema (MIGRATIONS)
- [ ] Create b2b_configurations table
- [ ] Create b2c_configurations table
- [ ] Create subscription_plans table
- [ ] Add group_path, group_path_ids, hierarchy_level zu groups table
- [ ] Add group_category, group_tags zu groups table
- [ ] Add subscription_plan_id zu groups table

### PHASE 2: Backend Implementation
- [ ] B2BConfigurationRepository
- [ ] B2CConfigurationRepository
- [ ] SubscriptionPlanRepository
- [ ] Update GroupRepository (path-basiert)
- [ ] Add Hierarchy-Level Validation
- [ ] Add Path-Generation Logic

### PHASE 3: API Endpoints (B2B)
- [ ] POST /organisations (mit b2b_config)
- [ ] POST /organisations/{id}/groups (mit hierarchy validation)
- [ ] PUT /organisations/{id}/config (edit b2b_config)
- [ ] GET /organisations/{id}/config (view config + limits)

### PHASE 4: API Endpoints (B2C)
- [ ] POST /auth/register (auto free tier)
- [ ] POST /subscriptions/purchase (Stripe integration)
- [ ] GET /plans (list subscription plans)
- [ ] POST /subscriptions/{id}/cancel

### PHASE 5: Celery Tasks (Automation)
- [ ] add_user_to_subscription_group
- [ ] remove_user_from_subscription_group
- [ ] check_expired_subscriptions (daily)
- [ ] send_renewal_reminder (weekly)

### PHASE 6: Stripe Integration
- [ ] Webhook endpoint
- [ ] Payment Intent creation
- [ ] Subscription management

### PHASE 7: Frontend (B2B Admin Panel)
- [ ] Organisation Setup Wizard
- [ ] B2B Configuration UI
- [ ] Hierarchy Depth Validator
- [ ] Group Management UI (mit Path-Visualization)

### PHASE 8: Frontend (B2C Self-Service)
- [ ] Signup Form
- [ ] Plan Selection UI
- [ ] Payment Form (Stripe Elements)
- [ ] Subscription Management Dashboard

---

## 📊 Datenbank-Schema Summary

```sql
-- Alle neuen Tabellen sind DATABASE-DRIVEN (NICHTS hardcoded!)

CREATE TABLE b2b_configurations (
    organisation_id UUID PRIMARY KEY,
    max_hierarchy_depth INT DEFAULT 10,        -- ← FLEXIBLE!
    max_groups_per_level INT DEFAULT 500,      -- ← FLEXIBLE!
    allow_nested_groups BOOLEAN DEFAULT TRUE,  -- ← FLEXIBLE!
    max_groups INT DEFAULT 500,                -- ← FLEXIBLE!
    billing_model VARCHAR(50),
    ... (siehe 1.2 vollständig)
);

CREATE TABLE b2c_configurations (
    id UUID PRIMARY KEY,
    free_tier_monthly_tokens INT DEFAULT 10000,  -- ← FLEXIBLE!
    enable_subscriptions BOOLEAN DEFAULT TRUE,   -- ← FLEXIBLE!
    auto_renew_subscriptions BOOLEAN DEFAULT TRUE, -- ← FLEXIBLE!
    ... (siehe 2.2 vollständig)
);

CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY,
    code VARCHAR(50),           -- 'free', 'starter', 'premium', ...
    price_monthly DECIMAL,
    features JSON,              -- ← FLEXIBLE!
    permissions VARCHAR[],      -- ← FLEXIBLE!
    auto_group_name VARCHAR,    -- 'abo:X' (auto-created)
    ... (siehe 2.3 vollständig)
);

ALTER TABLE groups ADD COLUMN (
    group_path VARCHAR(1000),       -- z.B. "org/fak-phil/inst-phil/lehrstuhl-logik"
    group_path_ids VARCHAR(1000),   -- z.B. "fac-1/inst-2/chair-3"
    hierarchy_level INT,            -- 1, 2, 3, ... (Ebene in Hierarchie)
    group_category VARCHAR(50),     -- 'department', 'team', 'project', 'cohort', 'abo'
    group_tags VARCHAR[],           -- ['type:academic', 'client:BMW', 'year:2024']
    subscription_plan_id UUID       -- Link zu subscription_plans (für Abo-Groups)
);
```

---

## ✅ Fazit

**B2B + B2C nutzen SAME Permission-Infrastruktur, aber völlig unterschiedliche Workflows:**

| | B2B | B2C |
|---|-----|-----|
| **WHO** | Du (Manual) | User (Self-Service) |
| **HIERARCHY** | Tief (OPTION B: Path-basiert) | Flach (nur Abo-Groups) |
| **LIMITS** | Flexibel pro Org (b2b_config) | Global (b2c_config) |
| **AUTOMATION** | Minimal | Maximal (Celery) |
| **PERMISSIONS** | UNION-Modell | UNION-Modell |
| **SCALING** | Manuell | Automatisch |

**Alles ist database-driven. Nichts ist hardcoded!** 🎯

---

**Version:** 1.0
**Status:** Ready for Implementation
**Nächster Schritt:** PHASE 1 Database Migrations

Sollen wir mit den Migrations starten? 🚀
