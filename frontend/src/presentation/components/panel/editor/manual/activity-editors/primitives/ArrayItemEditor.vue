/**
 * ArrayItemEditor.vue
 *
 * Generic array editor: add/remove/reorder items with scoped slot for item content.
 */
<script setup lang="ts" generic="T extends Record<string, unknown>">
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  modelValue: T[]
  defaultItem: () => T
  label?: string
  maxItems?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: T[]]
}>()

const { t } = useI18n()

const addItem = () => {
  if (props.maxItems && props.modelValue.length >= props.maxItems) return
  emit('update:modelValue', [...props.modelValue, props.defaultItem()])
}

const removeItem = (index: number) => {
  const arr = [...props.modelValue]
  arr.splice(index, 1)
  emit('update:modelValue', arr)
}

const moveUp = (index: number) => {
  if (index <= 0) return
  const arr = [...props.modelValue]
  ;[arr[index - 1], arr[index]] = [arr[index], arr[index - 1]]
  emit('update:modelValue', arr)
}

const moveDown = (index: number) => {
  if (index >= props.modelValue.length - 1) return
  const arr = [...props.modelValue]
  ;[arr[index], arr[index + 1]] = [arr[index + 1], arr[index]]
  emit('update:modelValue', arr)
}

const updateItem = (index: number, updated: T) => {
  const arr = [...props.modelValue]
  arr[index] = updated
  emit('update:modelValue', arr)
}
</script>

<template>
  <div class="array-editor">
    <div v-if="label" class="array-editor-label">{{ label }}</div>
    <div v-for="(item, idx) in modelValue" :key="idx" class="array-item">
      <div class="array-item-controls">
        <span class="array-item-index">#{{ idx + 1 }}</span>
        <button class="arr-btn" :disabled="idx === 0" @click="moveUp(idx)" :title="t('panel.manualEditor.activityEditor.arrayEditor.moveUp')">&#x25B2;</button>
        <button class="arr-btn" :disabled="idx === modelValue.length - 1" @click="moveDown(idx)" :title="t('panel.manualEditor.activityEditor.arrayEditor.moveDown')">&#x25BC;</button>
        <button class="arr-btn arr-btn--delete" @click="removeItem(idx)" :title="t('panel.manualEditor.activityEditor.arrayEditor.remove')">&times;</button>
      </div>
      <div class="array-item-content">
        <slot :item="item" :index="idx" :update="(val: T) => updateItem(idx, val)" />
      </div>
    </div>
    <button
      class="arr-add-btn"
      :disabled="maxItems !== undefined && modelValue.length >= maxItems"
      @click="addItem"
    >
      + {{ t('panel.manualEditor.activityEditor.arrayEditor.add') }}
    </button>
  </div>
</template>

<style scoped>
.array-editor {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.array-editor-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.array-item {
  display: flex;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
}

.array-item-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 24px;
}

.array-item-index {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-text-tertiary);
}

.arr-btn {
  background: none;
  border: none;
  font-size: 10px;
  cursor: pointer;
  padding: 1px 4px;
  color: var(--color-text-tertiary);
  border-radius: 2px;
}

.arr-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--color-accent) 10%, transparent);
  color: var(--color-accent);
}

.arr-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

.arr-btn--delete:hover:not(:disabled) {
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
  color: var(--color-error);
}

.array-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.arr-add-btn {
  width: 100%;
  padding: 5px;
  border: 1px dashed var(--color-border);
  border-radius: 4px;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 12px;
  cursor: pointer;
}

.arr-add-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.arr-add-btn:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
