/**
 * ContentEditPanel.vue
 *
 * Main content editing panel with TipTap rich text editor.
 * Supports text, video, quiz, and AI lesson types.
 * Replaces the shared ContentEditor stub.
 */

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Image from '@tiptap/extension-image'
import Link from '@tiptap/extension-link'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import type { EditorModeConfig } from '../types'

interface Props {
  modeConfig: EditorModeConfig
}

defineProps<Props>()

const { t } = useI18n()
const store = useCourseEditorStore()

const lesson = computed(() => store.currentLesson)
const lessonType = computed(() => lesson.value?.lesson_type || 'text')

// Video fields
const videoUrl = ref('')
const videoPlatform = ref<'youtube' | 'vimeo' | 'custom'>('youtube')

// Quiz fields
const quizQuestion = ref('')
const quizAnswers = ref<Array<{ text: string; correct: boolean }>>([
  { text: '', correct: true },
  { text: '', correct: false },
])

// AI fields
const aiPrompt = ref('')

// TipTap editor
const editor = useEditor({
  extensions: [
    StarterKit,
    Placeholder.configure({
      placeholder: () => t('panel.manualEditor.content.placeholder'),
    }),
    Image,
    Link.configure({ openOnClick: false }),
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Underline,
  ],
  content: '',
  onUpdate: ({ editor: ed }) => {
    if (lesson.value) {
      store.updateLessonContent(lesson.value.lesson_id, ed.getHTML())
    }
  },
})

// Sync editor content when lesson changes
watch(lesson, (newLesson) => {
  if (!editor.value) return

  if (newLesson) {
    const content = typeof newLesson.content === 'string' ? newLesson.content : ''
    if (editor.value.getHTML() !== content) {
      editor.value.commands.setContent(content, false)
    }
    // Load type-specific data
    if (newLesson.lesson_type === 'video') {
      const meta = newLesson.content_meta || {}
      videoUrl.value = meta.video_url || ''
      videoPlatform.value = meta.platform || 'youtube'
    }
  } else {
    editor.value.commands.setContent('', false)
  }
}, { immediate: true })

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// Quiz helpers
const addAnswer = (): void => {
  quizAnswers.value.push({ text: '', correct: false })
}

const removeAnswer = (index: number): void => {
  if (quizAnswers.value.length > 2) {
    quizAnswers.value.splice(index, 1)
  }
}

const setCorrectAnswer = (index: number): void => {
  quizAnswers.value.forEach((a, i) => {
    a.correct = i === index
  })
}

// Video save
const saveVideoMeta = (): void => {
  if (!lesson.value) return
  store.updateLessonMeta(lesson.value.lesson_id, {
    content_meta: {
      video_url: videoUrl.value,
      platform: videoPlatform.value,
    },
  })
}

// Toolbar actions
const toggleBold = (): void => editor.value?.chain().focus().toggleBold().run()
const toggleItalic = (): void => editor.value?.chain().focus().toggleItalic().run()
const toggleUnderline = (): void => editor.value?.chain().focus().toggleUnderline().run()
const toggleStrike = (): void => editor.value?.chain().focus().toggleStrike().run()
const setHeading = (level: 1 | 2 | 3): void => editor.value?.chain().focus().toggleHeading({ level }).run()
const toggleBulletList = (): void => editor.value?.chain().focus().toggleBulletList().run()
const toggleOrderedList = (): void => editor.value?.chain().focus().toggleOrderedList().run()
const toggleCodeBlock = (): void => editor.value?.chain().focus().toggleCodeBlock().run()
const setAlignLeft = (): void => editor.value?.chain().focus().setTextAlign('left').run()
const setAlignCenter = (): void => editor.value?.chain().focus().setTextAlign('center').run()
const setAlignRight = (): void => editor.value?.chain().focus().setTextAlign('right').run()
const undoAction = (): void => editor.value?.chain().focus().undo().run()
const redoAction = (): void => editor.value?.chain().focus().redo().run()

const insertLink = (): void => {
  const url = window.prompt('URL:')
  if (url) {
    editor.value?.chain().focus().setLink({ href: url }).run()
  }
}

const insertImage = (): void => {
  const url = window.prompt('Image URL:')
  if (url) {
    editor.value?.chain().focus().setImage({ src: url }).run()
  }
}

