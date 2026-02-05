<!--
  TheoryGenerationSettingsPanel - Settings and quick actions (right panel)

  Handles TTS settings and quick actions like regenerate, copy, print.
  Max 250 lines = focused settings handling.
-->

<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTTS } from '@/application/composables/useTTS'
import type { ChapterTheory } from '../types/theory.types'

interface Props {
  selectedTheory: ChapterTheory | null
}

interface Emits {
  (e: 'regenerate'): void
  (e: 'copy'): void
  (e: 'print'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

// Composables
const tts = useTTS()

// Methods
const handleRegenerate = () => {
  emit('regenerate')
}

const handleCopy = () => {
  if (!props.selectedTheory) return

  const content = [
    `# ${props.selectedTheory.title}`,
    '',
    props.selectedTheory.overview || '',
    '',
    t('course-editor.theory.settings.clipboard.learningGoals'),
    ...(props.selectedTheory.learningGoals || []).map(g => `- ${g}`),
    '',
    t('course-editor.theory.settings.clipboard.concepts'),
    ...(props.selectedTheory.concepts || []).map(c => `### ${c.name}\n${c.description}`),
    '',
    t('course-editor.theory.settings.clipboard.terms'),
    ...(props.selectedTheory.terms || []).map(t => `**${t.term}**: ${t.definition}`)
  ].join('\n')

  navigator.clipboard.writeText(content)
}

const handlePrint = () => {
  window.print()
}

// Lifecycle
onMounted(() => {
  tts.loadModels()
})
</script>

<template>
  <div class="theory-settings-panel">
    <!-- Header -->
    <div class="panel-header">
      <span class="panel-icon">⚙️</span>
      <span class="panel-title">{{ $t('course-editor.theory.settings.title') }}</span>
    </div>

    <!-- Content -->
    <div class="settings-content">
      <!-- TTS Settings Section -->
      <div class="settings-section">
        <h4>{{ $t('course-editor.theory.settings.tts.title') }}</h4>

        <!-- TTS Toggle -->
        <div class="setting-row">
          <label>{{ $t('course-editor.theory.settings.tts.enabled') }}</label>
          <button
            @click="tts.toggleTTS()"
            class="toggle-btn"
            :class="{ active: tts.ttsEnabled.value }"
          >
            {{ tts.ttsEnabled.value ? $t('course-editor.theory.settings.tts.on') : $t('course-editor.theory.settings.tts.off') }}
          </button>
        </div>

        <!-- Voice Select -->
        <div class="setting-row">
          <label>{{ $t('course-editor.theory.settings.tts.voice') }}</label>
          <select v-model="tts.selectedVoice.value" class="setting-select">
            <option v-for="voice in tts.voices.value" :key="voice.id" :value="voice.id">
              {{ voice.name }}
            </option>
          </select>
        </div>

        <!-- Model Select -->
        <div class="setting-row">
          <label>{{ $t('course-editor.theory.settings.tts.model') }}</label>
          <select v-model="tts.selectedModel.value" class="setting-select">
            <option value="browser">{{ $t('course-editor.theory.settings.tts.models.browser') }}</option>
            <option value="tts-1">{{ $t('course-editor.theory.settings.tts.models.tts1') }}</option>
            <option value="tts-1-hd">{{ $t('course-editor.theory.settings.tts.models.tts1hd') }}</option>
          </select>
        </div>
      </div>

      <!-- Quick Actions Section -->
      <div class="settings-section">
        <h4>{{ $t('course-editor.theory.settings.quickActions.title') }}</h4>

        <button
          v-if="selectedTheory"
          @click="handleRegenerate"
          class="quick-action-btn"
        >
          {{ $t('course-editor.theory.settings.quickActions.regenerate') }}
        </button>

        <button
          v-if="selectedTheory"
          @click="handleCopy"
          class="quick-action-btn"
        >
          {{ $t('course-editor.theory.settings.quickActions.copy') }}
        </button>

        <button
          v-if="selectedTheory"
          @click="handlePrint"
          class="quick-action-btn"
        >
          {{ $t('course-editor.theory.settings.quickActions.print') }}
        </button>
      </div>

      <!-- No Selection -->
      <div v-if="!selectedTheory" class="no-selection-message">
        <p>{{ $t('course-editor.theory.settings.noSelection') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.theory-settings-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-weight: 600;
  font-size: 0.875rem;
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.settings-section {
  margin-bottom: 1.5rem;
}

.settings-section h4 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
}

.setting-row label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  flex: 1;
}

.setting-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  background: var(--color-surface);
  max-width: 120px;
}

.setting-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.toggle-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
  min-width: 60px;
  text-align: center;
}

.toggle-btn:hover {
  background: var(--color-border);
}

.toggle-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.quick-action-btn {
  width: 100%;
  padding: 0.625rem;
  margin-bottom: 0.5rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.quick-action-btn:hover {
  background: var(--color-border);
}

.no-selection-message {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}
</style>
