<!--
  EditorPanel - Content Editor with Toolbar
  Sub-component of ContentTab
-->

<template>
  <div class="editor-panel">
    <div class="panel-header">
      <span class="panel-icon">✏️</span>
      <span class="panel-title">{{ contentTypeName }}</span>
      <button @click="$emit('generate')" class="generate-btn-small" :disabled="isGenerating">
        {{ isGenerating ? '⏳' : '✨' }} KI
      </button>
    </div>

    <!-- Toolbar -->
    <div class="editor-toolbar">
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.bold')"><strong>B</strong></button>
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.italic')"><em>I</em></button>
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.underline')"><u>U</u></button>
      <div class="toolbar-divider"></div>
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.list')">📋</button>
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.numberedList')">🔢</button>
      <div class="toolbar-divider"></div>
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.formula')">ƒx</button>
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.code')">&lt;/&gt;</button>
      <button class="toolbar-btn" :title="$t('windows.aiEditorContent.image')">🖼️</button>
    </div>

    <!-- Editor Area -->
    <div class="editor-area">
      <textarea
        :value="content"
        @input="$emit('update:content', ($event.target as HTMLTextAreaElement).value)"
        class="editor-textarea"
        :placeholder="$t('windows.aiEditorContent.editorPlaceholder')"
      ></textarea>
    </div>

    <!-- Editor Footer -->
    <div class="editor-footer">
      <div class="word-count">
        <span>{{ wordCount }} {{ $t('windows.aiEditorContent.words') }}</span>
        <span>{{ characterCount }} {{ $t('windows.aiEditorContent.characters') }}</span>
      </div>
      <div class="editor-actions">
        <button @click="$emit('reset')" class="btn-secondary">{{ $t('windows.aiEditorContent.reset') }}</button>
        <button @click="$emit('save')" class="btn-primary" :disabled="isSaving">
          {{ isSaving ? $t('windows.aiEditorContent.saving') : $t('windows.aiEditorContent.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  content: string
  contentTypeName: string
  wordCount: number
  characterCount: number
  isGenerating: boolean
  isSaving: boolean
}>()

defineEmits<{
  (e: 'update:content', value: string): void
  (e: 'generate'): void
  (e: 'save'): void
  (e: 'reset'): void
}>()
</script>

<style scoped>
.editor-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon { font-size: 1rem; }

.panel-title {
  flex: 1;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.generate-btn-small {
  padding: 0.25rem 0.5rem;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: opacity 0.15s;
}

.generate-btn-small:hover:not(:disabled) { opacity: 0.9; }
.generate-btn-small:disabled { opacity: 0.5; cursor: not-allowed; }

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.toolbar-btn {
  padding: 0.375rem 0.5rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.8125rem;
  transition: background 0.15s;
}

.toolbar-btn:hover { background: var(--color-surface-secondary); }

.toolbar-divider {
  width: 1px;
  height: 1rem;
  background: var(--color-border);
  margin: 0 0.25rem;
}

.editor-area {
  flex: 1;
  overflow: hidden;
}

.editor-textarea {
  width: 100%;
  height: 100%;
  padding: 1rem;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  line-height: 1.6;
  resize: none;
}

.editor-textarea:focus { outline: none; }

.editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.word-count {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.editor-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.btn-secondary:hover { background: var(--color-surface-secondary); }

.btn-primary {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) { background: var(--color-primary-dark, #2563eb); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
