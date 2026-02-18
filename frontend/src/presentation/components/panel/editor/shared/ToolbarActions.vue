/**
 * ToolbarActions.vue - Action buttons (save, undo, etc.)
 *
 * Shared component for both ManualEditor and AIEditor.
 * Provides common editing actions (save, publish, draft, undo, redo).
 */

<script setup lang="ts">
interface Props {
  isDirty: boolean
}

interface Emits {
  (e: 'save'): void
  (e: 'publish'): void
  (e: 'saveDraft'): void
  (e: 'undo'): void
  (e: 'redo'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<template>
  <div class="toolbar">
    <!-- Save Actions -->
    <div class="toolbar-group">
      <button
        class="btn-action btn-primary"
        :disabled="!isDirty"
        @click="$emit('save')"
      >
        💾 {{ $t('common.save') }}
      </button>
      <button
        class="btn-action"
        @click="$emit('publish')"
      >
        🚀 {{ $t('courses.editor.publish') }}
      </button>
      <button
        class="btn-action"
        @click="$emit('saveDraft')"
      >
        📝 {{ $t('courses.editor.saveDraft') }}
      </button>
    </div>

    <!-- Undo/Redo -->
    <div class="toolbar-group">
      <button class="btn-action" @click="$emit('undo')">
        ↶ {{ $t('common.undo') }}
      </button>
      <button class="btn-action" @click="$emit('redo')">
        ↷ {{ $t('common.redo') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  align-items: center;
}

.toolbar-group {
  display: flex;
  gap: 8px;
  padding-right: 16px;
  border-right: 1px solid #e0e0e0;
}

.toolbar-group:last-child {
  padding-right: 0;
  border-right: none;
}

.btn-action {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
  transition: all 0.2s;
}

.btn-action:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #999;
}

.btn-action.btn-primary {
  background: #2196f3;
  color: white;
  border-color: #1976d2;
}

.btn-action.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
