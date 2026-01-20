<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Mathe-Interaktiv
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Mathematikaufgaben mit schrittweiser Eingabe und Feedback
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgabenstellung
          </label>
          <textarea
            v-model="methodData.instruction"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Beschreiben Sie die mathematische Aufgabe..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Mathematik-Bereich
          </label>
          <select
            v-model="methodData.math_area"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Bereich wählen...</option>
            <option value="arithmetic">Grundrechenarten</option>
            <option value="algebra">Algebra</option>
            <option value="geometry">Geometrie</option>
            <option value="calculus">Analysis/Calculus</option>
            <option value="statistics">Statistik</option>
            <option value="linear_algebra">Lineare Algebra</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Formel / Gleichung (LaTeX)
          </label>
          <textarea
            v-model="methodData.formula"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            placeholder="z.B. \frac{x^2 + 2x}{3} = 5"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Lösungsschritte
          </label>
          <div class="space-y-2">
            <div
              v-for="(step, index) in methodData.solution_steps"
              :key="index"
              class="flex items-center space-x-2"
            >
              <span class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full text-sm font-medium">
                {{ index + 1 }}
              </span>
              <input
                v-model="methodData.solution_steps[index]"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Lösungsschritt..."
                required
              />
              <button
                type="button"
                @click="removeStep(index)"
                class="text-red-600 hover:text-red-800"
                :disabled="methodData.solution_steps.length <= 1"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <button
            type="button"
            @click="addStep"
            class="mt-2 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            + Schritt hinzufügen
          </button>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Endergebnis
          </label>
          <input
            v-model="methodData.final_answer"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="z.B. x = 5"
            required
          />
        </div>

        <div class="space-y-2">
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.step_by_step"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Schrittweise Eingabe
            </span>
          </label>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.show_hints"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Hinweise anzeigen
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import { BaseLearningMethodForm } from '@/presentation/components/content/admin/learning-methods/forms'

const METHOD_CODE = 12

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  instruction: string
  math_area: string
  formula: string
  solution_steps: string[]
  final_answer: string
  step_by_step: boolean
  show_hints: boolean
}>({
  instruction: '',
  math_area: '',
  formula: '',
  solution_steps: [''],
  final_answer: '',
  step_by_step: true,
  show_hints: true
})

const addStep = () => {
  methodData.value.solution_steps.push('')
}

const removeStep = (index: number) => {
  if (methodData.value.solution_steps.length > 1) {
    methodData.value.solution_steps.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      instruction: existingData.instruction || '',
      math_area: existingData.math_area || '',
      formula: existingData.formula || '',
      solution_steps: existingData.solution_steps || [''],
      final_answer: existingData.final_answer || '',
      step_by_step: existingData.step_by_step !== undefined ? existingData.step_by_step : true,
      show_hints: existingData.show_hints !== undefined ? existingData.show_hints : true
    }
  }
})
</script>
