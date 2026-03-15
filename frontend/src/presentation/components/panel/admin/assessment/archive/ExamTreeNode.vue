<!--
  ExamTreeNode — Recursive tree node for exam archive explorer.

  Renders group nodes (with children or session leaves) and
  exam leaves (loaded on demand when a session is expanded).
-->
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TreeNode, SessionLeaf } from '@/application/composables/panel/admin/assessment'
import type { ArchiveExam } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { archiveSessionExams } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  node: TreeNode
  depth?: number
}

const props = withDefaults(defineProps<Props>(), { depth: 0 })

const emit = defineEmits<{
  deleteSession: [sessionId: string, examCount: number]
  deleteExam: [examId: string, title: string]
  moveExam: [examId: string, title: string]
}>()

const { t } = useI18n()

// --- Expand state ---
const expanded = ref(false)
const expandedSessions = ref<Set<string>>(new Set())
const loadingSessions = ref<Set<string>>(new Set())
const sessionExams = reactive<Map<string, ArchiveExam[]>>(new Map())

function toggle() {
  expanded.value = !expanded.value
}

async function toggleSession(session: SessionLeaf) {
  const id = session.session_id
  if (expandedSessions.value.has(id)) {
    expandedSessions.value.delete(id)
    return
  }
  expandedSessions.value.add(id)
  if (!sessionExams.has(id)) {
    loadingSessions.value.add(id)
    try {
      sessionExams.set(id, await archiveSessionExams(id))
    } catch {
      sessionExams.set(id, [])
    } finally {
      loadingSessions.value.delete(id)
    }
  }
}

// --- Exposed for parent cache clear ---
function clearExamCache() {
  sessionExams.clear()
}
defineExpose({ clearExamCache })

// --- Status styling ---
const statusClasses: Record<string, string> = {
  ready: 'bg-[var(--color-success-bg,#dcfce7)] text-[var(--color-success-text,#15803d)]',
  pending: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
  analyzing: 'bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]',
  failed: 'bg-[var(--color-error-bg,#fee2e2)] text-[var(--color-error-text,#dc2626)]',
  pending_review: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
}

const statusDots: Record<string, string> = {
  ready: 'bg-[var(--color-success-text,#15803d)]',
  pending: 'bg-[var(--color-warning-text,#92400e)]',
  analyzing: 'bg-[var(--color-info-text,#1e40af)]',
  failed: 'bg-[var(--color-error-text,#dc2626)]',
  pending_review: 'bg-[var(--color-warning-text,#92400e)]',
}

const statusIcons: Record<string, string> = {
  ready: 'text-[var(--color-success-text,#15803d)]',
  pending: 'text-[var(--color-text-secondary)]',
  analyzing: 'text-[var(--color-info-text,#1e40af)]',
  failed: 'text-[var(--color-error-text,#dc2626)]',
  pending_review: 'text-[var(--color-warning-text,#92400e)]',
}
</script>

