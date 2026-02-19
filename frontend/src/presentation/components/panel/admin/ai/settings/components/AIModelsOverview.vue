<!--
  Compact overview of available AI models with a button to open the model selector.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
    <div class="px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div>
          <h3 class="text-lg font-bold text-[var(--color-text-primary)]">
            {{ $t('panel.aiSettingsPage.availableModels.title') }}
          </h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ $t('panel.aiSettingsPage.availableModels.modelsFromProviders', { count: totalModelCount, providers: providerCount }) }}
          </p>
        </div>
        <!-- Provider Badges -->
        <div class="flex gap-2 flex-wrap">
          <span
            v-for="(providerData, providerName) in availableModels"
            :key="providerName"
            class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-[var(--color-bg)] border border-[var(--color-border)]"
          >
            <span>{{ getProviderIcon(providerName as string) }}</span>
            <span class="text-[var(--color-text-secondary)]">{{ providerData.models.length }}</span>
          </span>
        </div>
      </div>
      <button
        class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors flex items-center gap-2"
        @click="$emit('openModelSelector')"
      >
        <span>&#x1F50D;</span>
        <span>{{ $t('panel.aiSettingsPage.availableModels.modelSelector') }}</span>
      </button>
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
}

defineProps<Props>()

defineEmits<{
  openModelSelector: []
}>()
</script>
