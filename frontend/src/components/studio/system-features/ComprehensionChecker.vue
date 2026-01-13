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
            Fehleranalyse
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Fehler in Code/Konfiguration finden und beheben
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aufgabenstellung
          </label>
          <textarea
            v-model="methodData.instruction"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Beschreiben Sie, was der Lernende analysieren soll..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Fehler-Typ
          </label>
          <select
            v-model="methodData.error_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Typ wählen...</option>
            <option value="syntax">Syntax-Fehler</option>
            <option value="logic">Logik-Fehler</option>
            <option value="runtime">Laufzeit-Fehler</option>
            <option value="config">Konfigurations-Fehler</option>
            <option value="security">Sicherheits-Lücke</option>
            <option value="performance">Performance-Problem</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Code/Konfiguration mit Fehler(n)
          </label>
          <textarea
            v-model="methodData.code_with_errors"
            rows="10"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            placeholder="// Code mit absichtlichen Fehlern..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Fehler-Beschreibungen (einer pro Zeile)
          </label>
          <textarea
            v-model="methodData.error_descriptions"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Zeile 5: Fehlender Semikolon&#10;Zeile 12: Falsche Variable verwendet&#10;Zeile 20: Off-by-one Fehler"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Korrigierter Code (Musterlösung)
          </label>
          <textarea
            v-model="methodData.corrected_code"
            rows="10"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            placeholder="// Korrekter Code..."
            required
          ></textarea>
        </div>

        <div class="space-y-2">
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.show_hints"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Hinweise bei Bedarf anzeigen
            </span>
          </label>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.show_line_numbers"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              Zeilennummern anzeigen
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/store/modules/desktop'
import { BaseLearningMethodForm } from '@/components/base/content/admin/learning-methods/forms'

const METHOD_CODE = 16

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  instruction: string
  error_type: string
  code_with_errors: string
  error_descriptions: string
  corrected_code: string
  show_hints: boolean
  show_line_numbers: boolean
}>({
  instruction: '',
  error_type: '',
  code_with_errors: '',
  error_descriptions: '',
  corrected_code: '',
  show_hints: true,
  show_line_numbers: true
})

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      instruction: existingData.instruction || '',
      error_type: existingData.error_type || '',
      code_with_errors: existingData.code_with_errors || '',
      error_descriptions: existingData.error_descriptions || '',
      corrected_code: existingData.corrected_code || '',
      show_hints: existingData.show_hints !== undefined ? existingData.show_hints : true,
      show_line_numbers: existingData.show_line_numbers !== undefined ? existingData.show_line_numbers : true
    }
  }
})
</script>
