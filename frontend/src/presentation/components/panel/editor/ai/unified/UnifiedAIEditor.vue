<!--
  UnifiedAIEditor — Tab-based orchestrator for AI-powered course creation.

  Layout: Top bar (course selector + phase badge)
          → Main area: [Tab bar + Active tab content | Structure sidebar]
  Tabs: Chat, Files, Plan, Skills, Prompts, History
  Structure sidebar is always visible on the right for context selection.
-->
<template>
  <div class="unified-ai-editor">
    <!-- Course selector (top bar) -->
    <div class="editor-topbar">
      <select
        v-model="selectedCourseId"
        class="course-select"
        :class="{ 'highlight-pulse': highlightCourseSelect }"
        @change="handleCourseChange"
        @animationend="highlightCourseSelect = false"
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
      <!-- Model selector (compact inline) -->
      <div v-if="modelSelector.providers.value.length > 0" class="model-selector">
        <select
          :value="modelSelector.selectedProvider.value"
          class="model-select"
          @change="modelSelector.handleProviderChange(($event.target as HTMLSelectElement).value)"
        >
          <option v-for="p in modelSelector.providers.value" :key="p.provider_name" :value="p.provider_name">
            {{ p.display_name }}
          </option>
        </select>
        <select v-model="modelSelector.selectedModel.value" class="model-select">
          <option v-for="m in modelSelector.currentModels.value" :key="m.model_name" :value="m.model_name">
            {{ m.display_name }}
          </option>
        </select>
      </div>
      <!-- Quality level selector -->
      <QualityLevelSelector v-if="qualityLevel.levels.value.length > 0" />
      <button
        v-if="chatSession.hasSession.value"
        class="new-session-btn"
        :title="$t('aiEditor.chat.newSession', 'Neue Session')"
        @click="handleNewSession"
      >
        ↻ {{ $t('aiEditor.chat.newSession', 'Neue Session') }}
      </button>
      <span v-if="chatSession.hasSession.value" class="session-badge">
        {{ $t('aiEditor.phase.' + workflowPhase.phase.value) }}
      </span>
      <span v-if="structureView.contextLabel.value" class="context-badge">
        {{ $t('aiEditor.chat.contextLabel') }}: {{ structureView.contextLabel.value }}
        <button class="context-clear" @click="structureView.clearContext()">×</button>
      </span>
    </div>

    <!-- Main area: tabs + content | structure sidebar -->
    <div class="editor-main">
      <!-- Left: Tabs + content -->
      <div class="editor-left">
        <EditorTabBar
          :tabs="editorState.tabs.value"
          :active-tab="editorState.activeTab.value"
          @select-tab="editorState.setTab($event)"
        />
        <div class="tab-content">
          <KeepAlive>
            <ChatTab
              v-if="editorState.activeTab.value === 'chat'"
              @new-course="handleNewCourse"
              @load-course="handleLoadCourse"
              @send="handleSend"
              @attach-file="handleAttachFile"
              @confirm="handleConfirmation"
            />
            <CourseTab v-else-if="editorState.activeTab.value === 'course'" :course-id="selectedCourseId" @deleted="handleCourseDeleted" />
            <FilesTab v-else-if="editorState.activeTab.value === 'files'" />
            <PlanTab v-else-if="editorState.activeTab.value === 'plan'" :course-id="selectedCourseId" :has-files="editorState.fileCount.value > 0" :file-ids="fileUpload.files.value.map((f: any) => f.file_id)" @refresh-structure="structureView.loadCourseStructure(selectedCourseId)" />
            <SkillsTab v-else-if="editorState.activeTab.value === 'skills'" :course-id="selectedCourseId" />
            <PromptsTab v-else-if="editorState.activeTab.value === 'prompts'" />
            <HistoryTab v-else-if="editorState.activeTab.value === 'history'" :course-id="selectedCourseId" />
            <ExamTab v-else-if="editorState.activeTab.value === 'exam'" />
          </KeepAlive>
        </div>
      </div>

      <!-- Right: Persistent structure sidebar -->
      <div class="editor-sidebar">
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
          @select-context="(type: 'chapter' | 'lesson', id: string, title: string) => handleSelectContext({ type, id, title })"
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
import { ref, onMounted, provide, computed, watch, KeepAlive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useChatSession } from './composables/generation/useChatSession'
import { useStructureView } from './composables/editor/useStructureView'
import { useWorkflowPhase } from './composables/plan/useWorkflowPhase'
import { useEditorState } from './composables/editor/useEditorState'
import { useFileUpload } from './composables/editor/useFileUpload'
import { useGenerationHistory } from './composables/generation/useGenerationHistory'
import { useModelSelector } from './composables/editor/useModelSelector'
import { useQualityLevel } from './composables/plan/useQualityLevel'
import QualityLevelSelector from './components/QualityLevelSelector.vue'
import { ChatTab, FilesTab, PromptsTab, PlanTab, SkillsTab, HistoryTab, CourseTab, ExamTab } from './tabs'
import { RightPanel } from './right-panel'
import EditorTabBar from './components/EditorTabBar.vue'
import type { ChatConfirmation } from './types'
import { listEditorCourses, createCourse } from '@/infrastructure/api/clients/panel/editor'

