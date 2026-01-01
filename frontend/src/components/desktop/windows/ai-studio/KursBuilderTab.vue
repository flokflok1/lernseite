<!--
  KursBuilderTab.vue - REFACTORED

  KI-Kurs-Builder Tab für chat-basiertes Authoring.

  Layout (2 Spalten):
  - Links (60%): Chat mit Quick-Actions (2x2 Grid)
  - Rechts (40%): Kursstruktur + Materialien

  Features:
  - Session-Status im Header integriert
  - Quick-Actions als 2x2 Grid über dem Input
  - Materialien mit Checkboxen für KI-Kontext
  - Vorschau-Button öffnet Desktop-Fenster

  Phase D4 - KI-Kurs-Builder Rebuild
-->

<template>
  <div class="kurs-builder-tab">
    <!-- Header mit Session-Status -->
    <div class="builder-header">
      <div class="header-left">
        <span class="header-icon">🏗️</span>
        <div class="header-info">
          <h3 class="header-title">KI-Kurs-Builder</h3>
          <div class="header-meta">
            <span v-if="course" class="course-badge">{{ course.title }}</span>
            <span v-if="draftStats.chapters > 0" class="stats-badge">
              {{ draftStats.chapters }} Kapitel · {{ draftStats.lessons }} Lektionen
            </span>
          </div>
        </div>
      </div>

      <div class="header-right">
        <!-- Session Status -->
        <div v-if="session" class="session-info">
          <span class="session-dot active"></span>
          <span class="session-text">Session aktiv</span>
          <span class="session-id">{{ session.session_id.slice(0, 8) }}</span>
        </div>
        <div v-else class="session-info">
          <span class="session-dot inactive"></span>
          <span class="session-text">Keine Session</span>
        </div>

        <!-- Actions -->
        <button
          v-if="!session && course"
          @click="createSession"
          :disabled="creatingSession"
          class="btn-primary"
        >
          {{ creatingSession ? 'Erstelle...' : '+ Neue Session' }}
        </button>

        <button
          v-if="session && session.status === 'active'"
          @click="finalizeSession"
          :disabled="finalizing || !hasChanges"
          class="btn-success"
        >
          {{ finalizing ? 'Finalisiere...' : '✓ Finalisieren' }}
        </button>
      </div>
    </div>

    <!-- No Course Selected -->
    <div v-if="!course" class="empty-state">
      <span class="empty-icon">📚</span>
      <p class="empty-title">Kein Kurs ausgewählt</p>
      <p class="empty-hint">Wähle oben einen Kurs um den KI-Kurs-Builder zu starten.</p>
    </div>

    <!-- Main Content (2 Spalten) -->
    <div v-else class="builder-content">
      <!-- Left: Chat Column (60%) -->
      <div class="chat-column">
        <!-- Chat Messages -->
        <div ref="chatContainer" class="chat-messages">
          <div v-if="chatMessages.length === 0" class="chat-welcome">
            <div class="welcome-icon">🤖</div>
            <h4>KI-Kurs-Builder bereit</h4>
            <p>Nutze die Quick-Actions oder schreibe eine Nachricht.</p>
            <p class="welcome-hint" v-if="selectedFileIds.length > 0">
              📎 {{ selectedFileIds.length }} Datei(en) als Kontext ausgewählt
            </p>
          </div>

          <div
            v-for="(msg, index) in chatMessages"
            :key="index"
            class="chat-message"
            :class="msg.role"
          >
            <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div v-if="msg.operations?.length" class="message-ops">
                <span v-for="op in msg.operations" :key="op" class="op-badge">{{ op }}</span>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="chatLoading" class="typing-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="typing-text">KI denkt...</span>
          </div>
        </div>

        <!-- Context Banner (when item selected) -->
        <div v-if="selectedContext" class="context-banner">
          <div class="context-info-row">
            <span class="context-icon">{{ selectedContext.type === 'chapter' ? '📖' : '📄' }}</span>
            <div class="context-details">
              <span class="context-type">{{ selectedContext.type === 'chapter' ? 'Kapitel' : 'Lektion' }}</span>
              <span class="context-title">{{ selectedContext.title }}</span>
            </div>
            <button @click="clearContext" class="context-close" title="Kontext schließen">×</button>
          </div>

          <!-- Step 1: Analyze with Materials -->
          <div v-if="selectedContext" class="workflow-section analyze-section">
            <div class="workflow-header">
              <span class="workflow-icon">🔍</span>
              <span class="workflow-title">1. Analyse</span>
              <span v-if="selectedFileIds.length" class="workflow-badge">{{ selectedFileIds.length }} Dateien</span>
            </div>
            <button
              @click="analyzeSelectedContext"
              class="workflow-action-btn"
              :class="{ 'is-loading': isAnalyzing }"
              :disabled="isAnalyzing || chatLoading"
            >
              <span v-if="isAnalyzing">⏳ Analysiere...</span>
              <span v-else-if="selectedFileIds.length">🔍 Mit {{ selectedFileIds.length }} Datei(en) analysieren</span>
              <span v-else>🔍 Kontext analysieren</span>
            </button>
            <p v-if="!selectedFileIds.length" class="workflow-hint">
              💡 Tipp: Wähle Materialien aus für bessere Empfehlungen
            </p>
          </div>

          <!-- Step 2: Theory Content -->
          <div v-if="selectedContext" class="workflow-section theory-section">
            <div class="workflow-header">
              <span class="workflow-icon">📖</span>
              <span class="workflow-title">2. Theorie</span>
              <span v-if="isLoadingTheories" class="workflow-badge">Lädt...</span>
              <span v-else-if="selectedContext.type === 'chapter' && chapterTheories.length" class="workflow-badge">{{ chapterTheories.length }} vorhanden</span>
              <span v-else-if="selectedContext.type === 'lesson' && lessonExplanations.length" class="workflow-badge">{{ lessonExplanations.length }} vorhanden</span>
              <span v-else class="workflow-badge workflow-badge--empty">Keine</span>
            </div>

            <!-- Loading State -->
            <div v-if="isLoadingTheories" class="theory-loading">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              <span class="loading-text">Lade vorhandene Inhalte...</span>
            </div>

            <!-- Chapter: Existing Theories List -->
            <div v-else-if="selectedContext.type === 'chapter'" class="theory-content-list">
              <div v-if="chapterTheories.length > 0" class="existing-items">
                <div
                  v-for="theory in chapterTheories"
                  :key="theory.theoryId"
                  class="theory-item"
                  :class="{ selected: selectedTheoryId === theory.theoryId }"
                  @click="openTheoryInTutor(theory)"
                >
                  <span class="theory-item-icon">📄</span>
                  <div class="theory-item-info">
                    <span class="theory-item-title">{{ theory.title }}</span>
                    <span class="theory-item-meta">{{ theory.style }} · {{ formatDate(theory.createdAt) }}</span>
                  </div>
                  <span v-if="theory.audioUrl" class="theory-item-audio" title="Mit Audio">🔊</span>
                </div>
              </div>
              <div v-else class="no-content-hint">
                <span>📋</span>
                <p>Noch keine Zusammenfassung vorhanden</p>
              </div>
              <button
                @click="generateTheory"
                class="workflow-action-btn workflow-action-btn--theory"
                :disabled="isGeneratingTheory || chatLoading"
              >
                <span v-if="isGeneratingTheory">⏳ Generiere...</span>
                <span v-else>{{ chapterTheories.length ? '➕ Weitere Zusammenfassung' : '📚 Zusammenfassung erstellen' }}</span>
              </button>
            </div>

            <!-- Lesson: Existing Explanations List -->
            <div v-else class="theory-content-list">
              <div v-if="lessonExplanations.length > 0" class="existing-items">
                <div
                  v-for="expl in lessonExplanations"
                  :key="expl.explanationId"
                  class="theory-item"
                  @click="openExplanationInTutor(expl)"
                >
                  <span class="theory-item-icon">📝</span>
                  <div class="theory-item-info">
                    <span class="theory-item-title">{{ expl.title }}</span>
                    <span class="theory-item-meta">{{ expl.stepCount }} Schritte · {{ formatDate(expl.createdAt) }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="no-content-hint">
                <span>📝</span>
                <p>Noch kein Theorieblatt vorhanden</p>
              </div>
              <button
                @click="generateTheory"
                class="workflow-action-btn workflow-action-btn--theory"
                :disabled="isGeneratingTheory || chatLoading"
              >
                <span v-if="isGeneratingTheory">⏳ Generiere...</span>
                <span v-else>{{ lessonExplanations.length ? '➕ Weiteres Theorieblatt' : '📖 Theorieblatt erstellen' }}</span>
              </button>
            </div>
          </div>

          <!-- Step 3: LM Suggestions (for lessons) -->
          <div v-if="selectedContext.type === 'lesson'" class="workflow-section lm-section">
            <div class="workflow-header">
              <span class="workflow-icon">🧠</span>
              <span class="workflow-title">3. Lernmethoden</span>
              <span v-if="lmSuggestionsLoading" class="workflow-badge">Analysiere...</span>
            </div>
            <div v-if="lmSuggestionsLoading" class="lm-suggestions-loading">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="loading-text">KI analysiert Lektionskontext...</span>
            </div>
            <div v-else-if="lmSuggestions.length > 0" class="lm-suggestions-grid">
              <button
                v-for="lm in lmSuggestions"
                :key="lm.lm_id"
                @click="createLMFromSuggestion(lm)"
                class="lm-suggestion-btn"
                :class="`lm-group-${lm.group.toLowerCase()}`"
                :disabled="chatLoading"
                :title="lm.reason"
              >
                <div class="lm-btn-top">
                  <span class="lm-icon">{{ lm.icon }}</span>
                  <span class="lm-name">{{ lm.name }}</span>
                </div>
                <div class="lm-btn-bottom">
                  <span class="lm-reason">{{ lm.reason }}</span>
                </div>
              </button>
            </div>
            <div v-else class="lm-no-suggestions">
              <span>Erst analysieren für LM-Empfehlungen</span>
            </div>
          </div>

          <!-- Context-specific Actions -->
          <div class="context-actions">
            <template v-if="contextActionsLoading">
              <span class="loading-text">Lade Aktionen...</span>
            </template>
            <template v-else>
              <button
                v-for="action in contextActions"
                :key="action.action_id"
                @click="sendContextAction(action)"
                class="context-action-btn"
                :disabled="chatLoading"
              >
                <span class="qa-icon">{{ action.icon }}</span>
                <span class="qa-label">{{ action.label }}</span>
              </button>
            </template>
          </div>
        </div>

        <!-- Confirmation Panel (when content generated) -->
        <div v-if="pendingAction" class="confirmation-panel">
          <div class="confirm-header">
            <span class="confirm-icon">✨</span>
            <span class="confirm-title">Inhalt generiert - Bestätigung erforderlich</span>
          </div>
          <div class="confirm-preview">
            <pre class="preview-text">{{ pendingAction.previewText }}</pre>
          </div>
          <div class="confirm-actions">
            <button
              @click="confirmPendingAction"
              class="confirm-btn confirm-btn--accept"
              :disabled="confirmLoading"
            >
              {{ confirmLoading ? 'Speichere...' : '✓ Bestätigen' }}
            </button>
            <button
              @click="modifyPendingAction"
              class="confirm-btn confirm-btn--modify"
              :disabled="confirmLoading"
            >
              ✏️ Ändern
            </button>
            <button
              @click="rejectPendingAction"
              class="confirm-btn confirm-btn--reject"
              :disabled="confirmLoading"
            >
              ✗ Verwerfen
            </button>
          </div>
        </div>

        <!-- Quick Actions (2x2 Grid) - Loaded from DB -->
        <div v-if="!selectedContext && !pendingAction" class="quick-actions-grid">
          <template v-if="actionsLoading">
            <div class="actions-loading">Lade Actions...</div>
          </template>
          <button
            v-else
            v-for="action in quickActions"
            :key="action.action_id"
            @click="sendQuickAction(action)"
            class="quick-action-btn"
            :class="action.color ? `action-${action.color}` : ''"
            :disabled="chatLoading"
          >
            <span class="qa-icon">{{ action.icon }}</span>
            <span class="qa-label">{{ action.label }}</span>
          </button>
        </div>

        <!-- Chat Input -->
        <div class="chat-input-wrapper">
          <div class="input-row">
            <textarea
              ref="inputField"
              v-model="inputMessage"
              @keydown.enter.ctrl="sendMessage"
              @keydown.enter.meta="sendMessage"
              placeholder="Nachricht eingeben... (Strg+Enter)"
              :disabled="chatLoading"
              rows="2"
            ></textarea>
            <button
              @click="sendMessage"
              class="send-btn"
              :disabled="!inputMessage.trim() || chatLoading"
            >
              {{ chatLoading ? '⏳' : '➤' }}
            </button>
          </div>
          <div class="input-footer">
            <select v-model="selectedMode" class="mode-select">
              <option value="">Auto</option>
              <option value="structure">📋 Struktur</option>
              <option value="lesson">📄 Lektionen</option>
              <option value="exam">🎓 Prüfung</option>
            </select>
            <span v-if="selectedFileIds.length > 0" class="context-info">
              📎 {{ selectedFileIds.length }} Datei(en) im Kontext
            </span>
          </div>
        </div>
      </div>

      <!-- Right: Structure + Materials (40%) -->
      <div class="right-column">
        <!-- Kursstruktur -->
        <div class="panel structure-panel">
          <div class="panel-header">
            <span class="panel-icon">📚</span>
            <span class="panel-title">Kursstruktur</span>
            <span v-if="draftStats.chapters > 0" class="panel-badge">{{ draftStats.chapters }}</span>
          </div>
          <div class="panel-content">
            <div v-if="!draftStructure?.chapters?.length" class="panel-empty">
              <span>📋</span>
              <p>Noch keine Struktur</p>
            </div>
            <div v-else class="structure-tree">
              <div
                v-for="(chapter, chapterIndex) in draftStructure.chapters"
                :key="chapter.id"
                class="tree-chapter"
                :class="{ 'drag-over': dragOverChapterId === chapter.id }"
                draggable="true"
                @dragstart="handleChapterDragStart($event, chapterIndex)"
                @dragover.prevent="handleChapterDragOver($event, chapter.id)"
                @dragleave="handleChapterDragLeave"
                @drop="handleChapterDrop($event, chapterIndex)"
                @dragend="handleDragEnd"
              >
                <div class="chapter-header">
                  <span class="drag-handle" title="Ziehen zum Umsortieren">⋮⋮</span>
                  <span
                    class="expand-icon"
                    @click.stop="toggleChapter(chapter.id)"
                  >{{ expandedChapters.has(chapter.id) ? '▼' : '▶' }}</span>
                  <span class="chapter-icon">📖</span>
                  <span class="chapter-title" @click="toggleChapter(chapter.id)">{{ chapter.title }}</span>
                  <span class="chapter-count">{{ chapter.lessons?.length || 0 }}</span>
                  <div class="item-actions">
                    <button
                      @click.stop="selectChapterForChat(chapter)"
                      class="action-btn action-btn--primary"
                      title="Mit KI bearbeiten"
                    >🤖</button>
                    <button
                      @click.stop="openChapterPreview(chapter)"
                      class="action-btn"
                      title="Vorschau"
                    >👁️</button>
                    <button
                      @click.stop="editChapter(chapter)"
                      class="action-btn"
                      title="Bearbeiten"
                    >✏️</button>
                    <button
                      @click.stop="deleteChapter(chapter.id, chapterIndex)"
                      class="action-btn action-btn--danger"
                      title="Löschen"
                    >🗑️</button>
                  </div>
                </div>
                <div v-if="expandedChapters.has(chapter.id)" class="chapter-lessons">
                  <div
                    v-for="(lesson, lessonIndex) in chapter.lessons"
                    :key="lesson.id"
                    class="tree-lesson"
                    :class="{ 'drag-over': dragOverLessonId === lesson.id }"
                    draggable="true"
                    @dragstart.stop="handleLessonDragStart($event, chapterIndex, lessonIndex)"
                    @dragover.prevent.stop="handleLessonDragOver($event, lesson.id)"
                    @dragleave="handleLessonDragLeave"
                    @drop.stop="handleLessonDrop($event, chapterIndex, lessonIndex)"
                    @dragend="handleDragEnd"
                  >
                    <span class="drag-handle" title="Ziehen zum Umsortieren">⋮⋮</span>
                    <span class="lesson-icon">📄</span>
                    <span class="lesson-title">{{ lesson.title }}</span>
                    <span v-if="lesson.methods?.length" class="lesson-methods">
                      {{ lesson.methods.length }} LM
                    </span>
                    <div class="item-actions">
                      <button
                        @click.stop="analyzeLessonWithFiles(chapter, lesson)"
                        class="action-btn action-btn--analyze"
                        :class="{ 'is-loading': analyzingLessonId === lesson.id }"
                        :disabled="analyzingLessonId === lesson.id"
                        :title="selectedFileIds.length ? `Analysieren (${selectedFileIds.length} Dateien)` : 'Analysieren'"
                      >{{ analyzingLessonId === lesson.id ? '⏳' : '🔍' }}</button>
                      <button
                        @click.stop="selectLessonForChat(chapter, lesson)"
                        class="action-btn action-btn--primary"
                        title="Mit KI bearbeiten"
                      >🤖</button>
                      <button
                        @click.stop="openLessonPreview(chapter, lesson)"
                        class="action-btn"
                        title="Vorschau"
                      >👁️</button>
                      <button
                        @click.stop="editLesson(chapter, lesson)"
                        class="action-btn"
                        title="Bearbeiten"
                      >✏️</button>
                      <button
                        @click.stop="deleteLesson(chapter.id, chapterIndex, lesson.id, lessonIndex)"
                        class="action-btn action-btn--danger"
                        title="Löschen"
                      >🗑️</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="draftStats.chapters > 0" class="panel-footer">
            {{ draftStats.chapters }} Kapitel · {{ draftStats.lessons }} Lektionen · {{ draftStats.methods }} Methoden
          </div>
        </div>

        <!-- Materialien -->
        <div class="panel materials-panel">
          <div class="panel-header">
            <span class="panel-icon">📁</span>
            <span class="panel-title">Materialien</span>
            <span v-if="sessionFiles.length" class="panel-badge">{{ sessionFiles.length }}</span>
            <button @click="triggerFileUpload" class="panel-action" title="Datei hochladen" :disabled="isUploadingFile">
              {{ isUploadingFile ? '⏳' : '📤' }}
            </button>
            <button @click="selectAllFiles" class="panel-action" title="Alle auswählen">
              {{ selectedFileIds.length === sessionFiles.length ? '☑️' : '☐' }}
            </button>
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
          <div class="panel-content files-list">
            <div v-if="!sessionFiles.length" class="panel-empty">
              <span>📄</span>
              <p>Keine Dateien</p>
            </div>
            <div
              v-for="file in sessionFiles"
              :key="file.id"
              class="file-item"
              :class="{ selected: selectedFileIds.includes(file.id) }"
              @click="toggleFileSelection(file.id)"
            >
              <input
                type="checkbox"
                :checked="selectedFileIds.includes(file.id)"
                @click.stop
                @change="toggleFileSelection(file.id)"
              />
              <span class="file-icon">{{ getFileIcon(file.type) }}</span>
              <div class="file-info">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-meta">{{ formatFileSize(file.size) }} · {{ file.type }}</span>
              </div>
              <button
                @click.stop="openFilePreview(file)"
                class="preview-btn"
                title="Vorschau"
              >
                👁️
              </button>
            </div>
          </div>
          <div v-if="selectedFileIds.length > 0" class="panel-footer">
            {{ selectedFileIds.length }} ausgewählt ·
            <button @click="clearFileSelection" class="link-btn">Auswahl aufheben</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button @click="error = null">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useWindowStore } from '@/store/window.store'
