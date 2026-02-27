<!--
  Compact stats bar showing provider counts as inline badges.
-->

<template>
  <div class="flex items-center gap-3 flex-wrap">
    <div
      v-for="stat in stats"
      :key="stat.label"
      class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)]"
    >
      <span class="text-sm">{{ stat.icon }}</span>
      <span class="text-sm font-semibold" :class="stat.color">{{ stat.value }}</span>
      <span class="text-xs text-[var(--color-text-secondary)]">{{ stat.label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  totalCount: number
  activeCount: number
  configuredCount: number
}

const props = defineProps<Props>()
const { t } = useI18n()

const stats = computed(() => [
  {
    icon: '\u{1F916}',
    value: props.totalCount,
    label: t('panel.aiSettingsPage.stats.providersTotal'),
    color: 'text-[var(--color-text-primary)]',
  },
  {
    icon: '\u2705',
    value: props.activeCount,
    label: t('panel.aiSettingsPage.stats.active'),
    color: 'text-green-600',
  },
  {
    icon: '\u{1F511}',
    value: props.configuredCount,
    label: t('panel.aiSettingsPage.stats.configured'),
    color: 'text-blue-600',
  },
])
</script>
