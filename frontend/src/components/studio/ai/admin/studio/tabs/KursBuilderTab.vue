<!--
  KursBuilderTab.vue - REFACTORED

  KI-Kurs-Builder Tab für chat-basiertes Authoring.
  Uses sub-components from ./kurs-builder/

  Layout (2 Spalten):
  - Links (60%): Chat + Workflow Panel
  - Rechts (40%): Kursstruktur + Materialien
-->

<template>
  <div class="kurs-builder-tab">
    <!-- Header mit Session-Status -->
    <div class="builder-header">
      <div class="header-left">
        <span class="header-icon">🏗️</span>
        <div class="header-info">
          <h3 class="header-title">{{ $t('features.kursBuilder.title') }}</h3>
          <div class="header-meta">
            <span v-if="course" class="course-badge">{{ course.title }}</span>
            <span v-if="draftStats.chapters > 0" class="stats-badge">
              {{ $t('features.kursBuilder.statsChapters', { chapters: draftStats.chapters, lessons: draftStats.lessons }) }}
            </span>
          </div>
        </div>
      </div>

      <div class="header-right">
        <div v-if="session" class="session-info">
          <span class="session-dot active"></span>
          <span class="session-text">{{ $t('features.kursBuilder.sessionActive') }}</span>
          <span class="session-id">{{ session.session_id.slice(0, 8) }}</span>
        </div>
        <div v-else class="session-info">
          <span class="session-dot inactive"></span>
          <span class="session-text">{{ $t('features.kursBuilder.noSession') }}</span>
        </div>

        <button v-if="!session && course" @click="createSession" :disabled="creatingSession" class="btn-primary">
          {{ creatingSession ? $t('features.kursBuilder.creating') : $t('features.kursBuilder.newSession') }}
        </button>

        <button v-if="session?.status === 'active'" @click="finalizeSession" :disabled="finalizing || !hasChanges" class="btn-success">
          {{ finalizing ? $t('features.kursBuilder.finalizing') : $t('features.kursBuilder.finalize') }}
        </button>
      </div>
    </div>

    <!-- No Course Selected -->
    <div v-if="!course" class="empty-state">
      <span class="empty-icon">📚</span>
      <p class="empty-title">{{ $t('features.kursBuilder.noCourseSelected') }}</p>
      <p class="empty-hint">{{ $t('features.kursBuilder.selectCourseHint') }}</p>
    </div>

    <!-- Main Content (2 Spalten) -->
    <div v-else class="builder-content">
      <!-- Left: Chat Column (60%) -->
      <div class="chat-column">
        <!-- Workflow Panel (when context selected) -->
        <WorkflowPanel
          v-if="selectedContext"
          :context="selectedContext"
          :selected-file-count="selectedFileIds.length"
          :is-analyzing="isAnalyzing"
          :is-loading-theories="isLoadingTheories"
          :is-generating-theory="isGeneratingTheory"
          :is-loading-l-m-suggestions="lmSuggestionsLoading"
          :is-loading-actions="contextActionsLoading"
          :theories="chapterTheories"
          :explanations="lessonExplanations"
          :lm-suggestions="lmSuggestions"
          :context-actions="contextActions"
          :selected-theory-id="selectedTheoryId"
          :disabled="chatLoading"
          @close="clearContext"
          @analyze="analyzeSelectedContext"
          @generate-theory="generateTheory"
          @open-theory="openTheoryInTutor"
          @open-explanation="openExplanationInTutor"
          @create-lm="createLMFromSuggestion"
          @action="sendContextAction"
        />

        <!-- Confirmation Panel -->
        <ConfirmationPanel
          v-if="pendingAction"
          :pending-action="pendingAction"
          :is-loading="confirmLoading"
          @confirm="confirmPendingAction"
          @modify="modifyPendingAction"
          @reject="rejectPendingAction"
        />

        <!-- Chat Panel -->
        <ChatPanel
          :messages="chatMessages"
          :is-loading="chatLoading"
          :quick-actions="quickActions"
          :actions-loading="actionsLoading"
          :selected-file-count="selectedFileIds.length"
          :has-context="!!selectedContext"
          :show-quick-actions="!pendingAction"
          v-model="inputMessage"
          v-model:mode="selectedMode"
          @send="sendMessage"
          @quick-action="sendQuickAction"
        />
      </div>

      <!-- Right: Structure + Materials (40%) -->
      <div class="right-column">
        <StructurePanel
          :chapters="draftStructure?.chapters || []"
          :analyzing-lesson-id="analyzingLessonId"
          :selected-file-count="selectedFileIds.length"
          @select-chapter="selectChapterForChat"
          @preview-chapter="openChapterPreview"
          @edit-chapter="editChapter"
          @delete-chapter="deleteChapter"
          @select-lesson="selectLessonForChat"
          @preview-lesson="openLessonPreview"
          @edit-lesson="editLesson"
          @delete-lesson="deleteLesson"
          @analyze-lesson="analyzeLessonWithFiles"
        />

        <MaterialsPanel
          :files="sessionFiles"
          v-model:selected-ids="selectedFileIds"
          @upload="triggerFileUpload"
          @preview="openFilePreview"
          @clear-selection="clearFileSelection"
        />
      </div>
    </div>

    <!-- Hidden file input -->
    <input
      ref="materialFileInput"
      type="file"
      multiple
      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md"
      style="display: none"
      @change="handleMaterialUpload"
    />

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button @click="error = null">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/store/modules/desktop'
import { useTheoryManagement } from '@/composables/useTheoryManagement'
import http from '@/api/http'
import {
  ChatPanel,
  ConfirmationPanel,
  MaterialsPanel,
  StructurePanel,
  WorkflowPanel
} from '../../authoring/kurs-builder'
import {
  getActionsByCategory,
  getActionsForEntity,
  getLMSuggestions,
  type AuthoringAction,
  type LMSuggestion
} from '@/api/ai-authoring.api'

