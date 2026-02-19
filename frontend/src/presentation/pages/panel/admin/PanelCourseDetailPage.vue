<template>
  <CourseDetailView :id="id" />
</template>

<script setup lang="ts">
import CourseDetailView from '@/presentation/components/panel/admin/courses/CourseDetailView.vue'

interface Props {
  id: string | number
}

defineProps<Props>()
</script>
