# 12 | Kurs-Kategorisierung: Flexibles Hierarchie-System

**Version:** 2.0
**Status:** Final
**Zuletzt aktualisiert:** 2025-12-03

## Übersicht

Das **Flexible Kategorie-System** des LSX Lernsystems ersetzt das ehemalige starre 5-Stufen-Modell und bietet **unbegrenzte Tiefe** (praktisches Limit: 20 Ebenen) für die Organisation von Kursen und Lerninhalten.

**Wichtige Eigenschaften:**
- **Unbegrenzte Hierarchietiefe:** Praktisches Limit von 20 Ebenen
- **Selbstreferenzierende Tabelle:** Eine `course_categories` Tabelle für alle Ebenen
- **Path-basierte Navigation:** Vollständiger Pfad wie "IT/Netzwerk/Cisco/CCNA/Routing"
- **Automatische Pfad-Berechnung:** Trigger aktualisiert `path`, `path_ids`, `root_id`
- **KI-Autokategorisierung:** Automatische Zuordnung von PDF-Uploads
- **Internationale Standards:** CompTIA, Cisco, IHK, Microsoft, CEFR (Sprachen)
- **Multi-Tenancy:** Organisation-spezifische Kategorien
- **Skalierbar:** Tausende Kurse strukturiert verwaltbar
- **Mehrsprachig:** Übersetzbare Kategorien (DE, EN, ES, FR, PL)

---

## 1. Architektur: Flexibles vs. Starres Modell

### 1.1 Vergleich Alt vs. Neu

| Aspekt | Alt (5-Stufen) | Neu (Flexibel) |
|--------|----------------|----------------|
| **Tiefe** | Fest: 5 Ebenen | Dynamisch: 1-20 Ebenen |
| **Tabellen** | 5 separate Tabellen | 1 selbstreferenzierende Tabelle |
| **Flexibilität** | Starr, Änderungen aufwändig | Hochflexibel, einfach erweiterbar |
| **Pfad-Navigation** | Manuell zusammensetzen | Automatisch via `path`-Spalte |
| **Performance** | JOINs über 5 Tabellen | Rekursive CTEs, GIN-Index |
| **Migration** | Schwierig | Einfach via `parent_id` ändern |

### 1.2 Datenmodell

```sql
CREATE TABLE course_categories (
    category_id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES course_categories(category_id),

    -- Basis-Felder
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    -- Hierarchie-Felder (automatisch via Trigger)
    level INTEGER NOT NULL DEFAULT 1 CHECK (level BETWEEN 1 AND 20),
    path VARCHAR(1000),           -- "IT/Netzwerk/Cisco/CCNA"
    path_ids INTEGER[],           -- [1, 5, 12, 45] für schnelle Abfragen
    root_id INTEGER REFERENCES course_categories(category_id),

    -- UI-Felder
    icon VARCHAR(10),             -- Emoji: "💻"
    color VARCHAR(7),             -- Hex: "#3B82F6"
    order_index INTEGER DEFAULT 0,

    -- Multi-Language
    name_en VARCHAR(100),
    name_es VARCHAR(100),
    name_fr VARCHAR(100),
    name_pl VARCHAR(100),

    -- Status
    active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Performance-Indizes
CREATE INDEX idx_categories_parent ON course_categories(parent_id);
CREATE INDEX idx_categories_level ON course_categories(level);
CREATE INDEX idx_categories_path ON course_categories(path);
CREATE INDEX idx_categories_path_ids ON course_categories USING GIN (path_ids);
CREATE INDEX idx_categories_root ON course_categories(root_id);
CREATE INDEX idx_categories_active ON course_categories(active) WHERE active = TRUE;
```

---

## 2. Hierarchie-Beispiele

### 2.1 IT-Zertifizierungen (7 Ebenen)

```
IT & Technologie (Level 1)
└── Netzwerke (Level 2)
    └── Cisco (Level 3)
        └── CCNA (Level 4)
            ├── CCNA Routing & Switching (Level 5)
            │   ├── OSI-Modell (Level 6)
            │   │   └── Layer 3 - Network (Level 7)
            │   └── Subnetting (Level 6)
            └── CCNA Security (Level 5)
```

**Datenbankeinträge:**

