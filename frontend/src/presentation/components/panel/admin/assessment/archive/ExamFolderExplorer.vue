<!--
  ExamFolderExplorer - Windows Explorer-like drill-down view for exam archive.

  Hierarchy:
  - Exam Type (e.g., "Fachinformatiker Systemintegration")
    - Region / Bundesland (e.g., "Baden-Württemberg")
      - Session (e.g., "Sommer 2024")
        - Exam parts (e.g., "AP1", "GA1") — loaded on demand
-->

<template>
  <div class="space-y-1">
    <!-- Level 0: Exam Types -->
    <div v-for="group in groups" :key="group.exam_type">
      <button
        class="folder-row w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left transition-colors hover:bg-[var(--color-surface)]"
        :class="expandedTypes.has(group.exam_type) ? 'bg-[var(--color-surface)]' : ''"
        @click="toggleType(group.exam_type)"
      >
        <svg
          class="w-4 h-4 text-[var(--color-text-secondary)] transition-transform duration-150 flex-shrink-0"
          :class="{ 'rotate-90': expandedTypes.has(group.exam_type) }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>

        <!-- Folder icon -->
        <svg class="w-5 h-5 flex-shrink-0" :class="expandedTypes.has(group.exam_type) ? 'text-[var(--color-primary)]' : 'text-[var(--color-warning-text,#d97706)]'" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19.906 9c.382 0 .749.057 1.094.162V9a3 3 0 00-3-3h-3.879a.75.75 0 01-.53-.22L11.47 3.66A2.25 2.25 0 009.879 3H6a3 3 0 00-3 3v3.162A3.756 3.756 0 014.094 9h15.812zM4.094 10.5a2.25 2.25 0 00-2.227 2.568l.857 6A2.25 2.25 0 004.951 21H19.05a2.25 2.25 0 002.227-1.932l.857-6a2.25 2.25 0 00-2.227-2.568H4.094z" />
        </svg>

        <span class="flex-1 text-sm font-semibold text-[var(--color-text-primary)] truncate">
          {{ resolveI18n(group.display_name) }}
        </span>

        <!-- Parts pills -->
        <span
          v-for="part in (group.parts || [])"
          :key="part"
          class="hidden sm:inline-flex px-2 py-0.5 rounded-md text-[10px] font-semibold bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]"
        >
          {{ part }}
        </span>

        <!-- Session count -->
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]">
          {{ countSessions(group) }}
        </span>
      </button>

      <!-- Level 1: Regions -->
      <div v-if="expandedTypes.has(group.exam_type)" class="relative ml-5 mt-0.5">
        <div class="guide-line"></div>
        <div
          v-for="(region, regionCode) in group.regions"
          :key="regionCode"
          class="relative"
        >
          <button
            class="folder-row w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors hover:bg-[var(--color-surface)]"
            :class="isRegionExpanded(group.exam_type, regionCode as string) ? 'bg-[var(--color-surface)]' : ''"
            @click="toggleRegion(group.exam_type, regionCode as string)"
          >
            <svg
              class="w-3.5 h-3.5 text-[var(--color-text-secondary)] transition-transform duration-150 flex-shrink-0"
              :class="{ 'rotate-90': isRegionExpanded(group.exam_type, regionCode as string) }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>

            <!-- Location icon -->
            <svg class="w-4 h-4 text-[var(--color-text-secondary)] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
            </svg>

            <span class="flex-1 text-sm font-medium text-[var(--color-text-primary)] truncate">
              {{ resolveRegionName(region) }}
            </span>

            <span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
              {{ region.sessions.length }}
            </span>
          </button>

          <!-- Level 2: Sessions -->
          <div v-if="isRegionExpanded(group.exam_type, regionCode as string)" class="relative ml-5 mt-0.5">
            <div class="guide-line"></div>
            <div
              v-for="session in region.sessions"
              :key="session.session_id"
              class="relative"
            >
              <button
                class="folder-row w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors hover:bg-[var(--color-surface)]"
                :class="expandedSessions.has(session.session_id) ? 'bg-[var(--color-surface)]' : ''"
                @click="toggleSession(session)"
              >
                <svg
                  class="w-3.5 h-3.5 text-[var(--color-text-secondary)] transition-transform duration-150 flex-shrink-0"
                  :class="{ 'rotate-90': expandedSessions.has(session.session_id) }"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>

                <!-- Calendar icon -->
                <svg class="w-4 h-4 text-[var(--color-info-text,#2563eb)] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                </svg>

                <span class="text-sm font-medium text-[var(--color-text-primary)]">
                  {{ t(`panel.examArchive.session.season.${session.season}`) }} {{ session.year }}
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
                  ></span>
                  {{ t('panel.examArchive.session.examCount', { ready: session.ready_count, total: session.exam_count }) }}
                </span>

                <!-- Question count -->
                <span
                  v-if="session.total_questions > 0"
                  class="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]"
                >
                  {{ t('panel.examArchive.session.totalQuestions', { count: session.total_questions }) }}
                </span>

                <!-- Tags -->
                <span
                  v-for="tag in session.tags"
                  :key="tag"
                  class="hidden lg:inline-flex px-2 py-0.5 rounded-full text-[10px] font-medium bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)]"
                >
                  {{ tag }}
                </span>
              </button>

              <!-- Level 3: Exam parts (lazy-loaded) -->
              <div v-if="expandedSessions.has(session.session_id)" class="relative ml-5 mt-0.5 mb-1">
                <div class="guide-line"></div>
                <div v-if="loadingSessions.has(session.session_id)" class="flex items-center gap-2 px-3 py-2">
                  <div class="animate-spin rounded-full h-4 w-4 border-2 border-[var(--color-border)] border-t-[var(--color-primary)]"></div>
                  <span class="text-xs text-[var(--color-text-secondary)]">{{ t('panel.examArchive.analyzing') }}</span>
                </div>
                <template v-else>
                  <div
                    v-for="exam in (sessionExamsMap.get(session.session_id) || [])"
                    :key="exam.exam_id"
                    class="folder-row flex items-center gap-2.5 px-3 py-1.5 rounded-lg transition-colors hover:bg-[var(--color-surface)]"
                  >
                    <!-- No expand arrow (leaf node) -->
                    <div class="w-3.5"></div>

                    <!-- Document icon -->
                    <svg class="w-4 h-4 flex-shrink-0" :class="statusIconColor(exam.analysis_status)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>

                    <span class="text-sm text-[var(--color-text-primary)]">
                      {{ exam.part || exam.title }}
                    </span>

                    <!-- Status pill -->
                    <span
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold"
                      :class="statusClass(exam.analysis_status)"
                    >
                      <span class="w-1.5 h-1.5 rounded-full" :class="statusDotClass(exam.analysis_status)"></span>
                      {{ t(`panel.examArchive.status.${exam.analysis_status}`) }}
                    </span>

                    <!-- Question count -->
                    <span class="text-[10px] text-[var(--color-text-secondary)]">
                      {{ t('panel.examArchive.questions', { count: exam.question_count }) }}
                    </span>
                  </div>
                  <p
                    v-if="(sessionExamsMap.get(session.session_id) || []).length === 0"
                    class="text-xs text-[var(--color-text-secondary)] px-3 py-2 ml-7"
                  >
                    {{ t('panel.examArchive.noExams') }}
                  </p>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SessionGroup, SessionRegion, ArchiveExam } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import { archiveSessionExams } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'

