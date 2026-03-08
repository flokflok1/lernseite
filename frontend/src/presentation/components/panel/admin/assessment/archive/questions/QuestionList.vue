<!--
  QuestionList - Displays all questions for an exam with inline editing.
  Features: quality dots, bulk selection, inline QuestionEditor, create new question.
-->

<template>
  <div class="space-y-2">
    <!-- Header row -->
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
        {{ t('panel.examArchive.questionEditor.title') }}
      </h3>
      <button
        @click="handleCreate"
        class="px-3 py-1.5 text-sm rounded text-white transition-colors"
        style="background-color: var(--color-primary, #7c3aed);"
      >
        {{ t('panel.examArchive.questionEditor.create') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-6">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-[var(--color-primary)]" />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="questions.length === 0"
      class="text-center py-8 text-sm text-[var(--color-text-secondary)]"
    >
      {{ t('panel.examArchive.noQuestions') }}
    </div>

    <!-- Questions -->
    <div v-else class="space-y-1">
      <div v-for="q in questions" :key="q.question_id">
        <!-- Row (non-editing) -->
        <div
          v-if="editingId !== q.question_id"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[var(--color-bg)] cursor-pointer transition-colors group"
          @click="editingId = q.question_id"
        >
          <!-- Checkbox -->
          <input
            type="checkbox"
            :checked="selectedIds.has(q.question_id)"
            @click.stop
            @change="toggleSelection(q.question_id)"
            class="accent-[var(--color-primary)] shrink-0"
          />

          <!-- Quality dot -->
          <span
            class="inline-block w-2 h-2 rounded-full shrink-0"
            :class="getQualityDotClass(q)"
          />

          <!-- Question number -->
          <span class="text-xs font-mono text-[var(--color-text-secondary)] w-8 shrink-0">
            {{ q.question_number || '-' }}
          </span>

          <!-- Question text (truncated) -->
          <span class="text-sm text-[var(--color-text-primary)] flex-1 truncate">
            {{ truncate(q.question_text, 50) }}
          </span>

          <!-- Type badge -->
          <span
            class="px-1.5 py-0.5 text-xs rounded bg-[var(--color-bg)] text-[var(--color-text-secondary)] border border-[var(--color-border)] shrink-0"
          >
            {{ q.question_type }}
          </span>

          <!-- Points -->
          <span class="text-xs text-[var(--color-text-secondary)] w-12 text-right shrink-0">
            {{ t('panel.examArchive.points', { count: q.points }) }}
          </span>

          <!-- Topic count -->
          <span class="text-xs text-[var(--color-text-secondary)] w-16 text-right shrink-0">
            {{ q.topics?.length ?? 0 }} {{ t('panel.examArchive.topics') }}
          </span>
        </div>

        <!-- Inline editor -->
        <QuestionEditor
          v-else
          :question="q"
          @save="(data) => handleSave(q.question_id, data)"
          @cancel="editingId = null"
          @delete="handleDelete(q.question_id)"
        />
      </div>
    </div>

    <!-- Bulk bar -->
    <QuestionBulkBar
      v-if="selectedIds.size > 0"
      :selected-count="selectedIds.size"
      @bulk-delete="handleBulkDelete"
      @bulk-topics="handleBulkTopics"
      @clear-selection="selectedIds.clear()"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ArchiveQuestion, QuestionEdit } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import {
  archiveGetQuestions,
  archiveUpdateQuestion,
  archiveDeleteQuestion,
  archiveCreateQuestion,
  archiveBulkDeleteQuestions,
  archiveBulkUpdateTopics,
} from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import QuestionEditor from './QuestionEditor.vue'
import QuestionBulkBar from './QuestionBulkBar.vue'

const { t } = useI18n()

interface Props {
  examId: string
}

const props = defineProps<Props>()

const questions = ref<ArchiveQuestion[]>([])
const loading = ref(false)
const editingId = ref<string | null>(null)
const selectedIds = ref<Set<string>>(new Set())

// Load questions
async function loadQuestions() {
  loading.value = true
  try {
    questions.value = await archiveGetQuestions(props.examId)
  } catch (err) {
    console.error('Failed to load questions:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadQuestions)

// Helpers
function truncate(text: string, max: number): string {
  if (!text) return '-'
  return text.length > max ? text.slice(0, max) + '...' : text
}

function getQualityDotClass(q: ArchiveQuestion): Record<string, boolean> {
  const hasText = !!q.question_text?.trim()
  const hasPoints = q.points > 0
  if (!hasText || !hasPoints) return { 'bg-red-500': true }

  const hasSolution = !!q.solution_text?.trim() || (q.solution && Object.keys(q.solution).length > 0)
  const hasTopics = q.topics?.length > 0
  if (!hasSolution || !hasTopics) return { 'bg-yellow-500': true }

  return { 'bg-green-500': true }
}

function toggleSelection(id: string) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
  // Force reactivity
  selectedIds.value = new Set(selectedIds.value)
}

// CRUD handlers
async function handleSave(questionId: string, data: QuestionEdit) {
  if (Object.keys(data).length === 0) {
    editingId.value = null
    return
  }
  try {
    const updated = await archiveUpdateQuestion(questionId, data)
    const idx = questions.value.findIndex((q) => q.question_id === questionId)
    if (idx !== -1) {
      questions.value[idx] = updated
    }
    editingId.value = null
  } catch (err) {
    console.error('Failed to update question:', err)
  }
}

async function handleDelete(questionId: string) {
  try {
    await archiveDeleteQuestion(questionId)
    questions.value = questions.value.filter((q) => q.question_id !== questionId)
    editingId.value = null
  } catch (err) {
    console.error('Failed to delete question:', err)
  }
}

async function handleCreate() {
  try {
    const newQ = await archiveCreateQuestion(props.examId, {
      question_text: '',
      question_type: 'essay',
      points: 0,
    })
    questions.value.push(newQ)
    editingId.value = newQ.question_id
  } catch (err) {
    console.error('Failed to create question:', err)
  }
}

async function handleBulkDelete() {
  const ids = [...selectedIds.value]
  try {
    await archiveBulkDeleteQuestions(ids)
    questions.value = questions.value.filter((q) => !selectedIds.value.has(q.question_id))
    selectedIds.value.clear()
  } catch (err) {
    console.error('Failed to bulk delete:', err)
  }
}

async function handleBulkTopics() {
  const input = window.prompt('Topics (comma-separated):')
  if (input === null) return
  const topics = input.split(',').map((s) => s.trim()).filter(Boolean)
  const ids = [...selectedIds.value]
  try {
    await archiveBulkUpdateTopics(ids, topics)
    // Reload to get updated data
    await loadQuestions()
    selectedIds.value.clear()
  } catch (err) {
    console.error('Failed to bulk update topics:', err)
  }
}
</script>
