# Refactoring-Analyse: KursBuilderTab.vue Sub-Komponenten
**Date:** 2025-01-07
**Analyst:** Senior Dev (ISO/IEC 26515 Compliance)
**Status:** ✅ Analyse COMPLETE

---

## 📊 Executive Summary

### Wichtigste Erkenntnis
**Sub-Komponenten existieren bereits**, sind aber **NICHT integriert** in KursBuilderTab.vue!

| Metrik | Wert | Details |
|--------|------|---------|
| **KursBuilderTab.vue** | 2945 LOC | ❌ Nutzt Sub-Komponenten NICHT |
| **Sub-Komponenten vorhanden** | 5 Dateien | ✅ Existieren in `kurs-builder/` |
| **Total Sub-LOC** | 2120 LOC | Bereits extrahiert, aber ungenutzt |
| **Fehlende Composables** | 6 | 🔴 KRITISCH - Logik noch in KursBuilderTab |
| **Fehlende Types** | 1 Paket | 🔴 Types in jeder Component dupliziert |

---

## 🔍 Detailed Component Analysis

### 1. ChatPanel.vue (473 LOC) ✅ **EXCELLENT**

**Verantwortung:** Chat UI mit Messages, Input, Quick Actions

#### Struktur
```vue
<script setup lang="ts">
// Props (7 properties)
const props = defineProps<{
  messages: ChatMessage[]
  isLoading: boolean
  quickActions: QuickAction[]
  actionsLoading: boolean
  selectedFileCount: number
  hasContext: boolean
  showQuickActions?: boolean
}>()

// Emits (4 events)
emit('send', message, mode)
emit('quick-action', action)
emit('update:modelValue', value)
emit('update:mode', value)

// Local State (4 refs)
const chatContainer = ref<HTMLElement>()
const inputField = ref<HTMLTextAreaElement>()
const localMessage = ref('')
const localMode = ref('')

// Methods (2)
function handleSend()
function scrollToBottom()
</script>
```

#### ✅ Stärken
1. **Klare API:** Props/Emits gut definiert
2. **v-model Support:** Für message und mode
3. **Auto-Scroll:** Watch-basiert, funktioniert
4. **Exposed Methods:** `focus()`, `scrollToBottom()` für Parent
5. **Typing Indicator:** Saubere Loading-UI
6. **Quick Actions Grid:** 2x2 Layout, context-aware

#### ⚠️ Potenzielle Optimierungen
1. **Types:** `ChatMessage`, `QuickAction` → eigenes File
2. **Scroll Logic:** Könnte in Composable (`useAutoScroll`)
3. **Keyboard Shortcuts:** Ctrl+Enter bereits implementiert ✅

**ISO Compliance:** ✅ PASS (< 500 LOC)
**Quality Rating:** ⭐⭐⭐⭐⭐ (9/10)
**Wartbarkeit:** Hoch
**Testbarkeit:** Hoch

---

### 2. MaterialsPanel.vue (356 LOC) ✅ **EXCELLENT**

**Verantwortung:** File Management mit Checkboxen, Upload, Preview

#### Struktur
```vue
<script setup lang="ts">
// Props (2)
const props = defineProps<{
  files: CourseFile[]
  selectedIds: string[]
}>()

// Emits (4)
emit('update:selectedIds', ids)
emit('upload')
emit('preview', file)
emit('clear-selection')

// Computed (2)
const allSelected = computed(...)
const someSelected = computed(...)

// Methods (4)
function toggleFile(fileId)
function toggleAll()
function getFileIcon(type): string
function formatFileSize(bytes): string
</script>
```

#### ✅ Stärken
1. **v-model Pattern:** `selectedIds` mit update emit
2. **Indeterminate Checkbox:** Für "Select All" State
3. **Utility Functions:** `getFileIcon`, `formatFileSize`
4. **Empty State:** Guter UX mit Upload-Button
5. **File Icons:** Emoji-basiert (PDF, DOC, XLS, etc.)

#### ⚠️ Potenzielle Optimierungen
1. **Types:** `CourseFile` → eigenes File
2. **Utilities:** `getFileIcon`, `formatFileSize` → `utils/files.ts`
3. **File Preview:** Emit-basiert ✅

