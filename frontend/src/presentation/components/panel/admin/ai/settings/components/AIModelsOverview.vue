<!--
  Compact models overview bar with provider badges, sync and model selector buttons.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
    <div class="px-4 py-3 flex items-center gap-3">
      <!-- Title + Count -->
      <div class="min-w-0">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ $t('panel.aiSettingsPage.availableModels.title') }}
        </h3>
        <p class="text-xs text-[var(--color-text-secondary)]">
          {{ $t('panel.aiSettingsPage.availableModels.modelsFromProviders', { count: totalModelCount, providers: providerCount }) }}
        </p>
      </div>

      <!-- Provider Badges -->
      <div class="flex gap-1.5 flex-wrap flex-1">
        <span
          v-for="(providerData, providerName) in availableModels"
          :key="providerName"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[var(--color-bg)] border border-[var(--color-border)]"
        >
          <span>{{ getProviderIcon(providerName as string) }}</span>
          <span class="text-[var(--color-text-secondary)] font-medium">{{ providerData.models.length }}</span>
        </span>
      </div>

      <!-- Buttons -->
      <div class="flex items-center gap-1.5 shrink-0">
        <button
          class="px-3 py-1.5 text-sm bg-[var(--color-bg)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-hover)] transition-colors flex items-center gap-1.5 disabled:opacity-50"
          :disabled="isSyncing"
          @click="$emit('sync')"
        >
          <span :class="{ 'animate-spin': isSyncing }">&#x1F504;</span>
          <span>{{ isSyncing ? $t('panel.aiSettingsPage.sync.syncing') : $t('panel.aiSettingsPage.sync.syncButton') }}</span>
        </button>
        <button
          class="px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors flex items-center gap-1.5"
          @click="$emit('openModelSelector')"
        >
          <span>&#x1F50D;</span>
          <span>{{ $t('panel.aiSettingsPage.availableModels.modelSelector') }}</span>
        </button>
      </div>
    </div>

    <!-- Sync Result Banner -->
    <div
      v-if="syncResult"
      class="px-4 py-2 border-t border-[var(--color-border)] text-xs flex items-center gap-2"
      :class="syncResult.success ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400' : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'"
    >
      <span>{{ syncResult.success ? '&#x2705;' : '&#x26A0;' }}</span>
      <span>{{ syncResult.message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProviderModels } from '../types'

interface Props {
  availableModels: Record<string, ProviderModels>
  totalModelCount: number
  providerCount: number
  getProviderIcon: (name: string) => string
  isSyncing?: boolean
  syncResult?: { success: boolean; message: string } | null
}

withDefaults(defineProps<Props>(), {
  isSyncing: false,
  syncResult: null,
})

defineEmits<{
  openModelSelector: []
  sync: []
}>()
</script>
