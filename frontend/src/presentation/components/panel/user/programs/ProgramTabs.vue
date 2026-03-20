<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{ activeTab: string }>()
const emit = defineEmits<{ change: [tab: string] }>()
const { t } = useI18n()

const tabs = [
  { key: 'learning', label: () => t('panel.programs.tabs.learningPath'), icon: '\uD83D\uDCD6' },
  { key: 'trainer', label: () => t('panel.programs.tabs.trainer'), icon: '\uD83D\uDCDD' },
  { key: 'prognosis', label: () => t('panel.programs.tabs.prognosis'), icon: '\uD83D\uDCCA' },
  { key: 'progress', label: () => t('panel.programs.tabs.progress'), icon: '\uD83D\uDCC8' },
]
</script>

<template>
  <div class="flex border-b border-[var(--color-border)] bg-[var(--color-surface)]">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      class="px-5 py-3 text-sm font-medium transition-colors border-b-2 flex items-center gap-2"
      :class="activeTab === tab.key
        ? 'border-blue-500 text-blue-400'
        : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text)]'"
      @click="emit('change', tab.key)"
    >
      <span>{{ tab.icon }}</span>
      <span>{{ tab.label() }}</span>
    </button>
  </div>
</template>
