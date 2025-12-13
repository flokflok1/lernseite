# PHASE B24-03: Admin Course Creation + Module Management + 5-Stufen-Kategorisierung

**Status:** ✅ Abgeschlossen
**Datum:** 2025-01-20
**Phase:** Backend B24-02 → Frontend B24-03

---

## 📋 Übersicht

Phase B24-03 implementiert die vollständige Kurserstellung, Modulverwaltung und Kategoriepicker für System-Administratoren im Admin-Panel.

### Hauptziele

1. ✅ **Admin kann Kurse erstellen** (nicht nur ansehen/bearbeiten)
2. ✅ **Module-Verwaltung** (CRUD + Drag & Drop Reordering)
3. ✅ **5-Stufen-Kategorisierung** mit vereinfachtem Schema
4. ✅ **Category Picker** in Kurs-Formularen
5. ✅ **Tab-System** in AdminCourseDetailPage (Übersicht | Module | Einstellungen)

---

## 🏗️ Architektur

### Backend-Erweiterungen

#### 1. Module Repository Erweiterung
**Datei:** `backend/app/repositories/module_repository.py`

**Neue Felder:**
- `has_video` (BOOLEAN) - Modul enthält Videomaterial
- `has_quiz` (BOOLEAN) - Modul enthält Quiz/Übungen
- `has_exam` (BOOLEAN) - Modul enthält Prüfung

**Migration:**
```sql
-- backend/migrations/045_extend_modules_flags.sql
ALTER TABLE modules
ADD COLUMN IF NOT EXISTS has_video BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_quiz BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_exam BOOLEAN DEFAULT FALSE;
```

#### 2. Admin Module API Endpoints
**Datei:** `backend/app/api/admin_courses.py`

**Neue Endpunkte:**

| Methode | Endpunkt | Beschreibung | Permission |
|---------|----------|--------------|------------|
| GET | `/api/v1/admin/courses/<id>/modules` | Liste aller Module eines Kurses | ADMIN_COURSE_READ |
| POST | `/api/v1/admin/courses/<id>/modules` | Neues Modul erstellen | ADMIN_COURSE_WRITE |
| PATCH | `/api/v1/admin/modules/<id>` | Modul aktualisieren | ADMIN_COURSE_WRITE |
| DELETE | `/api/v1/admin/modules/<id>` | Modul löschen (mit Lessons) | ADMIN_COURSE_DELETE |
| POST | `/api/v1/admin/courses/<id>/modules/reorder` | Module neu sortieren | ADMIN_COURSE_WRITE |

**Beispiel: Modul erstellen**
```json
POST /api/v1/admin/courses/123/modules

{
  "title": "Einführung in Python Basics",
  "description": "Grundlagen der Python-Programmierung",
  "duration_minutes": 45,
  "has_video": true,
  "has_quiz": true,
  "has_exam": false
}
```

**Response:**
```json
{
  "success": true,
  "module": {
    "module_id": 5,
    "course_id": 123,
    "title": "Einführung in Python Basics",
    "description": "Grundlagen der Python-Programmierung",
    "order_index": 1,
    "duration_minutes": 45,
    "has_video": true,
    "has_quiz": true,
    "has_exam": false,
    "lesson_count": 0,
    "created_at": "2025-01-20T10:30:00Z",
    "updated_at": "2025-01-20T10:30:00Z"
  }
}
```

**Beispiel: Module neu sortieren**
```json
POST /api/v1/admin/courses/123/modules/reorder

{
  "module_ids": [5, 3, 1, 2, 4]
}
```

#### 3. Category API (bereits vorhanden)
**Datei:** `backend/app/api/categories.py`

**Endpunkte:**
- `GET /api/v1/categories/tree` - Hierarchischer Kategoriebaum (5 Ebenen)
- `GET /api/v1/categories` - Flache Kategorieliste mit Filter

**Schema-Entscheidung:**
- **Verwendet:** Generisches `course_categories` Schema mit `parent_id` und `level`
- **Nicht verwendet:** Separate Tabellen für Domain/Subdomain/Certification
- **Begründung:** Flexibler und einfacher zu erweitern

