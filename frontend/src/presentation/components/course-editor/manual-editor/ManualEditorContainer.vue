/**
 * ManualEditorContainer.vue
 *
 * Main container for manual course editing.
 * Manages layout and coordination of manual editor components.
 * Includes theory and explanation generation integration.
 */

<script setup lang="ts">
import { ref, computed } from 'vue'
import { StructurePanel, ContentEditor, PreviewPanel, ToolbarActions } from '../shared'
import { TheoryGenerationContainer } from '../content-generation'
import { ExplanationGenerationContainer } from '../explanation-generation'

interface Props {
  projectId: string
  courseId?: string | null
}

interface Emits {
  (e: 'save'): void
}

defineProps<Props>()
defineEmits<Emits>()

const selectedChapterId = ref<string | null>(null)
const selectedLessonId = ref<string | null>(null)
const isDirty = ref(false)
const activeTab = ref<'content' | 'theory' | 'explanation'>('content')

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

const handleTheoryGenerated = () => {
  isDirty.value = true
  $emit('save')
}

const handleExplanationGenerated = () => {
  isDirty.value = true
  $emit('save')
}
</script>

<template>
  <div class="manual-editor-container">
    <!-- Toolbar -->
    <ToolbarActions
      :is-dirty="isDirty"
      @save="$emit('save')"
    />

    <!-- Tab Navigation -->
    <div class="editor-tabs">
      <button
        :class="['tab-btn', { active: activeTab === 'content' }]"
        @click="activeTab = 'content'"
      >
        ✏️ {{ $t('courses.editor.content') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'theory' }]"
        @click="activeTab = 'theory'"
      >
        📚 {{ $t('course-editor.theory.container.title') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'explanation' }]"
        @click="activeTab = 'explanation'"
      >
        💡 {{ $t('course-editor.explanation.container.title') }}
      </button>
    </div>

    <!-- Content Tab -->
    <div v-if="activeTab === 'content'" class="editor-layout">
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

    <!-- Theory Tab -->
    <div v-else-if="activeTab === 'theory'" class="theory-content">
      <TheoryGenerationContainer
        :chapter="selectedChapterId ? { chapter_id: selectedChapterId } : null"
        :course="courseId ? { course_id: courseId } : null"
        @generated="handleTheoryGenerated"
        @deleted="handleTheoryGenerated"
      />
    </div>

    <!-- Explanation Tab -->
    <div v-else-if="activeTab === 'explanation'" class="explanation-content">
      <ExplanationGenerationContainer
        :lesson="selectedLessonId ? { lesson_id: selectedLessonId, title: '' } : null"
        :course="courseId ? { course_id: courseId, title: '' } : null"
        @generated="handleExplanationGenerated"
        @deleted="handleExplanationGenerated"
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

.editor-tabs {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #e8e8e8;
}

.tab-btn.active {
  background: #2196f3;
  color: white;
  border-color: #1976d2;
}

.editor-layout {
  display: grid;
  grid-template-columns: 250px 1fr 300px;
  gap: 10px;
  flex: 1;
  overflow: hidden;
}

.theory-content,
.explanation-content {
  flex: 1;
  overflow: auto;
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
