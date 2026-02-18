<!--
  FilePreviewPanel.vue

  Panel variant of the file preview for the admin workspace.
  Previews course files (PDF, text, images), chapters, and lessons.

  Uses LsxPanel (panel store) as data source.
  Delegates to shared composable and sub-components.

  Phase D4 - KI-Studio Pro
-->

<template>
  <div class="preview-panel">
    <FilePreviewHeader
      :icon="headerIcon"
      :title="headerTitle"
      :meta="headerMeta"
      :show-download="previewType === 'file' && !!fileUrl"
      :show-edit="previewType !== 'file'"
      @download="downloadFile"
      @edit="openEditor"
    />

    <FilePreviewContent
      :loading="loading"
      :error="error"
      :preview-type="previewType"
      :file-url="fileUrl"
      :text-content="textContent"
      :is-pdf="isPdf"
      :is-image="isImage"
      :is-text="isText"
      :file="file"
      :chapter="chapter"
      :lesson="lesson"
      :chapter-lessons="chapterLessons"
      @download="downloadFile"
      @open-lesson="openLessonPreview"
    />
  </div>
</template>

<script setup lang="ts">
import type { LsxPanel } from '@/application/stores/modules/workspace'
import { usePanelStore } from '@/application/stores/modules/workspace'
import { useI18n } from 'vue-i18n'
import { useFilePreview } from '@/presentation/components/shared/composables/useFilePreview'
import type { LessonPayload } from '@/presentation/components/shared/composables/useFilePreview'
import FilePreviewHeader from '@/presentation/components/shared/FilePreviewHeader.vue'
import FilePreviewContent from '@/presentation/components/shared/FilePreviewContent.vue'

const { t } = useI18n()

const props = defineProps<{
  panel: LsxPanel
}>()

const panelStore = usePanelStore()

const {
  fileUrl,
  textContent,
  chapterLessons,
  loading,
  error,
  previewType,
  file,
  chapter,
  lesson,
  isPdf,
  isImage,
  isText,
  headerIcon,
  headerTitle,
  headerMeta,
  downloadFile,
  openEditor,
} = useFilePreview(() => props.panel.payload)

function openLessonPreview(lessonItem: LessonPayload): void {
  panelStore.openPanel({
    type: 'admin-file-preview',
    title: `${t('filePreview.lesson')}: ${lessonItem.title}`,
    icon: '\uD83D\uDCC4',
    payload: { lesson: lessonItem },
    size: { width: 700, height: 500 },
  })
}
</script>

<style scoped>
.preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
}
</style>
