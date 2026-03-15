<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFileExplorer } from '@/application/composables/panel/admin/assessment/useFileExplorer'
import { useContextMenu } from '@/application/composables/panel/admin/assessment/useContextMenu'
import { useDragDrop } from '@/application/composables/panel/admin/assessment/useDragDrop'
import ExplorerSidebar from './ExplorerSidebar.vue'
import ExplorerBreadcrumb from './ExplorerBreadcrumb.vue'
import ExplorerContent from './ExplorerContent.vue'
import ExplorerContextMenu from './ExplorerContextMenu.vue'
import ExplorerStatusBar from './ExplorerStatusBar.vue'
import FolderDetailDialog from './FolderDetailDialog.vue'
import type { ArchiveFolder, ArchiveFile } from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

const emit = defineEmits<{
  close: []
}>()

const { t } = useI18n()

const explorer = useFileExplorer()
const ctxMenu = useContextMenu()

const dragDrop = useDragDrop((item, targetFolderId) => {
  explorer.handleMoveItem(item.type, item.id, targetFolderId)
})

// ── Context Menu Actions ──
function handleContextAction(action: string) {
  const target = ctxMenu.target.value
  if (!target) return
  ctxMenu.hide()

  switch (action) {
    case 'open':
      if (target.type === 'folder') explorer.navigateToFolder(target.id!)
      break
    case 'rename':
      if (target.type === 'folder' && target.id) {
        const name = prompt(t('panel.examArchive.contextMenu.rename'))
        if (name) explorer.handleRenameFolder(target.id, name)
      }
      break
    case 'newSubfolder':
    case 'newFolder':
      const folderName = prompt(t('panel.examArchive.newFolder'))
      if (folderName) explorer.handleCreateFolder(folderName, target.id || undefined)
      break
    case 'delete':
      if (target.type === 'folder' && target.id) {
        if (confirm(t('panel.examArchive.confirmDelete'))) {
          explorer.handleDeleteFolder(target.id)
        }
      }
      break
  }
}

// ── Keyboard Shortcuts ──
function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Backspace' && !isInputFocused()) {
    e.preventDefault()
    explorer.navigateUp()
  }
}

function isInputFocused(): boolean {
  const el = document.activeElement
  return el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

// ── Sidebar event handlers ──
function onFolderContextMenu(event: MouseEvent, folder: ArchiveFolder) {
  ctxMenu.show(event, { type: 'folder', id: String(folder.folder_id), data: folder })
}

function onFileContextMenu(event: MouseEvent, file: ArchiveFile) {
  ctxMenu.show(event, { type: 'file', id: String(file.exam_id), data: file })
}

function onBackgroundContextMenu(event: MouseEvent) {
  ctxMenu.show(event, { type: 'background', id: null, data: null })
}

function onOpenFile(examId: string) {
  // Open PDF viewer in windowing system
  const { useDesktopPanelStore } = require('@/application/stores/modules/workspace/panel.store')
  const panelStore = useDesktopPanelStore()
  const file = explorer.files.value?.find(f => String(f.exam_id) === examId)
  panelStore.openPanel({
    type: 'admin-pdf-viewer' as any,
    title: file?.title || 'PDF Viewer',
    icon: '📄',
    payload: { examId, pdfPath: file?.pdf_path },
  })
}
</script>

<template>
  <div class="flex flex-col h-full bg-gray-900 text-white">
    <!-- Top Bar -->
    <div class="flex items-center gap-3 px-5 py-3 bg-gray-900/80 border-b border-gray-700/50">
      <span class="text-base font-semibold">
        <span class="text-indigo-400">📚</span> {{ t('panel.examArchive.title') }}
      </span>
      <button
        class="px-3 py-1 rounded-full text-xs font-medium bg-green-600 hover:bg-green-500 text-white"
        @click="emit('close')"
      >
        {{ t('panel.examArchive.back') }}
      </button>

      <div class="flex-1" />

      <!-- Search -->
      <div class="flex items-center gap-2 bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 w-64">
        <span class="text-gray-400 text-sm">🔍</span>
        <input
          v-model="explorer.searchQuery.value"
          :placeholder="t('panel.examArchive.search')"
          class="bg-transparent text-sm text-white outline-none flex-1 placeholder-gray-500"
        />
      </div>

      <button class="btn-secondary">
        ⬆ {{ t('panel.examArchive.uploadPdfs') }}
      </button>
      <button
        class="btn-primary"
        @click="explorer.handleCreateFolder(t('panel.examArchive.defaultFolderName'))"
      >
        + {{ t('panel.examArchive.newFolder') }}
      </button>
    </div>

    <!-- Main Layout -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar -->
      <ExplorerSidebar
        :programs="explorer.programs.value"
        :sidebar-tree="explorer.sidebarTree.value"
        :current-program-id="explorer.currentProgramId.value"
        :current-folder-id="explorer.currentFolderId.value"
        :drop-target-id="dragDrop.dropTargetId.value"
        @select-program="explorer.selectProgram"
        @select-folder="explorer.navigateToFolder"
        @create-folder="(name) => explorer.handleCreateFolder(name)"
        @contextmenu="onFolderContextMenu"
        @dragstart="(ev, f) => dragDrop.onDragStart(ev, 'folder', String(f.folder_id))"
        @dragover="dragDrop.onDragOver"
        @dragleave="dragDrop.onDragLeave"
        @drop="dragDrop.handleDrop"
      />

      <!-- Content Area -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <ExplorerBreadcrumb
          :breadcrumb="explorer.breadcrumb.value || []"
          :program-name="explorer.currentProgram.value?.display_name?.de"
          :view-mode="explorer.viewMode.value"
          @navigate="(id) => id ? explorer.navigateToFolder(id) : explorer.navigateUp()"
          @toggle-view="explorer.toggleViewMode"
        />

        <ExplorerContent
          :folders="explorer.folders.value || []"
          :files="explorer.files.value || []"
          :view-mode="explorer.viewMode.value"
          :loading="explorer.loading.value"
          :is-empty="explorer.isEmpty.value"
          :drop-target-id="dragDrop.dropTargetId.value"
          @open-folder="explorer.navigateToFolder"
          @open-file="onOpenFile"
          @folder-contextmenu="onFolderContextMenu"
          @file-contextmenu="onFileContextMenu"
          @background-contextmenu="onBackgroundContextMenu"
          @dragstart-folder="(ev, f) => dragDrop.onDragStart(ev, 'folder', String(f.folder_id))"
          @dragstart-file="(ev, f) => dragDrop.onDragStart(ev, 'file', String(f.exam_id))"
          @dragover="dragDrop.onDragOver"
          @dragleave="dragDrop.onDragLeave"
          @drop="dragDrop.handleDrop"
        />

        <ExplorerStatusBar
          :folder-count="explorer.stats.value?.folders ?? 0"
          :exam-count="explorer.stats.value?.exams ?? 0"
          :question-count="explorer.stats.value?.questions ?? 0"
        />
      </div>
    </div>

    <!-- Context Menu -->
    <ExplorerContextMenu
      :visible="ctxMenu.visible.value"
      :position="ctxMenu.position.value"
      :target="ctxMenu.target.value"
      @action="handleContextAction"
    />
  </div>
</template>

<style scoped>
.btn-secondary {
  @apply inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-sm font-medium
         border border-gray-600 bg-gray-800 text-gray-200 hover:bg-gray-700 transition-colors;
}
.btn-primary {
  @apply inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-sm font-medium
         bg-indigo-600 text-white hover:bg-indigo-500 transition-colors;
}
</style>