const { t } = useI18n()

// Types
interface Course { course_id: string; title: string }
interface ChatMessage { role: 'user' | 'assistant'; content: string; timestamp?: string; operations?: string[]; error?: boolean }
interface CourseFile { id: string; name: string; type: string; size: number; parsed: boolean; url?: string }
interface Session { session_id: string; course_id: string; status: 'active' | 'finalized' | 'archived'; draft_structure: DraftStructure; chat_history: ChatMessage[]; total_tokens_used: number }
interface DraftStructure { chapters?: Chapter[]; activity_log?: any[] }
interface Chapter { id: string; title: string; description?: string; lessons?: Lesson[] }
interface Lesson { id: string; title: string; description?: string; content?: any; duration_minutes?: number; methods?: { id: string; type: string; title?: string }[] }
interface QuickAction { action_id: string; action_key: string; label: string; icon: string; prompt_template: string; mode?: string; color?: string }
interface SelectedContext { type: 'chapter' | 'lesson' | 'method'; id: string; title: string; data: Chapter | Lesson | null; parentChapter?: Chapter }
interface PendingAction { type: 'create' | 'update' | 'delete'; entity: 'chapter' | 'lesson' | 'method' | 'quiz'; actionKey: string; generatedData: any; previewText: string; parentChapter?: Chapter; session_id?: string }

// Props
const props = defineProps<{ course: Course | null }>()

// Stores & Composables
const panelStore = usePanelStore()
const theoryMgmt = useTheoryManagement()

// State
const session = ref<Session | null>(null)
const chatMessages = ref<ChatMessage[]>([])
const draftStructure = ref<DraftStructure | null>(null)
const sessionFiles = ref<CourseFile[]>([])
const selectedFileIds = ref<string[]>([])
const materialFileInput = ref<HTMLInputElement | null>(null)
const isUploadingFile = ref(false)
const analyzingLessonId = ref<string | null>(null)
const isAnalyzing = ref(false)
const isGeneratingTheory = ref(false)
const inputMessage = ref('')
const selectedMode = ref('')
const creatingSession = ref(false)
const chatLoading = ref(false)
const finalizing = ref(false)
const error = ref<string | null>(null)
const actionsLoading = ref(false)
const selectedContext = ref<SelectedContext | null>(null)
const contextActionsLoading = ref(false)
const contextActions = ref<QuickAction[]>([])
const lmSuggestions = ref<LMSuggestion[]>([])
const lmSuggestionsLoading = ref(false)
const pendingAction = ref<PendingAction | null>(null)
const confirmLoading = ref(false)
const quickActions = ref<QuickAction[]>([])
const selectedTheoryId = ref<string | null>(null)

