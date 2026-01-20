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
            IT-Szenario lösen
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Komplexe, mehrstufige IT-Case-Studies
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Szenario-Titel
          </label>
          <input
            v-model="methodData.title"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="z.B. Netzwerkausfall im Unternehmen"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ausgangssituation
          </label>
          <textarea
            v-model="methodData.scenario"
            rows="5"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Beschreiben Sie die IT-Situation und das Problem..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            IT-Bereich
          </label>
          <select
            v-model="methodData.it_area"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Bereich wählen...</option>
            <option value="network">Netzwerk</option>
            <option value="security">IT-Sicherheit</option>
            <option value="server">Server-Administration</option>
            <option value="database">Datenbank</option>
            <option value="cloud">Cloud Computing</option>
            <option value="devops">DevOps</option>
            <option value="helpdesk">Helpdesk/Support</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgaben / Schritte
          </label>
          <div class="space-y-3">
            <div
              v-for="(step, index) in methodData.steps"
              :key="index"
              class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Schritt {{ index + 1 }}
                </span>
                <button
                  type="button"
                  @click="removeStep(index)"
                  class="text-red-600 hover:text-red-800"
                  :disabled="methodData.steps.length <= 1"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <textarea
                v-model="step.description"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white mb-2"
                placeholder="Aufgabenbeschreibung..."
                required
              ></textarea>
              <textarea
                v-model="step.expected_answer"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
                placeholder="Erwartete Lösung..."
              ></textarea>
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
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.allow_hints"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Hinweise bei Bedarf anzeigen
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 11

interface Step {
  description: string
  expected_answer: string
}

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  title: string
  scenario: string
  it_area: string
  steps: Step[]
  allow_hints: boolean
}>({
  title: '',
  scenario: '',
  it_area: '',
  steps: [{ description: '', expected_answer: '' }],
  allow_hints: true
})

const addStep = () => {
  methodData.value.steps.push({ description: '', expected_answer: '' })
}

const removeStep = (index: number) => {
  if (methodData.value.steps.length > 1) {
    methodData.value.steps.splice(index, 1)
  }
}

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      title: existingData.title || '',
      scenario: existingData.scenario || '',
      it_area: existingData.it_area || '',
      steps: existingData.steps || [{ description: '', expected_answer: '' }],
      allow_hints: existingData.allow_hints !== undefined ? existingData.allow_hints : true
    }
  }
})
</script>