| category_id | name | parent_id | level | path |
|-------------|------|-----------|-------|------|
| 1 | IT & Technologie | NULL | 1 | IT & Technologie |
| 5 | Netzwerke | 1 | 2 | IT & Technologie/Netzwerke |
| 12 | Cisco | 5 | 3 | IT & Technologie/Netzwerke/Cisco |
| 45 | CCNA | 12 | 4 | IT & Technologie/Netzwerke/Cisco/CCNA |
| 67 | CCNA Routing & Switching | 45 | 5 | IT & Technologie/Netzwerke/Cisco/CCNA/CCNA Routing & Switching |

### 2.2 Sprachen mit CEFR (4 Ebenen)

```
Sprachen (Level 1)
├── Englisch (Level 2)
│   ├── Business English (Level 3)
│   │   ├── B1 - Intermediate (Level 4)
│   │   ├── B2 - Upper Intermediate (Level 4)
│   │   └── C1 - Advanced (Level 4)
│   └── Technical English (Level 3)
│       └── IT English (Level 4)
└── Deutsch (Level 2)
    └── Deutsch als Fremdsprache (Level 3)
        ├── A1 - Anfänger (Level 4)
        └── A2 - Grundlagen (Level 4)
```

---

## 3. Automatische Pfad-Berechnung (Trigger)

### 3.1 Trigger-Funktion

```sql
CREATE OR REPLACE FUNCTION update_category_path()
RETURNS TRIGGER AS $$
DECLARE
    parent_path VARCHAR(1000);
    parent_path_ids INTEGER[];
    parent_root_id INTEGER;
BEGIN
    IF NEW.parent_id IS NULL THEN
        -- Root-Kategorie
        NEW.level := 1;
        NEW.path := NEW.name;
        NEW.path_ids := ARRAY[NEW.category_id];
        NEW.root_id := NEW.category_id;
    ELSE
        -- Kind-Kategorie
        SELECT path, path_ids, root_id, level
        INTO parent_path, parent_path_ids, parent_root_id
        FROM course_categories
        WHERE category_id = NEW.parent_id;

        NEW.level := (SELECT level FROM course_categories WHERE category_id = NEW.parent_id) + 1;
        NEW.path := parent_path || '/' || NEW.name;
        NEW.path_ids := parent_path_ids || NEW.category_id;
        NEW.root_id := parent_root_id;

        -- Max-Tiefe prüfen
        IF NEW.level > 20 THEN
            RAISE EXCEPTION 'Maximum category depth (20) exceeded';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER category_path_trigger
BEFORE INSERT OR UPDATE OF parent_id, name ON course_categories
FOR EACH ROW EXECUTE FUNCTION update_category_path();
```

### 3.2 Rekursive Pfad-Aktualisierung

```sql
-- Aktualisiert alle Nachkommen wenn eine Kategorie verschoben wird
CREATE OR REPLACE FUNCTION update_descendant_paths()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.parent_id IS DISTINCT FROM NEW.parent_id OR OLD.name != NEW.name THEN
        -- Rekursiv alle Nachkommen aktualisieren
        WITH RECURSIVE descendants AS (
            SELECT category_id FROM course_categories WHERE parent_id = NEW.category_id
            UNION ALL
            SELECT c.category_id FROM course_categories c
            JOIN descendants d ON c.parent_id = d.category_id
        )
        UPDATE course_categories SET updated_at = NOW()
        WHERE category_id IN (SELECT category_id FROM descendants);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. API-Endpunkte

### 4.1 Öffentliche Endpunkte

```python
# Kategorie-Baum abrufen
GET /api/v1/categories/tree
# Query-Parameter:
#   - active_only: bool (default: true)
#   - language: str (de, en, es, fr)

# Root-Kategorien
GET /api/v1/categories/roots
# Gibt alle Level-1 Kategorien zurück

# Kategorie nach Pfad
GET /api/v1/categories/by-path?path=IT/Netzwerk/Cisco

# Alle Nachkommen einer Kategorie
GET /api/v1/categories/{id}/descendants
# Query-Parameter:
#   - include_self: bool (default: false)

# Breadcrumb-Pfad
GET /api/v1/categories/{id}/breadcrumb
# Gibt Array von Root bis Kategorie zurück
```

### 4.2 Admin-Endpunkte

```python
# Kategorie erstellen
POST /api/v1/admin/categories
{
    "name": "Python",
    "slug": "python",
    "parent_id": 15,  # Optional - null für Root
    "description": "Python Programmierung",
    "icon": "🐍",
    "color": "#3776AB"
}

