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
            Code/IT-Config Sandbox
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            Interaktive Coding-/Konfigurations-Umgebung
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
            placeholder="Beschreiben Sie, was der Lernende programmieren/konfigurieren soll..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Programmiersprache / Konfigurationstyp
          </label>
          <select
            v-model="methodData.language"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">Typ wählen...</option>
            <optgroup label="Programmiersprachen">
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
              <option value="csharp">C#</option>
              <option value="php">PHP</option>
              <option value="ruby">Ruby</option>
              <option value="go">Go</option>
              <option value="rust">Rust</option>
            </optgroup>
            <optgroup label="Konfiguration">
              <option value="sql">SQL</option>
              <option value="bash">Bash/Shell</option>
              <option value="powershell">PowerShell</option>
              <option value="yaml">YAML</option>
              <option value="json">JSON</option>
              <option value="xml">XML</option>
              <option value="nginx">Nginx Config</option>
              <option value="apache">Apache Config</option>
              <option value="docker">Dockerfile</option>
            </optgroup>
            <optgroup label="Web">
              <option value="html">HTML</option>
              <option value="css">CSS</option>
            </optgroup>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Code-Vorlage (Starter Code)
          </label>
          <textarea
            v-model="methodData.code_template"
            rows="8"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            placeholder="// Geben Sie hier den Starter-Code ein, den der Lernende sieht..."
          ></textarea>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Optional: Vorausgefüllter Code, mit dem der Lernende startet
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Musterlösung
          </label>
          <textarea
            v-model="methodData.solution"
            rows="10"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            placeholder="// Geben Sie hier die Musterlösung ein..."
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Test-Fälle (einer pro Zeile)
          </label>
          <textarea
            v-model="methodData.tests"
            rows="5"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            placeholder="Input: [1, 2, 3] -> Expected: 6&#10;Input: [] -> Expected: 0&#10;Input: [-1, 1] -> Expected: 0"
          ></textarea>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Format: Input: [Wert] -> Expected: [Erwartetes Ergebnis] (ein Test pro Zeile)
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Optionen
          </label>
          <div class="space-y-2">
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.allow_run"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                Code-Ausführung erlauben (Lernende können den Code testen)
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.show_hints"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                Hinweise anzeigen (bei Fehlern)
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.show_solution"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                Musterlösung nach Abgabe zeigen
              </span>
            </label>
          </div>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/window.store'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 9

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  instruction: string
  language: string
  code_template: string
  solution: string
  tests: string
  allow_run: boolean
  show_hints: boolean
  show_solution: boolean
}>({
  instruction: '',
  language: '',
  code_template: '',
  solution: '',
  tests: '',
  allow_run: true,
  show_hints: true,
  show_solution: true
})

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      instruction: existingData.instruction || '',
      language: existingData.language || '',
      code_template: existingData.code_template || '',
      solution: existingData.solution || '',
      tests: existingData.tests || '',
      allow_run: existingData.allow_run !== undefined ? existingData.allow_run : true,
      show_hints: existingData.show_hints !== undefined ? existingData.show_hints : true,
      show_solution: existingData.show_solution !== undefined ? existingData.show_solution : true
    }
  }
})
</script>