const props = defineProps<{
  courseId?: string
}>()

const { t } = useI18n()

// ---- Composables ----
const chatSession = useChatSession()
const structureView = useStructureView()
const workflowPhase = useWorkflowPhase()
const editorState = useEditorState()

const generationHistory = useGenerationHistory()
const modelSelector = useModelSelector()
const qualityLevel = useQualityLevel()
const sessionId = computed(() => chatSession.session.value?.sessionId ?? null)
const fileUpload = useFileUpload(sessionId)

// Sync file count to editorState for tab badge
watch(() => fileUpload.files.value.length, (count) => {
  editorState.fileCount.value = count
})

// Provide for child components that need direct access
provide('chatSession', chatSession)
provide('structureView', structureView)
provide('workflowPhase', workflowPhase)
provide('editorState', editorState)
provide('fileUpload', fileUpload)
provide('generationHistory', generationHistory)
provide('modelSelector', modelSelector)
provide('qualityLevel', qualityLevel)
provide('onCourseCreated', handleExamCourseCreated)

// ---- Local state ----
const courses = ref<Array<{ id: string; title: string }>>([])
const highlightCourseSelect = ref(false)
const selectedCourseId = ref(props.courseId || '')

// ---- Lifecycle ----
onMounted(async () => {
  try {
    const result = await listEditorCourses()
    courses.value = (result || []).map((c) => ({
      id: String(c.course_id),
      title: c.title,
    }))
  } catch (e: unknown) {
    console.warn('[AIEditor] Failed to load courses:', e)
    courses.value = []
  }

  // Load available AI models and quality levels
  modelSelector.loadAvailableModels()
  qualityLevel.loadQualityLevels()

  if (props.courseId) {
    const course = courses.value.find(c => c.id === props.courseId)
    await Promise.all([
      chatSession.loadOrCreateSession(props.courseId, getModelOptions()),
      structureView.loadCourseStructure(props.courseId, course?.title ?? ''),
    ])
  }
})

// ---- Helpers ----
function getModelOptions() {
  const prov = modelSelector.selectedProvider.value
  const mod = modelSelector.selectedModel.value
  return prov && mod ? { providerName: prov, modelName: mod } : undefined
}

// ---- Handlers ----

async function handleCourseChange(): Promise<void> {
  if (!selectedCourseId.value) return
  chatSession.clearSession()
  structureView.clearStructure()
  workflowPhase.reset()

  // Load real course structure + AI session in parallel
  const course = courses.value.find(c => c.id === selectedCourseId.value)
  await Promise.all([
    chatSession.loadOrCreateSession(selectedCourseId.value, getModelOptions()),
    structureView.loadCourseStructure(selectedCourseId.value, course?.title ?? ''),
  ])
}

async function handleNewCourse(): Promise<void> {
  try {
    const draftTitle = t('aiEditor.chat.newCourseDraft', 'Neuer KI-Kurs')
    const course = await createCourse({ title: draftTitle })
    const id = String(course.course_id)
    courses.value.push({ id, title: draftTitle })
    selectedCourseId.value = id

    chatSession.clearSession()
    structureView.clearStructure()
    workflowPhase.reset()

    await chatSession.loadOrCreateSession(id, getModelOptions())
  } catch (e: unknown) {
    console.warn('[AIEditor] Failed to create course:', e)
    chatSession.addSystemMessage(t('aiEditor.chat.createCourseFailed', 'Kurs konnte nicht erstellt werden.'))
  }
}

async function handleNewSession(): Promise<void> {
  if (!selectedCourseId.value) return
  chatSession.clearSession()
  structureView.clearStructure()
  workflowPhase.reset()
  const course = courses.value.find(c => c.id === selectedCourseId.value)
  await Promise.all([
    chatSession.createSession(selectedCourseId.value, getModelOptions()),
    structureView.loadCourseStructure(selectedCourseId.value, course?.title ?? ''),
  ])
}

async function handleLoadCourse(): Promise<void> {
  if (selectedCourseId.value) {
    await handleCourseChange()
  } else {
    highlightCourseSelect.value = true
  }
}

