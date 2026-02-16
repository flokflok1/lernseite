<template>
  <div class="lesson-player-panel p-6">
    <div class="max-w-4xl mx-auto">
      <!-- Section Header -->
      <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
          {{ $t('chapter.lessons_in_chapter') }}
        </h2>
        <p v-if="lessons.length > 0" class="text-sm text-gray-600 dark:text-gray-400">
          {{ $t('chapter.completedLessons', { completed: completedLessons, total: lessons.length }) }}
        </p>
      </div>

      <!-- No Lessons State -->
      <div v-if="lessons.length === 0" class="text-center py-16">
        <div class="mb-4">
          <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-gray-600 dark:text-gray-400">{{ $t('common.noData') }}</p>
      </div>

      <!-- Lessons List -->
      <div v-else class="space-y-3">
        <div
          v-for="(lesson, index) in lessons"
          :key="lesson.lesson_id"
          :class="[
            'lesson-card group relative p-4 rounded-lg border-2 transition-all cursor-pointer',
            getLessonCardClasses(lesson, index)
          ]"
          @click="handleLessonClick(lesson, index)"
        >
          <!-- Lesson Content -->
          <div class="flex items-center gap-4">
            <!-- Lesson Number/Status Icon -->
            <div class="flex-shrink-0">
              <div
                :class="[
                  'w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg',
                  getLessonIconClasses(lesson, index)
                ]"
              >
                <!-- Completed Icon -->
                <svg
                  v-if="isLessonCompleted(lesson)"
                  class="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <!-- Locked Icon -->
                <svg
                  v-else-if="isLessonLocked(lesson, index)"
                  class="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <!-- Lesson Number -->
                <span v-else>{{ index + 1 }}</span>
              </div>
            </div>

            <!-- Lesson Info -->
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 dark:text-white truncate">
                {{ lesson.title }}
              </h3>
              <div class="flex items-center gap-3 mt-1 text-sm text-gray-600 dark:text-gray-400">
                <!-- Lesson Type Badge -->
                <span class="inline-flex items-center gap-1">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                  {{ getLessonTypeLabel(lesson.lesson_type) }}
                </span>

                <!-- Progress (if in progress) -->
                <span
                  v-if="getLessonProgress(lesson) > 0 && !isLessonCompleted(lesson)"
                  class="text-blue-600 dark:text-blue-400"
                >
                  {{ getLessonProgress(lesson) }}%
                </span>
              </div>
            </div>

            <!-- Arrow Icon (available lessons only) -->
            <div
              v-if="!isLessonLocked(lesson, index)"
              class="flex-shrink-0 transform transition-transform group-hover:translate-x-1"
            >
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>

          <!-- Lock Overlay (for locked lessons) -->
          <div
            v-if="isLessonLocked(lesson, index)"
            class="absolute inset-0 bg-gray-900/5 dark:bg-gray-100/5 rounded-lg flex items-center justify-center"
          >
            <span class="text-sm text-gray-500 dark:text-gray-500 font-medium">
              {{ $t('courses.status_locked') }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * LessonPlayerPanel Component
 * ===========================
 * Displays lessons list with status indicators
 */
import { useI18n } from 'vue-i18n'

interface Props {
  lessons: any[]
  lessonProgress: Record<string, any>
  completedLessons: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'lesson-select': [lesson: any, index: number]
}>()

const { t } = useI18n()

/**
 * Check if lesson is completed
 */
function isLessonCompleted(lesson: any): boolean {
  const prog = props.lessonProgress[lesson.lesson_id]
  return prog?.completed === true || prog?.progress_percentage === 100
}

/**
 * Check if lesson is locked
 */
function isLessonLocked(lesson: any, index: number): boolean {
  if (index === 0) return false
  const prevLesson = props.lessons[index - 1]
  return !isLessonCompleted(prevLesson)
}

/**
 * Get lesson progress percentage
 */
function getLessonProgress(lesson: any): number {
  const prog = props.lessonProgress[lesson.lesson_id]
  return prog?.progress_percentage || 0
}

/**
 * Get lesson card classes based on status
 */
function getLessonCardClasses(lesson: any, index: number): string {
  if (isLessonCompleted(lesson)) {
    return 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/10 hover:border-green-300 dark:hover:border-green-700'
  }
  if (isLessonLocked(lesson, index)) {
    return 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 cursor-not-allowed opacity-60'
  }
  return 'border-blue-200 dark:border-blue-800 bg-white dark:bg-gray-800 hover:border-blue-400 dark:hover:border-blue-600 hover:shadow-md'
}

/**
 * Get lesson icon container classes
 */
function getLessonIconClasses(lesson: any, index: number): string {
  if (isLessonCompleted(lesson)) {
    return 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
  }
  if (isLessonLocked(lesson, index)) {
    return 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
  }
  return 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
}

/**
 * Get lesson type label
 */
function getLessonTypeLabel(type: string): string {
  return t(`lesson.type_${type}`) || type
}

/**
 * Handle lesson click
 */
function handleLessonClick(lesson: any, index: number) {
  if (isLessonLocked(lesson, index)) return
  emit('lesson-select', lesson, index)
}
</script>

<style scoped>
.lesson-card {
  animation: fadeInUp 0.3s ease-out backwards;
}

.lesson-card:nth-child(1) { animation-delay: 0.05s; }
.lesson-card:nth-child(2) { animation-delay: 0.1s; }
.lesson-card:nth-child(3) { animation-delay: 0.15s; }
.lesson-card:nth-child(4) { animation-delay: 0.2s; }
.lesson-card:nth-child(5) { animation-delay: 0.25s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
