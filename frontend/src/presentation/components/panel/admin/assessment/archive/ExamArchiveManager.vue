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
        <p class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ t('panel.examArchive.examCount', { count: exams.length }) }}
        </p>
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
        </div>
      </div>
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

    <!-- Exam List -->
    <div v-else class="flex-1 overflow-y-auto p-4">
      <!-- Empty State -->
      <div v-if="exams.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4 opacity-30">📄</div>
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
          {{ t('panel.examArchive.noExams') }}
        </h3>
        <p class="text-sm text-[var(--color-text-secondary)] mb-4">
          {{ t('panel.examArchive.scanFirst') }}
        </p>
      </div>

      <!-- Exam Cards -->
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ScannedPaper, ArchiveExam } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import {
  archiveScanFolder,
  archiveImportPapers,
  archiveAnalyzeExam,
  archiveAnalyzeAll,
  archiveListExams
} from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import ExamArchiveCard from './ExamArchiveCard.vue'

const { t } = useI18n()

// State
const exams = ref<ArchiveExam[]>([])
const scannedPapers = ref<ScannedPaper[]>([])
const loading = ref(false)
const scanning = ref(false)
const importing = ref(false)
const analyzingAll = ref(false)
const statusMessage = ref('')

let refreshInterval: ReturnType<typeof setInterval> | null = null

// Computed
const hasPendingExams = computed(() =>
  exams.value.some((e) => e.analysis_status === 'pending')
)

const hasAnalyzingExams = computed(() =>
  exams.value.some((e) => e.analysis_status === 'analyzing')
)

// Methods
const loadExams = async () => {
  try {
    exams.value = await archiveListExams()
  } catch (err) {
    console.error('Failed to load archive exams:', err)
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
  await loadExams()
  loading.value = false

  if (hasAnalyzingExams.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>
