<!--
  StructureView — Default right-panel view.
  Shows course tree + finalize button.
-->
<template>
  <div class="structure-view">
    <div class="structure-header">
      <h3 class="structure-title">{{ $t('aiEditor.structure.title') }}</h3>
      <div v-if="chapterCount > 0" class="structure-stats">
        <span>{{ chapterCount }} {{ $t('aiEditor.structure.chapters') }}</span>
        <span>{{ lessonCount }} {{ $t('aiEditor.structure.lessons') }}</span>
      </div>
    </div>

    <div class="structure-scroll">
      <StructureTree
        :structure="structure"
        :expanded-nodes="expandedNodes"
        :selected-id="selectedId"
        @toggle-node="$emit('toggleNode', $event)"
        @select-context="(type, id, title) => $emit('selectContext', type, id, title)"
      />
    </div>

    <!-- Finalize button -->
    <div v-if="chapterCount > 0" class="structure-footer">
      <button
        class="finalize-btn"
        :disabled="isFinalizing"
        @click="$emit('finalize')"
      >
        {{ isFinalizing ? $t('aiEditor.structure.finalizing') : $t('aiEditor.structure.finalize') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DraftStructure } from '../types'
import StructureTree from './StructureTree.vue'

defineProps<{
  structure: DraftStructure | null
  expandedNodes: Set<string>
  selectedId?: string | null
  chapterCount: number
  lessonCount: number
  isFinalizing?: boolean
}>()

defineEmits<{
  toggleNode: [id: string]
  selectContext: [type: 'chapter' | 'lesson', id: string, title: string]
  finalize: []
}>()
</script>

<style scoped>
.structure-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.structure-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}
.structure-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}
.structure-stats {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.25rem;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}
.structure-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.08) transparent;
}
.structure-scroll:hover {
  scrollbar-color: rgba(255, 255, 255, 0.15) transparent;
}
.structure-scroll::-webkit-scrollbar {
  width: 4px;
}
.structure-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.structure-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
}
.structure-scroll:hover::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
}
.structure-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}
.finalize-btn {
  width: 100%;
  padding: 0.625rem;
  background: var(--color-success, #22c55e);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
}
.finalize-btn:hover:not(:disabled) { filter: brightness(0.9); }
.finalize-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
