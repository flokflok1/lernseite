<template>
  <div class="panel-system-settings min-h-screen bg-[#0a0e1a] p-6">
    <!-- Page Header -->
    <div class="max-w-7xl mx-auto mb-8">
      <div class="flex items-center justify-between mb-2">
        <h1 class="text-3xl font-bold text-white">
          {{ $t('panel.systemSettings.title') }}
        </h1>

        <!-- Environment Badge -->
        <span
          :class="[
            'px-4 py-2 rounded-full text-sm font-semibold',
            isProduction
              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/50'
              : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/50'
          ]"
        >
          {{ isProduction ? '🚀 Production' : '🛠️ Development' }}
        </span>
      </div>

      <p class="text-gray-400">
        {{ $t('panel.systemSettings.subtitle') }}
      </p>
    </div>

    <!-- Tab Navigation -->
    <div class="max-w-7xl mx-auto">
      <div class="border-b border-[#2a3350] mb-6">
        <nav class="flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'pb-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-primary-500 text-primary-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            ]"
          >
            <span class="flex items-center gap-2">
              <component :is="tab.icon" class="w-5 h-5" />
              {{ $t(tab.label) }}
            </span>
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div class="space-y-6">
        <!-- System Info Tab -->
        <div v-if="activeTab === 'info'">
          <SystemInfoWidget />
        </div>

        <!-- Environment Mode Tab -->
        <div v-if="activeTab === 'mode'">
          <SystemModeManager />
        </div>

        <!-- Maintenance Mode Tab -->
        <div v-if="activeTab === 'maintenance'">
          <MaintenanceModeToggle />
        </div>
      </div>
    </div>

    <!-- Help Section -->
    <div class="max-w-7xl mx-auto mt-12">
      <div class="bg-[#1a1f35] rounded-lg p-6 border border-[#2a3350]">
        <div class="flex gap-4">
          <div class="flex-shrink-0">
            <svg
              class="w-6 h-6 text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-white mb-2">
              {{ $t('panel.systemSettings.help.title') }}
            </h3>
            <ul class="space-y-2 text-sm text-gray-300">
              <li class="flex items-start gap-2">
                <span class="text-primary-400 mt-1">•</span>
                <span>{{ $t('panel.systemSettings.help.point1') }}</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="text-primary-400 mt-1">•</span>
                <span>{{ $t('panel.systemSettings.help.point2') }}</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="text-primary-400 mt-1">•</span>
                <span>{{ $t('panel.systemSettings.help.point3') }}</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="text-primary-400 mt-1">•</span>
                <span>{{ $t('panel.systemSettings.help.point4') }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AdminSystemSettingsPage
 *
 * Orchestration page for system configuration.
 * Provides tabbed interface for:
 * - System Info (status, uptime, connections)
 * - Environment Mode (development/production switching)
 * - Maintenance Mode (toggle, custom message)
 */
import { ref, h, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSystemMode } from '@/application/composables/useSystemMode'

// Sub-components
import { SystemInfoWidget, SystemModeManager, MaintenanceModeToggle } from '@/presentation/components/system/admin/settings'

const { t } = useI18n()

// System mode composable
const { isProduction } = useSystemMode()

// Tab state
type TabId = 'info' | 'mode' | 'maintenance'
const activeTab = ref<TabId>('info')

// Tab icons (SVG components)
const InfoIcon = () => h('svg', {
  class: 'w-5 h-5',
  fill: 'none',
  stroke: 'currentColor',
  viewBox: '0 0 24 24'
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  })
])

const SettingsIcon = () => h('svg', {
  class: 'w-5 h-5',
  fill: 'none',
  stroke: 'currentColor',
  viewBox: '0 0 24 24'
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
  }),
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z'
  })
])

const ToolIcon = () => h('svg', {
  class: 'w-5 h-5',
  fill: 'none',
  stroke: 'currentColor',
  viewBox: '0 0 24 24'
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
  })
])

// Tab configuration
const tabs = computed(() => [
  {
    id: 'info' as TabId,
    label: 'panel.systemSettings.tabs.info',
    icon: InfoIcon
  },
  {
    id: 'mode' as TabId,
    label: 'panel.systemSettings.tabs.mode',
    icon: SettingsIcon
  },
  {
    id: 'maintenance' as TabId,
    label: 'panel.systemSettings.tabs.maintenance',
    icon: ToolIcon
  }
])
</script>

<style scoped>
/* Additional styles if needed */
</style>
