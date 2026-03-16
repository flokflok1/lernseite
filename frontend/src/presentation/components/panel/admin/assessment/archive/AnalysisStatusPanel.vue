<!-- AnalysisStatusPanel - Floating bottom-right panel showing Vision AI analysis progress. -->
<template>
  <Teleport to="body">
    <div
      v-if="hasActiveAnalysis && analysisStatus"
      class="fixed bottom-4 right-4 w-80 rounded-xl border border-[var(--color-border)]
             bg-[var(--color-surface)] shadow-2xl z-50 overflow-hidden"
    >
      <!-- Header -->
      <div
        class="px-4 py-3 bg-[var(--color-surface-elevated)] border-b border-[var(--color-border)]
               flex items-center justify-between"
      >
        <div class="flex items-center gap-2">
          <div class="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent" />
          <span class="text-sm font-semibold text-[var(--color-text)]">
            {{ t('panel.examArchive.analysisStatus') }}
          </span>
        </div>
        <span class="text-xs text-[var(--color-text-secondary)]">
          {{ analysisStatus.ready }}/{{ analysisStatus.total }}
        </span>
      </div>

      <!-- Progress bar -->
      <div class="h-1.5 bg-[var(--color-background)]">
        <div
          class="h-full bg-gradient-to-r from-blue-500 to-emerald-500 transition-all duration-500"
          :style="{ width: progressPercent + '%' }"
        />
      </div>

      <!-- Stats -->
      <div class="px-4 py-2 flex gap-4 text-xs text-[var(--color-text-secondary)]">
        <span v-if="analysisStatus.analyzing > 0" class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          {{ analysisStatus.analyzing }} {{ t('panel.examArchive.statusAnalyzing') }}
        </span>
        <span v-if="analysisStatus.pending > 0" class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-amber-500" />
          {{ analysisStatus.pending }} {{ t('panel.examArchive.statusPending') }}
        </span>
        <span v-if="analysisStatus.failed > 0" class="flex items-center gap-1 text-red-400">
          <span class="w-2 h-2 rounded-full bg-red-500" />
          {{ analysisStatus.failed }} {{ t('panel.examArchive.statusFailed') }}
        </span>
      </div>

      <!-- Queue list -->
      <div class="max-h-48 overflow-y-auto border-t border-[var(--color-border)]">
        <div
          v-for="item in analysisStatus.queue.slice(0, 8)"
          :key="item.exam_id"
          class="px-4 py-2 flex items-center justify-between text-xs border-b border-[var(--color-border)]/50"
        >
          <span class="text-[var(--color-text)] truncate flex-1 mr-2">{{ item.title }}</span>
          <span
            class="px-1.5 py-0.5 rounded text-[10px] font-medium shrink-0"
            :class="item.status === 'analyzing'
              ? 'bg-blue-500/20 text-blue-400'
              : 'bg-amber-500/20 text-amber-400'"
          >
            {{ item.status === 'analyzing'
              ? t('panel.examArchive.statusAnalyzing')
              : t('panel.examArchive.statusPending') }}
          </span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  archiveGetAnalysisStatus,
  type AnalysisStatus,
} from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

const { t } = useI18n()

const analysisStatus = ref<AnalysisStatus | null>(null)
let statusInterval: ReturnType<typeof setInterval> | null = null

const hasActiveAnalysis = computed(() =>
  analysisStatus.value != null
  && (analysisStatus.value.pending > 0 || analysisStatus.value.analyzing > 0),
)

const progressPercent = computed(() => {
  if (!analysisStatus.value || analysisStatus.value.total === 0) return 0
  return Math.round((analysisStatus.value.ready / analysisStatus.value.total) * 100)
})

const loadAnalysisStatus = async () => {
  try {
    analysisStatus.value = await archiveGetAnalysisStatus()
    // Stop polling when nothing is processing
    if (
      analysisStatus.value.pending === 0
      && analysisStatus.value.analyzing === 0
    ) {
      if (statusInterval) {
        clearInterval(statusInterval)
        statusInterval = null
      }
    }
  } catch {
    // Silently ignore — panel is informational only
  }
}

onMounted(() => {
  loadAnalysisStatus()
  statusInterval = setInterval(loadAnalysisStatus, 5000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
    statusInterval = null
  }
})
</script>
