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
      <LessonPlayerTopBar
        :course-title="playerStore.course?.title ?? ''"
        :chapter-title="playerStore.currentChapter?.title ?? ''"
        :progress-percentage="playerStore.lessonProgress?.progress_percentage ?? null"
        :is-completed="playerStore.isLessonCompleted"
        @back="goBackToCourse"
        @complete="completeLesson"
      />

      <!-- Main Content Area -->
      <div class="main-area" :class="{ 'main-area--tasks-only': isInteractiveLesson }">
        <!-- Left Sidebar: Chapter Navigation (hidden for interactive lessons) -->
        <LessonPlayerSidebar
          v-if="!isInteractiveLesson"
          :lessons="playerStore.currentChapter?.lessons"
          :active-lesson-id="playerStore.currentLesson?.lesson_id"
          @navigate="navigateToLesson"
        />

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

            <!-- Lesson Content Component (Dynamic) -->
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
import { usePlayerStore } from '@/application/stores/modules/content/player.store'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'
import Button from '@/presentation/components/shared/ui/Button.vue'
import { MethodExecutionPanel } from '@/presentation/components/public/learning/methods'
import LessonPlayerTopBar from './LessonPlayerTopBar.vue'
import LessonPlayerSidebar from './LessonPlayerSidebar.vue'

interface Props {
  courseId: string
  chapterId: string
  lessonId: string
}

const props = defineProps<Props>()

const { t } = useI18n()
const playerStore = usePlayerStore()
const tutorStore = useTutorStore()
const router = useRouter()

// Lesson Components (Dynamic)
const lessonComponents: Record<string, ReturnType<typeof defineAsyncComponent>> = {
  text: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/TextLesson.vue')),
  video: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/VideoLesson.vue')),
  quiz: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/quiz/QuizLesson.vue')),
  ai: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/AiLesson.vue')),
  interactive: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/AiLesson.vue')),
  mixed: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/TextLesson.vue'))
}

// Computed
const courseId = computed(() => props.courseId)
const chapterId = computed(() => props.chapterId)
const lessonId = computed(() => props.lessonId)

const lessonComponent = computed(() => {
  const type = playerStore.currentLesson?.lesson_type || 'text'
  return lessonComponents[type] || lessonComponents.text
})

const isInteractiveLesson = computed(() => {
  const type = playerStore.currentLesson?.lesson_type
  return ['ai', 'interactive'].includes(type)
})

// Navigation
function goBackToCourse(): void {
  router.push({
    name: 'CourseOverview',
    params: { courseId: courseId.value }
  })
}

function navigateToLesson(newLessonId: number): void {
  router.push({
    name: 'LessonPlayer',
    params: {
      courseId: courseId.value,
      chapterId: chapterId.value,
      lessonId: newLessonId
    }
  })
}

function goToNextLesson(): void {
  if (playerStore.nextLesson) {
    navigateToLesson(playerStore.nextLesson.lesson_id)
  }
}

function goToPreviousLesson(): void {
  if (playerStore.previousLesson) {
    navigateToLesson(playerStore.previousLesson.lesson_id)
  }
}

async function completeLesson(): Promise<void> {
  try {
    await playerStore.markLessonCompleted(courseId.value, chapterId.value, lessonId.value)
  } catch (err) {
    console.error('Failed to complete lesson:', err)
  }
}

function handleLessonCompleted(): void {
  console.log('Lesson completed')
}

// Tutor context
function updateTutorContext(): void {
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

function clearTutorContext(): void {
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

// Lifecycle
onMounted(async () => {
  if (!playerStore.hasCourse || playerStore.course?.course_id !== courseId.value) {
    await playerStore.loadCourse(courseId.value)
  }

  if (!playerStore.currentChapter || playerStore.currentChapter.chapter_id !== chapterId.value) {
    await playerStore.loadChapter(courseId.value, chapterId.value)
  }

  await playerStore.loadLesson(courseId.value, chapterId.value, lessonId.value)
  updateTutorContext()
})

watch(() => playerStore.currentLesson, () => {
  updateTutorContext()
})

onUnmounted(() => {
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

/* Center Content */
.content-center {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background-color: var(--color-bg, #f5f5f7);
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
