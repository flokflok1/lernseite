# Courses Domain - Migration Checklist

**Version:** 1.0
**Datum:** 2026-01-08
**Für:** Entwickler die mit courses/ Domain arbeiten

---

## ✅ Quick Start

### 1. Neue Imports verwenden

**ALT (DEPRECATED):**
```python
from app.api.admin.courses.management.crud import admin_create_course
from app.repositories.courses import CourseRepository
```

**NEU:**
```python
# Domain Layer
from app.api.courses.core import CourseFactory, CourseService
from app.api.courses.core import CourseStatus, Visibility, Price

# API Layer
from app.api.courses import admin, courses_bp, enrollment_bp
```

---

## 📋 Migration Steps für bestehenden Code

### Schritt 1: Kurs erstellen

**ALT:**
```python
new_course = CourseRepository.admin_create_course(
    course_data={'title': 'Test', 'category_id': 'cat123'},
    created_by_admin=user_id
)
```

**NEU (mit Factory):**
```python
# Factory erstellt mit Business Rules
course_data = CourseFactory.create_draft(
    creator_id=user_id,
    title='Test',
    category_id='cat123',
    description='Optional'
)

# Repository speichert
new_course = CourseRepository.create(course_data)
```

**Vorteile:**
- ✅ Business Rules automatisch angewendet
- ✅ Gültiger Anfangszustand garantiert
- ✅ Keine vergessenen Pflichtfelder

---

### Schritt 2: Kurs publizieren

**ALT:**
```python
result = CourseRepository.publish(course_id)
```

**NEU (mit Factory):**
```python
# Load existing course
course = CourseRepository.find_by_id(course_id)

# Factory handhabt State Transition + Validierung
try:
    published_course = CourseFactory.publish(course, publisher_id)
    CourseRepository.update(published_course)
except ValueError as e:
    # Business Rule verletzt (z.B. kein Content)
    print(f"Cannot publish: {e}")
```

**Vorteile:**
- ✅ Business Rules validiert (min. 1 Kapitel)
- ✅ State Transition sauber
- ✅ Audit Trail (published_by, published_at)

---

### Schritt 3: Enrollment Check

**ALT:**
```python
# Manuell alle Regeln prüfen
if not course['is_published']:
    return False
if enrollment_exists:
    return False
# ... 4 weitere Checks
```

**NEU (mit Service):**
```python
from app.api.courses.core import CourseService

can_enroll, reason = CourseService.can_user_enroll(user, course)

if can_enroll:
    # Proceed with enrollment
    EnrollmentRepository.create(...)
else:
    # Show reason to user
    return jsonify({'error': reason}), 400
```

**Vorteile:**
- ✅ Alle 6 Business Rules an einem Ort
- ✅ Wiederverwendbar
- ✅ Leicht testbar

---

### Schritt 4: Progress berechnen

**ALT:**
```python
# Manuell Lessons zählen
chapters = ChapterRepository.find_by_course(course_id)
total = 0
completed = 0
for chapter in chapters:
    lessons = LessonRepository.find_by_chapter(chapter['chapter_id'])
    total += len(lessons)
    # ... komplexe Logik
progress = (completed / total) * 100 if total > 0 else 0
```

**NEU (mit Service):**
```python
progress = CourseService.calculate_progress(user_id, course_id)
# Returns: 75.5 (float 0-100)
```

**Vorteile:**
- ✅ Eine Zeile statt 20+
- ✅ Konsistente Berechnung
- ✅ Zentral testbar

---

## 🎯 Wann welchen Layer nutzen?

| Use Case | Layer | Beispiel |
|----------|-------|----------|
| Objekt erstellen | Factory | `CourseFactory.create_draft()` |
| State Transition | Factory | `CourseFactory.publish()` |
| Multi-Entity Logic | Service | `CourseService.can_user_enroll()` |
| Typ-sichere Werte | Value Object | `CourseStatus.DRAFT` |
| Datenzugriff | Repository | `CourseRepository.find_by_id()` |
| HTTP Endpoint | API Layer | `@api_v1.route('/courses')` |

---

