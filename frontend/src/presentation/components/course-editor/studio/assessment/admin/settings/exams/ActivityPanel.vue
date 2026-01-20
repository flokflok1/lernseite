<!--
  ActivityPanel - KI activity log and generation settings

  Shows current AI activity, history, token usage, and exam settings.
-->

<template>
  <div class="activity-panel">
    <div class="panel-header">
      <span class="panel-icon">📊</span>
      <span class="panel-title">{{ $t('features.aiEditorActivity.title') }}</span>
    </div>

    <!-- Activity Log -->
    <div class="activity-log">
      <!-- Current Activity -->
      <div v-if="currentActivity" class="current-activity">
        <div class="activity-spinner"></div>
        <span>{{ currentActivity }}</span>
      </div>

      <!-- Activity Items -->
      <div
        v-for="(activity, idx) in activityLog"
        :key="idx"
        class="activity-item"
        :class="activity.status"
      >
        <span class="activity-icon">{{ getActivityIcon(activity.status) }}</span>
        <span class="activity-text">{{ activity.message }}</span>
        <span v-if="activity.duration" class="activity-time">{{ activity.duration }}ms</span>
      </div>

      <!-- Empty State -->
      <div v-if="!currentActivity && activityLog.length === 0" class="activity-empty">
        <span class="empty-icon">⏳</span>
        <p>{{ $t('features.aiEditorActivity.noActivity') }}</p>
      </div>
    </div>

    <!-- Token Usage -->
    <div class="token-usage">
      <div class="usage-header">
        <span>{{ $t('features.aiEditorActivity.tokenUsage') }}</span>
        <span class="usage-value">{{ tokensUsed.toLocaleString() }}</span>
      </div>
      <div class="usage-bar">
        <div class="usage-fill" :style="{ width: `${Math.min(tokensUsed / 100, 100)}%` }"></div>
      </div>
      <div class="usage-cost">
        {{ $t('features.aiEditorActivity.estimatedCost', { cost: estimatedCost.toFixed(4) }) }}
      </div>
    </div>

    <!-- Generation Settings -->
    <div class="gen-settings">
      <h4>{{ $t('features.aiEditorActivity.settings') }}</h4>
      <div class="setting-row">
        <label>{{ $t('features.aiEditorActivity.questionCount') }}</label>
        <select :value="questionCount" @change="$emit('update:questionCount', Number(($event.target as HTMLSelectElement).value))">
          <option :value="5">{{ $t('features.aiEditorActivity.questions', { count: 5 }) }}</option>
          <option :value="10">{{ $t('features.aiEditorActivity.questions', { count: 10 }) }}</option>
          <option :value="15">{{ $t('features.aiEditorActivity.questions', { count: 15 }) }}</option>
          <option :value="20">{{ $t('features.aiEditorActivity.questions', { count: 20 }) }}</option>
        </select>
      </div>
      <div class="setting-row">
        <label>{{ $t('features.aiEditorActivity.difficulty') }}</label>
        <select :value="difficulty" @change="$emit('update:difficulty', ($event.target as HTMLSelectElement).value)">
          <option value="easy">{{ $t('features.aiEditorActivity.easy') }}</option>
          <option value="medium">{{ $t('features.aiEditorActivity.medium') }}</option>
          <option value="hard">{{ $t('features.aiEditorActivity.hard') }}</option>
          <option value="mixed">{{ $t('features.aiEditorActivity.mixed') }}</option>
        </select>
      </div>
      <div class="setting-row">
        <label>{{ $t('features.aiEditorActivity.duration') }}</label>
        <input
          type="number"
          :value="durationMinutes"
          @input="$emit('update:durationMinutes', Number(($event.target as HTMLInputElement).value))"
          min="5"
          max="180"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Types
interface ActivityItem {
  message: string
  status: 'pending' | 'success' | 'error'
  duration?: number
}

// Props
const props = defineProps<{
  currentActivity?: string | null
  activityLog: ActivityItem[]
  tokensUsed: number
  questionCount: number
  difficulty: string
  durationMinutes: number
}>()

// Emits
defineEmits<{
  (e: 'update:questionCount', value: number): void
  (e: 'update:difficulty', value: string): void
  (e: 'update:durationMinutes', value: number): void
}>()

// Computed
const estimatedCost = computed(() => {
  // Rough estimate: $0.00001 per token
  return props.tokensUsed * 0.00001
})

// Methods
function getActivityIcon(status: string): string {
  const icons: Record<string, string> = {
    pending: '⏳',
    success: '✅',
    error: '❌'
  }
  return icons[status] || '📝'
}
</script>

<style scoped>
.activity-panel {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-size: 0.875rem;
  font-weight: 600;
}

/* Activity Log */
.activity-log {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  max-height: 200px;
}

.current-activity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-primary-subtle);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.activity-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-primary-subtle);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0;
  font-size: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-item.success {
  color: #22c55e;
}

.activity-item.error {
  color: #ef4444;
}

.activity-icon {
  font-size: 0.75rem;
}

.activity-text {
  flex: 1;
}

.activity-time {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
}

.activity-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  color: var(--color-text-tertiary);
  text-align: center;
}

.activity-empty .empty-icon {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.activity-empty p {
  margin: 0;
  font-size: 0.75rem;
}

/* Token Usage */
.token-usage {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.usage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  margin-bottom: 0.375rem;
}

.usage-value {
  font-weight: 600;
  color: var(--color-primary);
}

.usage-bar {
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.usage-cost {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  margin-top: 0.25rem;
}

/* Generation Settings */
.gen-settings {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.gen-settings h4 {
  margin: 0 0 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.setting-row:last-child {
  margin-bottom: 0;
}

.setting-row label {
  flex: 1;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.setting-row select,
.setting-row input {
  width: 100px;
  padding: 0.375rem 0.5rem;
  font-size: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background: var(--color-bg);
}

.setting-row select:focus,
.setting-row input:focus {
  outline: none;
  border-color: var(--color-primary);
}
</style>
