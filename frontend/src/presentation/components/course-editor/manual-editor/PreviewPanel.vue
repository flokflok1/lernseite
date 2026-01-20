/**
 * PreviewPanel.vue - Live preview of content
 */

<script setup lang="ts">
interface Props {
  chapterId: string | null
  lessonId: string | null
}

defineProps<Props>()
</script>

<template>
  <div class="preview-panel">
    <div class="panel-header">{{ $t('courses.editor.preview') }}</div>
    <!-- TODO: Preview content -->
    <p class="placeholder">Preview panel</p>
  </div>
</template>

<style scoped>
.preview-panel {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
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
  font-size: 12px;
}
</style>
