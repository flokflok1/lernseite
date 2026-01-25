<template>
  <div class="single-choice-question space-y-3">
    <div
      v-for="option in question.options"
      :key="option.id"
      class="flex items-center p-3 border rounded-lg cursor-pointer transition-all"
      :class="{
        'border-primary-500 bg-primary-50': isSelected(option.id),
        'border-gray-200 hover:border-gray-300 hover:bg-gray-50': !isSelected(option.id)
      }"
      @click="selectOption(option.id)"
    >
      <div class="flex items-center flex-1">
        <!-- Radio Button -->
        <div
          class="flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center mr-3"
          :class="{
            'border-primary-500 bg-primary-500': isSelected(option.id),
            'border-gray-300': !isSelected(option.id)
          }"
        >
          <div v-if="isSelected(option.id)" class="w-2 h-2 bg-white rounded-full"></div>
        </div>

        <!-- Option Text -->
        <span
          class="text-sm"
          :class="{
            'text-gray-900 font-medium': isSelected(option.id),
            'text-gray-700': !isSelected(option.id)
          }"
        >
          {{ option.text }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { QuizQuestion, QuizAnswerSubmission } from '@/application/services/api/learning'

// ============================================================================
// Props & Emits
// ============================================================================

interface Props {
  question: QuizQuestion
  modelValue?: QuizAnswerSubmission
}

interface Emits {
  (e: 'update:modelValue', value: QuizAnswerSubmission): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ============================================================================
// Computed
// ============================================================================

const selectedOptionId = computed(() => {
  return props.modelValue?.selected_option_ids?.[0]
})

// ============================================================================
// Methods
// ============================================================================

const isSelected = (optionId: string | number): boolean => {
  return selectedOptionId.value === optionId
}

const selectOption = (optionId: string | number): void => {
  emit('update:modelValue', {
    question_id: props.question.question_id,
    selected_option_ids: [optionId]
  })
}
</script>
