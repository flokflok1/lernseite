<template>
  <div class="lesson-player">
    <!-- Loading State -->
    <div v-if="playerStore.loading" class="loading-container">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="playerStore.error" class="error-container">
      <div class="error-box">
        {{ playerStore.error }}
      </div>
      <Button @click="$router.push({ name: 'Courses' })">{{ t('lesson.back_to_courses') }}</Button>
    </div>

    <!-- Player Layout -->
    <div v-else-if="playerStore.currentLesson" class="player-layout">
      <!-- Top Navigation Bar -->
      <div class="top-bar">
        <div class="top-bar-content">
          <div class="top-bar-left">
            <Button
              variant="outline"
              size="sm"
              @click="goBackToCourse"
            >
              ← {{ t('chapter.back_to_course') }}
            </Button>
            <div class="course-info">
              <h2 class="course-title">
                {{ playerStore.course?.title }}
              </h2>
              <p class="chapter-title">
                {{ playerStore.currentChapter?.title }}
              </p>
            </div>
          </div>

          <div class="top-bar-right">
            <!-- Progress Indicator -->
            <div v-if="playerStore.lessonProgress?.progress_percentage != null" class="progress-text">
              {{ t('lesson.progress_completed', { progress: Math.round(playerStore.lessonProgress.progress_percentage) }) }}
            </div>
            <div v-else-if="playerStore.isLessonCompleted" class="progress-text">
              {{ t('lesson.progress_completed', { progress: 100 }) }}
            </div>

            <!-- Complete Button -->
            <Button
              v-if="!playerStore.isLessonCompleted"
              variant="primary"
              size="sm"
              @click="completeLesson"
            >
              ✓ {{ t('lesson.mark_completed') }}
            </Button>
            <span v-else class="completed-badge">
              ✓ {{ t('lesson.completed') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="main-area" :class="{ 'main-area--tasks-only': isInteractiveLesson }">
        <!-- Left Sidebar: Chapter Navigation (hidden for interactive lessons) -->
        <div v-if="!isInteractiveLesson" class="sidebar-left">
          <div class="sidebar-content">
            <h3 class="sidebar-title">{{ t('lesson.contents') }}</h3>

            <div v-if="playerStore.currentChapter?.lessons" class="lesson-list">
              <div
                v-for="(lesson, index) in playerStore.currentChapter.lessons"
                :key="lesson.lesson_id"
                class="lesson-item"
                :class="{
                  'lesson-item--active': lesson.lesson_id === playerStore.currentLesson?.lesson_id,
                  'lesson-item--inactive': lesson.lesson_id !== playerStore.currentLesson?.lesson_id
                }"
                @click="navigateToLesson(lesson.lesson_id)"
              >
                <div class="lesson-item-content">
                  <span class="lesson-number">{{ index + 1 }}</span>
                  <div class="lesson-info">
                    <p class="lesson-name">{{ lesson.title }}</p>
                    <div class="lesson-meta">
                      <span class="lesson-type-badge">
                        {{ lessonTypeLabel(lesson.lesson_type) }}
                      </span>
                      <span v-if="lesson.duration_minutes" class="lesson-duration">
                        {{ lesson.duration_minutes }} {{ t('courses.minutes_short') }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Center: Lesson Content (hidden for interactive lessons) -->
        <div v-if="!isInteractiveLesson" class="content-center">
          <div class="content-wrapper">
            <!-- Lesson Header -->
            <div class="lesson-header">
              <h1 class="lesson-title">
                {{ playerStore.currentLesson.title }}
              </h1>
              <p v-if="playerStore.currentLesson.description && !isInteractiveLesson" class="lesson-description">
                {{ playerStore.currentLesson.description }}
              </p>
            </div>

            <!-- Lesson Content Component (Dynamic) - NOT for interactive lessons -->
            <component
              v-if="!isInteractiveLesson"
              :is="lessonComponent"
              :lesson="playerStore.currentLesson"
              :course-id="courseId"
              :chapter-id="chapterId"
              class="lesson-component"
              @completed="handleLessonCompleted"
              @continue="goToNextLesson"
            />

            <!-- For interactive lessons: Simple prompt to use tasks -->
            <div v-else class="interactive-prompt">
              <p>{{ t('lesson.interactive_hint') }}</p>
            </div>

            <!-- Navigation Buttons -->
            <div class="nav-buttons">
              <Button
                v-if="playerStore.hasPreviousLesson"
                variant="outline"
                @click="goToPreviousLesson"
              >
                ← {{ t('lesson.previous_lesson') }}
              </Button>
              <div v-else></div>

              <Button
                v-if="playerStore.hasNextLesson"
                variant="primary"
                @click="goToNextLesson"
              >
                {{ t('lesson.next_lesson') }} →
              </Button>
              <Button
                v-else
                variant="primary"
                @click="goBackToCourse"
              >
                {{ t('lesson.finish_course') }}
              </Button>
            </div>
          </div>
        </div>

        <!-- Right Sidebar: Learning Methods -->
        <div class="sidebar-right">
          <MethodExecutionPanel
            v-if="playerStore.currentLesson"
            :lesson-id="playerStore.currentLesson.lesson_id"
            :methods="playerStore.availableMethods"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed, defineAsyncComponent, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePlayerStore } from '@/store/player.store'
import { useTutorStore } from '@/store/tutor.store'
import Button from '@/components/shared/ui/Button.vue'
import { MethodExecutionPanel } from '@/components/user/lessons'

// ============================================================================
// Props
// ============================================================================

interface Props {
  courseId: string
  chapterId: string
  lessonId: string
}

const props = defineProps<Props>()

// ============================================================================
// Store & Router
// ============================================================================

const { t } = useI18n()
const playerStore = usePlayerStore()
const tutorStore = useTutorStore()
const router = useRouter()

// ============================================================================
// Lesson Components (Dynamic)
// ============================================================================

const lessonComponents = {
  text: defineAsyncComponent(() => import('@/components/user/lessons/text/TextLesson.vue')),
  video: defineAsyncComponent(() => import('@/components/user/lessons/video/VideoLesson.vue')),
  quiz: defineAsyncComponent(() => import('@/components/user/lessons/quiz/QuizLesson.vue')),
  ai: defineAsyncComponent(() => import('@/components/user/lessons/ai/AiLesson.vue')),
  interactive: defineAsyncComponent(() => import('@/components/user/lessons/ai/AiLesson.vue')), // Interactive lessons
  mixed: defineAsyncComponent(() => import('@/components/user/lessons/text/TextLesson.vue')) // Fallback
}

// ============================================================================
// Computed
// ============================================================================

const courseId = computed(() => props.courseId)  // UUID string
const chapterId = computed(() => props.chapterId)  // UUID string
const lessonId = computed(() => props.lessonId)  // UUID string

const lessonComponent = computed(() => {
  const type = playerStore.currentLesson?.lesson_type || 'text'
  return lessonComponents[type] || lessonComponents.text
})

const isInteractiveLesson = computed(() => {
  const type = playerStore.currentLesson?.lesson_type
  return ['ai', 'interactive'].includes(type)
})

// ============================================================================
// Methods
// ============================================================================

const lessonTypeLabel = (type: string): string => {
  const typeMap: Record<string, string> = {
    text: t('lesson.type_text'),
    video: t('lesson.type_video'),
    quiz: t('lesson.type_quiz'),
    ai: t('lesson.type_ai'),
    interactive: t('lesson.type_interactive'),
    mixed: t('lesson.type_mixed')
  }
  return typeMap[type] || type
}

const goBackToCourse = () => {
  router.push({
    name: 'CourseOverview',
    params: { courseId: courseId.value }
  })
}

const navigateToLesson = (newLessonId: number) => {
  router.push({
    name: 'LessonPlayer',
    params: {
      courseId: courseId.value,
      chapterId: chapterId.value,
      lessonId: newLessonId
    }
  })
}

const goToNextLesson = () => {
  if (playerStore.nextLesson) {
    navigateToLesson(playerStore.nextLesson.lesson_id)
  }
}

const goToPreviousLesson = () => {
  if (playerStore.previousLesson) {
    navigateToLesson(playerStore.previousLesson.lesson_id)
  }
}

const completeLesson = async () => {
  try {
    await playerStore.markLessonCompleted(courseId.value, chapterId.value, lessonId.value)
  } catch (err) {
    console.error('Failed to complete lesson:', err)
  }
}

const handleLessonCompleted = () => {
  // Quiz lessons handle completion internally via submitQuiz
  // This handler is for other lesson types or additional processing
  console.log('Lesson completed')
}

// Update tutor context with current course/chapter/lesson
const updateTutorContext = () => {
  tutorStore.updateContext({
    page: 'lesson',
    courseId: playerStore.course?.course_id || null,
    courseName: playerStore.course?.title || null,
    chapterId: playerStore.currentChapter?.chapter_id || null,
    chapterName: playerStore.currentChapter?.title || null,
    lessonId: playerStore.currentLesson?.lesson_id || null,
    lessonName: playerStore.currentLesson?.title || null,
    methodId: null,
    methodType: null
  })
}

// Clear tutor context when leaving
const clearTutorContext = () => {
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

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  // Load course if not already loaded
  if (!playerStore.hasCourse || playerStore.course?.course_id !== courseId.value) {
    await playerStore.loadCourse(courseId.value)
  }

  // Load chapter if not already loaded
  if (!playerStore.currentChapter || playerStore.currentChapter.chapter_id !== chapterId.value) {
    await playerStore.loadChapter(courseId.value, chapterId.value)
  }

  // Load lesson
  await playerStore.loadLesson(courseId.value, chapterId.value, lessonId.value)

  // Update tutor context with current lesson info
  updateTutorContext()
})