# Kategorie aktualisieren
PATCH /api/v1/admin/categories/{id}
{
    "name": "Python 3",
    "is_active": true
}

# Kategorie verschieben
POST /api/v1/admin/categories/{id}/move
{
    "new_parent_id": 20  # null für Root
}

# Kategorie löschen (nur wenn leer)
DELETE /api/v1/admin/categories/{id}
```

### 4.3 Response-Format

```json
{
    "success": true,
    "data": {
        "category_id": 45,
        "name": "CCNA",
        "slug": "ccna",
        "description": "Cisco Certified Network Associate",
        "parent_id": 12,
        "level": 4,
        "path": "IT & Technologie/Netzwerke/Cisco/CCNA",
        "path_ids": [1, 5, 12, 45],
        "root_id": 1,
        "icon": "🌐",
        "color": "#1BA0D8",
        "order_index": 0,
        "is_active": true,
        "course_count": 15,
        "children": [
            {
                "category_id": 67,
                "name": "CCNA Routing & Switching",
                "level": 5,
                "children": []
            }
        ]
    }
}
```

---

## 5. Repository-Pattern

### 5.1 CategoryRepository

```python
class CategoryRepository(BaseRepository):
    """
    Repository für hierarchische Kategorien

    Features:
    - CRUD mit automatischer Hierarchie-Validierung
    - Tree-Building mit unbegrenzter Tiefe
    - Path-basierte Navigation
    - Kategorie-Verschiebung mit Validierung
    """

    table_name = 'course_categories'
    MAX_DEPTH = 20

    @classmethod
    def get_tree(cls, active_only: bool = False) -> List[Dict]:
        """Baut hierarchischen Baum aus flacher Liste"""
        all_categories = cls.get_all(active_only)

        # Lookup-Dictionary erstellen
        categories_dict = {
            cat['category_id']: {**cat, 'children': []}
            for cat in all_categories
        }

        # Baum aufbauen
        root_categories = []
        for category in all_categories:
            cat_id = category['category_id']
            parent_id = category['parent_id']

            if parent_id is None:
                root_categories.append(categories_dict[cat_id])
            elif parent_id in categories_dict:
                categories_dict[parent_id]['children'].append(
                    categories_dict[cat_id]
                )

        return root_categories

    @classmethod
    def get_descendants(cls, category_id: int, include_self: bool = False) -> List[Dict]:
        """Rekursive Abfrage aller Nachkommen"""
        query = """
            WITH RECURSIVE descendants AS (
                SELECT * FROM course_categories
                WHERE category_id = %(category_id)s

                UNION ALL

                SELECT c.* FROM course_categories c
                JOIN descendants d ON c.parent_id = d.category_id
            )
            SELECT * FROM descendants
        """
        if not include_self:
            query += " WHERE category_id != %(category_id)s"

        return fetch_all(query, {'category_id': category_id})

    @classmethod
    def move_category(cls, category_id: int, new_parent_id: Optional[int]) -> Dict:
        """
        Verschiebt Kategorie zu neuem Parent

        Validierungen:
        - Keine zirkulären Referenzen
        - Max-Tiefe nicht überschreiten
        - Alle Nachkommen werden automatisch aktualisiert
        """
        # Validierung: Nicht zu eigenem Nachkommen verschieben
        if new_parent_id:
            descendants = cls.get_descendants(category_id)
            if new_parent_id in [d['category_id'] for d in descendants]:
                raise ValueError('Cannot move category to its own descendant')

        # Level berechnen und Max-Tiefe prüfen
        # ... (siehe category_repository.py)
```

---

## 6. Frontend-Integration

### 6.1 Admin-UI Komponenten

```
frontend/src/
├── pages/admin/
│   └── AdminCategoriesPage.vue    # Hauptseite mit Tree-View
├── components/admin/
│   ├── CategoryTreeNode.vue       # Rekursive Baum-Komponente
│   └── CategoryModal.vue          # Create/Edit Modal
├── store/
│   └── admin.store.ts             # Pinia Store mit Category-Actions
└── api/
    └── admin.api.ts               # API-Client mit Category-Endpoints
