<!--
  AI Studio Main - Vollständiges KI-Authoring-System

  Orchestrator für 9 Tabs:
  - 📚 Kurs-Builder: KI-gestützte Kurserstellung
  - 🤖 Tutor: Kapitel/Lektions-Theorie & Erklärungen
  - 🧩 Lernmethoden: 12 Content-LMs (LM00-LM11)
  - 📝 Prüfungen: KI-Prüfungsgenerierung
  - 🎛️ Features: System-Features aktivieren
  - 📄 Prompts: System-Prompts verwalten
  - 📊 Analytics: Kurs-Statistiken & KI-Nutzung
  - ⚙️ Einstellungen: Kurs-spezifische KI-Modelle
  - 🌐 Global: Provider, Profile, API-Keys

  Refactored: 2026-01-09
  Size: 350 LOC (vorher 1270 LOC)
-->

<template>
  <div class="ai-studio-main">
    <!-- Header -->
    <AiStudioHeader
      :courses="courses"
      :selected-course-id="selectedCourseId"
      :stats="stats"
      @select-course="handleSelectCourse"
      @create-course="showNewCourseModal = true"
    />

    <!-- Hidden file input for course-specific uploads -->
    <input
      ref="fileUploadInput"
      type="file"
      class="hidden"
      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md"
      @change="handleFileUpload"
      multiple
    />

    <!-- New Course Modal -->
    <NewCourseModal
      v-if="showNewCourseModal"
      :available-categories="availableCategories"
      :available-profiles="availableProfiles"
      @close="showNewCourseModal = false"
      @create="handleCreateCourse"
      @analyze="handleAnalyzeFiles"
      ref="newCourseModalRef"
    />

    <!-- Main Tabs -->
    <div class="tabs-bar">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="setActiveTab(tab.id)"
        class="tab-button"
        :class="{ active: activeTab === tab.id }"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
        <span v-if="tab.badge" class="tab-badge" :class="tab.badgeColor || 'primary'">
          {{ tab.badge }}
        </span>
        <div v-if="activeTab === tab.id" class="tab-indicator"></div>
      </button>

      <div class="tabs-spacer"></div>

      <!-- Chat Toggle -->
      <button
        @click="toggleChat"
        class="tab-button"
        :class="{ active: chatExpanded }"
      >
        <span class="tab-icon">💬</span>
        <span class="tab-label">{{ $t('aiEditorPro.chat') }}</span>
        <svg
          class="chat-chevron"
          :class="{ open: chatExpanded }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>

    <!-- Main Content Area -->
    <div class="content-area">
      <!-- Sidebar (all tabs except Global) -->
      <template v-if="activeTab !== 'global'">
        <!-- Builder Tab: Session & Verlauf Sidebar -->
        <CourseAuthoringSidebar
          v-if="activeTab === 'builder'"
          :session-meta="kursBuilderRef?.sessionMeta"
          :activity-log="kursBuilderRef?.activityLog || []"
          :stats="kursBuilderRef?.draftStats"
        />

        <!-- Other Tabs: Chapter Tree Sidebar -->
        <CourseStructureSidebar
          v-else
          :course="selectedCourse"
          :chapters="chapters"
          :selected-chapter-id="selectedChapterId"
          :selected-lesson-id="selectedLessonId"
          :expanded-chapters="expandedChapters"
          :is-loading="loading"
          @select-chapter="handleSelectChapter"
          @select-lesson="handleSelectLesson"
          @toggle-chapter="handleToggleChapter"
          @create-chapter="handleCreateChapter"
        />
      </template>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- 📚 Kurs-Builder Tab -->
        <KursBuilderTab
          v-if="activeTab === 'builder'"
          ref="kursBuilderRef"
          :course="selectedCourse"
        />

        <!-- 🤖 Tutor Tab -->
        <TutorTab
          v-if="activeTab === 'tutor'"
          :lesson="selectedLesson"
          :chapter="selectedChapter"
          :course="selectedCourse"
          @back-to-chapter="clearLessonSelection"
        />

        <!-- 🧩 Lernmethoden Tab -->
        <LernmethodenTab
          v-if="activeTab === 'methods'"
          :course="selectedCourse"
          :chapter="selectedChapter"
          :lesson="selectedLesson"
          :chapters="chapters"
        />

        <!-- 📝 Prüfungen Tab -->
        <ExamsTab
          v-if="activeTab === 'exams'"
          :course="selectedCourse"
        />

        <!-- 🎛️ Features Tab -->
        <SystemFeaturesTab
          v-if="activeTab === 'features'"
          :course="selectedCourse"
        />

        <!-- 📄 Prompts Tab -->
        <PromptsTab
          v-if="activeTab === 'prompts'"
          :course="selectedCourse"
        />

        <!-- 📊 Analytics Tab -->
        <AnalyticsTab
          v-if="activeTab === 'analytics'"
          :course="selectedCourse"
        />

        <!-- ⚙️ Einstellungen Tab -->
        <SettingsTab
          v-if="activeTab === 'settings'"
          :course="selectedCourse"
        />

        <!-- 🌐 Globale Einstellungen Tab -->
        <GlobalSettingsTab
          v-if="activeTab === 'global'"
        />

        <!-- Chat Panel (overlays content when expanded) -->
        <ChatPanel
          v-if="chatExpanded"
          :course="selectedCourse"
          @close="closeChat"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AiStudioMain - Main orchestrator for AI Studio
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'

