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
      <!-- Chapter Header -->
      <!-- REMOVED: ChapterHeader (not exported) -->        :chapter="chapter"
        :course-name="courseName"
        :progress="progress"
        :lesson-count="lessons.length"
        :completed-lessons="completedLessons"
        @back="goBackToCourse"
      />

      <!-- Tab Navigation -->
      <!-- REMOVED: ChapterNavigation (not exported) -->        v-model="activeTab"
        :theory-count="theoryData ? 1 : 0"
        :lesson-count="lessons.length"
        @tab-change="handleTabChange"
      />

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Theory Panel -->
        <!-- REMOVED: ChapterTheoryPanel (not exported) -->          v-if="activeTab === 'theory'"
          :theory-data="theoryData"
          :theory-loading="theoryLoading"
          @generate-theory="handleGenerateTheory"
        />

        <!-- Lessons Panel -->
        <!-- REMOVED: LessonPlayerPanel (not exported) -->          v-if="activeTab === 'lessons'"
          :lessons="lessons"
          :lesson-progress="lessonProgress"
          :completed-lessons="completedLessons"
          @lesson-select="handleLessonSelect"
        />
      </div>

      <!-- Lesson Modal (simplified for now - will use LessonPlayerPage) -->
      <Teleport to="body">
        <div
          v-if="showLessonModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
          @click.self="closeLessonModal"
        >
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <!-- Modal Header -->
            <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between z-10">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                {{ selectedLesson?.title || $t('lesson.loading') }}
              </h2>
              <button
                @click="closeLessonModal"
                class="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Modal Content -->
            <div class="p-6">
              <p class="text-gray-600 dark:text-gray-400 text-center py-8">
                {{ $t('lesson.loading') }}
              </p>
              <!-- TODO: Use proper lesson component here (LessonPlayerPage or lesson components) -->
            </div>

            <!-- Modal Footer - Navigation -->
            <div class="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4 flex justify-between">
              <button
                v-if="selectedLessonIndex !== null && selectedLessonIndex > 0"
                @click="goToPrevLesson"
                class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                ← {{ $t('lesson.previous') }}
              </button>
              <div v-else></div>

              <button
                v-if="selectedLessonIndex !== null && selectedLessonIndex < lessons.length - 1"
                @click="goToNextLesson"
                class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                {{ $t('lesson.next') }} →
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ChapterDetailPage
 * =================
 * Orchestrator page for chapter detail view
 * Refactored from 2315 LOC to ~250 LOC
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTutorStore } from '@/application/stores/tutor.store'
import {
  // REMOVED: ChapterHeader (not exported)
  // REMOVED: ChapterNavigation (not exported)
  // REMOVED: ChapterTheoryPanel (not exported)
  // REMOVED: LessonPlayerPanel (not exported)
  useChapterDetail
} from '@/presentation/components/content/user/chapters/detail'

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
  // State
  loading,
  error,
  chapter,
  courseName,
  lessons,
  lessonProgress,
  theoryData,
  theoryLoading,
  // Computed
  progress,
  completedLessons,
  isChapterCompleted,
  // Methods
  isLessonCompleted,
  isLessonLocked,
  loadChapterData,
  loadTheoryById,
  generateTheory,
  initialize
} = useChapterDetail(courseId, chapterId)

// ============================================================================
// Local State
// ============================================================================

const activeTab = ref<'theory' | 'lessons'>('theory')
const showLessonModal = ref(false)
const selectedLesson = ref<any>(null)
const selectedLessonIndex = ref<number | null>(null)

// ============================================================================
// Navigation
// ============================================================================

function goBackToCourse() {
  router.push({ name: 'CourseOverview', params: { courseId } })
}

function handleTabChange(tab: 'theory' | 'lessons') {
  activeTab.value = tab
}

// ============================================================================
// Theory Actions
// ============================================================================

async function handleGenerateTheory() {
  await generateTheory()
}

// ============================================================================
// Lesson Actions
// ============================================================================

function handleLessonSelect(lesson: any, index: number) {
  // Check if locked
  if (isLessonLocked(lesson, index)) return

  selectedLesson.value = lesson
  selectedLessonIndex.value = index
  showLessonModal.value = true

  // TODO: Load full lesson data
  // In the future, navigate to LessonPlayerPage instead of modal
  // router.push({ name: 'LessonPlayer', params: { courseId, chapterId, lessonId: lesson.lesson_id } })
}

function closeLessonModal() {
  showLessonModal.value = false
  selectedLesson.value = null
  selectedLessonIndex.value = null
}

function goToNextLesson() {
  if (selectedLessonIndex.value !== null && selectedLessonIndex.value < lessons.value.length - 1) {
    const nextIndex = selectedLessonIndex.value + 1
    const nextLesson = lessons.value[nextIndex]
    selectedLesson.value = nextLesson
    selectedLessonIndex.value = nextIndex
    // TODO: Load full lesson data
  }
}

function goToPrevLesson() {
  if (selectedLessonIndex.value !== null && selectedLessonIndex.value > 0) {
    const prevIndex = selectedLessonIndex.value - 1
    const prevLesson = lessons.value[prevIndex]
    selectedLesson.value = prevLesson
    selectedLessonIndex.value = prevIndex
    // TODO: Load full lesson data
  }
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

// Watch for chapter changes
watch(() => route.params.chapterId, async (newChapterId) => {
  if (newChapterId && newChapterId !== chapterId) {
    await initialize()
    updateTutorContext()
  }
})

// Clear tutor context on unmount
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
/* Minimal styles - most styling is in sub-components */
.tab-content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
