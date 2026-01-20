<template>
  <div class="true-false-question flex gap-4">
    <!-- True Button -->
    <button
      class="flex-1 p-4 border-2 rounded-lg font-medium transition-all"
      :class="{
        'border-green-500 bg-green-50 text-green-900': selectedValue === true,
        'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50': selectedValue !== true
      }"
      @click="selectValue(true)"
    >
      <div class="flex items-center justify-center gap-2">
        <div
          class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
          :class="{
            'border-green-500 bg-green-500': selectedValue === true,
            'border-gray-300': selectedValue !== true
          }"
        >
          <div v-if="selectedValue === true" class="w-2 h-2 bg-white rounded-full"></div>
        </div>
        <span class="text-lg">✓ {{ $t('lesson.quiz.trueFalse.true') }}</span>
      </div>
    </button>

    <!-- False Button -->
    <button
      class="flex-1 p-4 border-2 rounded-lg font-medium transition-all"
      :class="{
        'border-red-500 bg-red-50 text-red-900': selectedValue === false,
        'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50': selectedValue !== false
      }"
      @click="selectValue(false)"
    >
      <div class="flex items-center justify-center gap-2">
        <div
          class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
          :class="{
            'border-red-500 bg-red-500': selectedValue === false,
            'border-gray-300': selectedValue !== false
          }"
        >
          <div v-if="selectedValue === false" class="w-2 h-2 bg-white rounded-full"></div>
        </div>
        <span class="text-lg">✗ {{ $t('lesson.quiz.trueFalse.false') }}</span>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import type { QuizQuestion, QuizAnswerSubmission } from '@/infrastructure/api/clients/learning'

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

const selectedValue = computed(() => {
  return props.modelValue?.answer_boolean
})

// ============================================================================
// Methods
// ============================================================================

const selectValue = (value: boolean): void => {
  emit('update:modelValue', {
    question_id: props.question.question_id,
    answer_boolean: value
  })
}
</script>
