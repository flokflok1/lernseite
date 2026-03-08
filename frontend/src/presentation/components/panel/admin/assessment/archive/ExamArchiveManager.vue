<!--
  ExamArchiveManager - Admin interface for importing and managing IHK exam PDFs.

  Features:
  - Scan AP1 folder for exam PDFs
  - Import scanned papers into the system
  - Trigger AI analysis for imported exams
  - Auto-refresh while analyses are running
-->

<template>
  <div class="h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Action Bar -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6 py-4">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-4">
          <!-- Exam Count Pill -->
          <div
            class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[var(--color-surface-secondary)] border border-[var(--color-border)]"
          >
            <svg class="w-4 h-4 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            <span class="text-sm font-semibold text-[var(--color-text-primary)]">
              {{ t('panel.examArchive.examCount', { count: exams.length }) }}
            </span>
          </div>

          <!-- View Mode Toggle -->
          <div class="flex rounded-lg border border-[var(--color-border)] overflow-hidden">
            <button
              v-for="mode in (['flat', 'grouped'] as const)"
              :key="mode"
              @click="viewMode = mode"
              class="px-3.5 py-1.5 text-xs font-medium transition-colors"
              :class="viewMode === mode
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)]'"
            >
              {{ t(`panel.examArchive.viewMode.${mode}`) }}
            </button>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <!-- Scan Folder -->
          <button
            @click="handleScan"
            :disabled="scanning"
            class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all bg-[var(--color-primary)] hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <span>{{ scanning ? t('panel.examArchive.scanning') : t('panel.examArchive.scanFolder') }}</span>
          </button>

          <!-- Import All (only visible after scan) -->
          <button
            v-if="scannedPapers.length > 0"
            @click="handleImport"
            :disabled="importing"
            class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style="background-color: var(--color-success-text, #16a34a);"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
            <span>{{ importing ? t('panel.examArchive.importing') : t('panel.examArchive.importAll') }}</span>
          </button>

          <!-- Analyze All -->
          <button
            v-if="hasPendingExams"
            @click="handleAnalyzeAll"
            :disabled="analyzingAll"
            class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style="background-color: var(--color-info-text, #2563eb);"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
            </svg>
            <span>{{ analyzingAll ? t('panel.examArchive.analyzing') : t('panel.examArchive.analyzeAll') }}</span>
          </button>

          <!-- Upload Button -->
          <button
            @click="showUploadDialog = true"
            class="inline-flex items-center gap-2 px-4 py-2 text-white rounded-lg text-sm font-medium transition-all bg-[var(--color-primary)] hover:opacity-90"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
            </svg>
            {{ t('panel.examArchive.upload.title') }}
          </button>

          <!-- Generate Course Button -->
          <button
            @click="showCourseGenerator = !showCourseGenerator"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all border"
            :class="showCourseGenerator
              ? 'bg-[var(--color-primary)] text-white border-transparent'
              : 'bg-[var(--color-surface)] text-[var(--color-text-primary)] border-[var(--color-border)] hover:bg-[var(--color-surface-secondary)]'"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.26 10.147a60.438 60.438 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.906 59.906 0 0112 3.493a59.903 59.903 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
            </svg>
            {{ t('panel.examCourseGenerator.title') }}
          </button>

          <!-- Pending Review Count -->
          <div
            v-if="pendingReviewCount > 0"
            class="inline-flex items-center gap-2 px-3.5 py-2 rounded-full text-xs font-semibold bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)] border border-[var(--color-warning-text)]/20"
          >
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

    <!-- Course Generator (collapsible) -->
    <div v-if="showCourseGenerator" class="px-6 py-4 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
      <ExamCourseGenerator />
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
      <div v-if="exams.length === 0 && sessionGroups.length === 0" class="text-center py-16">
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

      <!-- Grouped Session View -->
      <div v-else-if="viewMode === 'grouped'" class="space-y-8">
        <div v-if="loadingSessions" class="flex justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-2 border-[var(--color-border)] border-t-[var(--color-primary)]" />
        </div>
        <p
          v-else-if="sessionGroups.length === 0"
          class="text-sm text-[var(--color-text-secondary)] text-center py-12"
        >
          {{ t('panel.examArchive.session.noSessions') }}
        </p>
        <ExamTypeSection
          v-else
          v-for="group in sessionGroups"
          :key="group.exam_type"
          :group="group"
        />
      </div>

      <!-- Flat List View -->
      <div v-else class="space-y-3">
        <ExamArchiveCard
          v-for="exam in exams"
          :key="exam.exam_id"
          :exam="exam"
          @analyze="handleAnalyzeSingle"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ScannedPaper, ArchiveExam, SessionGroup } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import {
  archiveScanFolder,
  archiveImportPapers,
  archiveAnalyzeExam,
  archiveAnalyzeAll,
  archiveListExams,
  archiveListSessions,
} from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import ExamArchiveCard from './ExamArchiveCard.vue'
import ExamUploadDialog from './ExamUploadDialog.vue'
import { ExamTypeSection } from './sessions'
import { ExamCourseGenerator } from '../exams'

const { t } = useI18n()

// State
const viewMode = ref<'flat' | 'grouped'>('grouped')
const exams = ref<ArchiveExam[]>([])
const sessionGroups = ref<SessionGroup[]>([])
const scannedPapers = ref<ScannedPaper[]>([])
const loading = ref(false)
const loadingSessions = ref(false)
const scanning = ref(false)
const importing = ref(false)
const analyzingAll = ref(false)
const statusMessage = ref('')
const showUploadDialog = ref(false)
const showCourseGenerator = ref(false)

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
    sessionGroups.value = await archiveListSessions()
  } catch (err) {
    console.error('Failed to load sessions:', err)
  } finally {
    loadingSessions.value = false
  }
}

// Load sessions when switching to grouped view
watch(viewMode, (mode) => {
  if (mode === 'grouped' && sessionGroups.value.length === 0) {
    loadSessions()
  }
})

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
    await loadExams()
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
    await loadExams()
    startAutoRefresh()
  } catch (err) {
    console.error('Analyze all failed:', err)
    statusMessage.value = String(err)
  } finally {
    analyzingAll.value = false
  }
}

const handleAnalyzeSingle = async (examId: string) => {
  try {
    await archiveAnalyzeExam(examId)
    await loadExams()
    startAutoRefresh()
  } catch (err) {
    console.error('Analyze failed:', err)
  }
}

const handleUploadComplete = async (_examId: string) => {
  statusMessage.value = t('panel.examArchive.upload.success')
  await loadExams()
  if (viewMode.value === 'grouped') {
    await loadSessions()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshInterval = setInterval(async () => {
    await loadExams()
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
