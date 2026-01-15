<!--
  ProviderRow - API Key Management per Provider
  Sub-component of ModelsTab
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span
          class="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
          :class="providerStyle"
        >
          {{ providerIcon }}
        </span>
        <div>
          <h4 class="font-medium text-[var(--color-text-primary)]">{{ provider.display_name }}</h4>
          <p class="text-xs text-[var(--color-text-tertiary)]">
            {{ modelCount }} {{ $t('windows.aiEditorModels.models') }}
            <span v-if="provider.last_validated" class="ml-2">
              | {{ $t('windows.aiEditorModels.validated') }}: {{ formatDate(provider.last_validated) }}
            </span>
          </p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <span
          class="w-3 h-3 rounded-full"
          :class="provider.has_api_key ? 'bg-green-500' : 'bg-red-500'"
        ></span>
        <span class="text-sm text-[var(--color-text-secondary)]">
          {{ provider.has_api_key ? $t('windows.aiEditorModels.configured') : $t('windows.aiEditorModels.notConfigured') }}
        </span>
        <span
          v-if="provider.active"
          class="px-2 py-0.5 text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded"
        >
          {{ $t('windows.aiEditorModels.active') }}
        </span>
      </div>
    </div>
    <div class="mt-3 flex gap-2">
      <input
        :value="apiKeyInput"
        @input="$emit('update:apiKeyInput', ($event.target as HTMLInputElement).value)"
        type="password"
        class="flex-1 px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-sm font-mono"
        :placeholder="provider.has_api_key ? '••••••••••••••••' : $t('windows.aiEditorModels.apiKeyPlaceholder')"
      />
      <button
        @click="$emit('toggleVisibility')"
        class="px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-sm hover:bg-[var(--color-surface)] transition-colors"
      >
        {{ isVisible ? '🙈' : '👁️' }}
      </button>
      <button
        @click="$emit('save')"
        :disabled="!apiKeyInput"
        class="px-3 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition-colors disabled:opacity-50"
      >
        💾 {{ $t('windows.aiEditorModels.save') }}
      </button>
      <button
        @click="$emit('test')"
        :disabled="isTesting"
        class="px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-sm hover:bg-[var(--color-surface)] transition-colors"
      >
        <span :class="{ 'animate-spin': isTesting }">
          {{ isTesting ? '⏳' : '🔌' }}
        </span>
        Test
      </button>
      <button
        @click="$emit('sync')"
        :disabled="isSyncing"
        class="px-3 py-2 bg-purple-500 text-white rounded-lg text-sm hover:bg-purple-600 transition-colors disabled:opacity-50"
      >
        🔄 Sync
      </button>
    </div>
    <!-- Test Result -->
    <div v-if="testResult" class="mt-2 text-sm" :class="testResult.success ? 'text-green-600' : 'text-red-600'">
      {{ testResult.message }}
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
  last_validated?: string
}

interface TestResult {
  success: boolean
  message: string
}

const props = defineProps<{
  provider: Provider
  modelCount: number
  apiKeyInput: string
  isVisible: boolean
  isTesting: boolean
  isSyncing: boolean
  testResult?: TestResult
  providerIcon: string
  providerStyle: string
}>()

defineEmits<{
  (e: 'update:apiKeyInput', value: string): void
  (e: 'toggleVisibility'): void
  (e: 'save'): void
  (e: 'test'): void
  (e: 'sync'): void
}>()

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>
