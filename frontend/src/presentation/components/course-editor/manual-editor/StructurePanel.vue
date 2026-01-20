/**
 * StructurePanel.vue - Course structure browser (chapters/lessons)
 */

<script setup lang="ts">
interface Props {
  selectedChapter: string | null
  selectedLesson: string | null
}

interface Emits {
  (e: 'select', type: 'chapter' | 'lesson', id: string): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<template>
  <div class="structure-panel">
    <div class="panel-header">{{ $t('courses.editor.structure') }}</div>
    <!-- TODO: Render chapters and lessons -->
    <p class="placeholder">Structure panel content</p>
  </div>
</template>

<style scoped>
.structure-panel {
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
