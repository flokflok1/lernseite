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
            Whiteboard-Aufgabe
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Zeichenaufgaben auf digitalem Whiteboard mit KI-Analyse
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
            placeholder="Beschreiben Sie, was der Lernende zeichnen/skizzieren soll..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgabentyp
          </label>
          <select
            v-model="methodData.task_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Typ wählen...</option>
            <option value="diagram">Diagramm erstellen</option>
            <option value="flowchart">Flowchart zeichnen</option>
            <option value="network">Netzwerkskizze</option>
            <option value="uml">UML-Diagramm</option>
            <option value="mindmap">Mindmap erstellen</option>
            <option value="architecture">Architekturdiagramm</option>
            <option value="freeform">Freie Zeichnung</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Erwartete Elemente (eines pro Zeile)
          </label>
          <textarea
            v-model="methodData.expected_elements"
            rows="5"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Server&#10;Datenbank&#10;Client&#10;Firewall&#10;Verbindungslinien"
          ></textarea>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Die KI prüft, ob diese Elemente in der Zeichnung vorhanden sind
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Bewertungskriterien
          </label>
          <div class="space-y-2">
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.check_completeness"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                Vollständigkeit prüfen (alle erwarteten Elemente vorhanden)
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.check_connections"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                Verbindungen/Relationen prüfen
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.check_labels"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                Beschriftungen prüfen
              </span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Referenzbild (optional)
          </label>
          <input
            v-model="methodData.reference_image"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="URL zum Referenzbild..."
          />
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Optional: Musterlösung oder Orientierungsbild
          </p>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.allow_ai_feedback"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              KI-Feedback aktivieren (Analyse der Zeichnung)
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
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 8

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  instruction: string
  task_type: string
  expected_elements: string
  check_completeness: boolean
  check_connections: boolean
  check_labels: boolean
  reference_image: string
  allow_ai_feedback: boolean
}>({
  instruction: '',
  task_type: '',
  expected_elements: '',
  check_completeness: true,
  check_connections: true,
  check_labels: false,
  reference_image: '',
  allow_ai_feedback: true
})

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      instruction: existingData.instruction || '',
      task_type: existingData.task_type || '',
      expected_elements: existingData.expected_elements || '',
      check_completeness: existingData.check_completeness !== undefined ? existingData.check_completeness : true,
      check_connections: existingData.check_connections !== undefined ? existingData.check_connections : true,
      check_labels: existingData.check_labels !== undefined ? existingData.check_labels : false,
      reference_image: existingData.reference_image || '',
      allow_ai_feedback: existingData.allow_ai_feedback !== undefined ? existingData.allow_ai_feedback : true
    }
  }
})
</script>
