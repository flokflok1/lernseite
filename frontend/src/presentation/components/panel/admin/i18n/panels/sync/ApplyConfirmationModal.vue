<script setup lang="ts">
/**
 * ApplyConfirmationModal Component
 *
 * Displays confirmation dialog before applying synchronization changes.
 * Shows summary of pending resolutions and conflicts.
 */

import { useI18n } from 'vue-i18n'

interface Props {
  isVisible: boolean
  selectedMode: 'AUTO' | 'MANUAL'
  pendingResolutionsCount: number
  conflictsCount: number
  isApplying?: boolean
}

interface Emits {
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()

function handleConfirm(): void {
  emit('confirm')
}

function handleCancel(): void {
  emit('cancel')
}
</script>

<template>
  <div v-if="isVisible" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        ⚠️ {{ $t('panel.i18n.apply_confirmation') }}
      </div>

      <div class="modal-body">
        {{ $t('panel.i18n.apply_confirmation_desc') }}

        <ul class="confirmation-list">
          <li v-if="selectedMode === 'MANUAL'">
            {{ $t('panel.i18n.mode_manual') }}: {{ pendingResolutionsCount }}
            {{ $t('panel.i18n.pending_resolutions') }}
          </li>
          <li v-if="conflictsCount > 0">
            ⚠️ {{ conflictsCount }} {{ $t('panel.i18n.conflicts') }}
          </li>
        </ul>
      </div>

      <div class="modal-actions">
        <button
          class="btn btn-secondary"
          :disabled="isApplying"
          @click="handleCancel"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          class="btn btn-primary"
          :disabled="isApplying"
          @click="handleConfirm"
        >
          <span v-if="isApplying" class="spinner-small"></span>
          {{ $t('panel.i18n.apply_changes') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%;
  animation: slideUp 0.3s ease;
  display: flex;
  flex-direction: column;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border, #e0e0e0);
  font-weight: 600;
  font-size: 16px;
  color: var(--color-warning, #ff9800);
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-body {
  padding: 20px 24px;
  flex: 1;
  font-size: 14px;
  color: var(--color-text-primary, #333);
  line-height: 1.6;
}

.confirmation-list {
  list-style: none;
  padding: 0;
  margin: 12px 0 0 0;
}

.confirmation-list li {
  padding: 8px 0;
  padding-left: 24px;
  position: relative;
  color: var(--color-text-secondary, #666);
}

.confirmation-list li:before {
  content: '•';
  position: absolute;
  left: 8px;
  color: var(--color-primary, #2196f3);
  font-weight: bold;
}

.confirmation-list li:first-child {
  padding-top: 0;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--color-border, #e0e0e0);
  justify-content: flex-end;
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

.btn-secondary {
  background-color: var(--color-surface, #f5f5f5);
  color: var(--color-text-primary, #333);
  border: 1px solid var(--color-border, #e0e0e0);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-border, #e0e0e0);
  border-color: var(--color-text-secondary, #666);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--color-primary, #2196f3);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark, #1976d2);
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
