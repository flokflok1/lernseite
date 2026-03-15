<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ArchiveFolder } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

interface Props {
  node: ArchiveFolder
  depth?: number
  activeFolderId?: string | null
  dropTargetId?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  depth: 0,
  activeFolderId: null,
  dropTargetId: null,
})

const emit = defineEmits<{
  select: [folderId: string]
  contextmenu: [event: MouseEvent, folder: ArchiveFolder]
  dragstart: [event: DragEvent, folder: ArchiveFolder]
  dragover: [event: DragEvent, folderId: string]
  dragleave: [event: DragEvent]
  drop: [event: DragEvent, folderId: string]
}>()

const expanded = ref(false)
const hasChildren = computed(() =>
  (props.node.children && props.node.children.length > 0) ||
  (props.node.child_count && props.node.child_count > 0)
)
const isActive = computed(() => props.activeFolderId === String(props.node.folder_id))
const isDropTarget = computed(() => props.dropTargetId === String(props.node.folder_id))
const totalCount = computed(() =>
  (props.node.child_count || 0) + (props.node.file_count || 0)
)

function toggle() {
  expanded.value = !expanded.value
}

function handleClick() {
  if (hasChildren.value) expanded.value = true
  emit('select', String(props.node.folder_id))
}
</script>

<template>
  <div>
    <div
      class="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm cursor-pointer transition-colors select-none"
      :class="{
        'bg-indigo-500/20 text-indigo-300': isActive,
        'hover:bg-gray-700/50': !isActive,
        'ring-1 ring-indigo-400 bg-indigo-500/10': isDropTarget,
      }"
      :style="{ paddingLeft: `${8 + depth * 16}px` }"
      draggable="true"
      @click="handleClick"
      @contextmenu.prevent="emit('contextmenu', $event, node)"
      @dragstart="emit('dragstart', $event, node)"
      @dragover.prevent="emit('dragover', $event, String(node.folder_id))"
      @dragleave="emit('dragleave', $event)"
      @drop="emit('drop', $event, String(node.folder_id))"
    >
      <span
        class="w-3.5 text-[10px] text-gray-400 flex-shrink-0 text-center"
        @click.stop="toggle"
      >
        {{ hasChildren ? (expanded ? '▼' : '▶') : '' }}
      </span>
      <span class="text-sm flex-shrink-0">{{ node.icon || '📁' }}</span>
      <span class="flex-1 truncate">{{ node.name }}</span>
      <span
        v-if="totalCount > 0"
        class="text-[11px] text-gray-400 bg-gray-700/50 px-1.5 rounded-full"
      >
        {{ totalCount }}
      </span>
    </div>

    <div v-if="expanded && node.children?.length">
      <ExplorerSidebarNode
        v-for="child in node.children"
        :key="String(child.folder_id)"
        :node="child"
        :depth="depth + 1"
        :active-folder-id="activeFolderId"
        :drop-target-id="dropTargetId"
        @select="emit('select', $event)"
        @contextmenu="emit('contextmenu', $event[0] as any, $event[1] as any)"
        @dragstart="emit('dragstart', $event[0] as any, $event[1] as any)"
        @dragover="emit('dragover', $event[0] as any, $event[1] as any)"
        @dragleave="emit('dragleave', $event)"
        @drop="emit('drop', $event[0] as any, $event[1] as any)"
      />
    </div>
  </div>
</template>
