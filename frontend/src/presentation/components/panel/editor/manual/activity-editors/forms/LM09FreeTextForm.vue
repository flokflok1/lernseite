<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

const pre = 'panel.manualEditor.activityEditor.lm09'

const question = computed({
  get: () => (props.modelValue.question as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, question: v })
})

const minWords = computed({
  get: () => (props.modelValue.min_words as number) ?? 0,
  set: (v) => emit('update:modelValue', { ...props.modelValue, min_words: v })
})

const maxWords = computed({
  get: () => (props.modelValue.max_words as number | undefined),
  set: (v) => emit('update:modelValue', { ...props.modelValue, max_words: v || undefined })
})

const rubric = computed({
  get: () => (props.modelValue.rubric as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, rubric: v })
})

const sampleAnswer = computed({
  get: () => (props.modelValue.sample_answer as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, sample_answer: v })
})
</script>

<template>
  <div class="lm-form">
    <div class="lm-field">
      <label>{{ t(`${pre}.question`) }}</label>
      <textarea v-model="question" class="lm-textarea" rows="3" />
    </div>

    <div class="lm-row">
      <div class="lm-field" style="flex: 1">
        <label>{{ t(`${pre}.minWords`) }}</label>
        <input v-model.number="minWords" type="number" min="0" class="lm-input" />
      </div>
      <div class="lm-field" style="flex: 1">
        <label>{{ t(`${pre}.maxWords`) }}</label>
        <input v-model.number="maxWords" type="number" min="0" class="lm-input" />
      </div>
    </div>

    <div class="lm-field">
      <label>{{ t(`${pre}.rubric`) }}</label>
      <textarea v-model="rubric" class="lm-textarea" rows="3" />
    </div>

    <div class="lm-field">
      <label>{{ t(`${pre}.sampleAnswer`) }}</label>
      <textarea v-model="sampleAnswer" class="lm-textarea" rows="3" />
    </div>
  </div>
</template>

<style src="./lm-form.css" scoped />
