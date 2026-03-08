<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="emit('close')"
  >
    <div class="bg-white dark:bg-gray-900 rounded-lg shadow-xl w-full max-w-2xl max-h-[85vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b">
        <h2 class="text-lg font-semibold">
          {{ t('panel.curriculum.import.title') }}
        </h2>
        <button
          class="text-gray-400 hover:text-gray-600"
          @click="emit('close')"
        >
          &times;
        </button>
      </div>

      <div class="p-4 overflow-y-auto flex-1 space-y-4">
        <!-- Step 1: Input -->
        <div v-if="step === 'input'" class="space-y-4">
          <!-- PDF File Upload -->
          <div>
            <label class="block text-sm font-medium mb-1">
              {{ t('panel.curriculum.import.uploadLabel') }}
            </label>
            <div
              class="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors"
              :class="dragOver
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'"
              @click="triggerFileInput"
              @dragover.prevent="dragOver = true"
              @dragleave.prevent="dragOver = false"
              @drop.prevent="handleDrop"
            >
              <div v-if="!selectedFile" class="space-y-1">
                <div class="text-3xl opacity-40">📄</div>
                <p class="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {{ t('panel.curriculum.import.dropHint') }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ t('panel.curriculum.import.dropHintFormats') }}
                </p>
              </div>
              <div v-else class="flex items-center justify-center gap-2">
                <span class="text-green-600">✓</span>
                <span class="text-sm font-medium">{{ selectedFile.name }}</span>
                <button
                  class="ml-2 text-xs text-red-500 hover:text-red-700"
                  @click.stop="removeFile"
                >
                  {{ t('panel.curriculum.import.removeFile') }}
                </button>
              </div>
            </div>
            <input
              ref="fileInputRef"
              type="file"
              accept=".pdf"
              class="hidden"
              @change="handleFileSelect"
            />
          </div>

          <!-- Or paste text (collapsible) -->
          <div>
            <button
              class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
              @click="showPaste = !showPaste"
            >
              {{ t('panel.curriculum.import.orPasteText') }}
              <span class="ml-1">{{ showPaste ? '▲' : '▼' }}</span>
            </button>
            <div v-if="showPaste" class="mt-2">
              <textarea
                v-model="pdfText"
                rows="8"
                class="w-full border rounded p-2 text-sm font-mono dark:bg-gray-800"
                :placeholder="t('panel.curriculum.import.pastePlaceholder')"
              />
              <p class="text-xs text-gray-500 mt-1">
                {{ t('panel.curriculum.import.pasteHint') }}
              </p>
            </div>
          </div>

          <!-- AI Provider / Model -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">
                {{ t('panel.curriculum.import.selectProvider') }}
              </label>
              <select
                v-model="selectedProvider"
                class="w-full px-3 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
              >
                <option v-if="availableProviders.length === 0" value="" disabled>
                  {{ t('panel.curriculum.import.noProviders') }}
                </option>
                <option v-for="p in availableProviders" :key="p.name" :value="p.name">
                  {{ p.display_name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">
                {{ t('panel.curriculum.import.selectModel') }}
              </label>
              <select
                v-model="selectedModel"
                class="w-full px-3 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
              >
                <option v-for="m in availableModels" :key="m.model_name" :value="m.model_name">
                  {{ m.display_name || m.model_name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Step 2: Preview AI result -->
        <div v-if="step === 'preview' && preview">
          <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded mb-3">
            <p class="text-sm font-medium text-green-700 dark:text-green-400">
              {{ t('panel.curriculum.import.previewSuccess') }}
            </p>
          </div>
          <div class="text-sm space-y-2">
            <p>
              <strong>{{ t('panel.curriculum.import.name') }}:</strong>
              {{ preview.name }}
            </p>
            <p>
              <strong>{{ t('panel.curriculum.import.type') }}:</strong>
              {{ preview.framework_type }}
            </p>
            <p>
              <strong>{{ t('panel.curriculum.import.sections') }}:</strong>
              {{ preview.sections?.length || 0 }}
            </p>
            <label class="block text-sm font-medium mt-3 mb-1">
              {{ t('panel.curriculum.import.sourceDocument') }}
            </label>
            <input
              v-model="sourceDocument"
              type="text"
              class="w-full border rounded p-2 text-sm dark:bg-gray-800"
              :placeholder="t('panel.curriculum.import.sourcePlaceholder')"
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

      <!-- Footer -->
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
          :disabled="loading || !hasInput"
          @click="handleParse"
        >
          {{ loading ? t('panel.curriculum.import.analyzing') : t('panel.curriculum.import.parseBtn') }}
        </button>

        <button
          v-if="step === 'preview'"
          class="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          :disabled="loading"
          @click="handleConfirm"
        >
          {{ loading ? $t('common.loading') : t('panel.curriculum.import.confirmBtn') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { adminGetAIModelsRegistry } from '@/infrastructure/api/clients/panel/admin/ai/models.api'
import type { AIModelRegistryItem, AIProviderInfo } from '@/infrastructure/api/clients/panel/admin/types'

interface Props {
  visible: boolean
  loading: boolean
  error: string | null
}

defineProps<Props>()

const emit = defineEmits<{
  close: []
  parse: [pdfText: string, provider: string, model: string]
  parseFile: [file: File, provider: string, model: string]
  confirm: [sourceDocument: string | undefined]
}>()

const { t } = useI18n()

// --- Input state ---
const pdfText = ref('')
const selectedFile = ref<File | null>(null)
const showPaste = ref(false)
const dragOver = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const sourceDocument = ref('')
const step = ref<'input' | 'preview'>('input')
const preview = ref<Record<string, any> | null>(null)

// --- AI Provider / Model ---
const providers = ref<AIProviderInfo[]>([])
const models = ref<AIModelRegistryItem[]>([])
const selectedProvider = ref('')
const selectedModel = ref('')

const availableProviders = computed(() =>
  providers.value.filter(p => p.has_api_key)
)

const availableModels = computed(() =>
  models.value.filter(m => m.provider === selectedProvider.value && m.category === 'chat')
)

const hasInput = computed(() =>
  selectedFile.value !== null || pdfText.value.length >= 100
)

watch(selectedProvider, () => {
  const first = availableModels.value[0]
  selectedModel.value = first?.model_name || ''
})

onMounted(async () => {
  try {
    const registry = await adminGetAIModelsRegistry()
    providers.value = registry.providers
    models.value = registry.data
    const firstAvailable = availableProviders.value[0]
    if (firstAvailable) {
      selectedProvider.value = firstAvailable.name
    }
  } catch {
    /* AI registry unavailable — dropdowns stay empty */
  }
})

// --- File handling ---
function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
  }
}

function handleDrop(event: DragEvent) {
  dragOver.value = false
  const file = event.dataTransfer?.files[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
  }
}

function removeFile() {
  selectedFile.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

// --- Actions ---
function handleParse() {
  if (selectedFile.value) {
    emit('parseFile', selectedFile.value, selectedProvider.value, selectedModel.value)
  } else {
    emit('parse', pdfText.value, selectedProvider.value, selectedModel.value)
  }
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
  selectedFile.value = null
  sourceDocument.value = ''
  step.value = 'input'
  preview.value = null
  showPaste.value = false
  if (fileInputRef.value) fileInputRef.value.value = ''
}

defineExpose({ setPreview, reset })
</script>
