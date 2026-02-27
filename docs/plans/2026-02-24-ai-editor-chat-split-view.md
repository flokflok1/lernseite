# AI Editor: Chat-First Split-View Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the Unified AI Editor from a tab-based layout into a split-view where a persistent AI chat (left) drives course creation, and a context-dependent panel (right) shows live course structure, generation progress, or results.

**Architecture:** The chat is always visible (left 40-50%). Users create courses by chatting with the AI, optionally uploading materials. The AI builds the course structure, generates content (theory, flashcards, quizzes), and asks for confirmation before executing. The right panel switches automatically between Structure (default), Progress (during generation), and Result (for review) views based on workflow phase. Three consolidated composables (`useChatSession`, `useStructureView`, `useWorkflowPhase`) replace the current 6-composable tab-based system. The existing `courseAuthoring.api.ts` (session/chat endpoints) and `unified.api.ts` (plan/skill endpoints) provide the API layer.

**Tech Stack:** Vue 3 Composition API, TypeScript, Pinia, existing Flask backend (CourseAuthoringService + SkillExecutionService), psycopg3, AIAdapter (Claude)

**Design Doc:** `docs/plans/2026-02-24-ai-editor-chat-split-view-design.md`

---

## Existing Code Reference

### What we're building ON TOP OF (reuse, don't rewrite):

| Existing File | LOC | Reuse Strategy |
|---|---|---|
| `unified/types/plan.types.ts` | 54 | Keep as-is (ContentPlan, PlanPhase, PlanStep) |
| `unified/types/skill.types.ts` | 53 | Keep as-is (SkillConfig, SkillParameter) |
| `unified/types/generation.types.ts` | 49 | Keep as-is (GenerationResult, BatchProgress) |
| `unified/types/prompt.types.ts` | 35 | Keep as-is (PromptPreset, PROMPT_PRESETS) |
| `unified/composables/useGenerationHistory.ts` | 65 | Keep as-is |
| `unified/composables/useTokenBudget.ts` | 42 | Keep as-is |
| `unified/panels/GenerationResultPanel.vue` | 87 | Adapt patterns for ResultView |
| `unified/panels/BatchProgressPanel.vue` | 84 | Adapt patterns for ProgressView |
| `authoring/courseAuthoring.api.ts` | 155 | Use for session/chat API calls |
| `unified/unified.api.ts` | 99 | Use for plan/skill API calls |
| Backend: all `/course-editor/ai/` endpoints | — | No changes needed |

### What we're REPLACING:

| File | Why |
|---|---|
| `UnifiedAIEditor.vue` (145 LOC) | Tab-based layout → split-view |
| `unified/composables/useEditorState.ts` (135 LOC) | Merged into useChatSession |
| `unified/composables/usePlanMode.ts` (196 LOC) | Merged into useWorkflowPhase |
| `unified/composables/useSkillExecution.ts` (126 LOC) | Merged into useWorkflowPhase |
| `unified/composables/usePromptBuilder.ts` (96 LOC) | Merged into useChatSession |
| `unified/tabs/PlanTab.vue` (76 LOC) | Replaced by StructureView |
| `unified/tabs/SkillsTab.vue` (61 LOC) | Skills accessible via chat |
| `unified/panels/PlanModePanel.vue` (173 LOC) | Replaced by StructureView |
| `unified/panels/SkillCatalogPanel.vue` (123 LOC) | Optional, accessible from chat |
| `unified/panels/SkillExecutionPanel.vue` (165 LOC) | Replaced by chat + right panel |
| `unified/panels/PromptBuilderPanel.vue` (86 LOC) | Replaced by chat input |

### Key API Endpoints (all exist, no backend changes needed):

| Endpoint | Purpose |
|---|---|
| `POST /course-editor/ai/sessions` | Create authoring session |
| `GET /course-editor/ai/sessions/:id` | Load session (includes chat history + draft) |
| `POST /course-editor/ai/sessions/:id/chat` | Send chat message |
| `POST /course-editor/ai/sessions/:id/finalize` | Finalize draft to real entities |
| `DELETE /course-editor/ai/sessions/:id` | Archive session |
| `GET /course-editor/ai/courses/:courseId/sessions` | List sessions |
| `GET /course-editor/ai/method-types` | Available LM types |
| `GET /course-editor/ai/skills` | Skill catalog |
| `POST /course-editor/ai/skills/execute` | Execute a skill |

---

## Task 1: New Type Definitions

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/types/chat.types.ts`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/types/structure.types.ts`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/types/workflow.types.ts`
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/types/index.ts`

**Step 1: Create `chat.types.ts`**

```typescript
// chat.types.ts — Types for the persistent chat panel

export type MessageRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  timestamp: string
  /** File IDs attached to this message */
  fileIds?: string[]
  /** If AI applied operations (add_chapter, etc.) */
  operations?: ChatOperation[]
  /** Inline confirmation buttons from AI */
  confirmation?: ChatConfirmation
  /** Loading state for streaming */
  isStreaming?: boolean
}

export interface ChatOperation {
  type: string
  target_type?: string
  target_id?: string
  label: string
}

export interface ChatConfirmation {
  action: string
  label: string
  skillCode?: string
  targetId?: string
  params?: Record<string, unknown>
}

export interface ChatSession {
  sessionId: string
  courseId: string
  status: 'active' | 'completed' | 'archived'
  metadata?: Record<string, unknown>
  createdAt: string
  updatedAt: string
}

export interface FileContext {
  fileId: string
  fileName: string
  fileType: string
  selected: boolean
}
```

**Step 2: Create `structure.types.ts`**

```typescript
// structure.types.ts — Types for the right-panel structure view

export interface DraftStructure {
  courseId: string
  courseTitle: string
  chapters: DraftChapter[]
}

export interface DraftChapter {
  id: string
  title: string
  order: number
  lessons: DraftLesson[]
}

export interface DraftLesson {
  id: string
  title: string
  order: number
  contentIndicators: ContentIndicator[]
}

export interface ContentIndicator {
  type: 'theory' | 'flashcards' | 'quiz' | 'exercise' | 'method'
  label: string
  count?: number
  status: 'empty' | 'draft' | 'generated' | 'accepted'
}

export interface SelectedContext {
  type: 'chapter' | 'lesson'
  id: string
  title: string
}
```

**Step 3: Create `workflow.types.ts`**

```typescript
// workflow.types.ts — Types for workflow phase tracking

export type WorkflowPhase = 'plan' | 'generate' | 'accept'

export interface GenerateProgress {
  current: number
  total: number
  label: string
  percent: number
  skillCode?: string
}

export interface GenerateResult {
  generationId: string
  skillCode: string
  content: Record<string, unknown>
  tokensInput: number
  tokensOutput: number
  modelName: string
  targetType?: string
  targetId?: string
  targetTitle?: string
}
```

**Step 4: Update `index.ts` barrel export**

Add to the existing exports:
```typescript
export * from './chat.types'
export * from './structure.types'
export * from './workflow.types'
```

**Step 5: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS (types are just declarations, no runtime impact)

**Step 6: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/types/
git commit -m "feat(ai-editor): add chat, structure, and workflow type definitions

Types for the chat-first split-view redesign: ChatMessage, ChatSession,
DraftStructure, SelectedContext, WorkflowPhase, GenerateProgress, GenerateResult."
```

---

## Task 2: `useChatSession` Composable

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useChatSession.ts`
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/index.ts`

This composable merges session management + chat + token tracking + file context. It wraps the existing `courseAuthoring.api.ts` endpoints.

**Step 1: Create `useChatSession.ts`**

```typescript
import { ref, computed, type Ref } from 'vue'
import type { ChatMessage, ChatSession, FileContext } from '../types'
import {
  createSession as apiCreateSession,
  getSession as apiGetSession,
  sendChatMessage as apiSendChat,
  finalizeSession as apiFinalizeSession,
  listSessions as apiListSessions,
  archiveSession as apiArchiveSession,
} from '@/infrastructure/api/clients/panel/editor/authoring/courseAuthoring.api'

