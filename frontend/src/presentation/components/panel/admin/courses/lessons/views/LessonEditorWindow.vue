<!--
  Admin Lesson Editor Window - Phase 6 Complete

  Window variant of the lesson editor.
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
      Modul: <span class="font-medium text-[var(--color-text-primary)]">Modul {{ moduleId }}</span>
    </template>
  </LessonEditorForm>
</template>

<script setup lang="ts">
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import { useLessonEditor } from '../composables'
import LessonEditorForm from './LessonEditorForm.vue'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const _emit = defineEmits<Emits>()
const windowStore = useWindowStore()

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
