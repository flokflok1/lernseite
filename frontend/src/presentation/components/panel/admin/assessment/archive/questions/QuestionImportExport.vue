<!--
  QuestionImportExport - Modal for importing/exporting questions as JSON.
-->

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/50" @click="emit('close')"></div>

      <!-- Dialog -->
      <div
        class="relative w-full max-w-lg max-h-[80vh] rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] shadow-xl flex flex-col"
      >
        <!-- Header -->
        <div class="p-4 border-b border-[var(--color-border)]">
          <h3 class="font-semibold text-[var(--color-text-primary)]">
            {{ t('panel.examArchive.questionEditor.importExport') }}
          </h3>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4 space-y-6">
          <!-- Export section -->
          <div>
            <h4 class="text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ t('panel.examArchive.questionEditor.export') }}
            </h4>
            <button
              type="button"
              :disabled="exporting"
              class="px-3 py-1.5 text-sm rounded text-white transition-colors disabled:opacity-50"
              style="background-color: var(--color-primary, #7c3aed);"
              @click="handleExport"
            >
              {{ exporting ? '...' : t('panel.examArchive.questionEditor.export') }}
            </button>
          </div>

          <!-- Import section -->
          <div>
            <h4 class="text-sm font-medium text-[var(--color-text-primary)] mb-2">
              {{ t('panel.examArchive.questionEditor.import') }}
            </h4>
            <textarea
              v-model="importJson"
              rows="6"
              :placeholder="t('panel.examArchive.questionEditor.pasteJson')"
              class="w-full px-3 py-2 text-xs font-mono rounded border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] focus:outline-none focus:border-[var(--color-primary)] resize-none"
            ></textarea>

            <div class="flex items-center gap-3 mt-2">
              <button
                type="button"
                :disabled="!importJson.trim() || importing"
                class="px-3 py-1.5 text-sm rounded text-white transition-colors disabled:opacity-50"
                style="background-color: var(--color-primary, #7c3aed);"
                @click="handleImport"
              >
                {{ importing ? '...' : t('panel.examArchive.questionEditor.import') }}
              </button>

              <!-- Parse error -->
              <span v-if="parseError" class="text-xs text-[var(--color-error-text, #dc2626)]">
                {{ t('panel.examArchive.questionEditor.parseError') }}
              </span>
            </div>
          </div>

          <!-- Result message -->
          <div
            v-if="resultMsg"
            class="rounded p-3 text-sm text-center"
            style="background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);"
          >
            {{ resultMsg }}
          </div>
        </div>

        <!-- Footer -->
        <div class="p-3 border-t border-[var(--color-border)] flex justify-end">
          <button
            type="button"
            class="px-3 py-1.5 text-sm rounded border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors"
            @click="emit('close')"
          >
            {{ t('panel.examArchive.questionEditor.close') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  archiveExportQuestions,
  archiveImportQuestions
} from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import type { QuestionEdit } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  examId: string
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  imported: []
}>()

const { t } = useI18n()

const importJson = ref('')
const parseError = ref(false)
const importing = ref(false)
const exporting = ref(false)
const resultMsg = ref('')

async function handleExport() {
  exporting.value = true
  try {
    const questions = await archiveExportQuestions(props.examId)
    const blob = new Blob([JSON.stringify(questions, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `exam-${props.examId}-questions.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Export failed:', err)
  } finally {
    exporting.value = false
  }
}

async function handleImport() {
  parseError.value = false
  resultMsg.value = ''

  let questions: QuestionEdit[]
  try {
    questions = JSON.parse(importJson.value)
    if (!Array.isArray(questions)) throw new Error('Not an array')
  } catch {
    parseError.value = true
    return
  }

  importing.value = true
  try {
    const result = await archiveImportQuestions(props.examId, questions)
    resultMsg.value = t('panel.examArchive.questionEditor.importSuccess', {
      imported: result.imported,
      skipped: result.skipped
    })
    importJson.value = ''
    emit('imported')
  } catch (err) {
    console.error('Import failed:', err)
  } finally {
    importing.value = false
  }
}
</script>