import { useTheoryManagement } from '@/composables/useTheoryManagement'
import http from '@/api/http'
import {
  getActionsByCategory,
  getActionsForEntity,
  getLMSuggestions,
  type AuthoringAction,
  type LMSuggestion
} from '@/api/authoring.api'

// Types
interface Course {
  course_id: string
  title: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  operations?: string[]
  error?: boolean
}

interface CourseFile {
  id: string
  name: string
  type: string
  size: number
  parsed: boolean
  url?: string
}

interface Session {
  session_id: string
  course_id: string
  status: 'active' | 'finalized' | 'archived'
  model_profile?: string
  draft_structure: DraftStructure
  chat_history: ChatMessage[]
  total_tokens_used: number
  total_operations: number
}

interface DraftStructure {
  chapters?: Chapter[]
  activity_log?: any[]
}

interface Chapter {
  id: string
  title: string
  description?: string
  lessons?: Lesson[]
}

interface Lesson {
  id: string
  title: string
  description?: string
  content?: any
  duration_minutes?: number
  methods?: { id: string; type: string; title?: string }[]
}

// QuickAction type - use AuthoringAction from DB
interface QuickAction {
  action_id: string
  action_key: string
  label: string
  icon: string
  prompt_template: string
  mode?: string
  color?: string
}

