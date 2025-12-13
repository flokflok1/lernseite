<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <div class="space-y-4">
        <!-- Prüfungstyp -->
        <div>
          <label for="exam_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Prüfungstyp
          </label>
          <select
            id="exam_type"
            v-model="methodData.exam_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Bitte wählen...</option>
            <option value="mixed">Gemischt (Multiple-Choice, Kurzantwort, Essay)</option>
            <option value="multiple_choice">Nur Multiple-Choice</option>
            <option value="short_answer">Nur Kurzantworten</option>
            <option value="essay">Nur Essay-Fragen</option>
            <option value="true_false">Nur Richtig/Falsch</option>
          </select>
        </div>

        <!-- Zeitlimit -->
        <div>
          <label for="time_limit" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Zeitlimit (Minuten)
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
            Gesamtzeit für die Prüfung (5-300 Minuten)
          </p>
        </div>

        <!-- Anzahl der Fragen -->
        <div>
          <label for="question_count" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Anzahl der Fragen
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
            Gesamtanzahl der Prüfungsfragen (1-100)
          </p>
        </div>

        <!-- Bestehensgrenze -->
        <div>
          <label for="passing_score" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Bestehensgrenze (%)
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
            Mindestprozentsatz zum Bestehen (0-100%)
          </p>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 22

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref({
  exam_type: '',
  time_limit: 60,
  question_count: 20,
  passing_score: 60
})

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
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
