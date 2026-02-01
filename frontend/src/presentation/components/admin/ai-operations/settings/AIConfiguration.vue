<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAISettings } from './composables/useAISettings'
import AIProfileManager from './AIProfileManager.vue'

const { t } = useI18n()
const {
  settings,
  isLoading,
  error,
  syncProgress,
  claudeModels,
  openaiModels,
  availableProviders,
  loadSettings,
  updateApiKey,
  saveApiKey,
  syncModels,
  toggleModel,
  setDefaultProvider,
  testConnection
} = useAISettings()

const mainTab = ref<'settings' | 'profiles'>('settings')
const settingsTab = ref<'claude' | 'openai'>('claude')
const testingProvider = ref<string | null>(null)
const savedMessage = ref<string | null>(null)

onMounted(() => {
  loadSettings()
})

const handleTestConnection = async (provider: 'claude' | 'openai') => {
  testingProvider.value = provider
  const success = await testConnection(provider)
  testingProvider.value = null

  if (success) {
    savedMessage.value = `${provider} connection successful!`
    setTimeout(() => (savedMessage.value = null), 3000)
  }
}

const handleSaveApiKey = async (provider: 'claude' | 'openai') => {
  const apiKey = provider === 'claude' ? settings.value.claudeApiKey : settings.value.openaiApiKey
  const success = await saveApiKey(provider, apiKey)

  if (success) {
    savedMessage.value = `${provider} API key saved!`
    setTimeout(() => (savedMessage.value = null), 3000)
  }
}

const formatDate = (date: Date | undefined) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}
</script>

