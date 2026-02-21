<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

const pre = 'panel.manualEditor.activityEditor.lm11'

type Step = { title: string; description: string; points?: number; rubric?: string }

const steps = computed({
  get: () => (props.modelValue.steps as Step[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, steps: v })
})

const defaultStep = (): Step => ({ title: '', description: '', points: undefined, rubric: '' })
</script>

<template>
  <div class="lm-form">
    <ArrayItemEditor
      v-model="steps"
      :default-item="defaultStep"
      :label="t(`${pre}.steps`)"
    >
      <template #default="{ item, update }">
        <div class="lm-field">
          <label>{{ t(`${pre}.stepTitle`) }}</label>
          <input
            :value="item.title"
            @input="update({ ...item, title: ($event.target as HTMLInputElement).value })"
            class="lm-input"
          />
        </div>
        <div class="lm-field">
          <label>{{ t(`${pre}.stepDescription`) }}</label>
          <textarea
            :value="item.description"
            @input="update({ ...item, description: ($event.target as HTMLTextAreaElement).value })"
            class="lm-textarea"
            rows="2"
          />
        </div>
        <div class="lm-field">
          <label>{{ t(`${pre}.stepPoints`) }}</label>
          <input
            :value="item.points ?? ''"
            type="number"
            min="0"
            @input="update({ ...item, points: Number(($event.target as HTMLInputElement).value) || undefined })"
            class="lm-input"
          />
        </div>
        <div class="lm-field">
          <label>{{ t(`${pre}.stepRubric`) }}</label>
          <textarea
            :value="item.rubric ?? ''"
            @input="update({ ...item, rubric: ($event.target as HTMLTextAreaElement).value })"
            class="lm-textarea"
            rows="2"
          />
        </div>
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
