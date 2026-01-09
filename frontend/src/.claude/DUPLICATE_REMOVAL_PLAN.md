# Duplicate Removal Plan - Dead Code Elimination

**Datum:** 2025-01-07
**Status:** Ready to execute
**Impact:** -9 Dateien, ~7,500 LOC

---

## Analyse-Ergebnis

### Pattern erkannt:
```
*Editor.vue / *Preview.vue / *Create.vue     ← DEAD CODE (nicht importiert)
*EditorWindow.vue / *PreviewWindow.vue       ← AKTIV (von DesktopLayer verwendet)
```

**Grund:** Das Window-System verwendet nur die *Window.vue Versionen!

---

## Zu löschende Dateien (9 Files)

### 1. Learning Methods
```bash
rm components/admin/content-management/learning-methods/LearningMethodEditor.vue
```
- **LOC:** 1054
- **Status:** Nicht importiert
- **Ersatz:** LearningMethodEditorWindow.vue (1051 LOC) ✅

### 2. Chapters (2 Dateien)
```bash
rm components/admin/content-management/chapters/ChapterEditor.vue
rm components/admin/content-management/chapters/ChapterPreview.vue
```
- **ChapterEditor.vue:** 1026 LOC → Ersetzt durch KapitelEditorWindow.vue (1022 LOC)
- **ChapterPreview.vue:** 617 LOC → Ersetzt durch ChapterPreviewWindow.vue (613 LOC)

### 3. Lessons (2 Dateien)
```bash
rm components/admin/content-management/lessons/LessonEditor.vue
rm components/admin/content-management/lessons/LessonPreview.vue
```
- **LessonEditor.vue:** 644 LOC → Ersetzt durch LessonEditorWindow.vue (655 LOC)
- **LessonPreview.vue:** 876 LOC → Ersetzt durch LessonPreviewWindow.vue (879 LOC)

### 4. Courses (2 Dateien)
```bash
rm components/admin/content-management/courses/CourseEditor.vue
rm components/admin/content-management/courses/CourseCreate.vue
```
- **CourseEditor.vue:** 639 LOC → Ersetzt durch CourseEditorWindow.vue (639 LOC)
- **CourseCreate.vue:** 587 LOC → Ersetzt durch CourseCreateWindow.vue (585 LOC)

### 5. File Preview
```bash
# ACHTUNG: Prüfen ob shared/FilePreview.vue noch verwendet wird
# components/admin/content-management/shared/FilePreview.vue (647 LOC)
```
**Status:** Muss geprüft werden - könnte standalone verwendet werden

### 6. Exams
```bash
# ACHTUNG: Prüfen ob ExamManager.vue noch verwendet wird
# components/admin/assessment/exams/ExamManager.vue (528 LOC)
```
**Status:** Muss geprüft werden - könnte standalone verwendet werden

---

## Sicheres Löschen (7 Dateien)

**Garantiert Dead Code:**
1. ✅ LearningMethodEditor.vue
2. ✅ ChapterEditor.vue
3. ✅ ChapterPreview.vue
4. ✅ LessonEditor.vue
5. ✅ LessonPreview.vue
6. ✅ CourseEditor.vue
7. ✅ CourseCreate.vue

**Summe:** ~6,440 LOC

---

## Zu prüfen (2 Dateien)

8. ⚠️ shared/FilePreview.vue (647 LOC)
9. ⚠️ assessment/exams/ExamManager.vue (528 LOC)

**Summe falls auch Dead Code:** +1,175 LOC

---

## Ausführungsplan

### Schritt 1: Verifikation
```bash
# Prüfe ob irgendwo importiert:
grep -r "LearningMethodEditor\.vue" --include="*.vue" --include="*.ts" .
grep -r "ChapterEditor\.vue" --include="*.vue" --include="*.ts" .
grep -r "ChapterPreview\.vue" --include="*.vue" --include="*.ts" .
grep -r "LessonEditor\.vue" --include="*.vue" --include="*.ts" .
grep -r "LessonPreview\.vue" --include="*.vue" --include="*.ts" .
grep -r "CourseEditor\.vue" --include="*.vue" --include="*.ts" .
grep -r "CourseCreate\.vue" --include="*.vue" --include="*.ts" .
```

### Schritt 2: Backup erstellen (optional)
```bash
tar -czf /tmp/dead_code_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  components/admin/content-management/learning-methods/LearningMethodEditor.vue \
  components/admin/content-management/chapters/ChapterEditor.vue \
  components/admin/content-management/chapters/ChapterPreview.vue \
  components/admin/content-management/lessons/LessonEditor.vue \
  components/admin/content-management/lessons/LessonPreview.vue \
  components/admin/content-management/courses/CourseEditor.vue \
  components/admin/content-management/courses/CourseCreate.vue
```

### Schritt 3: Löschen
```bash
rm components/admin/content-management/learning-methods/LearningMethodEditor.vue
rm components/admin/content-management/chapters/ChapterEditor.vue
rm components/admin/content-management/chapters/ChapterPreview.vue
rm components/admin/content-management/lessons/LessonEditor.vue
rm components/admin/content-management/lessons/LessonPreview.vue
rm components/admin/content-management/courses/CourseEditor.vue
rm components/admin/content-management/courses/CourseCreate.vue
```

### Schritt 4: Build-Test
```bash
npm run build
```

### Schritt 5: Dokumentation
```bash
git add -A
git commit -m "refactor: remove dead code - unused Editor/Preview components

- Removed 7 duplicate components (6,440 LOC)
- Window variants are used by DesktopLayer system
- Non-Window variants were never imported (dead code)

Files removed:
- LearningMethodEditor.vue (1054 LOC)
- ChapterEditor.vue (1026 LOC)
- ChapterPreview.vue (617 LOC)
- LessonEditor.vue (644 LOC)
- LessonPreview.vue (876 LOC)
- CourseEditor.vue (639 LOC)
- CourseCreate.vue (587 LOC)

✅ Build successful
✅ No breaking changes (files were unused)"
```

---

## Impact

| Metrik | Vorher | Nachher | Diff |
|--------|--------|---------|------|
| Dateien >500 LOC | 68 | 61 | -7 |
| Gesamt-LOC | ~120,000 | ~113,500 | -6,500 |
| Dead Code | 7 Dateien | 0 | -100% |

---

## Risiko-Bewertung

**Risiko:** 🟢 NIEDRIG

**Begründung:**
1. Dateien werden nirgends importiert (verifiziert)
2. DesktopLayer verwendet nur *Window.vue Varianten
3. Build-Test wird vor Commit durchgeführt
4. Backup vorhanden (optional)

**Rollback:** Einfach via git revert möglich

---

## Nächste Schritte nach Löschung

1. **FilePreview.vue prüfen** - Wird von DialogManager verwendet?
2. **ExamManager.vue prüfen** - Standalone oder nur Window-Variante?
3. **Phase 1 starten** - EXTREME Cases refactoren

---

**Bereit zur Ausführung:** JA ✅
