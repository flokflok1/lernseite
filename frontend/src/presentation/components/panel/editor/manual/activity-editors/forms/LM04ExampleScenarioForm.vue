<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

type Scenario = { title: string; situation: string; solution: string; takeaway?: string }

const scenarios = computed({
  get: () => (props.modelValue.scenarios as Scenario[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, scenarios: v })
})

const defaultScenario = (): Scenario => ({ title: '', situation: '', solution: '', takeaway: '' })
</script>

<template>
  <div class="lm-form">
    <ArrayItemEditor
      v-model="scenarios"
      :default-item="defaultScenario"
      :label="t('panel.manualEditor.activityEditor.lm04.scenarios')"
    >
      <template #default="{ item, update }">
        <input :value="item.title" @input="update({ ...item, title: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm04.scenarioTitle')" />
        <textarea :value="item.situation" @input="update({ ...item, situation: ($event.target as HTMLTextAreaElement).value })" class="lm-textarea" rows="3" :placeholder="t('panel.manualEditor.activityEditor.lm04.scenarioSituation')" />
        <textarea :value="item.solution" @input="update({ ...item, solution: ($event.target as HTMLTextAreaElement).value })" class="lm-textarea" rows="3" :placeholder="t('panel.manualEditor.activityEditor.lm04.scenarioSolution')" />
        <input :value="item.takeaway ?? ''" @input="update({ ...item, takeaway: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm04.scenarioTakeaway')" />
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