// Watch for lesson changes and update tutor context
watch(() => playerStore.currentLesson, () => {
  updateTutorContext()
})

onUnmounted(() => {
  // Clear tutor context when leaving the lesson
  clearTutorContext()
})
</script>

<style scoped>
/* Base Layout */
.lesson-player {
  min-height: 100vh;
  background-color: var(--color-bg, #f5f5f7);
  color: var(--color-text-primary, #111827);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.player-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* Loading State */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border, #e5e7eb);
  border-top-color: var(--color-primary, #3b82f6);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error State */
.error-container {
  max-width: 56rem;
  margin: 0 auto;
  padding: 1.5rem;
}

.error-box {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

/* Top Bar */
.top-bar {
  background-color: var(--color-surface, #ffffff);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  padding: 1rem 1.5rem;
}

.top-bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.course-info {
  border-left: 1px solid var(--color-border, #e5e7eb);
  padding-left: 1rem;
}

.course-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  font-size: 1rem;
  margin: 0;
}

.chapter-title {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.completed-badge {
  font-size: 0.875rem;
  color: #10b981;
  font-weight: 500;
}

/* Main Area */
.main-area {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-area--tasks-only {
  justify-content: center;
}

.main-area--tasks-only .sidebar-right {
  flex: 0 0 600px;
  max-width: 800px;
}

/* Left Sidebar */
.sidebar-left {
  width: 16rem;
  background-color: var(--color-surface, #ffffff);
  border-right: 1px solid var(--color-border, #e5e7eb);
  overflow-y: auto;
}

.sidebar-content {
  padding: 1rem;
}

.sidebar-title {
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 1rem;
  font-size: 1rem;
}

.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.lesson-item {
  cursor: pointer;
  border-radius: 0.5rem;
  padding: 0.75rem;
  transition: all 0.2s;
}

.lesson-item--active {
  background-color: var(--color-primary, #3b82f6);
  color: white;
}

.lesson-item--active .lesson-number,
.lesson-item--active .lesson-name,
.lesson-item--active .lesson-duration {
  color: white;
}

.lesson-item--active .lesson-type-badge {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.lesson-item--inactive:hover {
  background-color: var(--color-surface-secondary, #f9fafb);
}

.lesson-item-content {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.lesson-number {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #9ca3af);
  font-weight: 500;
  min-width: 1rem;
}

.lesson-info {
  flex: 1;
}

.lesson-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.lesson-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.lesson-type-badge {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background-color: var(--color-surface-secondary, #f9fafb);
  color: var(--color-text-secondary, #6b7280);
  border-radius: 0.25rem;
}

.lesson-duration {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
}

/* Center Content */
.content-center {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background-color: var(--color-bg, #f5f5f7);
}

.content-center--minimal {
  flex: 0 0 auto;
  max-width: 300px;
  min-width: 250px;
}

.content-wrapper {
  max-width: 56rem;
  margin: 0 auto;
}

.interactive-prompt {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-secondary, #64748b);
  font-size: 0.9rem;
}

.lesson-header {
  margin-bottom: 1.5rem;
}

.lesson-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.5rem;
}

.lesson-description {
  font-size: 1.125rem;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

.lesson-component {
  margin-bottom: 2rem;
}

.nav-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--color-border, #e5e7eb);
  padding-top: 1.5rem;
}

/* Right Sidebar */
.sidebar-right {
  width: 20rem;
  background-color: var(--color-surface, #ffffff);
  border-left: 1px solid var(--color-border, #e5e7eb);
  overflow-y: auto;
}
</style>