**ISO Compliance:** ✅ PASS (< 500 LOC)
**Quality Rating:** ⭐⭐⭐⭐⭐ (9/10)
**Wartbarkeit:** Hoch
**Testbarkeit:** Sehr hoch (pure functions)

---

### 3. StructurePanel.vue (496 LOC) ✅ **GOOD**

**Verantwortung:** Kursstruktur Tree mit Drag & Drop

#### Struktur
```vue
<script setup lang="ts">
// Props (4)
const props = defineProps<{
  chapters: any[]
  selectedChapterId?: string
  selectedLessonId?: string
  sessionId?: string
}>()

// State (6 refs für Drag&Drop)
const expandedChapters = ref<Set<string>>(new Set())
const dragOverChapterId = ref<string | null>(null)
const dragOverLessonId = ref<string | null>(null)
const draggingType = ref<'chapter' | 'lesson' | null>(null)
const draggingFromIndex = ref<number>(-1)
const draggingFromChapterIndex = ref<number>(-1)

// Computed (1)
const stats = computed(() => ({
  chapters: chapters?.length || 0,
  lessons: chapters?.reduce((sum, ch) => sum + (ch.lessons?.length || 0), 0) || 0
}))

// Methods (11 - Drag & Drop heavy)
function toggleChapter(id)
function handleChapterDragStart(e, index)
function handleChapterDragOver(e, id)
function handleChapterDragLeave()
function handleChapterDrop(e, targetIndex)
function handleLessonDragStart(e, chapterIdx, lessonIdx)
function handleLessonDragOver(e, id)
function handleLessonDragLeave()
function handleLessonDrop(e, chapterIdx, lessonIdx)
function handleDragEnd()

// Exposed (4 methods)
defineExpose({
  expandChapter(id)
  collapseChapter(id)
  expandAll()
  collapseAll()
})
</script>
```

#### ✅ Stärken
1. **Drag & Drop:** Vollständig implementiert (Chapters + Lessons)
2. **Expand/Collapse:** Set-basierte State-Verwaltung
3. **Exposed API:** Parent kann Tree steuern
4. **Visual Feedback:** `drag-over` Classes

#### 🔴 **KRITISCHE Schwäche**
```typescript
function handleChapterDrop(e: DragEvent, targetIndex: number) {
  // ⚠️ PROBLEM: Mutiert lokales Array, aber kein Emit!
  const chapters = [...props.chapters]
  const [moved] = chapters.splice(fromIndex, 1)
  chapters.splice(targetIndex, 0, moved)
  // Note: Parent should handle the mutation via emit
  handleDragEnd()
}
```
**Problem:** Drag & Drop funktioniert visuell, aber **speichert nicht**!

#### ⚠️ Optimierungen erforderlich
1. **Drag & Drop Logic:** MUSS in Composable (`useDragDrop`)
2. **Emit Events:** `@reorder-chapter`, `@reorder-lesson` fehlen
3. **Types:** Chapter/Lesson Interfaces fehlen

**ISO Compliance:** ✅ PASS (< 500 LOC)
**Quality Rating:** ⭐⭐⭐⭐☆ (7/10) - Bug im Reordering
**Wartbarkeit:** Mittel
**Testbarkeit:** Schwierig (komplexe Drag&Drop Logik)

---

### 4. WorkflowPanel.vue (633 LOC) ⚠️ **OVER LIMIT**

**Verantwortung:** Context-Aware Workflow (3 Steps)

#### Struktur
```vue
<script setup lang="ts">
// Props (10!)
const props = defineProps<{
  context: SelectedContext | null
  theories: Theory[]
  explanations: Explanation[]
  lmSuggestions: LMSuggestion[]
  contextActions: ContextAction[]
  selectedFileCount: number
  isLoadingTheories: boolean
  isAnalyzing: boolean
  isGeneratingTheory: boolean
  isLoadingLMSuggestions: boolean
  // ... + mehr
}>()

// Emits (8!)
emit('close')
emit('analyze')
emit('generate-theory')
emit('open-theory', theory)
emit('open-explanation', expl)
emit('create-lm', lm)
emit('execute-action', action)

// Local State (1)
const selectedTheoryId = ref<string | null>(null)

// Methods (1 utility)
function formatDate(dateStr?: string): string

// Template Sections (3)
1. Analyze Section
2. Theory Section (Chapter vs Lesson conditional)
3. LM Suggestions Section (Lesson only)
</script>
```