// Computed from composable
const chapterTheories = computed(() => theoryMgmt.chapterTheories.value)
const lessonExplanations = computed(() => theoryMgmt.lessonExplanations.value)
const isLoadingTheories = computed(() => theoryMgmt.isLoading.value)
const hasChanges = computed(() => (draftStructure.value?.chapters?.length || 0) > 0)

const draftStats = computed(() => {
  const chapters = draftStructure.value?.chapters || []
  let lessons = 0, methods = 0
  for (const ch of chapters) {
    lessons += ch.lessons?.length || 0
    for (const l of ch.lessons || []) methods += l.methods?.length || 0
  }
  return { chapters: chapters.length, lessons, methods }
})

// Watch course changes
watch(() => props.course?.course_id, async (newId) => {
  if (newId) {
    await loadExistingSession()
    await loadCourseFiles()
    await loadExistingStructure()
  } else {
    resetState()
  }
})

// ============================================================================
// Data Loading
// ============================================================================
async function loadQuickActions() {
  actionsLoading.value = true
  try {
    const actions = await getActionsByCategory('course_builder')
    quickActions.value = actions?.length ? actions.map(a => ({
      action_id: a.action_id, action_key: a.action_key, label: a.label,
      icon: a.icon || '📋', prompt_template: a.prompt_template, mode: a.mode, color: a.color
    })) : getFallbackActions()
  } catch { quickActions.value = getFallbackActions() }
  finally { actionsLoading.value = false }
}

function getFallbackActions(): QuickAction[] {
  return [
    { action_id: 'fb-1', action_key: 'structure_suggest', label: t('features.kursBuilder.fallbackActions.structureSuggest'), icon: '📋', prompt_template: 'Analysiere das Kursmaterial und schlage eine passende Kapitelstruktur vor.', mode: 'structure' },
    { action_id: 'fb-2', action_key: 'chapters_create_3', label: t('features.kursBuilder.fallbackActions.createChapters'), icon: '📚', prompt_template: 'Erstelle 3 Kapitel mit je 3-5 Lektionen basierend auf dem Kursmaterial.', mode: 'structure' },
    { action_id: 'fb-3', action_key: 'exam_generate', label: t('features.kursBuilder.fallbackActions.generateExam'), icon: '🎓', prompt_template: 'Generiere IHK-Stil Prüfungsfragen basierend auf den vorhandenen Kapiteln.', mode: 'exam' },
    { action_id: 'fb-4', action_key: 'material_analyze', label: t('features.kursBuilder.fallbackActions.analyzeMaterial'), icon: '🔍', prompt_template: 'Analysiere das hochgeladene Material und extrahiere die wichtigsten Konzepte.', mode: 'analyze' }
  ]
}

async function loadExistingSession() {
  if (!props.course) return
  try {
    const res = await http.get(`/admin/course-authoring/courses/${props.course.course_id}/sessions?status=active`)
    if (res.data.success && res.data.data.sessions.length > 0) await loadSession(res.data.data.sessions[0].session_id)
  } catch { /* No active session */ }
}

async function loadSession(sessionId: string) {
  try {
    const res = await http.get(`/admin/course-authoring/sessions/${sessionId}`)
    if (res.data.success) {
      session.value = res.data.data
      chatMessages.value = res.data.data.chat_history || []
      draftStructure.value = res.data.data.draft_structure || { chapters: [] }
    }
  } catch (err) { console.error('Failed to load session:', err) }
}

async function loadCourseFiles() {
  if (!props.course) return
  try {
    const res = await http.get(`/admin/courses/${props.course.course_id}/files`)
    if (res.data.success) {
      sessionFiles.value = (res.data.files || []).map((f: any) => ({
        id: f.course_file_id || f.file_id, name: f.display_name || f.file_name || 'Unbekannt',
        type: f.file_type || 'pdf', size: f.file_size_bytes || 0, parsed: f.is_parsed || false, url: f.public_url || f.cdn_url || null
      }))
    }
  } catch (err) { console.error('Failed to load files:', err) }
}

