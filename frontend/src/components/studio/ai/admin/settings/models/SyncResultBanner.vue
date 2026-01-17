<!--
  SyncResultBanner - Sync Operation Result Display
  Sub-component of ModelsTab
-->

<template>
  <div
    v-if="result"
    class="mb-6 p-4 rounded-xl"
    :class="result.success ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'"
  >
    <div class="flex items-center gap-2">
      <span>{{ result.success ? '✅' : '❌' }}</span>
      <span :class="result.success ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
        {{ result.message }}
      </span>
    </div>
    <div v-if="result.details" class="mt-2 text-sm text-[var(--color-text-secondary)]">
      {{ $t('features.aiEditorModels.added') }}: {{ result.details.added || 0 }} |
      {{ $t('features.aiEditorModels.updated') }}: {{ result.details.updated || 0 }} |
      {{ $t('features.aiEditorModels.total') }}: {{ result.details.synced || 0 }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface SyncResult {
  success: boolean
  message: string
  details?: {
    added?: number
    updated?: number
    synced?: number
  }
}

defineProps<{
  result: SyncResult | null
}>()
</script>
