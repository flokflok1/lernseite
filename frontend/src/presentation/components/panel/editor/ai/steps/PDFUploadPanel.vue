/**
 * PDFUploadPanel.vue
 *
 * Step 2: PDF Upload & Analysis
 * - Drag-drop file upload
 * - File validation
 * - Upload progress
 * - PDF content analysis
 */

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

interface Props {
  isLoading: boolean
  error?: string | null
}

interface Emits {
  (e: 'upload', file: File): void
  (e: 'back'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()

const dragOver = ref(false)
const selectedFile = ref<File | null>(null)
const uploadProgress = ref(0)

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  dragOver.value = true
}

const handleDragLeave = () => {
  dragOver.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  dragOver.value = false

  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleFileSelect(files[0])
  }
}

const handleFileInputChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    handleFileSelect(input.files[0])
  }
}

const handleFileSelect = (file: File) => {
  selectedFile.value = file
  uploadProgress.value = 0
}

const handleUpload = async () => {
  if (!selectedFile.value) return

  // Simulate upload progress
  uploadProgress.value = 30

  // Emit upload event (actual upload happens in composable)
  emit('upload', selectedFile.value)

  // Reset after emit
  selectedFile.value = null
  uploadProgress.value = 0
}

const handleClearFile = () => {
  selectedFile.value = null
  uploadProgress.value = 0
}
</script>

<template>
  <div class="pdf-upload-panel">
    <h3>{{ $t('courses.editor.uploadFile') }}</h3>
    <p class="description">{{ $t('courses.editor.uploadFileDescription') }}</p>

    <!-- Upload Area -->
    <div
      class="upload-area"
      :class="{ 'drag-over': dragOver }"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      <div class="upload-content">
        <div class="upload-icon">📤</div>
        <h4>{{ $t('courses.editor.dragDropFile') }}</h4>
        <p>{{ $t('courses.editor.orClickToSelect') }}</p>

        <label class="file-input-label">
          <input
            type="file"
            accept=".pdf,.doc,.docx,.ppt,.pptx,.odp,.odt"
            @change="handleFileInputChange"
            :disabled="isLoading"
            class="file-input"
          />
          <span class="file-button">{{ $t('courses.editor.selectFile') }}</span>
        </label>

        <p class="file-size-limit">{{ $t('courses.editor.maxFileSize') }}</p>
      </div>
    </div>

    <!-- Selected File Info -->
    <div v-if="selectedFile" class="file-info">
      <div class="file-details">
        <div class="file-icon">📄</div>
        <div class="file-meta">
          <div class="file-name">{{ selectedFile.name }}</div>
          <div class="file-size">{{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB</div>
        </div>
      </div>
      <button
        v-if="!isLoading"
        class="btn-remove"
        @click="handleClearFile"
        type="button"
      >
        ✕
      </button>
    </div>

    <!-- Upload Progress -->
    <div v-if="isLoading && selectedFile" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <p class="progress-text">{{ $t('courses.editor.analyzingFile') }}</p>
    </div>

    <!-- Info Box -->
    <div class="info-box">
      <span class="info-icon">ℹ️</span>
      <div>
        <strong>{{ $t('courses.editor.supportedFormats') }}</strong>
        <p>{{ $t('courses.editor.pdfInfoText') }}</p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="panel-actions">
      <button
        class="btn btn-secondary"
        @click="$emit('back')"
        :disabled="isLoading"
      >
        {{ $t('common.back') }}
      </button>
      <button
        class="btn btn-primary"
        @click="handleUpload"
        :disabled="!selectedFile || isLoading"
      >
        <span v-if="isLoading">⏳ {{ $t('courses.editor.uploading') }}</span>
        <span v-else>{{ $t('courses.editor.uploadAndAnalyze') }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.pdf-upload-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
}

h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.description {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* Upload Area */
.upload-area {
  padding: 40px 20px;
  border: 2px dashed #2196f3;
  border-radius: 8px;
  background: #f5f9ff;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.upload-area:hover {
  border-color: #1976d2;
  background: #e3f2fd;
}

.upload-area.drag-over {
  border-color: #1976d2;
  background: #bbdefb;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  font-size: 40px;
}

.upload-area h4 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.upload-area p {
  font-size: 13px;
  color: #666;
  margin: 0;
}

.file-input-label {
  cursor: pointer;
  display: inline-block;
}

.file-input {
  display: none;
}

.file-button {
  display: inline-block;
  padding: 10px 20px;
  background: #2196f3;
  color: white;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.file-button:hover {
  background: #1976d2;
}

.file-size-limit {
  font-size: 12px;
  color: #999;
  margin-top: 8px !important;
}

/* File Info */
.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}

.file-details {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.file-meta {
  flex: 1;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.file-size {
  font-size: 12px;
  color: #999;
}

.btn-remove {
  background: none;
  border: none;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  transition: color 0.2s;
}

.btn-remove:hover {
  color: #d32f2f;
}

/* Upload Progress */
.upload-progress {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4caf50;
  transition: width 0.3s;
}

.progress-text {
  font-size: 13px;
  color: #666;
  margin: 0;
  text-align: center;
}

/* Info Box */
.info-box {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  border-radius: 4px;
}

.info-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.info-box strong {
  display: block;
  font-size: 13px;
  color: #f57c00;
  margin-bottom: 2px;
}

.info-box p {
  font-size: 12px;
  color: #e65100;
  margin: 0;
  line-height: 1.4;
}

/* Actions */
.panel-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background: #eeeeee;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .pdf-upload-panel {
    padding: 16px;
    gap: 16px;
  }

  .upload-area {
    padding: 30px 15px;
  }

  .panel-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
