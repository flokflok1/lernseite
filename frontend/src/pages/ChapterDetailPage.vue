<template>
  <div class="chapter-detail">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ t('chapter.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-box">{{ error }}</div>
      <Button @click="$router.push({ name: 'CourseOverview', params: { courseId } })">
        {{ t('chapter.back_to_course') }}
      </Button>
    </div>

    <!-- Content -->
    <div v-else-if="chapter" class="chapter-content">
      <!-- Header -->
      <div class="chapter-header">
        <div class="header-left">
          <Button variant="ghost" size="sm" @click="goBackToCourse">
            <span class="back-arrow">&larr;</span> {{ t('chapter.back_to_course') }}
          </Button>
        </div>
        <div class="header-center">
          <h1 class="chapter-title">{{ chapter.title }}</h1>
          <p v-if="courseName" class="course-name">{{ courseName }}</p>
        </div>
        <div class="header-right">
          <div v-if="progress !== null" class="progress-badge">
            {{ t('chapter.progress_completed', { progress }) }}
          </div>
        </div>
      </div>

      <!-- Tab Navigation -->
      <div class="tab-navigation">
        <button
          class="tab-button"
          :class="{ active: activeTab === 'theory' }"
          @click="activeTab = 'theory'"
        >
          <span class="tab-icon">&#128214;</span>
          {{ t('chapter.tab_theory') }}
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'lessons' }"
          @click="activeTab = 'lessons'"
        >
          <span class="tab-icon">&#128218;</span>
          {{ t('chapter.tab_lessons') }}
          <span v-if="lessons.length" class="lesson-count">({{ lessons.length }})</span>
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Theory Tab -->
        <div v-if="activeTab === 'theory'" class="theory-tab">
          <ChapterTheorySection
            :chapter-id="chapterId"
            :chapter-title="chapter.title"
            :course-title="courseName"
            :theory="theoryData"
            :loading="theoryLoading"
            @generate="generateTheory"
            @start-explanation="startExplanation"
            @select-theory="loadTheoryById"
          />
        </div>

        <!-- Lessons Tab -->
        <div v-if="activeTab === 'lessons'" class="lessons-tab">
          <div class="lessons-header">
            <h2>{{ t('chapter.lessons_in_chapter') }}</h2>
            <p class="lessons-info">
              {{ t('chapter.lessons_completed', { completed: completedLessons, total: lessons.length }) }}
            </p>
          </div>

          <div class="lessons-list">
            <div
              v-for="(lesson, index) in lessons"
              :key="lesson.lesson_id"
              class="lesson-card"
              :class="getLessonStatusClass(lesson, index)"
              @click="goToLesson(lesson, index)"
            >
              <div class="lesson-number">{{ index + 1 }}</div>
              <div class="lesson-info">
                <h3 class="lesson-title">{{ lesson.title }}</h3>
                <p v-if="lesson.description" class="lesson-description">
                  {{ truncate(lesson.description, 80) }}
                </p>
                <div class="lesson-meta">
                  <span v-if="lesson.duration_minutes" class="meta-item">
                    <span class="meta-icon">&#128337;</span>
                    {{ lesson.duration_minutes }} {{ t('courses.minutes_short') }}
                  </span>
                  <span class="meta-item lesson-type">
                    {{ getLessonTypeLabel(lesson.lesson_type) }}
                  </span>
                </div>
              </div>
              <div class="lesson-status">
                <span v-if="isLessonCompleted(lesson)" class="status-icon completed">&#10003;</span>
                <span v-else-if="isCurrentLesson(index)" class="status-icon current">&#9654;</span>
                <span v-else class="status-icon available">&#9654;</span>
              </div>
            </div>
          </div>

          <div class="lessons-action">
            <Button
              v-if="currentLessonIndex !== null"
              variant="primary"
              size="lg"
              @click="startLearning"
            >
              &#9654; {{ currentLessonIndex === 0 ? t('chapter.start_learning') : t('chapter.continue_learning') }}
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Lesson Modal Overlay -->
    <Teleport to="body">
      <div v-if="showLessonModal" class="lesson-modal-overlay" @click.self="closeLessonModal">
        <div class="lesson-modal">
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="modal-header-left">
              <span class="lesson-badge">{{ t('lesson.lesson_count', { current: (selectedLessonIndex ?? 0) + 1, total: lessons.length }) }}</span>
              <h2 class="modal-title">{{ selectedLesson?.title || lessons[selectedLessonIndex ?? 0]?.title }}</h2>
            </div>
            <button class="modal-close" @click="closeLessonModal">&times;</button>
          </div>

          <!-- Modal Tabs -->
          <div class="modal-tabs">
            <button
              class="modal-tab"
              :class="{ active: modalTab === 'lesson' }"
              @click="modalTab = 'lesson'"
            >
              <span class="tab-icon">📖</span>
              {{ t('lesson.tab_lesson') }}
            </button>
            <button
              class="modal-tab"
              :class="{ active: modalTab === 'tutor' }"
              @click="switchToTutorTab"
            >
              <span class="tab-icon">🎓</span>
              {{ t('lesson.tab_tutor') }}
              <span v-if="lessonExplanations.length > 0" class="tab-badge">{{ lessonExplanations.length }}</span>
            </button>
          </div>

          <!-- Modal Content -->
          <div class="modal-content" :class="{ 'tutor-content': modalTab === 'tutor' }">
            <!-- LESSON TAB -->
            <template v-if="modalTab === 'lesson'">
              <!-- Loading State -->
              <div v-if="lessonLoading" class="lesson-loading">
                <div class="loading-spinner"></div>
                <p>{{ t('lesson.loading') }}</p>
              </div>

              <!-- Lesson Content -->
              <template v-else-if="selectedLesson">
                <!-- Mode Selector (only for lessons with modes) -->
                <div v-if="lessonModes && lessonModes.available?.length > 1" class="mode-selector">
                  <div class="mode-selector-label">{{ t('lesson.select_mode') }}</div>
                  <div class="mode-buttons">
                    <button
                      v-for="modeKey in lessonModes.available"
                      :key="modeKey"
                      class="mode-btn"
                      :class="{ active: selectedMode === modeKey }"
                      @click="selectedMode = modeKey"
                    >
                      <span class="mode-icon">{{ getModeConfig(modeKey)?.icon || '📖' }}</span>
                      <span class="mode-label">{{ getModeConfig(modeKey)?.label || modeKey }}</span>
                    </button>
                  </div>
                  <p v-if="getModeConfig(selectedMode)?.description" class="mode-description">
                    {{ getModeConfig(selectedMode).description }}
                  </p>
                </div>

                <!-- Lesson Description -->
                <div v-if="selectedLesson.description" class="lesson-description">
                  <p>{{ selectedLesson.description }}</p>
                </div>

                <!-- For interactive/ai lessons: Show MethodExecutionPanel (Aufgaben) -->
                <div v-if="isInteractiveLesson(selectedLesson)" class="interactive-tasks-wrapper">
                  <MethodExecutionPanel
                    :lesson-id="selectedLesson.lesson_id"
                    :methods="lessonMethods"
                    :mode="selectedMode"
                  />
                </div>

                <!-- For text/video/quiz lessons: Show component directly -->
                <div v-else class="lesson-component-wrapper">
                  <component
                    :is="getLessonComponent(selectedLesson.lesson_type)"
                    :lesson="selectedLesson"
                    :lesson-id="selectedLesson.lesson_id"
                    @completed="markLessonAsCompleted"
                  />
                </div>
              </template>
            </template>

            <!-- TUTOR TAB -->
            <template v-else-if="modalTab === 'tutor'">
              <div class="tutor-layout">
                <!-- Left: Explanation List -->
                <div class="explanation-list-panel">
                  <div class="list-header">
                    <h3>{{ t('lesson.explanations') }}</h3>
                  </div>

                  <!-- Loading List -->
                  <div v-if="explanationsLoading" class="list-loading">
                    <div class="small-spinner"></div>
                    <span>{{ t('lesson.loading_short') }}</span>
                  </div>

                  <!-- Empty List -->
                  <div v-else-if="lessonExplanations.length === 0" class="list-empty">
                    <p>{{ t('lesson.no_explanations') }}</p>
                    <p class="list-empty-hint">{{ t('lesson.explanations_hint') }}</p>
                  </div>

                  <!-- List Items -->
                  <div v-else class="list-items">
                    <div
                      v-for="expl in lessonExplanations"
                      :key="expl.explanationId"
                      class="list-item"
                      :class="{ active: selectedExplanationId === expl.explanationId }"
                      @click="selectExplanation(expl.explanationId)"
                    >
                      <div class="item-main">
                        <span class="item-title">{{ expl.title }}</span>
                        <span class="item-meta">
                          {{ expl.style }} | {{ formatExplanationDate(expl.createdAt) }}
                        </span>
                      </div>
                      <div v-if="expl.hasAudio" class="item-audio-badge" title="Mit Audio">
                        🔊
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Right: Content Area -->
                <div class="content-panel">
                  <!-- Loading Explanation -->
                  <div v-if="explanationLoading" class="explanation-loading">
                    <div class="loading-spinner"></div>
                    <p>{{ t('lesson.explanation_loading') }}</p>
                  </div>

                  <!-- No Selection -->
                  <div v-else-if="!selectedExplanation && lessonExplanations.length > 0" class="no-selection">
                    <p>{{ t('lesson.select_explanation') }}</p>
                  </div>

                  <!-- Empty State -->
                  <div v-else-if="lessonExplanations.length === 0" class="no-explanations">
                    <div class="no-content-icon">🎓</div>
                    <h3>{{ t('lesson.no_tutor_explanations') }}</h3>
                    <p>{{ t('lesson.no_tutor_explanations_hint') }}</p>
                  </div>

                  <!-- Explanation Content -->
                  <template v-else-if="selectedExplanation">
                    <!-- Audio Player -->
                    <div v-if="selectedExplanation.audioUrl" class="audio-section">
                      <audio
                        ref="audioPlayer"
                        :src="selectedExplanation.audioUrl"
                        controls
                        class="audio-player"
                      ></audio>
                    </div>

                    <!-- Overview -->
                    <div v-if="selectedExplanation.overview" class="explanation-overview">
                      <strong>{{ t('lesson.overview') }}</strong>
                      <p>{{ selectedExplanation.overview }}</p>
                    </div>

                    <!-- Steps -->
                    <div v-if="selectedExplanation.steps?.length" class="explanation-steps">
                      <div
                        v-for="(step, index) in selectedExplanation.steps"
                        :key="index"
                        class="step-card"
                      >
                        <div class="step-number">{{ index + 1 }}</div>
                        <div class="step-content">
                          <h4 v-if="step.title" class="step-title">{{ step.title }}</h4>
                          <p class="step-text">{{ step.text || step.content }}</p>
                          <div v-if="step.example" class="step-example">
                            <strong>{{ t('lesson.example') }}</strong> {{ step.example }}
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Summary -->
                    <div v-if="selectedExplanation.summary" class="explanation-summary">
                      <strong>{{ t('lesson.summary') }}</strong>
                      <p>{{ selectedExplanation.summary }}</p>
                    </div>
                  </template>
                </div>
              </div>
            </template>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <div class="footer-left">
              <button
                v-if="selectedLessonIndex !== null && selectedLessonIndex > 0"
                class="nav-btn prev"
                @click="goToPrevLessonInModal"
              >
                ← {{ t('lesson.previous') }}
              </button>
            </div>

            <div class="footer-center">
              <template v-if="selectedLesson && !lessonLoading">
                <button
                  v-if="!isLessonCompleted(selectedLesson)"
                  class="complete-btn"
                  @click="markLessonAsCompleted"
                >
                  ✓ {{ t('lesson.mark_completed') }}
                </button>
                <span v-else class="completed-text">✓ {{ t('lesson.completed') }}</span>
              </template>
            </div>

            <div class="footer-right">
              <button
                v-if="selectedLessonIndex !== null && selectedLessonIndex < lessons.length - 1"
                class="nav-btn next"
                @click="goToNextLessonInModal"
              >
                {{ t('lesson.next') }} →
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, defineAsyncComponent, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from '@/components/ui/Button.vue'
import ChapterTheorySection from '@/components/chapter/ChapterTheorySection.vue'
import MethodExecutionPanel from '@/components/lesson/MethodExecutionPanel.vue'
import { useTutorStore } from '@/store/tutor.store'
import { useAuthStore } from '@/store/auth.store'
import http from '@/api/http'