async function loadExistingStructure() {
  if (!props.course || session.value) return
  try {
    const chaptersRes = await http.get(`/admin/courses/${props.course.course_id}/chapters`)
    if (!chaptersRes.data.success) return
    const chapters = chaptersRes.data.data?.chapters || chaptersRes.data.chapters || []
    const structureChapters: Chapter[] = []
    for (const ch of chapters) {
      const lessonsRes = await http.get(`/admin/chapters/${ch.chapter_id}/lessons`)
      const lessons = lessonsRes.data.success ? (lessonsRes.data.data?.lessons || lessonsRes.data.lessons || []) : []
      structureChapters.push({
        id: ch.chapter_id, title: ch.title, description: ch.description || '',
        lessons: lessons.map((l: any) => ({ id: l.lesson_id, title: l.title, methods: l.content?.lm_primary ? [{ id: `lm-${l.lesson_id}`, type: l.content.lm_primary, title: l.title }] : [] }))
      })
    }
    if (structureChapters.length > 0) draftStructure.value = { chapters: structureChapters, activity_log: [] }
  } catch (err) { console.error('Failed to load structure:', err) }
}

// ============================================================================
// Session Management
// ============================================================================
async function createSession() {
  if (!props.course) return
  creatingSession.value = true; error.value = null
  try {
    const res = await http.post('/admin/course-authoring/sessions', { course_id: props.course.course_id })
    if (res.data.success) { session.value = res.data.data; draftStructure.value = res.data.data.draft_structure || { chapters: [] }; chatMessages.value = [] }
    else error.value = res.data.error || 'Session konnte nicht erstellt werden'
  } catch (err: any) { error.value = 'Fehler: ' + (err.message || 'Unbekannt') }
  finally { creatingSession.value = false }
}

async function finalizeSession() {
  if (!session.value || !confirm('Session finalisieren? Änderungen werden in den Kurs übernommen.')) return
  finalizing.value = true
  try {
    const res = await http.post(`/admin/course-authoring/sessions/${session.value.session_id}/finalize`)
    if (res.data.success) { alert(`Erfolgreich! ${res.data.data.stats.chapters} Kapitel, ${res.data.data.stats.lessons} Lektionen`); resetState() }
    else error.value = res.data.error || 'Finalisierung fehlgeschlagen'
  } catch (err: any) { error.value = 'Fehler: ' + (err.message || 'Unbekannt') }
  finally { finalizing.value = false }
}

// ============================================================================
// Chat & Actions
// ============================================================================
async function sendMessage(msg: string, mode: string) {
  if (!msg.trim() || chatLoading.value) return
  if (!session.value) { await createSession(); if (!session.value) return }
  chatMessages.value.push({ role: 'user', content: msg, timestamp: new Date().toISOString() })
  chatLoading.value = true
  try {
    const res = await http.post(`/admin/course-authoring/sessions/${session.value.session_id}/chat`, { message: msg, mode: mode || undefined, file_ids: selectedFileIds.value })
    if (res.data.success) {
      chatMessages.value.push({ role: 'assistant', content: res.data.data.assistant_message, operations: res.data.data.operations_applied })
      const pending = checkForGeneratedContent(res.data.data)
      if (pending) pendingAction.value = pending
      if (res.data.data.draft_structure) draftStructure.value = res.data.data.draft_structure
    } else error.value = res.data.error || 'Chat-Fehler'
  } catch (err: any) { error.value = 'Chat-Fehler: ' + (err.message || 'Unbekannt') }
  finally { chatLoading.value = false }
}

function sendQuickAction(action: QuickAction) {
  selectedMode.value = action.mode || ''
  sendMessage(action.prompt_template, action.mode || '')
}

function addSystemMessage(content: string) {
  chatMessages.value.push({ role: 'assistant', content, timestamp: new Date().toISOString() })
}