// Components (reuse from views)
import {
  AiStudioHeader,
  CourseSelector as _CourseSelector,
  NewCourseModal,
  CourseStructureSidebar,
  useAiStudioState,
  useCourseManagement,
  useChatManagement,
  useTabManagement,
  type NewCourseData,
  type AIAnalysisResult
} from './views'

// Tab Components
import KursBuilderTab from './tabs/KursBuilderTab.vue'
import TutorTab from './tabs/TutorTab.vue'
import LernmethodenTab from './tabs/LernmethodenTab.vue'
import ExamsTab from './tabs/ExamsTab.vue'
import SystemFeaturesTab from './tabs/SystemFeaturesTab.vue'
import PromptsTab from './tabs/PromptsTab.vue'
import AnalyticsTab from './tabs/AnalyticsTab.vue'
import SettingsTab from './tabs/SettingsTab.vue'
import GlobalSettingsTab from './tabs/GlobalSettingsTab.vue'
import ChatPanel from './tabs/ChatPanel.vue'
import CourseAuthoringSidebar from '../authoring/course-builder/CourseAuthoringSidebar.vue'

const { t } = useI18n()

// =============================================================================
// Props
// =============================================================================

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

// =============================================================================
// Composables
// =============================================================================

const studioState = useAiStudioState()
const courseMgmt = useCourseManagement()
const chatMgmt = useChatManagement()

// KursBuilder ref for tab badges
const kursBuilderRef = ref<InstanceType<typeof KursBuilderTab> | null>(null)
const tabMgmt = useTabManagement(kursBuilderRef)

// =============================================================================
// State - From Composables
// =============================================================================

const selectedCourseId = computed(() => studioState.selectedCourseId.value)
const selectedCourse = computed(() => studioState.selectedCourse.value)
const selectedChapter = computed(() => studioState.selectedChapter.value)
const selectedLesson = computed(() => studioState.selectedLesson.value)
const selectedChapterId = computed(() => studioState.selectedChapterId.value)
const selectedLessonId = computed(() => studioState.selectedLessonId.value)
const chapters = computed(() => studioState.chapters.value)
const expandedChapters = studioState.expandedChapters
const loading = computed(() => studioState.loading.value)

const courses = computed(() => studioState.courses.value)
const availableCategories = computed(() => courseMgmt.availableCategories.value)
const availableProfiles = computed(() => courseMgmt.availableProfiles.value)

const chatExpanded = computed(() => chatMgmt.chatExpanded.value)
const activeTab = computed(() => tabMgmt.activeTab.value)
const tabs = computed(() => tabMgmt.tabs.value)

// =============================================================================
// State - Local UI
// =============================================================================

const showNewCourseModal = ref(false)
const fileUploadInput = ref<HTMLInputElement | null>(null)
const newCourseModalRef = ref<InstanceType<typeof NewCourseModal> | null>(null)

// =============================================================================
// Computed
// =============================================================================

