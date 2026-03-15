<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import ExplorerSidebarNode from './ExplorerSidebarNode.vue'
import type { ArchiveFolder, ExamProgram } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

interface Props {
  programs: ExamProgram[]
  sidebarTree: ArchiveFolder[]
  currentProgramId: number | null
  currentFolderId: string | null
  dropTargetId?: string | null
}

defineProps<Props>()

const emit = defineEmits<{
  selectProgram: [programId: number]
  selectFolder: [folderId: string]
  createFolder: [name: string, parentId?: string]
  contextmenu: [event: MouseEvent, folder: ArchiveFolder]
  dragstart: [event: DragEvent, folder: ArchiveFolder]
  dragover: [event: DragEvent, folderId: string]
  dragleave: [event: DragEvent]
  drop: [event: DragEvent, folderId: string]
}>()

const { t, locale } = useI18n()

const creatingIn = ref<number | null>(null)
const newFolderName = ref('')

function getDisplayName(displayName: Record<string, string>): string {
  return displayName[locale.value] || displayName['de'] || displayName['en'] || ''
}

function startCreate(programId: number) {
  creatingIn.value = programId
  newFolderName.value = t('panel.examArchive.defaultFolderName')
}

function confirmCreate() {
  if (newFolderName.value.trim()) {
    emit('createFolder', newFolderName.value.trim())
  }
  creatingIn.value = null
  newFolderName.value = ''
}

function cancelCreate() {
  creatingIn.value = null
  newFolderName.value = ''
}
</script>

<template>
  <aside class="w-[280px] bg-gray-900/60 border-r border-gray-700/50 overflow-y-auto flex-shrink-0">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 pt-3.5 pb-2">
      <span class="text-[11px] uppercase tracking-wider text-gray-400">
        {{ t('panel.examArchive.programs') }}
      </span>
    </div>

    <!-- Program list -->
    <div class="px-2 pb-4">
      <div v-for="prog in programs" :key="prog.program_id">
        <!-- Program root -->
        <div
          class="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm cursor-pointer transition-colors select-none"
          :class="{
            'text-indigo-300': currentProgramId === prog.program_id,
            'hover:bg-gray-700/50': currentProgramId !== prog.program_id,
          }"
          @click="emit('selectProgram', prog.program_id)"
        >
          <span
            class="w-3.5 text-[10px] text-gray-400 flex-shrink-0 text-center"
          >{{ currentProgramId === prog.program_id ? '▼' : '▶' }}</span>
          <span class="text-sm flex-shrink-0">{{ prog.icon || '🎓' }}</span>
          <span class="flex-1 truncate">{{ getDisplayName(prog.display_name) }}</span>
          <span
            v-if="prog.root_folder_count"
            class="text-[11px] text-gray-400 bg-gray-700/50 px-1.5 rounded-full"
          >{{ prog.root_folder_count }}</span>
          <button
            v-if="currentProgramId === prog.program_id"
            class="w-5 h-5 flex items-center justify-center rounded text-gray-400 hover:text-indigo-300 hover:bg-gray-700 text-sm"
            :title="t('panel.examArchive.newFolder')"
            @click.stop="startCreate(prog.program_id)"
          >+</button>
        </div>

        <!-- Inline create -->
        <div
          v-if="creatingIn === prog.program_id"
          class="flex items-center gap-1 px-2 py-1 ml-6"
        >
          <span class="text-sm">📁</span>
          <input
            v-model="newFolderName"
            class="flex-1 bg-gray-800 border border-indigo-500 rounded px-2 py-0.5 text-sm text-white outline-none"
            autofocus
            @keydown.enter="confirmCreate"
            @keydown.escape="cancelCreate"
            @blur="confirmCreate"
          />
        </div>

        <!-- Folder tree for active program -->
        <div v-if="currentProgramId === prog.program_id && sidebarTree.length" class="ml-2">
          <ExplorerSidebarNode
            v-for="node in sidebarTree"
            :key="String(node.folder_id)"
            :node="node"
            :depth="1"
            :active-folder-id="currentFolderId"
            :drop-target-id="dropTargetId"
            @select="emit('selectFolder', $event)"
            @contextmenu="(ev, folder) => emit('contextmenu', ev, folder)"
            @dragstart="(ev, folder) => emit('dragstart', ev, folder)"
            @dragover="(ev, id) => emit('dragover', ev, id)"
            @dragleave="(ev) => emit('dragleave', ev)"
            @drop="(ev, id) => emit('drop', ev, id)"
          />
        </div>
      </div>
    </div>
  </aside>
</template>