// ============================================================================
// Context Selection
// ============================================================================
async function selectChapterForChat(chapter: Chapter) {
  selectedContext.value = { type: 'chapter', id: chapter.id, title: chapter.title, data: chapter }
  lmSuggestions.value = []
  await Promise.all([loadContextActions('chapter'), theoryMgmt.loadChapterTheories(chapter.id)])
}

async function selectLessonForChat(chapter: Chapter, lesson: Lesson) {
  selectedContext.value = { type: 'lesson', id: lesson.id, title: lesson.title, data: lesson, parentChapter: chapter }
  await Promise.all([loadContextActions('lesson'), loadLMSuggestions(lesson, chapter), theoryMgmt.loadLessonExplanations(lesson.id)])
}

async function loadContextActions(entityType: 'chapter' | 'lesson' | 'method') {
  contextActionsLoading.value = true
  try {
    const actions = await getActionsForEntity(entityType)
    contextActions.value = actions?.length ? actions.map(a => ({ action_id: a.action_id, action_key: a.action_key, label: a.label, icon: a.icon || '📋', prompt_template: a.prompt_template, mode: a.mode, color: a.color })) : []
  } catch { contextActions.value = [] }
  finally { contextActionsLoading.value = false }
}

async function loadLMSuggestions(lesson: Lesson, chapter: Chapter) {
  lmSuggestionsLoading.value = true; lmSuggestions.value = []
  try {
    const existingLmIds = (lesson.methods || []).map(m => { const match = m.type?.match(/LM(\d+)/i); return match ? parseInt(match[1]) : null }).filter((id): id is number => id !== null)
    const result = await getLMSuggestions({ lesson_title: lesson.title, lesson_content: lesson.description || '', chapter_title: chapter.title, course_title: props.course?.title || '', existing_lm_ids: existingLmIds, max_suggestions: 6 })
    lmSuggestions.value = result.suggestions || []
  } catch { lmSuggestions.value = [] }
  finally { lmSuggestionsLoading.value = false }
}

function clearContext() {
  selectedContext.value = null; contextActions.value = []; lmSuggestions.value = []; theoryMgmt.reset()
}

function sendContextAction(action: QuickAction) {
  let prompt = action.prompt_template
  if (selectedContext.value) {
    prompt = prompt.replace('{{context_title}}', selectedContext.value.title).replace('{{context_type}}', selectedContext.value.type)
  }
  selectedMode.value = action.mode || ''
  sendMessage(prompt, action.mode || '')
}

// ============================================================================
// Analysis & Theory
// ============================================================================
async function analyzeLessonWithFiles(chapter: Chapter, lesson: Lesson) {
  if (!props.course) return
  analyzingLessonId.value = lesson.id
  try {
    const response = await http.post('/admin/ai-studio/analyze-lesson', { course_id: props.course.course_id, chapter_id: chapter.id, chapter_title: chapter.title, lesson_id: lesson.id, lesson_title: lesson.title, file_ids: selectedFileIds.value, request_type: 'lm_recommendation' })
    if (response.data.success) {
      const analysis = response.data.data
      addSystemMessage(`**${t('features.kursBuilder.messages.analysisFor', { name: lesson.title })}**\n\n${analysis.summary || ''}\n\n**${t('features.kursBuilder.messages.recommendedMethods')}**\n${(analysis.recommended_lms || []).map((lm: any) => `- ${lm.name}: ${lm.reason}`).join('\n')}`)
      if (analysis.recommended_lms?.length) lmSuggestions.value = analysis.recommended_lms.map((lm: any) => ({ lm_id: lm.lm_id, name: lm.name, reason: lm.reason, confidence: lm.confidence || 0.8 }))
    }
  } catch { addSystemMessage(t('features.kursBuilder.messages.analysisError', { name: lesson.title })) }
  finally { analyzingLessonId.value = null }
}

