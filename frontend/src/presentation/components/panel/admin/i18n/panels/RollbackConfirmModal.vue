<script setup lang="ts">
/**
 * RollbackConfirmModal Component
 *
 * Confirmation dialog for rolling back an i18n sync operation.
 * Shows sync details, a warning, and a reason input field.
 */

import type { SyncHistorySummary } from '../types/sync.types'

interface Props {
  sync: SyncHistorySummary
}

defineProps<Props>()

const rollbackReason = defineModel<string>('reason', { default: '' })

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <div class="modal-overlay" @click="emit('cancel')">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h3>{{ $t('panel.i18n.confirm_rollback') }}</h3>
      </div>

      <div class="modal-content">
        <p class="warning-text">
          {{ $t('panel.i18n.rollback_warning') }}
        </p>

        <div class="sync-info">
          <div class="info-row">
            <span class="label">{{ $t('panel.i18n.sync_id') }}:</span>
            <code>{{ sync.sync_id }}</code>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('panel.i18n.mode') }}:</span>
            <span>{{ sync.sync_mode }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ $t('panel.i18n.total_changes') }}:</span>
            <span>{{ sync.total_changes }}</span>
          </div>
        </div>

        <div class="reason-input">
          <label for="rollback-reason">{{ $t('panel.i18n.rollback_reason') }}</label>
          <textarea
            id="rollback-reason"
            v-model="rollbackReason"
            :placeholder="$t('panel.i18n.rollback_reason_placeholder')"
            rows="4"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('cancel')">
          {{ $t('panel.i18n.cancel') }}
        </button>
        <button class="btn btn-danger" @click="emit('confirm')">
          {{ $t('panel.i18n.confirm_rollback') }}
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.modal-content {
  padding: 24px;
}

.warning-text {
  margin: 0 0 16px;
  padding: 12px;
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  border-radius: 4px;
  color: #92400e;
  font-size: 14px;
  line-height: 1.5;
}

.sync-info {
  margin-bottom: 20px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 4px;
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: 600;
  color: #374151;
  min-width: 100px;
}

.reason-input {
  margin-bottom: 20px;
}

.reason-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
}

.reason-input textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-family: inherit;
  font-size: 13px;
  resize: vertical;
}

.reason-input textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 12px;
  transition: all 0.3s;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}
</style>
