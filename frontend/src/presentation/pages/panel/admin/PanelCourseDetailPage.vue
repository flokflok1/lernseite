<template>
  <CourseDetailView :id="id" />
</template>

<script setup lang="ts">
import CourseDetailView from '@/presentation/components/panel/admin/courses/core/CourseDetailView.vue'

interface Props {
  id: string | number
}

defineProps<Props>()
</script>
