import { ref, computed } from 'vue'
import type { ChatMessage, ChatSession, ChatOperation } from '../types'
import {
  createSession as apiCreateSession,
  getSession as apiGetSession,
  sendChatMessage as apiSendChat,
  listSessions as apiListSessions,
} from '@/infrastructure/api/clients/panel/editor/authoring/courseAuthoring.api'

/** Default token budget per session. TODO: Load from backend org/course settings via API. */
const DEFAULT_TOKEN_BUDGET = 100_000

/** Map backend operation strings to human-readable ChatOperation objects */
const OP_LABELS: Record<string, string> = {
  add_chapter: 'Kapitel erstellt',
  update_chapter: 'Kapitel aktualisiert',
  delete_chapter: 'Kapitel gelöscht',
  add_lesson: 'Lektion erstellt',
  update_lesson: 'Lektion aktualisiert',
  delete_lesson: 'Lektion gelöscht',
  add_method: 'Methode hinzugefügt',
  update_method: 'Methode aktualisiert',
  delete_method: 'Methode gelöscht',
  reorder_chapters: 'Kapitel umsortiert',
  reorder_lessons: 'Lektionen umsortiert',
  set_meta: 'Metadaten gesetzt',
}

function mapOperations(ops: unknown): ChatOperation[] | undefined {
  if (!Array.isArray(ops) || ops.length === 0) return undefined
  return ops.map((op: unknown) => {
    if (typeof op === 'string') {
      return { type: op, label: OP_LABELS[op] || op }
    }
    if (typeof op === 'object' && op !== null) {
      const o = op as Record<string, string>
      return { type: o.type || o.op || 'unknown', label: o.label || OP_LABELS[o.type || o.op] || o.type || 'Aktion' }
    }
    return { type: 'unknown', label: String(op) }
  })
}

export function useChatSession() {
  // ---- State ----
  const session = ref<ChatSession | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const isCreatingSession = ref(false)
  const error = ref<string | null>(null)

  // Token tracking
  const tokensUsed = ref(0)
  const tokenBudget = ref(DEFAULT_TOKEN_BUDGET)

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

  async function createSession(
    forCourseId?: string,
    modelOptions?: { providerName?: string; modelName?: string }
  ): Promise<void> {
    const cId = forCourseId || courseId.value
    if (!cId) {
      error.value = 'No course selected'
      return
    }
    isCreatingSession.value = true
    error.value = null
    try {
      const raw = await apiCreateSession(cId, {
        providerName: modelOptions?.providerName,
        modelName: modelOptions?.modelName,
      })
      // Backend returns { success, data: {...} } — unwrap
      const response = raw?.data ?? raw
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
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create session'
      error.value = message
    } finally {
      isCreatingSession.value = false
    }
  }

  async function loadSession(sessionId: string): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const raw = await apiGetSession(sessionId)
      // Backend returns { success, data: {...} } — unwrap
      const response = raw?.data ?? raw
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
        messages.value = response.chat_history.map(
          (msg: Record<string, unknown>, idx: number) => ({
            id: (msg.id as string) || `msg-${idx}`,
            role: (msg.role as string) || 'assistant',
            content: (msg.content as string) || '',
            timestamp:
              (msg.timestamp as string) || (msg.created_at as string) || new Date().toISOString(),
            operations: msg.operations,
            fileIds: msg.file_ids,
          })
        )
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load session'
      error.value = message
    } finally {
      isLoading.value = false
    }
  }

  async function loadOrCreateSession(
    forCourseId: string,
    modelOptions?: { providerName?: string; modelName?: string }
  ): Promise<void> {
    courseId.value = forCourseId
    error.value = null
    isLoading.value = true
    try {
      // Try to find existing active session
      const response = await apiListSessions(forCourseId, 'active')
      if (courseId.value !== forCourseId) return // stale — course changed during await
      // Backend returns { success, data: { sessions: [...] } }
      const sessions = response?.data?.sessions ?? (Array.isArray(response) ? response : [])
      if (sessions.length > 0) {
        await loadSession(sessions[0].session_id || sessions[0].id)
        return
      }
      if (courseId.value !== forCourseId) return // stale
      // No active session — create new
      await createSession(forCourseId, modelOptions)
    } catch (e: unknown) {
      if (courseId.value !== forCourseId) return // stale
      console.warn('[ChatSession] Failed to list sessions, creating new:', e)
      await createSession(forCourseId, modelOptions)
    } finally {
      isLoading.value = false
    }
  }

  async function sendMessage(
    content: string,
    fileIds?: string[],
    contextHint?: string
  ): Promise<ChatMessage | null> {
    if (!session.value) {
      error.value = 'No active session'
      return null
    }
    isLoading.value = true
    error.value = null

    // Add user message immediately (without context prefix — that's for the AI only)
    const resolvedFileIds =
      fileIds || (selectedFileIds.value.length > 0 ? [...selectedFileIds.value] : undefined)
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
      fileIds: resolvedFileIds,
    }
    messages.value.push(userMsg)

    // Prepend context hint to the message sent to AI (not shown in chat UI)
    const messageForAI = contextHint ? contextHint + content : content

    try {
      const raw = await apiSendChat(session.value.sessionId, messageForAI, {
        file_ids: fileIds || selectedFileIds.value,
      })
      // Backend returns { success, data: {...} } — unwrap
      const response = raw?.data ?? raw

      // Add AI response
      const rawOps = response.operations_applied || response.operations
      const aiMsg: ChatMessage = {
        id: response.message_id || `msg-${Date.now()}-ai`,
        role: 'assistant',
        content: response.assistant_message || response.response || response.content || '',
        timestamp: new Date().toISOString(),
        operations: mapOperations(rawOps),
      }
      messages.value.push(aiMsg)

      // Show parse error as system message if JSON parsing failed
      if (response.parse_error) {
        messages.value.push({
          id: `msg-${Date.now()}-parse-err`,
          role: 'system',
          content: 'JSON-Parsing fehlgeschlagen — die KI-Antwort konnte nicht als Aktion interpretiert werden. Versuche es erneut.',
          timestamp: new Date().toISOString(),
        })
      }

      // Track tokens
      if (response.tokens_used) {
        tokensUsed.value += response.tokens_used
      }

      return aiMsg
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to send message'
      error.value = message
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
