<!--
  Admin AI Settings Page - KI-Provider & API-Keys

  Verwaltung von KI-Providern (OpenAI, Anthropic, Google):
  - API-Keys sicher eingeben und speichern
  - Provider aktivieren/deaktivieren
  - API-Verbindung testen
  - Provider-Status anzeigen
-->

<template>
  <div class="panel-ai-settings-page p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-2">{{ $t('panel.aiSettingsPage.title') }}</h1>
      <p class="text-[var(--color-text-secondary)]">
        {{ $t('panel.aiSettingsPage.subtitle') }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]"></div>
      <span class="ml-3 text-[var(--color-text-secondary)]">{{ $t('panel.aiSettingsPage.loadingProviders') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div class="flex items-center gap-2 text-red-700">
        <span class="text-xl">&#x26A0;</span>
        <span>{{ error }}</span>
      </div>
      <button
        class="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        @click="loadProviders"
      >
        {{ $t('panel.aiSettingsPage.retry') }}
      </button>
    </div>

    <!-- Providers List -->
    <div v-else class="space-y-6">
      <!-- Stats Cards -->
      <AISettingsStatsBar
        :total-count="providers.length"
        :active-count="activeProviders"
        :configured-count="configuredProviders"
      />

      <!-- Provider Cards -->
      <div class="space-y-4">
        <AIProviderCard
          v-for="provider in providers"
          :key="provider.provider_id"
          :provider="provider"
          :api-key="apiKeys[provider.provider_id] || ''"
          :is-api-key-visible="showApiKey[provider.provider_id] || false"
          :is-saving="savingKey[provider.provider_id] || false"
          :is-testing="testingKey[provider.provider_id] || false"
          :is-deleting="deletingKey[provider.provider_id] || false"
          :test-result="testResults[provider.provider_id]"
          :provider-icon="getProviderIcon(provider.name)"
          @update:api-key="apiKeys[provider.provider_id] = $event"
          @toggle-visibility="toggleShowApiKey(provider.provider_id)"
          @save-key="saveApiKey(provider)"
          @test-key="testApiKey(provider)"
          @delete-key="deleteApiKey(provider)"
          @toggle-active="toggleActive(provider)"
          @update-priority="updatePriority(provider, $event)"
          @update-rate-limit="updateRateLimit(provider, $event)"
        />
      </div>

      <!-- Default Model Selection Section -->
      <AIDefaultModelSection
        :selected-provider="defaultSettings.provider"
        :selected-model="defaultSettings.model"
        :available-models="availableModels"
        :current-models="currentProviderModels"
        :selected-model-info="selectedModelInfo"
        :provider-icon="getProviderIcon(defaultSettings.provider)"
        :is-saving="savingSettings"
        :settings-result="settingsResult"
        :format-price="formatPrice"
        @provider-change="handleProviderChange"
        @model-change="defaultSettings.model = $event"
        @save="saveDefaultSettings"
      />

      <!-- Available Models Overview -->
      <AIModelsOverview
        :available-models="availableModels"
        :total-model-count="totalModelCount"
        :provider-count="Object.keys(availableModels).length"
        :get-provider-icon="getProviderIcon"
        @open-model-selector="openModelSelector"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useWindowStore } from '@/application/stores/modules/ui/window.store'

import { useAISettingsManager } from '@/presentation/components/panel/admin/ai-settings/composables'
import { AISettingsStatsBar, AIProviderCard, AIDefaultModelSection, AIModelsOverview } from '@/presentation/components/panel/admin/ai-settings/components'

const windowStore = useWindowStore()

const {
  providers,
  loading,
  error,
  apiKeys,
  showApiKey,
  savingKey,
  testingKey,
  deletingKey,
  testResults,
  availableModels,
  defaultSettings,
  savingSettings,
  settingsResult,
  activeProviders,
  configuredProviders,
  totalModelCount,
  currentProviderModels,
  selectedModelInfo,
  loadProviders,
  saveApiKey,
  testApiKey,
  deleteApiKey,
  toggleActive,
  updatePriority,
  updateRateLimit,
  onProviderChange,
  saveDefaultSettings,
  getProviderIcon,
  formatPrice,
  toggleShowApiKey,
  initializeAll,
} = useAISettingsManager()

function handleProviderChange(value: string): void {
  defaultSettings.value.provider = value
  onProviderChange()
}

function openModelSelector(): void {
  windowStore.openWindow({
    type: 'panel-model-selector',
    title: 'AI Model Selector',
    icon: '\u{1F916}',
    size: { width: 700, height: 600 },
    payload: {
      scope: 'global',
    },
  })
}

onMounted(async () => {
  await initializeAll()
})
</script>
