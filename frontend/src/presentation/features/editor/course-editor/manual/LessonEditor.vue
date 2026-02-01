/**
 * LessonEditor.vue - Lesson-level editing
 */

<script setup lang="ts">
interface Props {
  lessonId: string
}

defineProps<Props>()
</script>

<template>
  <div class="lesson-editor">Lesson Editor</div>
</template>

<style scoped>
.lesson-editor {
  padding: 16px;
}
</style>
