<!--
  Stats bar showing provider counts (total, active, configured).
-->

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-1">{{ $t('panel.aiSettingsPage.stats.providersTotal') }}</p>
          <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ totalCount }}</p>
        </div>
        <div class="text-3xl">&#x1F916;</div>
      </div>
    </div>

    <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-1">{{ $t('panel.aiSettingsPage.stats.active') }}</p>
          <p class="text-2xl font-bold text-green-600">{{ activeCount }}</p>
        </div>
        <div class="text-3xl">&#x2705;</div>
      </div>
    </div>

    <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-1">{{ $t('panel.aiSettingsPage.stats.configured') }}</p>
          <p class="text-2xl font-bold text-blue-600">{{ configuredCount }}</p>
        </div>
        <div class="text-3xl">&#x1F511;</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  totalCount: number
  activeCount: number
  configuredCount: number
}

defineProps<Props>()
</script>
