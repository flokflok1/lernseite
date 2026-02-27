# AI Editor Production Readiness — BLOCKER + HIGH Priority Fixes

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 8 critical issues (4 BLOCKER + 4 HIGH) that prevent the AI Editor from being production-ready.

**Architecture:** The AI Editor lives at `frontend/src/presentation/components/panel/editor/ai/unified/`. It uses a tab-based UI orchestrated by `UnifiedAIEditor.vue`, with composables in `composables/` providing state. Backend AI editor endpoints are in `backend/app/api/v1/panel/editor/ai/`. Fixes span both frontend composables/components and backend route decorators.

**Tech Stack:** Vue 3 Composition API, TypeScript, Flask, Python `@permission_required` decorator

---

### Task 1: Fix backend auth — wrong permission on all AI editor endpoints

All 14 AI editor endpoints use `@permission_required('admin.system:read')` which is an **admin-only** permission. Editors (content creators) cannot access the AI Editor at all. The correct permission is `content.courses:write` (used by other editor endpoints in `panel/editor/shared/`).

**Files:**
- Modify: `backend/app/api/v1/panel/editor/ai/skills.py` (lines 20, 39, 56, 93, 119)
- Modify: `backend/app/api/v1/panel/editor/ai/plans.py` (lines 20, 57, 78, 95, 117, 134)
- Modify: `backend/app/api/v1/panel/editor/ai/actions.py` (lines 29, 65, 117)

**Step 1: Replace permissions in skills.py**

In `backend/app/api/v1/panel/editor/ai/skills.py`, replace all 5 occurrences:
```python
# OLD (on lines 20, 39, 56, 93, 119):
@permission_required('admin.system:read')

# NEW:
@permission_required('content.courses:write')
```

**Step 2: Replace permissions in plans.py**

In `backend/app/api/v1/panel/editor/ai/plans.py`, replace all 6 occurrences:
```python
# OLD (on lines 20, 57, 78, 95, 117, 134):
@permission_required('admin.system:read')

# NEW:
@permission_required('content.courses:write')
```

**Step 3: Replace permissions in actions.py**

In `backend/app/api/v1/panel/editor/ai/actions.py`, replace all 3 occurrences:
```python
# OLD (on lines 29, 65, 117):
@permission_required('admin.system:read')

# NEW:
@permission_required('content.courses:write')
```

**Step 4: Verify backend starts without errors**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`
Expected: No import errors

**Step 5: Commit**

```bash
git add backend/app/api/v1/panel/editor/ai/skills.py backend/app/api/v1/panel/editor/ai/plans.py backend/app/api/v1/panel/editor/ai/actions.py
git commit -m "fix(auth): use content.courses:write for AI editor endpoints

All 14 AI editor endpoints incorrectly used admin.system:read,
blocking non-admin editors from accessing the AI Editor."
```

---

### Task 2: Fix event signature mismatch — RightPanel emits positional args, handler expects object

`RightPanel.vue:16` emits `selectContext` with 3 positional args: `(type, id, title)`.
`UnifiedAIEditor.vue:91` passes it to `handleSelectContext` which expects a single object: `{ type, id, title }`.
This causes the structure sidebar's "select context" click to silently fail.

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue` (line 91, line 219)

**Step 1: Fix the event handler binding**

In `UnifiedAIEditor.vue`, change line 91 from:
```vue
@select-context="handleSelectContext"
```
to:
```vue
@select-context="(type, id, title) => handleSelectContext({ type, id, title })"
```

This wraps the 3 positional args into the object that `handleSelectContext` expects at line 219.

**Step 2: Verify build passes**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue
git commit -m "fix(ai-editor): align selectContext event signature

