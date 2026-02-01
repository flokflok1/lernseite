<template>
  <div class="textarea-group">
    <label v-if="label" :for="id" class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <textarea
      :id="id"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :rows="rows"
      :maxlength="maxlength"
      :class="textareaClasses"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    />
    <div v-if="maxlength" class="mt-1 text-xs text-[var(--color-text-secondary)] text-right">
      {{ currentLength }} / {{ maxlength }}
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">
      {{ error }}
    </p>
    <p v-else-if="hint" class="mt-1 text-sm text-[var(--color-text-secondary)]">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  id?: string
  label?: string
  modelValue?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  rows?: number
  maxlength?: number
  error?: string
  hint?: string
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}

const props = withDefaults(defineProps<Props>(), {
  rows: 4,
  required: false,
  disabled: false,
  resize: 'vertical',
})

defineEmits<{
  'update:modelValue': [value: string]
  blur: []
  focus: []
}>()

const currentLength = computed(() => {
  return props.modelValue?.length || 0
})

const textareaClasses = computed(() => {
  return [
    'textarea-field',
    `resize-${props.resize}`,
    {
      'textarea-error': props.error,
      'opacity-50 cursor-not-allowed': props.disabled,
    },
  ]
})
</script>

<style scoped>
.textarea-field {
  @apply w-full px-3 py-2 border border-[var(--color-border)] rounded-md;
  @apply focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent;
  @apply transition-colors;
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.textarea-error {
  @apply border-red-500 focus:ring-red-500;
}

.resize-none { resize: none; }
.resize-vertical { resize: vertical; }
.resize-horizontal { resize: horizontal; }
.resize-both { resize: both; }
</style>
