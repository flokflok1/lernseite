<template>
  <div class="lesson-player">
    <!-- Loading State -->
    <div v-if="playerStore.loading" class="loading-container">
      <div class="loading-spinner" />
    </div>

    <!-- Error State -->
    <div v-else-if="playerStore.error" class="error-container">
      <div class="error-box">{{ playerStore.error }}</div>
      <Button @click="$router.push({ name: 'Courses' })">{{ t('lesson.back_to_courses') }}</Button>
    </div>

    <!-- Worksheet Layout -->
    <div v-else-if="playerStore.currentLesson" class="worksheet-layout">
      <!-- Minimal Top Bar -->
      <header class="top-bar">
        <button class="back-btn" @click="goBackToCourse">
          <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ t('chapter.backToCourse') }}
        </button>

        <div class="top-actions">
          <Button
            v-if="!playerStore.isLessonCompleted"
            variant="primary"
            size="sm"
            @click="completeLesson"
          >
            {{ t('lesson.mark_completed') }}
          </Button>
          <span v-else class="completed-badge">
            &#10003; {{ t('lesson.completed') }}
          </span>
        </div>
      </header>

      <!-- Progress Dots -->
      <WorksheetProgressBar
        v-if="playerStore.currentChapter?.lessons"
        :lessons="playerStore.currentChapter.lessons"
        :active-lesson-id="playerStore.currentLesson?.lesson_id"
        :completed-lesson-ids="completedLessonIds"
        @navigate="navigateToLesson"
      />

      <!-- Scrollable Content Area -->
      <div ref="contentRef" class="worksheet-scroll" @scroll="handleContentScroll">
        <WorksheetPage
          :chapter-title="playerStore.currentChapter?.title ?? ''"
          :lesson-title="playerStore.currentLesson?.title ?? ''"
          :lesson-type="playerStore.currentLesson?.lesson_type ?? 'text'"
          :page-position="pagePosition"
          :is-completed="playerStore.isLessonCompleted"
          :has-previous="playerStore.hasPreviousLesson"
          :has-next="playerStore.hasNextLesson"
          :difficulty="activeDifficulty"
          @previous="goToPreviousLesson"
          @next="goToNextLesson"
          @finish="goBackToCourse"
        >
          <!-- Practice/Assessment: render task directly on the worksheet -->
          <TaskContentPanel
            v-if="playerStore.activeExecution"
            :execution="playerStore.activeExecution"
            @complete="handleTaskComplete"
          />

          <!-- Theory: render lesson content -->
          <template v-else>
            <component
              :is="lessonComponent"
              :lesson="playerStore.currentLesson"
              :course-id="courseId"
              :chapter-id="chapterId"
              class="lesson-component"
              @completed="handleLessonCompleted"
              @continue="goToNextLesson"
            />
          </template>
        </WorksheetPage>
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
import { TaskContentPanel } from '@/presentation/components/public/learning/methods/method-execution'
import WorksheetPage from '@/presentation/components/panel/user/learning/lesson/WorksheetPage.vue'
import WorksheetProgressBar from '@/presentation/components/panel/user/learning/lesson/WorksheetProgressBar.vue'

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

// Dynamic lesson components
const lessonComponents: Record<string, ReturnType<typeof defineAsyncComponent>> = {
  text: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/explanatory/TextLesson.vue')),
  video: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/explanatory/VideoLesson.vue')),
  quiz: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/quiz/QuizLesson.vue')),
  ai: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/explanatory/AiLesson.vue')),
  interactive: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/explanatory/AiLesson.vue')),
  mixed: defineAsyncComponent(() => import('@/presentation/components/public/learning/methods/explanatory/TextLesson.vue')),
}

// ─── Computed ───
const courseId = computed(() => props.courseId)
const chapterId = computed(() => props.chapterId)
const lessonId = computed(() => props.lessonId)

const lessonComponent = computed(() => {
  const type = playerStore.currentLesson?.lesson_type || 'text'
  return lessonComponents[type] || lessonComponents.text
})

// Exercise patterns — auto-activate the task on these lessons
const EXERCISE_PATTERNS = [
  'rechenaufgaben', 'lückentext', 'ihk-prüfungsaufgaben',
  'lernkarten', 'zuordnung', 'fallstudien',
]

const isExerciseLesson = computed(() => {
  const title = (playerStore.currentLesson?.title || '').toLowerCase()
  return EXERCISE_PATTERNS.some(p => title.includes(p))
})

const pagePosition = computed(() => {
  const lessons = playerStore.currentChapter?.lessons
  if (!lessons || !playerStore.currentLesson) return { step: 1, total: 1 }
  const idx = lessons.findIndex((l: any) => l.lesson_id === playerStore.currentLesson?.lesson_id)
  return { step: Math.max(1, idx + 1), total: lessons.length }
})

const activeDifficulty = computed(() => {
  return playerStore.activeExecution?.difficulty ?? undefined
})

// ─── State ───
const contentRef = ref<HTMLElement | null>(null)
const lastSyncedDepth = ref(0)
const completedLessonIds = ref<number[]>([])
const showCompletionToast = ref(false)
let scrollDebounceTimer: ReturnType<typeof setTimeout> | null = null

// ─── Navigation ───
function goBackToCourse(): void {
  router.push({ name: 'CourseOverview', params: { courseId: courseId.value } })
}

