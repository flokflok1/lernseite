<!--
  ProviderGrid - Provider cards with API key management

  Displays all AI providers in a compact grid with
  status indicators and quick actions.
-->

<template>
  <div class="provider-section">
    <div class="section-header">
      <h3 class="section-title">Provider & API-Keys</h3>
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
          <span class="provider-meta">{{ getModelCount(provider.name) }} Modelle</span>
        </div>
        <div class="provider-status">
          <span class="status-dot" :class="provider.has_api_key ? 'ok' : 'missing'"></span>
        </div>
        <div class="provider-actions">
          <button
            @click="$emit('open-api-key', provider)"
            class="btn-small"
            title="API-Key"
          >
            🔑
          </button>
          <button
            @click="$emit('test', provider)"
            :disabled="testingProvider === provider.name"
            class="btn-small"
            title="Testen"
          >
            <span :class="{ 'animate-spin': testingProvider === provider.name }">🔌</span>
          </button>
          <button
            @click="$emit('sync', provider.name)"
            :disabled="isSyncing"
            class="btn-small"
            title="Sync"
          >
            🔄
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Types
interface Provider {
  provider_id: number
  name: string
  display_name: string
  active: boolean
  has_api_key: boolean
}

// Props
const props = defineProps<{
  providers: Provider[]
  modelCounts: Record<string, number>
  testingProvider?: string | null
  isSyncing?: boolean
}>()

// Emits
defineEmits<{
  (e: 'open-api-key', provider: Provider): void
  (e: 'test', provider: Provider): void
  (e: 'sync', providerName: string): void
}>()

// Methods
function getProviderIcon(provider: string): string {
  const icons: Record<string, string> = {
    openai: '🤖',
    anthropic: '🧠',
    google: '🔍',
    deepl: '🌍'
  }
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
.provider-section {
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.section-header {
  padding: 0.75rem 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.section-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.provider-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
}

.provider-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  transition: all 0.15s;
}

.provider-card:hover {
  border-color: var(--color-primary);
}

.provider-card.configured {
  border-left: 3px solid #22c55e;
}

.provider-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  background: var(--color-bg);
  border-radius: 0.5rem;
}

.provider-icon.provider-openai { background: #e0f2fe; }
.provider-icon.provider-anthropic { background: #fef3c7; }
.provider-icon.provider-google { background: #dcfce7; }
.provider-icon.provider-deepl { background: #e0e7ff; }

.provider-info {
  flex: 1;
  min-width: 0;
}

.provider-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
}

.provider-meta {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.provider-status {
  padding: 0 0.5rem;
}

.status-dot {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.ok {
  background: #22c55e;
}

.status-dot.missing {
  background: #ef4444;
}

.provider-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-small {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-small:hover:not(:disabled) {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.btn-small:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
