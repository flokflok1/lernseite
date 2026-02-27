<!--
  StructureNode — Single tree node (chapter or lesson).
  Chapters are expandable, lessons show content indicators.
-->
<template>
  <div class="structure-node" :class="{ 'is-selected': isSelected, 'is-chapter': isChapter }">
    <div class="node-header" @click="handleClick">
      <button
        v-if="isChapter"
        class="expand-btn"
        @click.stop="$emit('toggle', node.id)"
      >
        {{ isExpanded ? '▾' : '▸' }}
      </button>
      <span v-else class="node-indent" />
      <span class="node-icon">{{ isChapter ? '📖' : '📄' }}</span>
      <span class="node-title">{{ node.title }}</span>
      <span v-if="isChapter && lessonCount > 0" class="node-badge">{{ lessonCount }}</span>
    </div>
    <!-- Content indicators for lessons -->
    <div v-if="!isChapter && indicators.length > 0" class="node-indicators">
      <span
        v-for="ind in indicators"
        :key="ind.type"
        class="indicator"
        :class="`status-${ind.status}`"
      >
        {{ ind.label }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface ContentIndicator {
  type: string
  label: string
  count?: number
  status: string
}

interface TreeNode {
  id: string
  title: string
  type: 'chapter' | 'lesson'
  lessonCount?: number
  contentIndicators?: ContentIndicator[]
}

const props = defineProps<{
  node: TreeNode
  isExpanded?: boolean
  isSelected?: boolean
}>()

const emit = defineEmits<{
  toggle: [id: string]
  select: [type: 'chapter' | 'lesson', id: string, title: string]
}>()

const isChapter = computed(() => props.node.type === 'chapter')
const lessonCount = computed(() => props.node.lessonCount ?? 0)
const indicators = computed(() => props.node.contentIndicators ?? [])

function handleClick(): void {
  emit('select', props.node.type, props.node.id, props.node.title)
}
</script>

<style scoped>
.structure-node { padding: 0.125rem 0; }
.node-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.1s;
}
.node-header:hover { background: var(--color-surface-secondary); }
.is-selected > .node-header {
  background: var(--color-primary-subtle);
  border-left: 2px solid var(--color-primary);
}
.expand-btn {
  background: none;
  border: none;
  font-size: 0.75rem;
  cursor: pointer;
  color: var(--color-text-tertiary);
  width: 1rem;
  padding: 0;
}
.node-indent { width: 1rem; flex-shrink: 0; }
.node-icon { font-size: 0.875rem; flex-shrink: 0; }
.node-title {
  flex: 1;
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.is-chapter > .node-header > .node-title { font-weight: 600; }
.node-badge {
  font-size: 0.625rem;
  padding: 0.0625rem 0.375rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
  color: var(--color-text-tertiary);
}
.node-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding-left: 2.25rem;
  margin-top: 0.125rem;
}
.indicator {
  font-size: 0.5625rem;
  padding: 0.0625rem 0.25rem;
  border-radius: 0.125rem;
  border: 1px solid var(--color-border);
}
.indicator.status-empty { color: var(--color-text-tertiary); }
.indicator.status-draft { color: var(--color-warning, #f59e0b); border-color: currentColor; }
.indicator.status-generated { color: var(--color-primary); border-color: currentColor; }
.indicator.status-accepted { color: var(--color-success, #22c55e); border-color: currentColor; }
</style>
