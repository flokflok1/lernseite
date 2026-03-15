<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import FolderCard from './FolderCard.vue'
import FileRow from './FileRow.vue'
import type { ArchiveFolder, ArchiveFile } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

interface Props {
  folders: ArchiveFolder[]
  files: ArchiveFile[]
  viewMode: 'grid' | 'list'
  loading: boolean
  isEmpty: boolean
  dropTargetId?: string | null
}

defineProps<Props>()

const emit = defineEmits<{
  openFolder: [folderId: string]
  openFile: [examId: string]
  folderContextmenu: [event: MouseEvent, folder: ArchiveFolder]
  fileContextmenu: [event: MouseEvent, file: ArchiveFile]
  backgroundContextmenu: [event: MouseEvent]
  dragstartFolder: [event: DragEvent, folder: ArchiveFolder]
  dragstartFile: [event: DragEvent, file: ArchiveFile]
  dragover: [event: DragEvent, folderId: string]
  dragleave: [event: DragEvent]
  drop: [event: DragEvent, folderId: string]
}>()

const { t } = useI18n()
</script>

<template>
  <div
    class="flex-1 overflow-y-auto p-5"
    @contextmenu.prevent.self="emit('backgroundContextmenu', $event)"
  >
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center h-40">
      <div class="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="isEmpty"
      class="flex flex-col items-center justify-center h-40 text-gray-500"
    >
      <span class="text-4xl mb-3">📂</span>
      <span class="text-sm">{{ t('panel.examArchive.emptyFolder') }}</span>
    </div>

    <template v-else>
      <!-- Folders section -->
      <div v-if="folders.length > 0" class="mb-6">
        <div class="text-[11px] uppercase tracking-wider text-gray-400 mb-2.5 pb-1.5 border-b border-gray-700/50">
          {{ t('panel.examArchive.folders') }} — {{ folders.length }}
        </div>
        <div
          v-if="viewMode === 'grid'"
          class="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-3"
        >
          <FolderCard
            v-for="folder in folders"
            :key="String(folder.folder_id)"
            :folder="folder"
            :is-drop-target="dropTargetId === String(folder.folder_id)"
            @open="emit('openFolder', $event)"
            @contextmenu="(ev, f) => emit('folderContextmenu', ev, f)"
            @dragstart="(ev, f) => emit('dragstartFolder', ev, f)"
            @dragover="(ev, id) => emit('dragover', ev, id)"
            @dragleave="(ev) => emit('dragleave', ev)"
            @drop="(ev, id) => emit('drop', ev, id)"
          />
        </div>
        <div v-else>
          <FolderCard
            v-for="folder in folders"
            :key="String(folder.folder_id)"
            :folder="folder"
            :is-drop-target="dropTargetId === String(folder.folder_id)"
            @open="emit('openFolder', $event)"
            @contextmenu="(ev, f) => emit('folderContextmenu', ev, f)"
            @dragstart="(ev, f) => emit('dragstartFolder', ev, f)"
            @dragover="(ev, id) => emit('dragover', ev, id)"
            @dragleave="(ev) => emit('dragleave', ev)"
            @drop="(ev, id) => emit('drop', ev, id)"
          />
        </div>
      </div>

      <!-- Files section -->
      <div v-if="files.length > 0">
        <div class="text-[11px] uppercase tracking-wider text-gray-400 mb-2.5 pb-1.5 border-b border-gray-700/50">
          {{ t('panel.examArchive.files') }} — {{ files.length }}
        </div>
        <div>
          <FileRow
            v-for="file in files"
            :key="String(file.exam_id)"
            :file="file"
            @open="emit('openFile', $event)"
            @contextmenu="(ev, f) => emit('fileContextmenu', ev, f)"
            @dragstart="(ev, f) => emit('dragstartFile', ev, f)"
          />
        </div>
      </div>
    </template>
  </div>
</template>
