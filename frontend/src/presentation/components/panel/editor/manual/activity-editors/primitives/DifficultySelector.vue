/**
 * DifficultySelector.vue
 *
 * Three-option difficulty selector: easy / medium / hard
 */
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
const { t } = useI18n()

const levels = ['easy', 'medium', 'hard'] as const
</script>

<template>
  <div class="difficulty-selector">
    <button
      v-for="level in levels"
      :key="level"
      class="diff-btn"
      :class="{ 'diff-btn--active': modelValue === level }"
      @click="emit('update:modelValue', level)"
    >
      {{ t(`panel.manualEditor.activityEditor.difficulty.${level}`) }}
    </button>
  </div>
</template>

<style scoped>
.difficulty-selector {
  display: flex;
  gap: 4px;
}

.diff-btn {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.diff-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.diff-btn--active {
  background: color-mix(in srgb, var(--color-accent) 15%, transparent);
  border-color: var(--color-accent);
  color: var(--color-accent);
  font-weight: 600;
}
</style>
