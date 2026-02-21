<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ArrayItemEditor from '../primitives/ArrayItemEditor.vue'

const props = defineProps<{ modelValue: Record<string, unknown> }>()
const emit = defineEmits<{ 'update:modelValue': [value: Record<string, unknown>] }>()
const { t } = useI18n()

type Card = { front: string; back: string; hint?: string }

const cards = computed({
  get: () => (props.modelValue.cards as Card[]) ?? [],
  set: (v) => emit('update:modelValue', { ...props.modelValue, cards: v })
})

const defaultCard = (): Card => ({ front: '', back: '', hint: '' })
</script>

<template>
  <div class="lm-form">
    <ArrayItemEditor
      v-model="cards"
      :default-item="defaultCard"
      :label="t('panel.manualEditor.activityEditor.lm06.cards')"
    >
      <template #default="{ item, update }">
        <input :value="item.front" @input="update({ ...item, front: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm06.cardFront')" />
        <textarea :value="item.back" @input="update({ ...item, back: ($event.target as HTMLTextAreaElement).value })" class="lm-textarea" rows="2" :placeholder="t('panel.manualEditor.activityEditor.lm06.cardBack')" />
        <input :value="item.hint ?? ''" @input="update({ ...item, hint: ($event.target as HTMLInputElement).value })" class="lm-input" :placeholder="t('panel.manualEditor.activityEditor.lm06.cardHint')" />
      </template>
    </ArrayItemEditor>
  </div>
</template>

<style src="./lm-form.css" scoped />
