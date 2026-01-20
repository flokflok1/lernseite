<!--
  StatsOverview - Model Statistics Display
  Sub-component of ModelsTab
-->

<template>
  <div v-if="stats" class="grid grid-cols-5 gap-4 mb-6">
    <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
      <div class="text-2xl font-bold text-[var(--color-text-primary)]">{{ stats.total_models || 0 }}</div>
      <div class="text-xs text-[var(--color-text-tertiary)]">{{ $t('features.aiEditorModels.totalModels') }}</div>
    </div>
    <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
      <div class="text-2xl font-bold text-green-600">{{ stats.active_models || 0 }}</div>
      <div class="text-xs text-[var(--color-text-tertiary)]">{{ $t('features.aiEditorModels.activeModels') }}</div>
    </div>
    <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
      <div class="text-2xl font-bold text-blue-600">{{ stats.providers || 0 }}</div>
      <div class="text-xs text-[var(--color-text-tertiary)]">{{ $t('features.aiEditorModels.providers') }}</div>
    </div>
    <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
      <div class="text-2xl font-bold text-purple-600">{{ stats.categories || 0 }}</div>
      <div class="text-xs text-[var(--color-text-tertiary)]">{{ $t('features.aiEditorModels.categories') }}</div>
    </div>
    <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4 text-center">
      <div class="text-2xl font-bold text-orange-600">{{ stats.default_models || 0 }}</div>
      <div class="text-xs text-[var(--color-text-tertiary)]">{{ $t('features.aiEditorModels.defaultModels') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ModelStats {
  total_models: number
  active_models: number
  providers: number
  categories: number
  default_models: number
}

defineProps<{
  stats: ModelStats | null
}>()
</script>
