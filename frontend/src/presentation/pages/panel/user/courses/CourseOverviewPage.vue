<template>
  <CourseOverviewView :course-id="courseId" />
</template>

<script setup lang="ts">
import CourseOverviewView from '@/presentation/components/panel/user/courses/CourseOverviewView.vue'

interface Props {
  courseId: string
}

defineProps<Props>()
</script>
