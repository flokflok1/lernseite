<template>
  <div class="course-overview-header">
    <!-- Course Title -->
    <div class="course-header text-center mb-8">
      <h1 class="course-title text-3xl md:text-4xl font-extrabold mb-2">
        {{ courseTitle }}
      </h1>
      <p v-if="courseSubtitle" class="course-subtitle text-lg opacity-60">
        {{ courseSubtitle }}
      </p>
    </div>

    <!-- Progress Stats Cards -->
    <div class="progress-stats grid grid-cols-2 md:grid-cols-4 gap-4">
      <!-- Completed Chapters -->
      <div class="stat-card">
        <div class="stat-value">{{ completedChapters }}/{{ totalChapters }}</div>
        <div class="stat-label">{{ $t('courses.chapters_completed') }}</div>
      </div>

      <!-- Overall Progress -->
      <div class="stat-card">
        <div class="stat-value">{{ progressPercentage }}%</div>
        <div class="stat-label">{{ $t('courses.overall_progress') }}</div>
      </div>

      <!-- Average Grade -->
      <div class="stat-card">
        <div class="stat-value">{{ averageGrade }}%</div>
        <div class="stat-label">{{ $t('courses.average_grade') }}</div>
      </div>

      <!-- Learning Time -->
      <div class="stat-card">
        <div class="stat-value">{{ learningTime }}</div>
        <div class="stat-label">{{ $t('courses.learning_time') }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseOverviewHeader Component
 * ===============================
 * Course title and progress stats display
 */

interface Props {
  courseTitle: string
  courseSubtitle?: string | null
  completedChapters: number
  totalChapters: number
  progressPercentage: number
  averageGrade: number
  learningTime: string
}

defineProps<Props>()
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
</style>