// Async Lesson Components
const lessonComponents: Record<string, Component> = {
  text: defineAsyncComponent(() => import('@/components/lesson/TextLesson.vue')),
  video: defineAsyncComponent(() => import('@/components/lesson/VideoLesson.vue')),
  quiz: defineAsyncComponent(() => import('@/components/lesson/QuizLesson.vue')),
  ai: defineAsyncComponent(() => import('@/components/lesson/AiLesson.vue')),
  interactive: defineAsyncComponent(() => import('@/components/lesson/AiLesson.vue')),
  mixed: defineAsyncComponent(() => import('@/components/lesson/TextLesson.vue'))
}

const getLessonComponent = (lessonType: string): Component => {
  return lessonComponents[lessonType] || lessonComponents.text
}

// ============================================================================
// Props
// ============================================================================

interface Props {
  courseId: string
  chapterId: string
}

const props = defineProps<Props>()

// ============================================================================
// State
// ============================================================================

const { t } = useI18n()
const router = useRouter()
const tutorStore = useTutorStore()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref<string | null>(null)

// Chapter data
const chapter = ref<any>(null)
const courseName = ref<string>('')
const lessons = ref<any[]>([])
const lessonProgress = ref<Record<string, any>>({})

// Theory data
const theoryData = ref<any>(null)
const theoryLoading = ref(false)

