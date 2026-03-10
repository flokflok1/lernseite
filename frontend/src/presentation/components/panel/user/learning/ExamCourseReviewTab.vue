<script setup lang="ts">
import { useRouter } from 'vue-router'
import ReviewDashboard from './ReviewDashboard.vue'

interface Props {
  courseId: string
}

defineProps<Props>()
const router = useRouter()

function navigateToLm(methodId: string) {
  // TODO: Route may need adjustment once LM execution routing is finalized
  // Currently using LessonPlayer which expects courseId/chapterId/lessonId params
  router.push({ name: 'LessonPlayer', params: { methodId } })
}

function navigateToChapter(chapterId: string) {
  router.push({ name: 'ChapterDetail', params: { chapterId } })
}
</script>

<template>
  <ReviewDashboard
    :course-id="courseId"
    @navigate-to-lm="navigateToLm"
    @navigate-to-chapter="navigateToChapter"
  />
</template>
