/**
 * ContentEditPanel.vue
 *
 * Main content editing panel with TipTap rich text editor.
 * Supports text, video, quiz, and AI lesson types.
 * Replaces the shared ContentEditor stub.
 */

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { EditorContent } from '@tiptap/vue-3'
import { useContentEditor } from '../composables/editor/useContentEditor'
import { useFocusTrap } from '../composables/editor/useFocusTrap'
import VideoEditorSection from './content/VideoEditorSection.vue'
import QuizEditorSection from './content/QuizEditorSection.vue'
import AiEditorSection from './content/AiEditorSection.vue'

const { t } = useI18n()

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

// URL prompt modal state
const showUrlModal = ref(false)
const urlModalTitle = ref('')
const urlModalValue = ref('')
const { trapRef: urlTrapRef } = useFocusTrap(showUrlModal)
const urlInputRef = ref<HTMLInputElement | null>(null)
let urlModalCallback: ((url: string) => void) | null = null
let urlModalAllowMailto = false

watch(showUrlModal, (open) => {
  if (open) nextTick(() => urlInputRef.value?.focus())
})

const openUrlPrompt = (title: string, callback: (url: string) => void, allowMailto = false) => {
  urlModalTitle.value = title
  urlModalValue.value = ''
  urlModalCallback = callback
  urlModalAllowMailto = allowMailto
  showUrlModal.value = true
}

const isValidUrl = (url: string, allowMailto = false): boolean => {
  try {
    const parsed = new URL(url)
    const allowed = allowMailto ? ['http:', 'https:', 'mailto:'] : ['http:', 'https:']
    return allowed.includes(parsed.protocol)
  } catch {
    return false
  }
}

const confirmUrlPrompt = () => {
  const url = urlModalValue.value.trim()
  if (url && isValidUrl(url, urlModalAllowMailto) && urlModalCallback) urlModalCallback(url)
  showUrlModal.value = false
  urlModalCallback = null
}

const cancelUrlPrompt = () => {
  showUrlModal.value = false
  urlModalCallback = null
}

const handleInsertLink = () => {
  openUrlPrompt(t('panel.manualEditor.content.enterUrl'), (url) => insertLink(url), true)
}