## 🚨 Häufige Fehler vermeiden

### Fehler 1: Factory umgehen

**❌ FALSCH:**
```python
# Direkt Dict erstellen ohne Factory
course = {
    'course_id': str(uuid.uuid4()),
    'title': 'Test',
    'status': 'draft',
    # ... vergessene Felder, keine Business Rules
}
CourseRepository.create(course)
```

**✅ RICHTIG:**
```python
# Factory nutzen
course = CourseFactory.create_draft(creator_id, title, category_id)
CourseRepository.create(course)
```

---

### Fehler 2: Business Rules duplizieren

**❌ FALSCH:**
```python
# In jedem Endpoint die gleichen Checks
if not course['is_published']:
    return error()
if enrollment_exists:
    return error()
# ... (Code-Duplikation in 3+ Stellen)
```

**✅ RICHTIG:**
```python
# Service nutzen (DRY)
can_enroll, reason = CourseService.can_user_enroll(user, course)
if not can_enroll:
    return jsonify({'error': reason}), 400
```

---

### Fehler 3: Magic Strings verwenden

**❌ FALSCH:**
```python
course['status'] = 'draft'  # Magic String
if course['status'] == 'publshed':  # Typo!
    ...
```

**✅ RICHTIG:**
```python
from app.api.courses.core import CourseStatus

course['status'] = CourseStatus.DRAFT.value
if course['status'] == CourseStatus.PUBLISHED.value:
    ...
```

---

## 📝 Code Review Checklist

Beim Review von Code der courses/ nutzt:

- [ ] Nutzt Factory für Objekterstellung?
- [ ] Nutzt Service für Business Logic?
- [ ] Nutzt Enums statt Magic Strings?
- [ ] Keine Business Rules dupliziert?
- [ ] Type Hints vorhanden?
- [ ] Docstrings vorhanden?
- [ ] Tests dabei?
- [ ] Keine direkten SQL-Queries im API Layer?

---

## 🧪 Testing Beispiele

### Factory Tests

```python
def test_create_draft_business_rules():
    """Test: Draft courses are always private."""
    course = CourseFactory.create_draft(
        creator_id="user123",
        title="Test",
        category_id="cat456"
    )
    assert course['status'] == 'draft'
    assert course['visibility'] == 'private'
    assert course['is_published'] is False
    assert course['requires_enrollment'] is True
```

### Service Tests

```python
def test_can_enroll_published_course():
    """Test: Cannot enroll in unpublished course."""
    user = {'user_id': 'user123'}
    course = {'is_published': False}

    can_enroll, reason = CourseService.can_user_enroll(user, course)

    assert can_enroll is False
    assert reason == "Course is not published"
```

### Value Object Tests

```python
def test_price_validation():
    """Test: Price cannot be negative."""
    with pytest.raises(ValueError, match="Price cannot be negative"):
        Price(-10.0, "EUR")
```

---

## 🔗 Weitere Ressourcen

- `courses/ARCHITECTURE.md` - Vollständige Architektur-Dokumentation
- `courses/REFACTORING_SUMMARY.md` - Refactoring-Details
- `courses/core/factory.py` - Factory Pattern Beispiele
- `courses/core/services.py` - Service Pattern Beispiele

---

## ❓ FAQ

### Q: Muss ich immer Factory verwenden?

**A:** Ja, für neue Objekte. Factory garantiert gültigen Zustand und Business Rules.

### Q: Wann Service statt Factory?

**A:** Service für Logic über mehrere Entities (z.B. User + Course). Factory für einzelne Objekte.

### Q: Kann ich Repository direkt nutzen?

**A:** Ja, für CRUD. Aber keine Business Logic im Repository!

### Q: Was wenn ich neue Business Rule brauche?

**A:**
1. Regel in Factory/Service hinzufügen
2. Tests schreiben
3. Dokumentation updaten

### Q: Alte Endpoints löschen?

**A:** NEIN! Alte Endpoints bleiben für Backward Compatibility. Nur intern umstellen.

---

**Version:** 1.0
**Datum:** 2026-01-08
**Status:** ✅ READY FOR USE