export function useChatSession() {
  // ---- State ----
  const session = ref<ChatSession | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const isCreatingSession = ref(false)
  const error = ref<string | null>(null)

  // Token tracking
  const tokensUsed = ref(0)
  const tokenBudget = ref(100_000)

  // File context
  const selectedFileIds = ref<string[]>([])

  // Course selection
  const courseId = ref<string | null>(null)
  const courseTitle = ref('')

  // ---- Computed ----
  const hasSession = computed(() => session.value !== null)
  const tokensRemaining = computed(() => Math.max(0, tokenBudget.value - tokensUsed.value))
  const usagePercent = computed(() =>
    tokenBudget.value > 0 ? Math.round((tokensUsed.value / tokenBudget.value) * 100) : 0
  )
  const isOverBudget = computed(() => tokensUsed.value >= tokenBudget.value)

  // ---- Actions ----

  async function createSession(forCourseId?: string): Promise<void> {
    const cId = forCourseId || courseId.value
    if (!cId) {
      error.value = 'No course selected'
      return
    }
    isCreatingSession.value = true
    error.value = null
    try {
      const response = await apiCreateSession(cId)
      session.value = {
        sessionId: response.session_id || response.id,
        courseId: cId,
        status: 'active',
        metadata: response.metadata,
        createdAt: response.created_at || new Date().toISOString(),
        updatedAt: response.updated_at || new Date().toISOString(),
      }
      courseId.value = cId
      messages.value = []
      tokensUsed.value = 0
    } catch (err: any) {
      error.value = err?.message || 'Failed to create session'
    } finally {
      isCreatingSession.value = false
    }
  }

  async function loadSession(sessionId: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiGetSession(sessionId)
      session.value = {
        sessionId: response.session_id || response.id,
        courseId: response.course_id,
        status: response.status || 'active',
        metadata: response.metadata,
        createdAt: response.created_at,
        updatedAt: response.updated_at,
      }
      courseId.value = response.course_id
      // Load chat history if present
      if (response.chat_history && Array.isArray(response.chat_history)) {
        messages.value = response.chat_history.map((msg: any, idx: number) => ({
          id: msg.id || `msg-${idx}`,
          role: msg.role || 'assistant',
          content: msg.content || '',
          timestamp: msg.timestamp || msg.created_at || new Date().toISOString(),
          operations: msg.operations,
          fileIds: msg.file_ids,
        }))
      }
    } catch (err: any) {
      error.value = err?.message || 'Failed to load session'
    } finally {
      isLoading.value = false
    }
  }

  async function loadOrCreateSession(forCourseId: string): Promise<void> {
    courseId.value = forCourseId
    error.value = null
    isLoading.value = true
    try {
      // Try to find existing active session
      const sessions = await apiListSessions(forCourseId, 'active')
      if (sessions && Array.isArray(sessions) && sessions.length > 0) {
        await loadSession(sessions[0].session_id || sessions[0].id)
        return
      }
      // No active session — create new
      await createSession(forCourseId)
    } catch {
      // If list fails, just create new
      await createSession(forCourseId)
    } finally {
      isLoading.value = false
    }
  }

  async function sendMessage(content: string, fileIds?: string[]): Promise<ChatMessage | null> {
    if (!session.value) {
      error.value = 'No active session'
      return null
    }
    isLoading.value = true
    error.value = null

    // Add user message immediately
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      fileIds: fileIds || selectedFileIds.value.length > 0 ? [...selectedFileIds.value] : undefined,
    }
    messages.value.push(userMsg)

    try {
      const response = await apiSendChat(session.value.sessionId, content, {
        file_ids: fileIds || selectedFileIds.value,
      })

      // Add AI response
      const aiMsg: ChatMessage = {
        id: response.message_id || `msg-${Date.now()}-ai`,
        role: 'assistant',
        content: response.response || response.content || '',
        timestamp: new Date().toISOString(),
        operations: response.operations,
      }
      messages.value.push(aiMsg)

      // Track tokens
      if (response.tokens_used) {
        tokensUsed.value += response.tokens_used
      }

      return aiMsg
    } catch (err: any) {
      error.value = err?.message || 'Failed to send message'
      // Add error message
      messages.value.push({
        id: `msg-${Date.now()}-err`,
        role: 'system',
        content: `Error: ${error.value}`,
        timestamp: new Date().toISOString(),
      })
      return null
    } finally {
      isLoading.value = false
    }
  }

  function addSystemMessage(content: string): void {
    messages.value.push({
      id: `msg-${Date.now()}-sys`,
      role: 'system',
      content,
      timestamp: new Date().toISOString(),
    })
  }

  function toggleFileSelection(fileId: string): void {
    const idx = selectedFileIds.value.indexOf(fileId)
    if (idx >= 0) {
      selectedFileIds.value.splice(idx, 1)
    } else {
      selectedFileIds.value.push(fileId)
    }
  }

  function clearSession(): void {
    session.value = null
    messages.value = []
    tokensUsed.value = 0
    selectedFileIds.value = []
    error.value = null
  }

  return {
    // State
    session,
    messages,
    isLoading,
    isCreatingSession,
    error,
    courseId,
    courseTitle,
    tokensUsed,
    tokenBudget,
    selectedFileIds,

    // Computed
    hasSession,
    tokensRemaining,
    usagePercent,
    isOverBudget,

    // Actions
    createSession,
    loadSession,
    loadOrCreateSession,
    sendMessage,
    addSystemMessage,
    toggleFileSelection,
    clearSession,
  }
}
```

**Step 2: Update `index.ts` barrel**

Add: `export { useChatSession } from './useChatSession'`

**Step 3: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS

**Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/useChatSession.ts
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/index.ts
git commit -m "feat(ai-editor): add useChatSession composable

Consolidates session management, chat messaging, token tracking, and file context
into a single composable. Wraps courseAuthoring.api.ts endpoints."
```

---

## Task 3: `useStructureView` Composable

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useStructureView.ts`
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/index.ts`

**Step 1: Create `useStructureView.ts`**

```typescript
import { ref, computed } from 'vue'
import type { DraftStructure, DraftChapter, SelectedContext } from '../types'

export function useStructureView() {
  // ---- State ----
  const draftStructure = ref<DraftStructure | null>(null)
  const selectedContext = ref<SelectedContext | null>(null)
  const expandedNodes = ref<Set<string>>(new Set())
  const isFinalizing = ref(false)
  const error = ref<string | null>(null)

  // ---- Computed ----
  const hasStructure = computed(() =>
    draftStructure.value !== null && draftStructure.value.chapters.length > 0
  )

  const chapterCount = computed(() => draftStructure.value?.chapters.length ?? 0)

  const lessonCount = computed(() =>
    draftStructure.value?.chapters.reduce((sum, ch) => sum + ch.lessons.length, 0) ?? 0
  )

  const contextLabel = computed(() => {
    if (!selectedContext.value) return null
    return `${selectedContext.value.type === 'chapter' ? 'Ch' : 'L'}: ${selectedContext.value.title}`
  })

  // ---- Actions ----

  function setContext(type: 'chapter' | 'lesson', id: string, title: string): void {
    selectedContext.value = { type, id, title }
  }

  function clearContext(): void {
    selectedContext.value = null
  }

  function toggleNode(nodeId: string): void {
    if (expandedNodes.value.has(nodeId)) {
      expandedNodes.value.delete(nodeId)
    } else {
      expandedNodes.value.add(nodeId)
    }
    // Trigger reactivity
    expandedNodes.value = new Set(expandedNodes.value)
  }

  function expandAll(): void {
    if (!draftStructure.value) return
    const ids = new Set<string>()
    for (const ch of draftStructure.value.chapters) {
      ids.add(ch.id)
    }
    expandedNodes.value = ids
  }

  /**
   * Update the draft structure from an AI chat response.
   * Called when the chat composable receives operations that modify structure.
   */
  function updateFromResponse(structure: any): void {
    if (!structure) return
    draftStructure.value = {
      courseId: structure.course_id || draftStructure.value?.courseId || '',
      courseTitle: structure.course_title || draftStructure.value?.courseTitle || '',
      chapters: (structure.chapters || []).map((ch: any, ci: number) => ({
        id: ch.id || ch.chapter_id || `ch-${ci}`,
        title: ch.title || `Chapter ${ci + 1}`,
        order: ch.order ?? ci,
        lessons: (ch.lessons || []).map((ls: any, li: number) => ({
          id: ls.id || ls.lesson_id || `ls-${ci}-${li}`,
          title: ls.title || `Lesson ${li + 1}`,
          order: ls.order ?? li,
          contentIndicators: (ls.content_indicators || ls.methods || []).map((ind: any) => ({
            type: ind.type || 'method',
            label: ind.label || ind.name || ind.type,
            count: ind.count,
            status: ind.status || 'empty',
          })),
        })),
      })),
    }
    // Auto-expand all chapters
    expandAll()
  }

  function clearStructure(): void {
    draftStructure.value = null
    selectedContext.value = null
    expandedNodes.value = new Set()
    error.value = null
  }

  return {
    // State
    draftStructure,
    selectedContext,
    expandedNodes,
    isFinalizing,
    error,

    // Computed
    hasStructure,
    chapterCount,
    lessonCount,
    contextLabel,

    // Actions
    setContext,
    clearContext,
    toggleNode,
    expandAll,
    updateFromResponse,
    clearStructure,
  }
}
```

