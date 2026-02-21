<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import TagListInput from '../primitives/TagListInput.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

const content = computed({
  get: () => (props.modelValue.content as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, content: v })
})
const keyConcepts = computed({
  get: () => (props.modelValue.key_concepts as string[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, key_concepts: v })
})
const summary = computed({
  get: () => (props.modelValue.summary as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, summary: v })
})
</script>

<template>
  <div class="lm-form">
    <div class="lm-field">
      <label>{{ t('panel.manualEditor.activityEditor.lm00.content') }}</label>
      <textarea v-model="content" class="lm-textarea" rows="5" />
    </div>
    <div class="lm-field">
      <label>{{ t('panel.manualEditor.activityEditor.lm00.keyConcepts') }}</label>
      <TagListInput v-model="keyConcepts" />
    </div>
    <div class="lm-field">
      <label>{{ t('panel.manualEditor.activityEditor.lm00.summary') }}</label>
      <textarea v-model="summary" class="lm-textarea" rows="3" />
    </div>
  </div>
</template>

<style src="./lm-form.css" scoped />
