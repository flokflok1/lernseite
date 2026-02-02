/**
 * StructurePanel.vue - Course structure browser (chapters/lessons)
 *
 * Shared component for both ManualEditor and AIEditor.
 * Displays hierarchical course structure for navigation and selection.
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
    <div class="structure-content">
      <!-- TODO: Render chapters and lessons in tree structure -->
      <p class="placeholder">{{ $t('courses.editor.selectCourse') }}</p>
    </div>
  </div>
</template>

<style scoped>
.structure-panel {
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

.structure-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.placeholder {
  margin: 0;
  padding: 16px;
  color: #999;
  text-align: center;
  font-size: 12px;
}
</style>