**Step 2: Update barrel**

Add: `export { useStructureView } from './useStructureView'`

**Step 3: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS

**Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/useStructureView.ts
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/index.ts
git commit -m "feat(ai-editor): add useStructureView composable

Manages the course structure tree, context selection (click chapter/lesson to set
chat context), and node expand/collapse state for the right panel."
```

---

## Task 4: `useWorkflowPhase` Composable

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/composables/useWorkflowPhase.ts`
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/composables/index.ts`

**Step 1: Create `useWorkflowPhase.ts`**

```typescript
import { ref, computed } from 'vue'
import type { WorkflowPhase, GenerateProgress, GenerateResult } from '../types'
import { executeSkill as apiExecuteSkill } from '@/infrastructure/api/clients/panel/editor/unified/unified.api'
import {
  finalizeSession as apiFinalizeSession
} from '@/infrastructure/api/clients/panel/editor/authoring/courseAuthoring.api'

export function useWorkflowPhase() {
  // ---- State ----
  const phase = ref<WorkflowPhase>('plan')
  const generateProgress = ref<GenerateProgress | null>(null)
  const generateResult = ref<GenerateResult | null>(null)
  const isGenerating = ref(false)
  const error = ref<string | null>(null)

  // ---- Computed ----
  const isPlan = computed(() => phase.value === 'plan')
  const isGenerate = computed(() => phase.value === 'generate')
  const isAccept = computed(() => phase.value === 'accept')
  const hasResult = computed(() => generateResult.value !== null)

  // ---- Actions ----

  function setPhase(newPhase: WorkflowPhase): void {
    phase.value = newPhase
  }

  async function startGenerate(
    skillCode: string,
    courseId: string,
    options?: {
      targetType?: string
      targetId?: string
      parameters?: Record<string, unknown>
      promptOverride?: string
    }
  ): Promise<GenerateResult | null> {
    phase.value = 'generate'
    isGenerating.value = true
    error.value = null
    generateProgress.value = {
      current: 0,
      total: 1,
      label: skillCode,
      percent: 0,
      skillCode,
    }

    try {
      const response = await apiExecuteSkill({
        skill_code: skillCode,
        course_id: courseId,
        target_type: options?.targetType,
        target_id: options?.targetId,
        parameters: options?.parameters || {},
        prompt_override: options?.promptOverride,
      })

      const result: GenerateResult = {
        generationId: response.generation_id,
        skillCode: response.skill_code || skillCode,
        content: response.content,
        tokensInput: response.tokens_input || 0,
        tokensOutput: response.tokens_output || 0,
        modelName: response.model_name || '',
        targetType: options?.targetType,
        targetId: options?.targetId,
      }

      generateResult.value = result
      generateProgress.value = { current: 1, total: 1, label: skillCode, percent: 100, skillCode }
      phase.value = 'accept'
      return result
    } catch (err: any) {
      error.value = err?.message || 'Generation failed'
      phase.value = 'plan'
      return null
    } finally {
      isGenerating.value = false
    }
  }

  function acceptResult(): void {
    // Content is already saved by the backend during generation
    generateResult.value = null
    generateProgress.value = null
    phase.value = 'plan'
  }

  function rejectResult(): void {
    generateResult.value = null
    generateProgress.value = null
    phase.value = 'plan'
  }

  async function finalize(sessionId: string): Promise<boolean> {
    isGenerating.value = true
    error.value = null
    try {
      await apiFinalizeSession(sessionId)
      return true
    } catch (err: any) {
      error.value = err?.message || 'Finalization failed'
      return false
    } finally {
      isGenerating.value = false
    }
  }

  function reset(): void {
    phase.value = 'plan'
    generateProgress.value = null
    generateResult.value = null
    isGenerating.value = false
    error.value = null
  }

  return {
    // State
    phase,
    generateProgress,
    generateResult,
    isGenerating,
    error,

    // Computed
    isPlan,
    isGenerate,
    isAccept,
    hasResult,

    // Actions
    setPhase,
    startGenerate,
    acceptResult,
    rejectResult,
    finalize,
    reset,
  }
}
```

**Step 2: Update barrel**

Add: `export { useWorkflowPhase } from './useWorkflowPhase'`

**Step 3: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS

**Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/useWorkflowPhase.ts
git add frontend/src/presentation/components/panel/editor/ai/unified/composables/index.ts
git commit -m "feat(ai-editor): add useWorkflowPhase composable

Tracks workflow phase (plan/generate/accept), drives skill execution,
and manages accept/reject/revise flow for generation results."
```

---

## Task 5: Chat Components — ChatMessage + ChatInput + ChatWelcome

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/chat/ChatMessage.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/chat/ChatInput.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/chat/ChatWelcome.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/chat/index.ts`

**Step 1: Create `ChatMessage.vue`**

```vue
<!--
  ChatMessage — Single message bubble (user, assistant, system)
  Renders markdown content, inline confirmation buttons, and operation badges.
-->
<template>
  <div class="chat-message" :class="[`role-${message.role}`]">
    <div class="message-header">
      <span class="message-role">{{ roleLabel }}</span>
      <span class="message-time">{{ formattedTime }}</span>
    </div>
    <div class="message-content" v-html="sanitizedContent" />
    <!-- Inline confirmation button from AI -->
    <div v-if="message.confirmation" class="message-confirmation">
      <button
        class="confirm-btn"
        @click="$emit('confirm', message.confirmation)"
        :disabled="disabled"
      >
        {{ message.confirmation.label }}
      </button>
    </div>
    <!-- Operation badges -->
    <div v-if="message.operations?.length" class="message-operations">
      <span
        v-for="op in message.operations"
        :key="op.type + (op.target_id || '')"
        class="operation-badge"
      >
        {{ op.label }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import type { ChatMessage, ChatConfirmation } from '../types'

const props = defineProps<{
  message: ChatMessage
  disabled?: boolean
}>()

defineEmits<{
  confirm: [confirmation: ChatConfirmation]
}>()

const roleLabel = computed(() => {
  switch (props.message.role) {
    case 'user': return 'You'
    case 'assistant': return 'AI'
    case 'system': return 'System'
    default: return props.message.role
  }
})

const formattedTime = computed(() => {
  try {
    return new Date(props.message.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
})

const sanitizedContent = computed(() =>
  DOMPurify.sanitize(props.message.content, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre', 'h3', 'h4'],
    ALLOWED_ATTR: ['href', 'title'],
  })
)
</script>

<style scoped>
.chat-message {
  padding: 0.75rem;
  border-radius: 0.5rem;
  max-width: 90%;
}
.chat-message.role-user {
  background: var(--color-primary-subtle);
  align-self: flex-end;
  margin-left: auto;
}
.chat-message.role-assistant {
  background: var(--color-surface-secondary);
  align-self: flex-start;
}
.chat-message.role-system {
  background: var(--color-warning-subtle, rgba(255, 200, 0, 0.1));
  align-self: center;
  font-size: 0.8125rem;
  text-align: center;
}
.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.375rem;
}
.message-role {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}
.message-time {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
}
.message-content {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-primary);
  word-break: break-word;
}
.message-content :deep(code) {
  background: var(--color-surface);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
}
.message-content :deep(pre) {
  background: var(--color-surface);
  padding: 0.5rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}
.message-confirmation {
  margin-top: 0.5rem;
}
.confirm-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: background 0.15s;
}
.confirm-btn:hover:not(:disabled) { background: var(--color-primary-dark); }
.confirm-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.message-operations {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.375rem;
}
.operation-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  color: var(--color-text-secondary);
}
</style>
```

**Step 2: Create `ChatInput.vue`**

```vue
<!--
  ChatInput — Message input bar with file attach button and context badge