#### ✅ Stärken
1. **Context-Aware:** Zeigt unterschiedliche UI für Chapter vs Lesson
2. **3-Step Workflow:** Logischer Ablauf (Analyze → Theory → LMs)
3. **Loading States:** Für alle Async-Operationen
4. **Empty States:** Guter UX

#### 🔴 **KRITISCHE Probleme**
1. **ÜBER LIMIT:** 633 LOC (126% vom Limit)
2. **Zu viele Props:** 10+ Props = Code Smell
3. **Zu viele Emits:** 8 Events
4. **Gemischte Concerns:** 3 unterschiedliche Workflows in 1 Component
5. **Types dupliziert:** 5 Interfaces lokal definiert

#### 🎯 **REFACTORING REQUIRED**

**Empfohlene Aufteilung:**
```
workflow/
├── WorkflowPanel.vue               (150 LOC) - Orchestrator
├── WorkflowStepAnalyze.vue         (120 LOC) - Step 1
├── WorkflowStepTheory.vue          (200 LOC) - Step 2
└── WorkflowStepLearningMethods.vue (160 LOC) - Step 3
```

**ISO Compliance:** ❌ FAIL (>500 LOC)
**Quality Rating:** ⭐⭐⭐☆☆ (6/10)
**Wartbarkeit:** Niedrig
**Testbarkeit:** Schwierig

---

### 5. ConfirmationPanel.vue (162 LOC) ✅ **EXCELLENT**

**Verantwortung:** AI-Content Confirmation Dialog

#### Struktur
```vue
<script setup lang="ts">
// Props (2)
const props = defineProps<{
  pendingAction: PendingAction | null
  isLoading?: boolean
}>()

// Emits (3)
emit('confirm')
emit('modify')
emit('reject')

// Template
- Header mit Icon + Titel
- Preview Section (scrollbar wenn groß)
- 3 Buttons (Confirm, Modify, Reject)
</script>
```

#### ✅ Stärken
1. **Einfach & Fokussiert:** Macht nur 1 Sache
2. **Gutes Design:** Gelber Gradient, visuell auffällig
3. **Loading States:** Buttons disabled wenn loading
4. **Conditional Rendering:** `v-if="pendingAction"`

#### ⚠️ Kleine Optimierung
1. **Types:** `PendingAction` → eigenes File

**ISO Compliance:** ✅ PASS (<500 LOC)
**Quality Rating:** ⭐⭐⭐⭐⭐ (10/10)
**Wartbarkeit:** Sehr hoch
**Testbarkeit:** Sehr hoch

---

## 📦 Fehlende Infrastruktur

### 1. Composables (ALLE fehlen!)

| Composable | Verantwortung | LOC Est. | Priority |
|------------|---------------|----------|----------|
| `useSessionManager.ts` | Session Create/Finalize/Load | 200 | 🔴 HIGH |
| `useChatManager.ts` | Message Send/Scroll | 180 | 🔴 HIGH |
| `useFileManagement.ts` | Upload/Delete/Select | 150 | 🟡 MEDIUM |
| `useDragDrop.ts` | Drag & Drop für Structure | 250 | 🔴 HIGH |
| `useTheoryManagement.ts` | Theory/Explanation CRUD | 200 | 🟡 MEDIUM |
| `useLearningMethodSuggestions.ts` | LM Suggestions Loading | 150 | 🟡 MEDIUM |

**Total:** ~1130 LOC in Composables (aktuell: 0 LOC)

---

### 2. Types Package (ALLE fehlen!)

**Aktuell:** Types in jeder Component dupliziert!

```
types/
├── index.ts                (30 LOC)   - Barrel export
├── session.types.ts        (40 LOC)   - Session, ChatMessage
├── course.types.ts         (60 LOC)   - Course, Chapter, Lesson
├── file.types.ts           (30 LOC)   - CourseFile
├── action.types.ts         (50 LOC)   - QuickAction, ContextAction, PendingAction
├── theory.types.ts         (40 LOC)   - Theory, Explanation
└── lm.types.ts             (30 LOC)   - LMSuggestion, LMType
```

**Total:** ~280 LOC (aktuell dupliziert in 5 Components)

---

## 🚨 Kritische Findings

### 1. **KursBuilderTab.vue nutzt Sub-Komponenten NICHT**