async function analyzeSelectedContext() {
  if (!selectedContext.value || !props.course) return
  isAnalyzing.value = true
  try {
    const isChapter = selectedContext.value.type === 'chapter'
    const response = await http.post('/admin/ai-studio/analyze-lesson', { course_id: props.course.course_id, chapter_id: isChapter ? selectedContext.value.id : selectedContext.value.parentChapter?.id, chapter_title: isChapter ? selectedContext.value.title : selectedContext.value.parentChapter?.title, lesson_id: isChapter ? null : selectedContext.value.id, lesson_title: isChapter ? null : selectedContext.value.title, file_ids: selectedFileIds.value, request_type: 'lm_recommendation' })
    if (response.data.success) {
      const analysis = response.data.data
      const contextName = isChapter ? `${t('features.kursBuilder.chapter')} "${selectedContext.value.title}"` : `${t('features.kursBuilder.lesson')} "${selectedContext.value.title}"`
      addSystemMessage(`**${t('features.kursBuilder.messages.analysisFor', { name: contextName })}**\n\n${analysis.summary || ''}\n\n${selectedFileIds.value.length ? `📁 ${t('features.kursBuilder.messages.filesAnalyzed', { count: selectedFileIds.value.length })}` : ''}`)
      if (!isChapter && analysis.recommended_lms?.length) lmSuggestions.value = analysis.recommended_lms.map((lm: any) => ({ lm_id: lm.lm_id, name: lm.name, reason: lm.reason, confidence: lm.confidence || 0.8, icon: lm.icon || '📝', group: lm.group || 'B' }))
    }
  } catch { addSystemMessage(t('features.kursBuilder.messages.analysisErrorGeneric')) }
  finally { isAnalyzing.value = false }
}

async function generateTheory() {
  if (!selectedContext.value || !props.course) return
  isGeneratingTheory.value = true
  try {
    const isChapter = selectedContext.value.type === 'chapter'
    const prompt = isChapter ? `Erstelle eine Zusammenfassung für das Kapitel "${selectedContext.value.title}".` : `Erstelle ein detailliertes Theorieblatt für die Lektion "${selectedContext.value.title}".`
    selectedMode.value = isChapter ? 'chapter_summary' : 'lesson_theory'
    await sendMessage(prompt, selectedMode.value)
    addSystemMessage(t('features.kursBuilder.messages.generatingTheory', { title: selectedContext.value.title }))
  } catch { addSystemMessage(t('features.kursBuilder.messages.generatingTheoryError')) }
  finally { isGeneratingTheory.value = false }
}

function createLMFromSuggestion(suggestion: LMSuggestion) {
  const prompt = `Erstelle eine Lernmethode vom Typ "${suggestion.name}" (LM${String(suggestion.lm_id).padStart(2, '0')}) für die Lektion "${selectedContext.value?.title}". Begründung: ${suggestion.reason}`
  selectedMode.value = 'method'
  sendMessage(prompt, 'method')
}

// ============================================================================
// Confirmation Flow
// ============================================================================
function checkForGeneratedContent(response: any): PendingAction | null {
  if (!response.generated_content || !response.requires_confirmation) return null
  const entity = response.output_entity || 'chapter'
  let previewText = ''
  if (entity === 'chapter' && response.generated_content.title) {
    previewText = `Neues Kapitel: "${response.generated_content.title}"\n\n${response.generated_content.description || ''}\n\n${response.generated_content.lessons?.length ? `${response.generated_content.lessons.length} Lektionen` : ''}`
  } else if (entity === 'lesson' && response.generated_content.title) {
    previewText = `Neue Lektion: "${response.generated_content.title}"\n\n${response.generated_content.description || ''}`
  } else {
    previewText = typeof response.generated_content === 'string' ? response.generated_content.slice(0, 300) : JSON.stringify(response.generated_content, null, 2).slice(0, 300)
  }
  return { type: 'create', entity: entity as any, actionKey: response.action_key || 'unknown', generatedData: response.generated_content, previewText, parentChapter: selectedContext.value?.parentChapter, session_id: response.session_id }
}

