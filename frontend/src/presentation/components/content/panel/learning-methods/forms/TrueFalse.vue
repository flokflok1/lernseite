<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <div class="space-y-6">
        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.learningMethods.lm11.title') }}
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ $t('windows.learningMethods.lm11.description') }}
          </p>
        </div>

        <!-- Statements List -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            {{ $t('windows.learningMethods.lm11.statementsLabel') }}
          </label>

          <div v-if="methodData.statements && methodData.statements.length > 0" class="space-y-3">
            <div
              v-for="(statement, index) in methodData.statements"
              :key="index"
              class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div class="flex items-start space-x-3 mb-3">
                <span class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full text-sm font-medium">
                  {{ index + 1 }}
                </span>
                <div class="flex-1">
                  <textarea
                    v-model="statement.text"
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="$t('windows.learningMethods.lm11.statementPlaceholder')"
                    required
                  ></textarea>
                </div>
                <button
                  type="button"
                  @click="removeStatement(index)"
                  class="flex-shrink-0 p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  :title="$t('common.remove')"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>

              <div class="flex items-center space-x-4 ml-11">
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input
                    v-model="statement.is_true"
                    type="radio"
                    :name="`statement-${index}`"
                    :value="true"
                    class="text-green-600 focus:ring-green-500"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300">
                    {{ $t('windows.learningMethods.lm11.optionTrue') }}
                  </span>
                </label>
                <label class="flex items-center space-x-2 cursor-pointer">
                  <input
                    v-model="statement.is_true"
                    type="radio"
                    :name="`statement-${index}`"
                    :value="false"
                    class="text-red-600 focus:ring-red-500"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300">
                    {{ $t('windows.learningMethods.lm11.optionFalse') }}
                  </span>
                </label>
              </div>

              <div class="mt-3 ml-11">
                <input
                  v-model="statement.explanation"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
                  :placeholder="$t('windows.learningMethods.lm11.explanationPlaceholder')"
                />
              </div>
            </div>
          </div>

          <div v-else class="p-6 bg-gray-50 dark:bg-gray-800 rounded-lg text-center text-sm text-gray-500 dark:text-gray-400">
            {{ $t('windows.learningMethods.lm11.noStatements') }}
          </div>

          <button
            type="button"
            @click="addStatement"
            class="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            {{ $t('windows.learningMethods.lm11.addStatement') }}
          </button>
        </div>

        <!-- Options -->
        <div class="space-y-3">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {{ $t('common.options') }}
          </label>

          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.randomize"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ $t('windows.learningMethods.lm11.randomizeLabel') }}
            </span>
          </label>

          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.show_explanations"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ $t('windows.learningMethods.lm11.showExplanationsLabel') }}
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

interface Props {
  window: any
}

const props = defineProps<Props>()

const METHOD_CODE = 11

interface Statement {
  text: string
  is_true: boolean
  explanation: string
}

const methodData = reactive({
  statements: [] as Statement[],
  randomize: true,
  show_explanations: true
})

function addStatement() {
  methodData.statements.push({
    text: '',
    is_true: true,
    explanation: ''
  })
}

function removeStatement(index: number) {
  methodData.statements.splice(index, 1)
}

// Initialize with one statement
onMounted(() => {
  if (methodData.statements.length === 0) {
    addStatement()
  }
})
</script>
