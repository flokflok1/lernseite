<template>
  <div class="lm-plugin-management">
    <!-- Header -->
    <div class="header">
      <div>
        <h1 class="title">{{ $t('panel.plugins.title') }}</h1>
        <p class="subtitle">{{ $t('panel.plugins.subtitle') }}</p>
      </div>
      <button
        @click="handleScan"
        :disabled="isLoading"
        class="btn-scan"
      >
        {{ isLoading ? $t('panel.plugins.scanning') : $t('panel.plugins.scanPlugins') }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        :class="{ active: activeTab === 'pending' }"
        @click="activeTab = 'pending'"
        class="tab-btn"
      >
        {{ $t('panel.plugins.pending') }} ({{ pendingCount }})
      </button>
      <button
        :class="{ active: activeTab === 'active' }"
        @click="activeTab = 'active'"
        class="tab-btn"
      >
        {{ $t('panel.plugins.active') }} ({{ activeCount }})
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="hasError" class="error-state">
      <p class="error-message">{{ error }}</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="displayedPlugins.length === 0" class="empty-state">
      <p>{{ activeTab === 'pending' ? $t('panel.plugins.noPendingPlugins') : $t('panel.plugins.noActivePlugins') }}</p>
    </div>

    <!-- Plugin Grid -->
    <div v-else class="plugin-grid">
      <div
        v-for="plugin in displayedPlugins"
        :key="plugin.plugin_id"
        class="plugin-card"
        @click="openDetail(plugin)"
      >
        <div class="plugin-icon">{{ plugin.icon }}</div>
        <div class="plugin-info">
          <h3 class="plugin-name">{{ plugin.name }}</h3>
          <p class="plugin-code">{{ plugin.plugin_code }}</p>
          <div class="plugin-meta">
            <span class="badge badge-group">{{ plugin.group_code }}</span>
            <span class="badge badge-tier">{{ plugin.tier }}</span>
            <span class="badge badge-ki">{{ plugin.ki_usage }}</span>
          </div>
        </div>
        <div class="plugin-actions" @click.stop>
          <button
            v-if="activeTab === 'pending'"
            @click="handleApprove(plugin.plugin_id)"
            class="btn-approve"
          >
            {{ $t('panel.plugins.approve') }}
          </button>
          <button
            v-if="activeTab === 'active'"
            @click="handleDeactivate(plugin.plugin_id)"
            class="btn-deactivate"
          >
            {{ $t('panel.plugins.deactivate') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <LMPluginDetailModal
      v-if="selectedPlugin"
      :plugin="selectedPlugin"
      @close="selectedPlugin = null"
      @approve="handleModalApprove"
      @reject="handleModalReject"
      @activate="handleModalActivate"
      @deactivate="handleModalDeactivate"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLMPlugins } from '@/application/composables/useLMPlugins'
import { useI18n } from 'vue-i18n'
import type { LMPluginMetadata } from '@/types/plugins'
import LMPluginDetailModal from './LMPluginDetailModal.vue'

const { t } = useI18n()
const {
  activePlugins,
  pendingPlugins,
  isLoading,
  error,
  pendingCount,
  activeCount,
  hasError,
  fetchActivePlugins,
  fetchPendingPlugins,
  scanPlugins,
  approvePlugin,
  rejectPlugin,
  activatePlugin,
  deactivatePlugin
} = useLMPlugins()

const activeTab = ref<'pending' | 'active'>('pending')
const selectedPlugin = ref<LMPluginMetadata | null>(null)

const displayedPlugins = computed(() => {
  return activeTab.value === 'pending' ? pendingPlugins.value : activePlugins.value
})

async function handleScan() {
  try {
    const result = await scanPlugins()
    if (result) {
      alert(t('panel.plugins.scanSuccess', { count: result.registered_count }))
    }
  } catch (err) {
    console.error('Scan failed:', err)
    alert(t('panel.plugins.errors.scanFailed'))
  }
}

async function handleApprove(pluginId: string) {
  try {
    await approvePlugin(pluginId)
    alert(t('panel.plugins.approveSuccess'))
  } catch (err) {
    console.error('Approval failed:', err)
    alert(t('panel.plugins.errors.approveFailed'))
  }
}

async function handleDeactivate(pluginId: string) {
  if (!confirm(t('common.confirmAction'))) {
    return
  }

  try {
    await deactivatePlugin(pluginId)
    alert(t('panel.plugins.deactivateSuccess'))
  } catch (err) {
    console.error('Deactivation failed:', err)
    alert(t('panel.plugins.errors.deactivateFailed'))
  }
}

function openDetail(plugin: LMPluginMetadata) {
  selectedPlugin.value = plugin
}

async function handleModalApprove(pluginId: string) {
  try {
    await approvePlugin(pluginId)
    alert(t('panel.plugins.approveSuccess'))
    selectedPlugin.value = null
  } catch (err) {
    console.error('Approval failed:', err)
    alert(t('panel.plugins.errors.approveFailed'))
  }
}

async function handleModalReject(pluginId: string, reason: string) {
  try {
    await rejectPlugin(pluginId, reason)
    alert(t('panel.plugins.rejectSuccess'))
    selectedPlugin.value = null
  } catch (err) {
    console.error('Rejection failed:', err)
    alert(t('panel.plugins.errors.rejectFailed'))
  }
}

async function handleModalActivate(pluginId: string) {
  try {
    await activatePlugin(pluginId)
    alert(t('panel.plugins.activateSuccess'))
    selectedPlugin.value = null
  } catch (err) {
    console.error('Activation failed:', err)
    alert(t('panel.plugins.errors.activateFailed'))
  }
}

async function handleModalDeactivate(pluginId: string) {
  try {
    await deactivatePlugin(pluginId)
    alert(t('panel.plugins.deactivateSuccess'))
    selectedPlugin.value = null
  } catch (err) {
    console.error('Deactivation failed:', err)
    alert(t('panel.plugins.errors.deactivateFailed'))
  }
}

onMounted(async () => {
  await fetchPendingPlugins()
  await fetchActivePlugins()
})
</script>

<style scoped>
.lm-plugin-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: var(--color-text-primary, #1f2937);
}

.subtitle {
  margin: 0;
  color: var(--color-text-secondary, #6b7280);
  font-size: 0.95rem;
}

.btn-scan {
  padding: 0.75rem 1.5rem;
  background: var(--color-primary, #3b82f6);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-scan:hover:not(:disabled) {
  background: var(--color-primary-dark, #2563eb);
  transform: translateY(-1px);
}

.btn-scan:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--color-border, #e5e7eb);
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

.loading, .error-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--color-text-secondary, #6b7280);
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid var(--color-border, #e5e7eb);
  border-top-color: var(--color-primary, #3b82f6);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: var(--color-error, #ef4444);
  font-weight: 500;
}

.plugin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.plugin-card {
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-bg-card, white);
}

.plugin-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--color-primary-light, #93c5fd);
  transform: translateY(-2px);
}

.plugin-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  text-align: center;
}

.plugin-info {
  margin-bottom: 1rem;
}

.plugin-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
}

.plugin-code {
  color: var(--color-text-secondary, #6b7280);
  font-size: 0.875rem;
  font-family: monospace;
  margin: 0 0 0.75rem 0;
}

.plugin-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-group {
  background: var(--color-bg-badge-group, #dbeafe);
  color: var(--color-text-badge-group, #1e40af);
}

.badge-tier {
  background: var(--color-bg-badge-tier, #fef3c7);
  color: var(--color-text-badge-tier, #92400e);
}

.badge-ki {
  background: var(--color-bg-badge-ki, #e0e7ff);
  color: var(--color-text-badge-ki, #3730a3);
}

.plugin-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-approve, .btn-deactivate {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-approve {
  background: var(--color-success, #10b981);
  color: white;
}

.btn-approve:hover {
  background: var(--color-success-dark, #059669);
}

.btn-deactivate {
  background: var(--color-warning, #f59e0b);
  color: white;
}

.btn-deactivate:hover {
  background: var(--color-warning-dark, #d97706);
}
</style>
