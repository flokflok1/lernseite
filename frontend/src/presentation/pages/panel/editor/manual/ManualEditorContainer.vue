<template>
  <ManualEditorContainerView
    :project-id="projectId"
    :course-id="courseId"
  />
</template>

<script setup lang="ts">
import ManualEditorContainerView from '@/presentation/components/panel/editor/manual/core/ManualEditorContainerView.vue'

defineProps<{
  projectId: string
  courseId?: string | null
}>()
</script>
