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
      <!-- Hero Navigation Bar -->
      <LessonPlayerTopBar
        :course-title="playerStore.course?.title ?? ''"
        :chapter-title="playerStore.currentChapter?.title ?? ''"
        :lesson-title="playerStore.currentLesson?.title ?? ''"
        :lesson-type="playerStore.currentLesson?.lesson_type"
        :lesson-position="lessonPosition"
        :progress-percentage="playerStore.lessonProgress?.progress_percentage ?? null"
        :is-completed="playerStore.isLessonCompleted"
        :duration-minutes="playerStore.currentLesson?.duration_minutes"
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
          :completed-lesson-ids="completedLessonIds"
          @navigate="navigateToLesson"
        />

        <!-- Center: Task Content (when a task is active) -->
        <div v-if="playerStore.activeExecution && !isInteractiveLesson" class="content-center">
          <TaskContentPanel
            :execution="playerStore.activeExecution"
            @close="playerStore.clearActiveTask()"
            @complete="handleTaskComplete"
          />
        </div>

        <!-- Center: Lesson Content (hidden for interactive lessons and active tasks) -->
        <div v-else-if="!isInteractiveLesson" ref="contentRef" class="content-center" @scroll="handleContentScroll">
          <div class="content-wrapper">
            <!-- Lesson Content Component (Dynamic) -->
            <component
              :is="lessonComponent"
              :lesson="playerStore.currentLesson"
              :course-id="courseId"
              :chapter-id="chapterId"
              class="lesson-component"
              @completed="handleLessonCompleted"
              @continue="goToNextLesson"
            />

            <!-- Navigation Buttons -->
            <div class="nav-buttons">
              <button
                v-if="playerStore.hasPreviousLesson"
                class="nav-btn nav-btn--outline"
                @click="goToPreviousLesson"
              >
                <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                {{ t('lesson.previous_lesson') }}
              </button>
              <div v-else></div>

              <button
                v-if="playerStore.hasNextLesson"
                class="nav-btn nav-btn--primary"
                @click="goToNextLesson"
              >
                {{ t('lesson.next_lesson') }}
                <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <button
                v-else
                class="nav-btn nav-btn--primary"
                @click="goBackToCourse"
              >
                {{ t('lesson.finish_course') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Right Sidebar: Learning Methods -->
        <aside class="sidebar-right">
          <div class="sidebar-right-header">
            <h3 class="sidebar-right-title">{{ t('lesson.methods_sidebar_title') }}</h3>
          </div>
          <MethodExecutionPanel
            v-if="playerStore.currentLesson"
            :lesson-id="playerStore.currentLesson.lesson_id"
            :methods="playerStore.availableMethods"
          />
        </aside>
      </div>

      <!-- Completion Toast -->
      <Transition name="toast">
        <div v-if="showCompletionToast" class="completion-toast">
          <svg class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ t('lesson.completed_toast') }}</span>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, defineAsyncComponent, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePlayerStore } from '@/application/stores/modules/content/player.store'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'
import Button from '@/presentation/components/shared/ui/Button.vue'
import { MethodExecutionPanel } from '@/presentation/components/public/learning/methods'
import { TaskContentPanel } from '@/presentation/components/public/learning/methods/method-execution'
import LessonPlayerTopBar from '@/presentation/components/panel/user/learning/lesson/LessonPlayerTopBar.vue'
import LessonPlayerSidebar from '@/presentation/components/panel/user/learning/lesson/LessonPlayerSidebar.vue'

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

// Scroll-based progress tracking
const contentRef = ref<HTMLElement | null>(null)
const lastSyncedDepth = ref(0)
const completedLessonIds = ref<number[]>([])
const showCompletionToast = ref(false)
let scrollDebounceTimer: ReturnType<typeof setTimeout> | null = null

const lessonPosition = computed(() => {
  const lessons = playerStore.currentChapter?.lessons
  if (!lessons || !playerStore.currentLesson) return undefined
  const idx = lessons.findIndex((l: any) => l.lesson_id === playerStore.currentLesson?.lesson_id)
  if (idx === -1) return undefined
  return { current: idx + 1, total: lessons.length }
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
    // Issue #3: Track completed lesson for live sidebar dot update
    const lid = playerStore.currentLesson?.lesson_id
    if (lid && !completedLessonIds.value.includes(lid)) {
      completedLessonIds.value.push(lid)
    }
    showCompletionToast.value = true
    setTimeout(() => { showCompletionToast.value = false }, 3000)
  } catch (err) {
    console.error('Failed to complete lesson:', err)
  }
}

function handleLessonCompleted(): void {
  if (!playerStore.isLessonCompleted) {
    completeLesson()
  }
}

