/**
 * ChapterEditor.vue - Chapter-level editing
 */

<script setup lang="ts">
interface Props {
  chapterId: string
}

defineProps<Props>()
</script>

<template>
  <div class="chapter-editor">Chapter Editor</div>
</template>

<style scoped>
.chapter-editor {
  padding: 16px;
}
</style>