// Props
const props = defineProps<{
  course: Course | null
}>()

// Stores
const windowStore = useWindowStore()
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
const expandedChapters = ref<Set<string>>(new Set())

// Drag & Drop State
const dragOverChapterId = ref<string | null>(null)
const dragOverLessonId = ref<string | null>(null)
const draggingType = ref<'chapter' | 'lesson' | null>(null)
const draggingFromIndex = ref<number>(-1)
const draggingFromChapterIndex = ref<number>(-1)

const inputMessage = ref('')
const selectedMode = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const inputField = ref<HTMLTextAreaElement | null>(null)

const creatingSession = ref(false)
const chatLoading = ref(false)
const finalizing = ref(false)
const error = ref<string | null>(null)
const actionsLoading = ref(false)

// Context Selection for Item-Click → Chat
interface SelectedContext {
  type: 'chapter' | 'lesson' | 'method'
  id: string
  title: string
  data: Chapter | Lesson | null
  parentChapter?: Chapter
}
const selectedContext = ref<SelectedContext | null>(null)
const contextActionsLoading = ref(false)
const contextActions = ref<QuickAction[]>([])

// LM Suggestions - KI-gestützte Lernmethoden-Vorschläge
const lmSuggestions = ref<LMSuggestion[]>([])
const lmSuggestionsLoading = ref(false)
const showLmSuggestions = ref(false)

// Use composable for theory/explanation state (shared with TutorTab)
const chapterTheories = computed(() => theoryMgmt.chapterTheories.value)
const lessonExplanations = computed(() => theoryMgmt.lessonExplanations.value)
const isLoadingTheories = computed(() => theoryMgmt.isLoading.value)

// Pending Action for Confirmation Flow
interface PendingAction {
  type: 'create' | 'update' | 'delete'
  entity: 'chapter' | 'lesson' | 'method' | 'quiz'
  actionKey: string
  generatedData: any
  previewText: string
  parentChapter?: Chapter
  session_id?: string
}
const pendingAction = ref<PendingAction | null>(null)
const confirmLoading = ref(false)

// Quick Actions - loaded from database
const quickActions = ref<QuickAction[]>([])

// Fallback actions if DB is not available
const fallbackActions: QuickAction[] = [
  { action_id: 'fb-1', action_key: 'structure_suggest', label: 'Struktur vorschlagen', icon: '📋', prompt_template: 'Analysiere das Kursmaterial und schlage eine passende Kapitelstruktur vor.', mode: 'structure' },
  { action_id: 'fb-2', action_key: 'chapters_create_3', label: '3 Kapitel erstellen', icon: '📚', prompt_template: 'Erstelle 3 Kapitel mit je 3-5 Lektionen basierend auf dem Kursmaterial.', mode: 'structure' },
  { action_id: 'fb-3', action_key: 'exam_generate', label: 'Prüfung generieren', icon: '🎓', prompt_template: 'Generiere IHK-Stil Prüfungsfragen basierend auf den vorhandenen Kapiteln.', mode: 'exam' },
  { action_id: 'fb-4', action_key: 'material_analyze', label: 'Material analysieren', icon: '🔍', prompt_template: 'Analysiere das hochgeladene Material und extrahiere die wichtigsten Konzepte.', mode: 'analyze' }
]

// Load actions from database
async function loadQuickActions() {
  actionsLoading.value = true
  try {
    const actions = await getActionsByCategory('course_builder')
    if (actions && actions.length > 0) {
      quickActions.value = actions.map(a => ({
        action_id: a.action_id,
        action_key: a.action_key,
        label: a.label,
        icon: a.icon || '📋',
        prompt_template: a.prompt_template,
        mode: a.mode,
        color: a.color
      }))
    } else {
      // Use fallback if no actions in DB
      quickActions.value = fallbackActions
    }
  } catch (err) {
    console.warn('Failed to load actions from DB, using fallback:', err)
    quickActions.value = fallbackActions
  } finally {
    actionsLoading.value = false
  }
}

