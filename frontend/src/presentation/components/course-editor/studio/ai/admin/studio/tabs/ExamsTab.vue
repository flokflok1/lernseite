<!--
  ExamsTab - KI-Prüfungsgenerierung im AI Studio

  Features:
  - Datei-Browser für Kursmaterialien
  - Chat-Interface für Prüfungserstellung
  - Live KI-Aktivitätsanzeige
  - Prüfungsvorschau und Editor

  Phase: KI-Studio Prüfungs-Tab v2
  Refactored: Sub-components in ./exams/
-->

<template>
  <div class="exams-tab">
    <!-- No Course Selected -->
    <div v-if="!course" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>{{ $t('features.aiEditorExams.selectCourse') }}</h3>
      <p>{{ $t('features.aiEditorExams.selectCourseHint') }}</p>
    </div>

    <!-- Main Content -->
    <div v-else class="exams-content">
      <!-- Header -->
      <div class="exams-header">
        <div class="header-icon">📝</div>
        <div class="header-info">
          <h2>{{ $t('features.aiEditorExams.title') }}</h2>
          <p>{{ course.title }}</p>
        </div>
        <div class="header-stats">
          <div class="stat">
            <span class="stat-value">{{ courseFiles.length }}</span>
            <span class="stat-label">{{ $t('features.aiEditorExams.files') }}</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ selectedFiles.length }}</span>
            <span class="stat-label">{{ $t('features.aiEditorExams.selected') }}</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ totalQuestions }}</span>
            <span class="stat-label">{{ $t('features.aiEditorExams.questions') }}</span>
          </div>
        </div>
      </div>

      <!-- Three-Column Layout -->
      <div class="main-layout">
        <!-- Left: File Browser -->
        <FilesPanel
          :files="courseFiles"
          :selected-file-ids="selectedFiles"
          :selected-category="selectedCategory"
          :previewing-file-id="previewFile?.course_file_id"
          :is-loading="isLoadingFiles"
          :categories="fileCategories"
          @refresh="loadCourseFiles"
          @category-change="selectedCategory = $event"
          @toggle-selection="toggleFileSelection"
          @select-all="selectAllFiles"
          @clear-selection="clearFileSelection"
          @preview="openFilePreview"
        />

        <!-- Middle: Chat Interface -->
        <ChatPanel
          :messages="messages"
          :is-generating="isGenerating"
          :selected-files-count="selectedFiles.length"
          :selected-file-names="selectedFileNames"
          @send="sendMessage"
          @quick-prompt="useQuickPrompt"
        />

        <!-- Right: Activity Panel -->
        <ActivityPanel
          :current-activity="currentActivity"
          :activity-log="activityLog"
          :tokens-used="tokensUsed"
          :question-count="questionCount"
          :difficulty="difficulty"
          :duration-minutes="durationMinutes"
          @update:question-count="questionCount = $event"
          @update:difficulty="difficulty = $event"
          @update:duration-minutes="durationMinutes = $event"
        />
      </div>

      <!-- File Preview Modal -->
      <FilePreviewModal
        :file="previewFile"
        :file-url="previewFileUrl"
        :preview-content="previewContent"
        :is-selected="previewFile ? selectedFiles.includes(previewFile.course_file_id) : false"
        @close="closeFilePreview"
        @download="downloadFile"
        @toggle-selection="toggleFileSelection"
      />

      <!-- Generated Exam Preview -->
      <ExamPreviewPanel
        :exam="currentExam"
        @edit="editExam"
        @regenerate="regenerateExam"
        @save="saveExam"
        @close="currentExam = null"
        @edit-question="editQuestion"
        @regenerate-question="regenerateQuestion"
        @delete-question="deleteQuestion"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/api/http'
import { FilesPanel, ChatPanel, ActivityPanel, FilePreviewModal, ExamPreviewPanel } from '@/components/studio/assessment/admin/settings/exams'

const { t } = useI18n()

