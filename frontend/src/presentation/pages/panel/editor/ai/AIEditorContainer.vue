/**
 * AIEditorContainer.vue
 *
 * Main container for AI-assisted course editing.
 */

<script setup lang="ts">
import { ref } from 'vue'
import ChatInterface from './ChatInterface.vue'
import ContentGenerator from './ContentGenerator.vue'
import VariantSelector from './VariantSelector.vue'
import GenerationHistory from './GenerationHistory.vue'
import SourceSelectionContainer from './SourceSelectionContainer.vue'
import { ContentEditor, PreviewPanel, StructurePanel } from '../shared'
import { TheoryGenerationContainer } from '../content-generation'
import { ExplanationGenerationContainer } from '../explanation-generation'

interface Props {
  projectId: string
  chapterId?: string | null
  courseId?: string | null
}

interface Emits {
  (e: 'save'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const activeTab = ref<'source-selection' | 'chat' | 'content' | 'generator' | 'variants' | 'history' | 'theory' | 'explanation'>('source-selection')
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

const handleTheoryGenerated = () => {
  isDirty.value = true
  emit('save')
}

const handleExplanationGenerated = () => {
  isDirty.value = true
  emit('save')
}
</script>

<template>
  <div class="ai-editor-container">
    <!-- Tab Navigation -->
    <div class="ai-tabs">
      <button
        :class="['tab-btn', { active: activeTab === 'source-selection' }]"
        @click="activeTab = 'source-selection'"
      >
        📂 {{ $t('courses.editor.sourceSelection') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'chat' }]"
        @click="activeTab = 'chat'"
      >
        💬 {{ $t('courses.editor.aiChat') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'content' }]"
        @click="activeTab = 'content'"
      >
        ✏️ {{ $t('courses.editor.content') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'generator' }]"
        @click="activeTab = 'generator'"
      >
        ⚡ {{ $t('courses.editor.generate') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'theory' }]"
        @click="activeTab = 'theory'"
      >
        📚 {{ $t('course-editor.theory.container.title') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'variants' }]"
        @click="activeTab = 'variants'"
      >
        📋 {{ $t('courses.editor.variants') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'history' }]"
        @click="activeTab = 'history'"
      >
        📜 {{ $t('courses.editor.history') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'explanation' }]"
        @click="activeTab = 'explanation'"
      >
        💡 {{ $t('course-editor.explanation.container.title') }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="ai-content">
      <SourceSelectionContainer v-if="activeTab === 'source-selection'" :course-id="courseId || projectId" />

      <ChatInterface v-if="activeTab === 'chat'" />

      <!-- Content Tab - Shared Editor Layout (like ManualEditor) -->
      <div v-else-if="activeTab === 'content'" class="editor-layout">
        <StructurePanel
          :selected-chapter="selectedChapterId"
          :selected-lesson="selectedLessonId"
          @select="handleStructureSelect"
        />
        <ContentEditor
          :chapter-id="selectedChapterId"
          :lesson-id="selectedLessonId"
          @change="handleContentChange"
        />
        <PreviewPanel
          :chapter-id="selectedChapterId"
          :lesson-id="selectedLessonId"
        />
      </div>

      <ContentGenerator v-else-if="activeTab === 'generator'" />
      <TheoryGenerationContainer
        v-else-if="activeTab === 'theory'"
        :chapter="chapterId ? { chapter_id: chapterId } : null"
        :course="courseId ? { course_id: courseId } : null"
        @generated="handleTheoryGenerated"
        @deleted="handleTheoryGenerated"
      />
      <VariantSelector v-else-if="activeTab === 'variants'" />
      <GenerationHistory v-else-if="activeTab === 'history'" />
      <ExplanationGenerationContainer
        v-else-if="activeTab === 'explanation'"
        :lesson="selectedLessonId ? { lesson_id: selectedLessonId, title: '' } : null"
        :course="courseId ? { course_id: courseId, title: '' } : null"
        @generated="handleExplanationGenerated"
        @deleted="handleExplanationGenerated"
      />
    </div>
  </div>
</template>

<style scoped>
.ai-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 10px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.ai-tabs {
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

.ai-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
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
