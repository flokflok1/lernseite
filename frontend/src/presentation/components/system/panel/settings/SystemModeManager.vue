<template>
  <div class="system-mode-manager bg-[#1a1f35] rounded-lg p-6">
    <h3 class="text-lg font-semibold text-white mb-2">
      {{ $t('panel.systemSettings.environmentMode') }}
    </h3>
    <p class="text-sm text-gray-400 mb-6">
      {{ $t('panel.systemSettings.environmentDescription') }}
    </p>

    <!-- Current Mode Banner -->
    <div
      v-if="currentMode"
      class="mb-6 p-4 bg-primary-500/10 border border-primary-500/50 rounded-lg"
    >
      <p class="text-sm text-primary-200">
        {{ $t('panel.systemSettings.currentMode') }}:
        <span class="font-semibold">{{ currentMode }}</span>
      </p>
    </div>

    <!-- Mode Selection Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <!-- Development Card -->
      <div
        @click="selectMode('development')"
        :class="[
          'p-6 rounded-lg border-2 cursor-pointer transition-all',
          selectedMode === 'development'
            ? 'border-yellow-500 bg-yellow-500/10'
            : 'border-[#2a3350] bg-[#0f1419] hover:border-[#3a4360]'
        ]"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h4 class="text-lg font-semibold text-white mb-1">
              🛠️ {{ $t('panel.systemSettings.development') }}
            </h4>
            <p class="text-xs text-gray-400">
              {{ $t('panel.systemSettings.developmentDesc') }}
            </p>
          </div>
          <div
            :class="[
              'w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0',
              selectedMode === 'development'
                ? 'border-yellow-500 bg-yellow-500'
                : 'border-[#2a3350]'
            ]"
          >
            <svg
              v-if="selectedMode === 'development'"
              class="w-4 h-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>

        <ul class="space-y-2 text-sm text-gray-300">
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.debugMode') }}
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.corsAll') }}
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.detailedLogs') }}
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.hotReload') }}
          </li>
        </ul>
      </div>

      <!-- Production Card -->
      <div
        @click="selectMode('production')"
        :class="[
          'p-6 rounded-lg border-2 cursor-pointer transition-all',
          selectedMode === 'production'
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-[#2a3350] bg-[#0f1419] hover:border-[#3a4360]'
        ]"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h4 class="text-lg font-semibold text-white mb-1">
              🚀 {{ $t('panel.systemSettings.production') }}
            </h4>
            <p class="text-xs text-gray-400">
              {{ $t('panel.systemSettings.productionDesc') }}
            </p>
          </div>
          <div
            :class="[
              'w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0',
              selectedMode === 'production'
                ? 'border-blue-500 bg-blue-500'
                : 'border-[#2a3350]'
            ]"
          >
            <svg
              v-if="selectedMode === 'production'"
              class="w-4 h-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>

        <ul class="space-y-2 text-sm text-gray-300">
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.optimized') }}
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.securityHeaders') }}
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.rateLimiting') }}
          </li>
          <li class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clip-rule="evenodd"
              />
            </svg>
            {{ $t('panel.systemSettings.features.productionLogging') }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex items-center justify-between">
      <button
        @click="switchMode"
        :disabled="selectedMode === currentMode || loading"
        class="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2 px-6 rounded-lg transition-colors"
      >
        {{ loading ? $t('common.loading') : $t('panel.systemSettings.switchMode') }}
      </button>

      <div v-if="selectedMode !== currentMode" class="text-sm text-yellow-300">
        ⚠️ {{ $t('panel.systemSettings.requiresRestart') }}
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg">
      <p class="text-sm text-green-200 mb-2">{{ successMessage }}</p>
      <p class="text-xs text-green-300">
        {{ $t('panel.systemSettings.restartInstructions') }}
      </p>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-4 p-4 bg-red-900/30 border border-red-700 rounded-lg">
      <p class="text-sm text-red-200">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSystemMode } from '@/application/composables/useSystemMode'

const { t } = useI18n()

const {
  currentMode,
  loading,
  error,
  switchEnvironment
} = useSystemMode()

const selectedMode = ref<'development' | 'production'>('development')
const successMessage = ref('')

// Initialize selected mode from current mode
watch(currentMode, (newMode) => {
  selectedMode.value = newMode as 'development' | 'production'
}, { immediate: true })

const selectMode = (mode: 'development' | 'production') => {
  selectedMode.value = mode
  successMessage.value = ''
}

const switchMode = async () => {
  successMessage.value = ''

  const success = await switchEnvironment(selectedMode.value)

  if (success) {
    successMessage.value = t('panel.systemSettings.modeSwitched', {
      mode: selectedMode.value
    })
  }
}
</script>