RightPanel emits 3 positional args but handler expected single object.
Wrap args into object at the binding site."
```

---

### Task 3: Fix acceptResult no-op — skill results are never persisted

`useSkillExecution.ts:100-103` — `acceptResult()` only clears local state (`currentResult`, `selectedSkill`). It never persists the generated content to the course. The function needs to return the result before clearing so the caller can persist it.

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useSkillExecution.ts` (lines 100-103)
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue` (line 247-249)

**Step 1: Make acceptResult return the result before clearing**

In `useSkillExecution.ts`, replace lines 100-103:
```typescript
// OLD:
function acceptResult() {
  currentResult.value = null
  selectedSkill.value = null
}
```
with:
```typescript
function acceptResult(): GenerationResult | null {
  const result = currentResult.value
  currentResult.value = null
  selectedSkill.value = null
  return result
}
```

**Step 2: Wire up history tracking in UnifiedAIEditor**

In `UnifiedAIEditor.vue`, the `handleAcceptResult` function (around line 247) currently does:
```typescript
function handleAcceptResult(): void {
  workflowPhase.acceptResult()
  chatSession.addSystemMessage(t('aiEditor.result.accepted'))
}
```

This needs access to `generationHistory.addEntry()`. However, `workflowPhase` wraps skill execution. Since the skill execution composable is used inside `useWorkflowPhase`, we need to check how `workflowPhase.acceptResult()` delegates. For now, the fix is to ensure that whenever skill execution's `acceptResult` is called, the result gets added to history.

The simplest fix: in `useSkillExecution.ts`, add a callback parameter or have the caller handle it. Since `UnifiedAIEditor` already has `generationHistory`, update `handleAcceptResult`:

```typescript
function handleAcceptResult(): void {
  // acceptResult now returns the result before clearing
  const result = workflowPhase.acceptResult()
  if (result) {
    generationHistory.addEntry({
      id: `gen-${Date.now()}`,
      skill_code: result.skill_code || 'unknown',
      course_id: selectedCourseId.value,
      status: 'accepted',
      tokens_input: result.tokens_input || 0,
      tokens_output: result.tokens_output || 0,
      content_preview: typeof result.content === 'string'
        ? result.content.slice(0, 200)
        : JSON.stringify(result.content).slice(0, 200),
      created_at: new Date().toISOString(),
    })
  }
  chatSession.addSystemMessage(t('aiEditor.result.accepted'))
}
```

**Note:** This requires `workflowPhase.acceptResult()` to also propagate the return value from `useSkillExecution.acceptResult()`. Check `useWorkflowPhase.ts` to see if it has its own `acceptResult` wrapper and update it to return the value.

**Step 3: Verify build passes**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/useSkillExecution.ts frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue
git commit -m "fix(ai-editor): persist accepted skill results to history

acceptResult() was a no-op that only cleared state. Now returns the
result so the caller can persist it to generation history."
```

---

### Task 4: Fix PromptsTab missing KeepAlive wrapper

In `UnifiedAIEditor.vue:70`, PromptsTab is the only tab **without** a `<KeepAlive>` wrapper. This means switching away and back destroys all state (loaded templates, search filters, edit progress).

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue` (line 70)

**Step 1: Add KeepAlive wrapper**

Change line 70 from:
```vue
<PromptsTab v-if="editorState.activeTab.value === 'prompts'" />
```
to:
```vue
<KeepAlive>
  <PromptsTab v-if="editorState.activeTab.value === 'prompts'" />
</KeepAlive>
```

**Step 2: Verify build passes**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`

**Step 3: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue
git commit -m "fix(ai-editor): add KeepAlive to PromptsTab

PromptsTab was the only tab without KeepAlive, causing state loss
when switching tabs."
```

---

### Task 5: Fix 8x silent error swallowing (G08 violations)

Quality Gate G08 forbids silent exception swallowing. These catch blocks silently discard errors, making debugging impossible.

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useGenerationHistory.ts` (line 32-34)
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useFileUpload.ts` (line 47-49, line 121-122)
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useStructureView.ts` (line 102-103, line 125-128)
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/tabs/CourseTab.vue` (line 257)
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue` (line 156-158)

**Step 1: Fix useGenerationHistory.ts — loadHistory catch**

Replace lines 32-34:
```typescript
// OLD:
} catch {
  // Silently handle — table may not exist yet in dev
  entries.value = []
}
```
with:
```typescript
} catch (e: unknown) {
  console.warn('[GenerationHistory] Failed to load history:', e)
  entries.value = []
}
```

**Step 2: Fix useFileUpload.ts — loadFiles catch (line 47-49)**

