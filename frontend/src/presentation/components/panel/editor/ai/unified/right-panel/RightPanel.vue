<!--
  RightPanel — Container that switches between views based on workflow phase.
  plan -> StructureView | generate -> ProgressView | accept -> ResultView
-->
<template>
  <div class="right-panel">
    <StructureView
      v-if="phase === 'plan'"
      :structure="structure"
      :expanded-nodes="expandedNodes"
      :selected-id="selectedId"
      :chapter-count="chapterCount"
      :lesson-count="lessonCount"
      :is-finalizing="isFinalizing"
      @toggle-node="$emit('toggleNode', $event)"
      @select-context="(type, id, title) => $emit('selectContext', type, id, title)"
      @finalize="$emit('finalize')"
    />
    <ProgressView
      v-else-if="phase === 'generate'"
      :progress="progress"
    />
    <ResultView
      v-else-if="phase === 'accept'"
      :result="result"
      :disabled="isGenerating"
      @accept="$emit('acceptResult')"
      @reject="$emit('rejectResult')"
      @revise="$emit('reviseResult')"
    />
  </div>
</template>

<script setup lang="ts">
import type { WorkflowPhase, DraftStructure, GenerateProgress, GenerateResult } from '../types'
import StructureView from './StructureView.vue'
import ProgressView from './ProgressView.vue'
import ResultView from './ResultView.vue'

defineProps<{
  phase: WorkflowPhase
  // Structure props
  structure: DraftStructure | null
  expandedNodes: Set<string>
  selectedId?: string | null
  chapterCount: number
  lessonCount: number
  isFinalizing?: boolean
  // Progress props
  progress: GenerateProgress | null
  // Result props
  result: GenerateResult | null
  isGenerating?: boolean
}>()

defineEmits<{
  toggleNode: [id: string]
  selectContext: [type: 'chapter' | 'lesson', id: string, title: string]
  finalize: []
  acceptResult: []
  rejectResult: []
  reviseResult: []
}>()
</script>

<style scoped>
.right-panel {
  height: 100%;
  background: var(--color-surface);
  overflow: hidden;
}
</style>
