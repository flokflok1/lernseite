/**
 * ContentEditPanel.vue
 *
 * Main content editing panel with TipTap rich text editor.
 * Supports text, video, quiz, and AI lesson types.
 * Replaces the shared ContentEditor stub.
 */

<script setup lang="ts">
import { EditorContent } from '@tiptap/vue-3'
import { useContentEditor } from './composables/useContentEditor'
import VideoEditorSection from './content/VideoEditorSection.vue'
import QuizEditorSection from './content/QuizEditorSection.vue'
import AiEditorSection from './content/AiEditorSection.vue'
import type { EditorModeConfig } from '../types'

interface Props {
  modeConfig: EditorModeConfig
}

defineProps<Props>()

const {
  editor,
  lesson,
  lessonType,
  toggleBold,
  toggleItalic,
  toggleUnderline,
  toggleStrike,
  setHeading,
  toggleBulletList,
  toggleOrderedList,
  toggleCodeBlock,
  setAlignLeft,
  setAlignCenter,
  setAlignRight,
  undoAction,
  redoAction,
  insertLink,
  insertImage,
  isActive,
} = useContentEditor()
</script>

<template>
  <div class="content-edit-panel">
    <!-- No lesson selected -->
    <div v-if="!lesson" class="empty-state">
      <p>{{ $t('panel.manualEditor.content.noLessonSelected') }}</p>
    </div>

    <!-- Text editor -->
    <template v-else-if="lessonType === 'text'">
      <!-- Toolbar -->
      <div class="editor-toolbar">
        <div class="toolbar-group">
          <button :class="{ active: isActive('bold') }" @click="toggleBold" title="Bold"><b>B</b></button>
          <button :class="{ active: isActive('italic') }" @click="toggleItalic" title="Italic"><i>I</i></button>
          <button :class="{ active: isActive('underline') }" @click="toggleUnderline" title="Underline"><u>U</u></button>
          <button :class="{ active: isActive('strike') }" @click="toggleStrike" title="Strikethrough"><s>S</s></button>
        </div>

        <div class="toolbar-group">
          <button :class="{ active: isActive('heading', { level: 1 }) }" @click="setHeading(1)">H1</button>
          <button :class="{ active: isActive('heading', { level: 2 }) }" @click="setHeading(2)">H2</button>
          <button :class="{ active: isActive('heading', { level: 3 }) }" @click="setHeading(3)">H3</button>
        </div>

        <div class="toolbar-group">
          <button :class="{ active: isActive('bulletList') }" @click="toggleBulletList">&#8226;</button>
          <button :class="{ active: isActive('orderedList') }" @click="toggleOrderedList">1.</button>
          <button :class="{ active: isActive('codeBlock') }" @click="toggleCodeBlock">&lt;/&gt;</button>
        </div>

        <div class="toolbar-group">
          <button @click="setAlignLeft" :class="{ active: isActive({ textAlign: 'left' }) }">&#8676;</button>
          <button @click="setAlignCenter" :class="{ active: isActive({ textAlign: 'center' }) }">&#8596;</button>
          <button @click="setAlignRight" :class="{ active: isActive({ textAlign: 'right' }) }">&#8677;</button>
        </div>

        <div class="toolbar-group">
          <button @click="insertLink" title="Link">&#128279;</button>
          <button @click="insertImage" title="Image">&#128247;</button>
        </div>

        <div class="toolbar-group">
          <button @click="undoAction">&#8630;</button>
          <button @click="redoAction">&#8631;</button>
        </div>
      </div>

      <!-- TipTap editor area -->
      <div class="editor-area">
        <EditorContent :editor="editor" class="tiptap-content" />
      </div>
    </template>

    <!-- Video editor -->
    <VideoEditorSection
      v-else-if="lessonType === 'video'"
      :lesson="lesson"
    />

    <!-- Quiz editor -->
    <QuizEditorSection
      v-else-if="lessonType === 'quiz'"
      :lesson-id="lesson?.lesson_id"
    />

    <!-- AI editor -->
    <AiEditorSection v-else-if="lessonType === 'ai'" />
  </div>
</template>

<style scoped>
.content-edit-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
}

/* Toolbar */
.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
}

.toolbar-group {
  display: flex;
  gap: 2px;
  padding-right: 8px;
  border-right: 1px solid #e8e8e8;
}

.toolbar-group:last-child {
  border-right: none;
  padding-right: 0;
}

.toolbar-group button {
  padding: 4px 8px;
  border: 1px solid transparent;
  background: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  min-width: 28px;
  text-align: center;
  color: #555;
}

.toolbar-group button:hover {
  background: #e8e8e8;
}

.toolbar-group button.active {
  background: #e3f2fd;
  border-color: #90caf9;
  color: #1565c0;
}

/* TipTap area */
.editor-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.tiptap-content :deep(.tiptap) {
  outline: none;
  min-height: 300px;
  font-size: 14px;
  line-height: 1.6;
}

.tiptap-content :deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #aaa;
  pointer-events: none;
  height: 0;
}

.tiptap-content :deep(.tiptap h1) { font-size: 24px; font-weight: 700; margin: 16px 0 8px; }
.tiptap-content :deep(.tiptap h2) { font-size: 20px; font-weight: 600; margin: 14px 0 6px; }
.tiptap-content :deep(.tiptap h3) { font-size: 16px; font-weight: 600; margin: 12px 0 4px; }
.tiptap-content :deep(.tiptap ul),
.tiptap-content :deep(.tiptap ol) { padding-left: 24px; }
.tiptap-content :deep(.tiptap pre) {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}
.tiptap-content :deep(.tiptap a) { color: #1976d2; text-decoration: underline; }
.tiptap-content :deep(.tiptap img) { max-width: 100%; border-radius: 4px; }
</style>
