<!--
  ModelCard - AI Model Display Card
  Sub-component of ModelsTab
-->

<template>
  <div
    class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 hover:border-[var(--color-primary)] transition-colors"
    :class="{ 'border-yellow-500': model.is_default }"
  >
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-3">
        <span
          class="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
          :class="providerStyle"
        >
          {{ providerIcon }}
        </span>
        <div>
          <h4 class="font-medium text-[var(--color-text-primary)]">{{ model.display_name || model.model_name }}</h4>
          <p class="text-xs text-[var(--color-text-tertiary)]">{{ model.provider_name }} | {{ model.category }}</p>
        </div>
      </div>
      <div class="flex flex-col gap-1 items-end">
        <span
          class="px-2 py-1 text-xs rounded-full"
          :class="model.active
            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
            : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'"
        >
          {{ model.active ? $t('windows.aiStudioModels.active') : $t('windows.aiStudioModels.inactive') }}
        </span>
        <span v-if="model.is_default" class="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
          ⭐ {{ $t('windows.aiStudioModelCard.default') }}
        </span>
      </div>
    </div>

    <!-- Capabilities -->
    <div class="flex flex-wrap gap-1 mb-3">
      <span v-if="model.supports_vision" class="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded">Vision</span>
      <span v-if="model.supports_functions" class="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 rounded">Functions</span>
      <span class="px-2 py-0.5 text-xs bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] rounded capitalize">{{ model.model_type }}</span>
      <span v-if="model.cost_level" class="px-2 py-0.5 text-xs bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] rounded">{{ model.cost_level }}</span>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-2 text-xs">
      <div class="text-center p-2 bg-[var(--color-surface-secondary)] rounded-lg">
        <div class="text-[var(--color-text-tertiary)]">Input</div>
        <div class="font-medium text-[var(--color-text-primary)]">
          {{ model.input_price_per_1k ? `$${parseFloat(String(model.input_price_per_1k)).toFixed(4)}/1K` : '-' }}
        </div>
      </div>
      <div class="text-center p-2 bg-[var(--color-surface-secondary)] rounded-lg">
        <div class="text-[var(--color-text-tertiary)]">Output</div>
        <div class="font-medium text-[var(--color-text-primary)]">
          {{ model.output_price_per_1k ? `$${parseFloat(String(model.output_price_per_1k)).toFixed(4)}/1K` : '-' }}
        </div>
      </div>
      <div class="text-center p-2 bg-[var(--color-surface-secondary)] rounded-lg">
        <div class="text-[var(--color-text-tertiary)]">Context</div>
        <div class="font-medium text-[var(--color-text-primary)]">
          {{ model.context_window ? formatNumber(model.context_window) : '-' }}
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="mt-3 flex gap-2">
      <button
        @click="$emit('toggleActive')"
        class="flex-1 px-3 py-1.5 text-xs rounded-lg transition-colors"
        :class="model.active
          ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400'
          : 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-400'"
      >
        {{ model.active ? $t('windows.aiStudioModels.deactivate') : $t('windows.aiStudioModels.activate') }}
      </button>
      <button
        v-if="!model.is_default && model.active"
        @click="$emit('makeDefault')"
        class="flex-1 px-3 py-1.5 text-xs bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 rounded-lg transition-colors"
      >
        {{ $t('windows.aiStudioModels.setDefault') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface AIModel {
  model_id: number
  provider_name: string
  model_name: string
  display_name: string
  model_type: string
  category: string
  cost_level?: string
  context_window?: number
  supports_vision: boolean
  supports_functions: boolean
  input_price_per_1k?: number
  output_price_per_1k?: number
  active: boolean
  is_default: boolean
}

defineProps<{
  model: AIModel
  providerIcon: string
  providerStyle: string
}>()

defineEmits<{
  (e: 'toggleActive'): void
  (e: 'makeDefault'): void
}>()

function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(0)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(0)}K`
  return num.toString()
}
</script>
