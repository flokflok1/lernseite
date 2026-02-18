<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-left">
          <div class="plugin-icon-large">{{ plugin.icon }}</div>
          <div>
            <h2 class="modal-title">{{ plugin.name }}</h2>
            <p class="modal-subtitle">{{ plugin.plugin_code }}</p>
          </div>
        </div>
        <button @click="$emit('close')" class="close-btn" :title="$t('common.close')">
          &#x2715;
        </button>
      </div>

      <!-- Status Badge -->
      <div class="status-bar">
        <span class="status-badge" :class="`status-${plugin.approval_status}`">
          {{ $t(`panel.plugins.${plugin.approval_status}`) }}
        </span>
        <span v-if="plugin.is_active" class="active-badge">
          {{ $t('panel.plugins.active') }}
        </span>
      </div>

      <!-- Tabs -->
      <div class="modal-tabs">
        <button
          :class="{ active: activeTab === 'info' }"
          @click="activeTab = 'info'"
          class="tab-btn"
        >
          {{ $t('panel.plugins.info') }}
        </button>
        <button
          :class="{ active: activeTab === 'schema' }"
          @click="activeTab = 'schema'"
          class="tab-btn"
        >
          {{ $t('panel.plugins.schema') }}
        </button>
        <button
          :class="{ active: activeTab === 'preview' }"
          @click="activeTab = 'preview'"
          class="tab-btn"
        >
          {{ $t('panel.plugins.preview') }}
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <PluginInfoTab
          v-if="activeTab === 'info'"
          :plugin="plugin"
          :format-date="formatDate"
        />
        <PluginSchemaTab
          v-else-if="activeTab === 'schema'"
          :plugin="plugin"
        />
        <PluginPreviewTab
          v-else-if="activeTab === 'preview'"
        />
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <template v-if="plugin.approval_status === 'pending_review'">
          <button @click="handleReject" class="btn-reject" :disabled="isProcessing">
            {{ isProcessing ? $t('panel.plugins.rejecting') : $t('panel.plugins.reject') }}
          </button>
          <button @click="handleApprove" class="btn-approve" :disabled="isProcessing">
            {{ isProcessing ? $t('panel.plugins.approving') : $t('panel.plugins.approve') }}
          </button>
        </template>

        <template v-else-if="plugin.approval_status === 'approved' && !plugin.is_active">
          <button @click="handleActivate" class="btn-activate" :disabled="isProcessing">
            {{ isProcessing ? $t('panel.plugins.activating') : $t('panel.plugins.activate') }}
          </button>
        </template>

        <template v-else-if="plugin.is_active">
          <button @click="handleDeactivate" class="btn-deactivate" :disabled="isProcessing">
            {{ isProcessing ? $t('panel.plugins.deactivating') : $t('panel.plugins.deactivate') }}
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { LMPluginMetadata } from '@/types/plugins'
import { usePluginActions } from './composables/usePluginActions'
import PluginInfoTab from './PluginInfoTab.vue'
import PluginSchemaTab from './PluginSchemaTab.vue'
import PluginPreviewTab from './PluginPreviewTab.vue'

interface Props {
  plugin: LMPluginMetadata
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  approve: [pluginId: string]
  reject: [pluginId: string, reason: string]
  activate: [pluginId: string]
  deactivate: [pluginId: string]
}>()

const activeTab = ref<'info' | 'schema' | 'preview'>('info')

const {
  isProcessing,
  handleApprove,
  handleReject,
  handleActivate,
  handleDeactivate,
  formatDate,
} = usePluginActions(() => props.plugin, emit)
</script>

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
  padding: 2rem;
}

.modal-content {
  background: var(--color-bg-card, white);
  border-radius: 1rem;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.header-left {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.plugin-icon-large {
  font-size: 3rem;
  width: 4rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-secondary, #f3f4f6);
  border-radius: 0.75rem;
}

.modal-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary, #1f2937);
}

.modal-subtitle {
  margin: 0.25rem 0 0 0;
  color: var(--color-text-secondary, #6b7280);
  font-size: 0.875rem;
  font-family: monospace;
}

.close-btn {
  border: none;
  background: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-secondary, #6b7280);
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--color-bg-secondary, #f3f4f6);
  color: var(--color-text-primary, #1f2937);
}

.status-bar {
  display: flex;
  gap: 0.5rem;
  padding: 0 1.5rem;
  margin-top: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending_review {
  background: #fef3c7;
  color: #92400e;
}

.status-approved {
  background: #d1fae5;
  color: #065f46;
}

.status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

.active-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #10b981;
  color: white;
}

.modal-tabs {
  display: flex;
  gap: 0;
  padding: 0 1.5rem;
  border-bottom: 2px solid var(--color-border, #e5e7eb);
  margin-top: 1rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab-btn.active {
  color: var(--color-primary, #3b82f6);
  border-bottom-color: var(--color-primary, #3b82f6);
}

.tab-btn:hover {
  color: var(--color-primary, #3b82f6);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-approve,
.btn-reject,
.btn-activate,
.btn-deactivate {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.btn-approve,
.btn-activate {
  background: var(--color-success, #10b981);
  color: white;
}

.btn-approve:hover:not(:disabled),
.btn-activate:hover:not(:disabled) {
  background: var(--color-success-dark, #059669);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.4);
}

.btn-reject {
  background: var(--color-error, #ef4444);
  color: white;
}

.btn-reject:hover:not(:disabled) {
  background: var(--color-error-dark, #dc2626);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.4);
}

.btn-deactivate {
  background: var(--color-warning, #f59e0b);
  color: white;
}

.btn-deactivate:hover:not(:disabled) {
  background: var(--color-warning-dark, #d97706);
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.4);
}

.btn-approve:disabled,
.btn-reject:disabled,
.btn-activate:disabled,
.btn-deactivate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: var(--color-bg-secondary, #f3f4f6);
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: var(--color-border, #d1d5db);
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary, #9ca3af);
}
</style>
