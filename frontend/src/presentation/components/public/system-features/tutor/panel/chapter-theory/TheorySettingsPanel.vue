<!--
  TheorySettingsPanel - Right column with TTS settings and quick actions.
-->

<template>
  <div class="settings-panel">
    <div class="panel-header">
      <span class="panel-icon">⚙️</span>
      <span class="panel-title">{{ $t('chapterTheoryView.settings') }}</span>
    </div>

    <div class="settings-content">
      <!-- TTS Settings -->
      <div class="settings-section">
        <h4>{{ $t('chapterTheoryView.tts.title') }}</h4>
        <div class="setting-row">
          <label>{{ $t('chapterTheoryView.tts.enabled') }}</label>
          <button @click="$emit('toggleTts')" class="toggle-btn" :class="{ active: ttsEnabled }">
            {{ ttsEnabled ? $t('chapterTheoryView.tts.on') : $t('chapterTheoryView.tts.off') }}
          </button>
        </div>
        <div class="setting-row">
          <label>{{ $t('chapterTheoryView.tts.voice') }}</label>
          <select
            :value="selectedVoice"
            @change="$emit('update:selectedVoice', ($event.target as HTMLSelectElement).value)"
            class="setting-select"
          >
            <option v-for="voice in voices" :key="voice.id" :value="voice.id">
              {{ voice.name }}
            </option>
          </select>
        </div>
        <div class="setting-row">
          <label>{{ $t('chapterTheoryView.tts.model') }}</label>
          <select
            :value="selectedModel"
            @change="$emit('update:selectedModel', ($event.target as HTMLSelectElement).value)"
            class="setting-select"
          >
            <option value="browser">{{ $t('chapterTheoryView.tts.models.browser') }}</option>
            <option value="tts-1">{{ $t('chapterTheoryView.tts.models.tts1') }}</option>
            <option value="tts-1-hd">{{ $t('chapterTheoryView.tts.models.tts1hd') }}</option>
          </select>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="settings-section">
        <h4>{{ $t('chapterTheoryView.quickActions.title') }}</h4>
        <button v-if="hasSelection" @click="$emit('regenerate')" class="quick-action-btn">
          {{ $t('chapterTheoryView.quickActions.regenerate') }}
        </button>
        <button v-if="hasSelection" @click="$emit('copy')" class="quick-action-btn">
          {{ $t('chapterTheoryView.quickActions.copy') }}
        </button>
        <button v-if="hasSelection" @click="$emit('print')" class="quick-action-btn">
          {{ $t('chapterTheoryView.quickActions.print') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface TTSVoice {
  id: string
  name: string
}

interface Props {
  ttsEnabled: boolean
  selectedVoice: string
  selectedModel: string
  voices: TTSVoice[]
  hasSelection: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'toggleTts'): void
  (e: 'update:selectedVoice', value: string): void
  (e: 'update:selectedModel', value: string): void
  (e: 'regenerate'): void
  (e: 'copy'): void
  (e: 'print'): void
}>()
</script>

<style scoped>
.settings-panel {
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
  color: var(--color-text-primary);
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
  max-width: 140px;
}

.toggle-btn {
  padding: 0.375rem 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
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
</style>
