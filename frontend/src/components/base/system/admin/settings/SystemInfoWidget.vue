<template>
  <div class="system-info-widget bg-[#1a1f35] rounded-lg p-6">
    <h3 class="text-lg font-semibold text-white mb-4">
      {{ $t('admin.systemSettings.systemInfo') }}
    </h3>

    <!-- Environment Badge -->
    <div class="mb-6">
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-400">
          {{ $t('admin.systemSettings.currentEnvironment') }}:
        </span>
        <span
          :class="[
            'px-3 py-1 rounded-full text-xs font-semibold',
            isProduction
              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/50'
              : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/50'
          ]"
        >
          {{ isProduction ? '🚀 Production' : '🛠️ Development' }}
        </span>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-2 gap-4 mb-6">
      <!-- Uptime -->
      <div class="bg-[#0f1419] rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg
            class="w-5 h-5 text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span class="text-xs text-gray-400">
            {{ $t('admin.systemSettings.uptime') }}
          </span>
        </div>
        <p class="text-lg font-semibold text-white">{{ uptime }}</p>
      </div>

      <!-- Version -->
      <div class="bg-[#0f1419] rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg
            class="w-5 h-5 text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
            />
          </svg>
          <span class="text-xs text-gray-400">
            {{ $t('admin.systemSettings.version') }}
          </span>
        </div>
        <p class="text-lg font-semibold text-white">
          {{ systemStatus?.version || '1.0.0' }}
        </p>
      </div>

      <!-- Database Status -->
      <div class="bg-[#0f1419] rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg
            class="w-5 h-5 text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
            />
          </svg>
          <span class="text-xs text-gray-400">
            {{ $t('admin.systemSettings.database') }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              systemStatus?.database_connected ? 'bg-green-500' : 'bg-red-500'
            ]"
          />
          <p class="text-sm font-semibold text-white">
            {{
              systemStatus?.database_connected
                ? $t('common.connected')
                : $t('common.disconnected')
            }}
          </p>
        </div>
      </div>

      <!-- Redis Status -->
      <div class="bg-[#0f1419] rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <svg
            class="w-5 h-5 text-primary-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"
            />
          </svg>
          <span class="text-xs text-gray-400">Redis</span>
        </div>
        <div class="flex items-center gap-2">
          <span
            :class="[
              'w-2 h-2 rounded-full',
              systemStatus?.redis_connected ? 'bg-green-500' : 'bg-red-500'
            ]"
          />
          <p class="text-sm font-semibold text-white">
            {{
              systemStatus?.redis_connected
                ? $t('common.connected')
                : $t('common.disconnected')
            }}
          </p>
        </div>
      </div>
    </div>

    <!-- Feature Flags -->
    <div class="mb-6">
      <h4 class="text-sm font-semibold text-gray-300 mb-3">
        {{ $t('admin.systemSettings.activeFeatures') }}
      </h4>
      <div class="space-y-2">
        <div class="flex items-center justify-between p-2 bg-[#0f1419] rounded">
          <span class="text-sm text-gray-300">Debug Mode</span>
          <span
            :class="[
              'px-2 py-1 rounded text-xs font-semibold',
              debugEnabled
                ? 'bg-green-500/20 text-green-300'
                : 'bg-gray-500/20 text-gray-400'
            ]"
          >
            {{ debugEnabled ? 'ON' : 'OFF' }}
          </span>
        </div>
        <div class="flex items-center justify-between p-2 bg-[#0f1419] rounded">
          <span class="text-sm text-gray-300">
            {{ $t('admin.systemSettings.maintenanceMode') }}
          </span>
          <span
            :class="[
              'px-2 py-1 rounded text-xs font-semibold',
              maintenanceMode
                ? 'bg-yellow-500/20 text-yellow-300'
                : 'bg-gray-500/20 text-gray-400'
            ]"
          >
            {{ maintenanceMode ? 'ACTIVE' : 'OFF' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Refresh Button -->
    <button
      @click="handleRefresh"
      :disabled="loading"
      class="w-full bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
    >
      <svg
        :class="['w-4 h-4', loading && 'animate-spin']"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
        />
      </svg>
      {{ loading ? $t('common.loading') : $t('common.refresh') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSystemMode } from '@/composables/useSystemMode'

const { t } = useI18n()

const {
  systemStatus,
  loading,
  uptime,
  isProduction,
  debugEnabled,
  maintenanceMode,
  refreshStatus
} = useSystemMode()

let refreshInterval: ReturnType<typeof setInterval> | null = null

const handleRefresh = async () => {
  await refreshStatus()
}

onMounted(() => {
  // Initial load
  refreshStatus()

  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(() => {
    refreshStatus()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
