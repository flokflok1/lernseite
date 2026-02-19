<!--
  ChapterTheoryView - Chapter Theory Management Component

  Displays and manages chapter theories (Theorieblaetter).
  Uses useTheoryManagement composable for data loading.

  Split into sub-components:
  - TheoryListPanel: Left column (theory list)
  - TheoryDetailPanel: Middle column (create form / detail view)
  - TheorySettingsPanel: Right column (TTS settings / quick actions)
-->

<template>
  <div class="chapter-theory-view">
    <!-- Header -->
    <div class="view-header">
      <div class="header-icon">📚</div>
      <div class="header-info">
        <h2>{{ $t('chapterTheoryView.title') }}</h2>
        <p>{{ chapter?.title }} • {{ course?.title }}</p>
      </div>
      <div class="header-stats">
        <div class="stat">
          <span class="stat-value">{{ chapterTheories.length }}</span>
          <span class="stat-label">{{ $t('chapterTheoryView.available') }}</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ selectedTheoryId ? 1 : 0 }}</span>
          <span class="stat-label">{{ $t('chapterTheoryView.selected') }}</span>
        </div>
      </div>
    </div>

    <!-- Three-Column Layout -->
    <div class="main-layout">
      <TheoryListPanel
        :theories="chapterTheories"
        :selected-theory-id="selectedTheoryId"
        :is-loading="isLoading"
        :get-style-emoji="getStyleEmoji"
        :format-date="formatDate"
        @select="onSelectTheory"
        @delete="onDeleteTheory"
        @play-audio="playAudio"
        @refresh="loadTheories"
        @create="actions.showCreateForm.value = true"
      />

      <TheoryDetailPanel
        :show-create-form="actions.showCreateForm.value"
        :new-title="actions.newTitle.value"
        :selected-style="actions.selectedStyle.value"
        :generate-with-audio="actions.generateWithAudio.value"
        :is-generating="actions.isGenerating.value"
        :selected-theory="selectedTheory"
        :theory-title="currentTheoryTitle"
        :theory-style="currentTheoryStyle"
        :get-style-emoji="getStyleEmoji"
        :get-style-name="getStyleName"
        @update:new-title="actions.newTitle.value = $event"
        @update:selected-style="actions.selectedStyle.value = $event"
        @update:generate-with-audio="actions.generateWithAudio.value = $event"
        @generate="actions.generateNewTheory"
        @cancel-create="actions.showCreateForm.value = false"
      />

      <TheorySettingsPanel
        :tts-enabled="tts.ttsEnabled.value"
        :selected-voice="tts.selectedVoice.value"
        :selected-model="tts.selectedModel.value"
        :voices="tts.voices.value"
        :has-selection="!!selectedTheory"
        @toggle-tts="tts.toggleTTS()"
        @update:selected-voice="tts.selectedVoice.value = $event"
        @update:selected-model="tts.selectedModel.value = $event"
        @regenerate="actions.regenerateTheory"
        @copy="actions.copyToClipboard"
        @print="actions.printTheory"
      />
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button @click="actions.clearError">x</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTheoryManagement } from '@/application/composables/learning/useTheoryManagement'
import { useTTS } from '@/application/composables/system/useTTS'
import { useChapterTheoryActions } from './useChapterTheoryActions'
import TheoryListPanel from './TheoryListPanel.vue'
import TheoryDetailPanel from './TheoryDetailPanel.vue'
import TheorySettingsPanel from './TheorySettingsPanel.vue'
import type { Course, Chapter } from './chapter-theory.types'

const { t } = useI18n()

// Props & Emits
const props = defineProps<{
  course: Course | null
  chapter: Chapter | null
}>()

const emit = defineEmits<{
  (e: 'generated', theoryId: string): void
  (e: 'deleted', theoryId: string): void
}>()

// Composables
const theoryMgmt = useTheoryManagement()
const tts = useTTS()

const actions = useChapterTheoryActions({
  getChapterId: () => props.chapter?.chapter_id,
  theoryMgmt,
  onGenerated: (theoryId: string) => emit('generated', theoryId)
})

// Delegate composable state
const chapterTheories = computed(() => theoryMgmt.chapterTheories.value)
const isLoading = computed(() => theoryMgmt.isLoading.value)
const selectedTheoryId = computed(() => theoryMgmt.selectedTheoryId.value)
const selectedTheory = computed(() => theoryMgmt.selectedTheory.value)
const currentTheoryTitle = computed(() => theoryMgmt.currentTheoryTitle.value)
const currentTheoryStyle = computed(() => theoryMgmt.currentTheoryStyle.value)
const error = computed(() => actions.localError.value || theoryMgmt.error.value)

// Methods
async function loadTheories(): Promise<void> {
  if (props.chapter?.chapter_id) {
    await theoryMgmt.loadChapterTheories(props.chapter.chapter_id)
  }
}

async function onSelectTheory(theoryId: string): Promise<void> {
  await theoryMgmt.selectTheory(theoryId)
  actions.showCreateForm.value = false
}

async function onDeleteTheory(theoryId: string): Promise<void> {
  if (!confirm(t('chapterTheoryView.confirmDelete'))) return

  const success = await theoryMgmt.deleteTheory(theoryId)
  if (success) {
    emit('deleted', theoryId)
  }
}

function playAudio(url: string): void {
  tts.playAudioUrl(url)
}

const { getStyleEmoji, getStyleName, formatDate } = theoryMgmt

// Watchers & Lifecycle
watch(() => props.chapter, async (newChapter) => {
  theoryMgmt.reset()
  actions.showCreateForm.value = false

  if (newChapter?.chapter_id) {
    await loadTheories()
  }
}, { immediate: true })

onMounted(() => {
  tts.loadModels()
})
</script>

<style scoped>
.chapter-theory-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
}

.view-header {
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
  margin-left: auto;
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

.main-layout {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 1px;
  flex: 1;
  min-height: 0;
  background: var(--color-border);
}

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
}
</style>
