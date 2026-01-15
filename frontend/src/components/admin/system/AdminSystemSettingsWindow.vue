<!--
  Admin System Settings Window

  Desktop-layer window with tabbed interface for:
  - System Information
  - Environment Mode
  - KI/AI Settings
  - Maintenance Mode

  Can be minimized, dragged, resized like other windows
-->

<template>
  <div class="admin-system-settings-window h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header with Tab Navigation -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
          {{ window.title }}
        </h2>
        <span
          :class="[
            'px-3 py-1 rounded-full text-xs font-semibold',
            isProduction
              ? 'bg-blue-500/20 text-blue-300'
              : 'bg-yellow-500/20 text-yellow-300'
          ]"
        >
          {{ isProduction ? '🚀 Prod' : '🛠️ Dev' }}
        </span>
      </div>

      <!-- Tabs -->
      <div class="flex space-x-4 border-b border-[var(--color-border)]">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'pb-2 px-2 text-sm font-medium transition-colors',
            activeTab === tab.id
              ? 'border-b-2 border-blue-500 text-blue-400'
              : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl">
        <!-- System Info Tab -->
        <div v-if="activeTab === 'info'">
          <SystemInfoWidget />
        </div>

        <!-- Environment Mode Tab -->
        <div v-if="activeTab === 'mode'">
          <SystemModeManager />
        </div>

        <!-- KI Settings Tab -->
        <div v-if="activeTab === 'ki'">
          <div class="space-y-6">
            <div class="bg-[var(--color-surface)] rounded-lg p-6 border border-[var(--color-border)]">
              <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
                {{ $t('admin.systemSettings.ki.title') }}
              </h3>
              <p class="text-[var(--color-text-secondary)] mb-6">
                {{ $t('admin.systemSettings.ki.description') }}
              </p>
              <GlobalSettingsTab />
            </div>
          </div>
        </div>

        <!-- Maintenance Tab -->
        <div v-if="activeTab === 'maintenance'">
          <MaintenanceModeToggle />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/store/modules/desktop'
import SystemInfoWidget from '@/components/base/system/admin/settings/SystemInfoWidget.vue'
import SystemModeManager from '@/components/base/system/admin/settings/SystemModeManager.vue'
import MaintenanceModeToggle from '@/components/base/system/admin/settings/MaintenanceModeToggle.vue'
import GlobalSettingsTab from '@/components/studio/ai/admin/studio/tabs/GlobalSettingsTab.vue'

interface Props {
  window: LsxWindow
}

defineProps<Props>()
defineEmits<{ (e: 'close'): void }>()

const { t } = useI18n()
const activeTab = ref('info')

// Computed
const isProduction = computed(() => {
  return import.meta.env.PROD && !import.meta.env.DEV
})

// Tabs
const tabs = [
  { id: 'info', label: t('admin.systemSettings.tabs.info') },
  { id: 'mode', label: t('admin.systemSettings.tabs.mode') },
  { id: 'ki', label: t('admin.systemSettings.tabs.ki') },
  { id: 'maintenance', label: t('admin.systemSettings.tabs.maintenance') }
]
</script>

<style scoped>
.admin-system-settings-window {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
