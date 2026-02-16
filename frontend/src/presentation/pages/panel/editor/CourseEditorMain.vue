/**
 * CourseEditorMain.vue
 *
 * Main orchestrator component for course editing.
 * Routes between manual editor and AI editor based on user selection.
 */

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import EditorSwitcher from './EditorSwitcher.vue'
import ManualEditorContainer from './manual/ManualEditorContainer.vue'
import AIEditorContainer from './ai/AIEditorContainer.vue'

// Types
type EditorMode = 'manual' | 'ai'

// Composables
const route = useRoute()
const { t } = useI18n()

// State
const editorMode = ref<EditorMode>('manual')
const projectId = computed(() => route.params.projectId as string || '')
const courseId = computed(() => route.params.courseId as string || null)
const isLoading = ref(false)

// Methods
const switchEditor = (mode: EditorMode) => {
  editorMode.value = mode
}

const handleSave = async () => {
  isLoading.value = true
  try {
    // TODO: Implement save logic
    console.log(`Saving project ${projectId.value} from ${editorMode.value} editor`)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="course-editor-main">
    <!-- Header -->
    <div class="editor-header">
      <h1>{{ $t('courses.editor.title') }}</h1>
      <EditorSwitcher
        :current-mode="editorMode"
        @switch="switchEditor"
      />
    </div>

    <!-- Editor Container -->
    <div class="editor-container">
      <ManualEditorContainer
        v-if="editorMode === 'manual'"
        :project-id="projectId"
        :course-id="courseId"
        @save="handleSave"
      />
      <AIEditorContainer
        v-else-if="editorMode === 'ai'"
        :project-id="projectId"
        :course-id="courseId"
        @save="handleSave"
      />
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner">{{ $t('common.saving') }}</div>
    </div>
  </div>
</template>

<style scoped>
.course-editor-main {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.editor-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.editor-container {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner {
  color: white;
  font-size: 16px;
}
</style>
