<!--
  StructureTree — Interactive tree of chapters and lessons.
  Click a node to set the chat context.
-->
<template>
  <div class="structure-tree">
    <div v-if="!structure" class="tree-empty">
      <p>{{ $t('aiEditor.structure.empty') }}</p>
    </div>
    <template v-else>
      <div v-for="chapter in structure.chapters" :key="chapter.id" class="tree-chapter">
        <StructureNode
          :node="{ id: chapter.id, title: chapter.title, type: 'chapter', lessonCount: chapter.lessons.length }"
          :is-expanded="expandedNodes.has(chapter.id)"
          :is-selected="selectedId === chapter.id"
          @toggle="$emit('toggleNode', $event)"
          @select="(type, id, title) => $emit('selectContext', type, id, title)"
        />
        <div v-if="expandedNodes.has(chapter.id)" class="tree-lessons">
          <StructureNode
            v-for="lesson in chapter.lessons"
            :key="lesson.id"
            :node="{
              id: lesson.id,
              title: lesson.title,
              type: 'lesson',
              contentIndicators: lesson.contentIndicators,
            }"
            :is-selected="selectedId === lesson.id"
            @select="(type, id, title) => $emit('selectContext', type, id, title)"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { DraftStructure } from '../types'
import StructureNode from './StructureNode.vue'

defineProps<{
  structure: DraftStructure | null
  expandedNodes: Set<string>
  selectedId?: string | null
}>()

defineEmits<{
  toggleNode: [id: string]
  selectContext: [type: 'chapter' | 'lesson', id: string, title: string]
}>()
</script>

<style scoped>
.structure-tree {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}
.tree-empty {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}
.tree-lessons { padding-left: 0.75rem; }
</style>