```vue
<!-- KursBuilderTab.vue (2945 LOC) - AKTUELL -->
<template>
  <div class="kurs-builder-tab">
    <!-- Alle 2945 Zeilen Inline-Code -->
    <!-- KEINE Sub-Component Imports! -->
  </div>
</template>
```

**Problem:** Sub-Komponenten sind extrahiert, aber **toter Code**!

---

### 2. **StructurePanel Drag&Drop speichert nicht**

```typescript
// StructurePanel.vue - Line 218
function handleChapterDrop(e: DragEvent, targetIndex: number) {
  const chapters = [...props.chapters]
  const [moved] = chapters.splice(fromIndex, 1)
  chapters.splice(targetIndex, 0, moved)
  // ⚠️ KEINE Emit! Parent weiß nichts von Änderung!
}
```

**Fix Required:** Emit `@reorder` Event

---

### 3. **WorkflowPanel ist 126% über Limit**

633 LOC / 500 LOC = **126%**

**Muss aufgeteilt werden in 4 Components!**

---

### 4. **Types Duplication**

Gleiche Interfaces in 5 Files:
- `ChatMessage` (ChatPanel, KursBuilderTab)
- `CourseFile` (MaterialsPanel, KursBuilderTab)
- `QuickAction` (ChatPanel, KursBuilderTab, WorkflowPanel)
- `Theory`, `Explanation` (WorkflowPanel, KursBuilderTab)

**Single Source of Truth fehlt!**

---

### 5. **Keine Composables**

Alle Business-Logik ist entweder:
- In KursBuilderTab.vue (2945 LOC) - NOCH NICHT EXTRAHIERT
- Oder in Components inline (Chat scroll, File toggle, etc.)

**Wiederverwendbarkeit: 0%**

---

## ✅ ISO/IEC 26515 Compliance Check

| Component | LOC | Limit | Status | Actions Required |
|-----------|-----|-------|--------|------------------|
| ChatPanel.vue | 473 | 500 | ✅ PASS | Minor: Extract types |
| MaterialsPanel.vue | 356 | 500 | ✅ PASS | Minor: Extract utils |
| StructurePanel.vue | 496 | 500 | ✅ PASS | Major: Fix drag&drop emit |
| WorkflowPanel.vue | 633 | 500 | ❌ FAIL | Major: Split into 4 components |
| ConfirmationPanel.vue | 162 | 500 | ✅ PASS | Minor: Extract types |
| **KursBuilderTab.vue** | **2945** | **500** | **❌ CRITICAL** | **Complete refactoring** |

---

## 🎯 Refactoring Plan (Phase A - Next Steps)

### Phase A1: Types Package (30 min)
✅ **Goal:** Single Source of Truth für alle Types

```bash
kurs-builder/types/
├── index.ts          # Export all
├── session.types.ts
├── course.types.ts
├── file.types.ts
├── action.types.ts
├── theory.types.ts
└── lm.types.ts
```

**Deliverable:** Alle Components importieren von `@/types`

---

### Phase A2: Composables erstellen (4h)

#### A2.1 - useSessionManager.ts (1h)
```typescript
export function useSessionManager(courseId: Ref<string>) {
  const session = ref<Session | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function createSession() { ... }
  async function finalizeSession() { ... }
  async function loadSession() { ... }

  return { session, loading, error, createSession, finalizeSession, loadSession }
}
```

#### A2.2 - useChatManager.ts (1h)
```typescript
export function useChatManager(sessionId: Ref<string>) {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  async function sendMessage(content: string, mode: string) { ... }
  function scrollToBottom() { ... }

  return { messages, loading, sendMessage, scrollToBottom }
}
```

#### A2.3 - useDragDrop.ts (1.5h)
```typescript
export function useDragDrop<T>(
  items: Ref<T[]>,
  onReorder: (newOrder: T[]) => void
) {
  const dragState = ref({ ... })

  function handleDragStart(index: number) { ... }
  function handleDrop(targetIndex: number) { ... }

  return { dragState, handleDragStart, handleDrop }
}
```

#### A2.4 - useFileManagement.ts (30min)
```typescript
export function useFileManagement(sessionId: Ref<string>) {
  const files = ref<CourseFile[]>([])
  const selectedIds = ref<string[]>([])

  async function uploadFile(file: File) { ... }
  async function deleteFile(id: string) { ... }
  function toggleSelection(id: string) { ... }

  return { files, selectedIds, uploadFile, deleteFile, toggleSelection }
}
```