// ============================================================================
// Item-Click → Chat-Kontext
// ============================================================================

// Select a chapter for context-aware chat
async function selectChapterForChat(chapter: Chapter) {
  selectedContext.value = {
    type: 'chapter',
    id: chapter.id,
    title: chapter.title,
    data: chapter
  }

  // Reset state
  lessonExplanations.value = []
  lmSuggestions.value = []

  // Load context actions and existing theories in parallel
  await Promise.all([
    loadContextActions('chapter'),
    loadChapterTheories(chapter.id)
  ])
}

// Select a lesson for context-aware chat
async function selectLessonForChat(chapter: Chapter, lesson: Lesson) {
  selectedContext.value = {
    type: 'lesson',
    id: lesson.id,
    title: lesson.title,
    data: lesson,
    parentChapter: chapter
  }

  // Reset state
  chapterTheories.value = []

  // Load context actions, LM suggestions, and existing explanations in parallel
  await Promise.all([
    loadContextActions('lesson'),
    loadLMSuggestions(lesson, chapter),
    loadLessonExplanations(lesson.id)
  ])
}

// Load existing theories for a chapter
// Delegate to composable (shared with TutorTab)
async function loadChapterTheories(chapterId: string) {
  await theoryMgmt.loadChapterTheories(chapterId)
}

async function loadLessonExplanations(lessonId: string) {
  await theoryMgmt.loadLessonExplanations(lessonId)
}

// Analyze lesson with selected files
async function analyzeLessonWithFiles(chapter: Chapter, lesson: Lesson) {
  if (!props.course) return

  analyzingLessonId.value = lesson.id

  try {
    // Get selected file IDs
    const fileIds = selectedFileIds.value

    // Call API to analyze lesson with files
    const response = await http.post('/admin/ai-studio/analyze-lesson', {
      course_id: props.course.course_id,
      chapter_id: chapter.id,
      chapter_title: chapter.title,
      lesson_id: lesson.id,
      lesson_title: lesson.title,
      file_ids: fileIds,
      request_type: 'lm_recommendation'
    })

    if (response.data.success) {
      const analysis = response.data.data

      // Show recommendations in chat
      addSystemMessage(`**Analyse für "${lesson.title}":**\n\n${analysis.summary || ''}\n\n**Empfohlene Lernmethoden:**\n${(analysis.recommended_lms || []).map((lm: any) => `- ${lm.name}: ${lm.reason}`).join('\n')}`)

      // If we have LM suggestions, update the UI
      if (analysis.recommended_lms?.length) {
        lmSuggestions.value = analysis.recommended_lms.map((lm: any) => ({
          lm_id: lm.lm_id,
          name: lm.name,
          reason: lm.reason,
          confidence: lm.confidence || 0.8
        }))
        showLmSuggestions.value = true
      }
    }
  } catch (error) {
    console.error('Failed to analyze lesson:', error)
    addSystemMessage(`Fehler bei der Analyse von "${lesson.title}"`)
  } finally {
    analyzingLessonId.value = null
  }
}

// Analyze selected context (chapter or lesson) with materials
async function analyzeSelectedContext() {
  if (!selectedContext.value || !props.course) return

  isAnalyzing.value = true

  try {
    const isChapter = selectedContext.value.type === 'chapter'
    const fileIds = selectedFileIds.value

    const response = await http.post('/admin/ai-studio/analyze-lesson', {
      course_id: props.course.course_id,
      chapter_id: isChapter ? selectedContext.value.id : selectedContext.value.parentChapter?.id,
      chapter_title: isChapter ? selectedContext.value.title : selectedContext.value.parentChapter?.title,
      lesson_id: isChapter ? null : selectedContext.value.id,
      lesson_title: isChapter ? null : selectedContext.value.title,
      file_ids: fileIds,
      request_type: 'lm_recommendation'
    })

    if (response.data.success) {
      const analysis = response.data.data

      // Show analysis in chat
      const contextName = isChapter ? `Kapitel "${selectedContext.value.title}"` : `Lektion "${selectedContext.value.title}"`
      addSystemMessage(`**Analyse für ${contextName}:**\n\n${analysis.summary || ''}\n\n${fileIds.length ? `📁 ${fileIds.length} Datei(en) analysiert` : ''}`)

      // Update LM suggestions if lesson
      if (!isChapter && analysis.recommended_lms?.length) {
        lmSuggestions.value = analysis.recommended_lms.map((lm: any) => ({
          lm_id: lm.lm_id,
          name: lm.name,
          reason: lm.reason,
          confidence: lm.confidence || 0.8,
          icon: lm.icon || '📝',
          group: lm.group || 'B'
        }))
        showLmSuggestions.value = true
      }
    }
  } catch (error) {
    console.error('Failed to analyze context:', error)
    addSystemMessage('Fehler bei der Analyse')
  } finally {
    isAnalyzing.value = false
  }
}

// Generate theory for chapter (summary) or lesson (theory sheet)
async function generateTheory() {
  if (!selectedContext.value || !props.course) return

  isGeneratingTheory.value = true

  try {
    const isChapter = selectedContext.value.type === 'chapter'
    const fileIds = selectedFileIds.value

    // Build prompt based on context type
    const prompt = isChapter
      ? `Erstelle eine Zusammenfassung für das Kapitel "${selectedContext.value.title}". Fasse alle wichtigen Konzepte zusammen.`
      : `Erstelle ein detailliertes Theorieblatt für die Lektion "${selectedContext.value.title}". Erkläre alle wichtigen Begriffe und Konzepte.`

    // Send to chat for processing
    inputMessage.value = prompt
    selectedMode.value = isChapter ? 'chapter_summary' : 'lesson_theory'
    await sendMessage()

    addSystemMessage(isChapter
      ? `📚 Kapitel-Zusammenfassung wird erstellt für "${selectedContext.value.title}"...`
      : `📖 Theorieblatt wird erstellt für "${selectedContext.value.title}"...`
    )
  } catch (error) {
    console.error('Failed to generate theory:', error)
    addSystemMessage('Fehler beim Generieren der Theorie')
  } finally {
    isGeneratingTheory.value = false
  }
}

// Load AI-powered LM suggestions for a lesson
async function loadLMSuggestions(lesson: Lesson, chapter: Chapter) {
  lmSuggestionsLoading.value = true
  showLmSuggestions.value = true
  lmSuggestions.value = []

  try {
    // Get existing LM types from the lesson
    const existingLmIds = (lesson.methods || [])
      .map(m => {
        // Extract LM type number from method type string (e.g., "LM12" -> 12)
        const match = m.type?.match(/LM(\d+)/i)
        return match ? parseInt(match[1]) : null
      })
      .filter((id): id is number => id !== null)

    const result = await getLMSuggestions({
      lesson_title: lesson.title,
      lesson_content: lesson.description || '',
      chapter_title: chapter.title,
      course_title: props.course?.title || '',
      existing_lm_ids: existingLmIds,
      max_suggestions: 6
    })

    lmSuggestions.value = result.suggestions || []
  } catch (err) {
    console.warn('Failed to load LM suggestions:', err)
    lmSuggestions.value = []
  } finally {
    lmSuggestionsLoading.value = false
  }
}

// Clear selected context
function clearContext() {
  selectedContext.value = null
  contextActions.value = []
  lmSuggestions.value = []
  showLmSuggestions.value = false
  theoryMgmt.reset() // Reset theory/explanation state via composable
}

// Create a learning method from an LM suggestion
function createLMFromSuggestion(suggestion: LMSuggestion) {
  // Build a prompt to generate this specific LM type
  const prompt = `Erstelle eine Lernmethode vom Typ "${suggestion.name}" (LM${String(suggestion.lm_id).padStart(2, '0')}) für die Lektion "${selectedContext.value?.title}".

Begründung: ${suggestion.reason}

Die Methode sollte:
- Zum Thema der Lektion passen
- Die Stärken von "${suggestion.name}" nutzen (${suggestion.description})
- Interaktiv und lehrreich sein`

  inputMessage.value = prompt
  selectedMode.value = 'method'
  sendMessage()
}