// Issue #2: Scroll-depth progress sync
function handleContentScroll(): void {
  if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer)
  scrollDebounceTimer = setTimeout(() => {
    const el = contentRef.value
    if (!el) return

    const scrollDepth = el.scrollHeight - el.clientHeight
    if (scrollDepth <= 0) return

    const pct = Math.min(100, Math.round((el.scrollTop / scrollDepth) * 100))

    // Sync at 25% increments to avoid excessive API calls
    const milestone = Math.floor(pct / 25) * 25
    if (milestone > lastSyncedDepth.value && milestone > 0) {
      lastSyncedDepth.value = milestone
      playerStore.syncProgress(
        courseId.value, chapterId.value, lessonId.value, milestone
      )
    }

    // Auto-complete when scrolled near bottom (>= 95%)
    if (pct >= 95 && !playerStore.isLessonCompleted) {
      completeLesson()
    }
  }, 300)
}

// Issue #4: Handle task renderer @complete event — save score, refresh progress
async function handleTaskComplete(score: number, maxScore: number): Promise<void> {
  // Refresh the methods progress in the sidebar
  await playerStore.refreshMethodsProgress(lessonId.value)
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

// Issue #6: Keyboard shortcuts
function handleKeydown(e: KeyboardEvent): void {
  // Don't intercept when typing in inputs
  const tag = (e.target as HTMLElement)?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return

  switch (e.key) {
    case 'ArrowLeft':
      if (playerStore.hasPreviousLesson) goToPreviousLesson()
      break
    case 'ArrowRight':
      if (playerStore.hasNextLesson) goToNextLesson()
      break
    case 'Escape':
      if (playerStore.activeExecution) {
        playerStore.clearActiveTask()
      } else {
        goBackToCourse()
      }
      break
  }
}

// Lifecycle
onMounted(async () => {
  // Launch all data loads in parallel (course, chapter, lesson are independent)
  const promises: Promise<void>[] = []

  if (!playerStore.hasCourse || playerStore.course?.course_id !== courseId.value) {
    promises.push(playerStore.loadCourse(courseId.value))
  }

  if (!playerStore.currentChapter || playerStore.currentChapter.chapter_id !== chapterId.value) {
    promises.push(playerStore.loadChapter(courseId.value, chapterId.value))
  }

  promises.push(playerStore.loadLesson(courseId.value, chapterId.value, lessonId.value))

  await Promise.all(promises)
  updateTutorContext()

  window.addEventListener('keydown', handleKeydown)
})

// Reload lesson when route params change (same component, different lesson)
watch(lessonId, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    playerStore.clearActiveTask()
    lastSyncedDepth.value = 0
    await playerStore.loadLesson(courseId.value, chapterId.value, newId)
    updateTutorContext()
  }
})

watch(() => playerStore.currentLesson, () => {
  updateTutorContext()
  // Reset scroll tracking when lesson changes
  lastSyncedDepth.value = 0
})

onUnmounted(() => {
  clearTutorContext()
  window.removeEventListener('keydown', handleKeydown)
  if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer)
})
</script>

<style scoped>
/* Base Layout */
.lesson-player {
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
  padding: 1.5rem 2rem;
  background-color: var(--color-surface, #ffffff);
  border-left: 1px solid var(--color-border, #e5e7eb);
  border-right: 1px solid var(--color-border, #e5e7eb);
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.08) transparent;
}

:root.dark .content-center {
  background-color: #1e293b;
  border-left-color: rgba(255, 255, 255, 0.06);
  border-right-color: rgba(255, 255, 255, 0.06);
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

.lesson-component {
  margin-bottom: 1.5rem;
}

/* Navigation Buttons */
.nav-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--color-border, #e5e7eb);
  padding-top: 1.25rem;
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 0.5rem;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
}

.nav-btn--outline {
  background-color: var(--color-surface, #ffffff);
  color: var(--color-text-primary, #374151);
  border: 1px solid var(--color-border, #d1d5db);
}

.nav-btn--outline:hover {
  background-color: var(--color-surface-secondary, #f9fafb);
  border-color: var(--color-text-secondary, #9ca3af);
}

.nav-btn--primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}

.nav-btn--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
}

.nav-icon {
  width: 1rem;
  height: 1rem;
}

/* Custom Scrollbar (global for this view) */
.content-center::-webkit-scrollbar,
.sidebar-right::-webkit-scrollbar {
  width: 6px;
}

.content-center::-webkit-scrollbar-track,
.sidebar-right::-webkit-scrollbar-track {
  background: transparent;
}

.content-center::-webkit-scrollbar-thumb,
.sidebar-right::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
}

.content-center::-webkit-scrollbar-thumb:hover,
.sidebar-right::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

/* Right Sidebar */
.sidebar-right {
  width: 20rem;
  flex-shrink: 0;
  background-color: var(--color-surface, #ffffff);
  border-left: 1px solid var(--color-border, #e5e7eb);
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.08) transparent;
}

:root.dark .sidebar-right {
  background-color: #111827;
  border-left-color: rgba(255, 255, 255, 0.06);
}

.sidebar-right-header {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  flex-shrink: 0;
}

:root.dark .sidebar-right-header {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-bottom-color: rgba(255, 255, 255, 0.06);
}

.sidebar-right-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary, #6366f1);
  margin: 0;
}

/* Completion Toast */
.completion-toast {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 0.75rem;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
  z-index: 50;
}

.toast-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.toast-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-leave-active {
  transition: all 0.3s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(20px) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}
</style>
