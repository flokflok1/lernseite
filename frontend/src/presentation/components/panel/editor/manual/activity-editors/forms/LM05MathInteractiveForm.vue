<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

type Problem = { text: string; formula?: string; solution: string; steps?: Array<{ description: string }> }

const problems = computed({
  get: () => (props.modelValue.problems as Problem[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, problems: v })
})

const defaultProblem = (): Problem => ({ text: '', formula: '', solution: '', steps: [] })

const stepsToText = (steps?: Array<{ description: string }>): string => {
  if (!steps || steps.length === 0) return ''
  return steps.map((s) => s.description).join('\n')
}

const textToSteps = (text: string): Array<{ description: string }> => {
  if (!text.trim()) return []
  return text.split('\n').filter((line) => line.trim()).map((line) => ({ description: line.trim() }))
}
</script>

<template>
  <div class="lm-form">
    <ArrayItemEditor
      v-model="problems"
      :default-item="defaultProblem"
      :label="t('panel.manualEditor.activityEditor.lm05.problems')"
    >
      <template #default="{ item, update }">
        <input :value="item.text" @input="update({ ...item, text: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm05.problemText')" />
        <input :value="item.formula ?? ''" @input="update({ ...item, formula: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm05.problemFormula')" />
        <input :value="item.solution" @input="update({ ...item, solution: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm05.problemSolution')" />
        <textarea :value="stepsToText(item.steps)" @input="update({ ...item, steps: textToSteps(($event.target as HTMLTextAreaElement).value) })" class="lm-textarea" rows="3" :placeholder="t('panel.manualEditor.activityEditor.lm05.problemSteps')" />
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
