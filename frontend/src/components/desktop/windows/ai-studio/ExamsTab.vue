<!--
  Exams Tab - KI-Prüfungsgenerierung im AI Studio

  Features:
  - Datei-Browser für Kursmaterialien (PDF, TXT, PowerPoint)
  - Datei-Vorschau
  - Chat-Interface für Prüfungserstellung
  - Live KI-Aktivitätsanzeige
  - Prüfungsvorschau und Editor

  Phase: KI-Studio Prüfungs-Tab v2
  Created: 2025-12-18
-->

<template>
  <div class="exams-tab">
    <!-- No Course Selected -->
    <div v-if="!course" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>Kurs auswählen</h3>
      <p>Wähle einen Kurs aus, um Prüfungen zu erstellen.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="exams-content">
      <!-- Header -->
      <div class="exams-header">
        <div class="header-icon">📝</div>
        <div class="header-info">
          <h2>KI-Prüfungsgenerator</h2>
          <p>{{ course.title }}</p>
        </div>
        <div class="header-stats">
          <div class="stat">
            <span class="stat-value">{{ courseFiles.length }}</span>
            <span class="stat-label">Dateien</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ selectedFiles.length }}</span>
            <span class="stat-label">Ausgewählt</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ totalQuestions }}</span>
            <span class="stat-label">Fragen</span>
          </div>
        </div>
      </div>

      <!-- Three-Column Layout -->
      <div class="main-layout">
        <!-- Left: File Browser -->
        <div class="files-panel">
          <div class="panel-header">
            <span class="panel-icon">📁</span>
            <span class="panel-title">Kursmaterialien</span>
            <button @click="loadCourseFiles" class="refresh-btn" title="Aktualisieren">🔄</button>
          </div>

          <!-- File Categories -->
          <div class="file-categories">
            <button
              v-for="cat in fileCategories"
              :key="cat.id"
              @click="selectedCategory = cat.id"
              class="category-btn"
              :class="{ active: selectedCategory === cat.id }"
            >
              <span class="cat-icon">{{ cat.icon }}</span>
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-count">{{ getCategoryCount(cat.id) }}</span>
            </button>
          </div>

          <!-- File List -->
          <div class="file-list">
            <div v-if="isLoadingFiles" class="loading-files">
              <div class="spinner"></div>
              <span>Lade Dateien...</span>
            </div>

            <div v-else-if="filteredFiles.length === 0" class="no-files">
              <span class="no-files-icon">📭</span>
              <p>Keine Dateien in dieser Kategorie</p>
            </div>

            <div
              v-for="file in filteredFiles"
              :key="file.course_file_id"
              class="file-item"
              :class="{ selected: selectedFiles.includes(file.course_file_id), previewing: previewFile?.course_file_id === file.course_file_id }"
            >
              <label class="file-checkbox">
                <input
                  type="checkbox"
                  :checked="selectedFiles.includes(file.course_file_id)"
                  @change="toggleFileSelection(file)"
                />
              </label>
              <div class="file-icon">{{ getFileIcon(file.file_type) }}</div>
              <div class="file-info" @click="openFilePreview(file)">
                <span class="file-name">{{ file.display_name || file.file_name }}</span>
                <span class="file-meta">
                  {{ formatFileSize(file.file_size_bytes) }} • {{ file.file_category }}
                </span>
              </div>
              <button @click="openFilePreview(file)" class="preview-btn" title="Vorschau">
                👁️
              </button>
            </div>
          </div>

          <!-- Select All / Clear -->
          <div class="file-actions">
            <button @click="selectAllFiles" class="action-link">
              ✓ Alle auswählen
            </button>
            <button @click="clearFileSelection" class="action-link">
              ✗ Auswahl löschen
            </button>
          </div>
        </div>

        <!-- Middle: Chat Interface -->
        <div class="chat-panel">
          <div class="panel-header">
            <span class="panel-icon">💬</span>
            <span class="panel-title">KI-Chat</span>
            <span v-if="selectedFiles.length > 0" class="files-indicator">
              {{ selectedFiles.length }} Datei(en) als Kontext
            </span>
          </div>

          <!-- Chat Messages -->
          <div class="chat-messages" ref="chatMessagesRef">
            <!-- Welcome Message -->
            <div v-if="messages.length === 0" class="welcome-message">
              <div class="welcome-icon">🤖</div>
              <h4>Prüfungs-Assistent</h4>
              <p>Ich erstelle Prüfungen basierend auf deinen Kursmaterialien.</p>

              <div v-if="selectedFiles.length > 0" class="selected-files-info">
                <strong>{{ selectedFiles.length }} Datei(en) ausgewählt:</strong>
                <ul>
                  <li v-for="fileId in selectedFiles.slice(0, 3)" :key="fileId">
                    {{ getFileName(fileId) }}
                  </li>
                  <li v-if="selectedFiles.length > 3">
                    ... und {{ selectedFiles.length - 3 }} weitere
                  </li>
                </ul>
              </div>

              <div class="welcome-hints">
                <p>Beispiele:</p>
                <ul>
                  <li>"Erstelle 10 MC-Fragen aus den ausgewählten Dateien"</li>
                  <li>"IHK-Prüfung basierend auf dem Skript"</li>
                  <li>"Freitext-Fragen zu den wichtigsten Themen"</li>
                </ul>
              </div>
            </div>

            <!-- Messages -->
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="chat-message"
              :class="msg.role"
            >
              <div class="message-avatar">
                {{ msg.role === 'user' ? '👤' : '🤖' }}
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
                <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
              </div>
            </div>

            <!-- Typing Indicator -->
            <div v-if="isGenerating" class="typing-indicator">
              <div class="message-avatar">🤖</div>
              <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>

          <!-- Chat Input -->
          <div class="chat-input-area">
            <div class="input-wrapper">
              <textarea
                v-model="userInput"
                @keydown.enter.exact.prevent="sendMessage"
                placeholder="Beschreibe die gewünschte Prüfung..."
                rows="2"
                :disabled="isGenerating"
              ></textarea>
              <button
                @click="sendMessage"
                class="send-btn"
                :disabled="!userInput.trim() || isGenerating"
              >
                <svg v-if="!isGenerating" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                <span v-else class="loading-spinner"></span>
              </button>
            </div>

            <!-- Quick Actions -->
            <div class="quick-prompts">
              <button @click="useQuickPrompt('from_files')" class="quick-btn" :disabled="selectedFiles.length === 0">
                📄 Aus Dateien
              </button>
              <button @click="useQuickPrompt('exam_mc')" class="quick-btn">
                ✅ MC-Fragen
              </button>
              <button @click="useQuickPrompt('exam_ihk')" class="quick-btn">
                🎓 IHK-Stil
              </button>
              <button @click="useQuickPrompt('exam_mixed')" class="quick-btn">
                🎯 Gemischt
              </button>
            </div>
          </div>
        </div>

        <!-- Right: Activity Panel -->
        <div class="activity-panel">
          <div class="panel-header">
            <span class="panel-icon">📊</span>
            <span class="panel-title">KI-Aktivität</span>
          </div>

          <!-- Activity Log -->
          <div class="activity-log">
            <!-- Current Activity -->
            <div v-if="currentActivity" class="current-activity">
              <div class="activity-spinner"></div>
              <span>{{ currentActivity }}</span>
            </div>

            <!-- Activity Items -->
            <div v-for="(activity, idx) in activityLog" :key="idx" class="activity-item" :class="activity.status">
              <span class="activity-icon">{{ getActivityIcon(activity.status) }}</span>
              <span class="activity-text">{{ activity.message }}</span>
              <span v-if="activity.duration" class="activity-time">{{ activity.duration }}ms</span>
            </div>

            <!-- Empty State -->
            <div v-if="!currentActivity && activityLog.length === 0" class="activity-empty">
              <span class="empty-icon">⏳</span>
              <p>Noch keine Aktivität</p>
            </div>
          </div>

          <!-- Token Usage -->
          <div class="token-usage">
            <div class="usage-header">
              <span>Token-Verbrauch</span>
              <span class="usage-value">{{ tokensUsed.toLocaleString() }}</span>
            </div>
            <div class="usage-bar">
              <div class="usage-fill" :style="{ width: `${Math.min(tokensUsed / 100, 100)}%` }"></div>
            </div>
            <div class="usage-cost">
              Geschätzte Kosten: {{ estimatedCost.toFixed(4) }}€
            </div>
          </div>

          <!-- Generation Settings -->
          <div class="gen-settings">
            <h4>Einstellungen</h4>
            <div class="setting-row">
              <label>Anzahl Fragen:</label>
              <select v-model="questionCount">
                <option :value="5">5 Fragen</option>
                <option :value="10">10 Fragen</option>
                <option :value="15">15 Fragen</option>
                <option :value="20">20 Fragen</option>
              </select>
            </div>
            <div class="setting-row">
              <label>Schwierigkeit:</label>
              <select v-model="difficulty">
                <option value="easy">Einfach</option>
                <option value="medium">Mittel</option>
                <option value="hard">Schwer</option>
                <option value="mixed">Gemischt</option>
              </select>
            </div>
            <div class="setting-row">
              <label>Dauer (Min):</label>
              <input type="number" v-model="durationMinutes" min="5" max="180" />
            </div>
          </div>
        </div>
      </div>

      <!-- File Preview Modal -->
      <div v-if="previewFile" class="file-preview-modal" @click.self="closeFilePreview">
        <div class="preview-container">
          <div class="preview-header">
            <div class="preview-file-info">
              <span class="preview-icon">{{ getFileIcon(previewFile.file_type) }}</span>
              <div>
                <h3>{{ previewFile.display_name || previewFile.file_name }}</h3>
                <p>{{ formatFileSize(previewFile.file_size_bytes) }} • {{ previewFile.file_category }}</p>
              </div>
            </div>
            <div class="preview-actions">
              <button @click="downloadFile(previewFile)" class="preview-action-btn">
                ⬇️ Download
              </button>
              <button @click="toggleFileSelection(previewFile)" class="preview-action-btn" :class="{ selected: selectedFiles.includes(previewFile.course_file_id) }">
                {{ selectedFiles.includes(previewFile.course_file_id) ? '✓ Ausgewählt' : '+ Auswählen' }}
              </button>
              <button @click="closeFilePreview" class="preview-close-btn">✕</button>
            </div>
          </div>
          <div class="preview-content">
            <!-- PDF Preview -->
            <iframe
              v-if="previewFile.file_type === 'application/pdf'"
              :src="getFileUrl(previewFile)"
              class="pdf-preview"
            ></iframe>

            <!-- Image Preview -->
            <img
              v-else-if="previewFile.file_type?.startsWith('image/')"
              :src="getFileUrl(previewFile)"
              class="image-preview"
            />

            <!-- Text Preview -->
            <pre v-else-if="isTextFile(previewFile)" class="text-preview">{{ previewContent }}</pre>

            <!-- No Preview Available -->
            <div v-else class="no-preview">
              <span class="no-preview-icon">📄</span>
              <p>Vorschau nicht verfügbar für diesen Dateityp</p>
              <p class="file-type">{{ previewFile.file_type }}</p>
              <button @click="downloadFile(previewFile)" class="download-btn">
                ⬇️ Datei herunterladen
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Generated Exam Preview -->
      <div v-if="currentExam" class="exam-preview">
        <div class="preview-header">
          <div class="preview-title">
            <span class="preview-icon">📋</span>
            <div>
              <h3>{{ currentExam.title || 'Generierte Prüfung' }}</h3>
              <p>{{ currentExam.questions?.length || 0 }} Fragen • {{ currentExam.duration || 30 }} Minuten</p>
            </div>
          </div>
          <div class="preview-actions">
            <button @click="editExam" class="action-btn">✏️ Bearbeiten</button>
            <button @click="regenerateExam" class="action-btn">🔄 Neu generieren</button>
            <button @click="saveExam" class="action-btn primary">💾 Speichern</button>
            <button @click="currentExam = null" class="action-btn">✕ Schließen</button>
          </div>
        </div>

        <!-- Questions List -->
        <div class="questions-list">
          <div
            v-for="(question, qIdx) in currentExam.questions"
            :key="qIdx"
            class="question-card"
            :class="{ expanded: expandedQuestions.has(qIdx) }"
          >
            <div class="question-header" @click="toggleQuestion(qIdx)">
              <span class="question-number">{{ qIdx + 1 }}</span>
              <span class="question-type" :class="question.type">{{ getQuestionTypeLabel(question.type) }}</span>
              <span class="question-text">{{ truncateText(question.question, 80) }}</span>
              <span class="question-points">{{ question.points || 1 }} Pkt.</span>
              <svg class="expand-icon" :class="{ rotated: expandedQuestions.has(qIdx) }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>

            <!-- Expanded Content -->
            <div v-if="expandedQuestions.has(qIdx)" class="question-body">
              <div class="question-full-text">{{ question.question }}</div>

              <!-- MC Options -->
              <div v-if="question.type === 'mc' && question.options" class="mc-options">
                <div
                  v-for="(opt, oIdx) in question.options"
                  :key="oIdx"
                  class="mc-option"
                  :class="{ correct: isCorrectAnswer(question, oIdx) }"
                >
                  <span class="option-letter">{{ String.fromCharCode(65 + oIdx) }}</span>
                  <span class="option-text">{{ opt }}</span>
                  <span v-if="isCorrectAnswer(question, oIdx)" class="correct-badge">✓</span>
                </div>
              </div>

              <!-- Free Text Answer -->
              <div v-if="question.type === 'free_text' && question.sample_answer" class="sample-answer">
                <strong>Musterantwort:</strong>
                <p>{{ question.sample_answer }}</p>
              </div>

              <!-- Source Reference -->
              <div v-if="question.source_file" class="question-source">
                📄 Quelle: {{ question.source_file }}
              </div>

              <!-- Question Actions -->
              <div class="question-actions">
                <button @click="editQuestion(qIdx)" class="q-action-btn">✏️ Bearbeiten</button>
                <button @click="regenerateQuestion(qIdx)" class="q-action-btn">🔄 Neu</button>
                <button @click="deleteQuestion(qIdx)" class="q-action-btn danger">🗑️ Löschen</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import http from '@/api/http'

