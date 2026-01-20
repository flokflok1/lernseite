<!--
  NewCourseModal - Modal for creating new courses with AI analysis
-->

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <!-- Header -->
      <h3 class="modal-title">{{ $t('admin.aiStudio.newCourse') }}</h3>

      <div class="modal-body">
        <!-- Step 1: File Upload -->
        <div class="upload-section">
          <label class="section-label">
            📄 {{ $t('admin.aiStudio.step1UploadMaterial') }}
          </label>
          <div
            class="upload-area"
            :class="{ 'has-files': files.length > 0 }"
            @click="fileInput?.click()"
            @dragover.prevent
            @drop.prevent="handleFileDrop"
          >
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md"
              @change="handleFileSelect"
              multiple
            />

            <!-- Empty State -->
            <div v-if="files.length === 0" class="upload-empty">
              <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="upload-text">{{ $t('admin.aiStudio.uploadText') }}</p>
              <p class="upload-hint">{{ $t('admin.aiStudio.uploadHint') }}</p>
            </div>

            <!-- Files List -->
            <div v-else class="files-list">
              <div v-for="(file, index) in files" :key="index" class="file-item">
                <span>📄</span>
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
                <button @click.stop="removeFile(index)" class="file-remove">
                  ✕
                </button>
              </div>
              <p class="add-more">{{ $t('admin.aiStudio.addMoreFiles') }}</p>
            </div>
          </div>

          <!-- AI Analyze Button -->
          <button
            v-if="files.length > 0 && !aiAnalyzed"
            @click="handleAnalyze"
            :disabled="isAnalyzing"
            class="analyze-btn"
          >
            <span v-if="isAnalyzing" class="animate-spin">⏳</span>
            <span v-else>🤖</span>
            {{ isAnalyzing ? $t('admin.aiStudio.analyzing') : $t('admin.aiStudio.analyzeWithAI') }}
          </button>
          <p v-if="files.length > 0 && !aiAnalyzed" class="analyze-hint">
            {{ $t('admin.aiStudio.analyzeHint') }}
          </p>
        </div>

        <!-- Step 2: Course Details -->
        <div class="details-section" :class="{ faded: files.length > 0 && !aiAnalyzed && !courseData.title }">
          <div class="section-header">
            <span>📝</span>
            <span>{{ $t('admin.aiStudio.step2CourseDetails') }}</span>
            <span v-if="aiAnalyzed" class="ai-badge">✓ {{ $t('admin.aiStudio.aiSuggestion') }}</span>
          </div>

          <!-- Title -->
          <div class="form-field">
            <label class="field-label">{{ $t('admin.aiStudio.courseTitle') }} *</label>
            <input
              v-model="courseData.title"
              type="text"
              :placeholder="$t('admin.aiStudio.courseTitlePlaceholder')"
              class="field-input"
            />
          </div>

          <!-- Description -->
          <div class="form-field">
            <label class="field-label">{{ $t('admin.aiStudio.courseDescription') }}</label>
            <textarea
              v-model="courseData.description"
              rows="3"
              :placeholder="$t('admin.aiStudio.courseDescriptionPlaceholder')"
              class="field-textarea"
            ></textarea>
          </div>

          <!-- Category & Profile -->
          <div class="form-row">
            <div class="form-field">
              <label class="field-label">{{ $t('admin.aiStudio.category') }}</label>
              <select v-model="courseData.categoryId" class="field-select">
                <option :value="null">{{ $t('admin.aiStudio.noCategory') }}</option>
                <option v-for="cat in availableCategories" :key="cat.category_id" :value="cat.category_id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
            <div class="form-field">
              <label class="field-label">🤖 {{ $t('admin.aiStudio.aiProfile') }}</label>
              <select v-model="courseData.profileKey" class="field-select">
                <option v-for="profile in availableProfiles" :key="profile.key" :value="profile.key">
                  {{ profile.name }}{{ profile.is_default ? ` (${$t('admin.aiStudio.default')})` : '' }}
                </option>
              </select>
            </div>
          </div>

          <!-- Language & Level -->
          <div class="form-row">
            <div class="form-field">
              <label class="field-label">{{ $t('admin.aiStudio.language') }}</label>
              <select v-model="courseData.language" class="field-select">
                <option value="de">{{ $t('admin.aiStudio.languageDe') }}</option>
                <option value="en">{{ $t('admin.aiStudio.languageEn') }}</option>
                <option value="es">{{ $t('admin.aiStudio.languageEs') }}</option>
                <option value="fr">{{ $t('admin.aiStudio.languageFr') }}</option>
              </select>
            </div>
            <div class="form-field">
              <label class="field-label">{{ $t('admin.aiStudio.level') }}</label>
              <select v-model="courseData.level" class="field-select">
                <option value="beginner">{{ $t('admin.aiStudio.levelBeginner') }}</option>
                <option value="intermediate">{{ $t('admin.aiStudio.levelIntermediate') }}</option>
                <option value="advanced">{{ $t('admin.aiStudio.levelAdvanced') }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <p class="footer-hint">
          {{ $t('admin.aiStudio.afterCreationHint') }}
        </p>
        <div class="footer-actions">
          <button @click="$emit('close')" class="btn-cancel">
            {{ $t('common.cancel') }}
          </button>
          <button
            @click="handleCreate"
            :disabled="!canCreate || isCreating"
            class="btn-create"
          >
            <span v-if="isCreating" class="animate-spin">⏳</span>
            {{ $t('admin.aiStudio.createCourse') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * NewCourseModal - Multi-step course creation with AI analysis
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Category, Profile, NewCourseData } from '../composables/useCourseManagement'

const { t } = useI18n()

// =============================================================================
// Props
// =============================================================================

interface Props {
  availableCategories: Category[]
  availableProfiles: Profile[]
}

const props = defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', data: NewCourseData): void
  (e: 'analyze', files: File[]): void
}>()

// =============================================================================
// State
// =============================================================================

const fileInput = ref<HTMLInputElement | null>(null)
const files = ref<File[]>([])
const isAnalyzing = ref(false)
const isCreating = ref(false)
const aiAnalyzed = ref(false)

const courseData = ref({
  title: '',
  description: '',
  language: 'de',
  level: 'beginner' as 'beginner' | 'intermediate' | 'advanced',
  categoryId: null as number | null,
  profileKey: 'standard'
})

// =============================================================================
// Computed
// =============================================================================

const canCreate = computed(() => {
  return courseData.value.title.trim().length > 0
})

// =============================================================================
// Methods - File Handling
// =============================================================================

function handleFileSelect(event: Event): void {
  const target = event.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
}

function handleFileDrop(event: DragEvent): void {
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

function addFiles(newFiles: File[]): void {
  // Filter for accepted file types
  const acceptedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/markdown'
  ]

  const validFiles = newFiles.filter(file =>
    acceptedTypes.includes(file.type) ||
    file.name.endsWith('.md') ||
    file.name.endsWith('.txt')
  )

  files.value.push(...validFiles)

  // Reset AI analyzed flag when files change
  aiAnalyzed.value = false
}

function removeFile(index: number): void {
  files.value.splice(index, 1)
  aiAnalyzed.value = false
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// =============================================================================
// Methods - AI Analysis
// =============================================================================

async function handleAnalyze(): Promise<void> {
  if (files.value.length === 0) return

  isAnalyzing.value = true

  try {
    emit('analyze', files.value)

    // Parent component should handle the actual API call and update courseData
    // For now, just mark as analyzed
    aiAnalyzed.value = true
  } catch (error) {
    console.error('AI analysis failed:', error)
  } finally {
    isAnalyzing.value = false
  }
}

// Allow parent to update course data from AI analysis
function updateFromAIAnalysis(data: {
  title: string
  description: string
  categoryId: number | null
  profileKey: string
}): void {
  courseData.value.title = data.title
  courseData.value.description = data.description
  courseData.value.categoryId = data.categoryId
  courseData.value.profileKey = data.profileKey
  aiAnalyzed.value = true
}

// =============================================================================
// Methods - Create
// =============================================================================

async function handleCreate(): Promise<void> {
  if (!canCreate.value) return

  isCreating.value = true

  try {
    const data: NewCourseData = {
      title: courseData.value.title.trim(),
      description: courseData.value.description?.trim(),
      language: courseData.value.language,
      level: courseData.value.level,
      categoryId: courseData.value.categoryId,
      profileKey: courseData.value.profileKey,
      files: files.value
    }

    emit('create', data)
  } catch (error) {
    console.error('Course creation failed:', error)
  } finally {
    isCreating.value = false
  }
}

// =============================================================================
// Expose
// =============================================================================

defineExpose({
  updateFromAIAnalysis
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-content {
  background: var(--color-surface);
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 42rem;
  padding: 1.5rem;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 1rem;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Upload Section */
.upload-section {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 1rem;
}

.section-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: 0.5rem;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.15s;
}

.upload-area:hover {
  border-color: var(--color-primary);
}

.upload-area.has-files {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.hidden {
  display: none;
}

.upload-empty {
  color: var(--color-text-tertiary);
}

.upload-icon {
  width: 2.5rem;
  height: 2.5rem;
  margin: 0 auto 0.75rem;
  opacity: 0.5;
}

.upload-text {
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0 0 0.25rem;
}

.upload-hint {
  font-size: 0.75rem;
  margin: 0;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: left;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.file-remove {
  padding: 0.25rem;
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  transition: color 0.15s;
}

.file-remove:hover {
  color: #dc2626;
}

.add-more {
  font-size: 0.75rem;
  color: var(--color-primary);
  text-align: center;
  margin: 0.5rem 0 0;
}

.analyze-btn {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.625rem 1rem;
  background: linear-gradient(to right, #8b5cf6, #a855f7);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.15s;
}

.analyze-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #7c3aed, #9333ea);
}

.analyze-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.analyze-hint {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  text-align: center;
  margin: 0.5rem 0 0;
}

/* Details Section */
.details-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: opacity 0.15s;
}

.details-section.faded {
  opacity: 0.5;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.ai-badge {
  padding: 0.125rem 0.5rem;
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.field-input,
.field-textarea,
.field-select {
  padding: 0.5rem 0.75rem;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.field-input:focus,
.field-textarea:focus,
.field-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.field-textarea {
  resize: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.footer-hint {
  flex: 1;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin: 0;
}

.footer-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-cancel,
.btn-create {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-cancel {
  background: none;
  border: none;
  color: var(--color-text-secondary);
}

.btn-cancel:hover {
  color: var(--color-text-primary);
}

.btn-create {
  background: var(--color-primary);
  color: white;
  border: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-create:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-create:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
