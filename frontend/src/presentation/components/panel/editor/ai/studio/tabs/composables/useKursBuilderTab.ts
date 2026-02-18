/**
 * useKursBuilderTab - Business logic for the KursBuilder tab
 *
 * Encapsulates data loading, session management, and chat for the
 * KursBuilder tab. Context selection, analysis, confirmation, structure,
 * file management, and tutor integration are delegated to
 * useKursBuilderActions.
 *
 * @module studio/tabs/composables/useKursBuilderTab
 */

import { ref, computed, watch, onMounted, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'
import {
  getActionsByCategory,
  type LMSuggestion
} from '@/application/services/api/learning'
import { useKursBuilderActions } from './useKursBuilderActions'
import type {
  Course,
  ChatMessage,
  CourseFile,
  Session,
  DraftStructure,
  Chapter,
  QuickAction
} from './kursBuilder.types'

export type {
  Course,
  ChatMessage,
  CourseFile,
  Session,
  DraftStructure,
  Chapter,
  QuickAction,
  LMSuggestion
}

export { type Lesson, type SelectedContext, type PendingAction } from './kursBuilder.types'

/**
 * Composable for all KursBuilder tab business logic.
 *
 * @param courseRef - Reactive reference to the currently selected course
 */
export function useKursBuilderTab(courseRef: Ref<Course | null>) {
  const { t } = useI18n()

  // ---- Core State ----
  const session = ref<Session | null>(null)
  const chatMessages = ref<ChatMessage[]>([])
  const draftStructure = ref<DraftStructure | null>(null)
  const sessionFiles = ref<CourseFile[]>([])
  const selectedFileIds = ref<string[]>([])
  const inputMessage = ref('')
  const selectedMode = ref('')
  const creatingSession = ref(false)
  const chatLoading = ref(false)
  const finalizing = ref(false)
  const error = ref<string | null>(null)
  const actionsLoading = ref(false)
  const quickActions = ref<QuickAction[]>([])

  // ---- Computed ----
  const hasChanges = computed(() => (draftStructure.value?.chapters?.length || 0) > 0)

  const draftStats = computed(() => {
    const chapters = draftStructure.value?.chapters || []
    let lessons = 0
    let methods = 0
    for (const ch of chapters) {
      lessons += ch.lessons?.length || 0
      for (const l of ch.lessons || []) {
        methods += l.methods?.length || 0
      }
    }
    return { chapters: chapters.length, lessons, methods }
  })

  // ---- Actions composable (context, analysis, confirmation, structure, files, tutor) ----
  const actions = useKursBuilderActions({
    courseRef,
    session,
    chatMessages,
    draftStructure,
    sessionFiles,
    selectedFileIds,
    inputMessage,
    selectedMode,
    sendMessage
  })

  // ---- Watch course changes ----
  watch(() => courseRef.value?.course_id, async (newId) => {
    if (newId) {
      await loadExistingSession()
      await loadCourseFiles()
      await loadExistingStructure()
    } else {
      resetState()
    }
  })

  // ---- Data Loading ----

  async function loadQuickActions(): Promise<void> {
    actionsLoading.value = true
    try {
      const result = await getActionsByCategory('course_builder')
      quickActions.value = result?.length
        ? result.map(a => ({
            action_id: a.action_id, action_key: a.action_key, label: a.label,
            icon: a.icon || '', prompt_template: a.prompt_template,
            mode: a.mode, color: a.color
          }))
        : getFallbackActions()
    } catch {
      quickActions.value = getFallbackActions()
    } finally {
      actionsLoading.value = false
    }
  }

  function getFallbackActions(): QuickAction[] {
    return [
      { action_id: 'fb-1', action_key: 'structure_suggest', label: t('kursBuilder.fallbackActions.structureSuggest'), icon: '', prompt_template: 'Analysiere das Kursmaterial und schlage eine passende Kapitelstruktur vor.', mode: 'structure' },
      { action_id: 'fb-2', action_key: 'chapters_create_3', label: t('kursBuilder.fallbackActions.createChapters'), icon: '', prompt_template: 'Erstelle 3 Kapitel mit je 3-5 Lektionen basierend auf dem Kursmaterial.', mode: 'structure' },
      { action_id: 'fb-3', action_key: 'exam_generate', label: t('kursBuilder.fallbackActions.generateExam'), icon: '', prompt_template: 'Generiere IHK-Stil Prüfungsfragen basierend auf den vorhandenen Kapiteln.', mode: 'exam' },
      { action_id: 'fb-4', action_key: 'material_analyze', label: t('kursBuilder.fallbackActions.analyzeMaterial'), icon: '', prompt_template: 'Analysiere das hochgeladene Material und extrahiere die wichtigsten Konzepte.', mode: 'analyze' }
    ]
  }

  async function loadExistingSession(): Promise<void> {
    if (!courseRef.value) return
    try {
      const res = await http.get(
        `/admin/course-authoring/courses/${courseRef.value.course_id}/sessions?status=active`
      )
      if (res.data.success && res.data.data.sessions.length > 0) {
        await loadSession(res.data.data.sessions[0].session_id)
      }
    } catch { /* No active session */ }
  }

  async function loadSession(sessionId: string): Promise<void> {
    try {
      const res = await http.get(`/admin/course-authoring/sessions/${sessionId}`)
      if (res.data.success) {
        session.value = res.data.data
        chatMessages.value = res.data.data.chat_history || []
        draftStructure.value = res.data.data.draft_structure || { chapters: [] }
      }
    } catch (err) {
      console.error('Failed to load session:', err)
    }
  }

  async function loadCourseFiles(): Promise<void> {
    if (!courseRef.value) return
    try {
      const res = await http.get(`/admin/courses/${courseRef.value.course_id}/files`)
      if (res.data.success) {
        sessionFiles.value = (res.data.files || []).map((f: any) => ({
          id: f.course_file_id || f.file_id,
          name: f.display_name || f.file_name || 'Unbekannt',
          type: f.file_type || 'pdf',
          size: f.file_size_bytes || 0,
          parsed: f.is_parsed || false,
          url: f.public_url || f.cdn_url || null
        }))
      }
    } catch (err) {
      console.error('Failed to load files:', err)
    }
  }

  async function loadExistingStructure(): Promise<void> {
    if (!courseRef.value || session.value) return
    try {
      const chaptersRes = await http.get(
        `/admin/courses/${courseRef.value.course_id}/chapters`
      )
      if (!chaptersRes.data.success) return

      const chapters = chaptersRes.data.data?.chapters || chaptersRes.data.chapters || []
      const structureChapters: Chapter[] = []

      for (const ch of chapters) {
        const lessonsRes = await http.get(`/panel/chapters/${ch.chapter_id}/lessons`)
        const lessons = lessonsRes.data.success
          ? (lessonsRes.data.data?.lessons || lessonsRes.data.lessons || [])
          : []
        structureChapters.push({
          id: ch.chapter_id,
          title: ch.title,
          description: ch.description || '',
          lessons: lessons.map((l: any) => ({
            id: l.lesson_id,
            title: l.title,
            methods: l.content?.lm_primary
              ? [{ id: `lm-${l.lesson_id}`, type: l.content.lm_primary, title: l.title }]
              : []
          }))
        })
      }

      if (structureChapters.length > 0) {
        draftStructure.value = { chapters: structureChapters, activity_log: [] }
      }
    } catch (err) {
      console.error('Failed to load structure:', err)
    }
  }

  // ---- Session Management ----

  async function createSession(): Promise<void> {
    if (!courseRef.value) return
    creatingSession.value = true
    error.value = null
    try {
      const res = await http.post('/admin/course-authoring/sessions', {
        course_id: courseRef.value.course_id
      })
      if (res.data.success) {
        session.value = res.data.data
        draftStructure.value = res.data.data.draft_structure || { chapters: [] }
        chatMessages.value = []
      } else {
        error.value = res.data.error || 'Session konnte nicht erstellt werden'
      }
    } catch (err: any) {
      error.value = 'Fehler: ' + (err.message || 'Unbekannt')
    } finally {
      creatingSession.value = false
    }
  }

  async function finalizeSession(): Promise<void> {
    if (!session.value ||
        !confirm('Session finalisieren? Änderungen werden in den Kurs übernommen.')) return
    finalizing.value = true
    try {
      const res = await http.post(
        `/admin/course-authoring/sessions/${session.value.session_id}/finalize`
      )
      if (res.data.success) {
        alert(
          `Erfolgreich! ${res.data.data.stats.chapters} Kapitel, ${res.data.data.stats.lessons} Lektionen`
        )
        resetState()
      } else {
        error.value = res.data.error || 'Finalisierung fehlgeschlagen'
      }
    } catch (err: any) {
      error.value = 'Fehler: ' + (err.message || 'Unbekannt')
    } finally {
      finalizing.value = false
    }
  }

  // ---- Chat ----

  async function sendMessage(msg: string, mode: string): Promise<void> {
    if (!msg.trim() || chatLoading.value) return
    if (!session.value) {
      await createSession()
      if (!session.value) return
    }

    chatMessages.value.push({
      role: 'user', content: msg, timestamp: new Date().toISOString()
    })
    chatLoading.value = true

    try {
      const res = await http.post(
        `/admin/course-authoring/sessions/${session.value.session_id}/chat`,
        { message: msg, mode: mode || undefined, file_ids: selectedFileIds.value }
      )
      if (res.data.success) {
        chatMessages.value.push({
          role: 'assistant',
          content: res.data.data.assistant_message,
          operations: res.data.data.operations_applied
        })
        const pending = actions.checkForGeneratedContent(res.data.data)
        if (pending) actions.pendingAction.value = pending
        if (res.data.data.draft_structure) {
          draftStructure.value = res.data.data.draft_structure
        }
      } else {
        error.value = res.data.error || 'Chat-Fehler'
      }
    } catch (err: any) {
      error.value = 'Chat-Fehler: ' + (err.message || 'Unbekannt')
    } finally {
      chatLoading.value = false
    }
  }

  function sendQuickAction(action: QuickAction): void {
    selectedMode.value = action.mode || ''
    sendMessage(action.prompt_template, action.mode || '')
  }

  function resetState(): void {
    session.value = null
    chatMessages.value = []
    draftStructure.value = null
    selectedFileIds.value = []
  }

  // ---- Lifecycle ----
  onMounted(async () => {
    await loadQuickActions()
    if (courseRef.value) {
      await loadExistingSession()
      await loadCourseFiles()
      await loadExistingStructure()
    }
  })

  return {
    // Core state
    session,
    chatMessages,
    draftStructure,
    sessionFiles,
    selectedFileIds,
    inputMessage,
    selectedMode,
    creatingSession,
    chatLoading,
    finalizing,
    error,
    actionsLoading,
    quickActions,

    // Computed
    hasChanges,
    draftStats,

    // Session
    createSession,
    finalizeSession,

    // Chat
    sendMessage,
    sendQuickAction,

    // Delegated from actions composable
    ...actions,

    // Expose session meta
    sessionMeta: computed(() => session.value ? {
      sessionId: session.value.session_id,
      status: session.value.status,
      totalTokensUsed: session.value.total_tokens_used
    } : null),
    hasSession: computed(() => !!session.value)
  }
}
