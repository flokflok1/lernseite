<!--
  ProviderGrid - Provider Cards Grid
  Sub-component of GlobalSettingsTab
-->

<template>
  <div class="section provider-section">
    <div class="section-header">
      <h3 class="section-title">{{ $t('windows.aiEditorGlobalSettings.providerApiKeys') }}</h3>
    </div>
    <div class="provider-grid">
      <div
        v-for="provider in providers"
        :key="provider.provider_id"
        class="provider-card"
        :class="{ active: provider.active, configured: provider.has_api_key }"
      >
        <div class="provider-icon" :class="getProviderClass(provider.name)">
          {{ getProviderIcon(provider.name) }}
        </div>
        <div class="provider-info">
          <span class="provider-name">{{ provider.display_name }}</span>
          <span class="provider-meta">{{ getModelCount(provider.name) }} {{ $t('windows.aiEditorGlobalSettings.models') }}</span>
        </div>
        <div class="provider-status">
          <span class="status-dot" :class="provider.has_api_key ? 'ok' : 'missing'"></span>
        </div>
        <div class="provider-actions">
          <button @click="$emit('openApiKey', provider)" class="btn-small" title="API-Key">🔑</button>
          <button @click="$emit('testProvider', provider)" :disabled="testingProvider === provider.name" class="btn-small" title="Testen">
            <span :class="{ 'animate-spin': testingProvider === provider.name }">🔌</span>
          </button>
          <button @click="$emit('syncProvider', provider.name)" :disabled="isSyncing" class="btn-small" title="Sync">🔄</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Provider {
  provider_id: number
  name: string
  display_name: string
  active: boolean
  has_api_key: boolean
}

const props = defineProps<{
  providers: Provider[]
  modelCounts: Record<string, number>
  testingProvider: string | null
  isSyncing: boolean
}>()

defineEmits<{
  (e: 'openApiKey', provider: Provider): void
  (e: 'testProvider', provider: Provider): void
  (e: 'syncProvider', providerName: string): void
}>()

function getProviderIcon(provider: string): string {
  const icons: Record<string, string> = { openai: '🤖', anthropic: '🧠', google: '🔍', deepl: '🌍' }
  return icons[provider?.toLowerCase()] || '⚙️'
}

function getProviderClass(provider: string): string {
  return `provider-${provider?.toLowerCase() || 'default'}`
}

function getModelCount(providerName: string): number {
  return props.modelCounts[providerName] || 0
}
</script>

<style scoped>
.section { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 0.75rem; overflow: hidden; }
.section-header { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.75rem; background: var(--color-surface-secondary); border-bottom: 1px solid var(--color-border); }
.section-title { font-size: 0.8125rem; font-weight: 600; color: var(--color-text-primary); margin: 0; }
.provider-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 0.75rem; }
.provider-card { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; background: var(--color-surface-secondary); border: 1px solid var(--color-border); border-radius: 0.375rem; min-width: 220px; }
.provider-card.configured { border-color: var(--color-primary); }
.provider-icon { width: 2rem; height: 2rem; display: flex; align-items: center; justify-content: center; border-radius: 0.375rem; font-size: 1rem; background: var(--color-surface); }
.provider-openai { background: rgba(16, 163, 127, 0.1); }
.provider-anthropic { background: rgba(249, 115, 22, 0.1); }
.provider-info { flex: 1; display: flex; flex-direction: column; }
.provider-name { font-weight: 500; color: var(--color-text-primary); font-size: 0.8125rem; }
.provider-meta { font-size: 0.6875rem; color: var(--color-text-tertiary); }
.provider-status { padding: 0 0.5rem; }
.status-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; display: block; }
.status-dot.ok { background: #22c55e; }
.status-dot.missing { background: #ef4444; }
.provider-actions { display: flex; gap: 0.25rem; }
.btn-small { padding: 0.375rem; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 0.25rem; font-size: 0.875rem; transition: all 0.15s; }
.btn-small:hover:not(:disabled) { border-color: var(--color-primary); }
.btn-small:disabled { opacity: 0.5; }
.animate-spin { animation: spin 1s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
