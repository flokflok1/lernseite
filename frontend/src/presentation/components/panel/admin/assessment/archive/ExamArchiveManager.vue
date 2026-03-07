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
    <!-- Header -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <h2 class="text-lg font-bold text-[var(--color-text-primary)]">
        {{ t('panel.examArchive.title') }}
      </h2>
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ t('panel.examArchive.subtitle') }}
      </p>
    </div>

    <!-- Action Bar -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between flex-wrap gap-2">
        <div class="flex items-center gap-3">
          <p class="text-sm font-medium text-[var(--color-text-primary)]">
            {{ t('panel.examArchive.examCount', { count: exams.length }) }}
          </p>
          <!-- View Mode Toggle -->
          <div class="flex rounded-lg border border-[var(--color-border)] overflow-hidden">
            <button
              v-for="mode in (['flat', 'grouped'] as const)"
              :key="mode"
              @click="viewMode = mode"
              class="px-3 py-1 text-xs font-medium transition-colors"
              :class="viewMode === mode
                ? 'bg-[var(--color-primary)] text-white'
                : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)]'"
            >
              {{ t(`panel.examArchive.viewMode.${mode}`) }}
            </button>
          </div>
        </div>
        <div class="flex gap-2">
          <!-- Scan Folder -->
          <button
            @click="handleScan"
            :disabled="scanning"
            class="px-3 py-1.5 text-white rounded text-sm transition-colors flex items-center gap-1"
            style="background-color: var(--color-primary, #7c3aed);"
            :class="{ 'opacity-50 cursor-not-allowed': scanning }"
          >
            <span>{{ scanning ? t('panel.examArchive.scanning') : t('panel.examArchive.scanFolder') }}</span>
          </button>

          <!-- Import All (only visible after scan) -->
          <button
            v-if="scannedPapers.length > 0"
            @click="handleImport"
            :disabled="importing"
            class="px-3 py-1.5 text-white rounded text-sm transition-colors flex items-center gap-1"
            style="background-color: var(--color-success, #16a34a);"
            :class="{ 'opacity-50 cursor-not-allowed': importing }"
          >
            <span>{{ importing ? t('panel.examArchive.importing') : t('panel.examArchive.importAll') }}</span>
          </button>

          <!-- Analyze All -->
          <button
            v-if="hasPendingExams"
            @click="handleAnalyzeAll"
            :disabled="analyzingAll"
            class="px-3 py-1.5 text-white rounded text-sm transition-colors flex items-center gap-1"
            style="background-color: var(--color-info, #2563eb);"
            :class="{ 'opacity-50 cursor-not-allowed': analyzingAll }"
          >
            <span>{{ analyzingAll ? t('panel.examArchive.analyzing') : t('panel.examArchive.analyzeAll') }}</span>
          </button>

          <!-- Upload Button -->
          <button
            @click="showUploadDialog = true"
            class="px-3 py-1.5 text-white rounded text-sm transition-colors flex items-center gap-1"
            style="background-color: var(--color-primary, #7c3aed);"
          >
            {{ t('panel.examArchive.upload.title') }}
          </button>

          <!-- Generate Course Button -->
          <button
            @click="showCourseGenerator = !showCourseGenerator"
            class="px-3 py-1.5 rounded text-sm transition-colors flex items-center gap-1 border"
            :class="showCourseGenerator
              ? 'bg-[var(--color-primary)] text-white border-transparent'
              : 'bg-[var(--color-surface)] text-[var(--color-text-primary)] border-[var(--color-border)] hover:bg-[var(--color-surface-secondary)]'"
          >
            {{ t('panel.examCourseGenerator.title') }}
          </button>

          <!-- Pending Review Count -->
          <span
            v-if="pendingReviewCount > 0"
            class="px-2 py-1 rounded text-xs font-medium bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]"
          >
            {{ t('panel.examArchive.moderation.pendingReview') }}: {{ pendingReviewCount }}
          </span>
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
    <div v-if="showCourseGenerator" class="px-4 py-3">
      <ExamCourseGenerator />
    </div>

    <!-- Status Messages -->
    <div v-if="statusMessage" class="px-4 py-2">
      <div
        class="rounded-lg p-3 border text-sm"
        style="background-color: var(--color-info-bg, #eff6ff); border-color: var(--color-info-border, #bfdbfe); color: var(--color-info-text, #1e40af);"
      >
        {{ statusMessage }}
      </div>
    </div>

    <!-- Scanned Papers Preview -->
    <div v-if="scannedPapers.length > 0 && !importing" class="px-4 py-2">
      <div
        class="rounded-lg p-3 border text-sm"
        style="background-color: var(--color-success-bg, #dcfce7); border-color: var(--color-success-border, #bbf7d0); color: var(--color-success-text, #15803d);"
      >
        {{ t('panel.examArchive.papersFound', { count: scannedPapers.length }) }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ t('panel.examArchive.analyzing') }}</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="flex-1 overflow-y-auto p-4">
      <!-- Empty State -->
      <div v-if="exams.length === 0 && sessionGroups.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4 opacity-30">📄</div>
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
          {{ t('panel.examArchive.noExams') }}
        </h3>
        <p class="text-sm text-[var(--color-text-secondary)] mb-4">
          {{ t('panel.examArchive.scanFirst') }}
        </p>
      </div>

      <!-- Grouped Session View -->
      <div v-else-if="viewMode === 'grouped'" class="space-y-6">
        <div v-if="loadingSessions" class="flex justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)]" />
        </div>
        <p
          v-else-if="sessionGroups.length === 0"
          class="text-sm text-[var(--color-text-secondary)] text-center py-8"
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
