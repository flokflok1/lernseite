/**
 * ManualEditorContainer.vue
 *
 * Main container for manual course editing.
 * Manages layout and coordination of manual editor components.
 */

<script setup lang="ts">
import { ref, computed } from 'vue'
import StructurePanel from './StructurePanel.vue'
import ContentEditor from './ContentEditor.vue'
import PreviewPanel from './PreviewPanel.vue'
import ToolbarActions from './ToolbarActions.vue'

interface Props {
  projectId: string
}

interface Emits {
  (e: 'save'): void
}

defineProps<Props>()
defineEmits<Emits>()

const selectedChapterId = ref<string | null>(null)
const selectedLessonId = ref<string | null>(null)
const isDirty = ref(false)

const handleStructureSelect = (type: 'chapter' | 'lesson', id: string) => {
  if (type === 'chapter') {
    selectedChapterId.value = id
    selectedLessonId.value = null
  } else {
    selectedLessonId.value = id
  }
}

const handleContentChange = () => {
  isDirty.value = true
}
</script>

<template>
  <div class="manual-editor-container">
    <!-- Toolbar -->
    <ToolbarActions
      :is-dirty="isDirty"
      @save="$emit('save')"
    />

    <!-- Editor Layout -->
    <div class="editor-layout">
      <!-- Structure Panel (Left) -->
      <StructurePanel
        :selected-chapter="selectedChapterId"
        :selected-lesson="selectedLessonId"
        @select="handleStructureSelect"
      />

      <!-- Content Editor (Center) -->
      <ContentEditor
        :chapter-id="selectedChapterId"
        :lesson-id="selectedLessonId"
        @change="handleContentChange"
      />

      <!-- Preview Panel (Right) -->
      <PreviewPanel
        :chapter-id="selectedChapterId"
        :lesson-id="selectedLessonId"
      />
    </div>
  </div>
</template>

<style scoped>
.manual-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 10px;
}

.editor-layout {
  display: grid;
  grid-template-columns: 250px 1fr 300px;
  gap: 10px;
  flex: 1;
  overflow: hidden;
}

@media (max-width: 1400px) {
  .editor-layout {
    grid-template-columns: 200px 1fr;
  }

  .preview-panel {
    display: none;
  }
}

@media (max-width: 900px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }

  .structure-panel,
  .preview-panel {
    display: none;
  }
}
</style>
