<!--
  ModelsHeader - Header with title and action buttons
  Sub-component of ModelsTab
-->

<template>
  <div class="flex items-center justify-between mb-6">
    <div>
      <h2 class="text-xl font-bold text-[var(--color-text-primary)]">{{ $t('windows.aiStudioModels.title') }}</h2>
      <p class="text-sm text-[var(--color-text-secondary)] mt-1">
        {{ $t('windows.aiStudioModels.subtitle', { models: modelCount, providers: providerCount }) }}
      </p>
    </div>
    <div class="flex gap-2">
      <button
        @click="$emit('sync')"
        :disabled="isSyncing"
        class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2 disabled:opacity-50"
      >
        <span :class="{ 'animate-spin': isSyncing }">🔄</span>
        {{ isSyncing ? $t('windows.aiStudioModels.syncing') : $t('windows.aiStudioModels.syncButton') }}
      </button>
      <button
        @click="$emit('testAll')"
        :disabled="isTesting"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
      >
        <span :class="{ 'animate-spin': isTesting }">🔌</span>
        {{ isTesting ? $t('windows.aiStudioModels.testing') : $t('windows.aiStudioModels.testConnections') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelCount: number
  providerCount: number
  isSyncing: boolean
  isTesting: boolean
}>()

defineEmits<{
  (e: 'sync'): void
  (e: 'testAll'): void
}>()
</script>