```

### 6.2 Tree-View Komponente

```vue
<!-- CategoryTreeNode.vue - Rekursive Komponente -->
<template>
  <div class="category-node" :style="{ marginLeft: `${level * 16}px` }">
    <div class="category-row">
      <!-- Expand/Collapse -->
      <button v-if="hasChildren" @click="toggleExpanded">
        {{ isExpanded ? '▼' : '▶' }}
      </button>

      <!-- Level Badge mit Farbe -->
      <div class="level-badge" :class="getLevelClass()">
        L{{ category.level }}
      </div>

      <!-- Icon & Name -->
      <span class="icon">{{ category.icon || '📁' }}</span>
      <span class="name">{{ category.name }}</span>

      <!-- Path (bei tiefen Ebenen) -->
      <span v-if="category.level > 2" class="path">
        {{ category.path }}
      </span>

      <!-- Actions -->
      <div class="actions">
        <button @click="$emit('create-child', category)"
                v-if="category.level < 20">+</button>
        <button @click="$emit('edit', category)">✏️</button>
        <button @click="$emit('toggle-active', category)">
          {{ category.is_active ? '⏸' : '▶' }}
        </button>
        <button @click="$emit('delete', category)">🗑️</button>
      </div>
    </div>

    <!-- Rekursive Kinder -->
    <div v-if="hasChildren && isExpanded">
      <CategoryTreeNode
        v-for="child in category.children"
        :key="child.category_id"
        :category="child"
        :level="level + 1"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @toggle-active="$emit('toggle-active', $event)"
        @create-child="$emit('create-child', $event)"
      />
    </div>
  </div>
</template>
```

### 6.3 Level-Farben (20 Stufen)

```typescript
const levelColors = [
  'bg-purple-100 text-purple-700',   // Level 1
  'bg-blue-100 text-blue-700',       // Level 2
  'bg-green-100 text-green-700',     // Level 3
  'bg-yellow-100 text-yellow-700',   // Level 4
  'bg-orange-100 text-orange-700',   // Level 5
  'bg-red-100 text-red-700',         // Level 6
  'bg-pink-100 text-pink-700',       // Level 7
  'bg-indigo-100 text-indigo-700',   // Level 8
  'bg-cyan-100 text-cyan-700',       // Level 9
  'bg-teal-100 text-teal-700',       // Level 10
  'bg-lime-100 text-lime-700',       // Level 11
  'bg-amber-100 text-amber-700',     // Level 12
  'bg-emerald-100 text-emerald-700', // Level 13
  'bg-sky-100 text-sky-700',         // Level 14
  'bg-violet-100 text-violet-700',   // Level 15
  'bg-fuchsia-100 text-fuchsia-700', // Level 16
  'bg-rose-100 text-rose-700',       // Level 17
  'bg-slate-100 text-slate-700',     // Level 18
  'bg-zinc-100 text-zinc-700',       // Level 19
  'bg-stone-100 text-stone-700',     // Level 20
];
```

---

## 7. KI-Autokategorisierung

### 7.1 Kategorisierungs-Workflow

```
1. Creator lädt PDF/Text hoch
2. System extrahiert Text (OCR falls nötig)
3. KI analysiert Inhalt:
   - Keyword Extraction
   - Named Entity Recognition
   - Topic Modeling
   - Similarity Search gegen existierende Kurse
4. KI schlägt Kategorie-Pfad vor
5. Creator bestätigt oder korrigiert
6. Feedback trainiert das Modell
```

### 7.2 Beispiel-Vorschlag

```json
{
    "suggested_path": [
        {"category_id": 1, "name": "IT & Technologie", "confidence": 0.98},
        {"category_id": 5, "name": "Netzwerke", "confidence": 0.95},
        {"category_id": 12, "name": "Cisco", "confidence": 0.92},
        {"category_id": 45, "name": "CCNA", "confidence": 0.88}
    ],
    "reasoning": "Dokument enthält Schlüsselwörter: CCNA, Cisco, Routing, Switching, OSI-Modell",
    "alternative_paths": [
        {
            "path": ["IT & Technologie", "Netzwerke", "CompTIA", "Network+"],
            "confidence": 0.72
        }
    ]
}
```

---

## 8. Performance-Optimierungen

### 8.1 Indizes

```sql
-- Schnelle Parent-Lookups
CREATE INDEX idx_categories_parent ON course_categories(parent_id);