-->
<template>
  <div class="chat-input">
    <!-- Context badge -->
    <div v-if="contextLabel" class="context-badge">
      <span class="context-text">{{ contextLabel }}</span>
      <button class="context-clear" @click="$emit('clearContext')">&times;</button>
    </div>
    <div class="input-row">
      <button
        class="attach-btn"
        @click="$emit('attachFile')"
        :title="$t('aiEditor.chat.attachFile')"
      >
        <span>+</span>
      </button>
      <textarea
        ref="textareaRef"
        v-model="inputText"
        :placeholder="$t('aiEditor.chat.placeholder')"
        :disabled="disabled"
        @keydown.enter.exact.prevent="handleSend"
        rows="1"
        class="message-textarea"
      />
      <button
        class="send-btn"
        :disabled="!canSend"
        @click="handleSend"
      >
        &rarr;
      </button>
    </div>
    <div v-if="fileCount > 0" class="file-indicator">
      {{ fileCount }} {{ $t('aiEditor.chat.filesAttached') }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  disabled?: boolean
  contextLabel?: string | null
  fileCount?: number
}>()

const emit = defineEmits<{
  send: [content: string]
  attachFile: []
  clearContext: []
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSend = computed(() => inputText.value.trim().length > 0 && !props.disabled)

function handleSend(): void {
  if (!canSend.value) return
  emit('send', inputText.value.trim())
  inputText.value = ''
  // Reset textarea height
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
}
</script>

<style scoped>
.chat-input {
  border-top: 1px solid var(--color-border);
  padding: 0.5rem;
  background: var(--color-surface);
}
.context-badge {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.375rem;
  padding: 0.25rem 0.5rem;
  background: var(--color-primary-subtle);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-primary);
}
.context-text { flex: 1; }
.context-clear {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: var(--color-primary);
  padding: 0;
  line-height: 1;
}
.input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.375rem;
}
.attach-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 1.125rem;
  cursor: pointer;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}
.attach-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.message-textarea {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  resize: none;
  font-size: 0.875rem;
  font-family: inherit;
  background: var(--color-surface);
  color: var(--color-text-primary);
  min-height: 2rem;
  max-height: 8rem;
  overflow-y: auto;
}
.message-textarea:focus { outline: none; border-color: var(--color-primary); }
.message-textarea:disabled { opacity: 0.5; }
.send-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 1rem;
  cursor: pointer;
  flex-shrink: 0;
}
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.send-btn:hover:not(:disabled) { background: var(--color-primary-dark); }
.file-indicator {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-top: 0.25rem;
  padding-left: 2.375rem;
}
</style>
```

**Step 3: Create `ChatWelcome.vue`**

```vue
<!--
  ChatWelcome — Empty state shown when no session exists yet.
  Offers "Start new course" and "Load existing course" options.
-->
<template>
  <div class="chat-welcome">
    <div class="welcome-icon">AI</div>
    <h3 class="welcome-title">{{ $t('aiEditor.chat.welcome') }}</h3>
    <p class="welcome-desc">{{ $t('aiEditor.chat.welcomeDesc') }}</p>
    <div class="welcome-actions">
      <button class="welcome-btn primary" @click="$emit('newCourse')">
        {{ $t('aiEditor.chat.newCourse') }}
      </button>
      <button class="welcome-btn secondary" @click="$emit('loadCourse')">
        {{ $t('aiEditor.chat.loadCourse') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  newCourse: []
  loadCourse: []
}>()
</script>

<style scoped>
.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  flex: 1;
}
.welcome-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}
.welcome-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}
.welcome-desc {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin: 0 0 1.25rem;
  max-width: 280px;
}
.welcome-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  max-width: 220px;
}
.welcome-btn {
  padding: 0.625rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
}
.welcome-btn.primary {
  background: var(--color-primary);
  color: white;
}
.welcome-btn.primary:hover { background: var(--color-primary-dark); }
.welcome-btn.secondary {
  background: var(--color-surface-secondary);
  border-color: var(--color-border);
  color: var(--color-text-primary);
}
.welcome-btn.secondary:hover { border-color: var(--color-primary); }
</style>
```

**Step 4: Create barrel `index.ts`**

```typescript
export { default as ChatMessage } from './ChatMessage.vue'
export { default as ChatInput } from './ChatInput.vue'
export { default as ChatWelcome } from './ChatWelcome.vue'
```

**Step 5: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS (may warn about missing i18n keys, that's OK — we add them in Task 10)

**Step 6: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/chat/
git commit -m "feat(ai-editor): add chat components (ChatMessage, ChatInput, ChatWelcome)

ChatMessage: renders user/assistant/system messages with markdown, inline confirmations,
and operation badges. ChatInput: message bar with file attach and context badge.
ChatWelcome: empty state with new/load course options."
```

---

## Task 6: Chat Components — ChatMessageList + ChatPanel

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/chat/ChatMessageList.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/chat/ChatPanel.vue`
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/chat/index.ts`

**Step 1: Create `ChatMessageList.vue`**

```vue
<!--
  ChatMessageList — Scrollable list of chat messages with auto-scroll
-->
<template>
  <div ref="containerRef" class="chat-message-list">
    <ChatMessage
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
      :disabled="disabled"
      @confirm="$emit('confirm', $event)"
    />
    <div v-if="isLoading" class="typing-indicator">
      <span class="dot" /><span class="dot" /><span class="dot" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { ChatMessage as ChatMessageType, ChatConfirmation } from '../types'
import ChatMessage from './ChatMessage.vue'

const props = defineProps<{
  messages: ChatMessageType[]
  isLoading?: boolean
  disabled?: boolean
}>()

defineEmits<{
  confirm: [confirmation: ChatConfirmation]
}>()

const containerRef = ref<HTMLElement | null>(null)

function scrollToBottom(): void {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.scrollTo({
        top: containerRef.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  })
}

watch(() => props.messages.length, scrollToBottom)
watch(() => props.isLoading, scrollToBottom)

defineExpose({ scrollToBottom })
</script>

<style scoped>
.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  align-self: flex-start;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  animation: bounce 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-4px); }
}
</style>
```

**Step 2: Create `ChatPanel.vue`**

```vue
<!--
  ChatPanel — Left side of split-view. Persistent chat interface.
  Shows welcome state if no session, otherwise message list + input.
-->
<template>
  <div class="chat-panel">
    <!-- Token budget bar -->
    <div v-if="hasSession" class="token-bar">
      <div class="token-bar-fill" :style="{ width: `${usagePercent}%` }" :class="tokenBarClass" />
      <span class="token-label">{{ tokensUsed.toLocaleString() }} / {{ tokenBudget.toLocaleString() }}</span>
    </div>

    <!-- Welcome or Messages -->
    <ChatWelcome
      v-if="!hasSession"
      @new-course="$emit('newCourse')"
      @load-course="$emit('loadCourse')"
    />
    <ChatMessageList
      v-else
      ref="messageListRef"
      :messages="messages"
      :is-loading="isLoading"
      :disabled="isLoading"
      @confirm="$emit('confirm', $event)"
    />

    <!-- Input -->
    <ChatInput
      v-if="hasSession"
      :disabled="isLoading"
      :context-label="contextLabel"
      :file-count="fileCount"
      @send="$emit('send', $event)"
      @attach-file="$emit('attachFile')"
      @clear-context="$emit('clearContext')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ChatMessage as ChatMessageType, ChatConfirmation } from '../types'
import ChatWelcome from './ChatWelcome.vue'
import ChatMessageList from './ChatMessageList.vue'
import ChatInput from './ChatInput.vue'

const props = defineProps<{
  hasSession: boolean
  messages: ChatMessageType[]
  isLoading: boolean
  tokensUsed: number
  tokenBudget: number
  usagePercent: number
  contextLabel?: string | null
  fileCount?: number
}>()

defineEmits<{
  newCourse: []
  loadCourse: []
  send: [content: string]
  attachFile: []
  clearContext: []
  confirm: [confirmation: ChatConfirmation]
}>()

const messageListRef = ref<InstanceType<typeof ChatMessageList> | null>(null)

const tokenBarClass = computed(() => ({
  'is-warning': props.usagePercent >= 80 && props.usagePercent < 100,
  'is-over': props.usagePercent >= 100,
}))
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  min-width: 320px;
}
.token-bar {
  height: 3px;
  background: var(--color-surface-secondary);
  position: relative;
  flex-shrink: 0;
}
.token-bar-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s;
}
.token-bar-fill.is-warning { background: var(--color-warning, #f59e0b); }
.token-bar-fill.is-over { background: var(--color-danger, #ef4444); }
.token-label {
  position: absolute;
  right: 0.5rem;
  top: 4px;
  font-size: 0.5625rem;
  color: var(--color-text-tertiary);
}
</style>
```

**Step 3: Update barrel**

