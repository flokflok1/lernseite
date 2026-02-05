<template>
  <div class="panel-course-detail-page min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
      <p class="text-gray-600 dark:text-gray-400">{{ $t('panel.courseDetail.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex flex-col items-center justify-center min-h-screen p-6">
      <div class="max-w-md w-full bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <p class="text-red-700 dark:text-red-300 mb-4">{{ error }}</p>
        <button
          @click="initialize"
          class="mt-3 px-3 py-1.5 rounded text-xs transition-colors text-white"
          style="background-color: var(--color-error, #dc2626);"
        >
          {{ $t('panel.courseDetail.retry') }}
        </button>
      </div>
    </div>

    <!-- Course Details -->
    <div v-else-if="course">
      <!-- Course Detail Header Component -->
      <CourseDetailHeader
        :course="course"
        :status-badge-style="statusBadgeStyle"
        :status-text="statusText"
        :language-label="languageLabel"
        :level-label="levelLabel"
        :show-ad-badge="showAdBadge"
        :show-premium-badge="showPremiumBadge"
        :lesson-count="lessonCount"
        :file-count="fileCount"
        :revenue-display="revenueDisplay"
        :rating-display="ratingDisplay"
        :completion-rate-display="completionRateDisplay"
        @open-chapters="openChaptersWindow"
        @open-files="openFilesWindow"
      />

      <!-- Content Grid -->
      <div class="px-4 py-2 grid grid-cols-1 lg:grid-cols-2 gap-3">
        <!-- Left Column: Quick Actions -->
        <div>
          <CourseQuickActions
            :status="course.status"
            @open-chapters="openChaptersWindow"
            @open-files="openFilesWindow"
            @open-exams="openExamsWindow"
            @generate-exam="generateExam"
            @open-ai-studio="openAiStudioWindow"
            @publish="publishCourse"
            @unpublish="unpublishCourse"
            @archive="archiveCourse"
            @edit="openEditorWindow"
          />
        </div>

        <!-- Right Column: Creator Info -->
        <div>
          <CourseCreatorInfo
            :creator-name="course.creator_name"
            :creator-email="course.creator_email"
            :organisation-name="course.organisation_name"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AdminCourseDetailPage
 * =====================
 * Orchestrator page for admin course detail view
 * Refactored from 1319 LOC to ~250 LOC
 */
import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/window.store'
import {
  CourseDetailHeader,
  CourseQuickActions,
  CourseCreatorInfo,
  useCourseDetail
} from '@/presentation/components/content/panel/courses/detail'

// ============================================================================
// Setup
// ============================================================================

interface Props {
  id: string | number
}

const props = defineProps<Props>()
const { t } = useI18n()
const windowStore = useWindowStore()

// ============================================================================
// Course Detail Composable
// ============================================================================

const {
  // State
  course,
  loading,
  error,
  chapters: _chapters,
  // Computed
  lessonCount,
  fileCount,
  revenueDisplay,
  ratingDisplay,
  completionRateDisplay,
  statusBadgeStyle,
  statusText,
  languageLabel,
  levelLabel,
  showAdBadge,
  showPremiumBadge,
  // Methods
  loadCourse: _loadCourse,
  loadCourseChapters,
  publishCourse,
  unpublishCourse,
  archiveCourse,
  initialize
} = useCourseDetail(String(props.id))

// ============================================================================
// Window Management
// ============================================================================

function openEditorWindow(): void {
  if (!course.value) return

  windowStore.openWindow({
    type: 'panel-course-editor',
    title: t('panel.courseDetail.windows.editCourse', { title: course.value.title }),
    icon: '✏️',
    payload: {
      courseId: course.value.course_id,
      course: course.value
    }
  })
}

function openChaptersWindow(): void {
  if (!course.value) return

  windowStore.openWindow({
    type: 'panel-kapitel-manager',
    title: t('panel.courseDetail.windows.chapters', { title: course.value.title }),
    icon: '📚',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

function openFilesWindow(): void {
  if (!course.value) return

  windowStore.openWindow({
    type: 'panel-course-files',
    title: t('panel.courseDetail.windows.files', { title: course.value.title }),
    icon: '📁',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

function openExamsWindow(): void {
  if (!course.value) return

  windowStore.openWindow({
    type: 'panel-exam-manager',
    title: t('panel.courseDetail.windows.exams', { title: course.value.title }),
    icon: '📝',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

function generateExam(): void {
  if (!course.value) return

  windowStore.openWindow({
    type: 'panel-ai-exam-generator',
    title: t('panel.courseDetail.windows.generateExam', { title: course.value.title }),
    icon: '🤖',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

function openAiStudioWindow(): void {
  if (!course.value) return

  windowStore.openWindow({
    type: 'panel-ai-studio',
    title: t('panel.courseDetail.windows.aiStudio', { title: course.value.title }),
    icon: '🤖',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

// ============================================================================
// Event Handlers
// ============================================================================

function handleChapterUpdated(): void {
  console.log('chapter-updated event received, reloading chapters...')
  loadCourseChapters()
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await initialize()
  window.addEventListener('chapter-updated', handleChapterUpdated)
})

onUnmounted(() => {
  window.removeEventListener('chapter-updated', handleChapterUpdated)
})
</script>

<style scoped>
/* Minimal styles - most styling is in sub-components */
</style>
