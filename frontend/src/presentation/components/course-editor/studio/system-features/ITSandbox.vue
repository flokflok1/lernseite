<template>
  <BaseLearningMethodForm
    :panel="panel"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <div class="space-y-4">
        <!-- Prüfungstyp -->
        <div>
          <label for="exam_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ $t('features.learningMethods.lm22.examTypeLabel') }}
          </label>
          <select
            id="exam_type"
            v-model="methodData.exam_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">{{ $t('features.learningMethods.lm22.examTypeDefault') }}</option>
            <option value="mixed">{{ $t('features.learningMethods.lm22.examTypeMixed') }}</option>
            <option value="multiple_choice">{{ $t('features.learningMethods.lm22.examTypeMultipleChoice') }}</option>
            <option value="short_answer">{{ $t('features.learningMethods.lm22.examTypeShortAnswer') }}</option>
            <option value="essay">{{ $t('features.learningMethods.lm22.examTypeEssay') }}</option>
            <option value="true_false">{{ $t('features.learningMethods.lm22.examTypeTrueFalse') }}</option>
          </select>
        </div>

        <!-- Zeitlimit -->
        <div>
          <label for="time_limit" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ $t('features.learningMethods.lm22.timeLimitLabel') }}
          </label>
          <input
            id="time_limit"
            v-model.number="methodData.time_limit"
            type="number"
            min="5"
            max="300"
            step="5"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            required
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ $t('features.learningMethods.lm22.timeLimitHint') }}
          </p>
        </div>

        <!-- Anzahl der Fragen -->
        <div>
          <label for="question_count" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ $t('features.learningMethods.lm22.questionCountLabel') }}
          </label>
          <input
            id="question_count"
            v-model.number="methodData.question_count"
            type="number"
            min="1"
            max="100"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            required
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ $t('features.learningMethods.lm22.questionCountHint') }}
          </p>
        </div>

        <!-- Bestehensgrenze -->
        <div>
          <label for="passing_score" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ $t('features.learningMethods.lm22.passingScoreLabel') }}
          </label>
          <div class="flex gap-4 items-center">
            <input
              id="passing_score"
              v-model.number="methodData.passing_score"
              type="number"
              min="0"
              max="100"
              class="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              required
            />
            <span class="text-sm text-gray-600 dark:text-gray-400">%</span>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {{ $t('features.learningMethods.lm22.passingScoreHint') }}
          </p>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/store/modules/desktop'
import { BaseLearningMethodForm } from '@/components/base/content/admin/learning-methods/forms'

const { t } = useI18n()

const METHOD_CODE = 22

interface Props {
  panel: LsxPanel
}

const props = defineProps<Props>()

const methodData = ref({
  exam_type: '',
  time_limit: 60,
  question_count: 20,
  passing_score: 60
})

onMounted(() => {
  const existingData = props.panel.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      exam_type: existingData.exam_type || '',
      time_limit: existingData.time_limit || 60,
      question_count: existingData.question_count || 20,
      passing_score: existingData.passing_score || 60
    }
  }
})
</script>