```typescript
export { default as ChatMessage } from './ChatMessage.vue'
export { default as ChatInput } from './ChatInput.vue'
export { default as ChatWelcome } from './ChatWelcome.vue'
export { default as ChatMessageList } from './ChatMessageList.vue'
export { default as ChatPanel } from './ChatPanel.vue'
```

**Step 4: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/chat/
git commit -m "feat(ai-editor): add ChatMessageList and ChatPanel components

ChatMessageList: scrollable message list with auto-scroll and typing indicator.
ChatPanel: full left-side panel with token bar, welcome/messages toggle, and input."
```

---

## Task 7: Right Panel — StructureView + StructureTree + StructureNode

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/StructureNode.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/StructureTree.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/StructureView.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/index.ts`

**Step 1: Create `StructureNode.vue`**

```vue
<!--
  StructureNode — Single tree node (chapter or lesson).
  Chapters are expandable, lessons show content indicators.
-->
<template>
  <div class="structure-node" :class="{ 'is-selected': isSelected, 'is-chapter': isChapter }">
    <div class="node-header" @click="handleClick">
      <button
        v-if="isChapter"
        class="expand-btn"
        @click.stop="$emit('toggle', node.id)"
      >
        {{ isExpanded ? '▾' : '▸' }}
      </button>
      <span v-else class="node-indent" />
      <span class="node-icon">{{ isChapter ? '📖' : '📄' }}</span>
      <span class="node-title">{{ node.title }}</span>
      <span v-if="isChapter && lessonCount > 0" class="node-badge">{{ lessonCount }}</span>
    </div>
    <!-- Content indicators for lessons -->
    <div v-if="!isChapter && indicators.length > 0" class="node-indicators">
      <span
        v-for="ind in indicators"
        :key="ind.type"
        class="indicator"
        :class="`status-${ind.status}`"
      >
        {{ ind.label }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ContentIndicator {
  type: string
  label: string
  count?: number
  status: string
}

interface TreeNode {
  id: string
  title: string
  type: 'chapter' | 'lesson'
  lessonCount?: number
  contentIndicators?: ContentIndicator[]
}

const props = defineProps<{
  node: TreeNode
  isExpanded?: boolean
  isSelected?: boolean
}>()

const emit = defineEmits<{
  toggle: [id: string]
  select: [type: 'chapter' | 'lesson', id: string, title: string]
}>()

const isChapter = computed(() => props.node.type === 'chapter')
const lessonCount = computed(() => props.node.lessonCount ?? 0)
const indicators = computed(() => props.node.contentIndicators ?? [])

function handleClick(): void {
  emit('select', props.node.type, props.node.id, props.node.title)
}
</script>

<style scoped>
.structure-node { padding: 0.125rem 0; }
.node-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.1s;
}
.node-header:hover { background: var(--color-surface-secondary); }
.is-selected > .node-header {
  background: var(--color-primary-subtle);
  border-left: 2px solid var(--color-primary);
}
.expand-btn {
  background: none;
  border: none;
  font-size: 0.75rem;
  cursor: pointer;
  color: var(--color-text-tertiary);
  width: 1rem;
  padding: 0;
}
.node-indent { width: 1rem; flex-shrink: 0; }
.node-icon { font-size: 0.875rem; flex-shrink: 0; }
.node-title {
  flex: 1;
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.is-chapter > .node-header > .node-title { font-weight: 600; }
.node-badge {
  font-size: 0.625rem;
  padding: 0.0625rem 0.375rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  color: var(--color-text-tertiary);
}
.node-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding-left: 2.25rem;
  margin-top: 0.125rem;
}
.indicator {
  font-size: 0.5625rem;
  padding: 0.0625rem 0.25rem;
  border-radius: 0.125rem;
  border: 1px solid var(--color-border);
}
.indicator.status-empty { color: var(--color-text-tertiary); }
.indicator.status-draft { color: var(--color-warning, #f59e0b); border-color: currentColor; }
.indicator.status-generated { color: var(--color-primary); border-color: currentColor; }
.indicator.status-accepted { color: var(--color-success, #22c55e); border-color: currentColor; }
</style>
```

**Step 2: Create `StructureTree.vue`**

```vue
<!--
  StructureTree — Interactive tree of chapters and lessons.
  Click a node to set the chat context.
-->
<template>
  <div class="structure-tree">
    <div v-if="!structure" class="tree-empty">
      <p>{{ $t('aiEditor.structure.empty') }}</p>
    </div>
    <template v-else>
      <div v-for="chapter in structure.chapters" :key="chapter.id" class="tree-chapter">
        <StructureNode
          :node="{ id: chapter.id, title: chapter.title, type: 'chapter', lessonCount: chapter.lessons.length }"
          :is-expanded="expandedNodes.has(chapter.id)"
          :is-selected="selectedId === chapter.id"
          @toggle="$emit('toggleNode', $event)"
          @select="$emit('selectContext', $event[0], $event[1], $event[2])"
        />
        <div v-if="expandedNodes.has(chapter.id)" class="tree-lessons">
          <StructureNode
            v-for="lesson in chapter.lessons"
            :key="lesson.id"
            :node="{
              id: lesson.id,
              title: lesson.title,
              type: 'lesson',
              contentIndicators: lesson.contentIndicators,
            }"
            :is-selected="selectedId === lesson.id"
            @select="$emit('selectContext', $event[0], $event[1], $event[2])"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DraftStructure } from '../types'
import StructureNode from './StructureNode.vue'

const props = defineProps<{
  structure: DraftStructure | null
  expandedNodes: Set<string>
  selectedId?: string | null
}>()

defineEmits<{
  toggleNode: [id: string]
  selectContext: [type: 'chapter' | 'lesson', id: string, title: string]
}>()
</script>

<style scoped>
.structure-tree {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}
.tree-empty {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}
.tree-lessons { padding-left: 0.75rem; }
</style>
```

**Step 3: Create `StructureView.vue`**

```vue
<!--
  StructureView — Default right-panel view.
  Shows course tree + materials section + finalize button.
-->
<template>
  <div class="structure-view">
    <div class="structure-header">
      <h3 class="structure-title">{{ $t('aiEditor.structure.title') }}</h3>
      <div class="structure-stats" v-if="chapterCount > 0">
        <span>{{ chapterCount }} {{ $t('aiEditor.structure.chapters') }}</span>
        <span>{{ lessonCount }} {{ $t('aiEditor.structure.lessons') }}</span>
      </div>
    </div>

    <StructureTree
      :structure="structure"
      :expanded-nodes="expandedNodes"
      :selected-id="selectedId"
      @toggle-node="$emit('toggleNode', $event)"
      @select-context="$emit('selectContext', $event[0], $event[1], $event[2])"
    />

    <!-- Finalize button -->
    <div v-if="chapterCount > 0" class="structure-footer">
      <button
        class="finalize-btn"
        :disabled="isFinalizing"
        @click="$emit('finalize')"
      >
        {{ isFinalizing ? $t('aiEditor.structure.finalizing') : $t('aiEditor.structure.finalize') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DraftStructure } from '../types'
import StructureTree from './StructureTree.vue'

defineProps<{
  structure: DraftStructure | null
  expandedNodes: Set<string>
  selectedId?: string | null
  chapterCount: number
  lessonCount: number
  isFinalizing?: boolean
}>()

defineEmits<{
  toggleNode: [id: string]
  selectContext: [type: 'chapter' | 'lesson', id: string, title: string]
  finalize: []
}>()
</script>

<style scoped>
.structure-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.structure-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.structure-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}
.structure-stats {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.25rem;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}
.structure-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}
.finalize-btn {
  width: 100%;
  padding: 0.625rem;
  background: var(--color-success, #22c55e);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
}
.finalize-btn:hover:not(:disabled) { filter: brightness(0.9); }
.finalize-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
```

**Step 4: Create barrel `index.ts`**

```typescript
export { default as StructureNode } from './StructureNode.vue'
export { default as StructureTree } from './StructureTree.vue'
export { default as StructureView } from './StructureView.vue'
```

**Step 5: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS

**Step 6: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/right-panel/
git commit -m "feat(ai-editor): add StructureView, StructureTree, StructureNode components

Interactive course structure tree for the right panel. Chapters expand to show
lessons. Click any node to set the chat context. Content indicators show
generation status per lesson."
```

---

## Task 8: Right Panel — ProgressView + ResultView + RightPanel

**Files:**
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/ProgressView.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/ResultView.vue`
- Create: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/RightPanel.vue`
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/right-panel/index.ts`

**Step 1: Create `ProgressView.vue`**

