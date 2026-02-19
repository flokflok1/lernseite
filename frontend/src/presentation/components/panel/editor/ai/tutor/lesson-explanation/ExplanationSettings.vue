<!--
  ExplanationSettings - Settings panel for lesson explanations
-->

<template>
  <div class="explanation-settings">
    <div class="panel-header">
      <span class="panel-icon">⚙️</span>
      <span class="panel-title">{{ $t('lessonExplanationView.settings') }}</span>
    </div>

    <div class="settings-content">
      <!-- TTS Settings -->
      <div class="settings-section">
        <h4>{{ $t('lessonExplanationView.tts.title') }}</h4>

        <div class="setting-row">
          <label>{{ $t('lessonExplanationView.tts.autoPlay') }}</label>
          <button
            @click="$emit('update:autoPlay', !autoPlay)"
            class="toggle-btn"
            :class="{ active: autoPlay }"
          >
            {{
              autoPlay
                ? $t('lessonExplanationView.tts.on')
                : $t('lessonExplanationView.tts.off')
            }}
          </button>
        </div>

        <div class="setting-row">
          <label>{{ $t('lessonExplanationView.tts.speed') }}</label>
          <select
            :value="playbackSpeed"
            @input="$emit('update:playbackSpeed', ($event.target as HTMLSelectElement).value)"
            class="setting-select"
          >
            <option value="0.75">{{ $t('lessonExplanationView.tts.speedSlow') }}</option>
            <option value="1">{{ $t('lessonExplanationView.tts.speedNormal') }}</option>
            <option value="1.25">{{ $t('lessonExplanationView.tts.speedFast') }}</option>
          </select>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="settings-section">
        <h4>{{ $t('lessonExplanationView.quickActions.title') }}</h4>

        <button
          v-if="hasExplanation"
          @click="$emit('regenerate')"
          class="quick-action-btn"
        >
          {{ $t('lessonExplanationView.quickActions.regenerate') }}
        </button>

        <button
          v-if="hasExplanation"
          @click="$emit('download-pdf')"
          class="quick-action-btn"
        >
          {{ $t('lessonExplanationView.quickActions.pdf') }}
        </button>

        <button
          v-if="hasExplanation"
          @click="$emit('share')"
          class="quick-action-btn"
        >
          {{ $t('lessonExplanationView.quickActions.share') }}
        </button>
      </div>

      <!-- Info -->
      <div v-if="explanation" class="settings-section">
        <h4>{{ $t('lessonExplanationView.info.title') }}</h4>

        <div class="info-item">
          <span class="info-label">{{ $t('lessonExplanationView.info.created') }}</span>
          <span class="info-value">{{ formatDate(explanation.createdAt) }}</span>
        </div>

        <div class="info-item">
          <span class="info-label">{{ $t('lessonExplanationView.info.steps') }}</span>
          <span class="info-value">{{ stepsCount }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ExplanationSettings - Settings panel for explanations
 */
import type { LessonExplanation } from '@/application/composables/learning/useTheoryManagement'

// Props
interface Props {
  autoPlay: boolean
  playbackSpeed: string
  explanation: LessonExplanation | null
  stepsCount: number
}

defineProps<Props>()

// Emits
defineEmits<{
  (e: 'update:autoPlay', value: boolean): void
  (e: 'update:playbackSpeed', value: string): void
  (e: 'regenerate'): void
  (e: 'download-pdf'): void
  (e: 'share'): void
}>()

// Computed
const hasExplanation = computed(() => props.explanation !== null)

// Methods
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit'
    })
  } catch {
    return dateStr
  }
}
</script>

<script lang="ts">
import { computed } from 'vue'
</script>

<style scoped>
.explanation-settings {
  background: var(--color-surface);
  display: flex;
  flex-direction: column;
  min-height: 0;
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
  flex: 1;
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
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.setting-row label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.setting-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  background: var(--color-surface);
}

.toggle-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  font-size: 0.8125rem;
  cursor: pointer;
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
}

.quick-action-btn:hover {
  background: var(--color-border);
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.8125rem;
}

.info-label {
  color: var(--color-text-tertiary);
}
</style>