// Load context-specific actions
async function loadContextActions(entityType: 'chapter' | 'lesson' | 'method') {
  contextActionsLoading.value = true
  try {
    const actions = await getActionsForEntity(entityType)
    if (actions && actions.length > 0) {
      contextActions.value = actions.map(a => ({
        action_id: a.action_id,
        action_key: a.action_key,
        label: a.label,
        icon: a.icon || '📋',
        prompt_template: a.prompt_template,
        mode: a.mode,
        color: a.color
      }))
    } else {
      // Use category-specific fallback
      contextActions.value = getFallbackActionsForEntity(entityType)
    }
  } catch (err) {
    console.warn(`Failed to load ${entityType} actions:`, err)
    contextActions.value = getFallbackActionsForEntity(entityType)
  } finally {
    contextActionsLoading.value = false
  }
}

// Fallback actions per entity type
function getFallbackActionsForEntity(entityType: string): QuickAction[] {
  const fallbacks: Record<string, QuickAction[]> = {
    chapter: [
      { action_id: 'fb-c1', action_key: 'chapter_theory_generate', label: 'Theorie generieren', icon: '📄', prompt_template: `Generiere ein Theorieblatt für das Kapitel "${selectedContext.value?.title}".`, mode: 'theory' },
      { action_id: 'fb-c2', action_key: 'chapter_lesson_add', label: 'Lektion hinzufügen', icon: '➕', prompt_template: `Erstelle eine neue Lektion für das Kapitel "${selectedContext.value?.title}".`, mode: 'lesson' },
      { action_id: 'fb-c3', action_key: 'improve', label: 'Verbessern', icon: '✨', prompt_template: `Wie kann ich das Kapitel "${selectedContext.value?.title}" verbessern?`, mode: 'improve' }
    ],
    lesson: [
      { action_id: 'fb-l1', action_key: 'lesson_task_create', label: 'Aufgabe erstellen', icon: '📝', prompt_template: `Erstelle eine Aufgabe für die Lektion "${selectedContext.value?.title}".`, mode: 'task' },
      { action_id: 'fb-l2', action_key: 'lesson_quiz_add', label: 'Quiz hinzufügen', icon: '❓', prompt_template: `Erstelle ein Quiz für die Lektion "${selectedContext.value?.title}".`, mode: 'quiz' },
      { action_id: 'fb-l3', action_key: 'explain', label: 'Erklären', icon: '📖', prompt_template: `Erkläre mir die Lektion "${selectedContext.value?.title}" einfach und verständlich.`, mode: 'explain' }
    ],
    method: [
      { action_id: 'fb-m1', action_key: 'method_improve', label: 'Inhalt verbessern', icon: '✨', prompt_template: `Verbessere den Inhalt dieser Lernmethode.`, mode: 'improve' },
      { action_id: 'fb-m2', action_key: 'method_variant_create', label: 'Variante erstellen', icon: '🔄', prompt_template: `Erstelle eine alternative Version dieser Lernmethode.`, mode: 'variant' }
    ]
  }
  return fallbacks[entityType] || []
}

// Send context-aware action
function sendContextAction(action: QuickAction) {
  // Fill in context variables in prompt
  let prompt = action.prompt_template
  if (selectedContext.value) {
    prompt = prompt.replace('{{context_title}}', selectedContext.value.title)
    prompt = prompt.replace('{{context_type}}', selectedContext.value.type)
  }

  selectedMode.value = action.mode || ''
  inputMessage.value = prompt
  sendMessage()
}

// ============================================================================
// Bestätigungs-Flow (Confirmation)
// ============================================================================

// Check if response contains generated content that needs confirmation
function checkForGeneratedContent(response: any): PendingAction | null {
  // Check for structured JSON response with generated content
  if (response.generated_content && response.requires_confirmation) {
    const entity = response.output_entity || 'chapter'
    let previewText = ''

    if (entity === 'chapter' && response.generated_content.title) {
      previewText = `Neues Kapitel: "${response.generated_content.title}"\n\n`
      if (response.generated_content.description) {
        previewText += response.generated_content.description + '\n\n'
      }
      if (response.generated_content.lessons?.length) {
        previewText += `${response.generated_content.lessons.length} Lektionen`
      }
    } else if (entity === 'lesson' && response.generated_content.title) {
      previewText = `Neue Lektion: "${response.generated_content.title}"\n\n`
      if (response.generated_content.description) {
        previewText += response.generated_content.description
      }
    } else if (entity === 'method') {
      previewText = `Neue Lernmethode: ${JSON.stringify(response.generated_content, null, 2).slice(0, 200)}...`
    } else {
      previewText = typeof response.generated_content === 'string'
        ? response.generated_content.slice(0, 300)
        : JSON.stringify(response.generated_content, null, 2).slice(0, 300)
    }

    return {
      type: 'create',
      entity: entity as 'chapter' | 'lesson' | 'method',
      actionKey: response.action_key || 'unknown',
      generatedData: response.generated_content,
      previewText: previewText,
      parentChapter: selectedContext.value?.parentChapter,
      session_id: response.session_id
    }
  }

  return null
}

// Confirm the pending action (save to DB)
async function confirmPendingAction() {
  if (!pendingAction.value || !session.value) return

  confirmLoading.value = true
  try {
    const action = pendingAction.value

    // Apply the generated content to draft structure
    if (action.entity === 'chapter' && action.generatedData) {
      // Add generated chapter to draft structure
      if (!draftStructure.value) draftStructure.value = { chapters: [] }
      if (!draftStructure.value.chapters) draftStructure.value.chapters = []

      const newChapter: Chapter = {
        id: `ch-${Date.now()}`,
        title: action.generatedData.title || 'Neues Kapitel',
        description: action.generatedData.description || '',
        lessons: (action.generatedData.lessons || []).map((l: any, i: number) => ({
          id: `ls-${Date.now()}-${i}`,
          title: l.title || `Lektion ${i + 1}`,
          description: l.description || '',
          methods: l.methods || []
        }))
      }

      draftStructure.value.chapters.push(newChapter)
      expandedChapters.value.add(newChapter.id)

      chatMessages.value.push({
        role: 'assistant',
        content: `✅ Kapitel "${newChapter.title}" wurde erstellt mit ${newChapter.lessons?.length || 0} Lektionen.`
      })
    } else if (action.entity === 'lesson' && action.generatedData && action.parentChapter) {
      // Add generated lesson to parent chapter
      const chapter = draftStructure.value?.chapters?.find(c => c.id === action.parentChapter?.id)
      if (chapter) {
        if (!chapter.lessons) chapter.lessons = []

        const newLesson: Lesson = {
          id: `ls-${Date.now()}`,
          title: action.generatedData.title || 'Neue Lektion',
          description: action.generatedData.description || '',
          content: action.generatedData.content,
          methods: action.generatedData.methods || []
        }

        chapter.lessons.push(newLesson)

        chatMessages.value.push({
          role: 'assistant',
          content: `✅ Lektion "${newLesson.title}" wurde zum Kapitel "${chapter.title}" hinzugefügt.`
        })
      }
    } else if (action.entity === 'method' && action.generatedData && selectedContext.value) {
      chatMessages.value.push({
        role: 'assistant',
        content: `✅ Lernmethode wurde erstellt.`
      })
    }

    // Clear pending action
    pendingAction.value = null
    scrollToBottom()

  } catch (err: any) {
    error.value = 'Fehler beim Speichern: ' + (err.message || 'Unbekannt')
  } finally {
    confirmLoading.value = false
  }
}

// Reject the pending action
function rejectPendingAction() {
  chatMessages.value.push({
    role: 'assistant',
    content: '❌ Aktion wurde verworfen.'
  })
  pendingAction.value = null
}

// Modify the pending action (re-open chat with feedback)
function modifyPendingAction() {
  if (!pendingAction.value) return

  inputMessage.value = 'Bitte ändere das Ergebnis. Folgende Anpassungen: '
  pendingAction.value = null
  inputField.value?.focus()
}

// Computed
const hasChanges = computed(() => (draftStructure.value?.chapters?.length || 0) > 0)

const draftStats = computed(() => {
  const chapters = draftStructure.value?.chapters || []
  let lessons = 0, methods = 0
  for (const ch of chapters) {
    lessons += ch.lessons?.length || 0
    for (const l of ch.lessons || []) {
      methods += l.methods?.length || 0
    }
  }
  return { chapters: chapters.length, lessons, methods }
})