interface Course {
  course_id: string
  title: string
}

interface Chapter {
  chapter_id: string
  title: string
  order_index: number
}

interface CourseFile {
  course_file_id: string
  file_id?: string  // Reference to media_files table (optional)
  file_name: string
  display_name?: string
  file_type: string
  file_size_bytes: number
  file_category: string
  storage_path?: string
  external_url?: string
  ai_extracted_text?: string
  processed_for_ai?: boolean
  created_at?: string
}

interface Question {
  type: 'mc' | 'free_text' | 'matching' | 'fill_blank'
  question: string
  options?: string[]
  correct_answer?: number | number[] | string
  sample_answer?: string
  points?: number
  difficulty?: string
  source_file?: string
}

interface Exam {
  exam_id?: string
  title: string
  description?: string
  duration: number
  questions: Question[]
  chapter_id?: string
  created_at?: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ActivityItem {
  message: string
  status: 'pending' | 'success' | 'error'
  duration?: number
}

interface Props {
  course?: Course | null
  chapter?: Chapter | null
  chapters?: Chapter[]
}

const props = withDefaults(defineProps<Props>(), {
  course: null,
  chapter: null,
  chapters: () => []
})

// File categories
const fileCategories = [
  { id: 'all', name: 'Alle', icon: '📁' },
  { id: 'script', name: 'Skripte', icon: '📖' },
  { id: 'material', name: 'Material', icon: '📚' },
  { id: 'exercise', name: 'Übungen', icon: '✏️' },
  { id: 'solution', name: 'Lösungen', icon: '✅' },
  { id: 'reference', name: 'Referenz', icon: '📎' }
]

// State
const courseFiles = ref<CourseFile[]>([])
const selectedFiles = ref<string[]>([])
const selectedCategory = ref('all')
const isLoadingFiles = ref(false)
const previewFile = ref<CourseFile | null>(null)
const previewContent = ref('')

const messages = ref<ChatMessage[]>([])
const userInput = ref('')
const isGenerating = ref(false)
const currentActivity = ref<string | null>(null)
const activityLog = ref<ActivityItem[]>([])
const tokensUsed = ref(0)
const estimatedCost = ref(0)

const questionCount = ref(10)
const difficulty = ref('mixed')
const durationMinutes = ref(30)

const currentExam = ref<Exam | null>(null)
const generatedExams = ref<Exam[]>([])
const expandedQuestions = ref<Set<number>>(new Set())
const chatMessagesRef = ref<HTMLElement | null>(null)

// Computed
const filteredFiles = computed(() => {
  if (selectedCategory.value === 'all') {
    return courseFiles.value
  }
  return courseFiles.value.filter(f => f.file_category === selectedCategory.value)
})

const totalQuestions = computed(() => {
  return generatedExams.value.reduce((sum, exam) => sum + (exam.questions?.length || 0), 0)
})

// Methods
function getCategoryCount(categoryId: string): number {
  if (categoryId === 'all') return courseFiles.value.length
  return courseFiles.value.filter(f => f.file_category === categoryId).length
}

function getFileIcon(fileType: string): string {
  if (!fileType) return '📄'
  if (fileType.includes('pdf')) return '📕'
  if (fileType.includes('word') || fileType.includes('document')) return '📘'
  if (fileType.includes('powerpoint') || fileType.includes('presentation')) return '📙'
  if (fileType.includes('excel') || fileType.includes('spreadsheet')) return '📗'
  if (fileType.includes('image')) return '🖼️'
  if (fileType.includes('text')) return '📝'
  return '📄'
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(1)} ${units[i]}`
}

function isTextFile(file: CourseFile): boolean {
  const textTypes = ['text/plain', 'text/markdown', 'text/csv', 'application/json', 'txt', 'md']
  return textTypes.some(t => file.file_type?.includes(t)) || file.file_name?.endsWith('.txt') || file.file_name?.endsWith('.md')
}

function getFileUrl(file: CourseFile): string {
  return `/api/v1/admin/courses/${props.course?.course_id}/files/${file.course_file_id}/download`
}

function getFileName(fileId: string): string {
  const file = courseFiles.value.find(f => f.course_file_id === fileId)
  return file?.display_name || file?.file_name || fileId
}

async function loadCourseFiles() {
  if (!props.course) return

  isLoadingFiles.value = true
  try {
    const response = await http.get(`/admin/courses/${props.course.course_id}/files`)
    if (response.data.success) {
      courseFiles.value = response.data.files || []
    }
  } catch (error) {
    console.error('Failed to load course files:', error)
    courseFiles.value = []
  } finally {
    isLoadingFiles.value = false
  }
}

function toggleFileSelection(file: CourseFile) {
  const idx = selectedFiles.value.indexOf(file.course_file_id)
  if (idx >= 0) {
    selectedFiles.value.splice(idx, 1)
  } else {
    selectedFiles.value.push(file.course_file_id)
  }
}

function selectAllFiles() {
  selectedFiles.value = filteredFiles.value.map(f => f.course_file_id)
}

function clearFileSelection() {
  selectedFiles.value = []
}

async function openFilePreview(file: CourseFile) {
  previewFile.value = file
  previewContent.value = ''

  if (isTextFile(file)) {
    try {
      const response = await http.get(getFileUrl(file), { responseType: 'text' })
      previewContent.value = response.data
    } catch (error) {
      previewContent.value = 'Fehler beim Laden der Datei'
    }
  }
}

function closeFilePreview() {
  previewFile.value = null
  previewContent.value = ''
}

function downloadFile(file: CourseFile) {
  window.open(getFileUrl(file), '_blank')
}

function formatMessage(content: string): string {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

function getActivityIcon(status: string): string {
  switch (status) {
    case 'success': return '✓'
    case 'error': return '✗'
    default: return '○'
  }
}

function getQuestionTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    'mc': 'Multiple Choice',
    'free_text': 'Freitext',
    'matching': 'Zuordnung',
    'fill_blank': 'Lückentext'
  }
  return labels[type] || type
}

function truncateText(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text || ''
  return text.substring(0, maxLength) + '...'
}

function isCorrectAnswer(question: Question, idx: number): boolean {
  if (Array.isArray(question.correct_answer)) {
    return question.correct_answer.includes(idx)
  }
  return question.correct_answer === idx
}

function toggleQuestion(idx: number) {
  if (expandedQuestions.value.has(idx)) {
    expandedQuestions.value.delete(idx)
  } else {
    expandedQuestions.value.add(idx)
  }
}

function useQuickPrompt(type: string) {
  const fileContext = selectedFiles.value.length > 0
    ? ` basierend auf den ${selectedFiles.value.length} ausgewählten Dateien`
    : ''

  const prompts: Record<string, string> = {
    'from_files': `Erstelle ${questionCount.value} Prüfungsfragen aus den ausgewählten Kursmaterialien. Nutze die wichtigsten Inhalte und Konzepte.`,
    'exam_mc': `Erstelle ${questionCount.value} Multiple-Choice Fragen${fileContext}. Jede Frage soll 4 Antwortmöglichkeiten haben.`,
    'exam_ihk': `Erstelle eine IHK-konforme Prüfung mit ${durationMinutes.value} Minuten Bearbeitungszeit${fileContext}. Berücksichtige typische IHK-Aufgabenformate.`,
    'exam_mixed': `Erstelle eine gemischte Prüfung mit ${questionCount.value} Fragen${fileContext}: 60% MC, 30% Freitext, 10% Zuordnung.`
  }
  userInput.value = prompts[type] || ''
}

async function sendMessage() {
  if (!userInput.value.trim() || isGenerating.value) return

  const userMessage = userInput.value.trim()
  userInput.value = ''

  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  await nextTick()
  scrollToBottom()
  await generateExam(userMessage)
}

async function generateExam(prompt: string) {
  isGenerating.value = true
  currentActivity.value = 'Analysiere Anfrage...'
  activityLog.value = []

  const startTime = Date.now()

  try {
    // Build file context
    const selectedFileNames = selectedFiles.value
      .map(id => getFileName(id))
      .join(', ')

    if (selectedFiles.value.length > 0) {
      addActivity(`Analysiere ${selectedFiles.value.length} Datei(en)...`, 'pending')
    }

    addActivity('Generiere Prüfungsfragen...', 'pending')

    const response = await http.post('/admin/ai/generate-exam', {
      course_id: props.course?.course_id,
      chapter_id: props.chapter?.chapter_id,
      prompt: prompt,
      exam_type: 'mixed',
      question_count: questionCount.value,
      duration_minutes: durationMinutes.value,
      difficulty: difficulty.value,
      source_files: selectedFiles.value,
      source_file_names: selectedFileNames
    })

    if (response.data.success) {
      const data = response.data.data
      const genTime = Date.now() - startTime

      updateLastActivity('Fragen generiert', 'success', genTime)

      tokensUsed.value += data.tokens_used || 0
      estimatedCost.value += data.cost_eur || 0

      currentExam.value = {
        title: data.title || 'Generierte Prüfung',
        description: data.description,
        duration: data.duration_minutes || durationMinutes.value,
        questions: data.questions || []
      }

      const questionCount = data.questions?.length || 0
      messages.value.push({
        role: 'assistant',
        content: `Ich habe eine Prüfung mit **${questionCount} Fragen** erstellt:\n\n` +
          `📝 **${data.title || 'Prüfung'}**\n` +
          `⏱️ Dauer: ${data.duration_minutes || durationMinutes.value} Minuten\n` +
          `📊 Fragentypen: ${getQuestionTypeSummary(data.questions)}\n` +
          (selectedFiles.value.length > 0 ? `📁 Basierend auf: ${selectedFileNames}\n` : '') +
          `\nDu kannst die Fragen unten bearbeiten oder speichern.`,
        timestamp: new Date()
      })
    } else {
      throw new Error(response.data.error?.message || 'Generierung fehlgeschlagen')
    }
  } catch (error: any) {
    console.error('Exam generation failed:', error)
    updateLastActivity('Fehler bei Generierung', 'error', Date.now() - startTime)

    messages.value.push({
      role: 'assistant',
      content: `❌ Fehler: ${error.response?.data?.error?.message || error.message}\n\nBitte versuche es erneut.`,
      timestamp: new Date()
    })
  } finally {
    isGenerating.value = false
    currentActivity.value = null
    await nextTick()
    scrollToBottom()
  }
}

function getQuestionTypeSummary(questions: Question[]): string {
  if (!questions?.length) return 'Keine'

  const counts: Record<string, number> = {}
  for (const q of questions) {
    counts[q.type] = (counts[q.type] || 0) + 1
  }

  const labels: Record<string, string> = {
    'mc': 'MC', 'free_text': 'Freitext', 'matching': 'Zuordnung', 'fill_blank': 'Lückentext'
  }

  return Object.entries(counts).map(([t, c]) => `${c}x ${labels[t] || t}`).join(', ')
}

function addActivity(message: string, status: 'pending' | 'success' | 'error', duration?: number) {
  activityLog.value.push({ message, status, duration })
}

function updateLastActivity(message: string, status: 'pending' | 'success' | 'error', duration: number) {
  if (activityLog.value.length > 0) {
    const last = activityLog.value[activityLog.value.length - 1]
    last.message = message
    last.status = status
    last.duration = duration
  }
}

function scrollToBottom() {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

function editExam() {
  console.log('Edit exam:', currentExam.value)
}

function regenerateExam() {
  const lastUserMsg = [...messages.value].reverse().find(m => m.role === 'user')
  if (lastUserMsg) generateExam(lastUserMsg.content)
}

async function saveExam() {
  if (!currentExam.value || !props.course) return

  try {
    const response = await http.post('/admin/exams', {
      course_id: props.course.course_id,
      chapter_id: props.chapter?.chapter_id,
      title: currentExam.value.title,
      description: currentExam.value.description,
      duration_minutes: currentExam.value.duration,
      questions: currentExam.value.questions,
      exam_type: 'ai_generated'
    })

    if (response.data.success) {
      generatedExams.value.unshift({
        ...currentExam.value,
        exam_id: response.data.data.exam_id,
        created_at: new Date().toISOString()
      })

      messages.value.push({
        role: 'assistant',
        content: `✅ Prüfung **"${currentExam.value.title}"** erfolgreich gespeichert!`,
        timestamp: new Date()
      })

      currentExam.value = null
    }
  } catch (error: any) {
    messages.value.push({
      role: 'assistant',
      content: `❌ Fehler beim Speichern: ${error.response?.data?.error?.message || error.message}`,
      timestamp: new Date()
    })
  }
}

function editQuestion(idx: number) {
  console.log('Edit question:', idx)
}

async function regenerateQuestion(idx: number) {
  if (!currentExam.value) return
  const question = currentExam.value.questions[idx]
  currentActivity.value = `Generiere Frage ${idx + 1} neu...`

  try {
    const response = await http.post('/admin/ai/regenerate-question', {
      course_id: props.course?.course_id,
      chapter_id: props.chapter?.chapter_id,
      question_type: question.type,
      context: question.question,
      source_files: selectedFiles.value
    })

    if (response.data.success && response.data.data.question) {
      currentExam.value.questions[idx] = response.data.data.question
      tokensUsed.value += response.data.data.tokens_used || 0
    }
  } catch (error) {
    console.error('Failed to regenerate:', error)
  } finally {
    currentActivity.value = null
  }
}

function deleteQuestion(idx: number) {
  if (!currentExam.value) return
  if (confirm('Frage wirklich löschen?')) {
    currentExam.value.questions.splice(idx, 1)
    expandedQuestions.value.delete(idx)
  }
}

// Watch for course changes
watch(() => props.course, () => {
  messages.value = []
  currentExam.value = null
  courseFiles.value = []
  selectedFiles.value = []
  activityLog.value = []
  tokensUsed.value = 0
  estimatedCost.value = 0
  loadCourseFiles()
}, { immediate: true })

onMounted(() => {
  loadCourseFiles()
})
</script>

<style scoped>
.exams-tab {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-state h3 { color: var(--color-text-primary); margin: 0 0 0.5rem; }
.empty-state p { color: var(--color-text-secondary); margin: 0; }

/* Header */
.exams-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 1rem;
  margin-bottom: 1rem;
}

.header-icon {
  width: 56px; height: 56px;
  background: rgba(255,255,255,0.2);
  border-radius: 1rem;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.75rem;
}

.header-info { flex: 1; }
.header-info h2 { color: white; font-size: 1.25rem; font-weight: 700; margin: 0; }
.header-info p { color: rgba(255,255,255,0.8); font-size: 0.875rem; margin: 0.25rem 0 0; }

.header-stats { display: flex; gap: 1.5rem; }
.stat { text-align: center; }
.stat-value { display: block; font-size: 1.5rem; font-weight: 700; color: white; }
.stat-label { font-size: 0.75rem; color: rgba(255,255,255,0.7); }

/* Three-Column Layout */
.main-layout {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Panel Styles */
.files-panel, .chat-panel, .activity-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon { font-size: 1.125rem; }
.panel-title { font-weight: 600; color: var(--color-text-primary); flex: 1; }

.refresh-btn {
  width: 28px; height: 28px;
  border: none; background: transparent;
  border-radius: 0.25rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.refresh-btn:hover { background: var(--color-surface); }

.files-indicator {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
  border-radius: 1rem;
}

/* File Categories */
.file-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.category-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: transparent;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.category-btn:hover { background: var(--color-surface-secondary); }
.category-btn.active {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.cat-icon { font-size: 0.875rem; }
.cat-count { opacity: 0.6; }

/* File List */
.file-list {
  flex: 1;
  overflow-y: auto;
  max-height: 350px;
}

.loading-files, .no-files {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  color: var(--color-text-tertiary);
}

.spinner {
  width: 24px; height: 24px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.no-files-icon { font-size: 2rem; margin-bottom: 0.5rem; opacity: 0.5; }
.no-files p { margin: 0; font-size: 0.8125rem; }

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.15s;
}

.file-item:hover { background: var(--color-surface-secondary); }
.file-item.selected { background: rgba(99, 102, 241, 0.1); }
.file-item.previewing { border-left: 3px solid var(--color-primary); }

.file-checkbox input {
  width: 16px; height: 16px;
  cursor: pointer;
}

.file-icon { font-size: 1.25rem; flex-shrink: 0; }

.file-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.file-name {
  display: block;
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.preview-btn {
  width: 28px; height: 28px;
  border: none; background: transparent;
  border-radius: 0.25rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
}

.file-item:hover .preview-btn { opacity: 1; }
.preview-btn:hover { background: var(--color-surface); }

.file-actions {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-top: 1px solid var(--color-border);
}

.action-link {
  border: none;
  background: none;
  font-size: 0.75rem;
  color: var(--color-primary);
  cursor: pointer;
}
.action-link:hover { text-decoration: underline; }

/* Chat Panel */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  min-height: 300px;
  max-height: 400px;
}

.welcome-message {
  text-align: center;
  padding: 1.5rem 1rem;
}

.welcome-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.welcome-message h4 { color: var(--color-text-primary); margin: 0 0 0.5rem; }
.welcome-message p { color: var(--color-text-secondary); font-size: 0.875rem; margin: 0 0 1rem; }

.selected-files-info {
  text-align: left;
  padding: 0.75rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.8125rem;
}

.selected-files-info ul {
  margin: 0.5rem 0 0;
  padding-left: 1.25rem;
  color: var(--color-text-secondary);
}

.welcome-hints {
  text-align: left;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
}

.welcome-hints ul {
  margin: 0.25rem 0 0;
  padding-left: 1.25rem;
}

/* Chat Messages */
.chat-message {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.chat-message.user { flex-direction: row-reverse; }

.message-avatar {
  width: 32px; height: 32px;
  background: var(--color-surface-secondary);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.chat-message.user .message-avatar { background: var(--color-primary); }
.chat-message.assistant .message-avatar { background: linear-gradient(135deg, #6366f1, #8b5cf6); }

.message-content { max-width: 80%; }

.message-text {
  padding: 0.625rem 0.875rem;
  border-radius: 1rem;
  font-size: 0.8125rem;
  line-height: 1.5;
}

.chat-message.user .message-text {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.chat-message.assistant .message-text {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  border-bottom-left-radius: 0.25rem;
}

.message-time {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  margin-top: 0.25rem;
  padding: 0 0.5rem;
}

.chat-message.user .message-time { text-align: right; }

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.typing-dots {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.625rem 0.875rem;
  background: var(--color-surface-secondary);
  border-radius: 1rem;
}

.typing-dots span {
  width: 6px; height: 6px;
  background: var(--color-text-tertiary);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-3px); opacity: 1; }
}

/* Chat Input */
.chat-input-area {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.input-wrapper textarea {
  flex: 1;
  padding: 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.8125rem;
  resize: none;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.send-btn {
  width: 40px; height: 40px;
  background: var(--color-primary);
  border: none;
  border-radius: 0.5rem;
  color: white;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}

.send-btn:hover:not(:disabled) { filter: brightness(1.1); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.send-btn svg { width: 18px; height: 18px; }

.loading-spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Quick Prompts */
.quick-prompts {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 0.25rem 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.quick-btn:hover:not(:disabled) {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.quick-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Activity Panel */
.activity-log {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  min-height: 120px;
  max-height: 180px;
}

.current-activity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-primary);
}

.activity-spinner {
  width: 12px; height: 12px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0;
  font-size: 0.6875rem;
  border-bottom: 1px solid var(--color-border);
}

.activity-item:last-child { border-bottom: none; }

.activity-icon { width: 14px; text-align: center; }
.activity-item.success .activity-icon { color: #10b981; }
.activity-item.error .activity-icon { color: #ef4444; }

.activity-text { flex: 1; color: var(--color-text-secondary); }
.activity-time { color: var(--color-text-tertiary); font-family: monospace; }

.activity-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  text-align: center;
}

.activity-empty .empty-icon { font-size: 1.25rem; margin-bottom: 0.25rem; opacity: 0.5; }
.activity-empty p { margin: 0; font-size: 0.75rem; color: var(--color-text-tertiary); }

/* Token Usage */
.token-usage {
  padding: 0.5rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.usage-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.375rem;
}

.usage-value { font-weight: 600; color: var(--color-text-primary); }

.usage-bar {
  height: 3px;
  background: var(--color-border);
  border-radius: 1.5px;
  overflow: hidden;
  margin-bottom: 0.375rem;
}

.usage-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 1.5px;
}

.usage-cost {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
}

/* Generation Settings */
.gen-settings {
  padding: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.gen-settings h4 {
  font-size: 0.75rem;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem;
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.375rem;
}

.setting-row label {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
}

.setting-row select, .setting-row input {
  width: 100px;
  padding: 0.25rem 0.375rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.6875rem;
}

/* File Preview Modal */
.file-preview-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.preview-container {
  background: var(--color-surface);
  border-radius: 1rem;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-container .preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.preview-file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-file-info .preview-icon { font-size: 2rem; }
.preview-file-info h3 { margin: 0; font-size: 1rem; }
.preview-file-info p { margin: 0; font-size: 0.75rem; color: var(--color-text-tertiary); }

.preview-container .preview-actions {
  display: flex;
  gap: 0.5rem;
}

.preview-action-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
}

.preview-action-btn:hover { background: var(--color-surface-secondary); }
.preview-action-btn.selected {
  background: rgba(16, 185, 129, 0.1);
  border-color: #10b981;
  color: #10b981;
}

.preview-close-btn {
  width: 32px; height: 32px;
  border: none;
  background: var(--color-surface-secondary);
  border-radius: 50%;
  font-size: 1.25rem;
  cursor: pointer;
}

.preview-content {
  flex: 1;
  overflow: auto;
  background: var(--color-bg);
}

.pdf-preview {
  width: 100%;
  height: 70vh;
  border: none;
}

.image-preview {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

.text-preview {
  padding: 1rem;
  margin: 0;
  font-size: 0.875rem;
  white-space: pre-wrap;
  overflow-x: auto;
}

.no-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.no-preview-icon { font-size: 4rem; margin-bottom: 1rem; opacity: 0.5; }
.no-preview p { margin: 0; color: var(--color-text-secondary); }
.no-preview .file-type { font-family: monospace; color: var(--color-text-tertiary); margin-top: 0.5rem; }

.download-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

/* Exam Preview */
.exam-preview {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.exam-preview .preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-title .preview-icon { font-size: 1.5rem; }
.preview-title h3 { margin: 0; font-size: 1rem; color: var(--color-text-primary); }
.preview-title p { margin: 0.25rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary); }

.exam-preview .preview-actions { display: flex; gap: 0.5rem; }

.action-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
}

.action-btn:hover { background: var(--color-surface-secondary); color: var(--color-text-primary); }
.action-btn.primary { background: var(--color-primary); border-color: var(--color-primary); color: white; }
.action-btn.primary:hover { filter: brightness(1.1); }

/* Questions List */
.questions-list {
  max-height: 400px;
  overflow-y: auto;
}

.question-card {
  border-bottom: 1px solid var(--color-border);
}

.question-card:last-child { border-bottom: none; }

.question-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
}

.question-header:hover { background: var(--color-surface-secondary); }

.question-number {
  width: 24px; height: 24px;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 600;
}

.question-type {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.625rem; font-weight: 600;
  text-transform: uppercase;
}

.question-type.mc { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.question-type.free_text { background: rgba(99, 102, 241, 0.15); color: #6366f1; }
.question-type.matching { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.question-type.fill_blank { background: rgba(236, 72, 153, 0.15); color: #ec4899; }

.question-text {
  flex: 1;
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.question-points {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.expand-icon {
  width: 16px; height: 16px;
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

.expand-icon.rotated { transform: rotate(180deg); }

/* Question Body */
.question-body {
  padding: 0 1rem 1rem;
  background: var(--color-surface-secondary);
}

.question-full-text {
  font-size: 0.875rem;
  color: var(--color-text-primary);
  line-height: 1.6;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--color-surface);
  border-radius: 0.375rem;
}

/* MC Options */
.mc-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.mc-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
}

.mc-option.correct {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.option-letter {
  width: 22px; height: 22px;
  background: var(--color-surface-secondary);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.6875rem; font-weight: 600;
}

.mc-option.correct .option-letter { background: #10b981; color: white; }
.option-text { flex: 1; font-size: 0.8125rem; }
.correct-badge { color: #10b981; font-weight: bold; }

/* Sample Answer */
.sample-answer {
  padding: 0.75rem;
  background: var(--color-surface);
  border-left: 3px solid var(--color-primary);
  border-radius: 0 0.375rem 0.375rem 0;
  margin-bottom: 1rem;
}

.sample-answer strong { display: block; font-size: 0.6875rem; color: var(--color-text-tertiary); margin-bottom: 0.25rem; }
.sample-answer p { margin: 0; font-size: 0.8125rem; line-height: 1.5; }

.question-source {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-bottom: 0.75rem;
}

/* Question Actions */
.question-actions {
  display: flex;
  gap: 0.5rem;
}

.q-action-btn {
  padding: 0.375rem 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.6875rem;
  cursor: pointer;
}

.q-action-btn:hover { background: var(--color-surface); color: var(--color-text-primary); }
.q-action-btn.danger:hover { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: #ef4444; }

/* Responsive */
@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .files-panel { order: 1; max-height: 250px; }
  .chat-panel { order: 2; }
  .activity-panel { order: 3; }
}
</style>
