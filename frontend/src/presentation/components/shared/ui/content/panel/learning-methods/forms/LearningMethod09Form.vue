<template>
  <BaseLearningMethodForm
    :panel="panel"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form: _form }">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm09.codeSandboxTitle') }}
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {{ $t('features.lm09.codeSandboxDesc') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm09.instructionLabel') }}
          </label>
          <textarea
            v-model="methodData.instruction"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            :placeholder="$t('features.lm09.instructionPlaceholder')"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm09.languageLabel') }}
          </label>
          <select
            v-model="methodData.language"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">{{ $t('features.lm09.selectTypeOption') }}</option>
            <optgroup :label="$t('features.lm09.languagesOptGroup')">
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
            <optgroup :label="$t('features.lm09.configurationOptGroup')">
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
            <optgroup :label="$t('features.lm09.webOptGroup')">
              <option value="html">HTML</option>
              <option value="css">CSS</option>
            </optgroup>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm09.codeTemplateLabel') }}
          </label>
          <textarea
            v-model="methodData.code_template"
            rows="8"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            :placeholder="$t('features.lm09.codeTemplatePlaceholder')"
          ></textarea>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ $t('features.lm09.codeTemplateHint') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm09.solutionLabel') }}
          </label>
          <textarea
            v-model="methodData.solution"
            rows="10"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            :placeholder="$t('features.lm09.solutionPlaceholder')"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm09.testCasesLabel') }}
          </label>
          <textarea
            v-model="methodData.tests"
            rows="5"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            :placeholder="$t('features.lm09.testCasesPlaceholder')"
          ></textarea>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ $t('features.lm09.testCasesHint') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('features.lm09.optionsLabel') }}
          </label>
          <div class="space-y-2">
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.allow_run"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ $t('features.lm09.allowRunCheckbox') }}
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.show_hints"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ $t('features.lm09.showHintsCheckbox') }}
              </span>
            </label>
            <label class="flex items-center space-x-2">
              <input
                v-model="methodData.show_solution"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {{ $t('features.lm09.showSolutionCheckbox') }}
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
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 9
const { t } = useI18n()

interface Props {
  panel: LsxPanel
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
  const existingData = props.panel.payload?.instanceData?.data
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