---

### Phase A3: WorkflowPanel splitten (2h)

```
workflow/
├── WorkflowPanel.vue               (150 LOC)
│   └── Orchestrator - Props/Emits weiterleiten
├── WorkflowStepAnalyze.vue         (120 LOC)
│   └── Step 1 - Analyze Button + Hint
├── WorkflowStepTheory.vue          (200 LOC)
│   └── Step 2 - Theories/Explanations List
└── WorkflowStepLearningMethods.vue (160 LOC)
    └── Step 3 - LM Suggestions Grid
```

---

### Phase A4: KursBuilderTab.vue integrieren (2h)

**Von:**
```vue
<!-- 2945 LOC Monolith -->
<template>
  <div class="kurs-builder-tab">
    <!-- Alles inline -->
  </div>
</template>
```

**Zu:**
```vue
<!-- 250 LOC Orchestrator -->
<template>
  <div class="kurs-builder-tab">
    <BuilderHeader :course="course" :session="session" />

    <div class="builder-content">
      <ChatPanel
        :messages="messages"
        :loading="chatLoading"
        @send="handleSend"
      />

      <div class="right-column">
        <StructurePanel :chapters="chapters" />
        <MaterialsPanel :files="files" />
      </div>
    </div>

    <WorkflowPanel
      v-if="selectedContext"
      :context="selectedContext"
      @close="clearContext"
    />
  </div>
</template>

<script setup lang="ts">
import { ChatPanel, StructurePanel, MaterialsPanel, WorkflowPanel } from './kurs-builder'
import { useSessionManager, useChatManager } from './kurs-builder/composables'

const sessionMgr = useSessionManager(props.courseId)
const chatMgr = useChatManager(sessionMgr.session)

// Nur Koordination!
</script>
```

---

## 📈 Expected Results

### Before
| Metrik | Wert |
|--------|------|
| **Größte Datei** | 2945 LOC |
| **Composables** | 0 |
| **Type Duplication** | 5x |
| **Sub-Components genutzt** | 0% |
| **ISO Compliance** | ❌ FAIL |

### After (Phase A Complete)
| Metrik | Wert | Verbesserung |
|--------|------|--------------|
| **Größte Datei** | 400 LOC | **-86%** |
| **Composables** | 6 | ✅ |
| **Type Duplication** | 0 | **-100%** |
| **Sub-Components genutzt** | 100% | **+100%** |
| **ISO Compliance** | ✅ PASS | ✅ |

---

## 🏆 Summary & Recommendation

### ✅ Good News
1. **Sub-Komponenten existieren** - 5 von 6 sind brauchbar
2. **Struktur ist gut** - ChatPanel, MaterialsPanel perfekt
3. **Nur 2 Probleme:**
   - StructurePanel: Drag&Drop emit fehlt
   - WorkflowPanel: Zu groß, muss gesplittet werden

### 🔴 Critical Issues
1. **KursBuilderTab.vue nutzt sie nicht** - 2945 LOC Monolith bleibt
2. **Keine Composables** - Logic nicht extrahiert
3. **Types dupliziert** - In 5+ Files

### 🎯 Recommended Next Steps

**PRIORITÄT 1 (Heute - 2h):**
1. Types Package erstellen (30min)
2. useSessionManager Composable (1h)
3. useChatManager Composable (30min)

**PRIORITÄT 2 (Morgen - 3h):**
4. useDragDrop Composable + Fix StructurePanel (1.5h)
5. WorkflowPanel splitten (1.5h)

**PRIORITÄT 3 (Übermorgen - 2h):**
6. KursBuilderTab.vue umbauen auf Sub-Components (2h)

**Total:** 7 Stunden über 3 Tage

---

## 🚀 Ready to Start?

Du hast 2 Optionen:

### Option 1: Sofort mit Phase A1 starten
Ich erstelle jetzt das Types Package (30 min).

### Option 2: Erst WorkflowPanel optimieren
Wir splitten WorkflowPanel in 4 Components (2h).

**Was möchtest du zuerst angehen?**

---

**Status:** ✅ Analyse COMPLETE
**Bereit für:** Implementation Phase A
**Geschätzter Aufwand:** 7 Stunden
**ISO Compliance nach Abschluss:** ✅ FULL PASS
