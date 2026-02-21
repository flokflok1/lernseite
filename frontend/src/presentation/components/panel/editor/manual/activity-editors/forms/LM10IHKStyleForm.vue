<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

const pre = 'panel.manualEditor.activityEditor.lm10'

type Criterion = { text: string; points?: number }

const questionTypes = ['situational', 'case_study', 'analysis', 'evaluation'] as const

const questionType = computed({
  get: () => (props.modelValue.question_type as string) ?? 'situational',
  set: (v) => emit('update:modelValue', { ...props.modelValue, question_type: v })
})

const questionText = computed({
  get: () => (props.modelValue.question_text as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, question_text: v })
})

const context = computed({
  get: () => (props.modelValue.context as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, context: v })
})

const criteria = computed({
  get: () => (props.modelValue.criteria as Criterion[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, criteria: v })
})

const defaultCriterion = (): Criterion => ({ text: '', points: undefined })
</script>

<template>
  <div class="lm-form">
    <div class="lm-field">
      <label>{{ t(`${pre}.questionType`) }}</label>
      <select v-model="questionType" class="lm-input">
        <option v-for="qt in questionTypes" :key="qt" :value="qt">{{ qt }}</option>
      </select>
    </div>

    <div class="lm-field">
      <label>{{ t(`${pre}.questionText`) }}</label>
      <textarea v-model="questionText" class="lm-textarea" rows="3" />
    </div>

    <div class="lm-field">
      <label>{{ t(`${pre}.context`) }}</label>
      <textarea v-model="context" class="lm-textarea" rows="3" />
    </div>

    <ArrayItemEditor
      v-model="criteria"
      :default-item="defaultCriterion"
      :label="t(`${pre}.criteria`)"
    >
      <template #default="{ item, update }">
        <div class="lm-field">
          <label>{{ t(`${pre}.criterionText`) }}</label>
          <input
            :value="item.text"
            @input="update({ ...item, text: ($event.target as HTMLInputElement).value })"
            class="lm-input"
          />
        </div>
        <div class="lm-field">
          <label>{{ t(`${pre}.criterionPoints`) }}</label>
          <input
            :value="item.points ?? ''"
            type="number"
            min="0"
            @input="update({ ...item, points: Number(($event.target as HTMLInputElement).value) || undefined })"
            class="lm-input"
          />
        </div>
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