const isActive = (name: string, attrs?: Record<string, unknown>): boolean => {
  return editor.value?.isActive(name, attrs) || false
}
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
    <template v-else-if="lessonType === 'video'">
      <div class="video-editor">
        <h3>{{ $t('panel.manualEditor.content.videoUrl') }}</h3>
        <div class="form-row">
          <select v-model="videoPlatform" @change="saveVideoMeta">
            <option value="youtube">YouTube</option>
            <option value="vimeo">Vimeo</option>
            <option value="custom">{{ $t('panel.manualEditor.content.videoPlatform') }}</option>
          </select>
          <input
            v-model="videoUrl"
            type="url"
            :placeholder="$t('panel.manualEditor.content.videoUrl')"
            @change="saveVideoMeta"
          />
        </div>
        <div v-if="videoUrl" class="video-preview">
          <iframe
            v-if="videoPlatform === 'youtube'"
            :src="`https://www.youtube.com/embed/${videoUrl.split('v=')[1]?.split('&')[0] || ''}`"
            frameborder="0"
            allowfullscreen
          />
          <p v-else class="preview-url">{{ videoUrl }}</p>
        </div>
      </div>
    </template>

    <!-- Quiz editor -->
    <template v-else-if="lessonType === 'quiz'">
      <div class="quiz-editor">
        <h3>{{ $t('panel.manualEditor.content.quizQuestion') }}</h3>
        <textarea
          v-model="quizQuestion"
          :placeholder="$t('panel.manualEditor.content.quizQuestion')"
          rows="3"
        />

        <h4>{{ $t('panel.manualEditor.content.quizAnswer') }}</h4>
        <div v-for="(answer, i) in quizAnswers" :key="i" class="quiz-answer">
          <input
            type="radio"
            :name="'correct-' + lesson?.lesson_id"
            :checked="answer.correct"
            @change="setCorrectAnswer(i)"
          />
          <input
            v-model="answer.text"
            type="text"
            :placeholder="$t('panel.manualEditor.content.quizAnswer') + ' ' + (i + 1)"
          />
          <button
            v-if="quizAnswers.length > 2"
            class="remove-answer"
            @click="removeAnswer(i)"
          >
            &times;
          </button>
        </div>
        <button class="add-answer-btn" @click="addAnswer">
          + {{ $t('panel.manualEditor.content.quizAddAnswer') }}
        </button>
      </div>
    </template>

    <!-- AI editor -->
    <template v-else-if="lessonType === 'ai'">
      <div class="ai-editor">
        <h3>{{ $t('panel.manualEditor.content.aiPrompt') }}</h3>
        <textarea
          v-model="aiPrompt"
          :placeholder="$t('panel.manualEditor.content.aiPrompt')"
          rows="6"
        />
        <button class="ai-generate-btn">
          {{ $t('panel.manualEditor.content.aiGenerate') }}
        </button>
      </div>
    </template>
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

/* Video editor */
.video-editor {
  padding: 16px;
}

.video-editor h3 {
  font-size: 14px;
  margin: 0 0 8px;
}

.form-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.form-row select {
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.form-row input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.video-preview {
  margin-top: 12px;
}

.video-preview iframe {
  width: 100%;
  height: 280px;
  border-radius: 8px;
}

.preview-url {
  color: #666;
  font-size: 13px;
}

/* Quiz editor */
.quiz-editor {
  padding: 16px;
}

.quiz-editor h3,
.quiz-editor h4 {
  font-size: 14px;
  margin: 0 0 8px;
}

.quiz-editor textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
}

.quiz-answer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.quiz-answer input[type="text"] {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.remove-answer {
  border: none;
  background: none;
  color: #e53935;
  cursor: pointer;
  font-size: 18px;
}

.add-answer-btn {
  margin-top: 4px;
  padding: 6px 12px;
  border: 1px dashed #2196f3;
  background: none;
  color: #2196f3;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

/* AI editor */
.ai-editor {
  padding: 16px;
}

.ai-editor h3 {
  font-size: 14px;
  margin: 0 0 8px;
}

.ai-editor textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
}

.ai-generate-btn {
  margin-top: 8px;
  padding: 8px 16px;
  background: #7c4dff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.ai-generate-btn:hover {
  background: #651fff;
}
</style>