<template>
  <div>
    <!-- Group header -->
    <button
      class="folder-row w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left transition-colors hover:bg-[var(--color-surface)]"
      :class="expanded ? 'bg-[var(--color-surface)]' : ''"
      :style="{ paddingLeft: `${12 + depth * 20}px` }"
      @click="toggle"
    >
      <!-- Chevron -->
      <svg
        class="w-4 h-4 text-[var(--color-text-secondary)] transition-transform duration-150 flex-shrink-0"
        :class="{ 'rotate-90': expanded }"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>

      <!-- Folder icon -->
      <svg
        class="w-5 h-5 flex-shrink-0"
        :class="expanded ? 'text-[var(--color-primary)]' : 'text-[var(--color-warning-text,#d97706)]'"
        fill="currentColor" viewBox="0 0 24 24"
      >
        <path d="M19.906 9c.382 0 .749.057 1.094.162V9a3 3 0 00-3-3h-3.879a.75.75 0 01-.53-.22L11.47 3.66A2.25 2.25 0 009.879 3H6a3 3 0 00-3 3v3.162A3.756 3.756 0 014.094 9h15.812zM4.094 10.5a2.25 2.25 0 00-2.227 2.568l.857 6A2.25 2.25 0 004.951 21H19.05a2.25 2.25 0 002.227-1.932l.857-6a2.25 2.25 0 00-2.227-2.568H4.094z" />
      </svg>

      <!-- Program icon -->
      <span v-if="node.icon" class="text-base flex-shrink-0">{{ node.icon }}</span>

      <!-- Label -->
      <span class="flex-1 text-sm font-semibold text-[var(--color-text-primary)] truncate">
        {{ node.label }}
      </span>

      <!-- Exam count badge -->
      <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]">
        {{ node.examCount }}
      </span>
    </button>

    <!-- Children (nested group nodes) -->
    <div v-if="expanded && node.children.length > 0" class="relative">
      <ExamTreeNode
        v-for="child in node.children"
        :key="child.key"
        :node="child"
        :depth="depth + 1"
        @delete-session="(sid, cnt) => emit('deleteSession', sid, cnt)"
        @delete-exam="(eid, title) => emit('deleteExam', eid, title)"
        @move-exam="(eid, title) => emit('moveExam', eid, title)"
      />
    </div>

    <!-- Session leaves -->
    <div v-if="expanded && node.sessions.length > 0" class="relative">
      <div
        v-for="session in node.sessions"
        :key="session.session_id"
      >
        <!-- Session row -->
        <button
          class="group/session folder-row w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors hover:bg-[var(--color-surface)]"
          :class="expandedSessions.has(session.session_id) ? 'bg-[var(--color-surface)]' : ''"
          :style="{ paddingLeft: `${12 + (depth + 1) * 20}px` }"
          @click="toggleSession(session)"
        >
          <svg
            class="w-3.5 h-3.5 text-[var(--color-text-secondary)] transition-transform duration-150 flex-shrink-0"
            :class="{ 'rotate-90': expandedSessions.has(session.session_id) }"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>

          <svg
            class="w-4 h-4 flex-shrink-0"
            :class="expandedSessions.has(session.session_id)
              ? 'text-[var(--color-primary)]'
              : 'text-[var(--color-warning-text,#d97706)]'"
            fill="currentColor" viewBox="0 0 24 24"
          >
            <path d="M19.906 9c.382 0 .749.057 1.094.162V9a3 3 0 00-3-3h-3.879a.75.75 0 01-.53-.22L11.47 3.66A2.25 2.25 0 009.879 3H6a3 3 0 00-3 3v3.162A3.756 3.756 0 014.094 9h15.812zM4.094 10.5a2.25 2.25 0 00-2.227 2.568l.857 6A2.25 2.25 0 004.951 21H19.05a2.25 2.25 0 002.227-1.932l.857-6a2.25 2.25 0 00-2.227-2.568H4.094z" />
          </svg>

          <span class="flex-1 text-sm font-medium text-[var(--color-text-primary)] truncate">
            {{ session.seasonLabel }} {{ session.year }}
          </span>

          <!-- Status badge -->
          <span
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold"
            :class="session.ready_count === session.exam_count && session.exam_count > 0
              ? 'bg-[var(--color-success-bg,#dcfce7)] text-[var(--color-success-text,#15803d)]'
              : 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]'"
          >
            <span
              class="w-1.5 h-1.5 rounded-full"
              :class="session.ready_count === session.exam_count && session.exam_count > 0
                ? 'bg-[var(--color-success-text,#15803d)]'
                : 'bg-[var(--color-warning-text,#92400e)]'"
            />
            {{ t('panel.examArchive.session.examCount', { ready: session.ready_count, total: session.exam_count }) }}
          </span>

          <span
            v-if="session.total_questions > 0"
            class="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]"
          >
            {{ t('panel.examArchive.session.totalQuestions', { count: session.total_questions }) }}
          </span>

          <!-- Delete session -->
          <button
            @click.stop="emit('deleteSession', session.session_id, session.exam_count)"
            class="opacity-0 group-hover/session:opacity-100 p-1 rounded hover:bg-[var(--color-error-bg,#fee2e2)] text-[var(--color-text-secondary)] hover:text-[var(--color-error-text,#dc2626)] transition-all"
            :title="t('panel.examArchive.crud.deleteFolder')"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
            </svg>
          </button>
        </button>

        <!-- Exam leaves (lazy-loaded) -->
        <div v-if="expandedSessions.has(session.session_id)" class="relative">
          <div
            v-if="loadingSessions.has(session.session_id)"
            class="flex items-center gap-2 px-3 py-2"
            :style="{ paddingLeft: `${12 + (depth + 2) * 20}px` }"
          >
            <div class="animate-spin rounded-full h-4 w-4 border-2 border-[var(--color-border)] border-t-[var(--color-primary)]" />
            <span class="text-xs text-[var(--color-text-secondary)]">{{ t('panel.examArchive.analyzing') }}</span>
          </div>
          <template v-else>
            <div
              v-for="exam in (sessionExams.get(session.session_id) || [])"
              :key="exam.exam_id"
              class="group/exam folder-row flex items-center gap-2.5 px-3 py-1.5 rounded-lg transition-colors hover:bg-[var(--color-surface)]"
              :style="{ paddingLeft: `${12 + (depth + 2) * 20}px` }"
            >
              <div class="w-3.5" />
              <svg
                class="w-4 h-4 flex-shrink-0"
                :class="statusIcons[exam.analysis_status] || statusIcons.pending"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
              <span class="flex-1 text-sm text-[var(--color-text-primary)]">
                {{ exam.title || exam.part || t('panel.examArchive.session.title') }}
              </span>
              <span
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold"
                :class="statusClasses[exam.analysis_status] || statusClasses.pending"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="statusDots[exam.analysis_status] || statusDots.pending" />
                {{ t(`panel.examArchive.status.${exam.analysis_status}`) }}
              </span>
              <span class="text-[10px] text-[var(--color-text-secondary)]">
                {{ t('panel.examArchive.questions', { count: exam.question_count }) }}
              </span>
              <!-- Move -->
              <button
                @click.stop="emit('moveExam', exam.exam_id, exam.title || exam.part || '')"
                class="opacity-0 group-hover/exam:opacity-100 p-1 rounded hover:bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-text-secondary)] hover:text-[var(--color-info-text,#1e40af)] transition-all"
                :title="t('panel.examArchive.crud.moveExam')"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                </svg>
              </button>
              <!-- Delete -->
              <button
                @click.stop="emit('deleteExam', exam.exam_id, exam.title || exam.part || '')"
                class="opacity-0 group-hover/exam:opacity-100 p-1 rounded hover:bg-[var(--color-error-bg,#fee2e2)] text-[var(--color-text-secondary)] hover:text-[var(--color-error-text,#dc2626)] transition-all"
                :title="t('panel.examArchive.crud.deleteExam')"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                </svg>
              </button>
            </div>
            <p
              v-if="(sessionExams.get(session.session_id) || []).length === 0"
              class="text-xs text-[var(--color-text-secondary)] py-2"
              :style="{ paddingLeft: `${12 + (depth + 2) * 20 + 28}px` }"
            >
              {{ t('panel.examArchive.noExams') }}
            </p>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