function navigateToLesson(newLessonId: number): void {
  router.push({
    name: 'LessonPlayer',
    params: { courseId: courseId.value, chapterId: chapterId.value, lessonId: newLessonId },
  })
}

function goToNextLesson(): void {
  if (playerStore.nextLesson) navigateToLesson(playerStore.nextLesson.lesson_id)
}

function goToPreviousLesson(): void {
  if (playerStore.previousLesson) navigateToLesson(playerStore.previousLesson.lesson_id)
}

// ─── Completion ───
async function completeLesson(): Promise<void> {
  try {
    await playerStore.markLessonCompleted(courseId.value, chapterId.value, lessonId.value)
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
  if (!playerStore.isLessonCompleted) completeLesson()
}

// ─── Scroll Progress ───
function handleContentScroll(): void {
  if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer)
  scrollDebounceTimer = setTimeout(() => {
    const el = contentRef.value
    if (!el) return
    const scrollDepth = el.scrollHeight - el.clientHeight
    if (scrollDepth <= 0) return
    const pct = Math.min(100, Math.round((el.scrollTop / scrollDepth) * 100))
    const milestone = Math.floor(pct / 25) * 25
    if (milestone > lastSyncedDepth.value && milestone > 0) {
      lastSyncedDepth.value = milestone
      playerStore.syncProgress(courseId.value, chapterId.value, lessonId.value, milestone)
    }
    if (pct >= 95 && !playerStore.isLessonCompleted) completeLesson()
  }, 300)
}

// ─── Task Handling ───
async function handleTaskComplete(score: number, _maxScore: number): Promise<void> {
  await playerStore.refreshMethodsProgress(lessonId.value)
}

function autoActivateExerciseTask(): void {
  if (!isExerciseLesson.value) return
  if (playerStore.activeExecution) return
  if (playerStore.availableMethods.length === 0) return
  const firstMethod = playerStore.availableMethods[0]
  playerStore.executeLearningMethod({
    lesson_id: String(lessonId.value),
    method_id: firstMethod.method_id,
  }).catch(() => { /* silent — user sees theory content as fallback */ })
}

// ─── Tutor Context ───
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
    methodType: null,
  })
}

// ─── Keyboard Shortcuts ───
function handleKeydown(e: KeyboardEvent): void {
  const tag = (e.target as HTMLElement)?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return
  switch (e.key) {
    case 'ArrowLeft': if (playerStore.hasPreviousLesson) goToPreviousLesson(); break
    case 'ArrowRight': if (playerStore.hasNextLesson) goToNextLesson(); break
    case 'Escape': goBackToCourse(); break
  }
}

// ─── Lifecycle ───
onMounted(async () => {
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
  autoActivateExerciseTask()
  window.addEventListener('keydown', handleKeydown)
})

watch(lessonId, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    playerStore.clearActiveTask()
    lastSyncedDepth.value = 0
    await playerStore.loadLesson(courseId.value, chapterId.value, newId)
    updateTutorContext()
    autoActivateExerciseTask()
  }
})

watch(() => playerStore.currentLesson, () => {
  updateTutorContext()
  lastSyncedDepth.value = 0
})

onUnmounted(() => {
  tutorStore.updateContext({
    page: 'dashboard', courseId: null, courseName: null,
    chapterId: null, chapterName: null, lessonId: null,
    lessonName: null, methodId: null, methodType: null,
  })
  window.removeEventListener('keydown', handleKeydown)
  if (scrollDebounceTimer) clearTimeout(scrollDebounceTimer)
})
</script>

<style scoped>
/* ─── Base Layout ─── */
.lesson-player {
  background-color: var(--color-bg, #f0f1f3);
  color: var(--color-text-primary, #111827);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  min-height: 100vh;
}

:root.dark .lesson-player {
  background-color: #0f172a;
}

.worksheet-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* ─── Loading / Error ─── */
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

@keyframes spin { to { transform: rotate(360deg); } }

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

/* ─── Top Bar ─── */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1.25rem;
  background: var(--color-surface, #fff);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  flex-shrink: 0;
}

:root.dark .top-bar {
  background: #1e293b;
  border-bottom-color: rgba(255, 255, 255, 0.06);
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  transition: all 0.15s;
}

.back-btn:hover {
  color: var(--color-primary, #3b82f6);
  background: rgba(59, 130, 246, 0.06);
}

.back-icon {
  width: 1rem;
  height: 1rem;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.completed-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 0.375rem;
}

/* ─── Scrollable Worksheet Area ─── */
.worksheet-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 0 3rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.08) transparent;
}

:root.dark .worksheet-scroll {
  scrollbar-color: rgba(255, 255, 255, 0.08) transparent;
}

.worksheet-scroll::-webkit-scrollbar { width: 6px; }
.worksheet-scroll::-webkit-scrollbar-track { background: transparent; }
.worksheet-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.08);
  border-radius: 3px;
}

:root.dark .worksheet-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.08);
}

/* ─── Completion Toast ─── */
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

.toast-icon { width: 1.25rem; height: 1.25rem; }

.toast-enter-active { transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.toast-leave-active { transition: all 0.3s ease-in; }
.toast-enter-from { opacity: 0; transform: translateX(-50%) translateY(20px) scale(0.9); }
.toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(-10px); }

/* ─── Print ─── */
@media print {
  .top-bar,
  .completion-toast { display: none; }

  .worksheet-layout { height: auto; }
  .worksheet-scroll { overflow: visible; padding: 0; }
  .lesson-player { background: #fff; }
}
</style>
