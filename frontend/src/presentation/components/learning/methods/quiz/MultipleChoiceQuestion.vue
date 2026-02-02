<template>
  <div class="multiple-choice-question space-y-3">
    <div
      v-for="option in question.options"
      :key="option.id"
      class="flex items-center p-3 border rounded-lg cursor-pointer transition-all"
      :class="{
        'border-primary-500 bg-primary-50': isSelected(option.id),
        'border-gray-200 hover:border-gray-300 hover:bg-gray-50': !isSelected(option.id)
      }"
      @click="toggleOption(option.id)"
    >
      <div class="flex items-center flex-1">
        <!-- Checkbox -->
        <div
          class="flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center mr-3"
          :class="{
            'border-primary-500 bg-primary-500': isSelected(option.id),
            'border-gray-300': !isSelected(option.id)
          }"
        >
          <svg
            v-if="isSelected(option.id)"
            class="w-3 h-3 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="3"
              d="M5 13l4 4L19 7"
            />
          </svg>
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

    <p class="text-xs text-gray-500 mt-2">
      💡 {{ $t('lesson.quiz.multipleSelection') }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { QuizQuestion, QuizAnswerSubmission } from '@/application/services/api/learning'

const { t } = useI18n()

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

const selectedOptionIds = computed(() => {
  return props.modelValue?.selected_option_ids || []
})

// ============================================================================
// Methods
// ============================================================================

const isSelected = (optionId: string | number): boolean => {
  return selectedOptionIds.value.includes(optionId)
}

const toggleOption = (optionId: string | number): void => {
  let newSelection: (string | number)[]

  if (isSelected(optionId)) {
    // Remove option
    newSelection = selectedOptionIds.value.filter(id => id !== optionId)
  } else {
    // Add option
    newSelection = [...selectedOptionIds.value, optionId]
  }

  emit('update:modelValue', {
    question_id: props.question.question_id,
    selected_option_ids: newSelection
  })
}
</script>
