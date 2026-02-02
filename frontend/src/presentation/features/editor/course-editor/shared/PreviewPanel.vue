/**
 * PreviewPanel.vue - Live preview of content
 *
 * Shared component for both ManualEditor and AIEditor.
 * Displays real-time preview of course content as it will appear to users.
 */

<script setup lang="ts">
interface Props {
  chapterId: string | null
  lessonId: string | null
  content?: string
}

defineProps<Props>()
</script>

<template>
  <div class="preview-panel">
    <div class="panel-header">{{ $t('courses.editor.preview') }}</div>
    <div class="preview-content">
      <!-- TODO: Render preview based on content prop -->
      <p class="placeholder">{{ $t('courses.editor.selectContent') }}</p>
    </div>
  </div>
</template>

<style scoped>
.preview-panel {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.panel-header {
  padding: 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
  font-size: 14px;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.placeholder {
  margin: 0;
  color: #999;
  text-align: center;
  font-size: 12px;
}
</style>