const stats = computed(() => ({
  totalLessons: studioState.totalLessons.value,
  videosGenerated: 0,
  tokensUsed: 0,
  costToday: 0
}))

// =============================================================================
// Methods - Event Handlers
// =============================================================================

async function handleSelectCourse(courseId: string): Promise<void> {
  studioState.selectCourse(courseId)
}

async function handleCreateCourse(data: NewCourseData): Promise<void> {
  try {
    const newCourseId = await courseMgmt.createCourse(data)

    if (newCourseId) {
      // Reload courses
      await studioState.reloadCourses()

      // Select new course
      studioState.selectCourse(newCourseId)

      // Close modal
      showNewCourseModal.value = false
    }
  } catch (error) {
    console.error('Course creation failed:', error)
  }
}

async function handleAnalyzeFiles(files: File[]): Promise<void> {
  try {
    const result: AIAnalysisResult | null = await courseMgmt.analyzeFilesWithAI(files)

    if (result && newCourseModalRef.value) {
      // Update modal with AI suggestions
      newCourseModalRef.value.updateFromAIAnalysis({
        title: result.title,
        description: result.description,
        categoryId: result.suggested_category_id,
        profileKey: result.suggested_profile_key
      })
    }
  } catch (error) {
    console.error('AI analysis failed:', error)
  }
}

function handleSelectChapter(chapterId: string): void {
  studioState.selectChapter(chapterId)
}

function handleSelectLesson(lessonId: string, chapterId: string): void {
  studioState.selectLesson(lessonId, chapterId)
}

function handleToggleChapter(chapterId: string): void {
  studioState.toggleChapterExpanded(chapterId)
}

async function handleCreateChapter(): Promise<void> {
  if (!selectedCourse.value) return

  try {
    await courseMgmt.createChapter(selectedCourse.value.course_id)
    await studioState.reloadChapters()
  } catch (error) {
    console.error('Chapter creation failed:', error)
  }
}

function clearLessonSelection(): void {
  studioState.selectLesson(null)
}

function setActiveTab(tabId: string): void {
  tabMgmt.setActiveTab(tabId)
}

function toggleChat(): void {
  chatMgmt.toggleChat()
}

function closeChat(): void {
  chatMgmt.closeChat()
}

async function handleFileUpload(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  if (!input.files || !selectedCourse.value) return

  const files = Array.from(input.files)
  console.log(`Uploading ${files.length} files to course ${selectedCourse.value.course_id}`)

  // TODO: Implement file upload to course
  input.value = ''
}

// =============================================================================
// Lifecycle
// =============================================================================

onMounted(async () => {
  // Load initial data
  await Promise.all([
    studioState.loadCourses(),
    courseMgmt.loadCategories(),
    courseMgmt.loadProfiles()
  ])

  // Check if opened with courseId
  const courseId = props.window.payload?.courseId
  if (courseId && typeof courseId === 'string') {
    studioState.selectCourse(courseId)
  }
})

// Watch for payload changes (if window re-opened with different course)
watch(() => props.window.payload?.courseId, (newCourseId) => {
  if (newCourseId && typeof newCourseId === 'string' && newCourseId !== selectedCourseId.value) {
    studioState.selectCourse(newCourseId)
  }
})
</script>

<style scoped>
.ai-studio-main {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
  min-height: 600px;
  min-width: 900px;
}

.hidden {
  display: none;
}

/* Tabs Bar */
.tabs-bar {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
  transition: all 0.15s;
}

.tab-button:hover {
  color: var(--color-text-primary);
  background: var(--color-surface);
}

.tab-button.active {
  color: var(--color-primary);
  background: var(--color-bg);
}

.tab-icon {
  font-size: 1.125rem;
}

.tab-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  font-size: 0.625rem;
  font-weight: 700;
}

.tab-badge.primary {
  background: var(--color-primary);
  color: white;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-primary);
}

.tabs-spacer {
  flex: 1;
}

.chat-chevron {
  width: 1rem;
  height: 1rem;
  transition: transform 0.15s;
}

.chat-chevron.open {
  transform: rotate(180deg);
}

/* Content Area */
.content-area {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
}
</style>
