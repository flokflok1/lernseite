<!--
  FilePreview.vue

  Preview window for course files (PDF, text, images),
  chapters (with lesson list), and lessons (with content).

  Uses LsxWindow (window store) as data source.
  Delegates to shared composable and sub-components.

  Phase D4 - AI Editor
-->

<template>
  <div class="preview-window">
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
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import { useI18n } from 'vue-i18n'
import { useFilePreview } from '@/application/composables/content/useFilePreview'
import type { LessonPayload } from '@/application/composables/content/useFilePreview'
import FilePreviewHeader from './FilePreviewHeader.vue'
import FilePreviewContent from './FilePreviewContent.vue'

const { t } = useI18n()

const props = defineProps<{
  window: LsxWindow
}>()

const windowStore = useWindowStore()

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
} = useFilePreview(() => props.window.payload)

function openLessonPreview(lessonItem: LessonPayload): void {
  windowStore.openWindow({
    type: 'admin-file-preview',
    title: `${t('filePreview.lesson')}: ${lessonItem.title}`,
    icon: '\uD83D\uDCC4',
    payload: { lesson: lessonItem },
    size: { width: 700, height: 500 },
  })
}
</script>

<style scoped>
.preview-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
}
</style>
