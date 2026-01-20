/**
 * ContentEditor.vue - Main content editing area
 */

<script setup lang="ts">
interface Props {
  chapterId: string | null
  lessonId: string | null
}

interface Emits {
  (e: 'change'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<template>
  <div class="content-editor">
    <div class="editor-header">{{ $t('courses.editor.content') }}</div>
    <!-- TODO: Content editor -->
    <p class="placeholder">Content editor</p>
  </div>
</template>

<style scoped>
.content-editor {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-header {
  padding: 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
  font-size: 14px;
}

.placeholder {
  padding: 16px;
  color: #999;
  text-align: center;
}
</style>