// Tab state
const activeTab = ref<'theory' | 'lessons'>('theory')

// Lesson Modal state
const showLessonModal = ref(false)
const selectedLesson = ref<any>(null)
const selectedLessonIndex = ref<number | null>(null)
const lessonLoading = ref(false)
const modalTab = ref<'lesson' | 'tutor'>('lesson')

// Tutor Explanations state
const lessonExplanations = ref<any[]>([])
const selectedExplanationId = ref<string | null>(null)
const selectedExplanation = ref<any>(null)
const explanationsLoading = ref(false)
const explanationLoading = ref(false)
const audioPlayer = ref<HTMLAudioElement | null>(null)

// Lesson Mode state
const selectedMode = ref<string>('muster')

// Lesson Methods (for MethodExecutionPanel)
const lessonMethods = ref<any[]>([])

// LocalStorage key for visited chapters
const VISITED_KEY = 'lsx_visited_chapters'

// ============================================================================
// Computed
// ============================================================================

const progress = computed(() => {
  if (!lessons.value.length) return null
  const completed = lessons.value.filter(l => isLessonCompleted(l)).length
  return Math.round((completed / lessons.value.length) * 100)
})

const completedLessons = computed(() => {
  return lessons.value.filter(l => isLessonCompleted(l)).length
})