// Types
interface Course { course_id: string; title: string }
interface Chapter { chapter_id: string; title: string; order_index: number }
interface CourseFile {
  course_file_id: string; file_name: string; display_name?: string
  file_type: string; file_size_bytes: number; file_category: string
}
interface Question {
  type: 'mc' | 'free_text' | 'matching' | 'fill_blank'
  question: string; options?: string[]; correct_answer?: number | number[] | string
  sample_answer?: string; points?: number; source_file?: string
}
interface Exam { exam_id?: string; title: string; description?: string; duration: number; questions: Question[] }
interface ChatMessage { role: 'user' | 'assistant'; content: string; timestamp: Date }
interface ActivityItem { message: string; status: 'pending' | 'success' | 'error'; duration?: number }

interface Props { course?: Course | null; chapter?: Chapter | null; chapters?: Chapter[] }
const props = withDefaults(defineProps<Props>(), { course: null, chapter: null, chapters: () => [] })

// File categories
const fileCategories = computed(() => [
  { id: 'all', name: t('features.aiEditorExams.fileCategories.all'), icon: '📁' },
  { id: 'script', name: t('features.aiEditorExams.fileCategories.script'), icon: '📖' },
  { id: 'material', name: t('features.aiEditorExams.fileCategories.material'), icon: '📚' },
  { id: 'exercise', name: t('features.aiEditorExams.fileCategories.exercise'), icon: '✏️' },
  { id: 'solution', name: t('features.aiEditorExams.fileCategories.solution'), icon: '✅' },
  { id: 'reference', name: t('features.aiEditorExams.fileCategories.reference'), icon: '📎' }
])

// State
const courseFiles = ref<CourseFile[]>([])
const selectedFiles = ref<string[]>([])
const selectedCategory = ref('all')
const isLoadingFiles = ref(false)
const previewFile = ref<CourseFile | null>(null)
const previewContent = ref('')

const messages = ref<ChatMessage[]>([])
const isGenerating = ref(false)
const currentActivity = ref<string | null>(null)
const activityLog = ref<ActivityItem[]>([])
const tokensUsed = ref(0)

const questionCount = ref(10)
const difficulty = ref('mixed')
const durationMinutes = ref(30)

const currentExam = ref<Exam | null>(null)
const generatedExams = ref<Exam[]>([])

// Computed
const selectedFileNames = computed(() =>
  selectedFiles.value.map(id => {
    const file = courseFiles.value.find(f => f.course_file_id === id)
    return file?.display_name || file?.file_name || id
  })
)

const totalQuestions = computed(() =>
  generatedExams.value.reduce((sum, exam) => sum + (exam.questions?.length || 0), 0)
)

const previewFileUrl = computed(() =>
  previewFile.value ? `/api/v1/admin/courses/${props.course?.course_id}/files/${previewFile.value.course_file_id}/download` : ''
)

// Methods
async function loadCourseFiles() {
  if (!props.course) return
  isLoadingFiles.value = true
  try {
    const response = await http.get(`/admin/courses/${props.course.course_id}/files`)
    if (response.data.success) courseFiles.value = response.data.files || []
  } catch (error) {
    console.error('Failed to load course files:', error)
    courseFiles.value = []
  } finally {
    isLoadingFiles.value = false
  }
}

function toggleFileSelection(file: CourseFile) {
  const idx = selectedFiles.value.indexOf(file.course_file_id)
  idx >= 0 ? selectedFiles.value.splice(idx, 1) : selectedFiles.value.push(file.course_file_id)
}

function selectAllFiles() {
  const filtered = selectedCategory.value === 'all'
    ? courseFiles.value
    : courseFiles.value.filter(f => f.file_category === selectedCategory.value)
  selectedFiles.value = filtered.map(f => f.course_file_id)
}

function clearFileSelection() { selectedFiles.value = [] }

