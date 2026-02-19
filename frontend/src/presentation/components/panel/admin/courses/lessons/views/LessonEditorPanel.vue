<!--
  Admin Lesson Editor Panel - Phase 6 Complete

  Panel variant of the lesson editor.
  Uses useLessonEditor composable for business logic
  and LessonEditorForm for the shared form layout.
  Supports i18n labels via $t() for localized UI text.
-->

<template>
  <LessonEditorForm
    class="admin-lesson-editor-panel"
    :form="form"
    :save-status="saveStatus"
    :error-message="errorMessage"
    :module-id="moduleId"
    :lesson-type-label="lessonTypeLabel"
    :validation-errors="validationErrors"
    :title-label="$t('features.lessonEditor.titleLabel')"
    :title-placeholder="$t('features.lessonEditor.titlePlaceholder')"
    :description-label="$t('features.lessonEditor.descriptionLabel')"
    :description-placeholder="$t('features.lessonEditor.descriptionPlaceholder')"
    :type-select-label="$t('features.lessonEditor.typeLabel')"
    :type-default-option="$t('features.lessonEditor.selectType')"
    :type-options="localizedTypeOptions"
    :order-label="$t('features.lessonEditor.orderLabel')"
    :order-placeholder="$t('features.lessonEditor.orderPlaceholder')"
    :duration-label="$t('features.lessonEditor.durationLabel')"
    :duration-placeholder="$t('features.lessonEditor.durationPlaceholder')"
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
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDesktopPanelStore } from '@/application/stores/modules/workspace'
import type { LsxPanel } from '@/application/stores/modules/workspace'
import { useLessonEditor } from '../composables'
import LessonEditorForm from './LessonEditorForm.vue'

const { t } = useI18n()

interface Props {
  panel: LsxPanel
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const _emit = defineEmits<Emits>()
const panelStore = useDesktopPanelStore()

const localizedTypeOptions = computed(() => [
  { value: 'text', label: `\uD83D\uDCC4 ${t('features.lessonEditor.typeText')}` },
  { value: 'video', label: `\uD83C\uDFA5 ${t('features.lessonEditor.typeVideo')}` },
  { value: 'quiz', label: `\u2753 ${t('features.lessonEditor.typeQuiz')}` },
  { value: 'interactive', label: `\uD83C\uDFAE ${t('features.lessonEditor.typeInteractive')}` },
  { value: 'exercise', label: `\uD83D\uDCAA ${t('features.lessonEditor.typeExercise')}` },
  { value: 'ai', label: `\uD83E\uDD16 ${t('features.lessonEditor.typeAI')}` },
  { value: 'exam', label: `\uD83D\uDCDD ${t('features.lessonEditor.typeExam')}` }
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
  getPayload: () => props.panel.payload,
  onPayloadUpdate: (patch) => panelStore.updatePanelPayload(props.panel.id, patch)
})
</script>
