<!--
  GlobalSettingsHeader - Header with Stats and Actions
  Sub-component of GlobalSettingsTab
-->

<template>
  <div class="header-bar">
    <div class="header-left">
      <h2 class="header-title">{{ $t('windows.aiStudioGlobalSettings.title') }}</h2>
      <div class="header-stats">
        <span class="stat-item">{{ stats.total_models || 0 }} {{ $t('windows.aiStudioGlobalSettings.models') }}</span>
        <span class="stat-divider">|</span>
        <span class="stat-item">{{ stats.providers || 0 }} {{ $t('windows.aiStudioGlobalSettings.providers') }}</span>
        <span class="stat-divider">|</span>
        <span class="stat-item">{{ categoriesCount }} {{ $t('windows.aiStudioGlobalSettings.categories') }}</span>
      </div>
    </div>
    <div class="header-actions">
      <button @click="$emit('openPricing')" class="btn-action pricing">
        {{ $t('windows.aiPricing.title') }}
      </button>
      <button @click="$emit('syncAll')" :disabled="isSyncing" class="btn-action">
        <span :class="{ 'animate-spin': isSyncing }">🔄</span>
        {{ isSyncing ? $t('windows.aiStudioGlobalSettings.syncing') : $t('windows.aiStudioGlobalSettings.syncAll') }}
      </button>
      <button @click="$emit('testAll')" :disabled="isTesting" class="btn-action secondary">
        <span :class="{ 'animate-spin': isTesting }">🔌</span>
        {{ isTesting ? $t('windows.aiStudioGlobalSettings.testing') : $t('windows.aiStudioGlobalSettings.testAll') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Stats {
  total_models: number
  active_models: number
  providers: number
  categories: number
}

defineProps<{
  stats: Stats
  categoriesCount: number
  isSyncing: boolean
  isTesting: boolean
}>()

defineEmits<{
  (e: 'openPricing'): void
  (e: 'syncAll'): void
  (e: 'testAll'): void
}>()
</script>

<style scoped>
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.header-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.header-stats {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.stat-divider {
  color: var(--color-border);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.625rem;
  background: var(--color-primary);
  color: white;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  transition: opacity 0.15s;
}

.btn-action:hover:not(:disabled) { opacity: 0.9; }
.btn-action:disabled { opacity: 0.5; }

.btn-action.secondary {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-action.pricing {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border: none;
}

.animate-spin {
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
