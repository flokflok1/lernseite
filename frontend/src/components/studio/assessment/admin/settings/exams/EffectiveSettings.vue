<!--
  EffectiveSettings - Effective Settings Display
  Sub-component of SettingsTab
-->

<template>
  <div class="settings-card lg:col-span-2">
    <div class="card-header">
      <span class="card-icon">✅</span>
      <span class="card-title">{{ $t('windows.aiEditorSettings.effectiveSettings') }}</span>
      <span v-if="profileName" class="profile-badge">
        {{ $t('windows.aiEditorSettings.profile') }}: {{ profileName }}
      </span>
    </div>
    <div class="effective-grid">
      <div class="effective-item">
        <span class="effective-label">💬 Chat</span>
        <span class="effective-value">{{ effective?.chat_model_id || 'gpt-4o-mini' }}</span>
      </div>
      <div class="effective-item">
        <span class="effective-label">🧠 Reasoning</span>
        <span class="effective-value">{{ effective?.reasoning_model_id || 'gpt-4o' }}</span>
      </div>
      <div class="effective-item">
        <span class="effective-label">🖼️ Image</span>
        <span class="effective-value">{{ effective?.image_model_id || 'dall-e-3' }}</span>
      </div>
      <div class="effective-item">
        <span class="effective-label">🔊 Audio</span>
        <span class="effective-value">{{ effective?.audio_model_id || 'tts-1' }}</span>
      </div>
      <div class="effective-item">
        <span class="effective-label">⚡ Realtime</span>
        <span class="effective-value">{{ effective?.realtime_model_id || 'gpt-4o-realtime' }}</span>
      </div>
      <div class="effective-item">
        <span class="effective-label">🔗 Embedding</span>
        <span class="effective-value">{{ effective?.embedding_model_id || 'text-embedding-3-small' }}</span>
      </div>
    </div>
    <div class="card-footer text-xs text-[var(--color-text-tertiary)]">
      {{ $t('windows.aiEditorSettings.fallbackChain') }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface EffectiveSettings {
  chat_model_id?: string
  reasoning_model_id?: string
  image_model_id?: string
  audio_model_id?: string
  realtime_model_id?: string
  embedding_model_id?: string
}

defineProps<{
  effective?: EffectiveSettings | null
  profileName?: string
}>()
</script>

<style scoped>
.settings-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.card-icon { font-size: 1.25rem; }

.card-title {
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.profile-badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.effective-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.5rem;
  padding: 1rem;
}

@media (max-width: 1200px) {
  .effective-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .effective-grid { grid-template-columns: repeat(2, 1fr); }
}

.effective-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  text-align: center;
}

.effective-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.effective-value {
  font-family: ui-monospace, monospace;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-primary);
  word-break: break-all;
}
</style>
