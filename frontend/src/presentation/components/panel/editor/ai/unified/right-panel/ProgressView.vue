<!--
  ProgressView — Shown during content generation.
  Displays current task, progress bar, and token count.
-->
<template>
  <div class="progress-view">
    <div class="progress-header">
      <h3>{{ $t('aiEditor.progress.generating') }}</h3>
    </div>
    <div class="progress-content">
      <div class="progress-bar-container">
        <div class="progress-bar-fill" :style="{ width: `${progress?.percent ?? 0}%` }" />
      </div>
      <div class="progress-details">
        <span class="progress-label">{{ progress?.label || '...' }}</span>
        <span class="progress-percent">{{ progress?.percent ?? 0 }}%</span>
      </div>
      <div v-if="progress?.current && progress?.total" class="progress-steps">
        {{ progress.current }} / {{ progress.total }}
      </div>
    </div>
    <div class="progress-animation">
      <div class="pulse-ring" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GenerateProgress } from '../types'

defineProps<{
  progress: GenerateProgress | null
}>()
</script>

<style scoped>
.progress-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
}
.progress-header h3 {
  font-size: 1rem;
  margin: 0 0 1.5rem;
  color: var(--color-text-primary);
}
.progress-content { width: 100%; max-width: 300px; }
.progress-bar-container {
  height: 6px;
  background: var(--color-surface-secondary);
  border-radius: 3px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.5s ease;
  border-radius: 3px;
}
.progress-details {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.8125rem;
}
.progress-label { color: var(--color-text-secondary); }
.progress-percent { color: var(--color-primary); font-weight: 600; }
.progress-steps {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-top: 0.25rem;
}
.progress-animation { margin-top: 2rem; }
.pulse-ring {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid var(--color-primary);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.5; }
  100% { transform: scale(0.8); opacity: 1; }
}
</style>
