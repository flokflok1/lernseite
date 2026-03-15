<!-- ExamArchiveManager - Import, analyze, and manage exam PDFs with folder CRUD. -->
<template>
  <div class="h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Action Bar -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6 py-4">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[var(--color-surface-secondary)] border border-[var(--color-border)]">
          <svg class="w-4 h-4 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>
          <span class="text-sm font-semibold text-[var(--color-text-primary)]">{{ t('panel.examArchive.examCount', { count: exams.length }) }}</span>
        </div>
        <div class="flex items-center gap-2.5">
          <button @click="handleScan" :disabled="scanning" class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all bg-[var(--color-primary)] hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>
            {{ scanning ? t('panel.examArchive.scanning') : t('panel.examArchive.scanFolder') }}
          </button>
          <button v-if="scannedPapers.length > 0" @click="handleImport" :disabled="importing" class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed" style="background-color: var(--color-success-text, #16a34a);">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" /></svg>
            {{ importing ? t('panel.examArchive.importing') : t('panel.examArchive.importAll') }}
          </button>
          <button v-if="hasPendingExams" @click="handleAnalyzeAll" :disabled="analyzingAll" class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed" style="background-color: var(--color-info-text, #2563eb);">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" /></svg>
            {{ analyzingAll ? t('panel.examArchive.analyzing') : t('panel.examArchive.analyzeAll') }}
          </button>
          <button @click="showUploadDialog = true" class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all bg-[var(--color-primary)] hover:opacity-90">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" /></svg>
            {{ t('panel.examArchive.upload.title') }}
          </button>
          <GroupConfigPanel
            :levels="groupLevels"
            @toggle="toggleLevel"
            @move-up="moveLevelUp"
            @move-down="moveLevelDown"
            @reset="resetConfig"
          />
          <div v-if="pendingReviewCount > 0" class="inline-flex items-center gap-2 px-3.5 py-2 rounded-full text-xs font-semibold bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)] border border-[var(--color-warning-text)]/20">
            <span class="relative flex h-2.5 w-2.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--color-warning-text,#92400e)] opacity-40"></span>
              <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-[var(--color-warning-text,#92400e)]"></span>
            </span>
            {{ t('panel.examArchive.moderation.pendingReview') }}: {{ pendingReviewCount }}
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Dialog -->
    <ExamUploadDialog
      :visible="showUploadDialog"
      @close="showUploadDialog = false"
      @uploaded="handleUploadComplete"
    />

    <!-- Confirm Delete Dialog -->
    <div
      v-if="confirmDialog.visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="confirmDialog.visible = false"
    >
      <div class="bg-[var(--color-surface)] rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-base font-semibold text-[var(--color-text-primary)] mb-2">
          {{ confirmDialog.title }}
        </h3>
        <p class="text-sm text-[var(--color-text-secondary)] mb-4">{{ confirmDialog.message }}</p>
        <div class="flex justify-end gap-2">
          <button
            @click="confirmDialog.visible = false"
            class="px-4 py-2 text-sm border border-[var(--color-border)] rounded text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)]"
          >
            {{ t('panel.examArchive.crud.cancel') }}
          </button>
          <button
            @click="confirmDialog.onConfirm()"
            class="px-4 py-2 text-sm text-white rounded"
            style="background-color: var(--color-error-text, #dc2626);"
          >
            {{ t('actions.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Move Exam Dialog -->
    <div
      v-if="moveDialog.visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="moveDialog.visible = false"
    >
      <div class="bg-[var(--color-surface)] rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
        <h3 class="text-base font-semibold text-[var(--color-text-primary)] mb-1">
          {{ t('panel.examArchive.crud.moveExam') }}
        </h3>
        <p class="text-sm text-[var(--color-text-secondary)] mb-4">{{ moveDialog.examTitle }}</p>
        <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
          {{ t('panel.examArchive.crud.selectTarget') }}
        </label>
        <select
          v-model="moveDialog.targetSessionId"
          class="w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-bg)] text-sm text-[var(--color-text-primary)] mb-4"
        >
          <option value="" disabled>—</option>
          <option
            v-for="s in allSessions"
            :key="s.session_id"
            :value="s.session_id"
          >
            {{ s.label }}
          </option>
        </select>
        <div class="flex justify-end gap-2">
          <button
            @click="moveDialog.visible = false"
            class="px-4 py-2 text-sm border border-[var(--color-border)] rounded text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)]"
          >
            {{ t('panel.examArchive.crud.cancel') }}
          </button>
          <button
            @click="handleMoveExam"
            :disabled="!moveDialog.targetSessionId"
            class="px-4 py-2 text-sm text-white rounded disabled:opacity-50"
            style="background-color: var(--color-primary, #7c3aed);"
          >
            {{ t('panel.examArchive.crud.moveTo') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Status Messages -->
    <div v-if="statusMessage" class="px-6 py-3">
      <div
        class="flex items-center gap-3 rounded-lg px-4 py-3 border text-sm"
        style="background-color: var(--color-info-bg, #eff6ff); border-color: var(--color-info-border, #bfdbfe); color: var(--color-info-text, #1e40af);"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
        </svg>
        <span>{{ statusMessage }}</span>
      </div>
    </div>

    <!-- Scanned Papers Preview -->
    <div v-if="scannedPapers.length > 0 && !importing" class="px-6 py-3">
      <div
        class="flex items-center gap-3 rounded-lg px-4 py-3 border text-sm"
        style="background-color: var(--color-success-bg, #dcfce7); border-color: var(--color-success-border, #bbf7d0); color: var(--color-success-text, #15803d);"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ t('panel.examArchive.papersFound', { count: scannedPapers.length }) }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-2 border-[var(--color-border)] border-t-[var(--color-primary)] mx-auto mb-4"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ t('panel.examArchive.analyzing') }}</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="flex-1 overflow-y-auto px-6 py-5">
      <!-- Empty State -->
      <div v-if="exams.length === 0 && sessionRows.length === 0" class="text-center py-16">
        <div class="mx-auto mb-5 w-16 h-16 rounded-2xl bg-[var(--color-surface-secondary)] border border-[var(--color-border)] flex items-center justify-center">
          <svg class="w-8 h-8 text-[var(--color-text-secondary)] opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
          {{ t('panel.examArchive.noExams') }}
        </h3>
        <p class="text-sm text-[var(--color-text-secondary)] max-w-sm mx-auto">
          {{ t('panel.examArchive.scanFirst') }}
        </p>
      </div>

      <!-- Folder Explorer View -->
      <div v-else-if="loadingSessions" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-2 border-[var(--color-border)] border-t-[var(--color-primary)]" />
      </div>
      <p
        v-else-if="sessionRows.length === 0"
        class="text-sm text-[var(--color-text-secondary)] text-center py-12"
      >
        {{ t('panel.examArchive.session.noSessions') }}
      </p>
      <ExamFolderExplorer
        v-else
        ref="folderExplorerRef"
        :nodes="tree"
        @delete-session="handleDeleteSession"
        @delete-exam="confirmDeleteExam"
        @move-exam="openMoveDialog"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ScannedPaper, ArchiveExam, SessionRow } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import {
  archiveScanFolder,
  archiveImportPapers,
  archiveAnalyzeAll,
  archiveListExams,
  archiveListSessions,
  archiveDeleteSession,
  archiveDeleteExam,
  archiveMoveExam,
} from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { useExamArchiveTree } from '@/application/composables/panel/admin/assessment'
import ExamUploadDialog from './ExamUploadDialog.vue'
import ExamFolderExplorer from './ExamFolderExplorer.vue'
import GroupConfigPanel from './GroupConfigPanel.vue'

const { t, locale } = useI18n()

// State
const exams = ref<ArchiveExam[]>([])
const sessionRows = ref<SessionRow[]>([])
const scannedPapers = ref<ScannedPaper[]>([])
const loading = ref(false)
const loadingSessions = ref(false)
const scanning = ref(false)
const importing = ref(false)
const analyzingAll = ref(false)
const statusMessage = ref('')
const showUploadDialog = ref(false)
const folderExplorerRef = ref<InstanceType<typeof ExamFolderExplorer> | null>(null)

// Dynamic tree builder
const {
  groupLevels,
  tree,
  allSessions,
  toggleLevel,
  moveLevelUp,
  moveLevelDown,
  resetConfig,
} = useExamArchiveTree(sessionRows)

const confirmDialog = ref({
  visible: false,
  title: '',
  message: '',
  onConfirm: () => {},
})

const moveDialog = ref({
  visible: false,
  examId: '',
  examTitle: '',
  targetSessionId: '',
})

let refreshInterval: ReturnType<typeof setInterval> | null = null

// Computed
const hasPendingExams = computed(() =>
  exams.value.some((e) => e.analysis_status === 'pending')
)

const hasAnalyzingExams = computed(() =>
  exams.value.some((e) => e.analysis_status === 'analyzing')
)

const pendingReviewCount = computed(() =>
  exams.value.filter((e) => e.analysis_status === 'pending_review').length
)

// Methods
const loadExams = async () => {
  try {
    exams.value = await archiveListExams()
  } catch (err) {
    console.error('Failed to load archive exams:', err)
  }
}

const loadSessions = async () => {
  loadingSessions.value = true
  try {
    sessionRows.value = await archiveListSessions()
  } catch (err) {
    console.error('Failed to load sessions:', err)
  } finally {
    loadingSessions.value = false
  }
}

const handleScan = async () => {
  scanning.value = true
  statusMessage.value = ''
  try {
    scannedPapers.value = await archiveScanFolder()
    if (scannedPapers.value.length === 0) {
      statusMessage.value = t('panel.examArchive.noPapersFound')
    }
  } catch (err) {
    console.error('Scan failed:', err)
    statusMessage.value = String(err)
  } finally {
    scanning.value = false
  }
}

const handleImport = async () => {
  importing.value = true
  statusMessage.value = ''
  try {
    const result = await archiveImportPapers(scannedPapers.value)
    statusMessage.value = t('panel.examArchive.importSuccess', {
      imported: result.imported,
      skipped: result.skipped
    })
    scannedPapers.value = []
    await Promise.all([loadExams(), loadSessions()])
  } catch (err) {
    console.error('Import failed:', err)
    statusMessage.value = String(err)
  } finally {
    importing.value = false
  }
}

const handleAnalyzeAll = async () => {
  analyzingAll.value = true
  statusMessage.value = ''
  try {
    const result = await archiveAnalyzeAll()
    statusMessage.value = t('panel.examArchive.analyzeTriggered', {
      count: result.triggered
    })
    await Promise.all([loadExams(), loadSessions()])
    startAutoRefresh()
  } catch (err) {
    console.error('Analyze all failed:', err)
    statusMessage.value = String(err)
  } finally {
    analyzingAll.value = false
  }
}

const handleUploadComplete = async (_examId: string) => {
  statusMessage.value = t('panel.examArchive.upload.success')
  await Promise.all([loadExams(), loadSessions()])
}

// --- CRUD Handlers ---
const handleDeleteSession = (sessionId: string, examCount: number) => {
  if (examCount > 0) {
    statusMessage.value = t('panel.examArchive.crud.folderNotEmpty')
    return
  }
  confirmDialog.value = {
    visible: true,
    title: t('panel.examArchive.crud.deleteFolder'),
    message: t('panel.examArchive.crud.confirmDeleteFolder'),
    onConfirm: async () => {
      confirmDialog.value.visible = false
      try {
        await archiveDeleteSession(sessionId)
        statusMessage.value = t('panel.examArchive.crud.folderDeleted')
        await loadSessions()
      } catch (err: any) {
        statusMessage.value = err?.response?.data?.error || t('panel.examArchive.crud.deleteError')
      }
    },
  }
}

const confirmDeleteExam = (examId: string, title: string) => {
  confirmDialog.value = {
    visible: true,
    title: `${t('panel.examArchive.crud.deleteExam')}: ${title}`,
    message: t('panel.examArchive.crud.confirmDeleteExam'),
    onConfirm: async () => {
      confirmDialog.value.visible = false
      try {
        await archiveDeleteExam(examId)
        statusMessage.value = t('panel.examArchive.crud.examDeleted')
        folderExplorerRef.value?.clearExamCache()
        await Promise.all([loadExams(), loadSessions()])
      } catch (err: any) {
        statusMessage.value = err?.response?.data?.error || t('panel.examArchive.crud.deleteError')
      }
    },
  }
}

const openMoveDialog = (examId: string, title: string) => {
  moveDialog.value = {
    visible: true,
    examId,
    examTitle: title,
    targetSessionId: '',
  }
}

const handleMoveExam = async () => {
  const { examId, targetSessionId } = moveDialog.value
  if (!targetSessionId) return
  moveDialog.value.visible = false
  try {
    await archiveMoveExam(examId, targetSessionId)
    statusMessage.value = t('panel.examArchive.crud.examMoved')
    folderExplorerRef.value?.clearExamCache()
    await Promise.all([loadExams(), loadSessions()])
  } catch (err: any) {
    statusMessage.value = err?.response?.data?.error || t('panel.examArchive.crud.moveError')
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshInterval = setInterval(async () => {
    await Promise.all([loadExams(), loadSessions()])
    if (!hasAnalyzingExams.value) {
      stopAutoRefresh()
    }
  }, 10000)
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

// Lifecycle
onMounted(async () => {
  loading.value = true
  await Promise.all([loadExams(), loadSessions()])
  loading.value = false

  if (hasAnalyzingExams.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>
