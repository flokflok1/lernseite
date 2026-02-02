/**
 * useCourseOverview Composable
 * =============================
 * Manages course overview data, progress, and chapter navigation
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlayerStore } from '@/application/stores/player.store'
import { useTutorStore } from '@/application/stores/tutor.store'
import type { Chapter } from '@/application/services/api/learning'

export function useCourseOverview(courseId: string) {
  const router = useRouter()
  const playerStore = usePlayerStore()
  const tutorStore = useTutorStore()

  // ============================================================================
  // Computed - Progress Stats
  // ============================================================================

  const totalChapters = computed(() => playerStore.chapters.length)

  const completedChapters = computed(() => {
    if (!playerStore.courseProgress) return 0
    return playerStore.courseProgress.chapters_completed || 0
  })

  const progressPercentage = computed(() => {
    if (!playerStore.courseProgress) return 0
    return Math.round(playerStore.courseProgress.progress_percentage || 0)
  })

  const averageGrade = computed(() => {
    // TODO: Calculate from actual exam results
    return 85
  })

  const learningTimeFormatted = computed(() => {
    const minutes = playerStore.course?.total_duration_minutes || 0
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) return `${hours}h ${mins}m`
    return `${mins}m`
  })

  // ============================================================================
  // Computed - Chapter Status
  // ============================================================================

  const currentChapterIndex = computed(() => {
    return Math.min(completedChapters.value, totalChapters.value - 1)
  })

  const isCompleted = (index: number): boolean => {
    return index < completedChapters.value
  }

  const isCurrent = (index: number): boolean => {
    return index === currentChapterIndex.value
  }

  const isLocked = (index: number): boolean => {
    return index > currentChapterIndex.value
  }

  const getChapterStatus = (index: number): 'completed' | 'current' | 'locked' => {
    if (isCompleted(index)) return 'completed'
    if (isCurrent(index)) return 'current'
    return 'locked'
  }

  // ============================================================================
  // Methods - Chapter Navigation
  // ============================================================================

  const startChapter = (chapter: Chapter): void => {
    router.push({
      name: 'ChapterDetail',
      params: {
        courseId: courseId,
        chapterId: chapter.chapter_id
      }
    })
  }

  const handleChapterClick = (chapter: Chapter, index: number): void => {
    if (!isLocked(index)) {
      startChapter(chapter)
    }
  }

  // ============================================================================
  // Methods - Utilities
  // ============================================================================

  const formatDuration = (minutes: number, shortText: string): string => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) return `${hours}h ${mins}m`
    return `${mins} ${shortText}`
  }

  const truncateDescription = (text: string, maxLength = 120): string => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + '...'
  }

  // ============================================================================
  // Lifecycle - Load Course & Setup Context
  // ============================================================================

  const initialize = async (): Promise<void> => {
    await playerStore.loadCourse(courseId)

    // Update tutor context with course info
    tutorStore.updateContext({
      page: 'course',
      courseId: playerStore.course?.course_id || courseId,
      courseName: playerStore.course?.title || null,
      chapterId: null,
      chapterName: null,
      lessonId: null,
      lessonName: null,
      methodId: null,
      methodType: null
    })
  }

  const cleanup = (): void => {
    // Clear tutor context when leaving the course
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
  }

  return {
    // Store references
    playerStore,
    // Computed - Progress
    totalChapters,
    completedChapters,
    progressPercentage,
    averageGrade,
    learningTimeFormatted,
    currentChapterIndex,
    // Methods - Chapter Status
    isCompleted,
    isCurrent,
    isLocked,
    getChapterStatus,
    // Methods - Navigation
    startChapter,
    handleChapterClick,
    // Methods - Utilities
    formatDuration,
    truncateDescription,
    // Lifecycle
    initialize,
    cleanup
  }
}