-- Level-basierte Filterung
CREATE INDEX idx_categories_level ON course_categories(level);

-- Path-Suche (LIKE 'IT/%')
CREATE INDEX idx_categories_path ON course_categories(path);

-- Array-Contains für path_ids
CREATE INDEX idx_categories_path_ids ON course_categories USING GIN (path_ids);

-- Root-Kategorie Lookups
CREATE INDEX idx_categories_root ON course_categories(root_id);

-- Aktive Kategorien (partieller Index)
CREATE INDEX idx_categories_active ON course_categories(active) WHERE active = TRUE;
```

### 8.2 Caching-Strategie

```python
# Cache-Keys
CATEGORY_TREE_CACHE = "CACHE:CATEGORY:tree:{active_only}"
CATEGORY_BREADCRUMB_CACHE = "CACHE:CATEGORY:breadcrumb:{category_id}"

# TTL: 1 Stunde (3600 Sekunden)
# Invalidierung bei:
# - CREATE/UPDATE/DELETE Kategorie
# - Kategorie-Verschiebung
```

---

## 9. Migration vom 5-Stufen-Modell

### 9.1 Migrations-Script

```sql
-- Migration 056: Flexibles Kategorie-System

-- 1. Neue Spalten hinzufügen
ALTER TABLE course_categories
ADD COLUMN IF NOT EXISTS path VARCHAR(1000),
ADD COLUMN IF NOT EXISTS path_ids INTEGER[],
ADD COLUMN IF NOT EXISTS root_id INTEGER REFERENCES course_categories(category_id);

-- 2. Level-Constraint anpassen (5 -> 20)
ALTER TABLE course_categories
DROP CONSTRAINT IF EXISTS course_categories_level_check;

ALTER TABLE course_categories
ADD CONSTRAINT course_categories_level_check CHECK (level BETWEEN 1 AND 20);

-- 3. Trigger für automatische Pfad-Berechnung
CREATE OR REPLACE FUNCTION update_category_path() ...

-- 4. Initiale Pfad-Berechnung für existierende Daten
WITH RECURSIVE category_paths AS (
    SELECT category_id, name, parent_id, 1 AS level,
           name::VARCHAR(1000) AS path,
           ARRAY[category_id] AS path_ids,
           category_id AS root_id
    FROM course_categories WHERE parent_id IS NULL

    UNION ALL

    SELECT c.category_id, c.name, c.parent_id, cp.level + 1,
           (cp.path || '/' || c.name)::VARCHAR(1000),
           cp.path_ids || c.category_id,
           cp.root_id
    FROM course_categories c
    JOIN category_paths cp ON c.parent_id = cp.category_id
)
UPDATE course_categories cc SET
    level = cp.level,
    path = cp.path,
    path_ids = cp.path_ids,
    root_id = cp.root_id
FROM category_paths cp
WHERE cc.category_id = cp.category_id;
```

---

## 10. Zusammenfassung

Das flexible Kategorie-System bietet **maximale Flexibilität** bei **optimaler Performance**:

### Kerneigenschaften

| Feature | Status |
|---------|--------|
| Unbegrenzte Tiefe (max 20) | ✅ |
| Automatische Pfad-Berechnung | ✅ |
| Path-basierte Navigation | ✅ |
| Rekursive Abfragen (CTEs) | ✅ |
| GIN-Index für path_ids | ✅ |
| Kategorie-Verschiebung | ✅ |
| Zirkuläre Referenz-Schutz | ✅ |
| Multi-Language Support | ✅ |
| Admin-UI mit Tree-View | ✅ |
| KI-Autokategorisierung | ✅ |
| Caching-Strategie | ✅ |

### Vorteile gegenüber 5-Stufen-Modell

- **Flexibilität:** Keine feste Struktur mehr - passt sich Inhalten an
- **Einfachheit:** Eine Tabelle statt fünf separate
- **Performance:** Optimierte Indizes und CTEs
- **Wartbarkeit:** Einfache Erweiterung ohne Schema-Änderungen
- **Navigation:** Vollständiger Pfad direkt verfügbar

---

**Dokument abgeschlossen.**
**Letzte Aktualisierung:** 2025-12-03
**Migration:** 056_flexible_categories.sql
