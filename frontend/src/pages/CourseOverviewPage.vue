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
      <!-- Course Header -->
      <div class="course-header text-center mb-8">
        <h1 class="course-title text-3xl md:text-4xl font-extrabold mb-2">
          {{ playerStore.course.title }}
        </h1>
        <p v-if="playerStore.course.subtitle" class="course-subtitle text-lg opacity-60">
          {{ playerStore.course.subtitle }}
        </p>
      </div>

      <!-- Progress Stats Cards -->
      <div class="progress-stats grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div class="stat-card">
          <div class="stat-value">{{ completedChapters }}/{{ totalChapters }}</div>
          <div class="stat-label">{{ t('courses.chapters_completed') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ progressPercentage }}%</div>
          <div class="stat-label">{{ t('courses.overall_progress') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ averageGrade }}%</div>
          <div class="stat-label">{{ t('courses.average_grade') }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ learningTimeFormatted }}</div>
          <div class="stat-label">{{ t('courses.learning_time') }}</div>
        </div>
      </div>

      <!-- Learning Journey Mountain Map -->
      <div class="map-section relative mb-12">
        <h2 class="map-title text-xl font-bold text-center mb-4">
          {{ t('courses.your_journey') }}
        </h2>

        <div class="mountain-journey-container">
          <!-- SVG Mountain Path -->
          <svg
            class="mountain-svg"
            :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <!-- Path gradient for completed -->
              <linearGradient id="pathGradientComplete" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#34d399;stop-opacity:1" />
              </linearGradient>
              <!-- Glow filter -->
              <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
              <!-- Drop shadow for nodes -->
              <filter id="nodeShadow" x="-50%" y="-50%" width="200%" height="200%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.4"/>
              </filter>
            </defs>

            <!-- Background path (dashed gray) -->
            <path
              :d="mountainPathD"
              stroke="rgba(255,255,255,0.2)"
              stroke-width="4"
              fill="none"
              stroke-linecap="round"
              stroke-dasharray="12 8"
            />

            <!-- Completed progress path (green glow) -->
            <path
              v-if="completedChapters > 0"
              :d="mountainPathD"
              stroke="url(#pathGradientComplete)"
              stroke-width="4"
              fill="none"
              stroke-linecap="round"
              class="progress-path"
              :stroke-dasharray="totalPathLength"
              :stroke-dashoffset="remainingPathOffset"
              filter="url(#glow)"
            />

            <!-- Summit Flag -->
            <g :transform="`translate(${summitPosition.x + 20}, ${summitPosition.y - 50})`">
              <!-- Flag pole -->
              <rect x="0" y="0" width="4" height="50" fill="#d97706" rx="1"/>
              <!-- Flag -->
              <path d="M 4 2 L 30 12 L 4 22 Z" fill="#ef4444">
                <animate attributeName="d"
                  values="M 4 2 L 30 12 L 4 22 Z;M 4 2 L 28 10 L 4 20 Z;M 4 2 L 30 12 L 4 22 Z"
                  dur="2s"
                  repeatCount="indefinite"/>
              </path>
              <!-- Flag highlight -->
              <path d="M 4 2 L 18 8 L 4 14 Z" fill="#f87171" opacity="0.6"/>
            </g>
          </svg>

          <!-- Journey Nodes -->
          <div class="journey-nodes">
            <!-- Animated Character -->
            <div
              v-if="totalChapters > 0"
              class="character-container"
              :style="characterPositionStyle"
            >
              <!-- Hiker Character SVG -->
              <svg viewBox="0 0 80 100" class="hiker-character">
                <!-- Shadow -->
                <ellipse cx="40" cy="95" rx="18" ry="5" fill="rgba(0,0,0,0.3)"/>

                <!-- Legs (animated) -->
                <g class="legs">
                  <path d="M35 65 L30 85 L25 88" stroke="#374151" stroke-width="6" stroke-linecap="round" fill="none" class="leg-left"/>
                  <path d="M45 65 L52 82 L58 85" stroke="#1f2937" stroke-width="6" stroke-linecap="round" fill="none" class="leg-right"/>
                  <!-- Shoes -->
                  <ellipse cx="24" cy="89" rx="6" ry="3" fill="#92400e"/>
                  <ellipse cx="59" cy="86" rx="6" ry="3" fill="#78350f"/>
                </g>

                <!-- Body -->
                <path d="M40 35 L40 68" stroke="#f59e0b" stroke-width="16" stroke-linecap="round"/>

                <!-- Backpack -->
                <rect x="22" y="38" width="14" height="22" rx="4" fill="#3b82f6"/>
                <rect x="24" y="40" width="10" height="4" rx="1" fill="#60a5fa"/>

                <!-- Arms (animated) -->
                <g class="arms">
                  <path d="M40 42 L25 55" stroke="#fbbf24" stroke-width="5" stroke-linecap="round" fill="none" class="arm-left"/>
                  <path d="M40 42 L58 48" stroke="#f59e0b" stroke-width="5" stroke-linecap="round" fill="none" class="arm-right"/>
                </g>

                <!-- Walking stick -->
                <line x1="60" y1="45" x2="68" y2="85" stroke="#92400e" stroke-width="3" stroke-linecap="round" class="walking-stick"/>

                <!-- Head -->
                <circle cx="40" cy="22" r="16" fill="#fcd34d"/>

                <!-- Hair -->
                <path d="M26 18 Q30 8 42 10 Q54 8 52 20" fill="#78350f"/>

                <!-- Face (looking right) -->
                <circle cx="47" cy="19" r="3" fill="#1f2937"/> <!-- Eye -->
                <circle cx="48" cy="18" r="1" fill="white"/> <!-- Eye highlight -->
                <path d="M50 26 Q54 28 52 30" stroke="#1f2937" stroke-width="2" fill="none"/> <!-- Smile -->

                <!-- Cap -->
                <ellipse cx="40" cy="10" rx="14" ry="5" fill="#dc2626"/>
                <rect x="26" y="8" width="28" height="6" fill="#dc2626"/>
              </svg>
            </div>

            <!-- Chapter Nodes -->
            <div
              v-for="(chapter, index) in playerStore.chapters"
              :key="chapter.chapter_id"
              class="mountain-node"
              :class="getNodeStatusClass(index)"
              :style="getNodePositionStyle(index)"
              @click="handleNodeClick(chapter, index)"
            >
              <div class="node-outer">
                <div class="node-inner">
                  <!-- Completed checkmark -->
                  <svg v-if="isCompleted(index)" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                  <!-- Current play -->
                  <svg v-else-if="isCurrent(index)" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                  <!-- Locked -->
                  <svg v-else viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                    <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                  </svg>
                </div>
              </div>
              <span class="node-label">{{ index + 1 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Chapter Grid -->
      <div class="chapters-section mt-8">
        <h2 class="section-title text-xl font-bold mb-6 flex items-center gap-3">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-primary-500">
            <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
          </svg>
          {{ t('courses.chapters') }}
        </h2>

        <div class="chapters-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="(chapter, index) in playerStore.chapters"
            :key="chapter.chapter_id"
            class="chapter-card"
            :class="getChapterCardClass(index)"
            @click="handleChapterClick(chapter, index)"
          >
            <div class="chapter-top-bar"></div>

            <div class="chapter-header flex items-start gap-4 mb-4">
              <div class="chapter-number">{{ index + 1 }}</div>
              <div class="chapter-content flex-1">
                <div class="chapter-title text-lg font-bold">
                  {{ chapter.title }}
                </div>
              </div>
            </div>

            <div v-if="chapter.description" class="chapter-description text-sm opacity-60 leading-relaxed mb-4">
              {{ truncateDescription(chapter.description) }}
            </div>

            <div class="chapter-meta flex items-center gap-4 text-sm opacity-50">
              <span v-if="chapter.duration_minutes" class="flex items-center gap-1">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                  <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                </svg>
                {{ formatDuration(chapter.duration_minutes) }}
              </span>
              <span v-if="chapter.lessons" class="flex items-center gap-1">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                  <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
                </svg>
                {{ t('courses.lessons_count', { count: chapter.lessons.length }) }}
              </span>
            </div>

            <div class="status-badge mt-4">
              <template v-if="isCompleted(index)">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 mr-2">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                {{ t('courses.status_completed') }}
              </template>
              <template v-else-if="isCurrent(index)">
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 mr-2">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                {{ t('courses.status_in_progress') }}
              </template>
              <template v-else>
                <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 mr-2">
                  <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                </svg>
                {{ t('courses.status_locked') }}
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Course Description -->
      <div class="mt-8">
        <details class="details-card">
          <summary class="cursor-pointer font-semibold flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
            {{ t('courses.description') }}
          </summary>
          <p class="mt-4 opacity-70 whitespace-pre-line">
            {{ playerStore.course.description }}
          </p>
        </details>
      </div>

      <!-- Learning Goals -->
      <div v-if="playerStore.course.learning_goals?.length" class="mt-4">
        <details class="details-card">
          <summary class="cursor-pointer font-semibold flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            {{ t('courses.learning_goals') }}
          </summary>
          <ul class="mt-4 list-disc list-inside space-y-2 opacity-70">
            <li v-for="(goal, idx) in playerStore.course.learning_goals" :key="idx">
              {{ goal }}
            </li>
          </ul>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePlayerStore } from '@/store/player.store'
import { useTutorStore } from '@/store/tutor.store'
import type { Chapter } from '@/api/player.api'

interface Props {
  courseId: string
}

const props = defineProps<Props>()
const { t } = useI18n()
const playerStore = usePlayerStore()
const tutorStore = useTutorStore()
const router = useRouter()

// Progress Stats
const courseId = computed(() => props.courseId)
const totalChapters = computed(() => playerStore.chapters.length)

const completedChapters = computed(() => {
  if (!playerStore.courseProgress) return 0
  return playerStore.courseProgress.chapters_completed || 0
})

const progressPercentage = computed(() => {
  if (!playerStore.courseProgress) return 0
  return Math.round(playerStore.courseProgress.progress_percentage || 0)
})

const averageGrade = computed(() => 85)

const learningTimeFormatted = computed(() => {
  const minutes = playerStore.course?.total_duration_minutes || 0
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins}m`
})

// Chapter Status
const currentChapterIndex = computed(() => {
  return Math.min(completedChapters.value, totalChapters.value - 1)
})

const isCompleted = (index: number): boolean => index < completedChapters.value
const isCurrent = (index: number): boolean => index === currentChapterIndex.value
const isLocked = (index: number): boolean => index > currentChapterIndex.value

// SVG Dimensions
const svgWidth = computed(() => 900)
const svgHeight = computed(() => 250)

// Node positions - mountain climb from bottom-left to top-right
const nodePositions = computed(() => {
  const total = Math.max(totalChapters.value, 1)
  const positions: { x: number; y: number }[] = []

  const startX = 60
  const endX = svgWidth.value - 100
  const startY = svgHeight.value - 40
  const endY = 50

  for (let i = 0; i < total; i++) {
    const progress = total === 1 ? 0 : i / (total - 1)
    const x = startX + progress * (endX - startX)

    // Smooth curve up with slight wave
    const baseY = startY - progress * (startY - endY)
    const wave = Math.sin(progress * Math.PI * 2) * 20
    const y = baseY + (progress > 0 && progress < 1 ? wave : 0)

    positions.push({ x, y })
  }

  return positions
})

const summitPosition = computed(() => {
  const positions = nodePositions.value
  if (positions.length === 0) return { x: svgWidth.value - 100, y: 50 }
  return positions[positions.length - 1]
})

// SVG Path
const mountainPathD = computed(() => {
  const positions = nodePositions.value
  if (positions.length === 0) return ''
  if (positions.length === 1) return `M ${positions[0].x} ${positions[0].y}`

  let d = `M ${positions[0].x} ${positions[0].y}`

  for (let i = 1; i < positions.length; i++) {
    const prev = positions[i - 1]
    const curr = positions[i]
    const cpX = (prev.x + curr.x) / 2
    d += ` Q ${cpX} ${prev.y}, ${cpX} ${(prev.y + curr.y) / 2}`
    d += ` Q ${cpX} ${curr.y}, ${curr.x} ${curr.y}`
  }

  return d
})

const totalPathLength = computed(() => 1400)

const remainingPathOffset = computed(() => {
  if (totalChapters.value === 0) return totalPathLength.value
  const progress = completedChapters.value / totalChapters.value
  return totalPathLength.value * (1 - progress)
})

// Node Positioning
const getNodePositionStyle = (index: number) => {
  const positions = nodePositions.value
  if (index >= positions.length) return {}
  const pos = positions[index]
  return {
    left: `${(pos.x / svgWidth.value) * 100}%`,
    top: `${(pos.y / svgHeight.value) * 100}%`
  }
}

const characterPositionStyle = computed(() => {
  const positions = nodePositions.value
  const charIndex = currentChapterIndex.value
  if (charIndex >= positions.length || positions.length === 0) return { display: 'none' }

  const pos = positions[charIndex]
  return {
    left: `${(pos.x / svgWidth.value) * 100}%`,
    top: `${((pos.y - 55) / svgHeight.value) * 100}%`
  }
})

const getNodeStatusClass = (index: number): string => {
  if (isCompleted(index)) return 'completed'
  if (isCurrent(index)) return 'current'
  return 'locked'
}

const getChapterCardClass = (index: number): string => {
  if (isCompleted(index)) return 'completed'
  if (isCurrent(index)) return 'current'
  return 'locked'
}

// Methods
const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins} ${t('courses.minutes_short')}`
}

const truncateDescription = (text: string, maxLength = 120): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

const handleNodeClick = (chapter: Chapter, index: number) => {
  if (!isLocked(index)) startChapter(chapter)
}

const handleChapterClick = (chapter: Chapter, index: number) => {
  if (!isLocked(index)) startChapter(chapter)
}

const startChapter = (chapter: Chapter) => {
  // Navigate to chapter detail page (with theory + lessons tabs)
  router.push({
    name: 'ChapterDetail',
    params: {
      courseId: courseId.value,
      chapterId: chapter.chapter_id
    }
  })
}

onMounted(async () => {
  await playerStore.loadCourse(courseId.value)

  // Update tutor context with course info
  tutorStore.updateContext({
    page: 'course',
    courseId: playerStore.course?.course_id || courseId.value,
    courseName: playerStore.course?.title || null,
    chapterId: null,
    chapterName: null,
    lessonId: null,
    lessonName: null,
    methodId: null,
    methodType: null
  })
})

onUnmounted(() => {
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
})
</script>

<style scoped>
/* Title Gradient */
.course-title {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.course-subtitle {
  color: var(--color-text-secondary);
}

/* Stat Cards */
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: var(--color-surface-hover);
  transform: translateY(-2px);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Map Section */
.map-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  padding: 1.5rem;
}

.map-title {
  color: var(--color-text-primary);
}

/* Mountain Container */
.mountain-journey-container {
  position: relative;
  width: 100%;
  height: 300px;
  margin-top: 1rem;
}

.mountain-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.progress-path {
  transition: stroke-dashoffset 1s ease-out;
}

/* Journey Nodes Container */
.journey-nodes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* Mountain Node */
.mountain-node {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 10;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mountain-node:hover:not(.locked) {
  transform: translate(-50%, -50%) scale(1.15);
}

.node-outer {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.node-inner {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.node-icon {
  width: 24px;
  height: 24px;
}

.node-label {
  margin-top: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-secondary);
  background: rgba(0, 0, 0, 0.4);
  padding: 2px 10px;
  border-radius: 10px;
}

/* Completed Node */
.mountain-node.completed .node-outer {
  background: rgba(16, 185, 129, 0.2);
}

.mountain-node.completed .node-inner {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

/* Current Node */
.mountain-node.current .node-outer {
  background: rgba(245, 158, 11, 0.3);
  animation: pulse-outer 2s infinite;
}

.mountain-node.current .node-inner {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  animation: pulse-inner 2s infinite;
}

@keyframes pulse-outer {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.2); opacity: 0.5; }
}

@keyframes pulse-inner {
  0%, 100% { box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4); }
  50% { box-shadow: 0 4px 35px rgba(245, 158, 11, 0.8); }
}

/* Locked Node */
.mountain-node.locked .node-outer {
  background: rgba(100, 100, 120, 0.1);
}

.mountain-node.locked .node-inner {
  background: rgba(60, 60, 80, 0.6);
  color: rgba(255, 255, 255, 0.4);
}

.mountain-node.locked {
  cursor: not-allowed;
}

/* Character */
.character-container {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 20;
  pointer-events: none;
}

.hiker-character {
  width: 70px;
  height: 88px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
  animation: hiker-bounce 1s ease-in-out infinite;
}

@keyframes hiker-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

/* Walking animations */
.leg-left {
  animation: leg-left-swing 0.6s ease-in-out infinite;
  transform-origin: 35px 65px;
}

.leg-right {
  animation: leg-right-swing 0.6s ease-in-out infinite;
  transform-origin: 45px 65px;
}

.arm-left {
  animation: arm-left-swing 0.6s ease-in-out infinite;
  transform-origin: 40px 42px;
}

.arm-right {
  animation: arm-right-swing 0.6s ease-in-out infinite;
  transform-origin: 40px 42px;
}

.walking-stick {
  animation: stick-swing 0.6s ease-in-out infinite;
  transform-origin: 60px 45px;
}

@keyframes leg-left-swing {
  0%, 100% { transform: rotate(-8deg); }
  50% { transform: rotate(8deg); }
}

@keyframes leg-right-swing {
  0%, 100% { transform: rotate(8deg); }
  50% { transform: rotate(-8deg); }
}

@keyframes arm-left-swing {
  0%, 100% { transform: rotate(5deg); }
  50% { transform: rotate(-5deg); }
}

@keyframes arm-right-swing {
  0%, 100% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
}

@keyframes stick-swing {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}

/* Section Title */
.section-title {
  color: var(--color-text-primary);
}

/* Chapter Cards */
.chapter-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.chapter-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--color-border);
}