async function confirmPendingAction() {
  if (!pendingAction.value || !session.value) return
  confirmLoading.value = true
  try {
    const action = pendingAction.value
    if (action.entity === 'chapter' && action.generatedData) {
      if (!draftStructure.value) draftStructure.value = { chapters: [] }
      if (!draftStructure.value.chapters) draftStructure.value.chapters = []
      const newChapter: Chapter = { id: `ch-${Date.now()}`, title: action.generatedData.title || 'Neues Kapitel', description: action.generatedData.description || '', lessons: (action.generatedData.lessons || []).map((l: any, i: number) => ({ id: `ls-${Date.now()}-${i}`, title: l.title || `Lektion ${i + 1}`, description: l.description || '', methods: l.methods || [] })) }
      draftStructure.value.chapters.push(newChapter)
      chatMessages.value.push({ role: 'assistant', content: `✅ Kapitel "${newChapter.title}" wurde erstellt mit ${newChapter.lessons?.length || 0} Lektionen.` })
    } else if (action.entity === 'lesson' && action.generatedData && action.parentChapter) {
      const chapter = draftStructure.value?.chapters?.find(c => c.id === action.parentChapter?.id)
      if (chapter) {
        if (!chapter.lessons) chapter.lessons = []
        const newLesson: Lesson = { id: `ls-${Date.now()}`, title: action.generatedData.title || 'Neue Lektion', description: action.generatedData.description || '', content: action.generatedData.content, methods: action.generatedData.methods || [] }
        chapter.lessons.push(newLesson)
        chatMessages.value.push({ role: 'assistant', content: `✅ Lektion "${newLesson.title}" wurde zum Kapitel "${chapter.title}" hinzugefügt.` })
      }
    }
    pendingAction.value = null
  } catch (err: any) { error.value = 'Fehler beim Speichern: ' + (err.message || 'Unbekannt') }
  finally { confirmLoading.value = false }
}

function rejectPendingAction() { chatMessages.value.push({ role: 'assistant', content: '❌ Aktion wurde verworfen.' }); pendingAction.value = null }
function modifyPendingAction() { inputMessage.value = 'Bitte ändere das Ergebnis. Folgende Anpassungen: '; pendingAction.value = null }

// ============================================================================
// Structure Actions
// ============================================================================
function openChapterPreview(chapter: Chapter) { panelStore.openPanel({ type: 'admin-chapter-preview', title: `Kapitel: ${chapter.title}`, icon: '📖', payload: { chapter: { chapter_id: chapter.id, title: chapter.title, description: chapter.description, lessons: chapter.lessons, created_at: new Date().toISOString() } }, size: { width: 650, height: 700 } }) }
function openLessonPreview(chapter: Chapter, lesson: Lesson) { const lessonIndex = chapter.lessons?.findIndex(l => l.id === lesson.id) ?? 0; panelStore.openPanel({ type: 'admin-lesson-preview', title: `Vorschau: ${lesson.title}`, icon: '📄', payload: { lesson: { lesson_id: lesson.id, title: lesson.title, description: lesson.description, content: lesson.content, duration_minutes: lesson.duration_minutes, methods: lesson.methods }, chapter: { chapter_id: chapter.id, title: chapter.title }, position: `${lessonIndex + 1}/${chapter.lessons?.length ?? 1}` }, size: { width: 600, height: 700 } }) }
function editChapter(chapter: Chapter) { console.log('Edit chapter:', chapter.id) }
function editLesson(chapter: Chapter, lesson: Lesson) { console.log('Edit lesson:', lesson.id, 'in chapter:', chapter.id) }
function deleteChapter(chapterId: string, chapterIndex: number) { if (!confirm('Kapitel wirklich löschen?') || !draftStructure.value?.chapters) return; draftStructure.value.chapters.splice(chapterIndex, 1) }
function deleteLesson(chapterId: string, chapterIndex: number, lessonId: string, lessonIndex: number) { if (!confirm('Lektion wirklich löschen?') || !draftStructure.value?.chapters?.[chapterIndex]?.lessons) return; draftStructure.value.chapters[chapterIndex].lessons!.splice(lessonIndex, 1) }

// ============================================================================
// File Management
// ============================================================================
function clearFileSelection() { selectedFileIds.value = [] }
function openFilePreview(file: CourseFile) { panelStore.openPanel({ type: 'admin-file-preview', title: `Vorschau: ${file.name}`, icon: '📄', payload: { file }, size: { width: 800, height: 600 } }) }
function triggerFileUpload() { materialFileInput.value?.click() }
async function handleMaterialUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length || !props.course) return
  isUploadingFile.value = true
  try {
    for (const file of Array.from(input.files)) {
      const formData = new FormData(); formData.append('file', file); formData.append('file_category', 'material')
      await http.post(`/admin/courses/${props.course.course_id}/files`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    }
    await loadCourseFiles()
  } catch (err) { console.error('File upload failed:', err) }
  finally { isUploadingFile.value = false; input.value = '' }
}

