<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ContextMenuTarget } from '@/application/composables/panel/admin/assessment/useContextMenu'

interface Props {
  visible: boolean
  position: { x: number; y: number }
  target: ContextMenuTarget | null
}

defineProps<Props>()

const emit = defineEmits<{
  action: [action: string]
}>()

const { t } = useI18n()

function act(action: string) {
  emit('action', action)
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible && target"
      data-context-menu
      class="fixed bg-gray-800 border border-gray-600/50 rounded-xl p-1.5 min-w-[210px]
             shadow-2xl shadow-black/40 z-[10000]"
      :style="{ left: `${position.x}px`, top: `${position.y}px` }"
      @click.stop
      @mousedown.stop
    >
      <!-- Folder actions -->
      <template v-if="target.type === 'folder'">
        <button class="ctx-item" @click="act('open')">
          <span class="ctx-icon">📂</span>
          {{ t('panel.examArchive.contextMenu.open') }}
          <span class="ctx-key">Enter</span>
        </button>
        <button class="ctx-item" @click="act('rename')">
          <span class="ctx-icon">✏️</span>
          {{ t('panel.examArchive.contextMenu.rename') }}
          <span class="ctx-key">F2</span>
        </button>
        <button class="ctx-item" @click="act('moveTo')">
          <span class="ctx-icon">📎</span>
          {{ t('panel.examArchive.contextMenu.moveTo') }}
        </button>
        <div class="ctx-divider" />
        <button class="ctx-item" @click="act('newSubfolder')">
          <span class="ctx-icon">📁</span>
          {{ t('panel.examArchive.contextMenu.newSubfolder') }}
        </button>
        <button class="ctx-item" @click="act('uploadPdfs')">
          <span class="ctx-icon">⬆</span>
          {{ t('panel.examArchive.contextMenu.uploadPdfs') }}
        </button>
        <div class="ctx-divider" />
        <button class="ctx-item" @click="act('analyzeAll')">
          <span class="ctx-icon">🔍</span>
          {{ t('panel.examArchive.contextMenu.analyzeAll') }}
        </button>
        <button class="ctx-item" @click="act('generateCourse')">
          <span class="ctx-icon">📊</span>
          {{ t('panel.examArchive.contextMenu.generateCourse') }}
        </button>
        <div class="ctx-divider" />
        <button class="ctx-item text-red-400" @click="act('delete')">
          <span class="ctx-icon">🗑</span>
          {{ t('panel.examArchive.contextMenu.delete') }}
          <span class="ctx-key">Del</span>
        </button>
      </template>

      <!-- File actions -->
      <template v-if="target.type === 'file'">
        <button class="ctx-item" @click="act('open')">
          <span class="ctx-icon">📄</span>
          {{ t('panel.examArchive.contextMenu.open') }}
        </button>
        <button class="ctx-item" @click="act('download')">
          <span class="ctx-icon">⬇</span>
          {{ t('panel.examArchive.contextMenu.download') }}
        </button>
        <button class="ctx-item" @click="act('analyze')">
          <span class="ctx-icon">🔍</span>
          {{ t('panel.examArchive.contextMenu.analyze') }}
        </button>
        <button class="ctx-item" @click="act('moveTo')">
          <span class="ctx-icon">📎</span>
          {{ t('panel.examArchive.contextMenu.moveTo') }}
        </button>
        <div class="ctx-divider" />
        <button class="ctx-item text-red-400" @click="act('delete')">
          <span class="ctx-icon">🗑</span>
          {{ t('panel.examArchive.contextMenu.delete') }}
        </button>
      </template>

      <!-- Background actions -->
      <template v-if="target.type === 'background'">
        <button class="ctx-item" @click="act('newFolder')">
          <span class="ctx-icon">📁</span>
          {{ t('panel.examArchive.newFolder') }}
        </button>
        <button class="ctx-item" @click="act('uploadPdfs')">
          <span class="ctx-icon">⬆</span>
          {{ t('panel.examArchive.uploadPdfs') }}
        </button>
      </template>
    </div>
  </Teleport>
</template>

<style scoped>
.ctx-item {
  @apply flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-sm text-left
         text-gray-200 hover:bg-gray-700/60 transition-colors cursor-pointer;
}
.ctx-icon {
  @apply w-5 text-center text-sm shrink-0;
}
.ctx-key {
  @apply ml-auto text-[11px] text-gray-500 font-mono;
}
.ctx-divider {
  @apply h-px bg-gray-700/50 my-1 mx-2;
}
</style>
