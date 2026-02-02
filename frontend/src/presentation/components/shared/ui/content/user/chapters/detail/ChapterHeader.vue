<template>
  <div class="chapter-header bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
    <div class="max-w-7xl mx-auto">
      <!-- Back Button Row -->
      <div class="mb-4">
        <button
          @click="$emit('back')"
          class="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ $t('chapter.backToCourse') }}
        </button>
      </div>

      <!-- Title and Progress Row -->
      <div class="flex items-start justify-between gap-4">
        <!-- Title Section -->
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-2 truncate">
            {{ chapter?.title || $t('chapter.loading') }}
          </h1>
          <p v-if="courseName" class="text-sm text-gray-600 dark:text-gray-400">
            {{ courseName }}
          </p>
        </div>

        <!-- Progress Badge -->
        <div v-if="progress !== null" class="flex-shrink-0">
          <div
            :class="[
              'px-4 py-2 rounded-lg font-semibold text-sm transition-colors',
              progress === 100
                ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                : 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
            ]"
          >
            <div class="flex items-center gap-2">
              <!-- Checkmark Icon (completed) -->
              <svg
                v-if="progress === 100"
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <!-- Progress Text -->
              <span>{{ progress }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Chapter Description (if available) -->
      <div v-if="chapter?.description" class="mt-4">
        <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
          {{ chapter.description }}
        </p>
      </div>

      <!-- Chapter Meta Info -->
      <div v-if="chapter" class="mt-4 flex flex-wrap items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
        <!-- Lesson Count -->
        <div v-if="lessonCount > 0" class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span>{{ $t('chapter.lessonsCount', { count: lessonCount }) }}</span>
        </div>

        <!-- Completed Lessons -->
        <div v-if="completedLessons !== null && lessonCount > 0" class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ $t('chapter.completedLessons', { completed: completedLessons, total: lessonCount }) }}</span>
        </div>

        <!-- Chapter Order -->
        <div v-if="chapter.order_index !== undefined" class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
          </svg>
          <span>{{ $t('chapter.chapterNumber', { number: chapter.order_index + 1 }) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ChapterHeader Component
 * ======================
 * Displays chapter header with navigation, title, and progress
 */

interface Props {
  chapter: any | null
  courseName: string
  progress: number | null
  lessonCount?: number
  completedLessons?: number | null
}

withDefaults(defineProps<Props>(), {
  lessonCount: 0,
  completedLessons: null
})

defineEmits<{
  back: []
}>()
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
