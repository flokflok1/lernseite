<script setup lang="ts">
import ReviewDashboard from './ReviewDashboard.vue'

interface Props {
  courseId: string
}

defineProps<Props>()

const emit = defineEmits<{
  'navigate-to-lm': [methodId: string]
  'navigate-to-chapter': [chapterId: string]
}>()
</script>

<template>
  <ReviewDashboard
    :course-id="courseId"
    @navigate-to-lm="emit('navigate-to-lm', $event)"
    @navigate-to-chapter="emit('navigate-to-chapter', $event)"
  />
</template>
