<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

type Section = { title: string; content: string; question?: string; answer?: string }

const sections = computed({
  get: () => (props.modelValue.sections as Section[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, sections: v })
})

const defaultSection = (): Section => ({ title: '', content: '', question: '', answer: '' })
</script>

<template>
  <div class="lm-form">
    <ArrayItemEditor
      v-model="sections"
      :default-item="defaultSection"
      :label="t('panel.manualEditor.activityEditor.lm02.sections')"
    >
      <template #default="{ item, update }">
        <input :value="item.title" @input="update({ ...item, title: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm02.sectionTitle')" />
        <textarea :value="item.content" @input="update({ ...item, content: ($event.target as HTMLTextAreaElement).value })" class="lm-textarea" rows="2" :placeholder="t('panel.manualEditor.activityEditor.lm02.sectionContent')" />
        <input :value="item.question ?? ''" @input="update({ ...item, question: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm02.sectionQuestion')" />
        <input :value="item.answer ?? ''" @input="update({ ...item, answer: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm02.sectionAnswer')" />
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
