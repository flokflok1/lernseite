<template>
  <div class="panel-ai-settings-page p-4">
    <!-- Page Header -->
    <div class="mb-4 flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-[var(--color-text-primary)]">{{ $t('panel.aiSettingsPage.title') }}</h1>
        <p class="text-xs text-[var(--color-text-secondary)]">
          {{ $t('panel.aiSettingsPage.subtitle') }}
        </p>
      </div>

      <!-- Stats inline with header -->
      <AISettingsStatsBar
        v-if="!loading && !error"
        :total-count="providers.length"
        :active-count="activeProviders"
        :configured-count="configuredProviders"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--color-primary)]"></div>
      <span class="ml-2 text-sm text-[var(--color-text-secondary)]">{{ $t('panel.aiSettingsPage.loadingProviders') }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-4">
      <div class="flex items-center gap-2 text-red-700 dark:text-red-400 text-sm">
        <span>&#x26A0;</span>
        <span>{{ error }}</span>
        <button
          class="ml-auto text-xs underline hover:no-underline"
          @click="loadProviders"
        >
          {{ $t('panel.aiSettingsPage.retry') }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-3">
      <!-- Provider Cards -->
      <div class="space-y-2">
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

      <!-- Default Model Selection -->
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

      <!-- Models Overview + Sync -->
      <AIModelsOverview
        :available-models="availableModels"
        :total-model-count="totalModelCount"
        :provider-count="Object.keys(availableModels).length"
        :get-provider-icon="getProviderIcon"
        :is-syncing="syncingModels"
        :sync-result="syncResult"
        @open-model-selector="openModelSelector"
        @sync="syncModelsFromProviders"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useWindowStore } from '@/application/stores/modules/ui/window.store'

import { useAISettingsManager } from '@/presentation/components/panel/admin/ai/settings/composables'
import { AISettingsStatsBar, AIProviderCard, AIDefaultModelSection, AIModelsOverview } from '@/presentation/components/panel/admin/ai/settings/components'

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
  syncingModels,
  syncResult,
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
  syncModelsFromProviders,
  initializeAll,
} = useAISettingsManager()

function handleProviderChange(value: string): void {
  defaultSettings.value.provider = value
  onProviderChange()
}

function openModelSelector(): void {
  windowStore.openWindow({
    type: 'admin-model-selector',
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
