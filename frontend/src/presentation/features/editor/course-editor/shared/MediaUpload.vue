/**
 * MediaUpload.vue - Media file upload interface
 *
 * Shared component for both ManualEditor and AIEditor.
 * Handles image, video, and document uploads.
 */

<script setup lang="ts">
import { ref } from 'vue'

interface Emits {
  (e: 'upload', file: File): void
  (e: 'uploading', isUploading: boolean): void
}

const emit = defineEmits<Emits>()
const isUploading = ref(false)

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    isUploading.value = true
    emit('uploading', true)
    emit('upload', file)
    isUploading.value = false
    emit('uploading', false)
  }
}
</script>

<template>
  <div class="media-upload">
    <label class="upload-area">
      <input
        type="file"
        @change="handleFileSelect"
        :disabled="isUploading"
        accept="image/*,video/*,.pdf,.doc,.docx"
      />
      <div class="upload-content">
        <span v-if="!isUploading" class="upload-icon">📁</span>
        <span v-else class="upload-icon">⏳</span>
        <p>{{ isUploading ? $t('common.uploading') : $t('courses.editor.uploadMedia') }}</p>
      </div>
    </label>
  </div>
</template>

<style scoped>
.media-upload {
  padding: 16px;
}

.upload-area {
  display: block;
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #2196f3;
  background: rgba(33, 150, 243, 0.05);
}

.upload-area input {
  display: none;
}

.upload-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.upload-area p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.upload-area:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
