<template>
  <CourseEditorView
    :course-id="courseId"
    :mode="mode"
  />
</template>

<script setup lang="ts">
import CourseEditorView from '@/presentation/components/panel/editor/shared/views/CourseEditorView.vue'

defineProps<{
  courseId?: number
  mode: 'create' | 'edit'
}>()
</script>
