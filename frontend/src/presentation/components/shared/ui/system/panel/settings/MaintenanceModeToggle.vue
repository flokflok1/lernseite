<template>
  <div class="maintenance-toggle bg-[#1a1f35] rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h3 class="text-lg font-semibold text-white mb-1">
          {{ $t('panel.systemSettings.maintenanceMode') }}
        </h3>
        <p class="text-sm text-gray-400">
          {{ $t('panel.systemSettings.maintenanceModeDescription') }}
        </p>
      </div>

      <!-- Toggle Switch -->
      <button
        @click="toggleMode"
        :disabled="loading"
        :class="[
          'relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50',
          maintenanceEnabled ? 'bg-yellow-500' : 'bg-gray-600'
        ]"
      >
        <span
          :class="[
            'inline-block h-6 w-6 transform rounded-full bg-white transition-transform',
            maintenanceEnabled ? 'translate-x-7' : 'translate-x-1'
          ]"
        />
      </button>
    </div>

    <!-- Status Banner -->
    <div
      v-if="maintenanceEnabled"
      class="mb-6 p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg"
    >
      <div class="flex items-start gap-3">
        <svg
          class="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
            clip-rule="evenodd"
          />
        </svg>
        <div>
          <p class="text-sm font-semibold text-yellow-200 mb-1">
            {{ $t('panel.systemSettings.maintenanceModeActive') }}
          </p>
          <p class="text-xs text-yellow-300">
            {{ $t('panel.systemSettings.onlyAdminsCanAccess') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Custom Message Editor -->
    <div v-if="maintenanceEnabled" class="mb-6">
      <label class="block text-sm font-medium text-gray-300 mb-2">
        {{ $t('panel.systemSettings.customMessage') }}
      </label>
      <textarea
        v-model="maintenanceMessage"
        rows="3"
        :placeholder="$t('panel.systemSettings.messagePlaceholder')"
        class="w-full bg-[#0f1419] border border-[#2a3350] rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      />
      <p class="mt-2 text-xs text-gray-400">
        {{ $t('panel.systemSettings.messageHint') }}
      </p>

      <button
        @click="saveMessage"
        :disabled="loading || !maintenanceMessage.trim()"
        class="mt-3 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg transition-colors"
      >
        {{ $t('common.save') }}
      </button>
    </div>

    <!-- Info Box -->
    <div class="p-4 bg-blue-900/20 border border-blue-700/50 rounded-lg">
      <div class="flex gap-3">
        <svg
          class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
            clip-rule="evenodd"
          />
        </svg>
        <div>
          <p class="text-sm font-semibold text-blue-200 mb-1">
            {{ $t('panel.systemSettings.maintenanceInfo.title') }}
          </p>
          <ul class="text-xs text-blue-300/80 space-y-1">
            <li>• {{ $t('panel.systemSettings.maintenanceInfo.point1') }}</li>
            <li>• {{ $t('panel.systemSettings.maintenanceInfo.point2') }}</li>
            <li>• {{ $t('panel.systemSettings.maintenanceInfo.point3') }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="mt-4 p-3 bg-green-900/30 border border-green-700 rounded-lg">
      <p class="text-sm text-green-200">{{ successMessage }}</p>
    </div>

    <div v-if="error" class="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg">
      <p class="text-sm text-red-200">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSystemMode } from '@/features/useSystemMode'

const { t } = useI18n()

const {
  maintenanceMode,
  loading,
  error,
  toggleMaintenanceMode
} = useSystemMode()

const maintenanceEnabled = ref(false)
const maintenanceMessage = ref('')
const successMessage = ref('')

// Watch for changes from composable
watch(maintenanceMode, (newValue) => {
  maintenanceEnabled.value = newValue
}, { immediate: true })

const toggleMode = async () => {
  const newState = !maintenanceEnabled.value

  successMessage.value = ''

  const success = await toggleMaintenanceMode(newState, maintenanceMessage.value)

  if (success) {
    maintenanceEnabled.value = newState
    successMessage.value = newState
      ? t('panel.systemSettings.maintenanceEnabled')
      : t('panel.systemSettings.maintenanceDisabled')

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  }
}

const saveMessage = async () => {
  if (!maintenanceMessage.value.trim()) return

  successMessage.value = ''

  const success = await toggleMaintenanceMode(true, maintenanceMessage.value)

  if (success) {
    successMessage.value = t('panel.systemSettings.messageSaved')

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  }
}
</script>
