<template>
  <LessonPlayerView
    :course-id="courseId"
    :chapter-id="chapterId"
    :lesson-id="lessonId"
  />
</template>

<script setup lang="ts">
import LessonPlayerView from '@/presentation/components/panel/user/learning/core/LessonPlayerView.vue'

interface Props {
  courseId: string
  chapterId: string
  lessonId: string
}

defineProps<Props>()
</script>
