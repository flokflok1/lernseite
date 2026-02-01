<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/desktop'

// Composables
import { useChapterData } from './composables/useChapterData'
import { useLessonManagement } from './composables/useLessonManagement'
import { useLearningMethodStats } from './composables/useLearningMethodStats'
import { useVideoManagement } from './composables/useVideoManagement'

// Components
import { InfoTab, TheoryTab, VideosTab, MethodsTab, LessonsTab } from './tabs'

// Types
import type { AdminLesson } from '@/application/services/api/admin'

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

const { t } = useI18n()

// Initialize composables
const chapter = useChapterData(props.panel)
const lessons = useLessonManagement(
  props.panel.payload?.courseId,
  props.panel.payload?.chapterId,
  !props.panel.payload?.chapterId
)
const methods = useLearningMethodStats()
const videos = useVideoManagement()

// Local state
const activeTab = ref<'info' | 'theory' | 'videos' | 'methods' | 'lessons'>('info')
const isGenerating = ref(false)
const theoryContent = ref('')

// Lifecycle
onMounted(async () => {
  await chapter.loadChapter()

  if (!chapter.isNewChapter.value) {
    await lessons.loadLessons()
    await methods.loadLearningMethodsStats(
      chapter.chapterId.value,
      chapter.isNewChapter.value
    )
  }
})

// Watch for chapter creation - load related data
watch(() => chapter.chapter.value?.chapter_id, async (chapterId) => {
  if (chapterId) {
    await lessons.loadLessons()
    await methods.loadLearningMethodsStats(chapterId, false)
  }
})

// Handle AI generation
const handleGenerateTheory = async () => {
  isGenerating.value = true
  try {
    // AI generation logic would go here
    // For now, this is a placeholder
    theoryContent.value = t('features.chapterEditor.messages.generationStarted')

    // Simulate generation delay
    await new Promise(resolve => setTimeout(resolve, 2000))

    isGenerating.value = false
  } catch (error) {
    isGenerating.value = false
    console.error('Generation failed:', error)
  }
}

// Handle chapter save
const handleSaveChapter = async () => {
  await chapter.saveChapter()
}

// Handle form updates
const handleFormUpdate = (newForm: any) => {
  chapter.form.value = newForm
  chapter.debouncedSave()
}

// Lesson handlers
const handleAddLesson = () => {
  lessons.addLesson()
}

const handleEditLesson = (lesson: AdminLesson) => {
  lessons.editLesson(lesson)
}

const handleDeleteLesson = async (lessonId: string) => {
  await lessons.deleteLesson(lessonId)
}

const handleDragStart = (index: number) => {
  lessons.handleDragStart(index)
}

const handleDragOver = (index: number) => {
  lessons.handleDragOver(index)
}

const handleDrop = async (targetIndex: number) => {
  await lessons.handleDrop(targetIndex)
}

const handleDragEnd = () => {
  lessons.handleDragEnd()
}

// Video handlers
const handleAddVideo = () => {
  videos.addVideo()
}

const handleRemoveVideo = (index: number) => {
  videos.removeVideo(index)
}

const handleUpdateVideo = (index: number, video: any) => {
  videos.updateVideo(index, video)
}

// Methods handlers
const handleOpenMethodsEditor = (group: string) => {
  methods.openLearningMethodsEditor(
    chapter.courseId.value,
    chapter.chapterId.value,
    chapter.chapter.value?.title || '',
    chapter.isNewChapter.value,
    group
  )
}
</script>

<template>
  <div class="chapter-editor-main">
    <!-- Loading State -->
    <div v-if="chapter.loading.value" class="loading-overlay">
      <div class="loading-spinner">⏳ {{ $t('common.loading') }}</div>
    </div>

    <!-- Error State -->
    <div v-if="chapter.error.value" class="error-banner">
      {{ chapter.error.value }}
    </div>

    <!-- Main Editor -->
    <div v-else class="editor-container">
      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button
          v-for="tab in ['info', 'theory', 'videos', 'methods', 'lessons']"
          :key="tab"
          :class="['tab-button', { active: activeTab === tab }]"
          @click="activeTab = tab as any"
        >
          <span class="tab-icon">
            {{ tab === 'info' ? '📋' : tab === 'theory' ? '📚' : tab === 'videos' ? '🎥' : tab === 'methods' ? '🎯' : '📝' }}
          </span>
          {{ $t(`features.chapterEditor.tabs.${tab}`) }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Info Tab -->
        <InfoTab
          v-show="activeTab === 'info'"
          :form="chapter.form.value"
          :is-new-chapter="chapter.isNewChapter.value"
          :is-generating="isGenerating"
          :save-status="chapter.saveStatus.value"
          :error="chapter.error.value"
          @update:form="handleFormUpdate"
          @generate-theory="handleGenerateTheory"
          @save-chapter="handleSaveChapter"
        />

        <!-- Theory Tab -->
        <TheoryTab
          v-show="activeTab === 'theory'"
          :content="theoryContent"
          :is-loading="isGenerating"
          @update:content="theoryContent = $event"
        />

        <!-- Videos Tab -->
        <VideosTab
          v-show="activeTab === 'videos'"
          :videos="videos.videos.value"
          :is-loading="false"
          @add-video="handleAddVideo"
          @remove-video="handleRemoveVideo"
          @update-video="handleUpdateVideo"
        />

        <!-- Methods Tab -->
        <MethodsTab
          v-show="activeTab === 'methods'"
          :method-stats="methods.methodStats.value"
          :is-loading="methods.loadingMethods.value"
          @open-editor="handleOpenMethodsEditor"
        />

        <!-- Lessons Tab -->
        <LessonsTab
          v-show="activeTab === 'lessons'"
          :lessons="lessons.sortedLessons.value"
          :drag-state="lessons.dragState.value"
          :is-loading="lessons.loadingLessons.value"
          @add-lesson="handleAddLesson"
          @edit-lesson="handleEditLesson"
          @delete-lesson="handleDeleteLesson"
          @drag-start="handleDragStart"
          @drag-over="handleDragOver"
          @drop="handleDrop"
          @drag-end="handleDragEnd"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.chapter-editor-main {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
  position: relative;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.loading-spinner {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.error-banner {
  padding: 1rem;
  background-color: var(--color-error-bg);
  color: var(--color-error-text);
  border-bottom: 1px solid var(--color-error);
  font-size: 0.95rem;
}

.editor-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.tab-navigation {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
  overflow-x: auto;
  flex-shrink: 0;
}

.tab-button {
  padding: 0.75rem 1.25rem;
  background-color: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tab-button:hover {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.tab-button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  background-color: white;
}

.tab-icon {
  font-size: 1.1rem;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Scrollbar styling */
.tab-content::-webkit-scrollbar {
  width: 8px;
}

.tab-content::-webkit-scrollbar-track {
  background-color: var(--color-bg-secondary);
}

.tab-content::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 4px;
}

.tab-content::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-text-secondary);
}
</style>
