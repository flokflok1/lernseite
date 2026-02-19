<!--
  Default model selection section for choosing the default AI provider and model.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
    <div class="px-6 py-4 border-b border-[var(--color-border)]">
      <h3 class="text-lg font-bold text-[var(--color-text-primary)]">
        {{ $t('panel.aiSettingsPage.defaultModel.title') }}
      </h3>
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ $t('panel.aiSettingsPage.defaultModel.subtitle') }}
      </p>
    </div>

    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Default Provider Selection -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('panel.aiSettingsPage.defaultModel.defaultProvider') }}
          </label>
          <select
            :value="selectedProvider"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
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

        <!-- Default Model Selection -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('panel.aiSettingsPage.defaultModel.defaultModelLabel') }}
          </label>
          <select
            :value="selectedModel"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            @change="$emit('modelChange', ($event.target as HTMLSelectElement).value)"
          >
            <option
              v-for="model in currentModels"
              :key="model.name"
              :value="model.name"
            >
              {{ model.name }} ({{ formatPrice(model.input_price) }}/{{ formatPrice(model.output_price) }} {{ $t('panel.aiSettingsPage.defaultModel.perThousandTokens') }})
            </option>
          </select>
        </div>
      </div>

      <!-- Model Info -->
      <div v-if="selectedModelInfo" class="mt-4 p-4 bg-[var(--color-bg)] rounded-lg border border-[var(--color-border)]">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-[var(--color-text-primary)]">{{ selectedModelInfo.name }}</p>
            <p class="text-sm text-[var(--color-text-secondary)]">
              {{ $t('panel.aiSettingsPage.defaultModel.input') }}: {{ formatPrice(selectedModelInfo.input_price) }} | {{ $t('panel.aiSettingsPage.defaultModel.output') }}: {{ formatPrice(selectedModelInfo.output_price) }} {{ $t('panel.aiSettingsPage.defaultModel.perThousandTokens') }}
            </p>
          </div>
          <div class="text-2xl">
            {{ providerIcon }}
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="mt-4 flex justify-end">
        <button
          :disabled="isSaving"
          class="px-6 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity flex items-center gap-2"
          @click="$emit('save')"
        >
          <span v-if="isSaving" class="animate-spin">&#x23F3;</span>
          <span>{{ isSaving ? $t('panel.aiSettingsPage.defaultModel.savingSettings') : $t('panel.aiSettingsPage.defaultModel.saveSettings') }}</span>
        </button>
      </div>

      <!-- Settings Result -->
      <div
        v-if="settingsResult"
        :class="[
          'mt-3 p-3 rounded-lg text-sm',
          settingsResult.success
            ? 'bg-green-50 text-green-700 border border-green-200'
            : 'bg-red-50 text-red-700 border border-red-200'
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
