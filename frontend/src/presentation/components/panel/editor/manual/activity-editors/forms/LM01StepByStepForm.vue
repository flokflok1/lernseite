<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

type Step = { title: string; content: string; hint?: string }

const steps = computed({
  get: () => (props.modelValue.steps as Step[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, steps: v })
})

const defaultStep = (): Step => ({ title: '', content: '', hint: '' })
</script>

<template>
  <div class="lm-form">
    <ArrayItemEditor
      v-model="steps"
      :default-item="defaultStep"
      :label="t('panel.manualEditor.activityEditor.lm01.steps')"
    >
      <template #default="{ item, update }">
        <input :value="item.title" @input="update({ ...item, title: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm01.stepTitle')" />
        <textarea :value="item.content" @input="update({ ...item, content: ($event.target as HTMLTextAreaElement).value })" class="lm-textarea" rows="2" :placeholder="t('panel.manualEditor.activityEditor.lm01.stepContent')" />
        <input :value="item.hint ?? ''" @input="update({ ...item, hint: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm01.stepHint')" />
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
