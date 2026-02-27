<template>
  <div class="course-overview min-h-screen">
    <!-- Loading State -->
    <div v-if="playerStore.loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="playerStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
      {{ playerStore.error }}
    </div>

    <!-- Course Content -->
    <div v-else-if="playerStore.course" class="container mx-auto max-w-6xl px-4 py-8">
      <!-- Course Header with Progress Stats -->
      <CourseOverviewHeader
        :course-title="playerStore.course.title"
        :course-subtitle="playerStore.course.subtitle"
        :completed-chapters="completedChapters"
        :total-chapters="totalChapters"
        :progress-percentage="progressPercentage"
        :average-grade="averageGrade"
        :learning-time="learningTimeFormatted"
      />

      <!-- Mountain Journey Map -->
      <div class="mb-12">
        <MountainJourneyMap
          :total-chapters="totalChapters"
          :completed-chapters="completedChapters"
          :current-chapter-index="currentChapterIndex"
          @node-click="handleNodeClick"
        />
      </div>

      <!-- Chapter Grid -->
      <ChapterGridList
        :chapters="playerStore.chapters"
        :get-chapter-status="getChapterStatus"
        :format-duration="formatDurationWithText"
        :truncate-description="truncateDescription"
        @chapter-click="handleChapterClick"
      />

      <!-- Course Details -->
      <div class="mt-8">
        <CourseDetailsSections
          :description="playerStore.course.description"
          :learning-goals="playerStore.course.learning_goals"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseOverviewView
 * ==================
 * Orchestrator component for course overview with mountain journey visualization
 */
import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  CourseOverviewHeader,
  MountainJourneyMap,
  ChapterGridList,
  CourseDetailsSections,
  useCourseOverview
} from '@/presentation/components/panel/user/courses/overview'

// ============================================================================
// Setup
// ============================================================================

interface Props {
  courseId: string
}

const props = defineProps<Props>()
const { t } = useI18n()

// ============================================================================
// Course Overview Composable
// ============================================================================

const {
  playerStore,
  // Computed - Progress
  totalChapters,
  completedChapters,
  progressPercentage,
  averageGrade,
  learningTimeFormatted,
  currentChapterIndex,
  // Methods - Chapter Status
  isLocked,
  getChapterStatus,
  // Methods - Navigation
  handleChapterClick,
  // Methods - Utilities
  formatDuration,
  truncateDescription,
  // Lifecycle
  initialize,
  cleanup
} = useCourseOverview(props.courseId)

// ============================================================================
// Event Handlers
// ============================================================================

const handleNodeClick = (index: number): void => {
  const chapter = playerStore.chapters[index]
  if (chapter && !isLocked(index)) {
    handleChapterClick(chapter, index)
  }
}

const formatDurationWithText = (minutes: number): string => {
  return formatDuration(minutes, t('courses.minutes_short'))
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await initialize()
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.course-overview {
  background: var(--color-background);
  color: var(--color-text-primary);
}
</style>