async function handleSend(content: string): Promise<void> {
  const ctx = structureView.selectedContext.value
  const contextHint = ctx
    ? `[Kontext: ${ctx.type === 'chapter' ? 'Kapitel' : 'Lektion'} "${ctx.title}" (ID: ${ctx.id})]\n`
    : undefined
  const focusContext = ctx ? { type: ctx.type, id: ctx.id } : undefined
  const result = await chatSession.sendMessage(
    content, undefined, contextHint, focusContext,
    qualityLevel.selectedLevel.value
  )

  // Refresh structure sidebar if operations were applied
  if (result?.operations?.length && selectedCourseId.value) {
    const course = courses.value.find(c => c.id === selectedCourseId.value)
    await structureView.loadCourseStructure(selectedCourseId.value, course?.title ?? '')
  }
}

function handleAttachFile(): void {
  editorState.setTab('files')
}

function handleSelectContext(payload: { type: 'chapter' | 'lesson'; id: string; title: string }): void {
  structureView.setContext(payload.type, payload.id, payload.title)
  chatSession.addSystemMessage(t('aiEditor.chat.contextSet', { type: payload.type, title: payload.title }))
}

async function handleFinalize(): Promise<void> {
  if (!chatSession.session.value) return
  structureView.isFinalizing.value = true
  const success = await workflowPhase.finalize(chatSession.session.value.sessionId)
  structureView.isFinalizing.value = false
  if (success) {
    chatSession.addSystemMessage(t('aiEditor.structure.finalizeSuccess'))
  }
}

async function handleConfirmation(confirmation: ChatConfirmation): Promise<void> {
  if (confirmation.skillCode && chatSession.courseId.value) {
    await workflowPhase.startGenerate(
      confirmation.skillCode,
      chatSession.courseId.value,
      {
        targetId: confirmation.targetId,
        parameters: confirmation.params,
      }
    )
  }
}

function handleAcceptResult(): void {
  const result = workflowPhase.acceptResult()
  if (result) {
    generationHistory.addEntry({
      generation_id: result.generationId || `gen-${Date.now()}`,
      plan_id: null,
      skill_code: result.skillCode || 'unknown',
      course_id: selectedCourseId.value,
      target_type: result.targetType || null,
      target_id: result.targetId || null,
      tokens_input: result.tokensInput || 0,
      tokens_output: result.tokensOutput || 0,
      model_name: result.modelName || '',
      provider_name: '',
      status: 'completed',
      created_at: new Date().toISOString(),
    })
  }
  chatSession.addSystemMessage(t('aiEditor.result.accepted'))
}

function handleRejectResult(): void {
  workflowPhase.rejectResult()
  chatSession.addSystemMessage(t('aiEditor.result.rejected'))
}

function handleReviseResult(): void {
  workflowPhase.setPhase('plan')
  chatSession.addSystemMessage(t('aiEditor.result.revisePrompt'))
}

async function handleExamCourseCreated(courseId: string, courseTitle: string): Promise<void> {
  // Add to local courses list and select it
  const id = String(courseId)
  if (!courses.value.find(c => c.id === id)) {
    courses.value.push({ id, title: courseTitle })
  }
  selectedCourseId.value = id

  // Load course structure in sidebar
  chatSession.clearSession()
  structureView.clearStructure()
  workflowPhase.reset()

  await Promise.all([
    chatSession.loadOrCreateSession(id, getModelOptions()),
    structureView.loadCourseStructure(id, courseTitle),
  ])
}

function handleCourseDeleted(courseId: string): void {
  courses.value = courses.value.filter(c => c.id !== courseId)
  selectedCourseId.value = ''
  chatSession.clearSession()
  structureView.clearStructure()
  workflowPhase.reset()
  editorState.setTab('chat')
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

.model-selector {
  display: flex;
  gap: 0.375rem;
  align-items: center;
}

.model-select {
  max-width: 160px;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.8125rem;
}

.new-session-btn {
  padding: 0.25rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 600;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}

.new-session-btn:hover {
  background: var(--color-primary-subtle, rgba(99, 102, 241, 0.08));
  border-color: var(--color-primary, #6366f1);
  color: var(--color-primary, #6366f1);
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

.context-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  background: var(--color-surface-secondary, var(--color-surface));
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  color: var(--color-text-secondary);
}

.context-clear {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0;
  line-height: 1;
}

.context-clear:hover {
  color: var(--color-danger, #e53e3e);
}

.editor-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.editor-left {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.tab-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-sidebar {
  width: 320px;
  flex-shrink: 0;
  border-left: 1px solid var(--color-border);
  overflow: hidden;
}

.course-select.highlight-pulse {
  animation: pulse-border 1.5s ease-out;
}

@keyframes pulse-border {
  0% { border-color: #3b82f6; box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.6); }
  50% { border-color: #3b82f6; box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.25); }
  100% { border-color: var(--color-border); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
}
</style>
