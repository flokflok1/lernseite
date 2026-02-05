<!--
  ExplanationSettingsPanel - Settings and quick actions

  Right panel with TTS settings, playback controls, and quick action buttons
  for regenerating, downloading, or sharing explanations.
-->

<script setup lang="ts">
// Vue imports removed - not needed in this component
import { useI18n } from 'vue-i18n'
import type { LessonExplanation } from '../types/explanation.types'

const { t } = useI18n()

interface Props {
  explanation: LessonExplanation | null
  autoPlay: boolean
  playbackSpeed: string
}

interface Emits {
  (e: 'update:autoPlay', value: boolean): void
  (e: 'update:playbackSpeed', value: string): void
  (e: 'regenerate'): void
  (e: 'download-pdf'): void
  (e: 'share'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

// Methods
const handleAutoPlayChange = (value: boolean) => {
  emit('update:autoPlay', value)
}

const handlePlaybackSpeedChange = (value: string) => {
  emit('update:playbackSpeed', value)
}

const handleRegenerate = () => {
  emit('regenerate')
}

const handleDownloadPDF = () => {
  emit('download-pdf')
}

const handleShare = () => {
  emit('share')
}
</script>

<template>
  <div class="explanation-settings-panel">
    <div v-if="explanation" class="settings-content">
      <!-- Playback Settings -->
      <section class="settings-section">
        <h4 class="section-title">⏯️ {{ $t('course-editor.explanation.settings.playback') }}</h4>

        <!-- Auto-play -->
        <div class="setting-item checkbox">
          <input
            id="auto-play"
            type="checkbox"
            :checked="autoPlay"
            @change="e => handleAutoPlayChange((e.target as HTMLInputElement).checked)"
          />
          <label for="auto-play">
            {{ $t('course-editor.explanation.settings.autoPlay') }}
          </label>
        </div>

        <!-- Playback Speed -->
        <div class="setting-item">
          <label for="playback-speed">
            {{ $t('course-editor.explanation.settings.speed') }}
          </label>
          <select
            id="playback-speed"
            :value="playbackSpeed"
            @change="e => handlePlaybackSpeedChange((e.target as HTMLSelectElement).value)"
            class="speed-select"
          >
            <option value="0.75">0.75x</option>
            <option value="1">1x</option>
            <option value="1.25">1.25x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2x</option>
          </select>
        </div>
      </section>

      <!-- Quick Actions -->
      <section class="settings-section">
        <h4 class="section-title">⚡ {{ $t('course-editor.explanation.settings.actions') }}</h4>

        <div class="actions-grid">
          <button class="action-btn" @click="handleRegenerate">
            🔄
            <span>{{ $t('course-editor.explanation.settings.regenerate') }}</span>
          </button>

          <button class="action-btn" @click="handleDownloadPDF">
            📥
            <span>{{ $t('course-editor.explanation.settings.downloadPdf') }}</span>
          </button>

          <button class="action-btn" @click="handleShare">
            🔗
            <span>{{ $t('course-editor.explanation.settings.share') }}</span>
          </button>
        </div>
      </section>

      <!-- Explanation Info -->
      <section class="settings-section">
        <h4 class="section-title">ℹ️ {{ $t('course-editor.explanation.settings.info') }}</h4>

        <div class="info-item">
          <span class="info-label">{{ $t('common.style') }}:</span>
          <span class="info-value">{{ explanation.style }}</span>
        </div>

        <div class="info-item">
          <span class="info-label">{{ $t('course-editor.explanation.list.steps') }}:</span>
          <span class="info-value">{{ explanation.steps.length }}</span>
        </div>

        <div class="info-item">
          <span class="info-label">{{ $t('common.created') }}:</span>
          <span class="info-value">{{ new Date(explanation.createdAt).toLocaleDateString() }}</span>
        </div>

        <div v-if="explanation.updatedAt" class="info-item">
          <span class="info-label">{{ $t('common.updated') }}:</span>
          <span class="info-value">{{ new Date(explanation.updatedAt).toLocaleDateString() }}</span>
        </div>
      </section>
    </div>

    <div v-else class="empty-state">
      <p>{{ $t('course-editor.explanation.settings.empty') }}</p>
    </div>
  </div>
</template>

<style scoped>
.explanation-settings-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-left: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
  overflow-y: auto;
}

.settings-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Settings Section */
.settings-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-primary);
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

/* Setting Items */
.setting-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.setting-item label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.setting-item.checkbox {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.setting-item.checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.setting-item.checkbox label {
  margin: 0;
  cursor: pointer;
  user-select: none;
}

.speed-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.speed-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

/* Actions Grid */
.actions-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.action-btn span {
  flex: 1;
}

/* Info Section */
.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 0.875rem;
  color: var(--color-text-primary);
  padding: 0.375rem;
  background: var(--color-surface);
  border-radius: 3px;
  word-break: break-word;
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 1rem;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}
</style>
