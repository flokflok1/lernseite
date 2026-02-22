/**
 * InlineErrorBanner.vue
 *
 * Lightweight inline error banner for the Manual Editor.
 * Used by ManualEditorContainerView, CourseInfoPanel, LessonActivitiesSection.
 * Accepts optional hint text and inherits class/style for positioning overrides.
 */

<script setup lang="ts">
defineProps<{
  message: string | null
  hint?: string | null
}>()

const emit = defineEmits<{
  dismiss: []
}>()
</script>

<template>
  <div v-if="message" class="inline-error-banner" role="alert">
    <span class="inline-error-text">{{ message }}</span>
    <span v-if="hint" class="inline-error-hint">{{ hint }}</span>
    <button class="inline-error-dismiss" :aria-label="$t('panel.manualEditor.toolbar.dismiss')" @click="emit('dismiss')">&times;</button>
  </div>
</template>

<style scoped>
.inline-error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 12px;
  font-size: 12px;
  color: var(--color-error);
  background: color-mix(in srgb, var(--color-error) 10%, var(--color-surface));
  border: 1px solid color-mix(in srgb, var(--color-error) 25%, transparent);
  border-radius: 4px;
}

.inline-error-text {
  flex: 1;
}

.inline-error-hint {
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.inline-error-dismiss {
  background: none;
  border: none;
  color: var(--color-error);
  cursor: pointer;
  font-size: 14px;
  padding: 0 2px;
  line-height: 1;
  flex-shrink: 0;
}

.inline-error-dismiss:hover {
  opacity: 0.7;
}
</style>