<template>
  <div class="ai-configuration">
    <!-- Header -->
    <div class="mb-6">
      <h3 class="text-xl font-semibold text-[var(--color-text-primary)] mb-2">
        {{ $t('admin.aiSettings.title', 'AI Provider Configuration') }}
      </h3>
      <p class="text-[var(--color-text-secondary)]">
        {{ $t('admin.aiSettings.description', 'Configure API keys for Claude and OpenAI, and synchronize available models') }}
      </p>
    </div>

    <!-- Success Message -->
    <div v-if="savedMessage" class="mb-4 p-3 bg-green-500/20 border border-green-500/50 rounded-lg text-green-300">
      {{ savedMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && !settings.models.length" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
      <p class="text-[var(--color-text-secondary)]">{{ $t('common.loading', 'Loading') }}...</p>
    </div>

    <!-- Main Tabs -->
    <div v-else class="space-y-6">
      <!-- Main Tab Navigation -->
      <div class="flex gap-4 border-b border-[var(--color-border)]">
        <button
          @click="mainTab = 'settings'"
          :class="[
            'pb-3 px-1 font-medium transition-colors border-b-2',
            mainTab === 'settings'
              ? 'text-blue-400 border-blue-400'
              : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
          ]"
        >
          API Settings
        </button>
        <button
          @click="mainTab = 'profiles'"
          :class="[
            'pb-3 px-1 font-medium transition-colors border-b-2',
            mainTab === 'profiles'
              ? 'text-blue-400 border-blue-400'
              : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
          ]"
        >
          Manage Profiles
        </button>
      </div>

      <!-- API SETTINGS TAB -->
      <div v-show="mainTab === 'settings'" class="space-y-6">
        <!-- Provider Sub-Tabs -->
        <div class="flex gap-4 border-b border-[var(--color-border)]">
          <button
            @click="settingsTab = 'claude'"
            :class="[
              'pb-3 px-1 font-medium transition-colors border-b-2',
              settingsTab === 'claude'
                ? 'text-blue-400 border-blue-400'
                : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
            ]"
          >
            Claude (Anthropic)
          </button>
          <button
            @click="settingsTab = 'openai'"
            :class="[
              'pb-3 px-1 font-medium transition-colors border-b-2',
              settingsTab === 'openai'
                ? 'text-blue-400 border-blue-400'
                : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
            ]"
          >
            OpenAI (GPT)
          </button>
        </div>

        <!-- Claude Configuration -->
        <div v-show="settingsTab === 'claude'" class="space-y-4">
        <div class="bg-[var(--color-surface)] rounded-lg p-6 border border-[var(--color-border)]">
          <h4 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Claude API Configuration</h4>

          <!-- API Key Input -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              API Key
            </label>
            <div class="flex gap-2">
              <input
                :value="settings.claudeApiKey"
                @input="e => updateApiKey('claude', (e.target as HTMLInputElement).value)"
                type="password"
                placeholder="sk-ant-..."
                class="flex-1 px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)]/50 focus:outline-none focus:border-blue-500"
              />
              <button
                @click="() => handleSaveApiKey('claude')"
                :disabled="isLoading || !settings.claudeApiKey"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
              >
                {{ isLoading ? '...' : 'Save' }}
              </button>
            </div>
            <p class="text-xs text-[var(--color-text-secondary)] mt-2">
              Get your API key from https://console.anthropic.com
            </p>
          </div>

          <!-- Test Connection -->
          <div class="mb-6">
            <button
              @click="() => handleTestConnection('claude')"
              :disabled="isLoading || !settings.claudeApiKey"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {{ testingProvider === 'claude' ? 'Testing...' : 'Test Connection' }}
            </button>
          </div>

          <!-- Available Models -->
          <div>
            <h5 class="font-medium text-[var(--color-text-primary)] mb-3">Available Models</h5>
            <div class="space-y-2">
              <div v-if="claudeModels.length === 0" class="text-sm text-[var(--color-text-secondary)]">
                Click "Sync Models" to load available Claude models
              </div>
              <div
                v-for="model in claudeModels"
                :key="model.id"
                class="flex items-start gap-3 p-3 bg-[var(--color-bg)] rounded-lg border border-[var(--color-border)]"
              >
                <input
                  type="checkbox"
                  :checked="model.isAvailable"
                  @change="() => toggleModel(model.id)"
                  class="mt-1 w-4 h-4 cursor-pointer"
                />
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <p class="font-medium text-[var(--color-text-primary)]">{{ model.name }}</p>
                    <span v-if="model.category" class="px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded text-xs font-medium">
                      {{ model.category }}
                    </span>
                  </div>
                  <p v-if="model.description" class="text-xs text-[var(--color-text-secondary)]">
                    {{ model.description }}
                  </p>
                  <div v-if="model.inputTokens || model.outputTokens" class="text-xs text-[var(--color-text-secondary)] mt-1">
                    <span v-if="model.inputTokens">Input: {{ model.inputTokens.toLocaleString() }}</span>
                    <span v-if="model.outputTokens" class="ml-3">Output: {{ model.outputTokens }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- OpenAI Configuration -->
      <div v-show="settingsTab === 'openai'" class="space-y-4">
        <div class="bg-[var(--color-surface)] rounded-lg p-6 border border-[var(--color-border)]">
          <h4 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">OpenAI API Configuration</h4>

          <!-- API Key Input -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              API Key
            </label>
            <div class="flex gap-2">
              <input
                :value="settings.openaiApiKey"
                @input="e => updateApiKey('openai', (e.target as HTMLInputElement).value)"
                type="password"
                placeholder="sk-..."
                class="flex-1 px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)]/50 focus:outline-none focus:border-blue-500"
              />
              <button
                @click="() => handleSaveApiKey('openai')"
                :disabled="isLoading || !settings.openaiApiKey"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
              >
                {{ isLoading ? '...' : 'Save' }}
              </button>
            </div>
            <p class="text-xs text-[var(--color-text-secondary)] mt-2">
              Get your API key from https://platform.openai.com/account/api-keys
            </p>
          </div>

          <!-- Test Connection -->
          <div class="mb-6">
            <button
              @click="() => handleTestConnection('openai')"
              :disabled="isLoading || !settings.openaiApiKey"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {{ testingProvider === 'openai' ? 'Testing...' : 'Test Connection' }}
            </button>
          </div>

          <!-- Available Models -->
          <div>
            <h5 class="font-medium text-[var(--color-text-primary)] mb-3">Available Models</h5>
            <div class="space-y-2">
              <div v-if="openaiModels.length === 0" class="text-sm text-[var(--color-text-secondary)]">
                Click "Sync Models" to load available OpenAI models
              </div>
              <div
                v-for="model in openaiModels"
                :key="model.id"
                class="flex items-start gap-3 p-3 bg-[var(--color-bg)] rounded-lg border border-[var(--color-border)]"
              >
                <input
                  type="checkbox"
                  :checked="model.isAvailable"
                  @change="() => toggleModel(model.id)"
                  class="mt-1 w-4 h-4 cursor-pointer"
                />
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <p class="font-medium text-[var(--color-text-primary)]">{{ model.name }}</p>
                    <span v-if="model.category" class="px-2 py-0.5 bg-green-500/20 text-green-300 rounded text-xs font-medium">
                      {{ model.category }}
                    </span>
                  </div>
                  <p v-if="model.description" class="text-xs text-[var(--color-text-secondary)]">
                    {{ model.description }}
                  </p>
                  <div v-if="model.inputTokens || model.outputTokens" class="text-xs text-[var(--color-text-secondary)] mt-1">
                    <span v-if="model.inputTokens">Input: {{ model.inputTokens.toLocaleString() }}</span>
                    <span v-if="model.outputTokens" class="ml-3">Output: {{ model.outputTokens }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Model Synchronization Section -->
      <div class="bg-[var(--color-surface)] rounded-lg p-6 border border-[var(--color-border)]">
        <h4 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">Model Synchronization</h4>
        <p class="text-sm text-[var(--color-text-secondary)] mb-4">
          Sync available models from all configured providers. This loads the latest models and their capabilities.
        </p>

        <!-- Sync Progress -->
        <div v-if="settings.isSyncing" class="mb-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-[var(--color-text-primary)]">Syncing models...</span>
            <span class="text-sm text-[var(--color-text-secondary)]">{{ syncProgress }}%</span>
          </div>
          <div class="w-full h-2 bg-[var(--color-bg)] rounded-full overflow-hidden">
            <div
              class="h-full bg-blue-500 transition-all duration-300"
              :style="{ width: `${syncProgress}%` }"
            ></div>
          </div>
        </div>

        <!-- Sync Button -->
        <div class="flex gap-2 mb-4">
          <button
            @click="syncModels"
            :disabled="settings.isSyncing || availableProviders.length === 0"
            class="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
          >
            {{ settings.isSyncing ? 'Syncing...' : 'Sync Models' }}
          </button>
          <span v-if="availableProviders.length === 0" class="text-sm text-red-400 flex items-center">
            Configure at least one API key to sync models
          </span>
        </div>

        <!-- Last Sync Info -->
        <div v-if="settings.lastSyncTime" class="text-sm text-[var(--color-text-secondary)]">
          Last synced: {{ formatDate(settings.lastSyncTime) }}
        </div>
      </div>

        <!-- Default Provider Selection -->
        <div class="bg-[var(--color-surface)] rounded-lg p-6 border border-[var(--color-border)]">
          <h4 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Default Provider</h4>
          <div class="space-y-2">
            <label v-for="provider in availableProviders" :key="provider.id" class="flex items-center gap-3 p-3 bg-[var(--color-bg)] rounded-lg border border-[var(--color-border)] cursor-pointer hover:border-blue-500">
              <input
                type="radio"
                :value="provider.id"
                :checked="settings.defaultProvider === provider.id"
                @change="() => setDefaultProvider(provider.id)"
                class="w-4 h-4 cursor-pointer"
              />
              <span class="text-[var(--color-text-primary)] font-medium">{{ provider.name }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- PROFILES TAB -->
      <div v-show="mainTab === 'profiles'" class="space-y-6">
        <AIProfileManager />
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-configuration {
  /* Inherits colors from theme variables */
}
</style>
