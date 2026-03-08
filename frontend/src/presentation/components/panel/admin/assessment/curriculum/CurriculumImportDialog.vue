<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="emit('close')"
  >
    <div class="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
      <div class="flex items-center justify-between p-4 border-b">
        <h2 class="text-lg font-semibold">
          {{ $t('panel.curriculum.import.title') }}
        </h2>
        <button
          class="text-gray-400 hover:text-gray-600"
          @click="emit('close')"
        >
          &times;
        </button>
      </div>

      <div class="p-4 overflow-y-auto flex-1 space-y-4">
        <!-- Step 1: Paste PDF text -->
        <div v-if="step === 'input'">
          <label class="block text-sm font-medium mb-1">
            {{ $t('panel.curriculum.import.pasteLabel') }}
          </label>
          <textarea
            v-model="pdfText"
            rows="12"
            class="w-full border rounded p-2 text-sm font-mono dark:bg-gray-800"
            :placeholder="$t('panel.curriculum.import.pastePlaceholder')"
          />
          <p class="text-xs text-gray-500 mt-1">
            {{ $t('panel.curriculum.import.pasteHint') }}
          </p>
        </div>

        <!-- Step 2: Preview AI result -->
        <div v-if="step === 'preview' && preview">
          <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded mb-3">
            <p class="text-sm font-medium text-green-700 dark:text-green-400">
              {{ $t('panel.curriculum.import.previewSuccess') }}
            </p>
          </div>

          <div class="text-sm space-y-2">
            <p>
              <strong>{{ $t('panel.curriculum.import.name') }}:</strong>
              {{ preview.name }}
            </p>
            <p>
              <strong>{{ $t('panel.curriculum.import.type') }}:</strong>
              {{ preview.framework_type }}
            </p>
            <p>
              <strong>{{ $t('panel.curriculum.import.sections') }}:</strong>
              {{ preview.sections?.length || 0 }}
            </p>

            <label class="block text-sm font-medium mt-3 mb-1">
              {{ $t('panel.curriculum.import.sourceDocument') }}
            </label>
            <input
              v-model="sourceDocument"
              type="text"
              class="w-full border rounded p-2 text-sm dark:bg-gray-800"
              :placeholder="$t('panel.curriculum.import.sourcePlaceholder')"
            />
          </div>
        </div>

        <!-- Error state -->
        <div
          v-if="error"
          class="bg-red-50 dark:bg-red-900/20 p-3 rounded text-sm text-red-700 dark:text-red-400"
        >
          {{ error }}
        </div>
      </div>

      <div class="flex justify-end gap-2 p-4 border-t">
        <button
          class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          @click="emit('close')"
        >
          {{ $t('common.cancel') }}
        </button>

        <button
          v-if="step === 'input'"
          class="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          :disabled="loading || pdfText.length < 100"
          @click="handleParse"
        >
          {{ loading ? $t('common.loading') : $t('panel.curriculum.import.parseBtn') }}
        </button>

        <button
          v-if="step === 'preview'"
          class="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          :disabled="loading"
          @click="handleConfirm"
        >
          {{ loading ? $t('common.loading') : $t('panel.curriculum.import.confirmBtn') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  visible: boolean
  loading: boolean
  error: string | null
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  parse: [pdfText: string]
  confirm: [sourceDocument: string | undefined]
}>()

const pdfText = ref('')
const sourceDocument = ref('')
const step = ref<'input' | 'preview'>('input')
const preview = ref<Record<string, any> | null>(null)

function handleParse() {
  emit('parse', pdfText.value)
}

function handleConfirm() {
  emit('confirm', sourceDocument.value || undefined)
}

function setPreview(data: Record<string, any>) {
  preview.value = data
  step.value = 'preview'
}

function reset() {
  pdfText.value = ''
  sourceDocument.value = ''
  step.value = 'input'
  preview.value = null
}

defineExpose({ setPreview, reset })
</script>