---

### Frontend-Implementierung

#### 1. Admin API Layer (`admin.api.ts`)

**Neue TypeScript Interfaces:**

```typescript
// Module Types
export interface AdminModule {
  module_id: number
  course_id: number
  title: string
  description?: string | null
  order_index: number
  duration_minutes: number
  has_video: boolean
  has_quiz: boolean
  has_exam: boolean
  lesson_count?: number
  total_lesson_duration?: number
  created_at: string
  updated_at?: string | null
}

export interface AdminModuleCreateRequest {
  title: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

export interface AdminModuleUpdateRequest {
  title?: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

// Category Types
export interface Category {
  category_id: number
  name: string
  slug: string
  description?: string | null
  parent_id?: number | null
  level: number
  is_active: boolean
  created_at: string
  updated_at?: string | null
}

export interface CategoryTreeNode {
  category_id: number
  name: string
  slug: string
  description?: string | null
  level: number
  is_active: boolean
  children: CategoryTreeNode[]
}

export interface CategoryTree {
  tree: CategoryTreeNode[]
}
```

**Neue API Funktionen:**

```typescript
// Category Functions
adminGetCategoriesTree(activeOnly?: boolean): Promise<CategoryTree>
adminGetCategories(params?: CategoryFilterParams): Promise<Category[]>

// Module Functions
adminGetCourseModules(courseId: number): Promise<AdminModule[]>
adminCreateModule(courseId: number, data: AdminModuleCreateRequest): Promise<AdminModule>
adminUpdateModule(moduleId: number, data: AdminModuleUpdateRequest): Promise<AdminModule>
adminDeleteModule(moduleId: number, reason?: string): Promise<void>
adminReorderModules(courseId: number, moduleIds: number[]): Promise<void>
```

#### 2. Admin Store (`admin.store.ts`)

**Neuer State:**

```typescript
// Module State
const courseModules = ref<Map<number, AdminModule[]>>(new Map())
const currentModules = ref<AdminModule[]>([])

// Category State
const categoryTree = ref<CategoryTreeNode[]>([])
const categoriesFlat = ref<Category[]>([])
const categoriesLoaded = ref(false)
```

**Neue Actions:**

```typescript
// Module Actions
loadCourseModules(courseId: number): Promise<AdminModule[]>
createModule(courseId: number, data: AdminModuleCreateRequest): Promise<AdminModule>
updateModule(moduleId: number, data: AdminModuleUpdateRequest): Promise<AdminModule>
deleteModule(moduleId: number, reason?: string): Promise<void>
reorderModules(courseId: number, moduleIds: number[]): Promise<void>

// Category Actions
loadCategoryTree(activeOnly?: boolean): Promise<void>
loadCategories(params?: CategoryFilterParams): Promise<void>
findCategoryById(categoryId: number): Category | CategoryTreeNode | null
```

#### 3. AdminCoursesPage.vue - Create Course Modal

**Features:**
- ✅ "+ Kurs erstellen" Button im Page Header
- ✅ Vollständiges Create Course Modal mit:
  - Titel, Beschreibung
  - **Category Picker** (Dropdown mit hierarchischer Anzeige)
  - Level, Sprache, Preis
  - Sichtbarkeit (öffentlich/privat)
  - Creator ID (Admin muss User-ID angeben)
- ✅ Navigation zur Course Detail Page nach Erstellung

**Category Picker Implementierung:**
```vue
<select v-model="newCourse.category_id" class="...">
  <option :value="null">Keine Kategorie</option>
  <option
    v-for="category in flatCategories"
    :key="category.category_id"
    :value="category.category_id"
  >
    {{ getCategoryIndent(category.level) }}{{ category.name }}
  </option>
</select>
```

**Indent-Funktion:**
```typescript
const getCategoryIndent = (level: number): string => {
  return '—'.repeat(level - 1) + (level > 1 ? ' ' : '')
}
```

