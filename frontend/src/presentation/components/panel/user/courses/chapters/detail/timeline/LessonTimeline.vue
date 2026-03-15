<template>
  <div class="lesson-timeline px-6 pt-4 pb-4">
    <div class="max-w-5xl mx-auto">
      <!-- Section Header -->
      <div class="mb-3">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
          {{ $t('chapter.learningPath') }}
          <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
            {{ $t('chapter.completedLessons', { completed: completedLessons, total: lessons.length }) }}
          </span>
        </h2>
      </div>

      <!-- No Lessons State -->
      <div v-if="lessons.length === 0" class="text-center py-10">
        <div class="mb-4">
          <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-gray-600 dark:text-gray-400">{{ $t('common.noData') }}</p>
      </div>

      <!-- Timeline -->
      <div v-else class="timeline-list">
        <LessonTimelineNode
          v-for="(lesson, index) in lessons"
          :key="lesson.lesson_id"
          :lesson="lesson"
          :index="index"
          :total="lessons.length"
          :status="getStatus(lesson, index)"
          :progress="getLessonProgress(lesson)"
          :is-last="index === lessons.length - 1"
          @select="(l, i) => emit('lesson-select', l, i)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LessonTimelineNode from './LessonTimelineNode.vue'

interface Props {
  lessons: any[]
  lessonProgress: Record<string, any>
  completedLessons: number
  sequential?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  sequential: true
})

const emit = defineEmits<{
  'lesson-select': [lesson: any, index: number]
}>()

function isLessonCompleted(lesson: any): boolean {
  const prog = props.lessonProgress[lesson.lesson_id]
  return prog?.completed === true || prog?.progress_percentage === 100
}

function isLessonLocked(lesson: any, index: number): boolean {
  if (!props.sequential) return false
  if (index === 0) return false
  const prevLesson = props.lessons[index - 1]
  return !isLessonCompleted(prevLesson)
}

function getStatus(lesson: any, index: number): 'completed' | 'current' | 'available' | 'locked' {
  if (isLessonCompleted(lesson)) return 'completed'
  if (isLessonLocked(lesson, index)) return 'locked'

  // When not sequential, only the first incomplete lesson is "current" (recommended)
  if (!props.sequential) {
    const firstIncompleteIdx = props.lessons.findIndex(l => !isLessonCompleted(l))
    if (index === firstIncompleteIdx) return 'current'
    return 'available'
  }

  return 'current'
}

function getLessonProgress(lesson: any): number {
  const prog = props.lessonProgress[lesson.lesson_id]
  return prog?.progress_percentage || 0
}
</script>