Replace:
```typescript
// OLD:
} catch {
  // Silently handle — endpoint may not be available yet
  files.value = []
}
```
with:
```typescript
} catch (e: unknown) {
  console.warn('[FileUpload] Failed to load files:', e)
  files.value = []
}
```

**Step 3: Fix useFileUpload.ts — loadPreview catch (line 121-122)**

Replace:
```typescript
// OLD:
} catch {
  previewText.value = null
}
```
with:
```typescript
} catch (e: unknown) {
  console.warn('[FileUpload] Failed to load preview:', e)
  previewText.value = null
}
```

**Step 4: Fix useStructureView.ts — getLessonsForEdit catch (line 102-103)**

Replace:
```typescript
// OLD:
} catch {
  lessons = []
}
```
with:
```typescript
} catch (e: unknown) {
  console.warn('[StructureView] Failed to load lessons for chapter', ch.chapter_id, e)
  lessons = []
}
```

**Step 5: Fix useStructureView.ts — loadCourseStructure catch (line 125-128)**

Replace:
```typescript
// OLD:
} catch {
  // Course may have no chapters yet — not an error
  draftStructure.value = null
}
```
with:
```typescript
} catch (e: unknown) {
  console.warn('[StructureView] Failed to load course structure:', e)
  draftStructure.value = null
}
```

**Step 6: Fix CourseTab.vue — save() catch (line ~257)**

Find the empty catch in the `save()` function and add error feedback. This one is user-facing (auto-save failure), so also set an error state:

```typescript
// OLD:
} catch {
}
```
Replace with:
```typescript
} catch (e: unknown) {
  console.warn('[CourseTab] Failed to save course:', e)
  error.value = t('aiEditor.course.saveFailed') || 'Save failed'
}
```

Also add the i18n key `aiEditor.course.saveFailed` in all 3 locale files (Task 8).

**Step 7: Fix UnifiedAIEditor.vue — onMounted catch (line ~156-158)**

Find the silent catch in `onMounted`:
```typescript
// OLD (inside onMounted):
} catch {
  // Course loading failed silently
}
```
Replace with:
```typescript
} catch (e: unknown) {
  console.warn('[AIEditor] Failed to load courses on mount:', e)
}
```

**Step 8: Verify build passes**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`

**Step 9: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/useGenerationHistory.ts frontend/src/presentation/components/panel/editor/ai/unified/composables/useFileUpload.ts frontend/src/presentation/components/panel/editor/ai/unified/composables/useStructureView.ts frontend/src/presentation/components/panel/editor/ai/unified/tabs/CourseTab.vue frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue
git commit -m "fix(ai-editor): add console.warn to 8 silent catch blocks (G08)

Silent error swallowing made debugging impossible. All catch blocks
now log warnings while preserving graceful degradation."
```

---

### Task 6: Fix raw JSON result display in SkillExecutionPanel

`SkillExecutionPanel.vue:138` displays skill results as `JSON.stringify(result.content, null, 2)` in a `<pre>` tag. This is unreadable for users. Replace with formatted content display.

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/panels/SkillExecutionPanel.vue` (line 138)

**Step 1: Add smart content rendering**

Replace line 138:
```vue
<!-- OLD: -->
<pre class="result-content">{{ JSON.stringify(result.content, null, 2) }}</pre>
```
with:
```vue
<div class="result-content" v-if="typeof result.content === 'string'" v-html="sanitizeHtml(result.content)" />
<div class="result-content" v-else>
  <div v-for="(value, key) in result.content" :key="String(key)" class="result-field">
    <span class="result-field-key">{{ key }}:</span>
    <span class="result-field-value">{{ typeof value === 'string' ? value : JSON.stringify(value) }}</span>
  </div>
</div>
```

**Step 2: Add DOMPurify import and sanitize function**

Add to `<script setup>`:
```typescript
import DOMPurify from 'dompurify'

function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'code', 'pre'],
    ALLOWED_ATTR: []
  })
}
```

**Step 3: Add CSS for result fields**

```css
.result-field {
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--color-border);
}
.result-field:last-child { border-bottom: none; }
.result-field-key {
  font-weight: 600;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  margin-right: 0.5rem;
}
.result-field-value {
  font-size: 0.75rem;
  color: var(--color-text-primary);
}
```

**Step 4: Verify build passes**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`

