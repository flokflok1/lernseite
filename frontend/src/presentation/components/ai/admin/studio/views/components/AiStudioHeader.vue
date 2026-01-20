<!--
  AiStudioHeader - Header with logo, course selector, and stats
-->

<template>
  <div class="ai-studio-header">
    <!-- Logo & Title -->
    <div class="header-left">
      <div class="logo">
        <svg class="logo-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </div>
      <div class="title-area">
        <h2 class="title">{{ $t('admin.aiStudio.title') }}</h2>
        <p class="subtitle">{{ selectedCourseTitle || $t('admin.aiStudio.selectCourse') }}</p>
      </div>
    </div>

    <!-- Actions -->
    <div class="header-right">
      <!-- Course Selector -->
      <CourseSelector
        :courses="courses"
        :selected-course-id="selectedCourseId"
        @select="$emit('select-course', $event)"
        @create="$emit('create-course')"
      />

      <!-- Quick Stats -->
      <div class="stats">
        <span class="stats-label">{{ $t('admin.aiStudio.lessons') }}:</span>
        <span class="stats-value">{{ stats.totalLessons }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AiStudioHeader - Top header with branding and course selection
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CourseSelector from './CourseSelector.vue'
import type { Course } from '../composables/useAiStudioState'

const { t } = useI18n()

// =============================================================================
// Props
// =============================================================================

interface Stats {
  totalLessons: number
  videosGenerated?: number
  tokensUsed?: number
  costToday?: number
}

interface Props {
  courses: Course[]
  selectedCourseId: string | null
  stats: Stats
}

const props = defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

defineEmits<{
  (e: 'select-course', courseId: string): void
  (e: 'create-course'): void
}>()

// =============================================================================
// Computed
// =============================================================================

const selectedCourseTitle = computed(() => {
  if (!props.selectedCourseId) return ''
  const course = props.courses.find(c => c.course_id === props.selectedCourseId)
  return course?.title || ''
})
</script>

<style scoped>
.ai-studio-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: linear-gradient(to right, #8b5cf6, #a855f7);
  border-bottom: 1px solid var(--color-border);
}

/* Left Side */
.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: white;
}

.title-area {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.title {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.subtitle {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* Right Side */
.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
}

.stats-label {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
}

.stats-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: white;
}
</style>
