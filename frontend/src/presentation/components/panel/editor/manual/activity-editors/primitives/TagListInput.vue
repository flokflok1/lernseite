/**
 * TagListInput.vue
 *
 * Input for managing a string[] as tag chips. Enter to add, click X to remove.
 */
<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  modelValue: string[]
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const { t } = useI18n()
const inputVal = ref('')

const addTag = () => {
  const tag = inputVal.value.trim()
  if (!tag || props.modelValue.includes(tag)) return
  emit('update:modelValue', [...props.modelValue, tag])
  inputVal.value = ''
}

const removeTag = (index: number) => {
  const arr = [...props.modelValue]
  arr.splice(index, 1)
  emit('update:modelValue', arr)
}
</script>

<template>
  <div class="tag-list-input">
    <div v-if="modelValue.length > 0" class="tag-list">
      <span v-for="(tag, idx) in modelValue" :key="idx" class="tag-chip">
        {{ tag }}
        <button class="tag-remove" @click="removeTag(idx)">&times;</button>
      </span>
    </div>
    <input
      v-model="inputVal"
      type="text"
      class="tag-input"
      :placeholder="placeholder ?? t('panel.manualEditor.courseInfo.tagsHint')"
      @keydown.enter.prevent="addTag"
    />
  </div>
</template>

<style scoped>
.tag-list-input {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  font-size: 12px;
  background: color-mix(in srgb, var(--color-accent) 12%, transparent);
  color: var(--color-accent);
  border-radius: 12px;
}

.tag-remove {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0 2px;
  opacity: 0.7;
}

.tag-remove:hover {
  opacity: 1;
}

.tag-input {
  padding: 5px 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 13px;
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.tag-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 10%, transparent);
}
</style>
