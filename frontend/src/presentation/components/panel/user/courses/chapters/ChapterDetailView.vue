<template>
  <div class="chapter-detail-page min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center min-h-screen">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
      <p class="text-gray-600 dark:text-gray-400">{{ $t('chapter.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex flex-col items-center justify-center min-h-screen p-6">
      <div class="max-w-md w-full bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <p class="text-red-700 dark:text-red-300 mb-4">{{ error }}</p>
        <button
          @click="router.push({ name: 'CourseOverview', params: { courseId } })"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          {{ $t('chapter.backToCourse') }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="chapter">
      <!-- Chapter Hero (replaces ChapterHeader) -->
      <ChapterHero
        :chapter="chapter"
        :course-name="courseName"
        :progress="progress"
        :lesson-count="lessons.length"
        :completed-lessons="completedLessons"
        :total-duration="totalDuration"
        :lesson-type-breakdown="lessonTypeBreakdown"
        :is-chapter-completed="isChapterCompleted"
        :has-next-lesson="!!firstIncompleteLesson"
        @back="goBackToCourse"
        @continue-learning="handleContinueLearning"
      />

      <!-- Tab Navigation -->
      <ChapterNavigation
        v-model="activeTab"
        :theory-count="theorySheets.length"
        :lesson-count="lessons.length"
        @tab-change="handleTabChange"
      />

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Theory Accordion (replaces ChapterTheoryPanel) -->
        <TheoryAccordion
          v-if="activeTab === 'theory'"
          :theories="theorySheets"
          :loading="theorySheetsLoading"
          :load-content="loadTheoryContent"
        />

        <!-- Lesson Timeline (replaces LessonPlayerPanel) -->
        <LessonTimeline
          v-if="activeTab === 'lessons'"
          :lessons="lessons"
          :lesson-progress="lessonProgress"
          :completed-lessons="completedLessons"
          @lesson-select="handleLessonSelect"
        />
      </div>

      <!-- Chapter Complete Banner -->
      <ChapterCompleteBanner
        v-if="isChapterCompleted && lessons.length > 0"
        :lesson-count="lessons.length"
        @continue="goBackToCourse"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ChapterDetailView
 * =================
 * Orchestrator component for chapter detail view.
 * Redesigned with Hero, Timeline, and Theory Accordion.
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'
import {
  ChapterHero,
  ChapterNavigation,
  TheoryAccordion,
  LessonTimeline,
  ChapterCompleteBanner,
  useChapterDetail
} from '@/presentation/components/panel/user/courses/chapters/detail'

// ============================================================================
// Setup
// ============================================================================

const route = useRoute()
const router = useRouter()
const tutorStore = useTutorStore()

const courseId = route.params.courseId as string
const chapterId = route.params.chapterId as string

// ============================================================================
// Chapter Detail Composable
// ============================================================================

const {
  loading,
  error,
  chapter,
  courseName,
  lessons,
  lessonProgress,
  theorySheets,
  theorySheetsLoading,
  progress,
  completedLessons,
  isChapterCompleted,
  firstIncompleteLesson,
  totalDuration,
  lessonTypeBreakdown,
  isLessonLocked,
  loadTheoryContent,
  initialize
} = useChapterDetail(courseId, chapterId)

// ============================================================================
// Local State
// ============================================================================

const activeTab = ref<'theory' | 'lessons'>('lessons')

// ============================================================================
// Navigation
// ============================================================================

function goBackToCourse() {
  router.push({ name: 'CourseOverview', params: { courseId } })
}

function handleTabChange(tab: 'theory' | 'lessons') {
  activeTab.value = tab
}

function handleContinueLearning() {
  const lesson = firstIncompleteLesson.value
  if (lesson) {
    router.push({
      name: 'LessonPlayer',
      params: { courseId, chapterId, lessonId: lesson.lesson_id }
    })
  }
}

// ============================================================================
// Lesson Actions
// ============================================================================

function handleLessonSelect(lesson: any, index: number) {
  if (isLessonLocked(lesson, index)) return

  router.push({
    name: 'LessonPlayer',
    params: { courseId, chapterId, lessonId: lesson.lesson_id }
  })
}

// ============================================================================
// Tutor Context Management
// ============================================================================

function updateTutorContext() {
  tutorStore.updateContext({
    page: 'chapter',
    courseId: courseId,
    courseName: courseName.value || null,
    chapterId: chapterId,
    chapterName: chapter.value?.title || null,
    lessonId: null,
    lessonName: null,
    methodId: null,
    methodType: null
  })
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await initialize()
  updateTutorContext()
})

watch(() => route.params.chapterId, async (newChapterId) => {
  if (newChapterId && newChapterId !== chapterId) {
    await initialize()
    updateTutorContext()
  }
})

onUnmounted(() => {
  tutorStore.updateContext({
    page: 'dashboard',
    courseId: null,
    courseName: null,
    chapterId: null,
    chapterName: null,
    lessonId: null,
    lessonName: null,
    methodId: null,
    methodType: null
  })
})
</script>

<style scoped>
.tab-content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