.chapter-card.completed {
  border-color: rgba(16, 185, 129, 0.3);
}

.chapter-card.completed .chapter-top-bar {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.chapter-card.completed:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(16, 185, 129, 0.2);
}

.chapter-card.current {
  border-color: rgba(245, 158, 11, 0.4);
  animation: card-pulse 2s infinite;
}

.chapter-card.current .chapter-top-bar {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

.chapter-card.current:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.2);
}

@keyframes card-pulse {
  0%, 100% { border-color: rgba(245, 158, 11, 0.4); }
  50% { border-color: rgba(245, 158, 11, 0.7); }
}

.chapter-card.locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.chapter-card.locked:hover {
  transform: none;
}

.chapter-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-surface-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.chapter-card.completed .chapter-number {
  background: #10b981;
  color: white;
}

.chapter-card.current .chapter-number {
  background: #f59e0b;
  color: white;
}

.chapter-title {
  color: var(--color-text-primary);
}

.chapter-description {
  color: var(--color-text-secondary);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chapter-card.completed .status-badge {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.chapter-card.current .status-badge {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.chapter-card.locked .status-badge {
  background: var(--color-surface-secondary);
  color: var(--color-text-tertiary);
}

/* Details Card */
.details-card {
  background: var(--color-surface);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  padding: 1rem 1.25rem;
  color: var(--color-text-primary);
}

.details-card summary {
  list-style: none;
}

.details-card summary::-webkit-details-marker {
  display: none;
}

.details-card[open] summary {
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .mountain-journey-container {
    height: 220px;
  }

  .node-outer {
    width: 44px;
    height: 44px;
  }

  .node-inner {
    width: 38px;
    height: 38px;
  }

  .node-icon {
    width: 18px;
    height: 18px;
  }

  .hiker-character {
    width: 50px;
    height: 63px;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}
</style>
