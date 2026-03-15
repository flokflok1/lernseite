<!--
  ExamFolderExplorer — Dynamic file-explorer for exam archive.

  Renders a tree built by useExamArchiveTree composable.
  Hierarchy depth and order are fully configurable by the admin.
-->
<script setup lang="ts">
import { ref } from 'vue'
import type { TreeNode } from '@/application/composables/panel/admin/assessment'
import ExamTreeNode from './ExamTreeNode.vue'

interface Props {
  nodes: TreeNode[]
}

defineProps<Props>()

const emit = defineEmits<{
  deleteSession: [sessionId: string, examCount: number]
  deleteExam: [examId: string, title: string]
  moveExam: [examId: string, title: string]
}>()

// Collect refs to child nodes for cache clearing
const nodeRefs = ref<InstanceType<typeof ExamTreeNode>[]>([])

function clearExamCache() {
  nodeRefs.value.forEach((n) => n?.clearExamCache?.())
}

defineExpose({ clearExamCache })
</script>

<template>
  <div class="space-y-1">
    <ExamTreeNode
      v-for="node in nodes"
      :key="node.key"
      :ref="(el: any) => { if (el) nodeRefs.push(el) }"
      :node="node"
      :depth="0"
      @delete-session="(sid, cnt) => emit('deleteSession', sid, cnt)"
      @delete-exam="(eid, title) => emit('deleteExam', eid, title)"
      @move-exam="(eid, title) => emit('moveExam', eid, title)"
    />
  </div>
</template>