async function openFilePreview(file: CourseFile) {
  previewFile.value = file
  previewContent.value = ''
  const textTypes = ['text/plain', 'text/markdown', 'text/csv', 'application/json']
  if (textTypes.some(t => file.file_type?.includes(t)) || file.file_name?.endsWith('.txt')) {
    try {
      const response = await http.get(previewFileUrl.value, { responseType: 'text' })
      previewContent.value = response.data
    } catch { previewContent.value = t('features.aiEditorExams.loadFileError') }
  }
}

function closeFilePreview() { previewFile.value = null; previewContent.value = '' }
function downloadFile(file: CourseFile) { window.open(`/api/v1/admin/courses/${props.course?.course_id}/files/${file.course_file_id}/download`, '_blank') }

function useQuickPrompt(type: string) {
  const fileContext = selectedFiles.value.length > 0 ? ` basierend auf den ${selectedFiles.value.length} ausgewählten Dateien` : ''
  const prompts: Record<string, string> = {
    'from_files': `Erstelle ${questionCount.value} Prüfungsfragen aus den ausgewählten Kursmaterialien.`,
    'exam_mc': `Erstelle ${questionCount.value} Multiple-Choice Fragen${fileContext}. Jede Frage soll 4 Antwortmöglichkeiten haben.`,
    'exam_ihk': `Erstelle eine IHK-konforme Prüfung mit ${durationMinutes.value} Minuten Bearbeitungszeit${fileContext}.`,
    'exam_mixed': `Erstelle eine gemischte Prüfung mit ${questionCount.value} Fragen${fileContext}: 60% MC, 30% Freitext, 10% Zuordnung.`
  }
  sendMessage(prompts[type] || '')
}

async function sendMessage(content: string) {
  if (!content.trim() || isGenerating.value) return
  messages.value.push({ role: 'user', content: content.trim(), timestamp: new Date() })
  await generateExam(content)
}

async function generateExam(prompt: string) {
  isGenerating.value = true
  currentActivity.value = t('features.aiEditorExams.analyzing')
  activityLog.value = []
  const startTime = Date.now()

  try {
    if (selectedFiles.value.length > 0) addActivity(t('features.aiEditorExams.analyzingFiles', { count: selectedFiles.value.length }), 'pending')
    addActivity(t('features.aiEditorExams.generatingQuestions'), 'pending')

    const response = await http.post('/admin/ai/generate-exam', {
      course_id: props.course?.course_id, chapter_id: props.chapter?.chapter_id, prompt,
      exam_type: 'mixed', question_count: questionCount.value, duration_minutes: durationMinutes.value,
      difficulty: difficulty.value, source_files: selectedFiles.value, source_file_names: selectedFileNames.value.join(', ')
    })

    if (response.data.success) {
      const data = response.data.data
      updateLastActivity(t('features.aiEditorExams.questionsGenerated'), 'success', Date.now() - startTime)
      tokensUsed.value += data.tokens_used || 0
      currentExam.value = { title: data.title || 'Generierte Prüfung', description: data.description, duration: data.duration_minutes || durationMinutes.value, questions: data.questions || [] }

      messages.value.push({
        role: 'assistant',
        content: `Ich habe eine Prüfung mit **${data.questions?.length || 0} Fragen** erstellt:\n\n📝 **${data.title || 'Prüfung'}**\n⏱️ Dauer: ${data.duration_minutes || durationMinutes.value} Minuten`,
        timestamp: new Date()
      })
    } else throw new Error(response.data.error?.message || 'Generierung fehlgeschlagen')
  } catch (error: any) {
    updateLastActivity(t('features.aiEditorExams.generationError'), 'error', Date.now() - startTime)
    messages.value.push({ role: 'assistant', content: `❌ Fehler: ${error.response?.data?.error?.message || error.message}`, timestamp: new Date() })
  } finally {
    isGenerating.value = false
    currentActivity.value = null
  }
}

function addActivity(message: string, status: 'pending' | 'success' | 'error', duration?: number) {
  activityLog.value.push({ message, status, duration })
}

