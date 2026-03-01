<template>
  <div class="courses-section">
    <div class="section-header">
      <h3 class="section-title">
        <span class="section-icon">\uD83D\uDCDA</span>
        {{ $t('dashboard.my_courses') }}
      </h3>
      <span class="course-count">{{ $t('dashboard.enrolled_count', { count: courses.length }) }}</span>
    </div>

    <div v-if="courses.length === 0" class="empty-courses">
      <span class="empty-icon">\uD83D\uDCED</span>
      <p class="empty-text">{{ $t('dashboard.no_courses') }}</p>
      <p class="empty-hint">{{ $t('dashboard.no_courses_hint') }}</p>
      <button class="cta-btn" @click="$emit('navigateCourses')">
        \uD83D\uDCDA {{ $t('dashboard.discover_courses') }}
      </button>
    </div>

    <div v-else class="courses-list">
      <div
        v-for="course in courses"
        :key="course.course_id"
        class="course-card"
      >
        <div class="course-icon">
          {{ getCourseIcon(course) }}
        </div>
        <div class="course-info">
          <h4 class="course-title">{{ course.title || course.name }}</h4>
          <p class="course-description">{{ course.description?.substring(0, 80) }}...</p>
          <div class="course-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${course.progress || 0}%` }"
              ></div>
            </div>
            <span class="progress-text">{{ course.progress || 0 }}%</span>
          </div>
        </div>
        <div class="course-xp">
          <span class="xp-badge">+{{ getQuestXp(course) }} XP</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EnrolledCourse } from '@/infrastructure/api/clients/panel/editor'

interface Props {
  courses: EnrolledCourse[]
  getCourseIcon: (course: EnrolledCourse) => string
  getQuestXp: (course: EnrolledCourse) => number
}

defineProps<Props>()

defineEmits<{
  navigateCourses: []
}>()
</script>

<style scoped>
.courses-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(
    145deg,
    var(--color-background) 0%,
    var(--color-surface) 100%
  );
  border-bottom: 1px solid var(--color-border);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.section-icon {
  font-size: 18px;
}

.course-count {
  font-size: 13px;
  color: var(--color-text-muted);
}

.empty-courses {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0 0 20px 0;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
}

.courses-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.course-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.course-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border-radius: 10px;
  font-size: 24px;
  flex-shrink: 0;
}

.course-info {
  flex: 1;
  min-width: 0;
}

.course-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.course-description {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.course-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--color-surface);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary) 0%, #818cf8 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 36px;
}

.course-xp {
  flex-shrink: 0;
}

.xp-badge {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, var(--color-background) 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #8b5cf6;
}

@media (max-width: 640px) {
  .course-card {
    flex-wrap: wrap;
  }

  .course-xp {
    width: 100%;
    margin-top: 8px;
  }
}
</style>