const currentLessonIndex = computed(() => {
  // Find first incomplete lesson
  const index = lessons.value.findIndex(l => !isLessonCompleted(l))
  return index >= 0 ? index : (lessons.value.length > 0 ? 0 : null)
})

// Check if user can create exam simulations (admin, teacher, creator, school, company)
const canCreateExam = computed(() => {
  const role = authStore.userRole
  return ['admin', 'superadmin', 'teacher', 'creator', 'school_admin', 'company_admin'].includes(role)
})

// Get available modes for current lesson
const lessonModes = computed(() => {
  const content = selectedLesson.value?.content
  if (!content?.modes) return null
  return content.modes
})

// Get mode config for display
const getModeConfig = (modeKey: string) => {
  return lessonModes.value?.config?.[modeKey] || null
}

// ============================================================================
// Methods
// ============================================================================

const isFirstVisit = (): boolean => {
  try {
    const visited = JSON.parse(localStorage.getItem(VISITED_KEY) || '[]')
    return !visited.includes(props.chapterId)
  } catch {
    return true
  }
}

const markAsVisited = () => {
  try {
    const visited = JSON.parse(localStorage.getItem(VISITED_KEY) || '[]')
    if (!visited.includes(props.chapterId)) {
      visited.push(props.chapterId)
      localStorage.setItem(VISITED_KEY, JSON.stringify(visited))
    }
  } catch {
    // Ignore localStorage errors
  }
}

const isLessonCompleted = (lesson: any): boolean => {
  if (!lesson?.lesson_id) return false
  // Check if lesson has progress data
  const progress = lessonProgress.value[lesson.lesson_id]
  if (progress?.is_completed) return true
  // Also check if lesson itself has completion flag from API
  return lesson.is_completed || false
}

const isCurrentLesson = (index: number): boolean => {
  return index === currentLessonIndex.value
}

const getLessonStatusClass = (lesson: any, index: number): string => {
  if (isLessonCompleted(lesson)) return 'completed'
  if (isCurrentLesson(index)) return 'current'
  // All lessons are available - no locking
  return 'available'
}

const getLessonTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    text: t('lesson.type_text'),
    video: t('lesson.type_video'),
    quiz: t('lesson.type_quiz'),
    ai: t('lesson.type_ai'),
    interactive: t('lesson.type_interactive'),
    mixed: t('lesson.type_mixed')
  }
  return labels[type] || type
}

const isInteractiveLesson = (lesson: any): boolean => {
  if (!lesson) return false
  return ['ai', 'interactive'].includes(lesson.lesson_type)
}

const openInFullPlayer = () => {
  if (!selectedLesson.value?.lesson_id) return
  const lessonId = selectedLesson.value.lesson_id
  closeLessonModal()
  router.push({
    name: 'LessonPlayer',
    params: {
      courseId: props.courseId,
      chapterId: props.chapterId,
      lessonId: lessonId
    }
  })
}

const truncate = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

// ============================================================================
// Navigation
// ============================================================================

const goBackToCourse = () => {
  router.push({
    name: 'CourseOverview',
    params: { courseId: props.courseId }
  })
}

const goToExamSimulation = () => {
  router.push({
    name: 'ExamSimulation',
    params: { courseId: props.courseId }
  })
}

const goToLesson = async (lesson: any, index: number) => {
  // Open lesson in modal
  selectedLessonIndex.value = index
  showLessonModal.value = true
  lessonLoading.value = true
  selectedLesson.value = null
  modalTab.value = 'lesson'
  lessonExplanations.value = []
  selectedExplanation.value = null
  selectedExplanationId.value = null
  selectedMode.value = 'muster' // Reset to default mode
  lessonMethods.value = [] // Reset methods

  // Load full lesson data with content
  try {
    const response = await http.get(`/lessons/${lesson.lesson_id}`)
    if (response.data.success) {
      selectedLesson.value = response.data.data || response.data.lesson || lesson
      // Set default mode from lesson content if available
      if (selectedLesson.value?.content?.modes?.default) {
        selectedMode.value = selectedLesson.value.content.modes.default
      }
    } else {
      selectedLesson.value = lesson
    }

    // Load learning methods for this lesson
    const methodsResponse = await http.get(`/lessons/${lesson.lesson_id}/methods`)
    if (methodsResponse.data.success) {
      lessonMethods.value = methodsResponse.data.methods || []
    }
  } catch (err) {
    console.error('Failed to load lesson details:', err)
    selectedLesson.value = lesson
  } finally {
    lessonLoading.value = false
  }
}

const closeLessonModal = () => {
  showLessonModal.value = false
  selectedLesson.value = null
  modalTab.value = 'lesson'
  lessonExplanations.value = []
  selectedExplanation.value = null
  selectedExplanationId.value = null
  lessonMethods.value = []
}

// ============================================================================
// Tutor Explanations
// ============================================================================

const switchToTutorTab = async () => {
  modalTab.value = 'tutor'
  if (lessonExplanations.value.length === 0 && selectedLesson.value) {
    await loadLessonExplanations()
  }
}