interface Props {
  groups: SessionGroup[]
}

defineProps<Props>()
const { t, locale } = useI18n()

// Expand state
const expandedTypes = ref<Set<string>>(new Set())
const expandedRegions = ref<Set<string>>(new Set())
const expandedSessions = ref<Set<string>>(new Set())
const loadingSessions = ref<Set<string>>(new Set())
const sessionExamsMap = reactive<Map<string, ArchiveExam[]>>(new Map())

// i18n helpers
const resolveI18n = (names: Record<string, string>): string =>
  names?.[locale.value] || names?.de || Object.values(names)[0] || ''

const resolveRegionName = (region: SessionRegion): string => {
  if (!region.region_name) return region.region_code
  return (region.region_name as Record<string, string>)[locale.value]
    || (region.region_name as Record<string, string>).de
    || region.region_code
}

// Counts
const countSessions = (group: SessionGroup): number =>
  Object.values(group.regions).reduce((sum, r) => sum + r.sessions.length, 0)

// Toggle functions
const toggleType = (examType: string) => {
  if (expandedTypes.value.has(examType)) {
    expandedTypes.value.delete(examType)
  } else {
    expandedTypes.value.add(examType)
  }
}

const regionKey = (examType: string, regionCode: string) => `${examType}:${regionCode}`

const isRegionExpanded = (examType: string, regionCode: string) =>
  expandedRegions.value.has(regionKey(examType, regionCode))

const toggleRegion = (examType: string, regionCode: string) => {
  const key = regionKey(examType, regionCode)
  if (expandedRegions.value.has(key)) {
    expandedRegions.value.delete(key)
  } else {
    expandedRegions.value.add(key)
  }
}

const toggleSession = async (session: { session_id: string }) => {
  const id = session.session_id
  if (expandedSessions.value.has(id)) {
    expandedSessions.value.delete(id)
    return
  }
  expandedSessions.value.add(id)

  if (!sessionExamsMap.has(id)) {
    loadingSessions.value.add(id)
    try {
      const exams = await archiveSessionExams(id)
      sessionExamsMap.set(id, exams)
    } catch (err) {
      console.error('Failed to load session exams:', err)
      sessionExamsMap.set(id, [])
    } finally {
      loadingSessions.value.delete(id)
    }
  }
}

// Status styling
const statusClass = (status: string): string => {
  const map: Record<string, string> = {
    ready: 'bg-[var(--color-success-bg,#dcfce7)] text-[var(--color-success-text,#15803d)]',
    pending: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
    analyzing: 'bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]',
    failed: 'bg-[var(--color-error-bg,#fee2e2)] text-[var(--color-error-text,#dc2626)]',
    pending_review: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
  }
  return map[status] || map.pending
}

const statusDotClass = (status: string): string => {
  const map: Record<string, string> = {
    ready: 'bg-[var(--color-success-text,#15803d)]',
    pending: 'bg-[var(--color-warning-text,#92400e)]',
    analyzing: 'bg-[var(--color-info-text,#1e40af)]',
    failed: 'bg-[var(--color-error-text,#dc2626)]',
    pending_review: 'bg-[var(--color-warning-text,#92400e)]',
  }
  return map[status] || map.pending
}

const statusIconColor = (status: string): string => {
  const map: Record<string, string> = {
    ready: 'text-[var(--color-success-text,#15803d)]',
    pending: 'text-[var(--color-text-secondary)]',
    analyzing: 'text-[var(--color-info-text,#1e40af)]',
    failed: 'text-[var(--color-error-text,#dc2626)]',
    pending_review: 'text-[var(--color-warning-text,#92400e)]',
  }
  return map[status] || map.pending
}
</script>

<style scoped>
.guide-line {
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--color-border);
  opacity: 0.3;
}
</style>
