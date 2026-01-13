/**
 * useSessionManager - Course Authoring Session Management
 *
 * Manages authoring sessions: create, load, finalize, and state management.
 *
 * @module kurs-builder/composables/useSessionManager
 */

import { ref, computed, type Ref } from 'vue'
import http from '@/api/http'
import type { Session, DraftStructure, DraftStats } from '../types'

/**
 * Session Manager Composable
 *
 * Provides reactive session management for course authoring.
 *
 * @param courseId - Reactive course ID reference
 * @returns Session management state and methods
 *
 * @example
 * ```typescript
 * const sessionMgr = useSessionManager(computed(() => props.courseId))
 *
 * // Create new session
 * await sessionMgr.createSession()
 *
 * // Finalize session (apply changes to course)
 * await sessionMgr.finalizeSession()
 * ```
 */
export function useSessionManager(courseId: Ref<string | undefined>) {
  // State
  const session = ref<Session | null>(null)
  const draftStructure = ref<DraftStructure | null>(null)
  const creatingSession = ref(false)
  const finalizing = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasSession = computed(() => !!session.value)

  const hasChanges = computed(() => {
    return (draftStructure.value?.chapters?.length || 0) > 0
  })

  const draftStats = computed<DraftStats>(() => {
    const chapters = draftStructure.value?.chapters || []
    let lessons = 0
    let methods = 0

    for (const ch of chapters) {
      lessons += ch.lessons?.length || 0
      for (const l of ch.lessons || []) {
        methods += l.methods?.length || 0
      }
    }

    return {
      chapters: chapters.length,
      lessons,
      methods
    }
  })

  const sessionMeta = computed(() => {
    if (!session.value) return null
    return {
      sessionId: session.value.session_id,
      status: session.value.status,
      metadata: session.value.metadata
    }
  })

  /**
   * Create a new authoring session
   *
   * Creates a new session for the current course. If a session
   * already exists, it will be returned instead.
   *
   * @throws {Error} If course ID is not set or API call fails
   */
  async function createSession(): Promise<void> {
    if (!courseId.value) {
      error.value = 'Kein Kurs ausgewählt'
      return
    }

    creatingSession.value = true
    error.value = null

    try {
      const res = await http.post('/admin/course-authoring/sessions', {
        course_id: courseId.value
      })

      if (res.data.success) {
        session.value = res.data.data
        draftStructure.value = res.data.data.draft_structure || {
          course_id: courseId.value,
          chapters: [],
          version: 1,
          updated_at: new Date().toISOString(),
          has_changes: false
        }
      } else {
        error.value = res.data.error || 'Session konnte nicht erstellt werden'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = 'Fehler beim Erstellen der Session: ' + (err.message || 'Unbekannt')
      throw err
    } finally {
      creatingSession.value = false
    }
  }

  /**
   * Finalize the current session
   *
   * Applies all draft changes to the actual course structure
   * and marks the session as completed.
   *
   * @param skipConfirmation - Skip confirmation dialog
   * @returns Finalization statistics
   * @throws {Error} If no active session or API call fails
   */
  async function finalizeSession(skipConfirmation = false): Promise<{
    chapters: number
    lessons: number
    methods: number
  } | null> {
    if (!session.value) {
      error.value = 'Keine aktive Session'
      return null
    }

    if (!skipConfirmation) {
      const confirmed = confirm(
        'Session finalisieren? Alle Änderungen werden in den Kurs übernommen.'
      )
      if (!confirmed) return null
    }

    finalizing.value = true
    error.value = null

    try {
      const res = await http.post(
        `/admin/course-authoring/sessions/${session.value.session_id}/finalize`
      )

      if (res.data.success) {
        const stats = res.data.data.stats

        // Reset state after successful finalization
        resetState()

        return stats
      } else {
        error.value = res.data.error || 'Finalisierung fehlgeschlagen'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = 'Fehler bei der Finalisierung: ' + (err.message || 'Unbekannt')
      throw err
    } finally {
      finalizing.value = false
    }
  }

  /**
   * Load an existing session by ID
   *
   * @param sessionId - Session ID to load
   * @throws {Error} If session not found or API call fails
   */
  async function loadSession(sessionId: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const res = await http.get(`/admin/course-authoring/sessions/${sessionId}`)

      if (res.data.success) {
        session.value = res.data.data
        draftStructure.value = res.data.data.draft_structure || {
          course_id: courseId.value || '',
          chapters: [],
          version: 1,
          updated_at: new Date().toISOString(),
          has_changes: false
        }
      } else {
        error.value = res.data.error || 'Session konnte nicht geladen werden'
        throw new Error(error.value)
      }
    } catch (err: any) {
      error.value = 'Fehler beim Laden der Session: ' + (err.message || 'Unbekannt')
      console.error('Failed to load session:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Load existing active session for current course
   *
   * Searches for an active session for the current course
   * and loads it if found.
   *
   * @returns True if session was found and loaded, false otherwise
   */
  async function loadExistingSession(): Promise<boolean> {
    if (!courseId.value) return false

    try {
      const res = await http.get(
        `/admin/course-authoring/courses/${courseId.value}/sessions?status=active`
      )

      if (res.data.success && res.data.data.sessions.length > 0) {
        const activeSession = res.data.data.sessions[0]
        await loadSession(activeSession.session_id)
        return true
      }

      return false
    } catch (err) {
      // No active session found (expected case)
      console.debug('No active session for course:', courseId.value)
      return false
    }
  }

  /**
   * Reset all session state
   *
   * Clears session, draft structure, and error state.
   * Used after finalization or when switching courses.
   */
  function resetState(): void {
    session.value = null
    draftStructure.value = null
    error.value = null
    creatingSession.value = false
    finalizing.value = false
    loading.value = false
  }

  /**
   * Update draft structure
   *
   * Updates the local draft structure state.
   * Note: This does not persist to backend automatically.
   *
   * @param newStructure - New draft structure
   */
  function updateDraftStructure(newStructure: DraftStructure): void {
    draftStructure.value = {
      ...newStructure,
      updated_at: new Date().toISOString(),
      has_changes: true
    }
  }

  return {
    // State
    session,
    draftStructure,
    creatingSession,
    finalizing,
    loading,
    error,

    // Computed
    hasSession,
    hasChanges,
    draftStats,
    sessionMeta,

    // Methods
    createSession,
    finalizeSession,
    loadSession,
    loadExistingSession,
    resetState,
    updateDraftStructure
  }
}