const loadLessonExplanations = async () => {
  if (!selectedLesson.value?.lesson_id) return

  explanationsLoading.value = true
  try {
    const response = await http.get(`/lessons/${selectedLesson.value.lesson_id}/explanations`)
    if (response.data.success) {
      lessonExplanations.value = response.data.data?.explanations || []
      // Auto-select first if available
      if (lessonExplanations.value.length > 0 && !selectedExplanationId.value) {
        await selectExplanation(lessonExplanations.value[0].explanationId)
      }
    }
  } catch (err) {
    console.error('Failed to load lesson explanations:', err)
    lessonExplanations.value = []
  } finally {
    explanationsLoading.value = false
  }
}

const selectExplanation = async (explanationId: string) => {
  if (selectedExplanationId.value === explanationId && selectedExplanation.value) return

  selectedExplanationId.value = explanationId
  explanationLoading.value = true
  selectedExplanation.value = null

  try {
    const response = await http.get(`/lesson-explanation/${explanationId}`)
    if (response.data.success) {
      selectedExplanation.value = response.data.data
    }
  } catch (err) {
    console.error('Failed to load explanation:', err)
  } finally {
    explanationLoading.value = false
  }
}

const formatExplanationDate = (dateStr: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

const goToNextLessonInModal = async () => {
  if (selectedLessonIndex.value !== null && selectedLessonIndex.value < lessons.value.length - 1) {
    const nextIndex = selectedLessonIndex.value + 1
    const nextLesson = lessons.value[nextIndex]
    selectedLessonIndex.value = nextIndex
    lessonLoading.value = true
    selectedLesson.value = null
    lessonMethods.value = [] // Reset methods
    // Reset tutor state for new lesson
    modalTab.value = 'lesson'
    lessonExplanations.value = []
    selectedExplanation.value = null
    selectedExplanationId.value = null

    try {
      const response = await http.get(`/lessons/${nextLesson.lesson_id}`)
      if (response.data.success) {
        selectedLesson.value = response.data.data || response.data.lesson || nextLesson
      } else {
        selectedLesson.value = nextLesson
      }

      // Load learning methods for this lesson
      const methodsResponse = await http.get(`/lessons/${nextLesson.lesson_id}/methods`)
      if (methodsResponse.data.success) {
        lessonMethods.value = methodsResponse.data.methods || []
      }
    } catch (err) {
      selectedLesson.value = nextLesson
    } finally {
      lessonLoading.value = false
    }
  }
}

const goToPrevLessonInModal = async () => {
  if (selectedLessonIndex.value !== null && selectedLessonIndex.value > 0) {
    const prevIndex = selectedLessonIndex.value - 1
    const prevLesson = lessons.value[prevIndex]
    selectedLessonIndex.value = prevIndex
    lessonLoading.value = true
    selectedLesson.value = null
    lessonMethods.value = [] // Reset methods
    // Reset tutor state for new lesson
    modalTab.value = 'lesson'
    lessonExplanations.value = []
    selectedExplanation.value = null
    selectedExplanationId.value = null

    try {
      const response = await http.get(`/lessons/${prevLesson.lesson_id}`)
      if (response.data.success) {
        selectedLesson.value = response.data.data || response.data.lesson || prevLesson
      } else {
        selectedLesson.value = prevLesson
      }

      // Load learning methods for this lesson
      const methodsResponse = await http.get(`/lessons/${prevLesson.lesson_id}/methods`)
      if (methodsResponse.data.success) {
        lessonMethods.value = methodsResponse.data.methods || []
      }
    } catch (err) {
      selectedLesson.value = prevLesson
    } finally {
      lessonLoading.value = false
    }
  }
}

// Go back to theory tab
const goBackToTheory = () => {
  closeLessonModal()
  activeTab.value = 'theory'
}

// Open practice mode (could navigate to quiz or interactive lesson)
const openPracticeMode = () => {
  // For now, just mark as needing practice
  console.log('Practice mode requested for lesson:', selectedLesson.value?.title)
  // Could emit event or navigate to a practice component
}

// Detailed Steps Generation now handled by LessonTutorPlayer component

const markLessonAsCompleted = async () => {
  if (!selectedLesson.value) return

  try {
    await http.post(`/lessons/${selectedLesson.value.lesson_id}/complete`)
    // Refresh chapter data
    await loadChapter()
  } catch (err) {
    console.error('Failed to mark lesson completed:', err)
  }
}

const startLearning = () => {
  if (currentLessonIndex.value !== null && lessons.value[currentLessonIndex.value]) {
    const lesson = lessons.value[currentLessonIndex.value]
    goToLesson(lesson, currentLessonIndex.value)
  }
}

// ============================================================================
// Theory Generation
// ============================================================================

const generateTheory = async () => {
  theoryLoading.value = true
  try {
    const response = await http.post(`/chapters/${props.chapterId}/theory/generate`, {
      style: 'adhs',
      generateTts: true,
      ttsVoice: 'nova'
    })
    if (response.data.success) {
      theoryData.value = {
        hasTheory: true,
        theory: response.data.data,
        audioUrl: response.data.audioUrl,
        style: response.data.style
      }
    }
  } catch (err: any) {
    console.error('Failed to generate theory:', err)
    error.value = 'Fehler beim Generieren der Theorie'
  } finally {
    theoryLoading.value = false
  }
}

const startExplanation = () => {
  // This will be handled by ChapterTheorySection
  console.log('Starting explanation with TTS + Whiteboard')
}

// Load a specific theory by ID (when user selects from dropdown)
const loadTheoryById = async (theoryId: string) => {
  try {
    const response = await http.get(`/chapter-theory/${theoryId}`)
    if (response.data.success) {
      const data = response.data.data
      theoryData.value = {
        hasTheory: true,
        theory: data.theory,
        audioUrl: data.audioUrl,
        style: data.style,
        theoryId: data.theoryId,
        title: data.title
      }
      console.log('Loaded theory:', data.title)
    }
  } catch (err: any) {
    console.error('Failed to load theory:', err)
  }
}

// ============================================================================
// Data Loading
// ============================================================================

const loadChapter = async () => {
  loading.value = true
  error.value = null

  try {
    // Load chapter details
    const chapterResponse = await http.get(`/courses/${props.courseId}/chapters/${props.chapterId}`)
    if (chapterResponse.data.success) {
      // API returns 'chapter' not 'data'
      chapter.value = chapterResponse.data.chapter || chapterResponse.data.data
      lessons.value = chapter.value?.lessons || []
    }

    // Load course info
    const courseResponse = await http.get(`/courses/${props.courseId}`)
    if (courseResponse.data.success) {
      // API returns 'course' not 'data'
      const courseData = courseResponse.data.course || courseResponse.data.data
      courseName.value = courseData?.title || ''
    }

    // Load lesson progress for each lesson in the chapter
    // API doesn't have batch endpoint, so we load individually or skip for now
    try {
      // Use chapter progress endpoint which gives us completion count
      const progressResponse = await http.get(`/courses/${props.courseId}/chapters/${props.chapterId}/progress`)
      if (progressResponse.data.success) {
        const progressData = progressResponse.data.progress || progressResponse.data.data
        // Store chapter-level progress info
        // lessonProgress will be populated per-lesson if needed
        console.log('Chapter progress:', progressData)
      }
    } catch {
      // Progress may not exist yet
    }

    // Load existing theory
    try {
      const theoryResponse = await http.get(`/chapters/${props.chapterId}/theory?style=adhs`)
      if (theoryResponse.data.success) {
        theoryData.value = theoryResponse.data.data
      }
    } catch {
      // Theory may not exist yet
    }

    // Determine initial tab based on first visit
    if (isFirstVisit()) {
      activeTab.value = 'theory'
      markAsVisited()
    } else {
      activeTab.value = 'lessons'
    }

  } catch (err: any) {
    console.error('Failed to load chapter:', err)
    error.value = err.response?.data?.message || t('chapter.load_error')
  } finally {
    loading.value = false
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(async () => {
  await loadChapter()

  // Update tutor context with chapter info
  tutorStore.updateContext({
    page: 'chapter',
    courseId: props.courseId,
    courseName: courseName.value || null,
    chapterId: props.chapterId,
    chapterName: chapter.value?.title || null,
    lessonId: null,
    lessonName: null,
    methodId: null,
    methodType: null
  })
})

watch(() => props.chapterId, async () => {
  await loadChapter()

  // Update tutor context when chapter changes
  tutorStore.updateContext({
    page: 'chapter',
    courseId: props.courseId,
    courseName: courseName.value || null,
    chapterId: props.chapterId,
    chapterName: chapter.value?.title || null,
    lessonId: null,
    lessonName: null,
    methodId: null,
    methodType: null
  })
})

onUnmounted(() => {
  // Clear tutor context when leaving the chapter
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
.chapter-detail {
  min-height: 100vh;
  background: var(--color-bg, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: var(--color-text-secondary, #94a3b8);
}

/* Error */
.error-container {
  max-width: 600px;
  margin: 4rem auto;
  padding: 2rem;
  text-align: center;
}

.error-box {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

/* Content */
.chapter-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* Header */
.chapter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  flex: 1;
}

.back-arrow {
  margin-right: 0.25rem;
}

.header-center {
  flex: 2;
  text-align: center;
}

.chapter-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.course-name {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  margin: 0.25rem 0 0;
}

.header-right {
  flex: 1;
  text-align: right;
}

.progress-badge {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 9999px;
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 600;
}

/* Tab Navigation */
.tab-navigation {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: rgba(30, 41, 59, 0.5);
  padding: 0.375rem;
  border-radius: 0.75rem;
  width: fit-content;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-button:hover {
  color: var(--color-text-primary, #f1f5f9);
  background: rgba(255, 255, 255, 0.05);
}

.tab-button.active {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.tab-icon {
  font-size: 1.1rem;
}

.lesson-count {
  font-size: 0.75rem;
  opacity: 0.8;
}

/* Tab Content */
.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Lessons Tab */
.lessons-tab {
  background: var(--color-surface, #1e293b);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.lessons-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.lessons-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.lessons-info {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
  margin: 0;
}

/* Lesson Cards */
.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.lesson-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.lesson-card:hover:not(.locked) {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
  transform: translateX(4px);
}

.lesson-card.completed {
  border-color: rgba(16, 185, 129, 0.3);
}

.lesson-card.current {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.1);
}

.lesson-card.locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.lesson-card.available {
  border-color: rgba(148, 163, 184, 0.2);
}

.lesson-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(99, 102, 241, 0.2);
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.875rem;
  color: #818cf8;
  flex-shrink: 0;
}

.lesson-card.completed .lesson-number {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.lesson-card.current .lesson-number {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.lesson-info {
  flex: 1;
  min-width: 0;
}

.lesson-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem;
  color: var(--color-text-primary, #f1f5f9);
}

.lesson-description {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #94a3b8);
  margin: 0 0 0.5rem;
}

.lesson-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.meta-icon {
  font-size: 0.875rem;
}

.lesson-type {
  padding: 0.125rem 0.5rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 0.25rem;
  color: #818cf8;
}

.lesson-status {
  flex-shrink: 0;
}

.status-icon {
  font-size: 1.25rem;
}

.status-icon.completed {
  color: #10b981;
}

.status-icon.current {
  color: #f59e0b;
}

.status-icon.locked {
  color: var(--color-text-tertiary, #64748b);
}

.status-icon.available {
  color: var(--color-text-secondary, #94a3b8);
  opacity: 0.5;
}

/* Lessons Action */
.lessons-action {
  margin-top: 1.5rem;
  text-align: center;
}

/* KI-Prüfungssimulation CTA */
.exam-simulation-cta {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 1rem;
  margin-bottom: 1.5rem;
}

.exam-cta-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.exam-cta-content {
  flex: 1;
}

.exam-cta-content h3 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.exam-cta-content p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.exam-cta-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.exam-cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
}

/* Mode Selector */
.mode-selector {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.mode-selector-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary, #94a3b8);
  margin-bottom: 0.75rem;
}

.mode-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
  color: var(--color-text-primary, #f1f5f9);
}

.mode-btn.active {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366f1;
  color: #818cf8;
  font-weight: 600;
}

.mode-icon {
  font-size: 1.1rem;
}

.mode-label {
  font-size: 0.875rem;
}

.mode-description {
  margin: 0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary, #64748b);
  font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
  .chapter-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .header-left, .header-right {
    text-align: center;
  }

  .tab-navigation {
    width: 100%;
  }

  .tab-button {
    flex: 1;
    justify-content: center;
  }

  .lesson-card {
    flex-wrap: wrap;
  }

  .lesson-info {
    flex-basis: calc(100% - 60px);
  }

  .exam-simulation-cta {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }

  .exam-cta-btn {
    width: 100%;
  }

  .mode-buttons {
    flex-direction: column;
  }

  .mode-btn {
    justify-content: center;
  }
}

/* ============================================ */
/* LESSON MODAL */
/* ============================================ */
.lesson-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.lesson-modal {
  background: var(--color-surface, #1e293b);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.5);
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.lesson-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-secondary, #94a3b8);
  border-radius: 0.5rem;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Modal Tabs */
.modal-tabs {
  display: flex;
  gap: 0;
  background: rgba(15, 23, 42, 0.3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border: none;
  background: transparent;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.modal-tab:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary, #f1f5f9);
}

.modal-tab.active {
  color: var(--color-primary, #6366f1);
  background: rgba(99, 102, 241, 0.1);
  border-bottom-color: var(--color-primary, #6366f1);
}

.modal-tab .tab-icon {
  font-size: 1rem;
}

/* Lesson Content Tab */
.lesson-content-tab {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.lesson-description {
  padding: 1rem 1.25rem;
  background: rgba(99, 102, 241, 0.1);
  border-left: 3px solid var(--color-primary, #6366f1);
  border-radius: 0 0.5rem 0.5rem 0;
}

.lesson-description p {
  margin: 0;
  color: var(--color-text-primary, #f1f5f9);
  line-height: 1.6;
}

.lesson-component-wrapper {
  min-height: 300px;
}

.interactive-tasks-wrapper {
  min-height: 400px;
}

/* Interactive Lesson Prompt */
.interactive-lesson-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 3rem 2rem;
  gap: 1rem;
}

.interactive-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.interactive-lesson-prompt h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary, #f1f5f9);
}

.interactive-lesson-prompt > p {
  margin: 0;
  color: var(--color-text-secondary, #94a3b8);
  max-width: 400px;
}

.lesson-topic {
  padding: 0.75rem 1.25rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 0.5rem;
  color: var(--color-text-primary, #f1f5f9);
}

.lesson-topic strong {
  color: #818cf8;
}

.lesson-meta-info {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.meta-badge {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.open-player-btn {
  margin-top: 1rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.open-player-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

.player-hint {
  font-size: 0.8rem;
  color: var(--color-text-tertiary, #64748b);
  margin: 0;
}

/* Lesson Loading */
.lesson-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.lesson-loading p {
  color: var(--color-text-secondary, #94a3b8);
  margin: 0;
}

.tutor-hint {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.tutor-hint .hint-icon {
  font-size: 1.25rem;
}

.tutor-hint strong {
  color: #fbbf24;
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.modal-content.tutor-modal-content {
  padding: 0;
  display: flex;
  flex-direction: column;
}

.lesson-info-card {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.info-row:not(:last-child) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.info-row.description {
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.8125rem;
  color: var(--color-text-tertiary, #64748b);
  min-width: 80px;
}

.info-value {
  font-size: 0.875rem;
  color: var(--color-text-primary, #f1f5f9);
  margin: 0;
}

.type-badge {
  padding: 0.25rem 0.5rem;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Detailed Steps Section */
.detailed-steps-section {
  margin-bottom: 1.5rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
  margin: 0;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.loading-hint {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
  animation: pulse 1.5s ease infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.steps-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.steps-loading p {
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
  margin: 0;
}

.loading-spinner.small {
  width: 32px;
  height: 32px;
  border-width: 3px;
}

/* Detailed Extras */
.detailed-extras {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-overview,
.detail-example,
.detail-summary,
.detail-practice {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #94a3b8);
}

.detail-overview strong,
.detail-example strong,
.detail-summary strong,
.detail-practice strong {
  color: var(--color-text-primary, #f1f5f9);
  display: block;
  margin-bottom: 0.5rem;
}

.detail-example {
  background: rgba(245, 158, 11, 0.05);
  border-color: rgba(245, 158, 11, 0.1);
}

.detail-practice {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.1);
}

.detail-practice p {
  margin: 0 0 0.75rem;
}

.practice-values {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.practice-value {
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.8125rem;
}

.practice-solution {
  padding: 0.5rem 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 0.25rem;
  color: #10b981;
  font-weight: 600;
}

.lesson-content-area {
  min-height: 300px;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.5);
}

.footer-left, .footer-right {
  min-width: 120px;
}

.footer-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-btn {
  padding: 0.625rem 1rem;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: var(--color-text-primary, #f1f5f9);
}

.nav-btn.next {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
  color: #818cf8;
}

.nav-btn.next:hover {
  background: rgba(99, 102, 241, 0.2);
}

.complete-btn {
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.complete-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.completed-text {
  color: #10b981;
  font-size: 0.875rem;
  font-weight: 600;
}

/* Mobile adjustments for modal */
@media (max-width: 640px) {
  .lesson-modal-overlay {
    padding: 1rem;
  }

  .lesson-modal {
    max-height: 95vh;
  }

  .modal-header {
    padding: 1rem;
  }

  .modal-header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .modal-title {
    font-size: 1.1rem;
  }

  .modal-content {
    padding: 1rem;
  }

  .modal-footer {
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .footer-left, .footer-right, .footer-center {
    min-width: unset;
  }
}

/* ============================================ */
/* TUTOR EXPLANATIONS LAYOUT */
/* ============================================ */

.tab-badge {
  background: rgba(99, 102, 241, 0.3);
  color: #818cf8;
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.modal-content.tutor-content {
  padding: 0;
}

.tutor-layout {
  display: flex;
  height: 100%;
  min-height: 400px;
}

.explanation-list-panel {
  width: 280px;
  min-width: 280px;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  background: rgba(15, 23, 42, 0.3);
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.list-header h3 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.list-loading,
.list-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  gap: 0.5rem;
  text-align: center;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.875rem;
}

.list-empty-hint {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
}

.small-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.list-items {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 0.25rem;
}

.list-item:hover {
  background: rgba(99, 102, 241, 0.1);
}

.list-item.active {
  background: rgba(99, 102, 241, 0.2);
  border-left: 3px solid #6366f1;
}

.item-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.item-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary, #f1f5f9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-meta {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #64748b);
}

.item-audio-badge {
  font-size: 1rem;
  opacity: 0.7;
}

.content-panel {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

.explanation-loading,
.no-selection,
.no-explanations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
  text-align: center;
  color: var(--color-text-secondary, #94a3b8);
}

.no-content-icon {
  font-size: 3rem;
  opacity: 0.5;
}

.no-explanations h3 {
  margin: 0;
  color: var(--color-text-primary, #f1f5f9);
}

.no-explanations p {
  margin: 0;
  font-size: 0.875rem;
}

.audio-section {
  margin-bottom: 1.5rem;
}

.audio-player {
  width: 100%;
  border-radius: 0.5rem;
}

.explanation-overview,
.explanation-summary {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.explanation-overview strong,
.explanation-summary strong {
  color: #818cf8;
  display: block;
  margin-bottom: 0.5rem;
}

.explanation-overview p,
.explanation-summary p {
  margin: 0;
  color: var(--color-text-primary, #f1f5f9);
  line-height: 1.6;
}

.explanation-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.step-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.75rem;
}

.step-number {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(99, 102, 241, 0.2);
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.875rem;
  color: #818cf8;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary, #f1f5f9);
}

.step-text {
  margin: 0;
  color: var(--color-text-secondary, #94a3b8);
  line-height: 1.6;
}

.step-example {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: var(--color-text-primary, #f1f5f9);
}

.step-example strong {
  color: #f59e0b;
}

/* Mobile Tutor Layout */
@media (max-width: 768px) {
  .tutor-layout {
    flex-direction: column;
  }

  .explanation-list-panel {
    width: 100%;
    min-width: unset;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
}
</style>