**Step 5: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/panels/SkillExecutionPanel.vue
git commit -m "fix(ai-editor): render skill results as formatted content

Replaced raw JSON.stringify display with DOMPurify-sanitized HTML
for string content and key-value display for object content."
```

---

### Task 7: Replace hardcoded token budget with configurable value

`useChatSession.ts:20` hardcodes `tokenBudget` to `100_000`. This should come from the backend or at least be configurable per course/organization.

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useChatSession.ts` (line 20)

**Step 1: Accept token budget as parameter with fallback**

Change the composable to accept an optional config:
```typescript
// OLD (line 20):
const tokenBudget = ref(100_000)
```

Add a `loadSessionConfig` approach — but since this is a HIGH (not BLOCKER) and we don't have a backend endpoint for org config yet, the minimal fix is to make it a named constant at the top of the file:

```typescript
// At top of file, after imports:
/** Default token budget per session. TODO: Load from org/course settings via API. */
const DEFAULT_TOKEN_BUDGET = 100_000

// Then line 20:
const tokenBudget = ref(DEFAULT_TOKEN_BUDGET)
```

This extracts the magic number (G08-adjacent) and documents the TODO for backend integration.

**Step 2: Verify build passes**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`

**Step 3: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/useChatSession.ts
git commit -m "refactor(ai-editor): extract token budget to named constant

Replaced magic number 100_000 with DEFAULT_TOKEN_BUDGET constant.
TODO: Load from backend org/course settings."
```

---

### Task 8: Add missing i18n key for course save failure

Task 5 Step 6 adds a reference to `aiEditor.course.saveFailed` which doesn't exist yet.

**Files:**
- Modify: `frontend/src/infrastructure/i18n/locales/de/panel/aiEditor/unified.json`
- Modify: `frontend/src/infrastructure/i18n/locales/en/panel/aiEditor/unified.json`
- Modify: `frontend/src/infrastructure/i18n/locales/pl/panel/aiEditor/unified.json`

**Step 1: Add saveFailed key to DE**

In `de/panel/aiEditor/unified.json`, inside `aiEditor.course`, add:
```json
"saveFailed": "Speichern fehlgeschlagen"
```

**Step 2: Add saveFailed key to EN**

In `en/panel/aiEditor/unified.json`, inside `aiEditor.course`, add:
```json
"saveFailed": "Save failed"
```

**Step 3: Add saveFailed key to PL**

In `pl/panel/aiEditor/unified.json`, inside `aiEditor.course`, add:
```json
"saveFailed": "Zapisywanie nie powiodlo sie"
```

**Step 4: Commit**

```bash
git add frontend/src/infrastructure/i18n/locales/de/panel/aiEditor/unified.json frontend/src/infrastructure/i18n/locales/en/panel/aiEditor/unified.json frontend/src/infrastructure/i18n/locales/pl/panel/aiEditor/unified.json
git commit -m "feat(i18n): add saveFailed key for AI editor course tab"
```

---

## Verification

After all tasks:

1. `cd /home/pascal/Lernsystem/frontend && npm run build` — No TypeScript/build errors
2. Backend starts: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`
3. AI Editor loads for editor-role users (not just admins)
4. Structure sidebar → click chapter/lesson → context set correctly (no silent fail)
5. Skills tab → execute skill → accept → result appears in History tab
6. All catch blocks produce console.warn output in DevTools
7. Skill results display formatted content, not raw JSON
8. PromptsTab retains state when switching tabs

---

## Issue Summary

| # | Severity | Issue | Task |
|---|----------|-------|------|
| 1 | BLOCKER | Wrong auth permission on 14 endpoints | Task 1 |
| 2 | BLOCKER | Event signature mismatch (selectContext) | Task 2 |
| 3 | BLOCKER | acceptResult is no-op (no persistence) | Task 3 |
| 4 | HIGH | PromptsTab missing KeepAlive | Task 4 |
| 5 | HIGH | 8x silent error swallowing (G08) | Task 5 |
| 6 | HIGH | Raw JSON display for results | Task 6 |
| 7 | HIGH | Hardcoded token budget 100K | Task 7 |
| 8 | HIGH | Missing i18n key (saveFailed) | Task 8 |
