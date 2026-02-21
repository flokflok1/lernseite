<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

type Element = { label: string; description?: string }

const diagramType = computed({
  get: () => (props.modelValue.diagram_type as string) ?? 'flowchart',
  set: (v) => emit('update:modelValue', { ...props.modelValue, diagram_type: v })
})
const description = computed({
  get: () => (props.modelValue.description as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, description: v })
})
const diagramCode = computed({
  get: () => (props.modelValue.diagram_code as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, diagram_code: v })
})
const elements = computed({
  get: () => (props.modelValue.elements as Element[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, elements: v })
})

const diagramTypes = ['flowchart', 'sequence', 'class', 'er', 'mindmap'] as const

const defaultElement = (): Element => ({ label: '', description: '' })
</script>

<template>
  <div class="lm-form">
    <div class="lm-field">
      <label>{{ t('panel.manualEditor.activityEditor.lm03.diagramType') }}</label>
      <select v-model="diagramType" class="lm-input">
        <option v-for="dtype in diagramTypes" :key="dtype" :value="dtype">{{ dtype }}</option>
      </select>
    </div>
    <div class="lm-field">
      <label>{{ t('panel.manualEditor.activityEditor.lm03.description') }}</label>
      <textarea v-model="description" class="lm-textarea" rows="3" />
    </div>
    <div class="lm-field">
      <label>{{ t('panel.manualEditor.activityEditor.lm03.diagramCode') }}</label>
      <textarea v-model="diagramCode" class="lm-textarea lm-code" rows="6" />
    </div>
    <ArrayItemEditor
      v-model="elements"
      :default-item="defaultElement"
      :label="t('panel.manualEditor.activityEditor.lm03.elements')"
    >
      <template #default="{ item, update }">
        <input :value="item.label" @input="update({ ...item, label: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm03.elementLabel')" />
        <input :value="item.description ?? ''" @input="update({ ...item, description: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm03.elementDescription')" />
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
