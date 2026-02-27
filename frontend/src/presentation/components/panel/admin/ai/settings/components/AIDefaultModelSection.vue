<!--
  Compact default model selection: provider + model dropdowns in one row.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
    <div class="px-4 py-3">
      <div class="flex items-center gap-2 mb-3">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ $t('panel.aiSettingsPage.defaultModel.title') }}
        </h3>
        <span class="text-xs text-[var(--color-text-secondary)]">
          {{ $t('panel.aiSettingsPage.defaultModel.subtitle') }}
        </span>
      </div>

      <div class="flex items-end gap-3">
        <!-- Provider -->
        <div class="w-48">
          <label class="block text-[10px] uppercase tracking-wide text-[var(--color-text-secondary)] mb-1">
            {{ $t('panel.aiSettingsPage.defaultModel.defaultProvider') }}
          </label>
          <select
            :value="selectedProvider"
            class="w-full px-3 py-1.5 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            @change="$emit('providerChange', ($event.target as HTMLSelectElement).value)"
          >
            <option
              v-for="(providerData, providerName) in availableModels"
              :key="providerName"
              :value="providerName"
            >
              {{ providerData.display_name }}
            </option>
          </select>
        </div>

        <!-- Model -->
        <div class="flex-1">
          <label class="block text-[10px] uppercase tracking-wide text-[var(--color-text-secondary)] mb-1">
            {{ $t('panel.aiSettingsPage.defaultModel.defaultModelLabel') }}
          </label>
          <select
            :value="selectedModel"
            class="w-full px-3 py-1.5 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            @change="$emit('modelChange', ($event.target as HTMLSelectElement).value)"
          >
            <option
              v-for="model in currentModels"
              :key="model.name"
              :value="model.name"
            >
              {{ model.name }}
            </option>
          </select>
        </div>

        <!-- Price Info -->
        <div v-if="selectedModelInfo" class="shrink-0 text-xs text-[var(--color-text-secondary)] text-right">
          <div>{{ $t('panel.aiSettingsPage.defaultModel.input') }}: {{ formatPrice(selectedModelInfo.input_price) }}</div>
          <div>{{ $t('panel.aiSettingsPage.defaultModel.output') }}: {{ formatPrice(selectedModelInfo.output_price) }}</div>
        </div>

        <!-- Save -->
        <button
          :disabled="isSaving"
          class="shrink-0 px-4 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
          @click="$emit('save')"
        >
          {{ isSaving ? $t('panel.aiSettingsPage.defaultModel.savingSettings') : $t('panel.aiSettingsPage.defaultModel.saveSettings') }}
        </button>
      </div>

      <!-- Settings Result -->
      <div
        v-if="settingsResult"
        :class="[
          'mt-2 px-3 py-1.5 rounded-lg text-xs',
          settingsResult.success
            ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400'
            : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'
        ]"
      >
        {{ settingsResult.message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AIModel, ProviderModels, SettingsResult } from '../types'

interface Props {
  selectedProvider: string
  selectedModel: string
  availableModels: Record<string, ProviderModels>
  currentModels: AIModel[]
  selectedModelInfo: AIModel | null
  providerIcon: string
  isSaving: boolean
  settingsResult: SettingsResult | null
  formatPrice: (price: number | string | null | undefined) => string
}

defineProps<Props>()

defineEmits<{
  providerChange: [value: string]
  modelChange: [value: string]
  save: []
}>()
</script>
