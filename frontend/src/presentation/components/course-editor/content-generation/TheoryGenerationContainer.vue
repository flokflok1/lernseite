<!--
  TheoryGenerationContainer - Chapter Theory Management System

  Main orchestrator for theory generation and management.
  Coordinates 3-column layout: list | detail | settings.
  Integrated into course-editor system.
-->

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTheoryGeneration } from './composables/useTheoryGeneration'
import TheoryGenerationListPanel from './panels/TheoryGenerationListPanel.vue'
import TheoryGenerationDetailPanel from './panels/TheoryGenerationDetailPanel.vue'
import TheoryGenerationSettingsPanel from './panels/TheoryGenerationSettingsPanel.vue'
import type { Chapter, Course, TheoryStyle } from './types/theory.types'

interface Props {
  chapter: Chapter | null
  course: Course | null
}

interface Emits {
  (e: 'generated', theoryId: string): void
  (e: 'deleted', theoryId: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

// Composables
const theoryMgmt = useTheoryGeneration()

// Local state
const showCreateForm = ref(false)
const localError = ref<string | null>(null)

// Computed shortcuts
const {
  chapterTheories,
  selectedTheoryId,
  selectedTheory,
  isLoading,
  isGenerating,
  error,
  currentTheoryTitle,
  currentTheoryStyle
} = theoryMgmt

// Combined error (local + from composable)
const displayError = ref('')

// Methods
const loadTheories = async () => {
  if (props.chapter?.chapter_id) {
    await theoryMgmt.loadChapterTheories(props.chapter.chapter_id)
  }
}

const onSelectTheory = async (theoryId: string) => {
  await theoryMgmt.selectTheory(theoryId)
  showCreateForm.value = false
}

const onDeleteTheory = async (theoryId: string) => {
  const success = await theoryMgmt.deleteTheory(theoryId)
  if (success) {
    emit('deleted', theoryId)
  }
}

const handleGenerateTheory = async (style: TheoryStyle, title: string, withAudio: boolean) => {
  if (!props.chapter?.chapter_id) return

  const newTheoryId = await theoryMgmt.generateTheory(
    props.chapter.chapter_id,
    style,
    title,
    withAudio
  )

  if (newTheoryId) {
    showCreateForm.value = false
    await theoryMgmt.selectTheory(newTheoryId)
    emit('generated', newTheoryId)
  }
}

const handleRegenerateTheory = () => {
  if (selectedTheoryId.value) {
    showCreateForm.value = true
  }
}

const clearError = () => {
  displayError.value = ''
  localError.value = null
}

// Watchers
watch(() => props.chapter, async (newChapter) => {
  theoryMgmt.reset()
  showCreateForm.value = false

  if (newChapter?.chapter_id) {
    await loadTheories()
  }
}, { immediate: true })

watch(() => error.value, (newError) => {
  displayError.value = newError || ''
})

// Lifecycle
onMounted(() => {
  loadTheories()
})
</script>

<template>
  <div class="theory-generation-container">
    <!-- Header with Course/Chapter Info -->
    <div class="container-header">
      <div class="header-icon">📚</div>
      <div class="header-info">
        <h2>{{ $t('course-editor.theory.container.title') }}</h2>
        <p v-if="course && chapter">{{ course.title }} • {{ chapter.title }}</p>
      </div>
      <div class="header-stats">
        <div class="stat">
          <span class="stat-value">{{ chapterTheories.length }}</span>
          <span class="stat-label">{{ $t('course-editor.theory.container.available') }}</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ selectedTheoryId ? 1 : 0 }}</span>
          <span class="stat-label">{{ $t('course-editor.theory.container.selected') }}</span>
        </div>
      </div>
    </div>

    <!-- Main 3-Column Layout -->
    <div class="main-layout">
      <!-- Left: Theory List -->
      <TheoryGenerationListPanel
        :theories="chapterTheories"
        :is-loading="isLoading"
        :selected-id="selectedTheoryId"
        @select="onSelectTheory"
        @delete="onDeleteTheory"
        @refresh="loadTheories"
        @create="showCreateForm = true"
      />

      <!-- Middle: Detail/Generator Panel -->
      <TheoryGenerationDetailPanel
        :selected-theory="selectedTheory"
        :is-generating="isGenerating"
        :show-create-form="showCreateForm"
        @generate="handleGenerateTheory"
        @cancel-create="showCreateForm = false"
      />

      <!-- Right: Settings Panel -->
      <TheoryGenerationSettingsPanel
        :selected-theory="selectedTheory"
        @regenerate="handleRegenerateTheory"
        @copy="() => {}"
        @print="() => {}"
      />
    </div>

    <!-- Error Banner -->
    <div v-if="displayError" class="error-banner">
      <span>⚠️ {{ displayError }}</span>
      <button @click="clearError">×</button>
    </div>
  </div>
</template>

<style scoped>
.theory-generation-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
}

/* Header */
.container-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.header-icon {
  font-size: 2rem;
}

.header-info {
  flex: 1;
}

.header-info h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--color-text-primary);
}

.header-info p {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.header-stats {
  display: flex;
  gap: 1.5rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* Main Layout - 3 Columns */
.main-layout {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 0;
  flex: 1;
  min-height: 0;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  font-size: 0.875rem;
}

.error-banner button {
  background: none;
  border: none;
  color: currentColor;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
}

.error-banner button:hover {
  opacity: 0.7;
}
</style>