const handleInsertImage = () => {
  openUrlPrompt(t('panel.manualEditor.content.enterImageUrl'), (url) => insertImage(url))
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
          <button :class="{ active: isActive('bold') }" @click="toggleBold" :title="$t('panel.manualEditor.content.toolbarBold')" :aria-label="$t('panel.manualEditor.content.toolbarBold')"><b>B</b></button>
          <button :class="{ active: isActive('italic') }" @click="toggleItalic" :title="$t('panel.manualEditor.content.toolbarItalic')" :aria-label="$t('panel.manualEditor.content.toolbarItalic')"><i>I</i></button>
          <button :class="{ active: isActive('underline') }" @click="toggleUnderline" :title="$t('panel.manualEditor.content.toolbarUnderline')" :aria-label="$t('panel.manualEditor.content.toolbarUnderline')"><u>U</u></button>
          <button :class="{ active: isActive('strike') }" @click="toggleStrike" :title="$t('panel.manualEditor.content.toolbarStrikethrough')" :aria-label="$t('panel.manualEditor.content.toolbarStrikethrough')"><s>S</s></button>
        </div>

        <div class="toolbar-group">
          <button :class="{ active: isActive('heading', { level: 1 }) }" @click="setHeading(1)" :aria-label="$t('panel.manualEditor.content.toolbarHeading', { level: 1 })">H1</button>
          <button :class="{ active: isActive('heading', { level: 2 }) }" @click="setHeading(2)" :aria-label="$t('panel.manualEditor.content.toolbarHeading', { level: 2 })">H2</button>
          <button :class="{ active: isActive('heading', { level: 3 }) }" @click="setHeading(3)" :aria-label="$t('panel.manualEditor.content.toolbarHeading', { level: 3 })">H3</button>
        </div>

        <div class="toolbar-group">
          <button :class="{ active: isActive('bulletList') }" @click="toggleBulletList" :aria-label="$t('panel.manualEditor.content.toolbarBulletList')">&#8226;</button>
          <button :class="{ active: isActive('orderedList') }" @click="toggleOrderedList" :aria-label="$t('panel.manualEditor.content.toolbarOrderedList')">1.</button>
          <button :class="{ active: isActive('codeBlock') }" @click="toggleCodeBlock" :aria-label="$t('panel.manualEditor.content.toolbarCodeBlock')">&lt;/&gt;</button>
        </div>

        <div class="toolbar-group">
          <button @click="setAlignLeft" :class="{ active: isActive({ textAlign: 'left' }) }" :aria-label="$t('panel.manualEditor.content.toolbarAlignLeft')">&#8676;</button>
          <button @click="setAlignCenter" :class="{ active: isActive({ textAlign: 'center' }) }" :aria-label="$t('panel.manualEditor.content.toolbarAlignCenter')">&#8596;</button>
          <button @click="setAlignRight" :class="{ active: isActive({ textAlign: 'right' }) }" :aria-label="$t('panel.manualEditor.content.toolbarAlignRight')">&#8677;</button>
        </div>

        <div class="toolbar-group">
          <button @click="handleInsertLink" :title="$t('panel.manualEditor.content.enterUrl')" :aria-label="$t('panel.manualEditor.content.enterUrl')">&#128279;</button>
          <button @click="handleInsertImage" :title="$t('panel.manualEditor.content.enterImageUrl')" :aria-label="$t('panel.manualEditor.content.enterImageUrl')">&#128247;</button>
        </div>

        <div class="toolbar-group">
          <button @click="undoAction" :aria-label="$t('panel.manualEditor.content.toolbarUndo')">&#8630;</button>
          <button @click="redoAction" :aria-label="$t('panel.manualEditor.content.toolbarRedo')">&#8631;</button>
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

    <!-- URL prompt modal -->
    <Teleport to="body">
      <div v-if="showUrlModal" class="url-modal-overlay" @click.self="cancelUrlPrompt">
        <div ref="urlTrapRef" class="url-modal" role="dialog" :aria-label="urlModalTitle">
          <h4 class="url-modal-title">{{ urlModalTitle }}</h4>
          <input
            ref="urlInputRef"
            v-model="urlModalValue"
            type="url"
            class="url-modal-input"
            placeholder="https://..."
            @keydown.enter="confirmUrlPrompt"
            @keydown.escape="cancelUrlPrompt"
          />
          <div class="url-modal-actions">
            <button class="url-modal-cancel" @click="cancelUrlPrompt">
              {{ $t('panel.manualEditor.content.cancel') }}
            </button>
            <button class="url-modal-confirm" @click="confirmUrlPrompt">
              {{ $t('panel.manualEditor.content.insert') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.content-edit-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: var(--color-surface);
  overflow: hidden;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  font-size: 14px;
}

/* Toolbar */
.editor-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.toolbar-group {
  display: flex;
  gap: 2px;
  padding-right: 8px;
  border-right: 1px solid var(--color-border);
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
  color: var(--color-text-secondary);
}

.toolbar-group button:hover {
  background: var(--color-border);
}

.toolbar-group button.active {
  background: color-mix(in srgb, var(--color-accent) 15%, transparent);
  border-color: var(--color-accent);
  color: var(--color-accent);
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
  color: var(--color-text-primary);
}

.tiptap-content :deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: var(--color-text-tertiary);
  pointer-events: none;
  height: 0;
}

.tiptap-content :deep(.tiptap h1) { font-size: 24px; font-weight: 700; margin: 16px 0 8px; }
.tiptap-content :deep(.tiptap h2) { font-size: 20px; font-weight: 600; margin: 14px 0 6px; }
.tiptap-content :deep(.tiptap h3) { font-size: 16px; font-weight: 600; margin: 12px 0 4px; }
.tiptap-content :deep(.tiptap ul),
.tiptap-content :deep(.tiptap ol) { padding-left: 24px; }
.tiptap-content :deep(.tiptap pre) {
  background: var(--color-surface-secondary);
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}
.tiptap-content :deep(.tiptap a) { color: var(--color-accent); text-decoration: underline; }
.tiptap-content :deep(.tiptap img) { max-width: 100%; border-radius: 4px; }

/* URL prompt modal */
.url-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.url-modal {
  background: var(--color-surface);
  border-radius: 8px;
  padding: 20px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.url-modal-title {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.url-modal-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 13px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  box-sizing: border-box;
}

.url-modal-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.url-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.url-modal-cancel {
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 12px;
}

.url-modal-confirm {
  padding: 6px 14px;
  border: none;
  border-radius: 4px;
  background: var(--color-accent);
  color: white;
  cursor: pointer;
  font-size: 12px;
}
</style>