```vue
<!--
  ProgressView — Shown during content generation.
  Displays current task, progress bar, and token count.
-->
<template>
  <div class="progress-view">
    <div class="progress-header">
      <h3>{{ $t('aiEditor.progress.generating') }}</h3>
    </div>
    <div class="progress-content">
      <div class="progress-bar-container">
        <div class="progress-bar-fill" :style="{ width: `${progress?.percent ?? 0}%` }" />
      </div>
      <div class="progress-details">
        <span class="progress-label">{{ progress?.label || '...' }}</span>
        <span class="progress-percent">{{ progress?.percent ?? 0 }}%</span>
      </div>
      <div v-if="progress?.current && progress?.total" class="progress-steps">
        {{ progress.current }} / {{ progress.total }}
      </div>
    </div>
    <div class="progress-animation">
      <div class="pulse-ring" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GenerateProgress } from '../types'

defineProps<{
  progress: GenerateProgress | null
}>()
</script>

<style scoped>
.progress-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
}
.progress-header h3 {
  font-size: 1rem;
  margin: 0 0 1.5rem;
  color: var(--color-text-primary);
}
.progress-content { width: 100%; max-width: 300px; }
.progress-bar-container {
  height: 6px;
  background: var(--color-surface-secondary);
  border-radius: 3px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.5s ease;
  border-radius: 3px;
}
.progress-details {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.8125rem;
}
.progress-label { color: var(--color-text-secondary); }
.progress-percent { color: var(--color-primary); font-weight: 600; }
.progress-steps {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-top: 0.25rem;
}
.progress-animation { margin-top: 2rem; }
.pulse-ring {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid var(--color-primary);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.5; }
  100% { transform: scale(0.8); opacity: 1; }
}
</style>
```

**Step 2: Create `ResultView.vue`**

```vue
<!--
  ResultView — Shown after generation completes.
  Displays generated content preview with accept/reject/revise actions.
-->
<template>
  <div class="result-view">
    <div class="result-header">
      <h3>{{ $t('aiEditor.result.title') }}</h3>
      <span v-if="result" class="result-meta">
        {{ result.modelName }} · {{ result.tokensOutput.toLocaleString() }} tokens
      </span>
    </div>
    <div class="result-content" v-if="result">
      <div class="result-target" v-if="result.targetTitle">
        {{ result.targetTitle }}
      </div>
      <div class="result-preview">
        <pre class="result-json">{{ JSON.stringify(result.content, null, 2) }}</pre>
      </div>
    </div>
    <div class="result-actions" v-if="result">
      <button class="action-btn accept" @click="$emit('accept')" :disabled="disabled">
        {{ $t('aiEditor.result.accept') }}
      </button>
      <button class="action-btn revise" @click="$emit('revise')" :disabled="disabled">
        {{ $t('aiEditor.result.revise') }}
      </button>
      <button class="action-btn reject" @click="$emit('reject')" :disabled="disabled">
        {{ $t('aiEditor.result.reject') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GenerateResult } from '../types'

defineProps<{
  result: GenerateResult | null
  disabled?: boolean
}>()

defineEmits<{
  accept: []
  reject: []
  revise: []
}>()
</script>

<style scoped>
.result-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.result-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.result-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}
.result-meta {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}
.result-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}
.result-target {
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--color-primary);
}
.result-preview {
  background: var(--color-surface-secondary);
  border-radius: 0.375rem;
  padding: 0.75rem;
}
.result-json {
  font-size: 0.75rem;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  color: var(--color-text-secondary);
}
.result-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}
.action-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
}
.action-btn.accept { background: var(--color-success, #22c55e); color: white; }
.action-btn.revise { background: var(--color-warning, #f59e0b); color: white; }
.action-btn.reject { background: var(--color-surface-secondary); color: var(--color-text-primary); border: 1px solid var(--color-border); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn:hover:not(:disabled) { filter: brightness(0.9); }
</style>
```

**Step 3: Create `RightPanel.vue`**

```vue
<!--
  RightPanel — Container that switches between views based on workflow phase.
  plan -> StructureView | generate -> ProgressView | accept -> ResultView
-->
<template>
  <div class="right-panel">
    <StructureView
      v-if="phase === 'plan'"
      :structure="structure"
      :expanded-nodes="expandedNodes"
      :selected-id="selectedId"
      :chapter-count="chapterCount"
      :lesson-count="lessonCount"
      :is-finalizing="isFinalizing"
      @toggle-node="$emit('toggleNode', $event)"
      @select-context="$emit('selectContext', $event[0], $event[1], $event[2])"
      @finalize="$emit('finalize')"
    />
    <ProgressView
      v-else-if="phase === 'generate'"
      :progress="progress"
    />
    <ResultView
      v-else-if="phase === 'accept'"
      :result="result"
      :disabled="isGenerating"
      @accept="$emit('acceptResult')"
      @reject="$emit('rejectResult')"
      @revise="$emit('reviseResult')"
    />
  </div>
</template>

<script setup lang="ts">
import type { WorkflowPhase, DraftStructure, GenerateProgress, GenerateResult } from '../types'
import StructureView from './StructureView.vue'
import ProgressView from './ProgressView.vue'
import ResultView from './ResultView.vue'

defineProps<{
  phase: WorkflowPhase
  // Structure props
  structure: DraftStructure | null
  expandedNodes: Set<string>
  selectedId?: string | null
  chapterCount: number
  lessonCount: number
  isFinalizing?: boolean
  // Progress props
  progress: GenerateProgress | null
  // Result props
  result: GenerateResult | null
  isGenerating?: boolean
}>()

defineEmits<{
  toggleNode: [id: string]
  selectContext: [type: 'chapter' | 'lesson', id: string, title: string]
  finalize: []
  acceptResult: []
  rejectResult: []
  reviseResult: []
}>()
</script>

<style scoped>
.right-panel {
  height: 100%;
  background: var(--color-surface);
  overflow: hidden;
}
</style>
```

**Step 4: Update barrel**

```typescript
export { default as StructureNode } from './StructureNode.vue'
export { default as StructureTree } from './StructureTree.vue'
export { default as StructureView } from './StructureView.vue'
export { default as ProgressView } from './ProgressView.vue'
export { default as ResultView } from './ResultView.vue'
export { default as RightPanel } from './RightPanel.vue'
```

**Step 5: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS

**Step 6: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/right-panel/
git commit -m "feat(ai-editor): add ProgressView, ResultView, and RightPanel container

ProgressView: generation progress with animated indicator.
ResultView: content preview with accept/reject/revise actions.
RightPanel: container that switches view based on workflow phase."
```

---

## Task 9: Rewrite `UnifiedAIEditor.vue` as Split-View

**Files:**
- Modify: `frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue`

This is the core change: replacing the tab-based layout with a split-view. Read the existing file first, then rewrite.

**Step 1: Read the existing file**

Read: `frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue`

**Step 2: Rewrite as split-view**

Replace the entire file content with:

```vue
<!--
  UnifiedAIEditor — Split-view orchestrator for AI-powered course creation.

  Layout: Chat (left 45%) | Right Panel (right 55%)
  The chat is always visible. The right panel switches between:
  - StructureView (default, during plan phase)
  - ProgressView (during generation)
  - ResultView (after generation, for accept/reject)
-->
<template>
  <div class="unified-ai-editor">
    <!-- Course selector (top bar) -->
    <div class="editor-topbar">
      <select
        v-model="selectedCourseId"
        class="course-select"
        @change="handleCourseChange"
      >
        <option value="">{{ $t('aiEditor.chat.selectCourse') }}</option>
        <option
          v-for="course in courses"
          :key="course.id"
          :value="course.id"
        >
          {{ course.title }}
        </option>
      </select>
      <span v-if="chatSession.hasSession.value" class="session-badge">
        {{ $t('aiEditor.phase.' + workflowPhase.phase.value) }}
      </span>
    </div>

    <!-- Split view -->
    <div class="split-view">
      <!-- Left: Chat Panel -->
      <div class="split-left">
        <ChatPanel
          :has-session="chatSession.hasSession.value"
          :messages="chatSession.messages.value"
          :is-loading="chatSession.isLoading.value"
          :tokens-used="chatSession.tokensUsed.value"
          :token-budget="chatSession.tokenBudget.value"
          :usage-percent="chatSession.usagePercent.value"
          :context-label="structureView.contextLabel.value"
          :file-count="chatSession.selectedFileIds.value.length"
          @new-course="handleNewCourse"
          @load-course="handleLoadCourse"
          @send="handleSend"
          @attach-file="handleAttachFile"
          @clear-context="structureView.clearContext()"
          @confirm="handleConfirmation"
        />
      </div>

      <!-- Right: Context-dependent panel -->
      <div class="split-right">
        <RightPanel
          :phase="workflowPhase.phase.value"
          :structure="structureView.draftStructure.value"
          :expanded-nodes="structureView.expandedNodes.value"
          :selected-id="structureView.selectedContext.value?.id"
          :chapter-count="structureView.chapterCount.value"
          :lesson-count="structureView.lessonCount.value"
          :is-finalizing="structureView.isFinalizing.value"
          :progress="workflowPhase.generateProgress.value"
          :result="workflowPhase.generateResult.value"
          :is-generating="workflowPhase.isGenerating.value"
          @toggle-node="structureView.toggleNode($event)"
          @select-context="handleSelectContext"
          @finalize="handleFinalize"
          @accept-result="handleAcceptResult"
          @reject-result="handleRejectResult"
          @revise-result="handleReviseResult"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChatPanel } from './chat'
