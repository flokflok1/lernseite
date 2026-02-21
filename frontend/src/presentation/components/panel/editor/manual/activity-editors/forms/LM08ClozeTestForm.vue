<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'
import TagListInput from '../primitives/TagListInput.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

const pre = 'panel.manualEditor.activityEditor.lm08'

type Blank = { answer: string; alternatives: string[] }

const text = computed({
  get: () => (props.modelValue.text as string) ?? '',
  set: (v) => emit('update:modelValue', { ...props.modelValue, text: v })
})

const blanks = computed({
  get: () => (props.modelValue.blanks as Blank[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, blanks: v })
})

const defaultBlank = (): Blank => ({ answer: '', alternatives: [] })
</script>

<template>
  <div class="lm-form">
    <div class="lm-field">
      <label>{{ t(`${pre}.text`) }}</label>
      <textarea v-model="text" class="lm-textarea" rows="4" />
    </div>

    <ArrayItemEditor
      v-model="blanks"
      :default-item="defaultBlank"
      :label="t(`${pre}.blanks`)"
    >
      <template #default="{ item, update }">
        <div class="lm-field">
          <label>{{ t(`${pre}.blankAnswer`) }}</label>
          <input
            :value="item.answer"
            @input="update({ ...item, answer: ($event.target as HTMLInputElement).value })"
            class="lm-input"
          />
        </div>
        <div class="lm-field">
          <label>{{ t(`${pre}.blankAlternatives`) }}</label>
          <TagListInput
            :model-value="item.alternatives"
            @update:model-value="update({ ...item, alternatives: $event })"
          />
        </div>
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