function updateLastActivity(message: string, status: 'pending' | 'success' | 'error', duration: number) {
  if (activityLog.value.length > 0) Object.assign(activityLog.value[activityLog.value.length - 1], { message, status, duration })
}

function editExam() { console.log('Edit exam:', currentExam.value) }
function regenerateExam() {
  const lastUserMsg = [...messages.value].reverse().find(m => m.role === 'user')
  if (lastUserMsg) generateExam(lastUserMsg.content)
}

async function saveExam() {
  if (!currentExam.value || !props.course) return
  try {
    const response = await http.post('/admin/exams', {
      course_id: props.course.course_id, chapter_id: props.chapter?.chapter_id,
      title: currentExam.value.title, description: currentExam.value.description,
      duration_minutes: currentExam.value.duration, questions: currentExam.value.questions, exam_type: 'ai_generated'
    })
    if (response.data.success) {
      generatedExams.value.unshift({ ...currentExam.value, exam_id: response.data.data.exam_id })
      messages.value.push({ role: 'assistant', content: `✅ Prüfung **"${currentExam.value.title}"** erfolgreich gespeichert!`, timestamp: new Date() })
      currentExam.value = null
    }
  } catch (error: any) {
    messages.value.push({ role: 'assistant', content: `❌ Fehler beim Speichern: ${error.response?.data?.error?.message || error.message}`, timestamp: new Date() })
  }
}

function editQuestion(idx: number) { console.log('Edit question:', idx) }
async function regenerateQuestion(idx: number) {
  if (!currentExam.value) return
  const question = currentExam.value.questions[idx]
  currentActivity.value = t('features.aiEditorExams.regeneratingQuestion', { num: idx + 1 })
  try {
    const response = await http.post('/admin/ai/regenerate-question', { course_id: props.course?.course_id, chapter_id: props.chapter?.chapter_id, question_type: question.type, context: question.question, source_files: selectedFiles.value })
    if (response.data.success && response.data.data.question) {
      currentExam.value.questions[idx] = response.data.data.question
      tokensUsed.value += response.data.data.tokens_used || 0
    }
  } catch (error) { console.error('Failed to regenerate:', error) }
  finally { currentActivity.value = null }
}

function deleteQuestion(idx: number) {
  if (!currentExam.value) return
  if (confirm(t('features.aiEditorExams.confirmDeleteQuestion'))) currentExam.value.questions.splice(idx, 1)
}

watch(() => props.course, () => {
  messages.value = []; currentExam.value = null; courseFiles.value = []; selectedFiles.value = []
  activityLog.value = []; tokensUsed.value = 0; loadCourseFiles()
}, { immediate: true })

onMounted(() => loadCourseFiles())
</script>

<style scoped>
.exams-tab { height: 100%; overflow-y: auto; padding: 1rem; }

/* Empty State */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; text-align: center; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-state h3 { color: var(--color-text-primary); margin: 0 0 0.5rem; }
.empty-state p { color: var(--color-text-secondary); margin: 0; }

/* Header */
.exams-header { display: flex; align-items: center; gap: 1rem; padding: 1rem; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 1rem; margin-bottom: 1rem; }
.header-icon { width: 56px; height: 56px; background: rgba(255,255,255,0.2); border-radius: 1rem; display: flex; align-items: center; justify-content: center; font-size: 1.75rem; }
.header-info { flex: 1; }
.header-info h2 { color: white; font-size: 1.25rem; font-weight: 700; margin: 0; }
.header-info p { color: rgba(255,255,255,0.8); font-size: 0.875rem; margin: 0.25rem 0 0; }
.header-stats { display: flex; gap: 1.5rem; }
.stat { text-align: center; }
.stat-value { display: block; font-size: 1.5rem; font-weight: 700; color: white; }
.stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.7); }

/* Three-Column Layout */
.main-layout { display: grid; grid-template-columns: 280px 1fr 280px; gap: 1rem; margin-bottom: 1rem; }

/* Responsive */
@media (max-width: 1200px) {
  .main-layout { grid-template-columns: 1fr; }
}
</style>
