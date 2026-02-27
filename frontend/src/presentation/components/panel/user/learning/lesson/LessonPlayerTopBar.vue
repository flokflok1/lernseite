<!--
  LessonPlayerTopBar - Hero-style navigation bar for the lesson player

  Shows animated gradient background, lesson info, progress bar, and completion controls.
  Design mirrors ChapterHero for visual consistency.
-->

<template>
  <div class="lesson-hero">
    <!-- Animated gradient background -->
    <div class="hero-gradient"></div>
    <!-- Floating orbs -->
    <div class="hero-orb hero-orb--1"></div>
    <div class="hero-orb hero-orb--2"></div>
    <div class="hero-orb hero-orb--3"></div>

    <div class="hero-content">
      <!-- Top row: back button + completion -->
      <div class="hero-top">
        <button class="back-btn" @click="$emit('back')">
          <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ $t('chapter.backToCourse') }}
        </button>

        <div class="hero-top-right">
          <Button
            v-if="!isCompleted"
            variant="primary"
            size="sm"
            class="complete-btn"
            @click="$emit('complete')"
          >
            {{ $t('lesson.mark_completed') }}
          </Button>
          <span v-else class="completed-badge">
            <svg class="badge-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
            </svg>
            {{ $t('lesson.completed') }}
          </span>
        </div>
      </div>

      <!-- Main info: single compact row -->
      <div class="hero-main">
        <div class="hero-info">
          <p class="hero-breadcrumb">{{ courseTitle }} · {{ chapterTitle }}</p>
          <div class="hero-title-row">
            <h1 class="hero-lesson-title">{{ lessonTitle || '' }}</h1>
            <div class="hero-meta">
              <span v-if="lessonType" class="meta-chip">{{ lessonTypeEmoji }} {{ lessonTypeLabel }}</span>
              <span v-if="lessonPosition" class="meta-chip">{{ $t('lesson.lesson_count', lessonPosition) }}</span>
              <span v-if="durationMinutes" class="meta-chip">{{ durationMinutes }} min</span>
            </div>
          </div>
        </div>

        <!-- Progress -->
        <div v-if="progressPercentage != null" class="hero-progress">
          <div class="progress-label">{{ Math.round(progressPercentage) }}%</div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${progressPercentage}%` }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/presentation/components/shared/ui/Button.vue'

interface Props {
  courseTitle: string
  chapterTitle: string
  progressPercentage: number | null
  isCompleted: boolean
  lessonTitle?: string
  lessonType?: string
  lessonPosition?: { current: number; total: number }
  durationMinutes?: number
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'back'): void
  (e: 'complete'): void
}>()

const { t } = useI18n()

const lessonTypeEmoji = computed(() => {
  const map: Record<string, string> = {
    text: '📝', video: '🎬', quiz: '❓', ai: '🤖', interactive: '🎮', mixed: '🔀'
  }
  return map[props.lessonType || ''] || '📄'
})

const lessonTypeLabel = computed(() => {
  if (!props.lessonType) return ''
  return t(`lesson.type_${props.lessonType}`)
})
</script>

<style scoped>
.lesson-hero {
  position: relative;
  overflow: hidden;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1e40af 0%, #4338ca 25%, #6d28d9 50%, #4338ca 75%, #1e40af 100%);
  background-size: 300% 300%;
  animation: gradientShift 8s ease-in-out infinite;
}

:root.dark .hero-gradient {
  background: linear-gradient(135deg, #1e3a5f 0%, #312e81 25%, #4c1d95 50%, #312e81 75%, #1e3a5f 100%);
  background-size: 300% 300%;
  animation: gradientShift 8s ease-in-out infinite;
}

@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Floating orbs */
.hero-orb {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.hero-orb--1 {
  top: -1.5rem;
  right: 15%;
  width: 10rem;
  height: 10rem;
  background: rgba(255, 255, 255, 0.06);
  filter: blur(48px);
  animation: floatOrb 6s ease-in-out infinite;
}

.hero-orb--2 {
  top: 0.5rem;
  right: 40%;
  width: 7rem;
  height: 7rem;
  background: rgba(103, 232, 249, 0.05);
  filter: blur(32px);
  animation: floatOrb 7s ease-in-out 2s infinite;
}

.hero-orb--3 {
  bottom: -1rem;
  left: 10%;
  width: 12rem;
  height: 12rem;
  background: rgba(167, 139, 250, 0.07);
  filter: blur(48px);
  animation: floatOrb 9s ease-in-out 1s infinite;
}

@keyframes floatOrb {
  0%, 100% { transform: translateY(0) scale(1); }
  50%      { transform: translateY(-8px) scale(1.03); }
}

/* Content */
.hero-content {
  position: relative;
  max-width: 80rem;
  margin: 0 auto;
  padding: 0.5rem 1.25rem 0.5rem;
}

.hero-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: rgba(191, 219, 254, 0.9);
  transition: color 0.2s;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.back-btn:hover {
  color: #ffffff;
}

.back-icon {
  width: 0.875rem;
  height: 0.875rem;
  transition: transform 0.2s;
}

.back-btn:hover .back-icon {
  transform: translateX(-2px);
}

.hero-top-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.complete-btn {
  background-color: rgba(255, 255, 255, 0.95) !important;
  color: #1e40af !important;
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.complete-btn:hover {
  background-color: #ffffff !important;
  transform: scale(1.02);
}

.completed-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  background-color: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(52, 211, 153, 0.3);
  border-radius: 0.5rem;
  color: #6ee7b7;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-icon {
  width: 0.875rem;
  height: 0.875rem;
}

/* Main row */
.hero-main {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.5rem;
}

.hero-info {
  flex: 1;
  min-width: 0;
}

.hero-breadcrumb {
  font-size: 0.6875rem;
  color: rgba(191, 219, 254, 0.7);
  font-weight: 500;
  margin: 0 0 0.125rem;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hero-lesson-title {
  font-size: 1.125rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 500;
  background-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Progress */
.hero-progress {
  flex-shrink: 0;
  width: 10rem;
  text-align: right;
}

.progress-label {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.25rem;
}

.progress-track {
  height: 0.375rem;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #34d399, #10b981);
  border-radius: 9999px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
