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
            {{ $t('windows.lm08.title') }}
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {{ $t('windows.lm08.description') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm08.textLabel') }}
          </label>
          <textarea
            v-model="methodData.text"
            rows="8"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            :placeholder="$t('windows.lm08.textPlaceholder')"
            required
          ></textarea>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {{ $t('windows.lm08.textHint') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm08.blanksLabel') }}
          </label>
          <div v-if="detectedBlanks.length > 0" class="space-y-2">
            <div
              v-for="(blank, index) in detectedBlanks"
              :key="index"
              class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
            >
              <span class="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded-full text-sm font-medium">
                {{ index + 1 }}
              </span>
              <div class="flex-1">
                <input
                  v-model="methodData.blanks[index].answer"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  :placeholder="$t('windows.lm08.answerPlaceholder')"
                  required
                />
              </div>
              <div class="flex-shrink-0 w-32">
                <input
                  v-model="methodData.blanks[index].alternatives"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white text-sm"
                  :placeholder="$t('windows.lm08.alternativesPlaceholder')"
                />
              </div>
            </div>
          </div>
          <div v-else class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg text-center text-sm text-gray-500 dark:text-gray-400">
            {{ $t('windows.lm08.noBlanks') }}
          </div>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.case_sensitive"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ $t('windows.lm08.caseSensitiveLabel') }}
            </span>
          </label>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.show_hints"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ $t('windows.lm08.showHintsLabel') }}
            </span>
          </label>
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.show_word_bank"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ $t('windows.lm08.showWordBankLabel') }}
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref, computed, watch, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const { t } = useI18n()
const METHOD_CODE = 8

interface Blank {
  answer: string
  alternatives?: string
}

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const methodData = ref<{
  text: string
  blanks: Blank[]
  case_sensitive: boolean
  show_hints: boolean
  show_word_bank: boolean
}>({
  text: '',
  blanks: [],
  case_sensitive: false,
  show_hints: true,
  show_word_bank: false
})

const detectedBlanks = computed(() => {
  const regex = /\{\{([^}]+)\}\}/g
  const matches = []
  let match
  while ((match = regex.exec(methodData.value.text)) !== null) {
    matches.push(match[1].trim())
  }
  return matches
})

watch(detectedBlanks, (newBlanks) => {
  // Sync blanks array with detected blanks
  const currentAnswers = methodData.value.blanks.map(b => b.answer)
  methodData.value.blanks = newBlanks.map((blank, index) => ({
    answer: currentAnswers[index] || blank,
    alternatives: methodData.value.blanks[index]?.alternatives || ''
  }))
})

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      text: existingData.text || '',
      blanks: existingData.blanks || [],
      case_sensitive: existingData.case_sensitive || false,
      show_hints: existingData.show_hints !== undefined ? existingData.show_hints : true,
      show_word_bank: existingData.show_word_bank || false
    }
  }
})
</script>
