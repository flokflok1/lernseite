<script setup lang="ts">
/**
 * ComparisonStatusBar Component
 *
 * Displays comparison statistics and provides apply/confirm action
 * Shows pending resolutions count and conflicts
 */

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  pendingResolutionsCount: number
  conflictsCount: number
  canApply: boolean
  isApplying: boolean
  applyError?: string | null
}

interface Emits {
  (e: 'apply-requested'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()

const hasError = computed(() => !!props.applyError)
</script>

<template>
  <div class="status-bar-container">
    <!-- Error Alert -->
    <div v-if="hasError" class="alert alert-error">
      <span class="alert-icon">⚠️</span>
      <span class="alert-message">{{ applyError }}</span>
    </div>

    <!-- Status Bar -->
    <div class="status-bar">
      <div class="status-left">
        <span class="status-info">
          <strong>{{ pendingResolutionsCount }}</strong>
          {{ $t('panel.i18n.pending_resolutions') }}
        </span>
        <span class="status-separator">•</span>
        <span class="status-info warning">
          <strong>{{ conflictsCount }}</strong>
          {{ $t('panel.i18n.conflicts') }}
        </span>
      </div>

      <button
        class="btn btn-primary"
        :disabled="!canApply || isApplying"
        @click="emit('apply-requested')"
      >
        <span v-if="isApplying" class="spinner-small"></span>
        {{ $t('panel.i18n.apply_changes') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.status-bar-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--color-surface, #f5f5f5);
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: 6px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-primary, #333);
}

.status-info.warning {
  color: var(--color-warning, #ff9800);
}

.status-separator {
  color: var(--color-border, #e0e0e0);
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.alert-error {
  background-color: var(--color-error-bg, #ffebee);
  border: 1px solid var(--color-error, #dc2626);
  color: var(--color-error, #dc2626);
}

.alert-icon {
  flex-shrink: 0;
  font-size: 16px;
}

.alert-message {
  flex: 1;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background-color: var(--color-primary, #2196f3);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark, #1976d2);
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner-small {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
