<template>
  <div class="chapter-detail">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Kapitel wird geladen...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-box">{{ error }}</div>
      <Button @click="$router.push({ name: 'CourseOverview', params: { courseId } })">
        Zuruck zum Kurs
      </Button>
    </div>

    <!-- Content -->
    <div v-else-if="chapter" class="chapter-content">
      <!-- Header -->
      <div class="chapter-header">
        <div class="header-left">
          <Button variant="ghost" size="sm" @click="goBackToCourse">
            <span class="back-arrow">&larr;</span> Zuruck zum Kurs
          </Button>
        </div>
        <div class="header-center">
          <h1 class="chapter-title">{{ chapter.title }}</h1>
          <p v-if="courseName" class="course-name">{{ courseName }}</p>
        </div>
        <div class="header-right">
          <div v-if="progress !== null" class="progress-badge">
            {{ progress }}% abgeschlossen
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
          Theorie
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'lessons' }"
          @click="activeTab = 'lessons'"
        >
          <span class="tab-icon">&#128218;</span>
          Lektionen
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
          />
        </div>

        <!-- Lessons Tab -->
        <div v-if="activeTab === 'lessons'" class="lessons-tab">
          <div class="lessons-header">
            <h2>Lektionen in diesem Kapitel</h2>
            <p class="lessons-info">
              {{ completedLessons }}/{{ lessons.length }} abgeschlossen
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
                    {{ lesson.duration_minutes }} Min.
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
              &#9654; {{ currentLessonIndex === 0 ? 'Lernen starten' : 'Fortsetzen' }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Button from '@/components/ui/Button.vue'
import ChapterTheorySection from '@/components/chapter/ChapterTheorySection.vue'
import http from '@/api/http'

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

const router = useRouter()

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
    text: 'Text',
    video: 'Video',
    quiz: 'Quiz',
    ai: 'KI-Interaktiv',
    interactive: 'Interaktiv',
    mixed: 'Gemischt'
  }
  return labels[type] || type
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

const goToLesson = (lesson: any, _index: number) => {
  // All lessons are accessible
  router.push({
    name: 'LessonPlayer',
    params: {
      courseId: props.courseId,
      chapterId: props.chapterId,
      lessonId: lesson.lesson_id
    }
  })
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
    error.value = err.response?.data?.message || 'Fehler beim Laden des Kapitels'
  } finally {
    loading.value = false
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadChapter()
})

watch(() => props.chapterId, () => {
  loadChapter()
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
}
</style>
