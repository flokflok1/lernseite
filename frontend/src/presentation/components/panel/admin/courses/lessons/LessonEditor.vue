<!--
  Admin Lesson Editor - Phase 6 Complete

  Window variant of the lesson editor with full i18n support.
  Uses useLessonEditor composable for business logic
  and LessonEditorForm for the shared form layout.
-->

<template>
  <LessonEditorForm
    class="admin-lesson-editor-window"
    :form="form"
    :save-status="saveStatus"
    :error-message="errorMessage"
    :module-id="moduleId"
    :lesson-type-label="lessonTypeLabel"
    :validation-errors="validationErrors"
    :title-label="$t('lessonEditor.lessonTitle')"
    :title-placeholder="$t('lessonEditor.titlePlaceholder')"
    :description-label="$t('lessonEditor.description')"
    :description-placeholder="$t('lessonEditor.descriptionPlaceholder')"
    :type-select-label="$t('lessonEditor.lessonType')"
    :type-default-option="$t('lessonEditor.selectType')"
    :type-options="localizedTypeOptions"
    :order-label="$t('lessonEditor.order')"
    :order-placeholder="'1'"
    :duration-label="$t('lessonEditor.duration')"
    :duration-placeholder="'15'"
    :saving-label="$t('lessonEditor.saving')"
    :saved-label="$t('lessonEditor.saved')"
    :error-label="$t('common.error')"
    :validation-title="$t('lessonEditor.validation.title')"
    @debounced-save="debouncedSave"
    @type-change="handleTypeChange"
    @add-question="addQuestion"
    @remove-question="removeQuestion"
    @add-option="addOption"
    @remove-option="removeOption"
    @add-exam-question="addExamQuestion"
    @remove-exam-question="removeExamQuestion"
  >
    <template #header-label>
      {{ $t('lessonEditor.moduleLabel') }} <span class="font-medium text-[var(--color-text-primary)]">{{ moduleId }}</span>
    </template>
  </LessonEditorForm>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import { useLessonEditor } from './composables'
import LessonEditorForm from './views/LessonEditorForm.vue'

const { t } = useI18n()

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const _emit = defineEmits<Emits>()
const windowStore = useWindowStore()

const localizedTypeOptions = computed(() => [
  { value: 'text', label: `\uD83D\uDCC4 ${t('lessonEditor.types.text')}` },
  { value: 'video', label: `\uD83C\uDFA5 ${t('lessonEditor.types.video')}` },
  { value: 'quiz', label: `\u2753 ${t('lessonEditor.types.quiz')}` },
  { value: 'interactive', label: `\uD83C\uDFAE ${t('lessonEditor.types.interactive')}` },
  { value: 'exercise', label: `\uD83D\uDCAA ${t('lessonEditor.types.exercise')}` },
  { value: 'ai', label: `\uD83E\uDD16 ${t('lessonEditor.types.ai')}` },
  { value: 'exam', label: `\uD83D\uDCDD ${t('lessonEditor.types.exam')}` }
])

const {
  form,
  saveStatus,
  errorMessage,
  moduleId,
  lessonTypeLabel,
  validationErrors,
  debouncedSave,
  handleTypeChange,
  addQuestion,
  removeQuestion,
  addOption,
  removeOption,
  addExamQuestion,
  removeExamQuestion
} = useLessonEditor({
  getPayload: () => props.window.payload,
  onPayloadUpdate: (patch) => windowStore.updateWindowPayload(props.window.id, patch)
})
</script>
