<!--
  QuestionMoveDialog - Modal to copy or move a question to another exam.
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
        class="relative w-full max-w-md max-h-[80vh] rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] shadow-xl flex flex-col"
      >
        <!-- Header -->
        <div class="p-4 border-b border-[var(--color-border)]">
          <h3 class="font-semibold text-[var(--color-text-primary)]">
            {{ mode === 'copy'
              ? t('panel.examArchive.questionEditor.copyTo')
              : t('panel.examArchive.questionEditor.moveTo')
            }}
          </h3>
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ t('panel.examArchive.questionEditor.selectExam') }}
          </p>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-2">
          <!-- Loading -->
          <div v-if="loadingExams" class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--color-primary)]"></div>
          </div>

          <!-- Exam list -->
          <div v-else class="space-y-1">
            <button
              v-for="exam in exams"
              :key="exam.exam_id"
              type="button"
              :disabled="processing"
              class="w-full text-left px-3 py-2.5 rounded hover:bg-[var(--color-surface-secondary)] transition-colors disabled:opacity-50"
              @click="selectExam(exam.exam_id)"
            >
              <div class="text-sm font-medium text-[var(--color-text-primary)]">
                {{ exam.title }}
              </div>
              <div class="text-xs text-[var(--color-text-secondary)] mt-0.5">
                {{ exam.year }} {{ exam.season }} &middot; {{ exam.part }}
              </div>
            </button>
          </div>
        </div>

        <!-- Success message -->
        <div
          v-if="successMsg"
          class="px-4 py-2 text-sm text-center"
          style="background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);"
        >
          {{ successMsg }}
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
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ArchiveExam } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import {
  archiveListExams,
  archiveCopyQuestion,
  archiveMoveQuestion
} from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  visible: boolean
  mode: 'copy' | 'move'
  questionId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  done: []
}>()

const { t } = useI18n()

const exams = ref<ArchiveExam[]>([])
const loadingExams = ref(false)
const processing = ref(false)
const successMsg = ref('')

watch(
  () => props.visible,
  async (val) => {
    if (!val) {
      successMsg.value = ''
      return
    }
    loadingExams.value = true
    try {
      exams.value = await archiveListExams()
    } catch (err) {
      console.error('Failed to load exams:', err)
    } finally {
      loadingExams.value = false
    }
  },
  { immediate: true }
)

async function selectExam(targetExamId: string) {
  processing.value = true
  try {
    if (props.mode === 'copy') {
      await archiveCopyQuestion(props.questionId, targetExamId)
    } else {
      await archiveMoveQuestion(props.questionId, targetExamId)
    }
    successMsg.value = t('panel.examArchive.questionEditor.operationSuccess')
    emit('done')
  } catch (err) {
    console.error('Copy/move failed:', err)
  } finally {
    processing.value = false
  }
}
</script>
