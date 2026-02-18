/**
 * ContentEditor.vue - Main content editing area
 *
 * Shared component for both ManualEditor and AIEditor.
 * Provides rich text editing capabilities for course content.
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
    <!-- TODO: Rich text editor integration (TipTap, CodeMirror, etc.) -->
    <p class="placeholder">Rich text editor placeholder</p>
  </div>
</template>

<style scoped>
.content-editor {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex: 1;
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
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