// Expose for parent
defineExpose({
  sessionMeta: computed(() => session.value ? {
    sessionId: session.value.session_id,
    status: session.value.status,
    totalTokensUsed: session.value.total_tokens_used
  } : null),
  draftStats,
  createSession,
  hasSession: computed(() => !!session.value)
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

// Data Loading
async function loadExistingSession() {
  if (!props.course) return
  try {
    const res = await http.get(`/admin/course-authoring/courses/${props.course.course_id}/sessions?status=active`)
    if (res.data.success && res.data.data.sessions.length > 0) {
      await loadSession(res.data.data.sessions[0].session_id)
    }
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
  } catch (err) {
    console.error('Failed to load session:', err)
  }
}

async function loadCourseFiles() {
  if (!props.course) return
  try {
    const res = await http.get(`/admin/courses/${props.course.course_id}/files`)
    if (res.data.success) {
      const files = res.data.files || []
      sessionFiles.value = files.map((f: any) => ({
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
        id: ch.chapter_id,
        title: ch.title,
        description: ch.description || '',
        lessons: lessons.map((l: any) => ({
          id: l.lesson_id,
          title: l.title,
          methods: l.content?.lm_primary ? [{ id: `lm-${l.lesson_id}`, type: l.content.lm_primary, title: l.title }] : []
        }))
      })
    }

    if (structureChapters.length > 0) {
      draftStructure.value = { chapters: structureChapters, activity_log: [] }
      // Auto-expand first chapter
      if (structureChapters[0]) expandedChapters.value.add(structureChapters[0].id)
    }
  } catch (err) {
    console.error('Failed to load structure:', err)
  }
}

// Session Management
async function createSession() {
  if (!props.course) return
  creatingSession.value = true
  error.value = null

  try {
    const res = await http.post('/admin/course-authoring/sessions', { course_id: props.course.course_id })
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

async function finalizeSession() {
  if (!session.value || !confirm('Session finalisieren? Änderungen werden in den Kurs übernommen.')) return

  finalizing.value = true
  try {
    const res = await http.post(`/admin/course-authoring/sessions/${session.value.session_id}/finalize`)
    if (res.data.success) {
      alert(`Erfolgreich! ${res.data.data.stats.chapters} Kapitel, ${res.data.data.stats.lessons} Lektionen`)
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

// Chat
async function sendMessage() {
  if (!inputMessage.value.trim() || chatLoading.value) return

  if (!session.value) {
    await createSession()
    if (!session.value) return
  }

  const msg = inputMessage.value.trim()
  inputMessage.value = ''
  chatMessages.value.push({ role: 'user', content: msg, timestamp: new Date().toISOString() })
  scrollToBottom()

  chatLoading.value = true
  try {
    const res = await http.post(`/admin/course-authoring/sessions/${session.value.session_id}/chat`, {
      message: msg,
      mode: selectedMode.value || undefined,
      file_ids: selectedFileIds.value
    })

    if (res.data.success) {
      const responseData = res.data.data

      chatMessages.value.push({
        role: 'assistant',
        content: responseData.assistant_message,
        operations: responseData.operations_applied
      })

      // Check if response contains generated content that needs confirmation
      const pending = checkForGeneratedContent(responseData)
      if (pending) {
        pendingAction.value = pending
      }

      // Update draft structure if provided
      if (responseData.draft_structure) {
        draftStructure.value = responseData.draft_structure
      }
    } else {
      error.value = res.data.error || 'Chat-Fehler'
    }
  } catch (err: any) {
    error.value = 'Chat-Fehler: ' + (err.message || 'Unbekannt')
  } finally {
    chatLoading.value = false
    scrollToBottom()
  }
}

function sendQuickAction(action: QuickAction) {
  selectedMode.value = action.mode || ''
  inputMessage.value = action.prompt_template
  sendMessage()
}

function addSystemMessage(content: string) {
  chatMessages.value.push({
    role: 'assistant',
    content,
    timestamp: new Date().toISOString()
  })
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// File Management
function toggleFileSelection(fileId: string) {
  const idx = selectedFileIds.value.indexOf(fileId)
  if (idx === -1) selectedFileIds.value.push(fileId)
  else selectedFileIds.value.splice(idx, 1)
}

function selectAllFiles() {
  if (selectedFileIds.value.length === sessionFiles.value.length) {
    selectedFileIds.value = []
  } else {
    selectedFileIds.value = sessionFiles.value.map(f => f.id)
  }
}

function clearFileSelection() {
  selectedFileIds.value = []
}

function openFilePreview(file: CourseFile) {
  windowStore.openWindow({
    type: 'admin-file-preview',
    title: `Vorschau: ${file.name}`,
    icon: '📄',
    payload: { file },
    size: { width: 800, height: 600 }
  })
}

function triggerFileUpload() {
  materialFileInput.value?.click()
}

async function handleMaterialUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length || !props.course) return

  isUploadingFile.value = true
  const files = Array.from(input.files)

  try {
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_category', 'material')

      await http.post(`/admin/courses/${props.course.course_id}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }

    // Reload files list
    await loadCourseFiles()
  } catch (error) {
    console.error('File upload failed:', error)
  } finally {
    isUploadingFile.value = false
    input.value = '' // Reset input
  }
}

// Tree
function toggleChapter(chapterId: string) {
  if (expandedChapters.value.has(chapterId)) {
    expandedChapters.value.delete(chapterId)
  } else {
    expandedChapters.value.add(chapterId)
  }
}

// ============================================================================
// Chapter/Lesson Actions
// ============================================================================

function openChapterPreview(chapter: Chapter) {
  windowStore.openWindow({
    type: 'admin-chapter-preview',
    title: `Kapitel: ${chapter.title}`,
    icon: '📖',
    payload: {
      chapter: {
        chapter_id: chapter.id,
        title: chapter.title,
        description: chapter.description,
        lessons: chapter.lessons,
        created_at: new Date().toISOString()
      }
    },
    size: { width: 650, height: 700 }
  })
}

function openLessonPreview(chapter: Chapter, lesson: Lesson) {
  // Calculate lesson position within chapter
  const lessonIndex = chapter.lessons?.findIndex(l => l.id === lesson.id) ?? 0
  const totalLessons = chapter.lessons?.length ?? 1
  const position = `${lessonIndex + 1}/${totalLessons}`

  windowStore.openWindow({
    type: 'admin-lesson-preview',
    title: `Vorschau: ${lesson.title}`,
    icon: '📄',
    payload: {
      lesson: {
        lesson_id: lesson.id,
        title: lesson.title,
        description: lesson.description,
        content: lesson.content,
        duration_minutes: lesson.duration_minutes,
        methods: lesson.methods
      },
      chapter: {
        chapter_id: chapter.id,
        title: chapter.title
      },
      position
    },
    size: { width: 600, height: 700 }
  })
}

function editChapter(chapter: Chapter) {
  // TODO: Open chapter editor window
  console.log('Edit chapter:', chapter.id)
}

function editLesson(chapter: Chapter, lesson: Lesson) {
  // TODO: Open lesson editor window
  console.log('Edit lesson:', lesson.id, 'in chapter:', chapter.id)
}

function deleteChapter(chapterId: string, chapterIndex: number) {
  if (!confirm('Kapitel wirklich löschen? Alle Lektionen werden ebenfalls gelöscht.')) return
  if (!draftStructure.value?.chapters) return

  draftStructure.value.chapters.splice(chapterIndex, 1)
  expandedChapters.value.delete(chapterId)
}

function deleteLesson(chapterId: string, chapterIndex: number, lessonId: string, lessonIndex: number) {
  if (!confirm('Lektion wirklich löschen?')) return
  if (!draftStructure.value?.chapters?.[chapterIndex]?.lessons) return

  draftStructure.value.chapters[chapterIndex].lessons!.splice(lessonIndex, 1)
}

// ============================================================================
// Drag & Drop for Reordering
// ============================================================================

function handleChapterDragStart(e: DragEvent, chapterIndex: number) {
  draggingType.value = 'chapter'
  draggingFromIndex.value = chapterIndex
  e.dataTransfer!.effectAllowed = 'move'
  e.dataTransfer!.setData('text/plain', `chapter:${chapterIndex}`)
}

function handleChapterDragOver(e: DragEvent, chapterId: string) {
  if (draggingType.value !== 'chapter') return
  dragOverChapterId.value = chapterId
}

function handleChapterDragLeave() {
  dragOverChapterId.value = null
}

function handleChapterDrop(e: DragEvent, targetIndex: number) {
  if (draggingType.value !== 'chapter') return
  if (!draftStructure.value?.chapters) return

  const fromIndex = draggingFromIndex.value
  if (fromIndex === targetIndex || fromIndex === -1) return

  // Move chapter
  const chapters = draftStructure.value.chapters
  const [moved] = chapters.splice(fromIndex, 1)
  chapters.splice(targetIndex, 0, moved)

  handleDragEnd()
}

function handleLessonDragStart(e: DragEvent, chapterIndex: number, lessonIndex: number) {
  draggingType.value = 'lesson'
  draggingFromChapterIndex.value = chapterIndex
  draggingFromIndex.value = lessonIndex
  e.dataTransfer!.effectAllowed = 'move'
  e.dataTransfer!.setData('text/plain', `lesson:${chapterIndex}:${lessonIndex}`)
}

function handleLessonDragOver(e: DragEvent, lessonId: string) {
  if (draggingType.value !== 'lesson') return
  dragOverLessonId.value = lessonId
}

function handleLessonDragLeave() {
  dragOverLessonId.value = null
}

function handleLessonDrop(e: DragEvent, targetChapterIndex: number, targetLessonIndex: number) {
  if (draggingType.value !== 'lesson') return
  if (!draftStructure.value?.chapters) return

  const fromChapterIndex = draggingFromChapterIndex.value
  const fromLessonIndex = draggingFromIndex.value

  if (fromChapterIndex === -1 || fromLessonIndex === -1) return
  if (fromChapterIndex === targetChapterIndex && fromLessonIndex === targetLessonIndex) return

  const sourceChapter = draftStructure.value.chapters[fromChapterIndex]
  const targetChapter = draftStructure.value.chapters[targetChapterIndex]

  if (!sourceChapter?.lessons || !targetChapter?.lessons) return

  // Remove from source
  const [moved] = sourceChapter.lessons.splice(fromLessonIndex, 1)

  // Adjust target index if moving within same chapter and target is after source
  let adjustedTargetIndex = targetLessonIndex
  if (fromChapterIndex === targetChapterIndex && fromLessonIndex < targetLessonIndex) {
    adjustedTargetIndex--
  }

  // Insert at target
  targetChapter.lessons.splice(adjustedTargetIndex, 0, moved)

  handleDragEnd()
}

function handleDragEnd() {
  draggingType.value = null
  draggingFromIndex.value = -1
  draggingFromChapterIndex.value = -1
  dragOverChapterId.value = null
  dragOverLessonId.value = null
}

// Helpers
function getFileIcon(type: string): string {
  const icons: Record<string, string> = { pdf: '📕', txt: '📝', doc: '📘', docx: '📘' }
  return icons[type?.toLowerCase()] || '📄'
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Use formatDate from composable
const { formatDate, getStyleEmoji } = theoryMgmt

// Open theory in Tutor tab (via window store)
function openTheoryInTutor(theory: { theoryId: string; title?: string }) {
  windowStore.openWindow({
    type: 'admin-ai-studio',
    title: 'KI-Studio: Tutor',
    icon: '🤖',
    payload: {
      tab: 'tutor',
      chapter: selectedContext.value?.data,
      theoryId: theory.theoryId
    },
    size: { width: 1200, height: 800 }
  })
}

// Open explanation in Tutor tab
function openExplanationInTutor(expl: { explanationId: string; title?: string }) {
  windowStore.openWindow({
    type: 'admin-ai-studio',
    title: 'KI-Studio: Tutor',
    icon: '🤖',
    payload: {
      tab: 'tutor',
      lesson: selectedContext.value?.data,
      chapter: selectedContext.value?.parentChapter,
      explanationId: expl.explanationId
    },
    size: { width: 1200, height: 800 }
  })
}

function resetState() {
  session.value = null
  chatMessages.value = []
  draftStructure.value = null
  selectedFileIds.value = []
  expandedChapters.value.clear()
}

// Mount
onMounted(async () => {
  // Load quick actions from DB
  await loadQuickActions()

  if (props.course) {
    await loadExistingSession()
    await loadCourseFiles()
    await loadExistingStructure()
  }
})
</script>

<style scoped>
.kurs-builder-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
}

/* Header */
.builder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  font-size: 1.5rem;
}

.header-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.125rem;
}

.course-badge, .stats-badge {
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  background: rgba(255,255,255,0.2);
  border-radius: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
}

.session-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.session-dot.active { background: #22c55e; }
.session-dot.inactive { background: rgba(255,255,255,0.4); }

.session-id {
  font-family: monospace;
  opacity: 0.7;
}

.btn-primary, .btn-success {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-primary {
  background: rgba(255,255,255,0.2);
  color: white;
}

.btn-primary:hover:not(:disabled) { background: rgba(255,255,255,0.3); }

.btn-success {
  background: #22c55e;
  color: white;
}

.btn-success:hover:not(:disabled) { background: #16a34a; }
.btn-primary:disabled, .btn-success:disabled { opacity: 0.5; cursor: not-allowed; }

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.125rem; font-weight: 500; margin: 0; }
.empty-hint { font-size: 0.875rem; opacity: 0.7; margin: 0.25rem 0 0; }

/* Main Content */
.builder-content {
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 1rem;
  overflow: hidden;
}

/* Chat Column */
.chat-column {
  flex: 6;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: var(--color-text-secondary);
}

.welcome-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.chat-welcome h4 { margin: 0; font-size: 1rem; color: var(--color-text-primary); }
.chat-welcome p { margin: 0.25rem 0; font-size: 0.875rem; }
.welcome-hint { color: var(--color-primary); font-size: 0.75rem !important; }

.chat-message {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
}

.chat-message.user { align-self: flex-end; flex-direction: row-reverse; }
.chat-message.assistant { align-self: flex-start; }

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-surface-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
}

.chat-message.user .message-content {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.chat-message.assistant .message-content {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  border-bottom-left-radius: 0.25rem;
}

.message-ops {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.op-badge {
  padding: 0.125rem 0.375rem;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border-radius: 0.25rem;
  font-size: 0.625rem;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background: var(--color-surface-secondary);
  border-radius: 1rem;
  width: fit-content;
}

.typing-indicator .dot {
  width: 6px;
  height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator .dot:nth-child(3) { animation-delay: 0.4s; }
.typing-text { margin-left: 0.5rem; font-size: 0.75rem; color: var(--color-text-secondary); }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}

/* Quick Actions Grid */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.875rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.quick-action-btn:hover:not(:disabled) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.quick-action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.qa-icon { font-size: 1rem; }
.qa-label { color: inherit; }

/* Action Colors */
.quick-action-btn.action-blue:hover:not(:disabled) { background: #3b82f6; border-color: #3b82f6; }
.quick-action-btn.action-green:hover:not(:disabled) { background: #22c55e; border-color: #22c55e; }
.quick-action-btn.action-purple:hover:not(:disabled) { background: #8b5cf6; border-color: #8b5cf6; }
.quick-action-btn.action-orange:hover:not(:disabled) { background: #f97316; border-color: #f97316; }
.quick-action-btn.action-yellow:hover:not(:disabled) { background: #eab308; border-color: #eab308; }

/* Actions Loading */
.actions-loading {
  grid-column: span 2;
  text-align: center;
  padding: 1rem;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

/* Context Banner */
.context-banner {
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-top: 1px solid var(--color-primary);
  border-bottom: 1px solid var(--color-border);
}

.context-info-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.context-icon {
  font-size: 1.25rem;
}

.context-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.context-type {
  font-size: 0.6875rem;
  text-transform: uppercase;
  color: var(--color-primary);
  font-weight: 600;
  letter-spacing: 0.05em;
}

.context-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.context-close {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  color: var(--color-text-tertiary);
  transition: all 0.15s;
}

.context-close:hover {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
}

/* Context Actions */
.context-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.context-action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-primary);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-primary);
  cursor: pointer;
  transition: all 0.15s;
}

.context-action-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
}

.context-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-text {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* LM Suggestions Section */
.lm-suggestions-section {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
}

.lm-suggestions-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.lm-header-icon {
  font-size: 1rem;
}

.lm-header-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.lm-loading {
  font-size: 0.6875rem;
  color: var(--color-primary);
  animation: pulse 1.5s infinite;
}

.lm-suggestions-loading {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem;
  justify-content: center;
}

.lm-suggestions-loading .dot {
  width: 6px;
  height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.lm-suggestions-loading .dot:nth-child(1) { animation-delay: -0.32s; }
.lm-suggestions-loading .dot:nth-child(2) { animation-delay: -0.16s; }
.lm-suggestions-loading .dot:nth-child(3) { animation-delay: 0s; }

.lm-suggestions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.lm-suggestion-btn {
  display: flex;
  flex-direction: column;
  padding: 0.625rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
}

.lm-suggestion-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: rgba(99, 102, 241, 0.05);
  transform: translateY(-1px);
}

.lm-suggestion-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.lm-btn-top {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.375rem;
}

.lm-icon {
  font-size: 1rem;
}

.lm-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lm-btn-bottom {
  display: flex;
}

.lm-reason {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.lm-no-suggestions {
  text-align: center;
  padding: 1rem;
  color: var(--color-text-tertiary);
  font-size: 0.8125rem;
}

/* LM Group Colors */
.lm-group-a { border-left: 3px solid #3b82f6; }
.lm-group-b { border-left: 3px solid #22c55e; }
.lm-group-c { border-left: 3px solid #f59e0b; }
.lm-group-d { border-left: 3px solid #8b5cf6; }
.lm-group-e { border-left: 3px solid #06b6d4; }
.lm-group-f { border-left: 3px solid #ec4899; }

/* Primary action button style */
.action-btn--primary {
  background: rgba(99, 102, 241, 0.1) !important;
}

.action-btn--primary:hover {
  background: var(--color-primary) !important;
  color: white;
}

/* Confirmation Panel */
.confirmation-panel {
  padding: 1rem;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
  border-top: 2px solid #22c55e;
  border-bottom: 1px solid var(--color-border);
}

.confirm-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.confirm-icon {
  font-size: 1.25rem;
}

.confirm-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #22c55e;
}

.confirm-preview {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  max-height: 150px;
  overflow-y: auto;
}

.preview-text {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: inherit;
}

.confirm-actions {
  display: flex;
  gap: 0.5rem;
}

.confirm-btn {
  flex: 1;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.15s;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-btn--accept {
  background: #22c55e;
  border-color: #22c55e;
  color: white;
}

.confirm-btn--accept:hover:not(:disabled) {
  background: #16a34a;
  border-color: #16a34a;
}

.confirm-btn--modify {
  background: var(--color-surface);
  border-color: #f59e0b;
  color: #f59e0b;
}

.confirm-btn--modify:hover:not(:disabled) {
  background: #f59e0b;
  color: white;
}

.confirm-btn--reject {
  background: var(--color-surface);
  border-color: #ef4444;
  color: #ef4444;
}

.confirm-btn--reject:hover:not(:disabled) {
  background: #ef4444;
  color: white;
}

/* Chat Input */
.chat-input-wrapper {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
}

.input-row {
  display: flex;
  gap: 0.5rem;
}

.input-row textarea {
  flex: 1;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.875rem;
  resize: none;
}

.input-row textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.send-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
}

.send-btn:hover:not(:disabled) { opacity: 0.9; }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
}

.mode-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.75rem;
}

.context-info {
  font-size: 0.75rem;
  color: var(--color-primary);
}

/* Right Column */
.right-column {
  flex: 4;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 300px;
}

/* Panels */
.panel {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.structure-panel { flex: 1; min-height: 0; }
.materials-panel { height: 220px; }

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.panel-icon { font-size: 1rem; }
.panel-title { flex: 1; font-size: 0.875rem; font-weight: 600; }
.panel-badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

.panel-action {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}

.panel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}

.panel-empty span { font-size: 1.5rem; margin-bottom: 0.25rem; }

.panel-footer {
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary);
  border-top: 1px solid var(--color-border);
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

/* Structure Tree */
.tree-chapter {
  margin-bottom: 0.25rem;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.15s;
}

.chapter-header:hover { background: var(--color-surface-secondary); }

.expand-icon {
  font-size: 0.625rem;
  width: 1rem;
  text-align: center;
  color: var(--color-text-tertiary);
}

.chapter-icon { font-size: 0.875rem; }
.chapter-title { flex: 1; font-size: 0.8125rem; font-weight: 500; }
.chapter-count {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.chapter-lessons {
  margin-left: 1.5rem;
  border-left: 1px solid var(--color-border);
  padding-left: 0.5rem;
}

.tree-lesson {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.lesson-icon { font-size: 0.75rem; }
.lesson-title { flex: 1; }
.lesson-methods {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
}

/* Drag Handle */
.drag-handle {
  cursor: grab;
  color: var(--color-text-tertiary);
  font-size: 0.75rem;
  opacity: 0.5;
  transition: opacity 0.15s;
  user-select: none;
}

.drag-handle:hover {
  opacity: 1;
}

.drag-handle:active {
  cursor: grabbing;
}

/* Item Actions */
.item-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.15s;
}

.chapter-header:hover .item-actions,
.tree-lesson:hover .item-actions {
  opacity: 1;
}

.action-btn {
  padding: 0.25rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  opacity: 0.7;
  transition: all 0.15s;
}

.action-btn:hover {
  opacity: 1;
  background: var(--color-surface);
}

.action-btn--danger:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* Drag Over States */
.tree-chapter.drag-over {
  background: var(--color-primary-subtle);
  border-radius: 0.375rem;
}

.tree-lesson.drag-over {
  background: var(--color-primary-subtle);
  border-radius: 0.25rem;
}

.tree-chapter[draggable="true"],
.tree-lesson[draggable="true"] {
  transition: transform 0.15s, background 0.15s;
}

.tree-chapter[draggable="true"]:active,
.tree-lesson[draggable="true"]:active {
  opacity: 0.6;
}

/* Files List */
.files-list {
  padding: 0.5rem !important;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.15s;
}

.file-item:hover { background: var(--color-surface-secondary); }
.file-item.selected { background: var(--color-primary-subtle); }

.file-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

.file-icon { font-size: 1.25rem; }

.file-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.preview-btn {
  padding: 0.25rem 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.15s;
}

.preview-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.link-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: inherit;
}

.link-btn:hover { text-decoration: underline; }

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid #ef4444;
  color: #ef4444;
  font-size: 0.875rem;
}

.error-banner button {
  background: none;
  border: none;
  color: currentColor;
  font-size: 1.25rem;
  cursor: pointer;
}

/* ============================================================================
   Workflow Sections (Analyze → Theory → LMs)
   ============================================================================ */
.workflow-section {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.workflow-section:hover {
  border-color: var(--color-primary);
}

.workflow-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.workflow-icon {
  font-size: 1rem;
}

.workflow-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.workflow-badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 500;
}

.workflow-action-btn {
  width: 100%;
  padding: 0.625rem 1rem;
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
}

.workflow-action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.workflow-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.workflow-action-btn.is-loading {
  background: var(--color-surface-secondary);
  color: var(--color-primary);
  border: 1px dashed var(--color-primary);
}

.workflow-action-btn--theory {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.workflow-action-btn--theory:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.workflow-hint {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-top: 0.5rem;
  text-align: center;
}

/* Section-specific styling */
.analyze-section {
  border-left: 3px solid #3b82f6;
}

.theory-section {
  border-left: 3px solid #22c55e;
}

.lm-section {
  border-left: 3px solid #f59e0b;
}

/* Analyze button (in tree) */
.action-btn--analyze {
  background: rgba(59, 130, 246, 0.1) !important;
}

.action-btn--analyze:hover:not(:disabled) {
  background: #3b82f6 !important;
  color: white;
}

.action-btn--analyze.is-loading {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Theory Content List */
.theory-content-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.theory-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 1rem;
}

.theory-loading .dot {
  width: 6px;
  height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.theory-loading .dot:nth-child(1) { animation-delay: -0.32s; }
.theory-loading .dot:nth-child(2) { animation-delay: -0.16s; }

.existing-items {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  max-height: 150px;
  overflow-y: auto;
}

.theory-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s;
}

.theory-item:hover {
  border-color: var(--color-primary);
  background: rgba(99, 102, 241, 0.05);
}

.theory-item.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.theory-item-icon {
  font-size: 1rem;
}

.theory-item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.theory-item-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.theory-item-meta {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.theory-item-audio {
  font-size: 0.875rem;
  opacity: 0.7;
}

.no-content-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  color: var(--color-text-tertiary);
  font-size: 0.8125rem;
  text-align: center;
}

.no-content-hint span {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.no-content-hint p {
  margin: 0;
}

.workflow-badge--empty {
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
}
</style>