// ============================================================================
// Tutor Integration
// ============================================================================
function openTheoryInTutor(theory: { theoryId: string }) { panelStore.openPanel({ type: 'admin-ai-editor', title: 'KI-Studio: Tutor', icon: '🤖', payload: { tab: 'tutor', chapter: selectedContext.value?.data, theoryId: theory.theoryId }, size: { width: 1200, height: 800 } }) }
function openExplanationInTutor(expl: { explanationId: string }) { panelStore.openPanel({ type: 'admin-ai-editor', title: 'KI-Studio: Tutor', icon: '🤖', payload: { tab: 'tutor', lesson: selectedContext.value?.data, chapter: selectedContext.value?.parentChapter, explanationId: expl.explanationId }, size: { width: 1200, height: 800 } }) }

function resetState() { session.value = null; chatMessages.value = []; draftStructure.value = null; selectedFileIds.value = [] }

// Expose for parent
defineExpose({ sessionMeta: computed(() => session.value ? { sessionId: session.value.session_id, status: session.value.status, totalTokensUsed: session.value.total_tokens_used } : null), draftStats, createSession, hasSession: computed(() => !!session.value) })

// Mount
onMounted(async () => { await loadQuickActions(); if (props.course) { await loadExistingSession(); await loadCourseFiles(); await loadExistingStructure() } })
</script>

<style scoped>
.kurs-builder-tab { display: flex; flex-direction: column; height: 100%; background: var(--color-bg); }

/* Header */
.builder-header { display: flex; align-items: center; justify-content: space-between; padding: 0.875rem 1.25rem; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; }
.header-left { display: flex; align-items: center; gap: 0.75rem; }
.header-icon { font-size: 1.5rem; }
.header-title { font-size: 1rem; font-weight: 600; margin: 0; }
.header-meta { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.125rem; }
.course-badge, .stats-badge { font-size: 0.6875rem; padding: 0.125rem 0.5rem; background: rgba(255,255,255,0.2); border-radius: 1rem; }
.header-right { display: flex; align-items: center; gap: 1rem; }
.session-info { display: flex; align-items: center; gap: 0.375rem; font-size: 0.75rem; }
.session-dot { width: 8px; height: 8px; border-radius: 50%; }
.session-dot.active { background: #22c55e; }
.session-dot.inactive { background: rgba(255,255,255,0.4); }
.session-id { font-family: monospace; opacity: 0.7; }
.btn-primary, .btn-success { padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.8125rem; font-weight: 500; border: none; cursor: pointer; transition: all 0.15s; }
.btn-primary { background: rgba(255,255,255,0.2); color: white; }
.btn-primary:hover:not(:disabled) { background: rgba(255,255,255,0.3); }
.btn-success { background: #22c55e; color: white; }
.btn-success:hover:not(:disabled) { background: #16a34a; }
.btn-primary:disabled, .btn-success:disabled { opacity: 0.5; cursor: not-allowed; }

/* Empty State */
.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--color-text-secondary); }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.125rem; font-weight: 500; margin: 0; }
.empty-hint { font-size: 0.875rem; opacity: 0.7; margin: 0.25rem 0 0; }

/* Main Content */
.builder-content { flex: 1; display: flex; gap: 1rem; padding: 1rem; overflow: hidden; }
.chat-column { flex: 6; display: flex; flex-direction: column; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 0.75rem; overflow: hidden; }
.right-column { flex: 4; display: flex; flex-direction: column; gap: 1rem; min-width: 300px; }

/* Error Banner */
.error-banner { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; background: rgba(239, 68, 68, 0.1); border-top: 1px solid #ef4444; color: #ef4444; font-size: 0.875rem; }
.error-banner button { background: none; border: none; color: currentColor; font-size: 1.25rem; cursor: pointer; }
</style>
