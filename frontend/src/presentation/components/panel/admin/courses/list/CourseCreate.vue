<!--
  Admin Course Create (Base / Window variant)

  Flow:
  1. Without file: Manually fill all fields
  2. With file: AI fills the fields (title, description, category, level, language)
  3. No module generation here - that happens on the detail page

  Phase: C2.1 - Kurs-Erstellen
-->

<template>
  <div class="admin-course-create-window h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
      <div>
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">{{ $t('courseCreate.title') }}</h3>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ selectedFile ? $t('courseCreate.subtitleWithFile') : $t('courseCreate.subtitleManual') }}
        </p>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 p-6 overflow-y-auto">
      <CourseCreateFormFields
        :form="form"
        :categories="categories"
        :selected-file="selectedFile"
        :file-error="fileError"
        :ai-status="aiStatus"
        :is-processing="isProcessing"
        :format-file-size="formatFileSize"
        :get-file-icon="getFileIcon"
        @trigger-file-input="fileInput?.click()"
        @clear-file="clearFile"
        @fill-with-a-i="fillFieldsWithAI"
        @open-model-selector="openModelSelector"
        @clear-model-override="clearModelOverride"
      />
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.doc,.docx,.ppt,.pptx,.txt"
        @change="handleFileSelect"
        class="hidden"
      />
    </div>

    <!-- Footer Actions -->
    <div class="px-6 py-3 bg-[var(--color-surface)] border-t border-[var(--color-border)] flex justify-between">
      <button
        type="button"
        @click="$emit('close')"
        :disabled="isProcessing"
        class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-bg)] transition-colors disabled:opacity-50"
      >
        {{ $t('courseCreate.actions.cancel') }}
      </button>

      <button
        type="button"
        @click="createCourse"
        :disabled="!canCreate"
        class="px-5 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
      >
        {{ isCreating ? $t('courseCreate.actions.creating') : $t('courseCreate.actions.createCourse') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import CourseCreateFormFields from './forms/CourseCreateFormFields.vue'
import { useCourseCreate } from './composables/useCourseCreate'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()
const windowStore = useWindowStore()

const {
  form,
  categories,
  selectedFile,
  fileInput,
  fileError,
  isCreating,
  aiStatus,
  isProcessing,
  canCreate,
  handleFileSelect,
  clearFile,
  formatFileSize,
  getFileIcon,
  fillFieldsWithAI,
  createCourse,
  clearModelOverride,
  generateCallbackId
} = useCourseCreate(() => emit('close'))

function openModelSelector(): void {
  const callbackId = generateCallbackId()

  windowStore.openWindow({
    type: 'admin-model-selector',
    title: t('courseCreate.modelSelector.title'),
    icon: '\uD83E\uDD16',
    payload: {
      scope: 'course',
      callbackId,
      onSelectModel: (modelName: string) => {
        form.value.ai_model_override = modelName
      }
    },
    size: { width: 600, height: 700 }
  })
}
</script>
