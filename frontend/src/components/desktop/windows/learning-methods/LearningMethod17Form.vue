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
            Hands-on Lab
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Praktische Labor-Übungen mit virtueller Umgebung
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Lab-Titel
          </label>
          <input
            v-model="methodData.title"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="z.B. Linux Server Administration Lab"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Lab-Typ
          </label>
          <select
            v-model="methodData.lab_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Typ wählen...</option>
            <option value="linux">Linux/Unix Lab</option>
            <option value="windows">Windows Server Lab</option>
            <option value="network">Netzwerk Lab</option>
            <option value="cloud">Cloud Lab (AWS/Azure/GCP)</option>
            <option value="container">Container/Docker Lab</option>
            <option value="kubernetes">Kubernetes Lab</option>
            <option value="database">Datenbank Lab</option>
            <option value="security">Security Lab</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgabenbeschreibung
          </label>
          <textarea
            v-model="methodData.description"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Was soll der Lernende in dieser Lab-Übung erreichen?"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgaben-Schritte
          </label>
          <div class="space-y-2">
            <div
              v-for="(step, index) in methodData.steps"
              :key="index"
              class="flex items-center space-x-2"
            >
              <span class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300 rounded-full text-sm font-medium">
                {{ index + 1 }}
              </span>
              <input
                v-model="methodData.steps[index]"
                type="text"
                class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Aufgabenschritt..."
                required
              />
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
            Zeitlimit (Minuten)
          </label>
          <input
            v-model.number="methodData.time_limit"
            type="number"
            min="5"
            step="5"
            class="w-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="60"
          />
        </div>

        <div class="space-y-2">
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.allow_hints"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Hinweise erlauben
            </span>
          </label>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.auto_validate"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Automatische Validierung
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 17

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  title: string
  lab_type: string
  description: string
  steps: string[]
  time_limit: number
  allow_hints: boolean
  auto_validate: boolean
}>({
  title: '',
  lab_type: '',
  description: '',
  steps: [''],
  time_limit: 60,
  allow_hints: true,
  auto_validate: true
})

const addStep = () => {
  methodData.value.steps.push('')
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
      lab_type: existingData.lab_type || '',
      description: existingData.description || '',
      steps: existingData.steps || [''],
      time_limit: existingData.time_limit || 60,
      allow_hints: existingData.allow_hints !== undefined ? existingData.allow_hints : true,
      auto_validate: existingData.auto_validate !== undefined ? existingData.auto_validate : true
    }
  }
})
</script>