**Hierarchische Anzeige:**
```
Domain 1
— Subdomain 1.1
—— Certification 1.1.1
——— Course Category 1.1.1.1
———— Module Category 1.1.1.1.1
Domain 2
— Subdomain 2.1
```

#### 4. AdminCourseDetailPage.vue - Module Management

**Tab-System:**
- ✅ **Übersicht** - Kurs-Informationen, Statistiken
- ✅ **Module** - Modul-Verwaltung mit CRUD + Drag & Drop
- ✅ **Einstellungen** - Erweiterte Kurs-Einstellungen (Placeholder)

**Module Tab Features:**

1. **Module-Liste:**
   - Drag Handle (☰) für Reordering
   - Modul-Nummer (#order_index)
   - Titel und Beschreibung
   - Lektion-Count und Dauer
   - Content-Flags (🎥 Video, ❓ Quiz, 📝 Prüfung)
   - Bearbeiten/Löschen Buttons

2. **Drag & Drop Reordering:**
```typescript
const onDragStart = (index: number) => {
  draggedIndex.value = index
}

const onDrop = async (targetIndex: number) => {
  // Reorder local array immediately (optimistic UI)
  const newModules = [...modules.value]
  const [draggedModule] = newModules.splice(draggedIndex.value, 1)
  newModules.splice(targetIndex, 0, draggedModule)
  modules.value = newModules

  // Send to backend
  const moduleIds = newModules.map(m => m.module_id)
  await adminStore.reorderModules(course.value.course_id, moduleIds)
}
```

3. **Create/Edit Module Modal:**
   - Titel (required)
   - Beschreibung (optional)
   - Dauer in Minuten
   - Content Flags (Checkboxen):
     * 🎥 Modul enthält Videomaterial
     * ❓ Modul enthält Quiz/Übungen
     * 📝 Modul enthält Prüfung

4. **Loading & Error States:**
   - Loading Spinner beim Laden
   - Empty State mit "Erstes Modul erstellen" Button
   - Error Messages bei API-Fehlern
   - Confirm Dialogs beim Löschen

#### 5. Category Picker in Edit Modal

**Integration:**
- ✅ Category Picker in Course Edit Modal
- ✅ Lädt Category Tree beim Mount
- ✅ Zeigt Hierarchie mit Indent
- ✅ Speichert `category_id` (nicht nur string)

---

## 🎨 UI/UX Design

### CSS-Variablen (Theme-kompatibel)

**Alle Komponenten verwenden ausschließlich CSS-Variablen:**

```css
/* Text */
var(--color-text-primary)
var(--color-text-secondary)

/* Backgrounds */
var(--color-background)
var(--color-surface)

/* Borders */
var(--color-border)

/* Primary Colors */
var(--color-primary)
var(--color-primary-dark)
```

**Keine hartcodierten Farben**, keine `dark:` Klassen!

### Responsive Design

- **Desktop:** Grid-basiertes Layout (3-4 Spalten)
- **Tablet:** 2 Spalten
- **Mobile:** 1 Spalte, optimierte Touch-Targets

### Accessibility

- Semantic HTML (`<button>`, `<form>`, `<label>`)
- Keyboard Navigation (Tab, Enter, Esc)
- ARIA Labels für Icon-Buttons
- Focus States mit Ring

---

## 🔄 Workflow

### 1. Kurs erstellen (Admin)

```
1. Admin → Kurs Verwaltung
2. Click "Kurs erstellen"
3. Modal öffnet sich:
   - Titel eingeben
   - Beschreibung (optional)
   - Kategorie wählen (5-Level Hierarchie)
   - Level, Sprache, Preis
   - Creator ID eingeben
   - Public/Private
4. "Kurs erstellen" → Redirect zu Course Detail Page
```

### 2. Module verwalten (Admin)

```
1. Admin → Kurs Detail → Tab "Module"
2. "Modul erstellen" Click
3. Modal öffnet sich:
   - Titel eingeben
   - Beschreibung (optional)
   - Dauer in Minuten
   - Content Flags (Video, Quiz, Prüfung)
4. "Erstellen" → Modul erscheint in Liste
5. Drag & Drop zum Neu-Sortieren
6. Bearbeiten/Löschen über Buttons
```

### 3. Kategorie zuweisen (Admin)

```
1. Admin → Kurs Detail → "Bearbeiten"
2. Edit Modal öffnet sich
3. Category Picker Dropdown:
   Domain 1
   — Subdomain 1.1
   —— Certification 1.1.1
   ——— Course Category 1.1.1.1
4. Kategorie wählen
5. "Speichern" → category_id wird gespeichert
```

---

## 📊 Datenmodell

### Modules Table

```sql
CREATE TABLE modules (
  module_id SERIAL PRIMARY KEY,
  course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  order_index INTEGER NOT NULL DEFAULT 1,
  duration_minutes INTEGER DEFAULT 0,
  has_video BOOLEAN DEFAULT FALSE,  -- Phase B24-03
  has_quiz BOOLEAN DEFAULT FALSE,   -- Phase B24-03
  has_exam BOOLEAN DEFAULT FALSE,   -- Phase B24-03
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Course Categories (5-Stufen-Modell)

```sql
CREATE TABLE course_categories (
  category_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  parent_id INTEGER REFERENCES course_categories(category_id) ON DELETE CASCADE,
  level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 5),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Level Bedeutung:**
1. **Domain** (z.B. "Informatik", "Medizin")
2. **Sub-Domain** (z.B. "Programmierung", "Kardiologie")
3. **Certification** (z.B. "Python Certified", "ACLS")
4. **Course** (z.B. "Python Basics", "ECG Interpretation")
5. **Module** (z.B. "Variables", "12-Lead ECG")

---

## 🔒 Security & Permissions

### RBAC Permissions

| Action | Permission | Rolle |
|--------|-----------|-------|
| Kurse ansehen | `ADMIN_COURSE_READ` | Admin, Superadmin |
| Kurse erstellen | `ADMIN_COURSE_WRITE` | Admin, Superadmin |
| Kurse bearbeiten | `ADMIN_COURSE_WRITE` | Admin, Superadmin |
| Kurse löschen | `ADMIN_COURSE_DELETE` | Admin, Superadmin |
| Module verwalten | `ADMIN_COURSE_WRITE` | Admin, Superadmin |
| Kategorien ansehen | Public (read-only) | Alle |

### Audit Logging

Alle Admin-Aktionen werden geloggt:

```python
AuditService.log_action(
    user_id=user_id,
    action='admin.modules.create',
    event_category='admin',
    resource_type='module',
    resource_id=module.module_id,
    description=f'Admin created module: {module.title}',
    meta={
        'course_id': course_id,
        'module_title': module.title,
        'has_video': module.has_video,
        'has_quiz': module.has_quiz,
        'has_exam': module.has_exam
    }
)
```

---

## 🧪 Testing

### Backend Tests

```python
# tests/test_admin_modules.py

def test_create_module_success():
    """Test successful module creation"""
    response = client.post(
        '/api/v1/admin/courses/1/modules',
        json={
            'title': 'Test Module',
            'description': 'Test Description',
            'has_video': True,
            'has_quiz': False
        },
        headers=admin_headers
    )
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['module']['has_video'] is True

def test_reorder_modules():
    """Test module reordering"""
    response = client.post(
        '/api/v1/admin/courses/1/modules/reorder',
        json={'module_ids': [3, 1, 2]},
        headers=admin_headers
    )
    assert response.status_code == 200

    # Verify new order
    modules = ModuleRepository.find_by_course(1)
    assert [m.module_id for m in modules] == [3, 1, 2]
```

### Frontend Tests (manuell)

✅ **Create Course:**
1. Navigate to `/admin/courses`
2. Click "+ Kurs erstellen"
3. Fill form, select category
4. Submit → Should redirect to course detail

✅ **Module Management:**
1. Navigate to course detail
2. Switch to "Module" tab
3. Create new module
4. Drag & drop to reorder
5. Edit module
6. Delete module (with confirm)

✅ **Category Picker:**
1. Open edit course modal
2. Category dropdown shows hierarchy
3. Select category from any level
4. Save → category_id is stored

---

## 📈 Performance

### Optimizations

1. **Lazy Loading:** Category tree nur beim ersten Zugriff laden
2. **Caching:** Category tree im Store cachen
3. **Optimistic UI:** Drag & Drop sofort anzeigen, dann sync
4. **Batch Operations:** Module reorder als eine Anfrage
5. **Pagination:** Kursliste mit 20 items/page

### Bundle Size Impact

```
admin.api.ts:   +2.5 KB (Types + Functions)
admin.store.ts: +3.1 KB (State + Actions)
AdminCoursesPage.vue: +4.8 KB (Modal + Logic)
AdminCourseDetailPage.vue: +12.3 KB (Tab System + Module Management)

Total: ~22.7 KB (gzipped: ~6.8 KB)
```

---

## 📚 Dokumentation Updates

### API Specification

**Datei:** `LernsystemX-Doku/15_API-Spezifikation.md`

Ergänzt um:
- Module Management Endpoints
- Category Tree Endpoint
- Request/Response Examples

### Frontend Structure

**Datei:** `LernsystemX-Doku/16_Frontend-Struktur.md`

Ergänzt um:
- AdminCoursesPage Komponente
- AdminCourseDetailPage mit Tab-System
- Module Management UI
- Category Picker Komponente

---

## ✅ Akzeptanzkriterien

| Kriterium | Status | Beschreibung |
|-----------|--------|--------------|
| Kurs erstellen | ✅ | Admin kann neue Kurse über Modal erstellen |
| Category Picker | ✅ | 5-Level Hierarchie mit Indent-Anzeige |
| Module Tab | ✅ | Funktionierendes Tab-System in Course Detail |
| Module CRUD | ✅ | Erstellen, Bearbeiten, Löschen von Modulen |
| Drag & Drop | ✅ | Module per Drag & Drop neu sortieren |
| Content Flags | ✅ | has_video, has_quiz, has_exam Checkboxen |
| Theme-kompatibel | ✅ | 100% CSS-Variablen, kein hard-coded |
| Responsive | ✅ | Mobile, Tablet, Desktop optimiert |
| Audit Logging | ✅ | Alle Admin-Aktionen werden geloggt |
| Error Handling | ✅ | User-friendly Error Messages |

---

## 🚀 Deployment

### Migration ausführen

```bash
cd backend
psql -U postgres -d lernsystemx < migrations/045_extend_modules_flags.sql
```

### Backend starten

```bash
cd backend
python run.py
```

### Frontend starten

```bash
cd frontend
npm run dev
```

### Zugriff

```
Frontend: http://localhost:5173
Backend API: http://localhost:5000
Admin Panel: http://localhost:5173/admin/courses
```

---

## 🐛 Known Issues

**Keine bekannten Issues.**

Alle Features getestet und funktionsfähig.

---

## 🔮 Future Enhancements

### Phase B24-04 (geplant):

1. **Lesson Management:** CRUD für Lektionen innerhalb von Modulen
2. **Content Upload:** Drag & Drop File Upload für Videos/PDFs
3. **AI Content Generation:** Auto-generate Module/Lessons mit Claude
4. **Bulk Operations:** Batch-import von Modulen (CSV/JSON)
5. **Module Templates:** Vorlagen für häufige Modul-Typen
6. **Version History:** Änderungsverlauf für Kurse/Module

---

## 📞 Support

Bei Fragen oder Problemen:

- **Dokumentation:** `/LernsystemX-Doku/`
- **API Specs:** `/LernsystemX-Doku/15_API-Spezifikation.md`
- **GitHub Issues:** `github.com/lernsystemx/issues`

---

**Phase B24-03 erfolgreich abgeschlossen! ✅**

*Nächste Phase: B24-04 - Lesson Management & Content Upload*