import { RightPanel } from './right-panel'
import { useChatSession } from './composables/useChatSession'
import { useStructureView } from './composables/useStructureView'
import { useWorkflowPhase } from './composables/useWorkflowPhase'
import type { ChatConfirmation } from './types'
import { listEditorCourses } from '@/infrastructure/api/clients/panel/editor'

const props = defineProps<{
  courseId?: string
}>()

const { t } = useI18n()

// ---- Composables ----
const chatSession = useChatSession()
const structureView = useStructureView()
const workflowPhase = useWorkflowPhase()

// Provide for child components that need direct access
provide('chatSession', chatSession)
provide('structureView', structureView)
provide('workflowPhase', workflowPhase)

// ---- Local state ----
const courses = ref<Array<{ id: string; title: string }>>([])
const selectedCourseId = ref(props.courseId || '')

// ---- Lifecycle ----
onMounted(async () => {
  try {
    const result = await listEditorCourses()
    courses.value = (result || []).map((c: any) => ({
      id: c.course_id || c.id,
      title: c.title || c.name,
    }))
  } catch {
    courses.value = []
  }

  // Auto-load if courseId prop provided
  if (props.courseId) {
    await chatSession.loadOrCreateSession(props.courseId)
  }
})

// ---- Handlers ----

async function handleCourseChange(): void {
  if (!selectedCourseId.value) return
  chatSession.clearSession()
  structureView.clearStructure()
  workflowPhase.reset()
  await chatSession.loadOrCreateSession(selectedCourseId.value)
}

async function handleNewCourse(): void {
  // For now, prompt user to select a course from the dropdown
  // Future: create course inline
  chatSession.addSystemMessage(t('aiEditor.chat.selectCourseFirst'))
}

async function handleLoadCourse(): void {
  chatSession.addSystemMessage(t('aiEditor.chat.selectCourseFirst'))
}

async function handleSend(content: string): void {
  const response = await chatSession.sendMessage(content)
  // If AI response contains structure updates, apply them
  if (response?.operations) {
    // Backend sends updated draft_structure in the response
    // The chat endpoint returns the full session state including draft
  }
}

function handleAttachFile(): void {
  // TODO: Open file picker modal
  chatSession.addSystemMessage(t('aiEditor.chat.fileUploadTodo'))
}

function handleSelectContext(type: 'chapter' | 'lesson', id: string, title: string): void {
  structureView.setContext(type, id, title)
  // Inform the chat about the context change
  chatSession.addSystemMessage(
    t('aiEditor.chat.contextSet', { type, title })
  )
}

async function handleFinalize(): void {
  if (!chatSession.session.value) return
  structureView.isFinalizing.value = true
  const success = await workflowPhase.finalize(chatSession.session.value.sessionId)
  structureView.isFinalizing.value = false
  if (success) {
    chatSession.addSystemMessage(t('aiEditor.structure.finalizeSuccess'))
  }
}

async function handleConfirmation(confirmation: ChatConfirmation): void {
  if (confirmation.skillCode && chatSession.courseId.value) {
    await workflowPhase.startGenerate(
      confirmation.skillCode,
      chatSession.courseId.value,
      {
        targetId: confirmation.targetId,
        params: confirmation.params as Record<string, unknown>,
      }
    )
  }
}

function handleAcceptResult(): void {
  workflowPhase.acceptResult()
  chatSession.addSystemMessage(t('aiEditor.result.accepted'))
}

function handleRejectResult(): void {
  workflowPhase.rejectResult()
  chatSession.addSystemMessage(t('aiEditor.result.rejected'))
}

async function handleReviseResult(): void {
  // Switch back to plan phase but keep result context
  workflowPhase.setPhase('plan')
  chatSession.addSystemMessage(t('aiEditor.result.revisePrompt'))
}
</script>

