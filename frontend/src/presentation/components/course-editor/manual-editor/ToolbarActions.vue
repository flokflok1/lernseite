/**
 * ToolbarActions.vue - Action buttons (save, undo, etc.)
 */

<script setup lang="ts">
interface Props {
  isDirty: boolean
}

interface Emits {
  (e: 'save'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<template>
  <div class="toolbar">
    <button class="btn-action" :disabled="!isDirty" @click="$emit('save')">
      {{ $t('common.save') }}
    </button>
    <button class="btn-action">{{ $t('common.undo') }}</button>
    <button class="btn-action">{{ $t('common.redo') }}</button>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-action {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-action:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #999;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