<style scoped>
.unified-ai-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
}
.editor-topbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.course-select {
  flex: 1;
  max-width: 300px;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.8125rem;
}
.session-badge {
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  text-transform: uppercase;
  font-weight: 600;
}
.split-view {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.split-left {
  width: 45%;
  min-width: 320px;
  flex-shrink: 0;
}
.split-right {
  flex: 1;
  border-left: 1px solid var(--color-border);
}
</style>
```

**Step 3: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS (i18n keys may show warnings but build should succeed)

**Step 4: Commit**

```bash
git add frontend/src/presentation/components/panel/editor/ai/unified/UnifiedAIEditor.vue
git commit -m "feat(ai-editor): rewrite UnifiedAIEditor as chat-first split-view

Replaces tab-based layout with split-view: persistent chat (left 45%)
and context-dependent right panel (structure/progress/result).
Uses new useChatSession, useStructureView, useWorkflowPhase composables."
```

---

## Task 10: i18n Keys (de/en/pl)

**Files:**
- Modify: `frontend/src/infrastructure/i18n/locales/de/panel/aiEditor/unified.json`
- Modify: `frontend/src/infrastructure/i18n/locales/en/panel/aiEditor/unified.json`
- Modify: `frontend/src/infrastructure/i18n/locales/pl/panel/aiEditor/unified.json`

**Step 1: Read the existing unified.json files**

Read all three to understand the existing key structure, then add the new keys.

**Step 2: Add new keys to DE**

Add the following keys to the existing `de/panel/aiEditor/unified.json`:

```json
{
  "aiEditor": {
    "chat": {
      "welcome": "KI-Kurseditor",
      "welcomeDesc": "Erstelle Kurse im Dialog mit der KI. Lade Materialien hoch oder starte von Grund auf.",
      "placeholder": "Nachricht eingeben...",
      "attachFile": "Datei anhängen",
      "filesAttached": "Dateien angehängt",
      "newCourse": "Neuen Kurs starten",
      "loadCourse": "Bestehenden Kurs laden",
      "selectCourse": "Kurs auswählen",
      "selectCourseFirst": "Bitte wähle zuerst einen Kurs aus der Auswahl oben.",
      "contextSet": "Kontext gesetzt: {type} \"{title}\"",
      "contextLabel": "Kontext",
      "clearContext": "Kontext löschen",
      "fileUploadTodo": "Datei-Upload wird in Kürze verfügbar sein."
    },
    "structure": {
      "title": "Kursstruktur",
      "empty": "Noch keine Struktur. Chatte mit der KI, um Kapitel und Lektionen zu erstellen.",
      "chapters": "Kapitel",
      "lessons": "Lektionen",
      "materials": "Materialien",
      "uploadMaterial": "Material hochladen",
      "finalize": "Kurs finalisieren",
      "finalizing": "Finalisiere...",
      "finalizeConfirm": "Möchtest du den Kurs wirklich finalisieren?",
      "finalizeSuccess": "Kurs erfolgreich finalisiert! Die Struktur wurde in die Datenbank übernommen."
    },
    "progress": {
      "generating": "Inhalt wird generiert...",
      "tokens": "Tokens"
    },
    "result": {
      "title": "Generiertes Ergebnis",
      "accept": "Akzeptieren",
      "reject": "Ablehnen",
      "revise": "Überarbeiten",
      "accepted": "Ergebnis akzeptiert und gespeichert.",
      "rejected": "Ergebnis abgelehnt.",
      "revisePrompt": "Beschreibe die gewünschten Änderungen im Chat."
    },
    "phase": {
      "plan": "Planung",
      "generate": "Generierung",
      "accept": "Prüfung"
    }
  }
}
```

**Step 3: Add new keys to EN**

```json
{
  "aiEditor": {
    "chat": {
      "welcome": "AI Course Editor",
      "welcomeDesc": "Create courses by chatting with the AI. Upload materials or start from scratch.",
      "placeholder": "Type a message...",
      "attachFile": "Attach file",
      "filesAttached": "files attached",
      "newCourse": "Start new course",
      "loadCourse": "Load existing course",
      "selectCourse": "Select course",
      "selectCourseFirst": "Please select a course from the dropdown above first.",
      "contextSet": "Context set: {type} \"{title}\"",
      "contextLabel": "Context",
      "clearContext": "Clear context",
      "fileUploadTodo": "File upload will be available soon."
    },
    "structure": {
      "title": "Course Structure",
      "empty": "No structure yet. Chat with the AI to create chapters and lessons.",
      "chapters": "Chapters",
      "lessons": "Lessons",
      "materials": "Materials",
      "uploadMaterial": "Upload material",
      "finalize": "Finalize course",
      "finalizing": "Finalizing...",
      "finalizeConfirm": "Do you really want to finalize this course?",
      "finalizeSuccess": "Course finalized successfully! Structure has been saved to the database."
    },
    "progress": {
      "generating": "Generating content...",
      "tokens": "Tokens"
    },
    "result": {
      "title": "Generated Result",
      "accept": "Accept",
      "reject": "Reject",
      "revise": "Revise",
      "accepted": "Result accepted and saved.",
      "rejected": "Result rejected.",
      "revisePrompt": "Describe the changes you want in the chat."
    },
    "phase": {
      "plan": "Planning",
      "generate": "Generating",
      "accept": "Review"
    }
  }
}
```

**Step 4: Add new keys to PL**

```json
{
  "aiEditor": {
    "chat": {
      "welcome": "Edytor kursów AI",
      "welcomeDesc": "Twórz kursy w rozmowie z AI. Prześlij materiały lub zacznij od zera.",
      "placeholder": "Wpisz wiadomość...",
      "attachFile": "Dołącz plik",
      "filesAttached": "plików dołączonych",
      "newCourse": "Rozpocznij nowy kurs",
      "loadCourse": "Załaduj istniejący kurs",
      "selectCourse": "Wybierz kurs",
      "selectCourseFirst": "Proszę najpierw wybrać kurs z listy powyżej.",
      "contextSet": "Kontekst ustawiony: {type} \"{title}\"",
      "contextLabel": "Kontekst",
      "clearContext": "Wyczyść kontekst",
      "fileUploadTodo": "Przesyłanie plików będzie wkrótce dostępne."
    },
    "structure": {
      "title": "Struktura kursu",
      "empty": "Brak struktury. Porozmawiaj z AI, aby utworzyć rozdziały i lekcje.",
      "chapters": "Rozdziały",
      "lessons": "Lekcje",
      "materials": "Materiały",
      "uploadMaterial": "Prześlij materiał",
      "finalize": "Finalizuj kurs",
      "finalizing": "Finalizowanie...",
      "finalizeConfirm": "Czy na pewno chcesz sfinalizować ten kurs?",
      "finalizeSuccess": "Kurs sfinalizowany pomyślnie! Struktura została zapisana w bazie danych."
    },
    "progress": {
      "generating": "Generowanie treści...",
      "tokens": "Tokeny"
    },
    "result": {
      "title": "Wygenerowany wynik",
      "accept": "Akceptuj",
      "reject": "Odrzuć",
      "revise": "Popraw",
      "accepted": "Wynik zaakceptowany i zapisany.",
      "rejected": "Wynik odrzucony.",
      "revisePrompt": "Opisz pożądane zmiany w czacie."
    },
    "phase": {
      "plan": "Planowanie",
      "generate": "Generowanie",
      "accept": "Sprawdzanie"
    }
  }
}
```

**Important:** These keys should be MERGED into the existing unified.json files, not replace them. The existing keys (for tabs, plan, skills, etc.) must be preserved.

**Step 5: Verify build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS

**Step 6: Commit**

```bash
git add frontend/src/infrastructure/i18n/locales/de/panel/aiEditor/unified.json
git add frontend/src/infrastructure/i18n/locales/en/panel/aiEditor/unified.json
git add frontend/src/infrastructure/i18n/locales/pl/panel/aiEditor/unified.json
git commit -m "feat(ai-editor): add i18n keys for chat split-view (de/en/pl)

New keys for chat panel, structure view, progress view, result view,
and workflow phases in all 3 languages."
```

---

## Task 11: Backend System Prompt Enhancement

**Files:**
- Modify: `backend/app/application/services/content/course_authoring/prompts.py`

**Step 1: Read the existing prompts.py**

Read: `backend/app/application/services/content/course_authoring/prompts.py`

Understand the current system prompt structure.

**Step 2: Enhance the system prompt**

Add these instructions to the existing system prompt (find the `SYSTEM_PROMPT` or equivalent constant and extend it):

```python
# Add to the system prompt string:
"""
Additional guidelines:
- When the user uploads materials (PDF, DOCX, etc.), use them as the PRIMARY source for course content.
- Generate complete content (theory sheets, flashcards, quizzes) — not just structure.
- ALWAYS ask for confirmation before heavy generation tasks (e.g., "Shall I generate flashcards for Lesson 2?").
- Be thorough in research and accuracy. Cross-reference uploaded materials.
- When suggesting a course structure, include content type indicators (theory, flashcards, exercises) for each lesson.
- Support iterative refinement: when the user says "make it simpler" or "add more examples", regenerate the specific content.
"""
```

**Step 3: Verify backend starts**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`
Expected: No import errors

**Step 4: Commit**

```bash
git add backend/app/application/services/content/course_authoring/prompts.py
git commit -m "feat(ai-editor): enhance course authoring system prompt

Add guidelines for material-based generation, confirmation before heavy tasks,
thorough research, content indicators, and iterative refinement support."
```

---

## Task 12: Final Build Verification + Cleanup

**Files:**
- No new files — verification only

**Step 1: Full build**

Run: `cd /home/pascal/Lernsystem/frontend && npm run build`
Expected: PASS with zero errors

**Step 2: TypeScript check**

Run: `cd /home/pascal/Lernsystem/frontend && npm run typecheck`
Expected: PASS or only pre-existing warnings

**Step 3: Backend check**

Run: `cd /home/pascal/Lernsystem/backend && python -c "from app import create_app; create_app()"`
Expected: No errors

**Step 4: Verify file count**

```
New files created:
  chat/ChatMessage.vue
  chat/ChatInput.vue
  chat/ChatWelcome.vue
  chat/ChatMessageList.vue
  chat/ChatPanel.vue
  chat/index.ts
  right-panel/StructureNode.vue
  right-panel/StructureTree.vue
  right-panel/StructureView.vue
  right-panel/ProgressView.vue
  right-panel/ResultView.vue
  right-panel/RightPanel.vue
  right-panel/index.ts
  composables/useChatSession.ts
  composables/useStructureView.ts
  composables/useWorkflowPhase.ts
  types/chat.types.ts
  types/structure.types.ts
  types/workflow.types.ts
Total: 19 new files

Modified files:
  types/index.ts
  composables/index.ts
  UnifiedAIEditor.vue
  3x unified.json (de/en/pl)
  prompts.py
Total: 7 modified files
```

**Step 5: Commit if any cleanup needed**

```bash
git add -A
git commit -m "chore(ai-editor): final build verification and cleanup"
```

---

## Summary

| Task | Description | New Files | Modified | Est. LOC |
|------|-------------|-----------|----------|----------|
| 1 | Type definitions | 3 | 1 | ~120 |
| 2 | useChatSession composable | 1 | 1 | ~180 |
| 3 | useStructureView composable | 1 | 1 | ~120 |
| 4 | useWorkflowPhase composable | 1 | 1 | ~130 |
| 5 | ChatMessage + ChatInput + ChatWelcome | 4 | 0 | ~350 |
| 6 | ChatMessageList + ChatPanel | 2 | 1 | ~200 |
| 7 | StructureView + Tree + Node | 4 | 0 | ~350 |
| 8 | ProgressView + ResultView + RightPanel | 3 | 1 | ~300 |
| 9 | UnifiedAIEditor.vue rewrite | 0 | 1 | ~250 |
| 10 | i18n keys (de/en/pl) | 0 | 3 | ~150 |
| 11 | Backend system prompt | 0 | 1 | ~30 |
| 12 | Final verification | 0 | 0 | 0 |
| **Total** | | **19** | **11** | **~2,180** |
